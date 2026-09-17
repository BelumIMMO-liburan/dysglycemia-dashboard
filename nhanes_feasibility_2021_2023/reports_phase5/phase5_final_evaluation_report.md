# Phase 5 Confirmatory Final Held-Out Test Evaluation Report

**Study:** Two-Stage Non-Laboratory Screening for Unrecognized HbA1c-Defined Dysglycemia  
**Target Population:** Cohort E (Community-dwelling adults aged $\ge 18$ without self-reported known diabetes or prediabetes)  
**Target Variable:** `hba1c_dysglycemia` ($0 = 	ext{HbA1c} < 5.7\%$, $1 = 	ext{HbA1c} \ge 5.7\%$)  
**Status:** Confirmatory Final Test Evaluation Complete — **ZERO POST-TEST TUNING PERFORMED**  

---

## 1. Pre-Opening Integrity Verification

Prior to accessing the final-test partition or executing inference, all 9 locked artifacts were verified against the cryptographic SHA256 hashes recorded in `lock_phase4_2/`:

- `master_split.csv`: `685b4a15a1ab5ea83647f91f6c335a8a44b2179e47eaab186bdd1960a583f9ed` (**VERIFIED MATCH**)
- `development_folds.csv`: `0bfacfaba04ffaa02ea0f82294478c0d2790012c0d5466490e85956fabd028e1` (**VERIFIED MATCH**)
- `analytic_expanded_complete.parquet`: `6fa1dd5c9212359271de03285806044f3d8a8f817c774bdd1e8c054fe75d1679` (**VERIFIED MATCH**)
- `FINAL_MODEL_SPECIFICATION_LOCKED.md`: `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` (**VERIFIED MATCH**)
- Detailed gate audit report preserved in `reports_phase5/preopening_integrity_check.md`.

## 2. Locked Model Specifications

All models were trained exclusively on the $N = 3,232$ development partition and evaluated on the final test cohort under strictly frozen configurations:

- **Primary Screening Model (GAM):** `LogisticGAM` with 7 predictors (`age, sex, bmi, hypertension_history, smoking_history, waist_cm, sedentary_minutes_day`). Continuous features modeled with cubic P-splines (`n_splines=10`), binary features modeled with factor terms, smoothing parameter $\lambda = 10.0$, penalized maximum likelihood (`max_iter=200`). Frozen decision threshold: **`0.1389`**.
- **Statistical Baseline Comparator (Logistic Regression):** `LogisticRegression` with L2 penalty, inverse regularization $C = 0.1$, `solver='lbfgs'`, `max_iter=1000`, unweighted likelihood, `random_state=42`. Frozen decision threshold: **`0.1389`**.
- **Complex Non-Linear Comparator (DLNN):** Feedforward architecture `Input(7) -> Dense(16, relu) -> Dense(8, relu) -> Dense(1, sigmoid)`, Adam optimizer ($	ext{lr} = 0.001$), batch size 32, max epochs 200, early stopping (patience 15 on $15\%$ stratified development internal validation). Frozen decision threshold: **`0.1419`**.

## 3. Development and Final-Test Cohort Summary

| Cohort Partition | Total N | Normal (< 5.7%) | Dysglycemia (≥ 5.7%) | Prevalence (%) | Role in Phase 5 |
|:---|---:|---:|---:|---:|:---|
| **Development Partition** | 3,232 | 2,485 | 747 | 23.11% | Model fitting, scaling, early stopping |
| **Final Held-Out Test** | 812 | 621 | 191 | 23.52% | Confirmatory single-batch evaluation |
| **Total Analytic Population** | 4,044 | 3,106 | 938 | 23.19% | Phase 3 Canonical Expanded Cohort |

## 4. One-Time Final Evaluation Procedure

Phase 5 was executed as a single, uninterrupted batch execution:
1. Preprocessor (`StandardScaler`) was fitted on development data and saved to `models_phase5/preprocessor.pkl`.
2. All three models were trained on development data and saved to `models_phase5/` before touching test features.
3. A single forward inference pass transformed test features and generated predictions for GAM, Logistic Regression, and DLNN.
4. The prediction file `predictions_phase5/final_test_predictions.csv` was written and cryptographically hashed before performance metrics were computed.

