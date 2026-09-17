# Phase D2.6 Implementation Report: Human Review Foundation & Accept Recommendation Workflow

**Phase:** D2.6  
**Implementation Date:** 2026-09-04  
**Status:** COMPLETED & VERIFIED  
**Governing Skill:** `research-governance` (Highest Precedence), `dashboard-design`, `frontend-quality`  

---

## 1. Executive Summary

Phase D2.6 successfully establishes the **Human Review Foundation and Accept Recommendation Workflow** for the Stage-1 Non-Laboratory Dysglycemia Screening Dashboard.

This phase bridges the gap between automated machine learning inference and clinical governance by introducing an auditable human review entity (`HumanReview`) strictly decoupled from the immutable `ScreeningRecord`. A clinician or researcher can inspect the screening inputs, the unrounded model probability, and the GAM-native additive explanation, and explicitly record agreement by accepting the AI referral recommendation.

### Scope Boundaries Strictly Enforced:
- **Included:** Human Review data entity, anonymous reviewer code validation, accept AI recommendation workflow, immutable audit trail persistence, explanation prerequisite gating, visual QA across all 3 review states.
- **Excluded (Deferred to Phase D2.7):** Human Override, override rationales, reason categories, clinical justification notes, decision mutation.
- **Excluded (Deferred to Phase D2.8):** Stage-2 diagnostic laboratory intake, HbA1c measurements, venous blood draws.
- **Excluded:** Clinical queue management, clinician authentication/login systems, acceptance rate analytics.

---

## 2. Preflight Verifications Completed

### Preflight A: Explanation Failure Decoupling
In `dashboard/predictor/views.py` (`run_screening_view`), the database transaction for `ScreeningRecord` was decoupled from `ScreeningExplanation` generation. Previously, an unhandled exception during explanation synthesis could have compromised or rolled back the newly created `ScreeningRecord`. Under the audited architecture:
1. `ScreeningRecord` is created and committed to the database in an atomic block.
2. `compute_and_persist_explanation` runs in an isolated try-except block. If explanation generation encounters an error, the error is caught, the failure status (`status='failed'`) is saved, and `ScreeningRecord` remains intact and valid.
3. Documented in `design/d2_6/D2_5_PREFLIGHT_VERIFICATION.md`.

### Preflight B: Spline Terminology Correction
All occurrences of `"10 knots"` in `design/d2_5/D2_5_IMPLEMENTATION_REPORT.md` were audited and updated to `"Spline (10-spline basis / n_splines=10)"`, adhering strictly to pyGAM mathematical specifications where continuous features utilize 10 spline basis functions rather than 10 internal knot partitions.

---

## 3. Legacy Model Forensic Audit

The legacy prototype model `Override` in `dashboard/predictor/models.py` was evaluated:
```python
# Legacy Override model
class Override(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    doctor_name = models.CharField(max_length=100)
    override_value = models.IntegerField()
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```
- **Audit Classification:** **Class C: LEGACY — DO NOT USE / Class D: ARCHIVE LATER**.
- **Violations Identified:**
  1. Stored real doctor names (`doctor_name`), violating privacy guidelines.
  2. Used non-unique `ForeignKey`, allowing conflicting overrides on the same prediction.
  3. Represented disease classification flipping (`override_value = 0 or 1`) rather than protocol referral decisions.
  4. Cascade deletion (`on_delete=CASCADE`) destroyed audit history.
- **Action Taken:** Complete isolation. The new `HumanReview` entity does not interact with `Override`.

---

## 4. Database Architecture: `HumanReview`

Migration `predictor/migrations/0004_humanreview.py` was created and applied.

### Schema:
- **`id`**: `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`
- **`screening_record`**: `OneToOneField(ScreeningRecord, on_delete=models.PROTECT, related_name='human_review')`
- **`reviewer_code`**: `CharField(max_length=32)`
- **`review_action`**: `CharField(max_length=20, default='accepted')`
- **`final_referral_recommended`**: `BooleanField()`
- **`created_at`**: `DateTimeField(auto_now_add=True)`

### Core Invariants Guaranteed:
1. **Zero Mutation:** `ScreeningRecord` attributes are never modified by human review.
2. **One-to-One Strictness:** Database-enforced `UNIQUE` constraint on `screening_record_id`.
3. **Deletion Protection:** `on_delete=models.PROTECT` prevents deletion of reviewed screening records.

---

## 5. Backend Validation & View Logic

### 5.1 Validation Form (`HumanReviewAcceptForm`)
- Strict alphanumeric regex: `^[a-zA-Z0-9_-]+$` (length: 1–32 characters).
- Strips whitespace; rejects special punctuation, HTML/script injections, and personal names.

### 5.2 Review Accept View (`accept_review_view`)
- **HTTP Method:** Strictly POST. GET requests return HTTP 405 Method Not Allowed.
- **Explanation Prerequisite Gate:** Gated on `ScreeningExplanation.status == 'generated'`. If missing or failed, returns HTTP 400.
- **Duplicate Defense:** If `hasattr(screening_record, 'human_review')`, gracefully redirects back to result view without modifying existing review record.
- **Server-Side Decision Derivation:**
  $$\text{final\_referral\_recommended} \leftarrow \text{screening\_record.ai\_referral\_recommended}$$
  The client payload cannot specify or alter the final referral recommendation.
