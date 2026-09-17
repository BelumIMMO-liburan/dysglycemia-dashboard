# Research Governance & Methodology Audit

**Phase:** D1 — Design Foundation  
**Scope:** Compliance between Current Dashboard (`dashboard/`) and Frozen Research Specification  
**Audit Date:** 2026-09-04  
**Status:** ACTION REQUIRED PRIOR TO IMPLEMENTATION  

---

## 1. Executive Summary

This audit evaluates the current dashboard implementation against the frozen research governance established in Phase 4.2, Phase 4.2A, Phase 5, and Phase 5.1. 

The finalized undergraduate thesis research protocol establishes a **Two-Stage Non-Laboratory Screening System for Previously Unrecognized HbA1c-Defined Dysglycemia**:
- **Stage-1 Primary Model:** Generalized Additive Model (GAM), $n\_splines=10, \lambda=10.0$
- **Stage-1 Predictors (Exactly 7 non-laboratory features):** `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`
- **Frozen Operating Threshold:** $0.1389$ (Development-derived, targeting $\ge 90\%$ screening sensitivity)
- **Held-Out Confirmatory Performance:** Sensitivity $86.39\%$, Specificity $42.51\%$, ROC-AUC $0.7277$, PR-AUC $0.4503$
- **Stage-2 Protocol:** Independent laboratory HbA1c testing for individuals with elevated Stage-1 screening signals.

The current dashboard codebase violates this protocol across prediction inputs, model selection, decision thresholds, clinical terminology, explainability, human override semantics, and analytics. Below is the complete catalog of discrepancies classified by severity.

---

## 2. Governance Severity Matrix

| Severity | Definition | Remediation Requirement |
| :--- | :--- | :--- |
| **P0** | **Research-Invalidating / Fatal Defect** | Must be redesigned and completely resolved before any functional code is accepted. |
| **P1** | **Evaluation-Impacting Defect** | Must be resolved before the prototype is presented to expert clinicians or study evaluators. |
| **P2** | **Design & Maintenance Improvement** | Ergonomic, visual, or architectural improvements to ensure long-term robustness. |

---

## 3. P0 Findings: Research-Invalidating Deficiencies

### P0-1: Inclusion of Laboratory Biomarkers in Non-Laboratory Screening
- **Location:** `predictor/models.py`, `predictor/views.py`, `predictor/templates/predictor/index.html`
- **Existing Behavior:** The intake form prompts for `HbA1c` and `glucose` as inputs to calculate risk.
- **Why Fatal:** The entire thesis premise is **non-laboratory screening** to identify individuals who warrant confirmatory laboratory testing. If HbA1c or fasting glucose is already known, Stage-1 screening is clinically redundant and conceptually invalid.
- **Mandatory Correction:** Eliminate `HbA1c` and `glucose` from the Stage-1 input form and prediction pipeline. The Stage-1 input form must accept **only the seven locked non-laboratory predictors**: `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`.

### P0-2: Utilization of Obsolete Kaggle Models Instead of Frozen Phase-5 NHANES GAM
- **Location:** `predictor/model_loader.py`
- **Existing Behavior:** `model_loader.py` loads models from `Skripsi/models/` (`dlnn_model_A.h5`, `dlnn_model_A_weighted.h5`, `gam_model.pkl`) trained on a synthetic/legacy Kaggle dataset.
- **Why Fatal:** The thesis experiments finalized on NHANES 2021–August 2023 data. Using obsolete Kaggle models produces invalid predictions that have no connection to the published research findings.
- **Mandatory Correction:** Connect exclusively to the frozen research artifact:
  `nhanes_feasibility_2021_2023/models_phase5/gam_final.pkl` using preprocessor `preprocessor.pkl`.

