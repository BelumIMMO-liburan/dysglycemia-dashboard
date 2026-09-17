# Phase 4 Locked Experimental Protocol

**Study:** Two-Stage Non-Laboratory Screening for Unrecognized HbA1c Dysglycemia
**Target Population:** Cohort E (Adults age ≥ 18 without self-reported known diabetes or prediabetes)
**Primary Target:** `hba1c_dysglycemia` (0 = HbA1c < 5.7%, 1 = HbA1c ≥ 5.7%)

---

## 1. Experimental Design & Partitioning
- **Master Cohort:** `analytic_core_complete.parquet` ($N = 4,194$).
- **Master Split:** Single deterministic 80/20 train/test partition seeded with random state `42`.
  - **Development Partition (80%):** $N = 3,355$ ($2,579$ normal, $776$ dysglycemia, prevalence $23.13\%$).
  - **Final Test Partition (20%):** $N = 839$ ($645$ normal, $194$ dysglycemia, prevalence $23.12\%$).
- **Final Test Set Lock Rule:** The test set is strictly locked. No model evaluation, feature selection, threshold tuning, error inspection, or metric calculation is permitted during development benchmarking.
- **Development Cross-Validation:** Stratified 5-fold cross-validation within the development partition (seed `42`). All models share identical fold assignments.

## 2. Fair Comparison Framework
Because `analytic_core_complete` ($N=4,194$) contains more participants than `analytic_expanded_complete` ($N=4,044$), models are evaluated across three distinct variants:
1. **CORE-FULL:** All $N=3,355$ development participants using 5 Core features (`age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`).
2. **CORE-COMMON:** Participants present in both Core and Expanded datasets ($N=3,232$ development) using 5 Core features.
3. **EXPANDED-COMMON:** The identical $N=3,232$ common development participants using 7 Expanded features (Core + `waist_cm`, `sedentary_minutes_day`).

## 3. Preprocessing & Leakage Protection
- **Continuous Features:** Scaled using `StandardScaler` fitted **strictly on the training fold**. Never fit on the full dataset or outer validation fold.
- **Categorical Features:** Transparent binary mapping (`sex`: Male=1, Female=0; `hypertension_history`: Yes=1, No=0; `smoking_history`: Yes=1, No=0).
- **Prohibited Variables:** Automated assertion prevents `SEQN`, lab outcomes (`LBXGH`, `LBXGLU`), categories, and survey weights from entering feature matrix $X$.

## 4. Candidate Model Architectures
1. **Logistic Regression:** L2 regularized ($C \in [0.01, 0.1, 1.0, 10.0]$).
2. **Generalized Additive Model (GAM):** `LogisticGAM` with $s(\text{continuous})$ splines ($n=10$) and $f(\text{categorical})$ factors across smoothing $\lambda \in [0.01, 0.1, 1.0, 10.0]$.
3. **Deep Learning Neural Network (DLNN):** Small feedforward architectures (16-8 and 32-16 with dropout $\in [0.0, 0.2]$), Adam optimizer, batch size 32, max epochs 200, early stopping patience 15 based on an **internal training-fold validation split**.

## 5. Development Metrics & Threshold Analysis
- **Discrimination:** ROC-AUC, PR-AUC, Brier Score (per-fold and pooled OOF).
- **Descriptive Operating Points:** Operating points targeting Sensitivity $\ge 0.80, 0.85, 0.90, 0.95$.
- **Screening Efficiency:** Referral rate (% referred to Stage-2 HbA1c testing), capture rate (% true cases identified), and Number Needed to Test ($1/\text{PPV}$).
- **Decision Rule:** No winning model or threshold is chosen programmatically. Factual findings are reported.