- **Transaction Safety:** Review record creation executes within `transaction.atomic()`.

### 5.3 Result Detail View Integration (`screening_result_view`)
- Passes `human_review`, `explanation_faithful`, `review_error`, and `review_form` to the template context.
- Makes **zero** GAM inference or XAI recomputation calls.

---

## 6. User Experience & Visual Interface

The Human Review component (`#human-review-card`) is integrated into `screening_result.html` directly following the GAM-native explanation card:
- **State A (Reviewed / Finalized):**
  - Displays `"Reviewed"` badge (`#review-status-badge`), final referral decision (`#final-decision-badge`), anonymous reviewer code (`#reviewer-code-display`), and UTC timestamp (`#review-timestamp-display`).
  - Displays permanent lock notice (`#review-immutable-notice`). Form is hidden.
- **State B (Review Unavailable):**
  - Displayed if explanation failed or is missing (`#review-unavailable-card`). Explains that human review requires local factor decomposition.
- **State C (Pending Review):**
  - Displays `"Pending Review"` badge, guidance banner, proposed AI recommendation summary, reviewer code input field (`#id_reviewer_code`) with helper text, and the high-contrast `"Accept AI Recommendation"` button (`#accept-recommendation-btn`).

---

## 7. Automated Test Suite Results

7 test classes containing 24 tests specifically targeting Phase D2.6 were added to `dashboard/predictor/tests.py`. The full test suite was executed:

```
Ran 54 tests in 3.655s
OK
```

### Coverage of Test Suites:
1. `HumanReviewModelUnitTests`: UUID primary keys, OneToOne relational constraints, model field structure, absence of clinical diagnosis/HbA1c/override fields.
2. `HumanReviewAcceptWorkflowTests`: Full workflow accepting elevated signal (REFER) and lower signal (NO REFER), verifying zero mutation of `ScreeningRecord`.
3. `HumanReviewTamperingDefenseTests`: Injected client parameters (`final_referral_recommended=false`, `override=true`) are ignored; server strictly persists AI recommendation.
4. `HumanReviewDuplicateDefenseTests`: Repeated POST submissions do not duplicate review rows; original timestamp is preserved.
5. `HumanReviewExplanationPrerequisiteTests`: Direct review POST on records with failed/missing explanations is rejected with HTTP 400; UI displays `#review-unavailable-card`.
6. `HumanReviewZeroReinferenceTests`: POST review submission and GET result view execute 0 GAM inference and 0 XAI calls.
7. `HumanReviewReviewerCodeValidationTests`: Validates accepted alphanumeric codes (`CLIN-01`, `DOC_99`) and rejects invalid inputs (spaces, punctuation, scripts).

---

## 8. Visual QA Verification

All visual states were captured in the browser using `browser_subagent` and saved to `design/d2_6/screenshots/`:

| Artifact Filename | Viewport | Target State & Verification |
| :--- | :--- | :--- |
| `01_human_review_refer.png` | Desktop ($1280 \times 800$) | Pending review state for elevated risk participant. |
| `02_human_review_no_refer.png` | Desktop ($1280 \times 800$) | Pending review state for lower risk participant. |
| `03_review_accepted_refer.png` | Desktop ($1280 \times 800$) | Finalized state for accepted referral decision. |
| `04_review_accepted_no_refer.png` | Desktop ($1280 \times 800$) | Finalized state for accepted non-referral decision. |
| `05_review_mobile.png` | Mobile ($375 \times 812$) | Mobile layout with full-width ergonomic touch targets. |
| `06_review_unavailable_explanation_failure.png` | Desktop ($1280 \times 800$) | Locked review card when explanation is unavailable. |

---

## 9. Protected Research Artifact Hash Verification

Bitwise SHA-256 hash verification was executed on all core research assets:

| Research Artifact | Expected Locked SHA-256 | Live Workspace SHA-256 | Verification Result |
| :--- | :--- | :--- | :--- |
| `gam_final.pkl` | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` | **MATCH (Frozen)** |
| `preprocessor.pkl` | `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` | `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` | **MATCH (Frozen)** |
| `FINAL_MODEL_SPECIFICATION_LOCKED.md` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | **MATCH (Frozen)** |
| `final_test_predictions.csv` | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` | **MATCH (Frozen)** |

---

## 10. Research Governance Compliance Confirmation

1. **Frozen GAM Unchanged:** No retraining, fine-tuning, or re-inference occurred.
2. **Locked Threshold Unchanged:** The research operating point ($0.1389$) remains immutable.
3. **No Clinical Diagnosis:** Language strictly refers to Stage-1 screening referrals, not clinical diabetes diagnoses.
4. **Separation of Concerns:** AI output and human governance are permanently separated in the data model.
