# NHANES Two-Stage Dysglycemia Screening — Research Notebook Suite

This directory contains the complete, reproducible, presentation-ready Jupyter Notebook suite documenting the machine learning research pipeline developed for this thesis.

---

## 1. Methodological Pipeline Architecture

```
Raw CDC/NCHS NHANES Microdata (2021–2023)
  ├── Demographic, Examination, Laboratory, and Questionnaire Modules
  └── Participant-level left join on SEQN (N = 11,933)
       │
       ▼
Cohort E Construction (Notebook 01)
  ├── Exclude age < 18 (N = 8,153 adults)
  ├── Exclude self-reported diabetes (DIQ010 != 2) & prediabetes (DIQ160 != 2) (N = 5,907)
  ├── Analytical phlebotomy validity (LBXGH notna & WTPH2YR > 0) (N = 4,260)
  ├── PAD680 sentinel cleaning (7777, 9999 -> NaN)
  └── Complete-case restriction -> Canonical Expanded Cohort (N = 4,044)
       │
       ▼
Master Partitioning & Stratification
  ├── Development Partition (80%, N = 3,232)
  └── Held-Out Final Test Partition (20%, N = 812) [STRICTLY LOCKED]
       │
       ▼
Development Cross-Validation (Notebook 02)
  ├── 5-Fold Stratified CV on Development Partition Only
  ├── In-fold scaling (StandardScaler fitted exclusively on training folds)
  ├── Benchmark 3 model families: Logistic Regression, GAM, and DLNN
  └── Generate Out-of-Fold (OOF) prediction vectors (N = 3,232)
       │
       ▼
Model Selection & Operating Point Lock (Notebook 03)
  ├── Standardized selection hierarchy (PR-AUC -> ROC-AUC -> Brier -> Parsimony)
  ├── 2,000 paired participant-level bootstrap resamples (seed 42)
  ├── Calibration diagnostics (Brier score, intercept, slope, ECE)
  ├── Screening sensitivity floor analysis (80%, 85%, 90%, 95%)
  ├── Operating threshold optimization -> GAM threshold 0.1389 (90% sensitivity floor)
  └── Pre-Test Specification Lock in lock_phase4_2/
       │
       ▼
======================= CRITICAL GOVERNANCE GATE =======================
Single Authorized Opening of Held-Out Final Test Partition (N = 812)
========================================================================
       │
       ▼
Confirmatory Final Test Evaluation (Notebook 04)
  ├── Single forward pass using frozen models and frozen thresholds
  ├── Zero post-test hyperparameter tuning or threshold readjustment
  ├── Verified read-only metric calculation on frozen predictions (SHA256 verified)
  └── Final clinical screening flow & generalization comparison
```

---

## 2. Notebook Inventory & Specifications

| Notebook | Research Phase | Primary Purpose | Model Training? | Accesses Final Test? | Runtime | Defense Guide | Validation Report |
|:---|:---|:---|:---:|:---:|:---:|:---|:---|
| **[`01_NHANES_Data_Preparation.ipynb`](01_NHANES_Data_Preparation.ipynb)** | Phase 3 | Raw data ingestion, participant merge, Cohort E filtering, outcome construction, special-code handling, canonical replication | No | No | ~3.6s | [`01_..._FELIK_GUIDE.md`](guides/01_NHANES_Data_Preparation_FELIK_GUIDE.md) | [`01_..._REPORT.md`](guides/01_NOTEBOOK_VALIDATION_REPORT.md) |
| **[`02_Model_Development.ipynb`](02_Model_Development.ipynb)** | Phase 4 | 5-fold stratified CV, in-fold scaling, candidate model architectures, development OOF prediction generation & metrics | Replay/Audit | No | ~4.8s | [`02_..._FELIK_GUIDE.md`](guides/02_Model_Development_FELIK_GUIDE.md) | [`02_..._REPORT.md`](guides/02_NOTEBOOK_VALIDATION_REPORT.md) |
| **[`03_Model_Selection.ipynb`](03_Model_Selection.ipynb)** | Phase 4.1 | Standardized configuration selection, paired bootstrap (2,000 resamples), calibration audit, 90% sensitivity floor lock | No | No | ~4.2s | [`03_..._FELIK_GUIDE.md`](guides/03_Model_Selection_FELIK_GUIDE.md) | [`03_..._REPORT.md`](guides/03_NOTEBOOK_VALIDATION_REPORT.md) |
| **[`04_Final_Test_Evaluation.ipynb`](04_Final_Test_Evaluation.ipynb)** | Phase 5 | Confirmatory held-out test evaluation on frozen predictions, confusion matrix analysis, referral flow, generalization comparison | No (Read-Only) | Yes (Frozen Preds Only) | ~4.6s | [`04_..._FELIK_GUIDE.md`](guides/04_Final_Test_Evaluation_FELIK_GUIDE.md) | [`04_..._REPORT.md`](guides/04_NOTEBOOK_VALIDATION_REPORT.md) |

---

## 3. Key Research Takeaways

1. **Screening Purpose:** This study evaluates Stage-1 non-laboratory screening for *currently present, unrecognized dysglycemia* in community adults. It does **not** model future longitudinal diabetes incidence, nor does it establish clinical diagnosis.
2. **Model Paradigm Findings:**
   * **GAM vs. Logistic Regression:** GAM demonstrated broadly comparable discrimination to linear Logistic Regression with a slight advantage in PR-AUC ($0.4503$ vs $0.4407$) and higher specificity ($42.51\%$ vs $40.74\%$), referring fewer normal participants while capturing the exact same number of true cases.
   * **DLNN Complexity:** Multi-layer deep neural networks did not demonstrate a predictive advantage over additive models on this tabular screening task ($k = 7$ features, $N = 3,232$ training participants).
3. **Operational Decision Rule:** Applying the development-derived 90% sensitivity threshold ($0.1389$) to the independent final test cohort captured **$86.39\%$** of unrecognized dysglycemia cases, achieving a screening efficiency of **3.16 laboratory HbA1c tests per case detected**.
4. **Generalization Scope:** All evaluations reflect unweighted participant-level predictive accuracy on the NHANES examination cohort. They are **not** claimed as nationally representative U.S. prevalence estimates, and external validity to the Indonesian population is explicitly not claimed.
