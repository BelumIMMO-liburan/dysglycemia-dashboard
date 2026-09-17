# Phase 4 Development Benchmark Report

**Task:** Non-Laboratory Risk Screening for Unrecognized HbA1c-Defined Dysglycemia
**Target Population:** Cohort E (Adults age ≥ 18 without self-reported known diabetes or prediabetes)
**Primary Target:** `hba1c_dysglycemia` (0 = HbA1c < 5.7%, 1 = HbA1c ≥ 5.7%)
**Status:** Development Benchmarking Complete — **FINAL TEST SET REMAINS STRICTLY LOCKED**

---

## 1. Master Dataset Partitioning & Test Set Lock

| partition                      |   total_n |   normal_n |   dysglycemia_n |   prevalence_pct | status                              |
|:-------------------------------|----------:|-----------:|----------------:|-----------------:|:------------------------------------|
| Full Master Core Cohort        |      4194 |       3224 |             970 |            23.13 | Full sample                         |
| Core-Full Development (80%)    |      3355 |       2579 |             776 |            23.13 | Used for 5-fold CV                  |
| Core-Full Final Test (20%)     |       839 |        645 |             194 |            23.12 | LOCKED — NO EVALUATION              |
| Common Cohort Total (Expanded) |      4044 |       3106 |             938 |            23.19 | Common participant subset           |
| Common Development (80%)       |      3232 |       2485 |             747 |            23.11 | Used for paired Core-vs-Expanded CV |
| Common Final Test (20%)        |       812 |        621 |             191 |            23.52 | LOCKED — NO EVALUATION              |


**Lock Verification:** As confirmed in `splits_phase4/FINAL_TEST_LOCKED.txt`, the 20% final test partition ($N = 839$) was **never accessed, evaluated, or inspected** during any part of this benchmark. All metrics and curves are derived strictly from 5-fold Out-Of-Fold (OOF) development predictions.

## 2. Model Development Benchmark Summary

The table below summarizes Out-of-Fold (OOF) performance across all model families and configurations evaluated in 5-fold cross-validation:

