# Final Model Specification Lock (Phase 4.2)

**Document Status:** **FROZEN & IMMUTABLE**  
**Protocol Phase:** Phase 4.2 Pre-Test Specification Lock  
**Final Test Status:** **LOCKED — ZERO ACCESS PERMITTED DURING SPECIFICATION**  
**Date Locked:** 2026-09-02  

---

## 1. Freeze Declaration & Governance

This document establishes the **immutable, pre-specified analytical protocol** for the final evaluation of the non-laboratory screening model in Phase 5.

Based exclusively on the completed development cross-validation benchmarks (Phase 4) and standardized selection audits (Phase 4.1):
- The final model family, architecture, hyperparameter configuration, predictor set, preprocessing procedure, and screening decision threshold are **fully specified and locked**.
- **Zero test-set tuning, threshold optimization, feature selection, or iterative evaluation is permitted.**
- The final test set ($N = 839$ in Core; $N = 812$ in Common) may be evaluated **exactly once** in Phase 5 under the exact conditions defined below.

---

## 2. Research Problem & Population Definition

- **Task:** Non-laboratory risk screening for unrecognized HbA1c-defined dysglycemia (Stage-1 community screening).
- **Clinical Scope:** This is a **risk-screening stratification instrument** intended to identify individuals who should be referred for confirmatory laboratory HbA1c testing (Stage 2). **It does NOT provide clinical diagnosis, disease staging, or longitudinal risk projection.**
- **Target Population (Cohort E):** Community-dwelling adults aged $\ge 18$ years without self-reported prior diagnosis of diabetes (`DIQ010 == 2`) or prediabetes (`DIQ160 == 2`), with valid laboratory HbA1c and complete physical examination.
- **Master Dataset:** `analytic_expanded_complete.parquet` ($N = 4,044$ total; $3,106$ normal, $938$ dysglycemia; prevalence $23.19\%$).
  - **Development Partition (80%):** $N = 3,232$ ($2,485$ normal, $747$ dysglycemia; prevalence $23.11\%$).
  - **Final Test Partition (20%):** $N = 812$ ($621$ normal, $191$ dysglycemia; prevalence $23.52\%$) — **CURRENTLY LOCKED**.

---

## 3. Primary Final Model Specification

### 3.1 Model Architecture & Family
- **Model Family:** **Generalized Additive Model (GAM)** with binomial logit link.
- **Implementation Package:** `pygam.LogisticGAM`.
- **Target Variable:** `hba1c_dysglycemia`
  - `0 = normal` (`LBXGH < 5.7%`)
  - `1 = dysglycemia` (`LBXGH ≥ 5.7%`)

### 3.2 Predictor Variables ($k = 7$ Non-Laboratory Features)

| Feature Name | Source Variable | Term Type | Coding & Representation | Missing Handling |
|:---|:---|:---:|:---|:---|
| **`age`** | `RIDAGEYR` | Spline $s(0)$ | Continuous (years, range 18–80) | Non-missing required |
| **`sex`** | `RIAGENDR` | Factor $f(1)$ | Binary indicator: `1 = Male`, `0 = Female` | Non-missing required |
| **`bmi`** | `BMXBMI` | Spline $s(2)$ | Continuous ($\text{kg/m}^2$, range 11.1–69.9) | Measured at MEC physical exam |
| **`hypertension_history`** | `BPQ020` | Factor $f(3)$ | Binary indicator: `1 = Yes`, `0 = No` | Recoded from 1/2; 7/9 set to NaN |
| **`smoking_history`** | `SMQ020` | Factor $f(4)$ | Binary indicator: `1 = Yes (≥100 cigs)`, `0 = No` | Recoded from 1/2; 7/9 set to NaN |
| **`waist_cm`** | `BMXWAIST` | Spline $s(5)$ | Continuous (cm, range 60.0–187.0) | Measured at MEC physical exam |
| **`sedentary_minutes_day`** | `PAD680` | Spline $s(6)$ | Continuous (minutes/day, range 0–1200) | Self-reported daily sitting; 7777/9999 set to NaN |

### 3.3 Mathematical Formulation & Hyperparameters
$$\text{logit}(P(Y=1 \mid X)) = \beta_0 + s_1(\text{age}) + f_2(\text{sex}) + s_3(\text{bmi}) + f_4(\text{hypertension}) + f_5(\text{smoking}) + s_6(\text{waist}) + s_7(\text{sedentary})$$
- **Spline Basis:** Cubic P-splines on continuous variables with `n_splines = 10`.
- **Regularization / Smoothing:** L2 second-derivative penalty with smoothing parameter $\lambda = 10.0$ applied uniformly across terms.
- **Fitting Criterion:** Penalized maximum likelihood via Iteratively Reweighted Least Squares (P-IRLS) with `max_iter = 200`.

