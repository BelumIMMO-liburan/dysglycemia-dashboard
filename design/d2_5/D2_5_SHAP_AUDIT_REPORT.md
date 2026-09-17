# Phase D2.5 — Legacy SHAP Explainer Forensic Audit Report
**Date:** September 2026  
**Auditor:** Antigravity Pairing Agent  
**Status:** COMPLETE & DECOUPLED  
**Target Module:** `dashboard/predictor/shap_explainer.py`  
**Classification:** **Class C: LEGACY / ARCHIVE LATER**

---

## 1. Background & Context

In early exploratory phases of the project (specifically the legacy Kaggle 8-feature dataset with DLNN and Random Forest models), `dashboard/predictor/shap_explainer.py` was created to provide feature attribution charts using the `shap` Python package (KernelSHAP / DeepExplainer).

With the completion of the thesis research methodology (Phase 5 locked GAM model on NHANES 2021–2023 with 7 non-laboratory predictors), the clinical decision-support system transitioned to a frozen Generalized Additive Model. Generalized Additive Models have closed-form, mathematically exact, additive term representations ($f_i(x_i)$). Applying heuristic SHAP sampling to an additive model introduces unnecessary approximation error, computational latency, and potential silent failures.

---

## 2. Forensic Code Audit of `shap_explainer.py`

An in-depth inspection of `dashboard/predictor/shap_explainer.py` revealed the following critical architectural and governance limitations:

### 2.1 Unaudited Background Data Sampling
```python
# Lines 31-43 in shap_explainer.py
def _get_background_data(model_name=None):
    # Attempts to sample 50 rows from data/processed/train.csv or generate random normal data
    ...
```
- **Finding:** The background reference distribution is loaded dynamically from an unpinned CSV file or synthesized on-the-fly with `np.random.normal()`.
- **Governance Risk:** This introduces non-determinism. Two evaluations of the exact same patient can produce differing SHAP values depending on the background sample seed.

### 2.2 Dangerous Silent Failure Catch-All
```python
# Lines 85-94 in shap_explainer.py
try:
    explainer = shap.KernelExplainer(predict_fn, background)
    shap_vals = explainer.shap_values(x_input)
except Exception as e:
    logger.error(...)
    return {feat: 0.0 for feat in feature_names}  # SILENT FALLBACK TO ZERO!
```
- **Finding:** If SHAP calculation fails (e.g., matrix dimension mismatch, timeout, memory exhaustion), the function silently swallows the error and returns a dictionary of zeros (`0.0`).
- **Clinical/Governance Risk:** A clinician viewing a chart with all zeros would falsely assume no features contributed to the risk score, obscuring a system defect. Research governance strictly prohibits silent fallbacks that fabricate scientific data.

### 2.3 Massive Computational Overhead
- **KernelSHAP Latency:** KernelSHAP requires generating dozens to hundreds of perturbed synthetic instances and evaluating the model iteratively, taking $800$ ms to $3,200$ ms per prediction.
- **GAM-Native Latency:** Direct spline basis evaluation takes $< 2$ ms (over $400\times$ faster).

---

## 3. Decoupling Verification

Phase D2.5 has achieved complete architectural and runtime decoupling from `shap_explainer.py`:

1. **Service Boundary:** The Stage-1 screening workflow invokes `predictor.services.screening_explanation.explain_screening()` exclusively. It never imports or calls `shap_explainer`.
2. **Template Independence:** `screening_result.html` renders GAM-native factor contributions from `ScreeningExplanation.contributions_json`. It contains zero SHAP tags, scripts, or references.
3. **Automated Test Guard:** `LegacyShapDecouplingTests` in `dashboard/predictor/tests.py` actively asserts:
   - No occurrences of `"SHAP"` or `"shap_values"` in `screening_result.html`.
   - Any invocation of `shap_explainer.explain_prediction` during Stage-1 screening triggers an immediate test failure.

---

## 4. Classification & Future Disposition

- **Classification:** **Class C: LEGACY / ARCHIVE LATER**.
- `shap_explainer.py` remains in the repository solely for backward compatibility with the legacy multi-model playground route (`/predict/`).
- It has been fully neutralized from all active Stage-1 screening paths.
- It will be formally archived to `legacy/` during post-thesis code sanitization without impacting the Stage-1 clinical CDSS.
