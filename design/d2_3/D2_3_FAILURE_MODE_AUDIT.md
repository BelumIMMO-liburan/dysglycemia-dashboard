# Phase D2.3 Failure Mode Audit: Defensive Architecture & Error Handling

**Phase:** D2.3  
**Status:** Audited & Verified  
**Date:** September 2026  
**Governing Skill:** `research-governance`  

---

## 1. Audit Purpose

In clinical decision support, silent errors, unhandled exceptions, and distorted probabilities can lead to critical patient safety risks or inappropriate clinical workflow disruptions. This audit examines all potential failure modes in the Stage-1 frozen GAM inference pipeline and confirms that the system fails safely, defensively, and transparently.

---

## 2. Taxonomy of Failure Modes & Defensive Strategies

| Failure Mode | Root Cause / Trigger | Defensive Mechanism | System Behavior |
| :--- | :--- | :--- | :--- |
| **FM-1: Artifact Tampering / Corruption** | Disk bit-rot, intentional file modification, or incorrect deployment of model files. | SHA-256 pre-verification against hardcoded canonical baselines. | Raises `ArtifactIntegrityError`. Halts execution immediately; no prediction generated. |
| **FM-2: Missing Artifacts** | `gam_final.pkl` or `preprocessor.pkl` absent from expected path. | File existence validation in `compute_file_sha256()`. | Raises `InferenceArtifactError`. Logs error server-side; displays clean generic error to user. |
| **FM-3: Missing Input Parameter** | Form bypassed or malformed API request missing one of 7 required keys. | Strict dictionary key verification in `encode_and_order_inputs()`. | Raises `InferenceDomainError` with parameter name. Fails before preprocessing. |
| **FM-4: Non-Finite Input Values** | `NaN`, `+Inf`, `-Inf` passed into numerical fields. | Explicit `np.isnan()` and `np.isinf()` guard clauses. | Raises `InferenceDomainError`. Trapped before NumPy conversion. |
| **FM-5: Invalid Semantic Categorical** | Arbitrary strings submitted for `sex`, `hypertension_history`, or `smoking_history`. | Whitelist lookup (`("male", "1", "1.0")`, `("yes", "1", "1.0")`). | Raises `InferenceDomainError`. Disallows unmapped factor indices. |
| **FM-6: Out-of-Bounds Continuous Value** | Values exceeding biological or model bounds (e.g., Age 150, BMI 100). | Django form clean methods + adapter domain checking. | Form re-rendered with specific field guidance before inference. |
| **FM-7: Non-Finite Output Probability** | Model returns `NaN`, negative, or $>1.0$ value due to mathematical divergence. | Post-prediction sanity assertions on `raw_prob`. | Raises `InferenceExecutionError` if `prob < 0.0` or `prob > 1.0` or `isnan`. |
| **FM-8: Concurrency Race Condition** | Multiple concurrent requests attempting to load model files simultaneously. | `threading.Lock` protecting lazy singleton initialization. | Thread-safe double-checked locking; exactly one load occurs. |
| **FM-9: Preprocessor State Corruption** | Accidental call to `.fit()` or `.fit_transform()` altering scaling constants. | Service only exposes `.transform()`; regression tests verify scaler invariance. | Scaler weights immutable across lifetime of process. |

---

## 3. UI Error Presentation & Privacy Preservation

When an inference failure occurs (e.g., FM-1 through FM-7):
1. **Server Logging:** The full Python stack trace is captured in Django's logger with level `ERROR` and `exc_info=True`.
2. **User Surface Presentation:** The user receives an accessible, reassuring alert:
   > **Screening Inference Execution Error**  
   > Screening could not be completed. Please try again or contact the study administrator.
3. **Traceback Concealment:** Internal paths, model file locations, stack traces, and database connection strings are strictly hidden from the presentation layer.
4. **Preservation of Inputs:** The user's entered parameters remain visible in the review summary so they can verify values or retry without losing their work.
5. **Zero Partial Persistence:** No database rows are written if inference fails.

---

## 4. Verification Evidence

The automated test `test_simulated_inference_error_renders_safe_alert` in `dashboard/predictor/tests.py` verifies this end-to-end behavior:
- HTTP status: `200` (safe rendering of error template)
- Element `id="inference-error-alert"` present with `role="alert"`
- Database count remains `0`
- Input parameter summary retained for user continuity