---

## 4. Decision Threshold & Pre-Specified Research Operating Point

- **Screening Objective:** In public health screening, high sensitivity is prioritized to capture unrecognized dysglycemia cases while maintaining a manageable referral fraction for Stage-2 laboratory testing.
- **Sensitivity Floor:** **$\ge 90\%$ Sensitivity**.
- **Frozen Decision Threshold:** **`0.1389`**
  - Derived strictly from pooled 5-fold development out-of-fold predictions.
  - Selected by identifying the highest threshold that satisfies the $\ge 90\%$ sensitivity floor on the development cohort (thereby maximizing specificity).
- **Strict Prohibition:** **This threshold (`0.1389`) is frozen and MUST NOT be recalculated, adjusted, or tuned using final-test data.**

### Development Operating Baseline (for Phase 5 Comparison)
- Development Achieved Sensitivity: **90.23%**
- Development Achieved Specificity: **42.25%**
- Development Referral Fraction: **65.25%**
- Development Dysglycemia Captured: **90.23%** (Missed: 9.77%)
- Development Screening Burden: **3.13 HbA1c tests per dysglycemia case detected** ($1/\text{PPV}$)

---

## 5. Final Training & Preprocessing Procedure (Phase 5 Execution)

When Phase 5 is authorized:
1. **Training Set:** The final model will be fitted on the entire development partition of `analytic_expanded_complete.parquet` ($N = 3,232$).
2. **Preprocessing Isolation:**
   - `StandardScaler` for continuous features (`age`, `bmi`, `waist_cm`, `sedentary_minutes_day`) will be fit **strictly on the $N = 3,232$ development set**.
   - Binary categorical features (`sex`, `hypertension_history`, `smoking_history`) will use fixed deterministic indicator mappings.
   - The fitted scaler and mappings will transform the final test set ($N = 812$) without re-estimation.
3. **One-Time Evaluation:**
   - The trained GAM will generate predicted probabilities on the transformed final test set.
   - Predictions $\ge 0.1389$ will be classified as positive referrals.
   - Final test metrics (ROC-AUC, PR-AUC, Brier score, sensitivity, specificity, PPV, NPV, referral fraction) will be calculated **exactly once**.

---

## 6. Comparator Status & Methodological Context

The research study evaluates three methodological approaches:
1. **Statistical Baseline Comparator:** Logistic Regression (`L2_C0.1` on Expanded; `L2_C0.01` on Core).
2. **Primary Final Screening Model:** Generalized Additive Model (GAM, `n_splines=10, lam=10.0` on Expanded).
3. **Complex Non-Linear Comparator:** Deep Learning Neural Network (`DLNN_16_8_drop0.0` on Expanded).

**Comparative Policy:**
- Neither comparator is removed or suppressed. Both will be trained on development data and evaluated on the final test set in Phase 5 to provide a rigorous, transparent methodological comparison.
- GAM was selected as the primary screening model based on development-set evidence demonstrating optimal calibration (slope 0.9652), superior precision (PR-AUC 0.4207), lowest referral burden at 90% sensitivity (65.25%), and clinically interpretable non-linear additive shape functions.

---

## 7. Language & Governance Rules

All reporting and discussion must adhere to the following standards:
- Use **"non-linear associations"** rather than claiming the model captures "biological reality."
- Use **"HbA1c-defined dysglycemia screening"** rather than "clinical diagnosis."
- Use **"pre-specified research operating point"** rather than claiming 90% sensitivity is "clinically optimal."
- Base claims strictly on **"development-set evidence."**
- In calibration discussions, note that a calibration slope $< 1$ reflects that probability predictions tend to be slightly overconfident (too extreme) relative to observed outcome rates, rather than under-confident.

---

## 8. Cryptographic Hashes of Locked Files

| Artifact Name | Relative File Path | SHA256 Hash |
|:---|:---|:---|
| Master Split | `splits_phase4/master_split.csv` | `685b4a15a1ab5ea83647f91f6c335a8a44b2179e47eaab186bdd1960a583f9ed` |
| Development Folds | `splits_phase4/development_folds.csv` | `0bfacfaba04ffaa02ea0f82294478c0d2790012c0d5466490e85956fabd028e1` |
| Canonical Expanded Parquet | `processed_phase3/analytic_expanded_complete.parquet` | `6fa1dd5c9212359271de03285806044f3d8a8f817c774bdd1e8c054fe75d1679` |
| Locked Specification | `lock_phase4_2/FINAL_MODEL_SPECIFICATION_LOCKED.md` | *(Computed upon file creation)* |

---

**MODEL SPECIFICATION FROZEN — READY FOR ONE-TIME FINAL TEST**
