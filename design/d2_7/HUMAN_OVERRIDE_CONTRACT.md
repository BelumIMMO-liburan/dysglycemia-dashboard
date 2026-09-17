# Human Override Contract: Data Architecture, Semantics & Audit Specification

**Document Version:** 1.0  
**Phase:** D2.7  
**Status:** Frozen & Approved  
**Governing Skill:** `research-governance` (Highest Precedence)  

---

## 1. Authoritative Override Definition & Governance Principles

> **"Human Override records a reviewer decision that differs from the AI's referral recommendation. It does not establish that either the human or the AI is clinically correct."**

In the Stage-1 Dysglycemia Decision-Support Screening Prototype, machine learning inference and human clinical review remain strictly separated:
1. **AI Output Is Immutable Truth of Machine Inference:** The `ScreeningRecord` captures the historical output evaluated by the frozen Phase-5 GAM at the pre-specified operating threshold ($0.1389$). Under no circumstances does human review or override modify `ScreeningRecord.screening_probability`, `ScreeningRecord.ai_referral_recommended`, `ScreeningRecord.decision_threshold`, or model hashes.
2. **Override Operates on Referral Action, NOT Diagnosis:** The override workflow governs only the decision of whether to refer the participant for Stage-2 confirmatory laboratory HbA1c testing. It does **not** alter biological reality, HbA1c values, prediabetes/diabetes status, or disease classification.
3. **No Clinical Correctness Implied:** Override records decision disagreement between the clinician/researcher and the statistical screening model. It provides structured provenance for research discordance analysis without establishing ground-truth accuracy.

---

## 2. Strict Binary Final-Decision Semantics

The Stage-1 screening referral protocol operates on a strictly binary decision space:
- `REFER FOR STAGE-2 HbA1c` ($\text{True}$)
- `DO NOT REFER AT THIS TIME` ($\text{False}$)

Human Override is operationalized strictly as **disagreement with the binary recommendation**:

$$\text{IF}\quad \text{ai\_referral\_recommended} == \text{True} \quad\implies\quad \text{override\_decision} == \text{False}$$
$$\text{IF}\quad \text{ai\_referral\_recommended} == \text{False} \quad\implies\quad \text{override\_decision} == \text{True}$$

### Scope Boundaries:
- Third intermediate decisions (e.g. "repeat screening", "defer", "request extra assessment") are **strictly prohibited** from the binary `final_referral_recommended` column in Phase D2.7. Such workflow categories may be logged as structured reasons, but the final referral disposition remains boolean.
- An "override" that preserves the original AI recommendation is logically invalid and rejected at both the application and model clean levels.

---

## 3. Server-Derived Determination & Anti-Tampering

The override endpoint (`/screening/<uuid>/review/override/`) does not accept client-dictated final decision flags:
- Any incoming POST parameter containing `final_referral_recommended`, `review_action`, `screening_probability`, `threshold`, or `model_sha256` is ignored.
- The server retrieves the persisted `ScreeningRecord` and derives the final decision deterministically:
  $$\text{final\_referral\_recommended} \leftarrow \text{not screening\_record.ai\_referral\_recommended}$$
- This guarantees by construction that client-side payload injection or browser manipulation cannot corrupt binary override integrity.

---

## 4. Human Review Schema Extension: `HumanReview`

Rather than introducing a secondary table or resurrecting legacy models, the existing `HumanReview` entity is extended:

| Column Name | Django Field Type | Null / Blank | Constraints & Semantics | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUIDField` | `False / False` | `primary_key=True`, default=`uuid.uuid4` | Cryptographically random unique identifier. |
| `screening_record` | `OneToOneField` | `False / False` | `on_delete=models.PROTECT`, `related_name='human_review'` | Strict 1:1 relational linkage. Deletion protected. |
| `reviewer_code` | `CharField(32)` | `False / False` | Pattern: `^[a-zA-Z0-9_-]+$` | Pseudonymous reviewer study identifier. |
| `review_action` | `CharField(20)` | `False / False` | Choices: `('accepted', 'Accepted')`, `('overridden', 'Overridden')` | Explicit action. Implicit defaults removed. |
| `final_referral_recommended` | `BooleanField` | `False / False` | Derived server-side | Final referral disposition. |
| `override_reason_code` | `CharField(64)` | `True / True` | Nullable; required if `review_action == 'overridden'` | Branch-specific structured rationale category. |
| `override_note` | `TextField(500)` | `True / True` | Nullable; optional (required if `code == 'other'`) | Brief contextual rationale (max 500 chars). |
| `created_at` | `DateTimeField` | `False / False` | `auto_now_add=True` | UTC review timestamp. |

---

## 5. Domain Invariants & Validation Rules

Model-level (`clean()`) and form-level (`clean()`) validation enforce the following relational invariants:

1. **Accepted Reviews (`review_action == 'accepted'`):**
   - `final_referral_recommended == screening_record.ai_referral_recommended`
   - `override_reason_code` must be empty / null.
   - `override_note` must be empty / null.
2. **Overridden Reviews (`review_action == 'overridden'`):**
   - `final_referral_recommended != screening_record.ai_referral_recommended`
   - `override_reason_code` must be present and match the branch-specific taxonomy.
   - If `override_reason_code == 'other'`, `override_note` is strictly required.
   - `override_note` is capped at 500 characters.

---

## 6. Single-Review Invariant & Immutability

1. **One-to-One Strictness:** Each `ScreeningRecord` has at most **one** finalized `HumanReview`.
2. **Read-Only Finalization:** Once a review (acceptance or override) is saved, it is permanently locked:
   - Repeated submissions redirect to the read-only result page.
   - Original decision, reason, reviewer code, and timestamp are preserved without mutation.
   - Switching decisions (Accept then Override, or Override then Accept) is prohibited.

---

## 7. Prerequisite Gate: Explanation Availability

In alignment with the **Evidence-First Guided Review** philosophy:
- Both Accept and Override actions require that a faithful GAM-native explanation exists in the database (`ScreeningExplanation.status == 'generated'`).
- If the explanation failed or is missing:
  - Both action buttons are hidden, and the `#review-unavailable-card` is rendered.
  - Direct POST requests are rejected.

---

## 8. Privacy & Data Minimization

- **Pseudonymous Reviewer Code:** Clinicians and researchers identify themselves solely using institutional codes (e.g., `REV-01`, `HP-04`).
- **No PII:** Personal names, emails, phone numbers, national identification numbers, or employee badge numbers are not collected.
- **Contextual Note Boundary:** The `override_note` field is intended for brief clinical context (e.g., recent fasting test or acute illness). It is not a clinical chart note or patient history repository.