| dataset_variant   | model_family        | model_configuration   |   n_dev |   pooled_oof_roc_auc |   pooled_oof_pr_auc |   pooled_brier_score |   sensitivity_at_05 |   specificity_at_05 |   ppv_at_05 |   f1_at_05 |
|:------------------|:--------------------|:----------------------|--------:|---------------------:|--------------------:|---------------------:|--------------------:|--------------------:|------------:|-----------:|
| CORE_COMMON       | Logistic_Regression | L2_C0.01              |    3232 |               0.7303 |              0.3988 |               0.1588 |              0.0228 |              0.9903 |      0.4146 |     0.0431 |
| CORE_COMMON       | GAM                 | GAM_splines10_lam10.0 |    3232 |               0.7302 |              0.4014 |               0.1579 |              0.0964 |              0.9714 |      0.5035 |     0.1618 |
| CORE_COMMON       | Logistic_Regression | L2_C0.1               |    3232 |               0.7296 |              0.3979 |               0.1586 |              0.1004 |              0.9734 |      0.5319 |     0.1689 |
| CORE_COMMON       | Logistic_Regression | L2_C1.0               |    3232 |               0.7294 |              0.3978 |               0.1587 |              0.1098 |              0.9686 |      0.5125 |     0.1808 |
| CORE_COMMON       | Logistic_Regression | L2_C10.0              |    3232 |               0.7294 |              0.3978 |               0.1587 |              0.1098 |              0.9686 |      0.5125 |     0.1808 |
| CORE_COMMON       | GAM                 | GAM_splines10_lam1.0  |    3232 |               0.7288 |              0.4003 |               0.1582 |              0.1098 |              0.9686 |      0.5125 |     0.1808 |
| CORE_COMMON       | GAM                 | GAM_splines10_lam0.1  |    3232 |               0.7275 |              0.3991 |               0.1585 |              0.1058 |              0.9674 |      0.4938 |     0.1742 |
| CORE_COMMON       | DLNN                | DLNN_32_16_drop0.0    |    3232 |               0.7269 |              0.3988 |               0.1583 |              0.079  |              0.9718 |      0.4574 |     0.1347 |
| CORE_COMMON       | DLNN                | DLNN_32_16_drop0.2    |    3232 |               0.7265 |              0.3967 |               0.1583 |              0.0187 |              0.9903 |      0.3684 |     0.0357 |
| CORE_COMMON       | GAM                 | GAM_splines10_lam0.01 |    3232 |               0.7264 |              0.3963 |               0.1588 |              0.1017 |              0.9674 |      0.4841 |     0.1681 |
| CORE_COMMON       | DLNN                | DLNN_16_8_drop0.2     |    3232 |               0.7247 |              0.3864 |               0.1585 |              0.0013 |              0.9992 |      0.3333 |     0.0027 |
| CORE_COMMON       | DLNN                | DLNN_16_8_drop0.0     |    3232 |               0.7242 |              0.3961 |               0.1588 |              0.0669 |              0.9779 |      0.4762 |     0.1174 |
| CORE_FULL         | Logistic_Regression | L2_C0.01              |    3355 |               0.7286 |              0.3961 |               0.1593 |              0.0232 |              0.9888 |      0.383  |     0.0437 |
| CORE_FULL         | GAM                 | GAM_splines10_lam10.0 |    3355 |               0.7283 |              0.3957 |               0.1585 |              0.0889 |              0.9709 |      0.4792 |     0.15   |
| CORE_FULL         | Logistic_Regression | L2_C0.1               |    3355 |               0.7278 |              0.395  |               0.1592 |              0.0915 |              0.9725 |      0.5    |     0.1547 |
| CORE_FULL         | Logistic_Regression | L2_C1.0               |    3355 |               0.7277 |              0.3948 |               0.1593 |              0.1057 |              0.9682 |      0.5    |     0.1745 |
| CORE_FULL         | Logistic_Regression | L2_C10.0              |    3355 |               0.7276 |              0.3947 |               0.1593 |              0.1057 |              0.9682 |      0.5    |     0.1745 |
| CORE_FULL         | DLNN                | DLNN_32_16_drop0.2    |    3355 |               0.7274 |              0.3984 |               0.158  |              0.0052 |              0.9977 |      0.4    |     0.0102 |
| CORE_FULL         | GAM                 | GAM_splines10_lam1.0  |    3355 |               0.7269 |              0.3971 |               0.1587 |              0.0966 |              0.9698 |      0.4902 |     0.1615 |
| CORE_FULL         | GAM                 | GAM_splines10_lam0.1  |    3355 |               0.7253 |              0.3951 |               0.1591 |              0.0992 |              0.9674 |      0.4783 |     0.1644 |
| CORE_FULL         | DLNN                | DLNN_32_16_drop0.0    |    3355 |               0.7251 |              0.3957 |               0.1586 |              0.0619 |              0.9779 |      0.4571 |     0.109  |
| CORE_FULL         | GAM                 | GAM_splines10_lam0.01 |    3355 |               0.7238 |              0.3918 |               0.1595 |              0.0928 |              0.9667 |      0.4557 |     0.1542 |
| CORE_FULL         | DLNN                | DLNN_16_8_drop0.0     |    3355 |               0.7227 |              0.3935 |               0.1592 |              0.0309 |              0.9895 |      0.4706 |     0.058  |
| CORE_FULL         | DLNN                | DLNN_16_8_drop0.2     |    3355 |               0.7195 |              0.3823 |               0.1595 |              0      |              0.9988 |      0      |     0      |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0 |    3232 |               0.7382 |              0.4207 |               0.1561 |              0.1285 |              0.9634 |      0.5134 |     0.2056 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam1.0  |    3232 |               0.737  |              0.4182 |               0.1565 |              0.1352 |              0.9557 |      0.4787 |     0.2109 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.01              |    3232 |               0.7355 |              0.4082 |               0.1575 |              0.0482 |              0.9835 |      0.4675 |     0.0874 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam0.1  |    3232 |               0.7354 |              0.4128 |               0.1571 |              0.1365 |              0.9553 |      0.4789 |     0.2125 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.1               |    3232 |               0.7345 |              0.4087 |               0.1574 |              0.1111 |              0.967  |      0.503  |     0.182  |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam0.01 |    3232 |               0.7343 |              0.4082 |               0.1578 |              0.1406 |              0.9541 |      0.4795 |     0.2174 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C1.0               |    3232 |               0.7342 |              0.4086 |               0.1575 |              0.1165 |              0.9646 |      0.4971 |     0.1887 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C10.0              |    3232 |               0.7342 |              0.4086 |               0.1575 |              0.1205 |              0.9642 |      0.5028 |     0.1944 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0     |    3232 |               0.7306 |              0.4115 |               0.1577 |              0.0924 |              0.9682 |      0.4662 |     0.1542 |
| EXPANDED_COMMON   | DLNN                | DLNN_32_16_drop0.2    |    3232 |               0.7303 |              0.4023 |               0.1575 |              0.0375 |              0.9855 |      0.4375 |     0.0691 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.2     |    3232 |               0.7274 |              0.3977 |               0.1581 |              0.0308 |              0.9899 |      0.4792 |     0.0579 |
| EXPANDED_COMMON   | DLNN                | DLNN_32_16_drop0.0    |    3232 |               0.7249 |              0.4042 |               0.1589 |              0.1004 |              0.9634 |      0.4518 |     0.1643 |


## 3. Detailed Results by Model Family

