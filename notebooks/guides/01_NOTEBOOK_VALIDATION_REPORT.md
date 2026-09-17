# Notebook 01 Validation Report

**Notebook:** `notebooks/01_NHANES_Data_Preparation.ipynb`  
**Validation Timestamp:** 2026-09-03 23:22:26  
**Validation Status:** **ALL CHECKS PASSED — 100% REPRODUCIBLE**  

---

## 1. Execution Summary

| Property | Value |
|:---|:---|
| **Notebook File** | `notebooks/01_NHANES_Data_Preparation.ipynb` |
| **Total Cells** | 22 (12 Markdown, 10 Code) |
| **Execution Mode** | Clean Kernel Top-to-Bottom (`nbclient.NotebookClient`) |
| **Execution Status** | Succeeded without errors (`0` cell exceptions) |
| **Total Execution Time** | 3.59 seconds |
| **File SHA256** | `76d2944aa698befb8ae6731f65ed443c3aad7349f65ee4bd89bb20f995bb4e12` |

---

## 2. Source Files & Reference Datasets Used

### Raw Source Files (`nhanes_feasibility_2021_2023/raw/`)
- `DEMO_L.xpt` ($N = 11,933$)
- `BMX_L.xpt` ($N = 11,933$)
- `BPQ_L.xpt` ($N = 11,933$)
- `SMQ_L.xpt` ($N = 11,933$)
- `PAQ_L.xpt` ($N = 11,933$)
- `DIQ_L.xpt` ($N = 11,933$)
- `GHB_L.xpt` ($N = 11,933$)
- `GLU_L.xpt` ($N = 11,933$)

### Canonical Reference Datasets for Comparison (`nhanes_feasibility_2021_2023/processed_phase3/`)
- `canonical_screening_population.parquet` ($N = 4,260$)
- `analytic_core_complete.parquet` ($N = 4,194$)
- `analytic_expanded_complete.parquet` ($N = 4,044$)

---

## 3. Reproduction & Reconciliation Audit

| Check Description | Expected (Phase 3) | Observed (Notebook 01) | Discrepancy | Verification Status |
|:---|:---:|:---:|:---:|:---:|
| **Total Initial Merged Cohort** | 11,933 | 11,933 | 0 | **PASS** |
| **Adult Cohort (Age $\ge 18$)** | 8,153 | 8,153 | 0 | **PASS** |
| **Cohort E (No Prior Diagnosis)** | 5,907 | 5,907 | 0 | **PASS** |
| **Screening Base (Cohort E + Valid HbA1c)** | 4,260 | 4,260 | 0 | **PASS** |
| **Core Complete Population** | 4,194 | 4,194 | 0 | **PASS** |
| **Core Normal Glycemia ($< 5.7\%$)** | 3,224 | 3,224 | 0 | **PASS** |
| **Core Dysglycemia ($\ge 5.7\%$)** | 970 | 970 | 0 | **PASS** |
| **Expanded Complete Population** | 4,044 | 4,044 | 0 | **PASS** |
| **Expanded Normal Glycemia ($< 5.7\%$)** | 3,106 | 3,106 | 0 | **PASS** |
| **Expanded Dysglycemia ($\ge 5.7\%$)** | 938 | 938 | 0 | **PASS** |
| **SEQN Set Equality (Core)** | `True` | `True` | None | **PASS** |
| **SEQN Set Equality (Expanded)** | `True` | `True` | None | **PASS** |
| **PAD680 9999 Sentinel Removal** | 21 cases | 21 cases | 0 | **PASS** |
| **PAD680 7777 Sentinel Removal** | 1 case | 1 case | 0 | **PASS** |
| **Prohibited Leakage Variables in $X$** | 0 variables | 0 variables | 0 | **PASS** |

---

## 4. Discrepancies & Audit Findings

- **Discrepancies Found:** **ZERO**. All participant counts, class distributions, and feature sets match the canonical Phase-3 datasets with 100% mathematical precision.
- **Leakage Audit:** Confirmed that all 16 prohibited variables (`SEQN`, survey weights, lab values, cohort definition variables) are strictly absent from candidate predictor sets.
- **Model Training:** Confirmed that **zero machine learning models were fitted** in this notebook.
- **Artifact Protection:** All existing Phase-3 canonical Parquet files, Phase-4 split manifests, and Phase-5 model results were accessed in read-only mode and remained completely unmodified.
