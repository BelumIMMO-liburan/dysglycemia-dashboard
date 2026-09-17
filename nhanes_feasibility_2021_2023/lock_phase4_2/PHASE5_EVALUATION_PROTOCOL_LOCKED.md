# Phase 5 Final Evaluation Protocol Lock (Phase 4.2A)

**Document Status:** **FROZEN & IMMUTABLE**  
**Protocol Phase:** Phase 4.2A Evaluation Protocol Lock  
**Final Test Status:** **LOCKED — ZERO ACCESS PERMITTED**  
**Date Locked:** 2026-09-02  

---

## 1. Single-Batch Phase-5 Execution Policy

To ensure complete scientific integrity, eliminate observer bias, and prevent inadvertent post-hoc tuning:
- **Phase 5 must be executed as a SINGLE BATCH evaluation.**
- The final test cohort ($N = 812$ participants in `EXPANDED_COMMON`) must face all three candidate models simultaneously under frozen settings.

### Sequence of Operations (Strictly Enforced Before Inspecting Labels):
1. **Model Fitting (Development Only):**
   - Fit `StandardScaler` strictly on the $N = 3,232$ development partition.
   - Train the primary model: **Generalized Additive Model (GAM)** (`splines10_lam10.0`).
   - Train baseline comparator: **Logistic Regression** (`L2_C0.1`).
   - Train non-linear comparator: **Deep Learning Neural Network (DLNN)** (`DLNN_16_8_drop0.0`, using an internal $15\%$ stratified split of the development set for early stopping).
2. **Model Artifact Freezing:**
   - Save trained model objects and preprocessor to disk in `models_phase5/`.
3. **Single Forward Test Inference:**
   - Apply the frozen preprocessor to the final test partition ($N = 812$).
   - Generate predicted probabilities for GAM, Logistic Regression, and DLNN in the same script execution.
4. **Prediction Persistence:**
   - Save all test predictions to `predictions_phase5/final_test_predictions.csv` before computing or displaying any performance metric.
5. **Metric Calculation:**
   - Compute all pre-specified metrics in a single automated evaluation run.

### Explicit Operational Prohibition:
- **DO NOT** run the GAM final test, inspect performance, alter models or thresholds, and then run Logistic Regression or DLNN.
- All three models must be trained, frozen, and evaluated in the same unbroken pipeline run.

---

## 2. Pre-Specified Final-Test Metrics

### 2.1 Threshold-Independent Metrics (All Models)
- **ROC-AUC:** Area under the Receiver Operating Characteristic curve.
- **PR-AUC:** Average Precision (Area under Precision-Recall curve).
- **Brier Score:** Mean squared error of probability predictions: $\frac{1}{N}\sum (p_i - y_i)^2$.

### 2.2 Threshold-Dependent Screening Metrics at Frozen 90% Sensitivity Operating Points

Each model will be evaluated at its own **frozen development-derived threshold targeting $\ge 90\%$ sensitivity**:
- **Primary Model (GAM):** Frozen threshold = **`0.1389`**
- **Baseline (Logistic Regression):** Frozen threshold = **`0.1389`**
- **Complex Comparator (DLNN):** Frozen threshold = **`0.1419`**

*Strict Rule: Thresholds MUST NOT be re-tuned, shifted, or optimized using final-test data.*

#### Required Reporting Metrics at Frozen Operating Threshold:
1. **Sensitivity** ($\text{TP} / (\text{TP} + \text{FN})$)
2. **Specificity** ($\text{TN} / (\text{TN} + \text{FP})$)
3. **Positive Predictive Value (PPV)** ($\text{TP} / (\text{TP} + \text{FP})$)
4. **Negative Predictive Value (NPV)** ($\text{TN} / (\text{TN} + \text{FN})$)
5. **F1-Score** ($2 \cdot \frac{\text{PPV} \cdot \text{Sens}}{\text{PPV} + \text{Sens}}$)
6. **Balanced Accuracy** ($\frac{\text{Sensitivity} + \text{Specificity}}{2}$)
7. **Confusion Matrix** ($\text{TP}, \text{FP}, \text{TN}, \text{FN}$)
8. **Referral Fraction (% Referred)** ($(\text{TP} + \text{FP}) / N \times 100$)
9. **Not-Referred Fraction (% Not Referred)** ($(\text{TN} + \text{FN}) / N \times 100$)
10. **Dysglycemia Captured Fraction** ($\text{TP} / (\text{TP} + \text{FN}) \times 100$)
11. **Dysglycemia Missed Fraction** ($\text{FN} / (\text{TP} + \text{FN}) \times 100$)
12. **Screening Efficiency Metric:** **"HbA1c tests per dysglycemia case detected"** ($1 / \text{PPV}$)

