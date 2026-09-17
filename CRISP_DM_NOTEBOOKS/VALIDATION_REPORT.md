# CRISP-DM Notebook Suite — Validation Report

**Execution Date:** 2026-09-17 22:31:20
**Total Suite Execution Time:** 6.91 seconds
**Status:** PASS — All Notebooks Clean

## Notebook Execution Results

| # | Notebook | Status | Code Cells | Runtime (s) | Cell Errors |
|:--|:---------|:-------|:-----------|:------------|:------------|
| 00 | `00_README_CRISP_DM.ipynb` | **PASS** | 1 | 2.18 | 0 |
| 01 | `01_BUSINESS_UNDERSTANDING.ipynb` | **PASS** | 0 | 0.00 | 0 |
| 02 | `02_DATA_UNDERSTANDING.ipynb` | **PASS** | 8 | 1.00 | 0 |
| 03 | `03_DATA_PREPARATION.ipynb` | **PASS** | 8 | 0.21 | 0 |
| 04 | `04_MODELING.ipynb` | **PASS** | 6 | 0.08 | 0 |
| 05 | `05_THRESHOLD_SELECTION.ipynb` | **PASS** | 6 | 1.31 | 0 |
| 06 | `06_FINAL_EVALUATION.ipynb` | **PASS** | 8 | 0.21 | 0 |
| 07 | `07_XAI_HUMAN_REVIEW.ipynb` | **PASS** | 5 | 1.90 | 0 |
| 08 | `08_STAGE2_USER_EVALUATION.ipynb` | **PASS** | 1 | 0.01 | 0 |

## Immutable Artifact Integrity Checks

| Artifact | Expected SHA-256 | Verification Status |
|:---------|:-----------------|:--------------------|
| `analytic_expanded_complete.parquet` | `6fa1dd5c92123592...` | **PASS (Byte-Identical)** |
| `master_split.csv` | `685b4a15a1ab5ea8...` | **PASS (Byte-Identical)** |
| `development_folds.csv` | `0bfacfaba04ffaa0...` | **PASS (Byte-Identical)** |
| `FINAL_MODEL_SPECIFICATION_LOCKED.md` | `7d2a5eb9c349dabf...` | **PASS (Byte-Identical)** |
| `COMPARATOR_SPECIFICATION_LOCKED.md` | `b2527b0681cc0ab3...` | **PASS (Byte-Identical)** |
| `PHASE5_EVALUATION_PROTOCOL_LOCKED.md` | `13bc7de29cde2d6b...` | **PASS (Byte-Identical)** |
| `final_test_predictions.csv` | `fac969a00df57d66...` | **PASS (Byte-Identical)** |
| `gam_final.pkl` | `204a94ff072ef4f1...` | **PASS (Byte-Identical)** |
| `logistic_final.pkl` | `4260bef53a88fb4e...` | **PASS (Byte-Identical)** |
| `dlnn_final.keras` | `e084f7c8711c3dd9...` | **PASS (Byte-Identical)** |

## Methodological Invariants Verified

1. **Partition Isolation:** Master split strictly yields Development N=3,232 and Test N=812.
2. **Zero Post-Test Tuning:** Frozen threshold $\tau=0.1389$ derived strictly from Development OOF predictions.
3. **Scientific Concordance:** Test sensitivity point estimate is exactly $86.39\%$ (165/191) with 95% CI [81.19%, 90.96%], specificity $42.51\%$ (264/621), ROC-AUC $0.7277$, PR-AUC $0.4503$.
4. **Mathematical Fidelity:** GAM additive term decomposition exactly reconstructs machine probabilities with error $\le 10^{-10}$.
5. **Human Override Semantics:** Override changes only referral action; input features, model probabilities, and ground truth remain strictly immutable.
6. **Stage-2 Clinical Governance:** HbA1c ranges presented as standard laboratory classifications, not automated AI diagnoses; selective verification warning explicitly stated.
