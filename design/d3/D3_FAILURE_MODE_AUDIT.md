# D3 Failure Mode, Tampering & Exception Audit

**Audit Date:** 2026-09-05  
**Evaluation Target:** Error handling, atomic transactions, and defense-in-depth safeguards  
**Status:** ALL DEFENSES VERIFIED — NO SILENT FALLBACKS

---

## 1. Failure Mode Testing Matrix

Every critical failure mode was tested to confirm that the prototype fails closed, preserves data integrity, and never manufactures synthetic or misleading evidence:

| Failure Mode / Edge Case | Test / Inspection Mechanism | System Response | Persistence Action | Silent Fallback Check | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Missing GAM Model File** | `verify_artifact_integrity` | Raises `InferenceArtifactError("Artifact file not found: gam_final.pkl")` | Zero records persisted; User sees error banner | None (No default probability) | **PASSED** |
| **Tampered GAM SHA256 Hash** | Simulated hash mismatch | Raises `InferenceArtifactError("GAM artifact hash mismatch! ... Failing closed.")` | Zero records persisted; Execution halted | None (No fallback model) | **PASSED** |
| **Missing Preprocessor File** | `verify_artifact_integrity` | Raises `InferenceArtifactError("Artifact file not found: preprocessor.pkl")` | Zero records persisted | None (No identity transformation) | **PASSED** |
| **Tampered Preprocessor Hash** | Simulated hash mismatch | Raises `InferenceArtifactError("Preprocessor artifact hash mismatch! ...")` | Zero records persisted | None | **PASSED** |
| **Invalid Stage-1 Input Value** | Form submission out-of-range (e.g. Age=15, BMI=10) | Server-side form validation rejects payload (`form.is_valid() == False`) | Zero records persisted; Form re-rendered with error | None | **PASSED** |
| **GAM-Native XAI Computation Failure** | Simulated `ScreeningExplanationFidelityError` | Catch block creates `ScreeningExplanation` with `status='failed'`, `failure_reason=...` | `ScreeningRecord` preserved; Human Review blocked | None (No zero-contribution dummy array) | **PASSED** |
| **Database Persistence Write Failure** | Simulated DB write exception during `run_screening` | Catch block logs error; returns error banner to user | Transaction rolled back; 0 partial records | None | **PASSED** |
| **Duplicate Screening Submission** | Idempotency token & double-submit defense | Re-renders existing result or rejects duplicate POST | Exactly 1 `ScreeningRecord` persisted | None | **PASSED** |
| **Duplicate Human Review Submission** | Concurrent POST to `accept_review` / `override_review` | `OneToOneField` + atomic transaction check (`hasattr(screening_record, 'human_review')`) | Exactly 1 `HumanReview` persisted; Subsequent redirects | None | **PASSED** |
| **Invalid Override Reason Code** | Post payload with unauthorized reason string | Form validation rejects (`forms.ValidationError`) | Review not created; Error shown to reviewer | None | **PASSED** |
| **Client-Tampered Referral Recommendation** | Injected `ai_referral_recommended` in POST payload | Parameter completely ignored; Server queries immutable `ScreeningRecord` | Database integrity preserved | None | **PASSED** |
| **Invalid Stage-2 HbA1c Percentage** | Post value < 2.0% or > 25.0% or non-numeric | Form validation fails; user redirected with error message | Zero `Stage2Assessment` records created | None | **PASSED** |
| **Duplicate Stage-2 Submission** | Repeated POST to `stage2_confirm` | `hasattr(human_review, 'stage2_assessment')` redirects idempotently | Exactly 1 `Stage2Assessment` persisted | None | **PASSED** |
| **Missing / Non-Existent Record UUID** | GET/POST to unknown UUID endpoint | Django `get_object_or_404(ScreeningRecord, id=...)` raises 404 | No action; Clean 404 response | None | **PASSED** |

---

## 2. No Silent Fallback Verification

A strict code audit of all `try / except` blocks in `dashboard/predictor/services/` confirmed that zero fallback heuristics exist:
- **No probability imputation:** No `probability = 0.5` or `0.0`.
- **No dummy contributions:** No `contributions = [0, 0, 0, ...]`.
- **No default referral decisions:** No `recommendation = False` fallback.
- **Fail-Closed Guarantee:** Every unexpected condition raises a typed exception and halts the pipeline cleanly.