### P0-3: User-Selectable Models & Multi-Model Consensus Architecture
- **Location:** `predictor/views.py` (`predict_view`, `prediction_detail_view`), `predictor/templates/predictor/index.html`
- **Existing Behavior:** Users can select between five deep learning configurations and a GAM via a dropdown menu. Results display a "Multi-Model Consensus" badge comparing DLNN to GAM.
- **Why Fatal:** The research phase conclusively rejected DLNN and selected GAM as the single authoritative primary model based on parsimony, interpretability, and equal discriminative performance. Exposing model selection invites clinician confusion and undermines scientific protocol.
- **Mandatory Correction:** Completely remove model selection and consensus logic. The dashboard must execute only the frozen GAM.

### P0-4: Dynamic Classification Threshold Sliders
- **Location:** `predictor/views.py` (`predict_view`), `predictor/templates/predictor/index.html`
- **Existing Behavior:** The form provides an adjustable threshold input/slider defaulting to $0.50$.
- **Why Fatal:** The operating point $0.1389$ was derived from development data to enforce high screening sensitivity ($\ge 90\%$). Allowing users to arbitrarily slide the threshold breaks the calibrated sensitivity/specificity trade-off.
- **Mandatory Correction:** Hardcode the frozen decision threshold to exactly **0.1389**. Prevent any user or runtime adjustment. Display the threshold purely as frozen methodological metadata.

### P0-5: Human Override Inverting Biological Disease Status
- **Location:** `predictor/views.py` (lines 190–191), `predictor/models.py` (lines 100–103)
- **Existing Behavior:**
  ```python
  if decision == 'reject':
      # If rejecting, the override is the opposite of the AI prediction
      override_value = 0 if prediction.prediction == 1 else 1
  ```
- **Why Fatal:** A clinician cannot change a patient's biological dysglycemia status with a mouse click. In a screening workflow, the AI issues a **referral recommendation** (e.g., "Refer for Stage-2 HbA1c assessment"). The human override acts upon the **referral decision**, not the patient's underlying physiology.
- **Mandatory Correction:** Refactor override semantics:
  - System output: `Refer for Stage-2 HbA1c Assessment` vs `Do Not Refer At This Time`
  - Human review: `Accept Recommendation` vs `Override Recommendation`
  - When overriding, the clinician selects a valid clinical disposition (e.g., "Decline Referral", "Immediate Clinical Referral", "Repeat Non-Lab Assessment") with an explicit reason. Biological status is never altered.

### P0-6: Unsound KernelSHAP Explanations on Obsolete Background
- **Location:** `predictor/shap_explainer.py`
- **Existing Behavior:** Runs `shap.KernelExplainer` sampling 100 observations from `clean_dataset.csv`, with a hardcoded fallback base value of 0.5 and zero-value fallback on error.
- **Why Fatal:** KernelSHAP is a slow, sampling-based approximation designed for black-box models. Running it on GAM is computationally wasteful, mathematically unfaithful to GAM's true spline curves, and crashes intermittently.
- **Mandatory Correction:** Replace KernelSHAP with **GAM-Native Additive Term Decomposition**, directly evaluating the fitted spline functions $f_i(x_i)$ from `gam_final.pkl`.

---

## 4. P1 Findings: Evaluation-Impacting Discrepancies

### P1-1: Misleading Diagnostic & Alarmist Language
- **Location:** `predictor/templates/predictor/` (`index.html`, `result.html`, `base.html`)
- **Existing Phrases:**
  - *"High Diabetes Risk (Prioritas)"* with red siren emojis (🚨)
  - *"Low Diabetes Risk (Sehat)"*
  - *"Moderate Diabetes Risk (Suspek)"*
  - *"Probability of diabetes"*
  - *"AI diagnoses patient"*
- **Clinical & Methodological Risk:** Non-laboratory screening models cannot diagnose diabetes. Claiming a patient is "Diabetic" or "Sehat" creates dangerous false reassurance or alarm.
- **Mandatory Correction:** Standardize language across all screens:
  - Use: **"Screening Signal: Elevated"** or **"Screening Signal: Non-Elevated"**
  - Use: **"Screening Probability"** (never "probability of diabetes" or "disease certainty")
  - Use: **"Refer for Stage-2 HbA1c Assessment"**
  - Include mandatory disclaimer: *"This screening tool does not provide a medical diagnosis. Confirmatory diagnosis requires venous HbA1c or plasma glucose testing."*

