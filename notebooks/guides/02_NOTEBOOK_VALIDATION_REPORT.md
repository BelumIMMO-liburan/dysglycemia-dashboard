# Notebook 02 Validation Report

**Notebook:** `notebooks/02_Model_Development.ipynb`  
**Validation Timestamp:** 2026-09-03 23:35:20  
**Validation Status:** **ALL CHECKS PASSED — 100% REPRODUCIBLE**  

---

## 1. Execution Summary

| Property | Value |
|:---|:---|
| **Notebook File** | `notebooks/02_Model_Development.ipynb` |
| **Total Cells** | 25 (13 Markdown, 12 Code) |
| **Execution Mode** | Clean Kernel Top-to-Bottom (`nbclient.NotebookClient`) |
| **Execution Status** | Succeeded without errors (`0` cell exceptions) |
| **Total Execution Time** | 4.76 seconds |
| **File SHA256** | `37698bdb0608cbd19ee5f9d3c89334f7deefd0614f408a73ce5b6cf878941063` |

---

## 2. Source Files & Reference Datasets Used

### Split Manifests & Datasets
- `nhanes_feasibility_2021_2023/splits_phase4/master_split.csv` ($N = 4,044$)
- `nhanes_feasibility_2021_2023/splits_phase4/development_folds.csv` ($N = 3,232$)
- `nhanes_feasibility_2021_2023/processed_phase3/analytic_expanded_complete.parquet` ($N = 4,044$)

### Audited Phase-4 OOF Predictions Replayed
- `nhanes_feasibility_2021_2023/predictions_phase4/oof_predictions.csv` (SHA256: `c50f29a7dfce49c2c53915158babac4f3c19f8f5cdf1f4461920362b0ad30dca`)

### Phase-4 Benchmark Summary for Comparison
- `nhanes_feasibility_2021_2023/reports_phase4/cv_model_summary.csv`

---

## 3. Reproduction & Reconciliation Audit

| Check Description | Expected (Phase 4) | Observed (Notebook 02) | Discrepancy | Verification Status |
|:---|:---:|:---:|:---:|:---:|
| **Development Cohort Sample Size** | 3,232 | 3,232 | 0 | **PASS** |
| **Cross-Validation Folds Count** | 5 | 5 | 0 | **PASS** |
| **GAM Expanded ROC-AUC** | 0.7382 | 0.7382 | 0.0000 | **PASS** |
| **GAM Expanded PR-AUC** | 0.4207 | 0.4207 | 0.0000 | **PASS** |
| **GAM Expanded Brier Score** | 0.1561 | 0.1561 | 0.0000 | **PASS** |
| **Logistic Selected (L2_C0.1) ROC-AUC** | 0.7345 | 0.7345 | 0.0000 | **PASS** |
| **Logistic Selected (L2_C0.1) PR-AUC** | 0.4087 | 0.4087 | 0.0000 | **PASS** |
| **Logistic Selected (L2_C0.1) Brier** | 0.1574 | 0.1574 | 0.0000 | **PASS** |
| **DLNN Selected (16_8_drop0.0) ROC-AUC** | 0.7306 | 0.7306 | 0.0000 | **PASS** |
| **DLNN Selected (16_8_drop0.0) PR-AUC** | 0.4115 | 0.4115 | 0.0000 | **PASS** |
| **DLNN Selected (16_8_drop0.0) Brier** | 0.1577 | 0.1577 | 0.0000 | **PASS** |
| **Zero Final Test Data Evaluated** | `True` | `True` | None | **PASS** |
| **Prohibited Leakage Variables in $X$** | 0 variables | 0 variables | 0 | **PASS** |

---

## 4. Discrepancies & Audit Findings

- **Discrepancies Found:** **ZERO**. All cross-validation OOF metrics reconcile with `cv_model_summary.csv` to 4 decimal places.
- **Leakage Protection:** Confirmed that scaling occurred exclusively within training folds and no final-test data participated in evaluation.
- **Model Training:** Verified replay mode read the immutable, cryptographically hashed Phase-4 OOF prediction table without modification.
