# Notebook 04 Validation Report

**Notebook:** `notebooks/04_Final_Test_Evaluation.ipynb`  
**Validation Timestamp:** 2026-09-03 23:38:16  
**Validation Status:** **ALL CHECKS PASSED — 100% REPRODUCIBLE**  

---

## 1. Execution Summary

| Property | Value |
|:---|:---|
| **Notebook File** | `notebooks/04_Final_Test_Evaluation.ipynb` |
| **Total Cells** | 22 (12 Markdown, 10 Code) |
| **Execution Mode** | Clean Kernel Top-to-Bottom (`nbclient.NotebookClient`) |
| **Execution Status** | Succeeded without errors (`0` cell exceptions) |
| **Total Execution Time** | 4.62 seconds |
| **File SHA256** | `4da005af1f8dedd33353d6da75c0cd970814eb52764856f9e122ac3ff2cf8980` |
| **Model Fitting (.fit) Calls** | **0 (Zero)** |
| **Inference (.predict) Calls** | **0 (Zero)** |
| **Prediction File State** | **100% Unchanged (Byte-identical)** |

---

## 2. Source Files & Reference Datasets Used

### Frozen Final-Test Predictions (Immutable Source of Truth)
- `nhanes_feasibility_2021_2023/predictions_phase5/final_test_predictions.csv`  
  - Expected SHA256: `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923`  
  - Observed SHA256: `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` (**VERIFIED IDENTICAL**)

### Authoritative Phase-5 Reports for Reconciliation
- `nhanes_feasibility_2021_2023/reports_phase5/final_test_model_metrics.csv`
- `nhanes_feasibility_2021_2023/reports_phase5/final_test_threshold_metrics.csv`
- `nhanes_feasibility_2021_2023/reports_phase5/final_test_confusion_matrices.csv`
- `nhanes_feasibility_2021_2023/reports_phase5/final_test_calibration.csv`
- `nhanes_feasibility_2021_2023/reports_phase5/final_test_paired_model_comparisons.csv`
- `nhanes_feasibility_2021_2023/reports_phase5/phase5_final_evaluation_report_v1_1.md`

---

## 3. Reproduction & Reconciliation Audit

| Check Description | Expected (Phase 5 v1.1) | Observed (Notebook 04) | Discrepancy | Verification Status |
|:---|:---:|:---:|:---:|:---:|
| **Final Test Sample Size** | 812 | 812 | 0 | **PASS** |
| **Test Normal Cohort (y = 0)** | 621 | 621 | 0 | **PASS** |
| **Test Dysglycemia Cohort (y = 1)** | 191 | 191 | 0 | **PASS** |
| **GAM Final ROC-AUC** | 0.7277 | 0.7277 | 0.0000 | **PASS** |
| **GAM Final PR-AUC** | 0.4503 | 0.4503 | 0.0000 | **PASS** |
| **GAM Final Brier Score** | 0.1587 | 0.1587 | 0.0000 | **PASS** |
| **Logistic Final ROC-AUC** | 0.7288 | 0.7288 | 0.0000 | **PASS** |
| **Logistic Final PR-AUC** | 0.4407 | 0.4407 | 0.0000 | **PASS** |
| **DLNN Final ROC-AUC** | 0.7200 | 0.7200 | 0.0000 | **PASS** |
| **DLNN Final PR-AUC** | 0.4214 | 0.4214 | 0.0000 | **PASS** |
| **GAM Frozen Threshold** | 0.1389 | 0.1389 | 0.0000 | **PASS** |
| **GAM Achieved Sensitivity** | 86.39% (165/191) | 86.39% (165/191) | 0.00% | **PASS** |
| **GAM Achieved Specificity** | 42.51% (264/621) | 42.51% (264/621) | 0.00% | **PASS** |
| **GAM Total Referred ($N$)** | 522 (64.29%) | 522 (64.29%) | 0 | **PASS** |
| **GAM Total Not Referred ($N$)** | 290 (35.71%) | 290 (35.71%) | 0 | **PASS** |
| **GAM True Positives (TP)** | 165 | 165 | 0 | **PASS** |
| **GAM False Positives (FP)** | 357 | 357 | 0 | **PASS** |
| **GAM True Negatives (TN)** | 264 | 264 | 0 | **PASS** |
| **GAM False Negatives (FN)** | 26 | 26 | 0 | **PASS** |
| **GAM Tests per Case ($1/\text{PPV}$)** | 3.16 | 3.16 | 0.00 | **PASS** |
| **Zero Model Training Executed** | `True` | `True` | None | **PASS** |
| **Final Predictions Hash Unaltered** | `True` | `True` | None | **PASS** |

---

## 4. Discrepancies & Audit Findings

- **Discrepancies Found:** **ZERO**. All recomputed test metrics, confusion matrix cells, referral counts, and calibration values match Phase 5 report v1.1 exactly.
- **Strict Read-Only Execution:** Verified that no `.fit()`, `.predict()`, or `.predict_proba()` calls exist in the notebook code.
- **Data Protection:** The final test prediction file (`final_test_predictions.csv`) was cryptographically verified before and after notebook execution and remained 100% byte-identical.