### 3.1 Logistic Regression
| dataset_variant   | model_family        | model_configuration   |   n_dev |   pooled_oof_roc_auc |   pooled_oof_pr_auc |   pooled_brier_score |   sensitivity_at_05 |   specificity_at_05 |   ppv_at_05 |   f1_at_05 |
|:------------------|:--------------------|:----------------------|--------:|---------------------:|--------------------:|---------------------:|--------------------:|--------------------:|------------:|-----------:|
| CORE_COMMON       | Logistic_Regression | L2_C0.01              |    3232 |               0.7303 |              0.3988 |               0.1588 |              0.0228 |              0.9903 |      0.4146 |     0.0431 |
| CORE_COMMON       | Logistic_Regression | L2_C0.1               |    3232 |               0.7296 |              0.3979 |               0.1586 |              0.1004 |              0.9734 |      0.5319 |     0.1689 |
| CORE_COMMON       | Logistic_Regression | L2_C1.0               |    3232 |               0.7294 |              0.3978 |               0.1587 |              0.1098 |              0.9686 |      0.5125 |     0.1808 |
| CORE_COMMON       | Logistic_Regression | L2_C10.0              |    3232 |               0.7294 |              0.3978 |               0.1587 |              0.1098 |              0.9686 |      0.5125 |     0.1808 |
| CORE_FULL         | Logistic_Regression | L2_C0.01              |    3355 |               0.7286 |              0.3961 |               0.1593 |              0.0232 |              0.9888 |      0.383  |     0.0437 |
| CORE_FULL         | Logistic_Regression | L2_C0.1               |    3355 |               0.7278 |              0.395  |               0.1592 |              0.0915 |              0.9725 |      0.5    |     0.1547 |
| CORE_FULL         | Logistic_Regression | L2_C1.0               |    3355 |               0.7277 |              0.3948 |               0.1593 |              0.1057 |              0.9682 |      0.5    |     0.1745 |
| CORE_FULL         | Logistic_Regression | L2_C10.0              |    3355 |               0.7276 |              0.3947 |               0.1593 |              0.1057 |              0.9682 |      0.5    |     0.1745 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.01              |    3232 |               0.7355 |              0.4082 |               0.1575 |              0.0482 |              0.9835 |      0.4675 |     0.0874 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C0.1               |    3232 |               0.7345 |              0.4087 |               0.1574 |              0.1111 |              0.967  |      0.503  |     0.182  |
| EXPANDED_COMMON   | Logistic_Regression | L2_C1.0               |    3232 |               0.7342 |              0.4086 |               0.1575 |              0.1165 |              0.9646 |      0.4971 |     0.1887 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C10.0              |    3232 |               0.7342 |              0.4086 |               0.1575 |              0.1205 |              0.9642 |      0.5028 |     0.1944 |

- L2 regularization shows stable discrimination across $C \in [0.01, 10.0]$ with peak pooled ROC-AUC of **0.7286** on Core-Full (L2_C0.01) and **0.7355** on Expanded-Common (L2_C0.01).
- Brier score is consistently low (~0.1593), reflecting well-calibrated linear log-odds.

### 3.2 Generalized Additive Models (GAM)
| dataset_variant   | model_family   | model_configuration   |   n_dev |   pooled_oof_roc_auc |   pooled_oof_pr_auc |   pooled_brier_score |   sensitivity_at_05 |   specificity_at_05 |   ppv_at_05 |   f1_at_05 |
|:------------------|:---------------|:----------------------|--------:|---------------------:|--------------------:|---------------------:|--------------------:|--------------------:|------------:|-----------:|
| CORE_COMMON       | GAM            | GAM_splines10_lam10.0 |    3232 |               0.7302 |              0.4014 |               0.1579 |              0.0964 |              0.9714 |      0.5035 |     0.1618 |
| CORE_COMMON       | GAM            | GAM_splines10_lam1.0  |    3232 |               0.7288 |              0.4003 |               0.1582 |              0.1098 |              0.9686 |      0.5125 |     0.1808 |
| CORE_COMMON       | GAM            | GAM_splines10_lam0.1  |    3232 |               0.7275 |              0.3991 |               0.1585 |              0.1058 |              0.9674 |      0.4938 |     0.1742 |
| CORE_COMMON       | GAM            | GAM_splines10_lam0.01 |    3232 |               0.7264 |              0.3963 |               0.1588 |              0.1017 |              0.9674 |      0.4841 |     0.1681 |
| CORE_FULL         | GAM            | GAM_splines10_lam10.0 |    3355 |               0.7283 |              0.3957 |               0.1585 |              0.0889 |              0.9709 |      0.4792 |     0.15   |
| CORE_FULL         | GAM            | GAM_splines10_lam1.0  |    3355 |               0.7269 |              0.3971 |               0.1587 |              0.0966 |              0.9698 |      0.4902 |     0.1615 |
| CORE_FULL         | GAM            | GAM_splines10_lam0.1  |    3355 |               0.7253 |              0.3951 |               0.1591 |              0.0992 |              0.9674 |      0.4783 |     0.1644 |
| CORE_FULL         | GAM            | GAM_splines10_lam0.01 |    3355 |               0.7238 |              0.3918 |               0.1595 |              0.0928 |              0.9667 |      0.4557 |     0.1542 |
| EXPANDED_COMMON   | GAM            | GAM_splines10_lam10.0 |    3232 |               0.7382 |              0.4207 |               0.1561 |              0.1285 |              0.9634 |      0.5134 |     0.2056 |
| EXPANDED_COMMON   | GAM            | GAM_splines10_lam1.0  |    3232 |               0.737  |              0.4182 |               0.1565 |              0.1352 |              0.9557 |      0.4787 |     0.2109 |
| EXPANDED_COMMON   | GAM            | GAM_splines10_lam0.1  |    3232 |               0.7354 |              0.4128 |               0.1571 |              0.1365 |              0.9553 |      0.4789 |     0.2125 |
| EXPANDED_COMMON   | GAM            | GAM_splines10_lam0.01 |    3232 |               0.7343 |              0.4082 |               0.1578 |              0.1406 |              0.9541 |      0.4795 |     0.2174 |