### P1-2: Total Absence of Stage-2 HbA1c Workflow
- **Location:** Entire `dashboard/` application
- **Existing Behavior:** The application terminates after Stage-1 prediction. There is no mechanism to record Stage-2 HbA1c laboratory results, categorize glycemic ranges, or reconcile the screening prediction with confirmatory testing.
- **Mandatory Correction:** Design an explicit **Stage-2 HbA1c Interface** enabling clinicians to enter laboratory HbA1c values, view standard clinical reference ranges (Normal $<5.7\%$, Prediabetes $5.7\%–6.4\%$, Diabetes $\ge 6.5\%$), and close the screening loop.

### P1-3: Mathematical Denominator Bug in Override Analytics
- **Location:** `predictor/views.py` (line 295)
- **Existing Code:**
  ```python
  rate = (model_rejects / model_preds * 100) if model_preds > 0 else 0
  ```
- **Flaw:** `model_preds` includes all predictions in the database, including unreviewed cases. Dividing rejections by unreviewed cases artificially deflates the calculated override rate.
- **Mandatory Correction:** Compute override metrics strictly over **reviewed cases**:
  $$\text{Override Rate} = \frac{N_{\text{overrides}}}{N_{\text{reviewed\_screenings}}} \times 100$$

### P1-4: Conflating Clinician Agreement with "Model Accuracy"
- **Location:** `predictor/views.py`, `predictor/templates/predictor/analytics.html`
- **Flaw:** Labelling clinician-AI agreement as "AI accuracy" in analytics views.
- **Correction:** Agreement represents human-AI concordance, not empirical diagnostic accuracy. Ground-truth accuracy can only be assessed after Stage-2 laboratory verification. Clearly label concordance as **"Human-AI Agreement Rate"**.

### P1-5: Lack of Deterministic Review Reason Enforcement & User Tracking
- **Location:** `predictor/views.py`, `predictor/models.py`
- **Existing Behavior:** `reason` is an optional text field; `doctor_name` is an unauthenticated text string.
- **Correction:** When overriding a screening recommendation, a structured categorical reason (e.g., *"Patient has known active corticosteroid therapy"*, *"Severe frailty / limited life expectancy"*, *"Recent lab test already normal"*) plus mandatory descriptive note must be required.

---

## 5. P2 Findings: UX & Architectural Maintenance

### P2-1: Unrestrained Visual Styling (Glassmorphism & Neon Palettes)
- **Observation:** `style.css` relies on heavy CSS blur filters (`backdrop-filter: blur(12px)`), saturated neon gradients, and emoji iconography.
- **Correction:** Align visual language with **shadcn/ui**: neutral surfaces, subtle 1px borders, calm semantic status indicators, and SVG icons.

### P2-2: Missing Auditability & History Detail
- **Observation:** The history view presents a flat table with minimal context and no ability to inspect the complete audit trail (inputs, term contributions, reviewer comments, timestamp, Stage-2 results).
- **Correction:** Create dedicated **Screening Detail** and **Audit Log** views with immutable change tracking.

### P2-3: Inadequate Accessibility (WCAG 2.1 AA)
- **Observation:** Low contrast on subtle placeholder text, lack of visible focus rings on interactive inputs, non-semantic buttons for toggles, and reliance on color alone for risk states.
- **Correction:** Implement full keyboard navigation, accessible ARIA attributes, visible focus indicators, and text+icon+color status indicators.

---

## 6. Research Governance Audit Sign-Off

The existing dashboard violates the core scientific protocol of the thesis in its current state. No further feature development can proceed without systematically addressing all P0 and P1 violations in the Phase D2 implementation plan.