---

## 3. Statistical Uncertainty: Participant-Level Bootstrap

To quantify sampling variability on the final test set:
- **Resampling Method:** Participant-level paired bootstrap with replacement.
- **Number of Resamples:** **2,000 iterations**.
- **Random Seed:** **`42`**.
- **Confidence Intervals:** Empirical percentile 95% bootstrap confidence intervals ($2.5\text{th}$ to $97.5\text{th}$ percentiles) for:
  - ROC-AUC
  - PR-AUC
  - Brier Score
  - Sensitivity (at frozen threshold)
  - Specificity (at frozen threshold)
  - PPV (at frozen threshold)
  - NPV (at frozen threshold)
- **Paired Comparator Differences:**
  - Differences between models ($\Delta \text{ROC-AUC}$, $\Delta \text{PR-AUC}$, $\Delta \text{Brier Score}$, $\Delta \text{Sensitivity}$, $\Delta \text{Specificity}$) will be calculated on the **exact same bootstrap participant resamples** for GAM vs. Logistic Regression and GAM vs. DLNN.
- **Timing:** Bootstrap analysis occurs strictly **after** the single set of frozen test predictions has been permanently stored. It must never be used to retune models.

---

## 4. Final Calibration Audit Protocol

Using the single frozen vector of final-test predicted probabilities (with probabilities clipped to $[\epsilon, 1 - \epsilon]$, $\epsilon = 1\times 10^{-6}$ for logit calculations):
1. **Brier Score:** $\frac{1}{N}\sum (p_i - y_i)^2$.
2. **Prevalence-Only Brier Reference:** $B_{\text{ref}} = \bar{y}_{\text{test}}(1 - \bar{y}_{\text{test}})$.
3. **Brier Skill Score:** $\text{BSS} = 1 - \frac{\text{Brier}}{B_{\text{ref}}}$.
4. **Calibration Intercept ($\alpha$):** Estimated from logistic regression with offset logit($p$): $\text{logit}(P(Y=1)) = \alpha + \text{logit}(p)$.
5. **Calibration Slope ($\beta$):** Estimated from logistic regression: $\text{logit}(P(Y=1)) = \alpha_0 + \beta \cdot \text{logit}(p)$.
   - *Interpretation governance:* A slope $< 1$ will be described as predictions tending to be too extreme / overconfident relative to observed rates.
6. **Expected Calibration Error (ECE):** Evaluated across 10 equal-width bins on $[0, 1]$: $\sum_{m=1}^{10} \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$.
7. **Calibration Curve:** 10-bin reliability diagram.
- **Strict Prohibition:** **Do NOT apply post-hoc probability recalibration (Platt scaling or isotonic regression) to final-test predictions.** The raw frozen predictions reflect the true operational performance of the models.

---

## 5. Survey-Design Claim Limit & Scope

- **Analytical Focus:** The primary Phase-5 predictive metrics evaluate individual-level discriminative and screening calibration performance on the untouched test partition.
- **Claim Limitation:** Primary test metrics are **unweighted participant-level metrics** and **must not be claimed as nationally representative U.S. population performance estimates**.
- **Metadata Preservation:** NHANES design variables (`WTPH2YR`, `SDMVSTRA`, `SDMVPSU`) remain preserved in the dataset as descriptive metadata.
- **Strict Prohibition:** **No survey-weighted model re-selection, threshold shifting, or post-hoc alteration is permitted after seeing test results.**

---

## 6. Failure Policy & Recovery Rules

1. **Pre-Prediction Technical Defect:**
   - If Phase-5 code encounters an execution crash or technical defect **before final-test predictions or metrics are generated**:
     - Document the technical failure in the audit log.
     - Repair only the implementation error (e.g., file path, formatting bug).
     - **Do not alter statistical specifications, hyperparameters, or thresholds.**
2. **Post-Prediction Status:**
   - If any valid final-test metrics or predictions have already been generated, **the test set is permanently considered OPENED**.
   - **Under no circumstances may features, preprocessing, configurations, hyperparameters, thresholds, or selection criteria be altered after opening.**

---

## 7. Cryptographic Integrity Signatures

| File Name | Description | SHA256 Hash |
|:---|:---|:---|
| `COMPARATOR_SPECIFICATION_LOCKED.md` | Frozen specification for Logistic Regression & DLNN | *(Computed upon creation)* |
| `comparator_specification.json` | Machine-readable comparator schemas | *(Computed upon creation)* |
| `PHASE5_EVALUATION_PROTOCOL_LOCKED.md` | Single-batch execution, metrics, CIs, failure policy | *(Computed upon creation)* |

---

**FINAL EVALUATION PROTOCOL FROZEN — ALL SPECIFICATIONS IMMUTABLE**
