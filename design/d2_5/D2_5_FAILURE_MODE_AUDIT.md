# Phase D2.5 — Explanation Failure Mode & Resilience Audit
**Date:** September 2026  
**Auditor:** Antigravity Pairing Agent  
**Status:** AUDITED & PROTECTED  
**Governing Skill:** `research-governance`

---

## 1. Audit Purpose

To evaluate the system's failure modes when generating, serializing, persisting, or displaying GAM-native additive explanations, ensuring that:
1. An explanation failure never fabricates data (zero silent fallbacks).
2. An explanation failure never corrupts or aborts a successful Stage-1 screening inference.
3. The clinician/researcher is presented with a clear, dignified status notice when explanation computation is temporarily unavailable.

---

## 2. Failure Mode Analysis Matrix

| Failure Mode ID | Scenario | Root Cause | System Response | Governance Compliance |
|:---|:---|:---|:---|:---:|
| **FM-EXP-1** | Additive reconstruction error exceeds $10^{-10}$ | Numerical drift, basis function mismatch, or model mutation | Raises `ScreeningExplanationFidelityError`. Explanation fails closed; persists `ScreeningExplanation(status='failed')`. | **COMPLIANT** |
| **FM-EXP-2** | Model artifact hash mismatch at explanation time | Tampering or corruption of `gam_final.pkl` or `preprocessor.pkl` | `load_model_and_preprocessor()` raises `InferenceArtifactError`. Persists `ScreeningExplanation(status='failed')`. | **COMPLIANT** |
| **FM-EXP-3** | Non-finite spline term output (NaN / Inf) | Extreme numerical overflow or domain boundary corruption | `np.isfinite()` check detects NaN/Inf; raises `ScreeningExplanationError`. Persists `status='failed'`. | **COMPLIANT** |
| **FM-EXP-4** | Non-serializable data types in payload (e.g., Decimal) | Form cleaned data passing Decimal objects into JSON field | `ScreeningContribution.to_dict()` safely casts `Decimal` to `float`. Persistence succeeds cleanly. | **COMPLIANT** |
| **FM-EXP-5** | Database write exception during explanation persistence | Disk full, locking conflict, or constraint violation | Atomic transaction rolls back; user receives clean retry prompt. Zero dangling records created. | **COMPLIANT** |
| **FM-EXP-6** | User accesses result detail route where explanation is absent or failed | Legacy screening record or failed explanation session | View detects `explanation_status == 'failed'`; displays `#explanation-failure-card`. Primary result remains intact. | **COMPLIANT** |

---

## 3. Resilience Verification Test Evidence

1. **Automated Simulated Failure Test:**
   - Test `test_simulated_explanation_failure_falls_back_gracefully` in `predictor/tests.py` submits a payload with `_simulate_explanation_error='1'`.
   - Result: `ScreeningRecord` is created and committed. `ScreeningExplanation` is persisted with `status='failed'` and diagnostic message.
   - Result View: Loads HTTP 200. Displays the primary recommendation (*"Referral for Stage-2 HbA1c assessment is recommended"*) alongside `#explanation-failure-card` (*"Model explanation temporarily unavailable"*). Zero silent zeros rendered.

2. **Visual QA Verification:**
   - Captured in `design/d2_5/screenshots/05_explanation_unavailable.png`.
   - Verified that the failure card displays an amber accent bar, explanation diagnostic summary, and technical disclosure without affecting the decision-support assessment.