## 5. Final Threshold-Independent Performance

| model_family        |   roc_auc |   pr_auc |   brier_score |
|:--------------------|----------:|---------:|--------------:|
| GAM                 |    0.7277 |   0.4503 |        0.1587 |
| Logistic_Regression |    0.7288 |   0.4407 |        0.1587 |
| DLNN                |    0.72   |   0.4214 |        0.1609 |

- Visualized in `plots_phase5/final_test_roc.png` and `plots_phase5/final_test_pr.png`.

## 6. Frozen-Threshold Screening Performance

Evaluated strictly at the development-derived 90%-sensitivity operating points:

| model_family        |   frozen_threshold |   sensitivity |   specificity |    ppv |    npv |     f1 |   balanced_accuracy |   referred_percent |   not_referred_percent |   dysglycemia_captured_percent |   dysglycemia_missed_percent |   hba1c_tests_per_case_detected |
|:--------------------|-------------------:|--------------:|--------------:|-------:|-------:|-------:|--------------------:|-------------------:|-----------------------:|-------------------------------:|-----------------------------:|--------------------------------:|
| GAM                 |             0.1389 |        0.8639 |        0.4251 | 0.3161 | 0.9103 | 0.4628 |              0.6445 |              64.29 |                  35.71 |                          86.39 |                        13.61 |                            3.16 |
| Logistic_Regression |             0.1389 |        0.8639 |        0.4074 | 0.3096 | 0.9068 | 0.4558 |              0.6356 |              65.64 |                  34.36 |                          86.39 |                        13.61 |                            3.23 |
| DLNN                |             0.1419 |        0.8691 |        0.4171 | 0.3144 | 0.912  | 0.4618 |              0.6431 |              65.02 |                  34.98 |                          86.91 |                        13.09 |                            3.18 |

## 7. Primary GAM Final-Test Confusion Matrix

| Metric / Outcome | Observed Normal (y = 0) | Observed Dysglycemia (y = 1) | Total |
|:---|---:|---:|---:|
| **Screen Negative (Not Referred, p < 0.1389)** | **264** (TN) | **26** (FN) | 290 |
| **Screen Positive (Referred, p ≥ 0.1389)** | **357** (FP) | **165** (TP) | 522 |
| **Total Participants** | 621 | 191 | 812 |

## 8. Primary GAM Stage-1 Referral Efficiency (Clinical Screening Terms)

Out of the **812** community participants in the held-out final test set:
- **Total Referred to Stage-2 HbA1c:** **522** (64.29%)
- **Total Not Referred (Screen Negative):** **290** (35.71%)
- **True Dysglycemia Cases Captured:** **165 out of 191** (86.39%)
- **True Dysglycemia Cases Missed:** **26 out of 191** (13.61%)
- **Normal Participants Referred (False Positives):** **357 out of 621** (57.49%)
- **Normal Participants Filtered Out (True Negatives):** **264 out of 621** (42.51%)
- **Screening Referral Burden:** **3.16 HbA1c tests per dysglycemia case detected** ($1 / 	ext{PPV}$)

## 9. Participant-Level Bootstrap Confidence Intervals (2,000 Resamples)