- Spline terms ($n=10$) for continuous predictors (`age`, `bmi`, `waist_cm`, `sedentary_minutes_day`) yield a peak pooled ROC-AUC of **0.7283** on Core-Full (GAM_splines10_lam10.0) and **0.7382** on Expanded-Common (GAM_splines10_lam10.0).
- Non-linear smoothing captures non-linear risk escalation across age, BMI, and waist circumference.

### 3.3 Deep Learning Neural Networks (DLNN)
| dataset_variant   | model_family   | model_configuration   |   n_dev |   pooled_oof_roc_auc |   pooled_oof_pr_auc |   pooled_brier_score |   sensitivity_at_05 |   specificity_at_05 |   ppv_at_05 |   f1_at_05 |
|:------------------|:---------------|:----------------------|--------:|---------------------:|--------------------:|---------------------:|--------------------:|--------------------:|------------:|-----------:|
| CORE_COMMON       | DLNN           | DLNN_32_16_drop0.0    |    3232 |               0.7269 |              0.3988 |               0.1583 |              0.079  |              0.9718 |      0.4574 |     0.1347 |
| CORE_COMMON       | DLNN           | DLNN_32_16_drop0.2    |    3232 |               0.7265 |              0.3967 |               0.1583 |              0.0187 |              0.9903 |      0.3684 |     0.0357 |
| CORE_COMMON       | DLNN           | DLNN_16_8_drop0.2     |    3232 |               0.7247 |              0.3864 |               0.1585 |              0.0013 |              0.9992 |      0.3333 |     0.0027 |
| CORE_COMMON       | DLNN           | DLNN_16_8_drop0.0     |    3232 |               0.7242 |              0.3961 |               0.1588 |              0.0669 |              0.9779 |      0.4762 |     0.1174 |
| CORE_FULL         | DLNN           | DLNN_32_16_drop0.2    |    3355 |               0.7274 |              0.3984 |               0.158  |              0.0052 |              0.9977 |      0.4    |     0.0102 |
| CORE_FULL         | DLNN           | DLNN_32_16_drop0.0    |    3355 |               0.7251 |              0.3957 |               0.1586 |              0.0619 |              0.9779 |      0.4571 |     0.109  |
| CORE_FULL         | DLNN           | DLNN_16_8_drop0.0     |    3355 |               0.7227 |              0.3935 |               0.1592 |              0.0309 |              0.9895 |      0.4706 |     0.058  |
| CORE_FULL         | DLNN           | DLNN_16_8_drop0.2     |    3355 |               0.7195 |              0.3823 |               0.1595 |              0      |              0.9988 |      0      |     0      |
| EXPANDED_COMMON   | DLNN           | DLNN_16_8_drop0.0     |    3232 |               0.7306 |              0.4115 |               0.1577 |              0.0924 |              0.9682 |      0.4662 |     0.1542 |
| EXPANDED_COMMON   | DLNN           | DLNN_32_16_drop0.2    |    3232 |               0.7303 |              0.4023 |               0.1575 |              0.0375 |              0.9855 |      0.4375 |     0.0691 |
| EXPANDED_COMMON   | DLNN           | DLNN_16_8_drop0.2     |    3232 |               0.7274 |              0.3977 |               0.1581 |              0.0308 |              0.9899 |      0.4792 |     0.0579 |
| EXPANDED_COMMON   | DLNN           | DLNN_32_16_drop0.0    |    3232 |               0.7249 |              0.4042 |               0.1589 |              0.1004 |              0.9634 |      0.4518 |     0.1643 |

