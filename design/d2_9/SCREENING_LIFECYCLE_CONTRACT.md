# Screening Case Lifecycle Contract — Data Specification & Governance Rules

## 1. Domain Purpose & Philosophy
The screening case lifecycle service (`dashboard/predictor/services/screening_lifecycle.py`) establishes a centralized, deterministic mechanism to derive the operational workflow status of any screening case across the two-stage screening cascade:
$$\text{Stage-1 Non-Lab Intake} \longrightarrow \text{Frozen GAM} \longrightarrow \text{GAM Additive XAI} \longrightarrow \text{Human Review} \longrightarrow \text{Final Human Decision} \longrightarrow \text{If Refer: Stage-2 HbA1c Lab} \longrightarrow \text{Laboratory Range}$$

### Epistemic Declaration
> **The screening lifecycle describes application workflow state, NOT patient biology, disease condition, or clinical diagnosis.**

All lifecycle states are **derived dynamically** from persisted immutable relational entities (`ScreeningRecord`, `ScreeningExplanation`, `HumanReview`, and `Stage2Assessment`). No mutable `status` column is added to `ScreeningRecord`.

---

## 2. Active Domain Entities & Relational Graph

The active system operates exclusively on modern Phase D2.4–D2.8 domain entities:
```
ScreeningRecord (1) [Immutable Stage-1 Intake & Model Provenance]
  ├── explanation (0..1) [OneToOne: ScreeningExplanation]
  └── human_review (0..1) [OneToOne: HumanReview]
        └── stage2_assessment (0..1) [OneToOne: Stage2Assessment]
```
Legacy entities (`Prediction`, `Override`, old multi-model rows) are strictly isolated and excluded from active workflow navigation.

---

## 3. Lifecycle State Definitions & Codes

| State Code | Presentation Label | Actionability | Next Action Type | Authorized Action Link | Stage-2 Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `explanation_unavailable` | Needs System Attention | False | `system_attention` | Locked (None) | `—` (`unavailable`) |
| `pending_review` | Pending Human Review | **True** | `review` | `/screening/<id>/result/` | `—` (`unavailable`) |
| `reviewed_no_referral` | Reviewed — No Stage 2 | False | `none` | `/screening/<id>/result/` | **Not applicable** |
| `pending_stage2` | Pending Stage 2 | **True** | `stage2` | `/screening/<id>/stage2/` | **Pending** |
| `completed_stage2` | Completed Two-Stage | False | `none` | `/screening/<id>/result/` | **Completed** |
| `integrity_error` | Data Integrity Issue | False | `integrity_error` | Locked (None) | `—` (`unavailable`) |

---

## 4. Deterministic Precedence Hierarchy

The state of a `ScreeningRecord` is evaluated in strict sequential precedence:

```python
IF data_integrity_audit_fails(record):
    RETURN integrity_error

ELIF explanation is None OR explanation.status != 'generated':
    RETURN explanation_unavailable

ELIF human_review is None:
    RETURN pending_review

ELIF human_review.final_referral_recommended is False:
    RETURN reviewed_no_referral

ELIF stage2_assessment is None:
    RETURN pending_stage2

ELSE:
    RETURN completed_stage2
```

### Precedence Rationale:
1. **Integrity Guard:** Any conflicting entity states (e.g. Stage 2 present without referral authorization) surface immediately as integrity errors rather than assigning a false status.
2. **Evidence-First Gate:** Under the research governance protocol, human review requires both the AI recommendation and faithful additive explanations. If XAI generation failed or is missing, human review is locked.
3. **Review Authority:** Until human review occurs, Stage-2 eligibility cannot be evaluated.
4. **Mandatory Referral Filter:** If the finalized human decision is "Do not refer", Stage 2 is explicitly **Not applicable** and the case terminates.
5. **Cascade Completion:** If referral is recommended and HbA1c is recorded, the two-stage cascade is **Completed**.

---

## 5. "Not Applicable" vs "Pending" Stage-2 Distinction

The system enforces a strict distinction between cases that are not indicated for laboratory assessment and those awaiting laboratory intake:

- **Stage 2: Not applicable**
  - Final human review decision is `final_referral_recommended == False`.
  - Reached via Accepted No Refer OR Overridden from Refer to No Refer.
  - Stage 2 is blocked and unavailable.
- **Stage 2: Pending**
  - Final human review decision is `final_referral_recommended == True`.
  - Reached via Accepted Refer OR Overridden from No Refer to Refer.
  - Stage-2 assessment is authorized but not yet completed.
- **Stage 2: Completed**
  - `Stage2Assessment` entity exists, linked to authorizing `HumanReview`.

---

## 6. Zero Computation & Immutability Invariant

1. **Zero Model Inference:** Lifecycle derivation inspects relational foreign keys and boolean columns. It executes **0 GAM inferences**, **0 preprocessing calls**, and **0 XAI generation calls**.
2. **Zero Database Writes:** Lifecycle derivation is a pure read-only service. GET requests across queue, history, and detail pages perform **0 writes**, 0 updates, and 0 timestamp changes.
3. **No HbA1c Reclassification:** Reads persisted `Stage2Assessment.laboratory_range` directly from the database; does not re-evaluate reference rules on GET.
