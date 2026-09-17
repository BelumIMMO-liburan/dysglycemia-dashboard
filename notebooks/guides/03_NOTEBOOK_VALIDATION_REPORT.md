# Notebook 03 Validation Report

**Notebook:** `notebooks/03_Model_Selection.ipynb`  
**Validation Timestamp:** 2026-09-03 23:36:51  
**Validation Status:** **ALL CHECKS PASSED — 100% REPRODUCIBLE**  

---

## 1. Execution Summary

| Property | Value |
|:---|:---|
| **Notebook File** | `notebooks/03_Model_Selection.ipynb` |
| **Total Cells** | 23 (12 Markdown, 11 Code) |
| **Execution Mode** | Clean Kernel Top-to-Bottom (`nbclient.NotebookClient`) |
| **Execution Status** | Succeeded without errors (`0` cell exceptions) |
| **Total Execution Time** | 4.15 seconds |
| **File SHA256** | `7fd75c13b7770a72ac0cb0a09ba56a1adfeac419677bd5a76ccc6e2fc9934035` |

---

## 2. Source Files & Reference Datasets Used

### Audited Phase-4 OOF Predictions
- `nhanes_feasibility_2021_2023/predictions_phase4/oof_predictions.csv` (SHA256: `c50f29a7dfce49c2c53915158babac4f3c19f8f5cdf1f4461920362b0ad30dca`)

### Official Phase 4.1 Selection Reports
- `nhanes_feasibility_2021_2023/reports_phase4_1/configuration_selection.csv`
- `nhanes_feasibility_2021_2023/reports_phase4_1/paired_bootstrap_feature_sets.csv`
- `nhanes_feasibility_2021_2023/reports_phase4_1/paired_bootstrap_models.csv`
- `nhanes_feasibility_2021_2023/reports_phase4_1/calibration_diagnostics.csv`
- `nhanes_feasibility_2021_2023/reports_phase4_1/screening_operating_points.csv`
- `nhanes_feasibility_2021_2023/reports_phase4_1/feature_burden_comparison.csv`

### Pre-Test Locked Specification
- `nhanes_feasibility_2021_2023/lock_phase4_2/FINAL_MODEL_SPECIFICATION_LOCKED.md` (SHA256: `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5`)

---

## 3. Reproduction & Reconciliation Audit

| Check Description | Expected (Phase 4.1) | Observed (Notebook 03) | Discrepancy | Verification Status |
|:---|:---:|:---:|:---:|:---:|
| **GAM Selected Configuration** | `GAM_splines10_lam10.0` | `GAM_splines10_lam10.0` | None | **PASS** |
| **Logistic Selected Configuration** | `L2_C0.1` | `L2_C0.1` | None | **PASS** |
| **DLNN Selected Configuration** | `DLNN_16_8_drop0.0` | `DLNN_16_8_drop0.0` | None | **PASS** |
| **GAM 90% Sensitivity Threshold** | 0.1389 | 0.1389 | 0.0000 | **PASS** |
| **GAM 90% Achieved Sensitivity** | 90.23% | 90.23% | 0.00% | **PASS** |
| **GAM 90% Specificity** | 42.25% | 42.25% | 0.00% | **PASS** |
| **GAM 90% Referral Rate** | 65.25% | 65.25% | 0.00% | **PASS** |
| **GAM 90% Tests per Case ($1/\text{PPV}$)** | 3.13 | 3.13 | 0.00 | **PASS** |
| **Primary Model Lock File Checksum** | Verified Match | Verified Match | None | **PASS** |
| **Zero Final Test Data Read** | `True` | `True` | None | **PASS** |

---

## 4. Discrepancies & Audit Findings

- **Discrepancies Found:** **ZERO**. All selection ranks, operating point thresholds, bootstrap confidence intervals, and calibration statistics reconcile 100% with Phase 4.1.
- **Data Governance Boundary:** Confirmed that **zero final-test data** was accessed or evaluated in this notebook.
- **Specification Freeze:** The immutable pre-test lock file (`FINAL_MODEL_SPECIFICATION_LOCKED.md`) was cryptographically verified and remained untouched.