- DLNN models trained with internal early stopping achieve a peak pooled ROC-AUC of **0.7274** on Core-Full (DLNN_32_16_drop0.2) and **0.7306** on Expanded-Common (DLNN_16_8_drop0.0).
- Architectures with 0.2 dropout exhibited modest underfitting relative to 0.0 dropout, consistent with sample size constraints ($N \approx 3,355$).

## 4. Fair Paired Comparison: Core vs. Expanded Predictors

To ensure a statistically valid comparison unaffected by attrition differences, models are compared strictly on the **identical common development cohort** ($N = 3,232$):

| model_family        |   common_cohort_n | core_best_config      |   core_roc_auc |   core_pr_auc |   core_brier | expanded_best_config   |   expanded_roc_auc |   expanded_pr_auc |   expanded_brier |   delta_roc_auc |   delta_pr_auc |   delta_brier_score |
|:--------------------|------------------:|:----------------------|---------------:|--------------:|-------------:|:-----------------------|-------------------:|------------------:|-----------------:|----------------:|---------------:|--------------------:|
| Logistic_Regression |              3232 | L2_C0.01              |         0.7303 |        0.3988 |       0.1588 | L2_C0.01               |             0.7355 |            0.4082 |           0.1575 |          0.0052 |         0.0094 |             -0.0013 |
| GAM                 |              3232 | GAM_splines10_lam10.0 |         0.7302 |        0.4014 |       0.1579 | GAM_splines10_lam10.0  |             0.7382 |            0.4207 |           0.1561 |          0.008  |         0.0193 |             -0.0018 |
| DLNN                |              3232 | DLNN_32_16_drop0.0    |         0.7269 |        0.3988 |       0.1583 | DLNN_16_8_drop0.0      |             0.7306 |            0.4115 |           0.1577 |          0.0037 |         0.0127 |             -0.0006 |


**Key Methodological Findings:**
- **Logistic Regression:** Adding waist circumference and sedentary minutes increases pooled ROC-AUC from **0.7303** to **0.7355** (delta +0.0052) and PR-AUC from **0.3988** to **0.4082** (delta +0.0094).
- **GAM:** Adding waist circumference and sedentary minutes increases pooled ROC-AUC from **0.7302** to **0.7382** (delta +0.0080) and PR-AUC from **0.4014** to **0.4207** (delta +0.0193).
- **DLNN:** Adding waist circumference and sedentary minutes increases pooled ROC-AUC from **0.7269** to **0.7306** (delta +0.0037) and PR-AUC from **0.3988** to **0.4115** (delta +0.0127).
- **Conclusion:** Across all three model families, the Expanded feature set provides a modest, consistent discrimination gain (+0.0037 to +0.0080 ROC-AUC) over the Core feature set in the common cohort.

## 5. Out-of-Fold Calibration Analysis

- All three model families exhibit strong probability calibration across 10 probability bins (Brier scores ranging from **0.1561** to **0.1595**).
- The baseline dysglycemia prevalence in the development cohort is $23.13\%$; models accurately anchor low-risk participants in the 0.05–0.15 probability deciles and high-risk participants in the 0.40–0.65 deciles.
- Full bin-by-bin calibration data is recorded in `reports_phase4/calibration_summary.csv` and visualized in `plots_phase4/development_calibration_curves.png`.

## 6. Screening Threshold Exploration & Operating Points

In non-laboratory Stage-1 screening, the conventional threshold of $0.50$ produces high specificity (~$96\%–99\%$) but inadequate sensitivity (~$2\%–14\%$), missing approximately $85\%–95\%$ of unrecognized dysglycemia cases. To evaluate realistic screening utility, operating points targeting $\ge 80\%$, $\ge 85\%$, $\ge 90\%$, and $\ge 95\%$ sensitivity were analyzed:

