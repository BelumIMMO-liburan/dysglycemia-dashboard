# Phase D2.7 Implementation Report: Human Override Workflow + Structured Rationale

**Phase:** D2.7  
**Implementation Date:** 2026-09-04  
**Status:** COMPLETED & AUDITED  
**Governing Skill:** `research-governance` (Highest Precedence), `dashboard-design`, `frontend-quality`  

---

## 1. Executive Summary

Phase D2.7 extends the Stage-1 Human Review system by introducing an auditable, branch-sensitive **Human Override Workflow**. A reviewer can either accept the AI referral recommendation or explicitly override it to the opposite referral decision (`REFER FOR STAGE-2 HbA1c` $\leftrightarrow$ `DO NOT REFER AT THIS TIME`).

### Core Architectural Invariant:
> **"Human Override records a reviewer decision that differs from the AI's referral recommendation. It changes only the final human referral disposition. The original AI output, model probability, GAM spline terms, and threshold remain permanently immutable."**

### Scope Boundaries Strictly Enforced:
- **Included:** Schema extension to `HumanReview`, removal of implicit default on `review_action`, branch-specific structured rationale taxonomy, server-derived binary opposite decision, accessible modal dialog UI, anti-tampering defenses, 11 automated test suites, 7 visual QA screenshots.
- **Excluded (Deferred to Phase D2.8):** Stage-2 confirmatory laboratory intake, venous blood draw data entry, HbA1c measurement ingestion.
- **Excluded:** Clinical queue management, clinician authentication systems, agreement/override rate analytics.

---

## 2. D2.6 Preflight Corrections Completed

1. **Reviewer Code Language & PII Filtering:**
   - Retracted claims implying regex validation automatically detects personal names.
   - Standardized user-facing instruction copy: *"Use the reviewer code assigned for this study. Do not enter your name or other identifying information."*
   - Documented in `design/d2_7/D2_6_PREFLIGHT_CORRECTIONS.md`.
2. **Review Action Default Removal:**
   - Removed `default='accepted'` from `HumanReview.review_action`.
   - Defined explicit Django choices: `[('accepted', 'Accepted Recommendation'), ('overridden', 'Overridden Recommendation')]`.
   - Backward-compatibility verified for all existing D2.6 database records.

---

## 3. Database Schema Extension & Migration

Migration `predictor/migrations/0005_humanreview_override_note_and_more.py` was created and applied.

### Schema Details:
- `override_reason_code = models.CharField(max_length=64, blank=True, null=True)`
- `override_note = models.TextField(max_length=500, blank=True, null=True)`
- `review_action`: Explicit choices (`accepted`, `overridden`), no default.
- `screening_record`: `on_delete=models.PROTECT`.

### Model Invariants (`clean()` method):
- `accepted`: Requires `final_referral_recommended == ai_referral_recommended`, reason & note must be empty.
- `overridden`: Requires `final_referral_recommended != ai_referral_recommended`, valid branch-specific reason code required, non-empty note required if reason is `'other'`.

---

## 4. Branch-Specific Structured Rationale Taxonomy

### Branch 1 (AI REFER $\to$ Human DO NOT REFER):
1. `additional_context_reduces_concern`: "Additional context supports not referring at this time"
2. `input_quality_concern`: "Concern about the quality or accuracy of one or more screening inputs"
3. `repeat_assessment_preferred`: "Repeat or additional assessment is preferred before referral"
4. `other`: "Other reason" *(strictly requires `override_note`)*

### Branch 2 (AI DO NOT REFER $\to$ Human REFER):
1. `additional_context_increases_concern`: "Additional context supports referral"
2. `input_quality_concern`: "Concern about the quality or accuracy of one or more screening inputs"
3. `precautionary_referral`: "Referral is preferred as a precaution"
4. `other`: "Other reason" *(strictly requires `override_note`)*

---

## 5. Backend Views & Anti-Tampering Defenses

1. **Route:** Added `path('screening/<uuid:screening_id>/review/override/', views.override_review_view, name='override_review')` in `predictor/urls.py`.
2. **Method Check:** POST-only; GET returns 302 or 405.
3. **Server-Derived Determination:**
   $$\text{final\_referral\_recommended} = \text{not screening\_record.ai\_referral\_recommended}$$
   Client payloads containing injected decision flags (`final_referral_recommended`, `review_action`, `model_probability`, etc.) are completely disregarded.
4. **Explanation Prerequisite Gate:** Gated on `ScreeningExplanation.status == 'generated'`. If missing or failed, override submission is blocked and creates zero reviews.
5. **Duplicate Defense:** Subsequent review submissions on an already-finalized record are rejected; original decision and timestamp are preserved.
6. **Zero Re-inference / Zero Re-explanation:** Review submission and result detail reload execute 0 GAM inference calls and 0 XAI calls.

---

## 6. User Interface & Accessible Modal Dialog