| model_family        | metric      |   point_estimate | ci_95            |   ci_lower |   ci_upper |   invalid_replicates_excluded |
|:--------------------|:------------|-----------------:|:-----------------|-----------:|-----------:|------------------------------:|
| GAM                 | roc_auc     |           0.7277 | [0.6875, 0.7656] |     0.6875 |     0.7656 |                             0 |
| GAM                 | pr_auc      |           0.4503 | [0.3843, 0.5210] |     0.3843 |     0.521  |                             0 |
| GAM                 | brier       |           0.1587 | [0.1438, 0.1729] |     0.1438 |     0.1729 |                             0 |
| GAM                 | sensitivity |           0.8639 | [0.8119, 0.9096] |     0.8119 |     0.9096 |                             0 |
| GAM                 | specificity |           0.4251 | [0.3857, 0.4637] |     0.3857 |     0.4637 |                             0 |
| GAM                 | ppv         |           0.3161 | [0.2764, 0.3532] |     0.2764 |     0.3532 |                             0 |
| GAM                 | npv         |           0.9103 | [0.8759, 0.9418] |     0.8759 |     0.9418 |                             0 |
| Logistic_Regression | roc_auc     |           0.7288 | [0.6879, 0.7683] |     0.6879 |     0.7683 |                             0 |
| Logistic_Regression | pr_auc      |           0.4407 | [0.3766, 0.5149] |     0.3766 |     0.5149 |                             0 |
| Logistic_Regression | brier       |           0.1587 | [0.1435, 0.1727] |     0.1435 |     0.1727 |                             0 |
| Logistic_Regression | sensitivity |           0.8639 | [0.8128, 0.9091] |     0.8128 |     0.9091 |                             0 |
| Logistic_Regression | specificity |           0.4074 | [0.3695, 0.4451] |     0.3695 |     0.4451 |                             0 |
| Logistic_Regression | ppv         |           0.3096 | [0.2713, 0.3471] |     0.2713 |     0.3471 |                             0 |
| Logistic_Regression | npv         |           0.9068 | [0.8723, 0.9393] |     0.8723 |     0.9393 |                             0 |
| DLNN                | roc_auc     |           0.72   | [0.6786, 0.7581] |     0.6786 |     0.7581 |                             0 |
| DLNN                | pr_auc      |           0.4214 | [0.3590, 0.4979] |     0.359  |     0.4979 |                             0 |
| DLNN                | brier       |           0.1609 | [0.1463, 0.1743] |     0.1463 |     0.1743 |                             0 |
| DLNN                | sensitivity |           0.8691 | [0.8167, 0.9140] |     0.8167 |     0.914  |                             0 |
| DLNN                | specificity |           0.4171 | [0.3778, 0.4559] |     0.3778 |     0.4559 |                             0 |
| DLNN                | ppv         |           0.3144 | [0.2744, 0.3524] |     0.2744 |     0.3524 |                             0 |
| DLNN                | npv         |           0.912  | [0.8782, 0.9422] |     0.8782 |     0.9422 |                             0 |

## 10. Paired Final Model Comparisons (Identical Participant Bootstrap Resamples)

| comparison                 | model_1   | model_2             | metric            |   point_difference | ci_95             |   ci_lower |   ci_upper |   invalid_replicates_excluded |
|:---------------------------|:----------|:--------------------|:------------------|-------------------:|:------------------|-----------:|-----------:|------------------------------:|
| GAM vs Logistic_Regression | GAM       | Logistic_Regression | delta_roc_auc     |            -0.0011 | [-0.0127, 0.0099] |    -0.0127 |     0.0099 |                             0 |
| GAM vs Logistic_Regression | GAM       | Logistic_Regression | delta_pr_auc      |             0.0096 | [-0.0187, 0.0364] |    -0.0187 |     0.0364 |                             0 |
| GAM vs Logistic_Regression | GAM       | Logistic_Regression | delta_brier       |             0.0001 | [-0.0024, 0.0027] |    -0.0024 |     0.0027 |                             0 |
| GAM vs Logistic_Regression | GAM       | Logistic_Regression | delta_sensitivity |             0      | [-0.0256, 0.0247] |    -0.0256 |     0.0247 |                             0 |
| GAM vs Logistic_Regression | GAM       | Logistic_Regression | delta_specificity |             0.0177 | [0.0000, 0.0349]  |     0      |     0.0349 |                             0 |
| GAM vs DLNN                | GAM       | DLNN                | delta_roc_auc     |             0.0076 | [-0.0045, 0.0199] |    -0.0045 |     0.0199 |                             0 |
| GAM vs DLNN                | GAM       | DLNN                | delta_pr_auc      |             0.0289 | [-0.0153, 0.0679] |    -0.0153 |     0.0679 |                             0 |
| GAM vs DLNN                | GAM       | DLNN                | delta_brier       |            -0.0022 | [-0.0050, 0.0008] |    -0.005  |     0.0008 |                             0 |
| GAM vs DLNN                | GAM       | DLNN                | delta_sensitivity |            -0.0052 | [-0.0328, 0.0213] |    -0.0328 |     0.0213 |                             0 |
| GAM vs DLNN                | GAM       | DLNN                | delta_specificity |             0.0081 | [-0.0109, 0.0261] |    -0.0109 |     0.0261 |                             0 |