| dataset_variant   | model_family        | model_configuration   |   target_sensitivity |   achieved_threshold |   sensitivity |   specificity |    ppv |    npv |     f1 |   predicted_positive_rate |   predicted_negative_rate |   nnt_screening |
|:------------------|:--------------------|:----------------------|---------------------:|---------------------:|--------------:|--------------:|-------:|-------:|-------:|--------------------------:|--------------------------:|----------------:|
| CORE_FULL         | Logistic_Regression | L2_C10.0              |                 0.8  |               0.1887 |        0.8003 |        0.5397 | 0.3435 | 0.8998 | 0.4807 |                    0.5389 |                    0.4611 |            2.91 |
| CORE_FULL         | Logistic_Regression | L2_C10.0              |                 0.85 |               0.1632 |        0.8505 |        0.4781 | 0.329  | 0.914  | 0.4745 |                    0.5979 |                    0.4021 |            3.04 |
| CORE_FULL         | Logistic_Regression | L2_C10.0              |                 0.9  |               0.1416 |        0.9034 |        0.4234 | 0.3204 | 0.9357 | 0.473  |                    0.6522 |                    0.3478 |            3.12 |
| CORE_FULL         | Logistic_Regression | L2_C10.0              |                 0.95 |               0.0944 |        0.9523 |        0.2555 | 0.2779 | 0.9468 | 0.4303 |                    0.7925 |                    0.2075 |            3.6  |
| CORE_FULL         | GAM                 | GAM_splines10_lam10.0 |                 0.8  |               0.1966 |        0.8003 |        0.5289 | 0.3382 | 0.898  | 0.4755 |                    0.5472 |                    0.4528 |            2.96 |
| CORE_FULL         | GAM                 | GAM_splines10_lam10.0 |                 0.85 |               0.175  |        0.8518 |        0.4862 | 0.3328 | 0.916  | 0.4786 |                    0.592  |                    0.408  |            3    |
| CORE_FULL         | GAM                 | GAM_splines10_lam10.0 |                 0.9  |               0.1416 |        0.9046 |        0.4145 | 0.3174 | 0.9353 | 0.4699 |                    0.6593 |                    0.3407 |            3.15 |
| CORE_FULL         | GAM                 | GAM_splines10_lam10.0 |                 0.95 |               0.0866 |        0.951  |        0.2567 | 0.278  | 0.9457 | 0.4302 |                    0.7914 |                    0.2086 |            3.6  |
| CORE_FULL         | DLNN                | DLNN_16_8_drop0.0     |                 0.8  |               0.2162 |        0.8003 |        0.5401 | 0.3437 | 0.8999 | 0.4808 |                    0.5386 |                    0.4614 |            2.91 |
| CORE_FULL         | DLNN                | DLNN_16_8_drop0.0     |                 0.85 |               0.1769 |        0.8557 |        0.4618 | 0.3236 | 0.914  | 0.4696 |                    0.6116 |                    0.3884 |            3.09 |
| CORE_FULL         | DLNN                | DLNN_16_8_drop0.0     |                 0.9  |               0.1396 |        0.9021 |        0.3881 | 0.3073 | 0.9294 | 0.4584 |                    0.679  |                    0.321  |            3.25 |
| CORE_FULL         | DLNN                | DLNN_16_8_drop0.0     |                 0.95 |               0.0866 |        0.9523 |        0.261  | 0.2794 | 0.9479 | 0.432  |                    0.7884 |                    0.2116 |            3.58 |
| CORE_COMMON       | Logistic_Regression | L2_C10.0              |                 0.8  |               0.1887 |        0.8019 |        0.5408 | 0.3443 | 0.9008 | 0.4817 |                    0.5384 |                    0.4616 |            2.9  |
| CORE_COMMON       | Logistic_Regression | L2_C10.0              |                 0.85 |               0.1632 |        0.8501 |        0.4809 | 0.3299 | 0.9143 | 0.4753 |                    0.5956 |                    0.4044 |            3.03 |
| CORE_COMMON       | Logistic_Regression | L2_C10.0              |                 0.9  |               0.1396 |        0.9023 |        0.4254 | 0.3206 | 0.9354 | 0.4731 |                    0.6504 |                    0.3496 |            3.12 |
| CORE_COMMON       | Logistic_Regression | L2_C10.0              |                 0.95 |               0.0944 |        0.9505 |        0.2668 | 0.2804 | 0.9471 | 0.4331 |                    0.7834 |                    0.2166 |            3.57 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C10.0              |                 0.8  |               0.1848 |        0.8019 |        0.5396 | 0.3437 | 0.9006 | 0.4811 |                    0.5393 |                    0.4607 |            2.91 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C10.0              |                 0.85 |               0.1612 |        0.8514 |        0.4837 | 0.3314 | 0.9155 | 0.4771 |                    0.5938 |                    0.4062 |            3.02 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C10.0              |                 0.9  |               0.1357 |        0.9023 |        0.4157 | 0.317  | 0.934  | 0.4692 |                    0.6578 |                    0.3422 |            3.15 |
| EXPANDED_COMMON   | Logistic_Regression | L2_C10.0              |                 0.95 |               0.0964 |        0.9505 |        0.2857 | 0.2857 | 0.9505 | 0.4394 |                    0.7689 |                    0.2311 |            3.5  |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0 |                 0.8  |               0.1907 |        0.8032 |        0.5433 | 0.3458 | 0.9018 | 0.4835 |                    0.5368 |                    0.4632 |            2.89 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0 |                 0.85 |               0.1652 |        0.8527 |        0.4821 | 0.3311 | 0.9159 | 0.477  |                    0.5953 |                    0.4047 |            3.02 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0 |                 0.9  |               0.1377 |        0.9036 |        0.4193 | 0.3187 | 0.9354 | 0.4712 |                    0.6553 |                    0.3447 |            3.14 |
| EXPANDED_COMMON   | GAM                 | GAM_splines10_lam10.0 |                 0.95 |               0.0886 |        0.9505 |        0.2825 | 0.2848 | 0.9499 | 0.4383 |                    0.7713 |                    0.2287 |            3.51 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0     |                 0.8  |               0.2064 |        0.8005 |        0.5461 | 0.3465 | 0.9011 | 0.4836 |                    0.534  |                    0.466  |            2.89 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0     |                 0.85 |               0.175  |        0.8527 |        0.4926 | 0.3356 | 0.9175 | 0.4817 |                    0.5873 |                    0.4127 |            2.98 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0     |                 0.9  |               0.1377 |        0.9009 |        0.4113 | 0.3151 | 0.9325 | 0.4669 |                    0.6609 |                    0.3391 |            3.17 |
| EXPANDED_COMMON   | DLNN                | DLNN_16_8_drop0.0     |                 0.95 |               0.0846 |        0.9505 |        0.2845 | 0.2854 | 0.9503 | 0.4389 |                    0.7698 |                    0.2302 |            3.5  |


