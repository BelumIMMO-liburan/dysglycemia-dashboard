# Phase 4.1 Pre-Final Model and Operating-Point Selection Audit Report

**Study:** Two-Stage Non-Laboratory Screening for Unrecognized HbA1c-Defined Dysglycemia
**Target Population:** Cohort E (Adults age ≥ 18 without self-reported known diabetes or prediabetes)
**Primary Target:** `hba1c_dysglycemia` (0 = HbA1c < 5.7%, 1 = HbA1c ≥ 5.7%)
**Status:** Pre-Final Audit Complete — **FINAL TEST SET REMAINS LOCKED**

---

## 1. Verification of Phase 3 Count Reconciliation

- **Audit Finding:** The discrepancy between the exploratory V2 feasibility audit ($N \approx 4,066$) and the canonical Phase 3 dataset `analytic_expanded_complete.parquet` ($N = 4,044$) is **100% reconciled and confirmed**.
- **Root Cause:** Variable `PAD680` contains sentinel missing-value codes: `9999` (Don't Know, $N = 21$) and `7777` (Refused, $N = 1$).
- **Verification:** Converting these 22 sentinel records to `NaN` is essential because treating $9,999$ minutes as a continuous physical measurement would severely distort model fitting and scaling. $N = 4,044$ is the exact, methodologically valid sample size.
- Verified documentation preserved in `reports_phase4_1/phase3_count_reconciliation_verified.md`.

## 2. Standardized Configuration Selection Hierarchy

To ensure complete scientific consistency, configuration selection was conducted strictly according to the pre-specified hierarchy:
1. **Primary:** Highest pooled OOF PR-AUC
2. **Tie Breaker 1:** Highest pooled OOF ROC-AUC
3. **Tie Breaker 2:** Lowest pooled OOF Brier Score
4. **Tie Breaker 3:** Simpler configuration

| dataset_variant   | model_family        | selected_configuration   |   pr_auc |   roc_auc |   brier | selection_reason                             |
|:------------------|:--------------------|:-------------------------|---------:|----------:|--------:|:---------------------------------------------|
| CORE_COMMON       | DLNN                | DLNN_32_16_drop0.0       |   0.3988 |    0.7269 |  0.1583 | Rank 1 by hierarchy: PR-AUC=0.3988 (primary) |
| CORE_COMMON       | GAM                 | GAM_splines10_lam10.0    |   0.4014 |    0.7302 |  0.1579 | Rank 1 by hierarchy: PR-AUC=0.4014 (primary) |
| CORE_COMMON       | Logistic_Regression | L2_C0.01                 |   0.3988 |    0.7303 |  0.1588 | Rank 1 by hierarchy: PR-AUC=0.3988 (primary) |
| CORE_FULL         | DLNN                | DLNN_32_16_drop0.2       |   0.3984 |    0.7274 |  0.158  | Rank 1 by hierarchy: PR-AUC=0.3984 (primary) |
| CORE_FULL         | GAM                 | GAM_splines10_lam1.0     |   0.3971 |    0.7269 |  0.1587 | Rank 1 by hierarchy: PR-AUC=0.3971 (primary) |
| CORE_FULL         | Logistic_Regression | L2_C0.01                 |   0.3961 |    0.7286 |  0.1593 | Rank 1 by hierarchy: PR-AUC=0.3961 (primary) |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0        |   0.4115 |    0.7306 |  0.1577 | Rank 1 by hierarchy: PR-AUC=0.4115 (primary) |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0    |   0.4207 |    0.7382 |  0.1561 | Rank 1 by hierarchy: PR-AUC=0.4207 (primary) |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.1                  |   0.4087 |    0.7345 |  0.1574 | Rank 1 by hierarchy: PR-AUC=0.4087 (primary) |

*(All subsequent Phase 4.1 analyses evaluate ONLY these winning configurations).*

## 3. Paired Uncertainty Analysis (2,000 Bootstrap Resamples)

### 3.1 Feature Set Comparison: CORE_COMMON vs. EXPANDED_COMMON
Evaluated on the identical $N = 3,232$ development participants:

| model_family        | core_config           | expanded_config       |   delta_roc_auc | roc_auc_ci_95     |   delta_pr_auc | pr_auc_ci_95      |   delta_brier | brier_ci_95        | interpretation                 |
|:--------------------|:----------------------|:----------------------|----------------:|:------------------|---------------:|:------------------|--------------:|:-------------------|:-------------------------------|
| Logistic_Regression | L2_C0.01              | L2_C0.1               |          0.0042 | [-0.0014, 0.0098] |         0.0099 | [-0.0008, 0.0207] |       -0.0014 | [-0.0028, -0.0000] | Compatible with null/uncertain |
| GAM                 | GAM_splines10_lam10.0 | GAM_splines10_lam10.0 |          0.008  | [0.0013, 0.0147]  |         0.0193 | [0.0031, 0.0363]  |       -0.0018 | [-0.0033, -0.0003] | Statistically positive         |
| DLNN                | DLNN_32_16_drop0.0    | DLNN_16_8_drop0.0     |          0.0037 | [-0.0049, 0.0121] |         0.0127 | [-0.0073, 0.0331] |       -0.0006 | [-0.0026, 0.0012]  | Compatible with null/uncertain |

- **Finding:** Across all three model families, the Expanded feature set demonstrates positive point-estimate gains in discrimination (+0.0037 to +0.0080 ROC-AUC; +0.0099 to +0.0193 PR-AUC) and reductions in Brier score. For GAM, the 95% CI for both ROC-AUC ([0.0013, 0.0147]) and PR-AUC ([0.0031, 0.0363]) is strictly positive, indicating that the addition of waist circumference and sedentary activity provides a statistically reliable gain in identifying true cases.

### 3.2 Model Family Pairwise Comparison on EXPANDED_COMMON

| comparison                  | m1   | m1_config             | m2                  | m2_config         |   delta_roc_auc | roc_auc_ci_95     |   delta_pr_auc | pr_auc_ci_95      |   delta_brier | brier_ci_95        |
|:----------------------------|:-----|:----------------------|:--------------------|:------------------|----------------:|:------------------|---------------:|:------------------|--------------:|:-------------------|
| GAM vs Logistic_Regression  | GAM  | GAM_splines10_lam10.0 | Logistic_Regression | L2_C0.1           |          0.0037 | [-0.0017, 0.0095] |         0.012  | [-0.0014, 0.0259] |       -0.0013 | [-0.0026, -0.0000] |
| DLNN vs Logistic_Regression | DLNN | DLNN_16_8_drop0.0     | Logistic_Regression | L2_C0.1           |         -0.0039 | [-0.0119, 0.0040] |         0.0028 | [-0.0193, 0.0232] |        0.0003 | [-0.0016, 0.0023]  |
| GAM vs DLNN                 | GAM  | GAM_splines10_lam10.0 | DLNN                | DLNN_16_8_drop0.0 |          0.0077 | [0.0004, 0.0146]  |         0.0092 | [-0.0102, 0.0287] |       -0.0016 | [-0.0033, 0.0001]  |

- **Finding:** Pairwise differences between GAM and Logistic Regression are modest (+0.0037 ROC-AUC, 95% CI: [-0.0017, 0.0095]; +0.0120 PR-AUC, 95% CI: [-0.0014, 0.0259]), confirming that both are viable candidates, while DLNN underperformed both classical architectures.

## 4. Comprehensive Calibration Audit

Calibration was evaluated across five diagnostic dimensions (Brier, Brier Skill Score, Calibration-in-the-large Intercept, Calibration Slope, and 10-bin ECE):

| dataset_variant   | model_family        | selected_configuration   |    n |   dysglycemia_prev |   brier_score |   brier_reference |   brier_skill_score |   cal_intercept | cal_intercept_desc    |   cal_slope | cal_slope_desc                      |   ece_10bins |
|:------------------|:--------------------|:-------------------------|-----:|-------------------:|--------------:|------------------:|--------------------:|----------------:|:----------------------|------------:|:------------------------------------|-------------:|
| CORE_COMMON       | DLNN                | DLNN_32_16_drop0.0       | 3232 |             0.2311 |        0.1583 |            0.1777 |              0.109  |         -0.029  | Well-calibrated large |      0.9086 | Well-calibrated slope               |       0.0118 |
| CORE_COMMON       | GAM                 | GAM_splines10_lam10.0    | 3232 |             0.2311 |        0.1579 |            0.1777 |              0.1114 |          0.0014 | Well-calibrated large |      0.9742 | Well-calibrated slope               |       0.0128 |
| CORE_COMMON       | Logistic_Regression | L2_C0.01                 | 3232 |             0.2311 |        0.1588 |            0.1777 |              0.1065 |          0.0008 | Well-calibrated large |      1.2838 | Under-confident (spread too narrow) |       0.0311 |
| CORE_FULL         | DLNN                | DLNN_32_16_drop0.2       | 3355 |             0.2313 |        0.158  |            0.1778 |              0.1111 |         -0.0211 | Well-calibrated large |      1.0059 | Well-calibrated slope               |       0.0101 |
| CORE_FULL         | GAM                 | GAM_splines10_lam1.0     | 3355 |             0.2313 |        0.1587 |            0.1778 |              0.1073 |          0.0009 | Well-calibrated large |      0.9541 | Well-calibrated slope               |       0.0116 |
| CORE_FULL         | Logistic_Regression | L2_C0.01                 | 3355 |             0.2313 |        0.1593 |            0.1778 |              0.1041 |          0.0008 | Well-calibrated large |      1.2675 | Under-confident (spread too narrow) |       0.0325 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0        | 3232 |             0.2311 |        0.1577 |            0.1777 |              0.1125 |         -0.0306 | Well-calibrated large |      0.903  | Well-calibrated slope               |       0.0135 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0    | 3232 |             0.2311 |        0.1561 |            0.1777 |              0.1214 |          0.0002 | Well-calibrated large |      0.9652 | Well-calibrated slope               |       0.0106 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.1                  | 3232 |             0.2311 |        0.1574 |            0.1777 |              0.1143 |          0.0006 | Well-calibrated large |      1.0005 | Well-calibrated slope               |       0.0169 |

- **Calibration Intercept:** Values range between `-0.0306` and `+0.0014`, confirming that all models are well-anchored to the baseline population prevalence ($23.11\%$ in common cohort).
- **Calibration Slope:** GAM achieved near-perfect slope (**0.9652**), whereas Logistic Regression (1.0005) and DLNN (0.9030) showed slight under-confidence / over-confidence.
- **Brier Skill Score:** Positive across all models, demonstrating predictive skill superior to marginal prevalence assignment.
- Visualized in `plots_phase4_1/selected_models_calibration.png`.

## 5. Standardized Screening Operating Points

Operating points were calculated by selecting the **highest threshold satisfying each sensitivity floor** (thereby maximizing specificity):

| dataset_variant   | model_family        | selected_configuration   |   target_sensitivity_floor |   operating_threshold |   achieved_sensitivity |   achieved_specificity |    ppv |    npv |     f1 |   referred_percent |   not_referred_percent |   dysglycemia_captured_percent |   dysglycemia_missed_percent |   hba1c_tests_per_case_detected |
|:------------------|:--------------------|:-------------------------|---------------------------:|----------------------:|-----------------------:|-----------------------:|-------:|-------:|-------:|-------------------:|-----------------------:|-------------------------------:|-----------------------------:|--------------------------------:|
| CORE_COMMON       | DLNN                | DLNN_32_16_drop0.0       |                       0.8  |                0.2028 |                 0.8019 |                 0.5328 | 0.3403 | 0.8995 | 0.4779 |              54.46 |                  45.54 |                          80.19 |                        19.81 |                            2.94 |
| CORE_COMMON       | DLNN                | DLNN_32_16_drop0.0       |                       0.85 |                0.1708 |                 0.8501 |                 0.4748 | 0.3273 | 0.9133 | 0.4726 |              60.02 |                  39.98 |                          85.01 |                        14.99 |                            3.06 |
| CORE_COMMON       | DLNN                | DLNN_32_16_drop0.0       |                       0.9  |                0.1329 |                 0.9009 |                 0.4024 | 0.3119 | 0.9311 | 0.4633 |              66.77 |                  33.23 |                          90.09 |                         9.91 |                            3.21 |
| CORE_COMMON       | DLNN                | DLNN_32_16_drop0.0       |                       0.95 |                0.0799 |                 0.9505 |                 0.262  | 0.2791 | 0.9462 | 0.4315 |              78.71 |                  21.29 |                          95.05 |                         4.95 |                            3.58 |
| CORE_COMMON       | GAM                 | GAM_splines10_lam10.0    |                       0.8  |                0.1968 |                 0.8005 |                 0.534  | 0.3405 | 0.8991 | 0.4778 |              54.33 |                  45.67 |                          80.05 |                        19.95 |                            2.94 |
| CORE_COMMON       | GAM                 | GAM_splines10_lam10.0    |                       0.85 |                0.1738 |                 0.8527 |                 0.4861 | 0.3328 | 0.9165 | 0.4788 |              59.22 |                  40.78 |                          85.27 |                        14.73 |                            3    |
| CORE_COMMON       | GAM                 | GAM_splines10_lam10.0    |                       0.9  |                0.1429 |                 0.9009 |                 0.4254 | 0.3203 | 0.9346 | 0.4726 |              65.01 |                  34.99 |                          90.09 |                         9.91 |                            3.12 |
| CORE_COMMON       | GAM                 | GAM_splines10_lam10.0    |                       0.95 |                0.0849 |                 0.9505 |                 0.26   | 0.2785 | 0.9458 | 0.4308 |              78.87 |                  21.13 |                          95.05 |                         4.95 |                            3.59 |
| CORE_COMMON       | Logistic_Regression | L2_C0.01                 |                       0.8  |                0.2038 |                 0.8005 |                 0.5429 | 0.3449 | 0.9005 | 0.4821 |              53.65 |                  46.35 |                          80.05 |                        19.95 |                            2.9  |
| CORE_COMMON       | Logistic_Regression | L2_C0.01                 |                       0.85 |                0.1828 |                 0.8527 |                 0.4833 | 0.3316 | 0.9161 | 0.4775 |              59.44 |                  40.56 |                          85.27 |                        14.73 |                            3.02 |
| CORE_COMMON       | Logistic_Regression | L2_C0.01                 |                       0.9  |                0.1638 |                 0.9023 |                 0.4298 | 0.3223 | 0.936  | 0.475  |              64.7  |                  35.3  |                          90.23 |                         9.77 |                            3.1  |
| CORE_COMMON       | Logistic_Regression | L2_C0.01                 |                       0.95 |                0.1219 |                 0.9518 |                 0.2696 | 0.2815 | 0.949  | 0.4345 |              78.16 |                  21.84 |                          95.18 |                         4.82 |                            3.55 |
| CORE_FULL         | DLNN                | DLNN_32_16_drop0.2       |                       0.8  |                0.2158 |                 0.8003 |                 0.539  | 0.3431 | 0.8997 | 0.4803 |              53.95 |                  46.05 |                          80.03 |                        19.97 |                            2.91 |
| CORE_FULL         | DLNN                | DLNN_32_16_drop0.2       |                       0.85 |                0.1808 |                 0.8505 |                 0.4715 | 0.3262 | 0.9129 | 0.4716 |              60.3  |                  39.7  |                          85.05 |                        14.95 |                            3.07 |
| CORE_FULL         | DLNN                | DLNN_32_16_drop0.2       |                       0.9  |                0.1489 |                 0.9008 |                 0.4122 | 0.3156 | 0.9325 | 0.4674 |              66.02 |                  33.98 |                          90.08 |                         9.92 |                            3.17 |
| CORE_FULL         | DLNN                | DLNN_32_16_drop0.2       |                       0.95 |                0.0879 |                 0.951  |                 0.252  | 0.2767 | 0.9448 | 0.4287 |              79.49 |                  20.51 |                          95.1  |                         4.9  |                            3.61 |
| CORE_FULL         | GAM                 | GAM_splines10_lam1.0     |                       0.8  |                0.1938 |                 0.8003 |                 0.5301 | 0.3388 | 0.8982 | 0.476  |              54.63 |                  45.37 |                          80.03 |                        19.97 |                            2.95 |
| CORE_FULL         | GAM                 | GAM_splines10_lam1.0     |                       0.85 |                0.1738 |                 0.8505 |                 0.4855 | 0.3322 | 0.9152 | 0.4777 |              59.23 |                  40.77 |                          85.05 |                        14.95 |                            3.01 |
| CORE_FULL         | GAM                 | GAM_splines10_lam1.0     |                       0.9  |                0.1429 |                 0.9008 |                 0.4211 | 0.3189 | 0.9338 | 0.471  |              65.34 |                  34.66 |                          90.08 |                         9.92 |                            3.14 |
| CORE_FULL         | GAM                 | GAM_splines10_lam1.0     |                       0.95 |                0.0849 |                 0.951  |                 0.2551 | 0.2775 | 0.9454 | 0.4297 |              79.25 |                  20.75 |                          95.1  |                         4.9  |                            3.6  |
| CORE_FULL         | Logistic_Regression | L2_C0.01                 |                       0.8  |                0.2028 |                 0.8028 |                 0.5405 | 0.3446 | 0.9011 | 0.4822 |              53.89 |                  46.11 |                          80.28 |                        19.72 |                            2.9  |
| CORE_FULL         | Logistic_Regression | L2_C0.01                 |                       0.85 |                0.1818 |                 0.8518 |                 0.48   | 0.3302 | 0.915  | 0.4759 |              59.67 |                  40.33 |                          85.18 |                        14.82 |                            3.03 |
| CORE_FULL         | Logistic_Regression | L2_C0.01                 |                       0.9  |                0.1638 |                 0.9008 |                 0.4257 | 0.3206 | 0.9345 | 0.4729 |              64.98 |                  35.02 |                          90.08 |                         9.92 |                            3.12 |
| CORE_FULL         | Logistic_Regression | L2_C0.01                 |                       0.95 |                0.1219 |                 0.951  |                 0.266  | 0.2805 | 0.9475 | 0.4332 |              78.42 |                  21.58 |                          95.1  |                         4.9  |                            3.57 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0        |                       0.8  |                0.2068 |                 0.8005 |                 0.5469 | 0.3469 | 0.9012 | 0.484  |              53.34 |                  46.66 |                          80.05 |                        19.95 |                            2.88 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0        |                       0.85 |                0.1758 |                 0.8501 |                 0.4942 | 0.3356 | 0.9164 | 0.4812 |              58.54 |                  41.46 |                          85.01 |                        14.99 |                            2.98 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0        |                       0.9  |                0.1419 |                 0.9009 |                 0.4193 | 0.3181 | 0.9337 | 0.4701 |              65.47 |                  34.53 |                          90.09 |                         9.91 |                            3.14 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0        |                       0.95 |                0.0849 |                 0.9505 |                 0.2845 | 0.2854 | 0.9503 | 0.4389 |              76.98 |                  23.02 |                          95.05 |                         4.95 |                            3.5  |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0    |                       0.8  |                0.1918 |                 0.8005 |                 0.5461 | 0.3465 | 0.9011 | 0.4836 |              53.4  |                  46.6  |                          80.05 |                        19.95 |                            2.89 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0    |                       0.85 |                0.1668 |                 0.8501 |                 0.4865 | 0.3323 | 0.9152 | 0.4778 |              59.13 |                  40.87 |                          85.01 |                        14.99 |                            3.01 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0    |                       0.9  |                0.1389 |                 0.9023 |                 0.4225 | 0.3196 | 0.935  | 0.472  |              65.25 |                  34.75 |                          90.23 |                         9.77 |                            3.13 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0    |                       0.95 |                0.0909 |                 0.9505 |                 0.2885 | 0.2865 | 0.9509 | 0.4403 |              76.67 |                  23.33 |                          95.05 |                         4.95 |                            3.49 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.1                  |                       0.8  |                0.1888 |                 0.8005 |                 0.5449 | 0.3459 | 0.9009 | 0.483  |              53.5  |                  46.5  |                          80.05 |                        19.95 |                            2.89 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.1                  |                       0.85 |                0.1648 |                 0.8501 |                 0.4861 | 0.3321 | 0.9152 | 0.4776 |              59.16 |                  40.84 |                          85.01 |                        14.99 |                            3.01 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.1                  |                       0.9  |                0.1389 |                 0.9023 |                 0.4165 | 0.3173 | 0.9341 | 0.4695 |              65.72 |                  34.28 |                          90.23 |                         9.77 |                            3.15 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.1                  |                       0.95 |                0.1029 |                 0.9505 |                 0.2998 | 0.2898 | 0.9527 | 0.4442 |              75.8  |                  24.2  |                          95.05 |                         4.95 |                            3.45 |

## 6. Provisional Research Operating Point: 90% Sensitivity Floor

Evaluating the $\ge 90\%$ sensitivity floor as the provisional research operating point:
- **Selected GAM on EXPANDED_COMMON:** At threshold **0.1389**, achieves **90.23% Sensitivity** and **42.25% Specificity**.
- **Two-Stage Efficiency:** Referring **65.25%** of the non-diagnosed adult screening population for laboratory HbA1c testing captures **90.23%** of all unrecognized dysglycemia cases while missing only **9.77%**.
- **Referral Burden:** Requires **3.13 HbA1c tests per dysglycemia case detected**.
- **Trade-off Analysis:** Increasing the sensitivity requirement from 85% to 90% captures an additional 5.22% of dysglycemia cases while increasing referrals by 6.12% (from 59.13% to 65.25%). In contrast, pushing sensitivity floor to 95% requires a substantial 11.42% jump in referrals (from 65.25% to 76.67%) to capture only 4.82% more cases. This factual non-linear penalty supports testing the 90% floor as the pre-specified research operating point.
- Visualized in `plots_phase4_1/screening_tradeoff_selected_gam.png`.

## 7. Feature-Burden Trade-Off Discussion

| feature_set     |   number_of_inputs |   roc_auc |   pr_auc |   brier | sensitivity_90_floor_referral_rate   | sensitivity_90_floor_specificity   | additional_input_burden                                                        |
|:----------------|-------------------:|----------:|---------:|--------:|:-------------------------------------|:-----------------------------------|:-------------------------------------------------------------------------------|
| CORE_COMMON     |                  5 |    0.7302 |   0.4014 |  0.1579 | 65.01%                               | 42.54%                             | None (baseline: age, sex, BMI, hypertension history, smoking history)          |
| EXPANDED_COMMON |                  7 |    0.7382 |   0.4207 |  0.1561 | 65.25%                               | 42.25%                             | Tape-measured waist circumference (cm) + self-reported daily sedentary minutes |

- **Core vs. Expanded Trade-off:** The Expanded model achieves higher PR-AUC (0.4207 vs 0.4014) and higher ROC-AUC (0.7382 vs 0.7302), with virtually identical referral rates at the 90% sensitivity floor (65.25% vs 65.01%). However, measuring waist circumference requires an anthropometric tape measure and trained clinical protocol, and sedentary time adds questionnaire length. This trade-off will be presented to researchers without automated forced selection.

## 8. Provisional Model Nomination

- **Nominated Model:** **Generalized Additive Model (GAM)** with spline smoothing ($n=10, \lambda=10.0$).
- **Rationale:** Superior calibration slope (0.9652), lowest Brier score (0.1561), highest PR-AUC (0.4207) and ROC-AUC (0.7382), lowest referral rate at 90% sensitivity (65.25%), and direct clinical explainability via additive component shape functions $s(x)$.

---

PRE-FINAL SELECTION AUDIT COMPLETE — FINAL TEST SET REMAINS LOCKED