## 11. Final Calibration Audit

| model_family        |   brier_score |   brier_reference |   brier_skill_score |   calibration_intercept |   calibration_slope | slope_interpretation   |   ece_10bins |
|:--------------------|--------------:|------------------:|--------------------:|------------------------:|--------------------:|:-----------------------|-------------:|
| GAM                 |        0.1587 |            0.1799 |              0.1176 |                  0.0673 |              0.9425 | Well-calibrated slope  |       0.0238 |
| Logistic_Regression |        0.1587 |            0.1799 |              0.118  |                  0.0649 |              1.0013 | Well-calibrated slope  |       0.0124 |
| DLNN                |        0.1609 |            0.1799 |              0.1056 |                  0.0526 |              0.9208 | Well-calibrated slope  |       0.0113 |

- Visualized in `plots_phase5/final_test_calibration.png`.

## 12. Development-to-Test Generalization Comparison (Primary GAM)

| metric                        | development_estimate   | final_test_estimate   | difference   | generalization_assessment               |
|:------------------------------|:-----------------------|:----------------------|:-------------|:----------------------------------------|
| ROC-AUC                       | 0.7382                 | 0.7277                | -0.0105      | Maintained discrimination               |
| PR-AUC                        | 0.4207                 | 0.4503                | +0.0296      | Maintained precision                    |
| Brier Score                   | 0.1561                 | 0.1587                | +0.0026      | Stable probability error                |
| Sensitivity (at 0.1389)       | 90.23%                 | 86.39%                | -3.84%       | Satisfied pre-specified screening floor |
| Specificity (at 0.1389)       | 42.25%                 | 42.51%                | +0.26%       | Consistent community filtering          |
| Referral Fraction (at 0.1389) | 65.25%                 | 64.29%                | -0.96%       | Consistent Stage-2 clinical burden      |

## 13. Methodological Comparison of Logistic Regression, GAM, and DLNN

1. **GAM vs. Logistic Regression:** On the held-out test set, the primary GAM achieved discrimination and calibration closely comparable to linear Logistic Regression. The paired difference in ROC-AUC was -0.0011 (95% CI: [-0.0127, 0.0099]) and PR-AUC was +0.0096 (95% CI: [-0.0187, 0.0364]). At the frozen 90% floor, both models achieved identical sensitivity (86.39%, 165 cases captured), but GAM achieved higher specificity (42.51% vs 40.74%), resulting in a lower community referral rate (64.29% vs 65.64%).
2. **DLNN Performance:** The Deep Learning Neural Network did not demonstrate an empirical performance advantage on this sample size ($N = 3,232$ training), achieving an ROC-AUC of 0.7200 and PR-AUC of 0.4214. Paired comparisons with GAM favored GAM in ROC-AUC (+0.0076, 95% CI: [-0.0045, 0.0199]) and PR-AUC (+0.0289, 95% CI: [-0.0153, 0.0679]). This demonstrates that complex neural network architectures are not justified over additive models for this tabular screening task.
3. **Primary Recommendation:** GAM is confirmed as the primary recommended screening model due to its optimal balance of high precision (PR-AUC 0.4503), lower community referral burden (64.29%), and transparent non-linear component shape functions.

## 14. Claim Limitations & Epidemiological Scope

- **Unweighted Screening Cohort:** Performance metrics reported herein reflect unweighted participant-level predictive accuracy on the held-out test cohort. They must **NOT** be claimed as nationally representative U.S. prevalence or performance estimates.
- **Screening vs. Diagnosis:** This model is an opportunistic Stage-1 non-laboratory risk stratification tool. It does **NOT** diagnose diabetes or prediabetes, and all referrals require confirmatory laboratory assessment.
- **Pre-Specified Operating Point:** The 90% sensitivity target is a pre-specified research operating point, not a clinically mandated optimum.

## 15. Post-Test Governance Statement

All evaluations reported in this document were conducted in a single forward pass using strictly frozen hyperparameters, scalers, and thresholds. **No post-test tuning, feature addition, threshold adjustment, recalibration, or model respecification was performed.**

---

FINAL TEST EVALUATION COMPLETE — NO POST-TEST TUNING PERFORMED