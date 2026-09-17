# Provisional Model Nomination Audit (Phase 4.1)

**Evaluation Scope:** Development Out-Of-Fold Data Only ($N = 3,232$) — **FINAL TEST SET REMAINS LOCKED**

---

## Model Family Comparison on EXPANDED_COMMON

| comparison                  | m1   | m1_config             | m2                  | m2_config         |   delta_roc_auc | roc_auc_ci_95     |   delta_pr_auc | pr_auc_ci_95      |   delta_brier | brier_ci_95        |
|:----------------------------|:-----|:----------------------|:--------------------|:------------------|----------------:|:------------------|---------------:|:------------------|--------------:|:-------------------|
| GAM vs Logistic_Regression  | GAM  | GAM_splines10_lam10.0 | Logistic_Regression | L2_C0.1           |          0.0037 | [-0.0017, 0.0095] |         0.012  | [-0.0014, 0.0259] |       -0.0013 | [-0.0026, -0.0000] |
| DLNN vs Logistic_Regression | DLNN | DLNN_16_8_drop0.0     | Logistic_Regression | L2_C0.1           |         -0.0039 | [-0.0119, 0.0040] |         0.0028 | [-0.0193, 0.0232] |        0.0003 | [-0.0016, 0.0023]  |
| GAM vs DLNN                 | GAM  | GAM_splines10_lam10.0 | DLNN                | DLNN_16_8_drop0.0 |          0.0077 | [0.0004, 0.0146]  |         0.0092 | [-0.0102, 0.0287] |       -0.0016 | [-0.0033, 0.0001]  |

## Multi-Criteria Evaluation Matrix

| Criteria | Logistic Regression (`L2_C0.1`) | GAM (`GAM_splines10_lam10.0`) | DLNN (`DLNN_16_8_drop0.0`) |
|:---|:---|:---|:---|
| **Discrimination (ROC-AUC)** | 0.7345 | **0.7382** (highest) | 0.7306 |
| **Precision (PR-AUC)** | 0.4087 | **0.4207** (highest) | 0.4115 |
| **Calibration (Brier Score)** | 0.1574 | **0.1561** (best) | 0.1577 |
| **Calibration Slope** | 1.0005 (well-calibrated) | **0.9652** (well-calibrated) | 0.9030 (under-confident) |
| **ECE (10 Bins)** | 0.0169 | **0.0106** (lowest error) | 0.0135 |
| **Referral Rate at 90% Floor** | 65.72% | **65.25%** (lowest referral) | 65.47% |
| **Specificity at 90% Floor** | 41.65% | **42.25%** (highest) | 41.93% |
| **Interpretability** | Transparent linear log-odds | **Transparent shape functions $s(x)$** | Black-box non-linear weights |
| **Computational Complexity** | Negligible (~0.01s) | Minimal (~0.2s) | High (requires internal early stopping) |
| **Feature Burden** | 7 non-lab inputs | 7 non-lab inputs | 7 non-lab inputs |

## Provisional Nomination Assessment

1. **GAM vs. Logistic Regression:** The Generalized Additive Model achieves slightly superior discrimination (+0.0037 ROC-AUC, 95% CI: [-0.0017, 0.0095]; +0.0120 PR-AUC, 95% CI: [-0.0014, 0.0259]) and lower ECE (0.0106 vs 0.0169). While the confidence interval crosses zero narrowly, GAM provides smooth, non-linear risk curves that capture biological reality without losing interpretability.

2. **DLNN Performance:** The Deep Learning Neural Network did not outperform classical statistical models on this sample size ($N \approx 3,232$). Its ROC-AUC (0.7306) and calibration slope (0.9030) were inferior to both GAM and Logistic Regression. DLNN is not justified merely because it is a neural network.

3. **Provisional Recommendation:** **Generalized Additive Model (GAM)** is nominated as the primary candidate model for two-stage screening due to its optimal balance of non-linear discrimination, superior probability calibration, low referral burden, and clinical explainability.