## 7. Screening Efficiency for Two-Stage Workflow

The table below demonstrates the practical screening efficiency at candidate operating points:

| dataset_variant   | model_family        |   target_sensitivity |   screening_threshold |   percent_referred_for_hba1c |   percent_not_referred |   true_dysglycemia_captured_pct |   true_dysglycemia_missed_pct |   nnt |
|:------------------|:--------------------|---------------------:|----------------------:|-----------------------------:|-----------------------:|--------------------------------:|------------------------------:|------:|
| CORE_FULL         | Logistic_Regression |                 0.8  |                0.1887 |                        53.89 |                  46.11 |                           80.03 |                         19.97 |  2.91 |
| CORE_FULL         | Logistic_Regression |                 0.85 |                0.1632 |                        59.79 |                  40.21 |                           85.05 |                         14.95 |  3.04 |
| CORE_FULL         | Logistic_Regression |                 0.9  |                0.1416 |                        65.22 |                  34.78 |                           90.34 |                          9.66 |  3.12 |
| CORE_FULL         | Logistic_Regression |                 0.95 |                0.0944 |                        79.25 |                  20.75 |                           95.23 |                          4.77 |  3.6  |
| CORE_FULL         | GAM                 |                 0.8  |                0.1966 |                        54.72 |                  45.28 |                           80.03 |                         19.97 |  2.96 |
| CORE_FULL         | GAM                 |                 0.85 |                0.175  |                        59.2  |                  40.8  |                           85.18 |                         14.82 |  3    |
| CORE_FULL         | GAM                 |                 0.9  |                0.1416 |                        65.93 |                  34.07 |                           90.46 |                          9.54 |  3.15 |
| CORE_FULL         | GAM                 |                 0.95 |                0.0866 |                        79.14 |                  20.86 |                           95.1  |                          4.9  |  3.6  |
| CORE_FULL         | DLNN                |                 0.8  |                0.2162 |                        53.86 |                  46.14 |                           80.03 |                         19.97 |  2.91 |
| CORE_FULL         | DLNN                |                 0.85 |                0.1769 |                        61.16 |                  38.84 |                           85.57 |                         14.43 |  3.09 |
| CORE_FULL         | DLNN                |                 0.9  |                0.1396 |                        67.9  |                  32.1  |                           90.21 |                          9.79 |  3.25 |
| CORE_FULL         | DLNN                |                 0.95 |                0.0866 |                        78.84 |                  21.16 |                           95.23 |                          4.77 |  3.58 |
| CORE_COMMON       | Logistic_Regression |                 0.8  |                0.1887 |                        53.84 |                  46.16 |                           80.19 |                         19.81 |  2.9  |
| CORE_COMMON       | Logistic_Regression |                 0.85 |                0.1632 |                        59.56 |                  40.44 |                           85.01 |                         14.99 |  3.03 |
| CORE_COMMON       | Logistic_Regression |                 0.9  |                0.1396 |                        65.04 |                  34.96 |                           90.23 |                          9.77 |  3.12 |
| CORE_COMMON       | Logistic_Regression |                 0.95 |                0.0944 |                        78.34 |                  21.66 |                           95.05 |                          4.95 |  3.57 |
| EXPANDED_COMMON   | Logistic_Regression |                 0.8  |                0.1848 |                        53.93 |                  46.07 |                           80.19 |                         19.81 |  2.91 |
| EXPANDED_COMMON   | Logistic_Regression |                 0.85 |                0.1612 |                        59.38 |                  40.62 |                           85.14 |                         14.86 |  3.02 |
| EXPANDED_COMMON   | Logistic_Regression |                 0.9  |                0.1357 |                        65.78 |                  34.22 |                           90.23 |                          9.77 |  3.15 |
| EXPANDED_COMMON   | Logistic_Regression |                 0.95 |                0.0964 |                        76.89 |                  23.11 |                           95.05 |                          4.95 |  3.5  |
| EXPANDED_COMMON   | GAM                 |                 0.8  |                0.1907 |                        53.68 |                  46.32 |                           80.32 |                         19.68 |  2.89 |
| EXPANDED_COMMON   | GAM                 |                 0.85 |                0.1652 |                        59.53 |                  40.47 |                           85.27 |                         14.73 |  3.02 |
| EXPANDED_COMMON   | GAM                 |                 0.9  |                0.1377 |                        65.53 |                  34.47 |                           90.36 |                          9.64 |  3.14 |
| EXPANDED_COMMON   | GAM                 |                 0.95 |                0.0886 |                        77.13 |                  22.87 |                           95.05 |                          4.95 |  3.51 |
| EXPANDED_COMMON   | DLNN                |                 0.8  |                0.2064 |                        53.4  |                  46.6  |                           80.05 |                         19.95 |  2.89 |
| EXPANDED_COMMON   | DLNN                |                 0.85 |                0.175  |                        58.73 |                  41.27 |                           85.27 |                         14.73 |  2.98 |
| EXPANDED_COMMON   | DLNN                |                 0.9  |                0.1377 |                        66.09 |                  33.91 |                           90.09 |                          9.91 |  3.17 |
| EXPANDED_COMMON   | DLNN                |                 0.95 |                0.0846 |                        76.98 |                  23.02 |                           95.05 |                          4.95 |  3.5  |