Integrated into `dashboard/predictor/templates/predictor/screening_result.html`:
- **Pending Review Card:**
  - Presents `[ Accept Recommendation ]` (primary button) alongside `[ Override Recommendation ]` (secondary outline button, non-destructive styling).
- **Accessible Modal Dialog (`#override-modal-backdrop`):**
  - Follows WAI-ARIA modal dialog pattern (`role="dialog"`, `aria-modal="true"`, focus trapping, ESC dismissal, focus return).
  - Prominently displays comparison between Original AI Recommendation and Final Human Decision.
  - Dynamically renders branch-specific reason radios within a semantic `<fieldset>`.
  - Contextual note textarea with live 500-char counter and PII reminder.
  - High-contrast `"Confirm Override"` button.
- **Completed Overridden State:**
  - Replaces the review form with `"Recommendation Overridden"` badge (`#review-status-badge`, restrained styling, never hostile red).
  - Displays original recommendation, final human decision, override reason, optional context note, reviewer code, and UTC timestamp.
  - Read-only audit notice; all forms omitted.

---

## 7. Automated Test Suite Results

A dedicated suite of 11 test cases in `HumanOverrideWorkflowTests` was added to `dashboard/predictor/tests.py`. The entire test suite was executed:

```
Ran 65 tests in 0.811s
OK
```

### Coverage of Test Suites:
1. `test_override_refer_to_no_refer`: REFER flipped to DO NOT REFER, reason stored, 0 ML/XAI calls.
2. `test_override_no_refer_to_refer`: DO NOT REFER flipped to REFER, reason stored, 0 ML/XAI calls.
3. `test_accept_regression`: D2.6 accept workflow verified functional without regressions.
4. `test_invalid_same_decision_at_model_level`: Override preserving AI decision rejected.
5. `test_invalid_reason_branch_rejected`: Cross-branch reasons rejected.
6. `test_other_reason_without_note_rejected`: Empty note on "Other" rejected.
7. `test_other_reason_with_valid_note_accepted`: Valid note on "Other" accepted.
8. `test_tampering_payload_ignored`: Injected client decision parameters disregarded.
9. `test_duplicate_and_concurrency_defense`: Multiple overrides or accept-then-override blocked.
10. `test_override_blocked_when_explanation_failed_or_missing`: Explanation prerequisite enforced.
11. `test_overridden_result_get_renders_all_fields_without_reinference`: GET detail page verified read-only with 0 re-inference calls.

---

## 8. Visual QA Verification

All 7 visual QA states were captured using `browser_subagent` and saved to `design/d2_7/screenshots/`:

| Filename | Viewport | Target State & Description |
| :--- | :--- | :--- |
| `01_review_choice_refer.png` | Desktop ($1280 \times 800$) | Pending review card showing both Accept and Override buttons for an elevated signal. |
| `02_override_dialog_refer_to_no_refer.png` | Desktop ($1280 \times 800$) | Open modal dialog with comparison grid and reasons for REFER $\to$ NO REFER. |
| `03_override_complete_refer_to_no_refer.png` | Desktop ($1280 \times 800$) | Finalized review card showing "Recommendation Overridden" from Refer to Do not refer. |
| `04_override_dialog_no_refer_to_refer.png` | Desktop ($1280 \times 800$) | Open modal dialog for lower signal showing reasons including Precautionary referral. |
| `05_override_complete_no_refer_to_refer.png` | Desktop ($1280 \times 800$) | Finalized review card showing "Recommendation Overridden" from No refer to Refer. |
| `06_override_validation_error.png` | Desktop ($1280 \times 800$) | Modal dialog displaying validation error banner when "Other" is selected without a note. |
| `07_override_mobile.png` | Mobile ($375 \times 812$) | Responsive mobile dialog layout with full-width ergonomic touch targets. |

---

## 9. Protected Research Artifact Hash Verification

Bitwise SHA-256 hash comparison confirms zero mutation across all core research assets:

| Research Artifact | Expected Locked SHA-256 | Live Workspace SHA-256 | Verification Result |
| :--- | :--- | :--- | :--- |
| `gam_final.pkl` | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` | **BYTE-IDENTICAL (Frozen)** |
| `preprocessor.pkl` | `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` | `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` | **BYTE-IDENTICAL (Frozen)** |
| `FINAL_MODEL_SPECIFICATION_LOCKED.md` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | **BYTE-IDENTICAL (Frozen)** |
| `final_test_predictions.csv` | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` | **BYTE-IDENTICAL (Frozen)** |

---

## 10. Research Governance Compliance Confirmation

1. **Frozen GAM Unchanged:** No retraining, weight modifications, or inference recalculations occurred.
2. **Locked Threshold Unchanged:** The research operating threshold ($0.1389$) remains immutable.
3. **Clinical Scope Maintained:** Override changes only the Stage-2 referral recommendation. It does not alter biological reality, prediabetes/diabetes status, or disease classification.
4. **Permanent Separation:** AI output and human review/override remain separate relational entities.