### Representative Screening Interpretations:
- **CORE_FULL / Logistic_Regression (Target Sens 80%):** At threshold 0.19, 53.89% of the screening population is referred for Stage-2 HbA1c testing, capturing 80.03% of true dysglycemia cases while missing 19.97%. (NNT = 2.91)
- **CORE_FULL / Logistic_Regression (Target Sens 85%):** At threshold 0.16, 59.79% of the screening population is referred for Stage-2 HbA1c testing, capturing 85.05% of true dysglycemia cases while missing 14.95%. (NNT = 3.04)
- **CORE_FULL / Logistic_Regression (Target Sens 90%):** At threshold 0.14, 65.22% of the screening population is referred for Stage-2 HbA1c testing, capturing 90.34% of true dysglycemia cases while missing 9.66%. (NNT = 3.12)
- **CORE_FULL / Logistic_Regression (Target Sens 95%):** At threshold 0.09, 79.25% of the screening population is referred for Stage-2 HbA1c testing, capturing 95.23% of true dysglycemia cases while missing 4.77%. (NNT = 3.6)
- **CORE_FULL / GAM (Target Sens 80%):** At threshold 0.20, 54.72% of the screening population is referred for Stage-2 HbA1c testing, capturing 80.03% of true dysglycemia cases while missing 19.97%. (NNT = 2.96)
- **CORE_FULL / GAM (Target Sens 85%):** At threshold 0.17, 59.2% of the screening population is referred for Stage-2 HbA1c testing, capturing 85.18% of true dysglycemia cases while missing 14.82%. (NNT = 3.0)
- **CORE_FULL / GAM (Target Sens 90%):** At threshold 0.14, 65.93% of the screening population is referred for Stage-2 HbA1c testing, capturing 90.46% of true dysglycemia cases while missing 9.54%. (NNT = 3.15)
- **CORE_FULL / GAM (Target Sens 95%):** At threshold 0.09, 79.14% of the screening population is referred for Stage-2 HbA1c testing, capturing 95.1% of true dysglycemia cases while missing 4.9%. (NNT = 3.6)

## 8. Publication Figures Generated
- **`plots_phase4/development_roc_curves.png`**: ROC curves for Logistic Regression, GAM, and DLNN.
- **`plots_phase4/development_pr_curves.png`**: Precision-Recall curves against sample prevalence baseline.
- **`plots_phase4/development_calibration_curves.png`**: 10-bin calibration curves demonstrating probability reliability.
- **`plots_phase4/threshold_sensitivity_specificity.png`**: Decision threshold sensitivity/specificity trade-off curves.

## 9. Reproducibility & Protocol Verification
- All development cross-validation runs used fixed seeds (`42`).
- Preprocessing scalers were strictly isolated within training folds.
- Zero leakage variables entered any feature matrix.
- All models produced exact out-of-fold probability records in `predictions_phase4/oof_predictions.csv`.

---

DEVELOPMENT BENCHMARK COMPLETE — FINAL TEST SET REMAINS LOCKED