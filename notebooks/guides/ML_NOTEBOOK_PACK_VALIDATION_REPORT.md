# Machine Learning Notebook Pack Validation Report

**Suite:** Two-Stage Non-Laboratory Screening for Unrecognized HbA1c-Defined Dysglycemia  
**Validation Timestamp:** 2026-09-03 23:39:25  
**Overall Validation Result:** **ALL 4 NOTEBOOKS VALIDATED — ZERO DISCREPANCIES — 100% REPRODUCIBLE**  

---

## 1. Notebook Execution Summary

| Notebook File | SHA256 Hash | Runtime | Total Cells | Execution Status |
|:---|:---|:---:|:---:|:---:|
| **`01_NHANES_Data_Preparation.ipynb`** | `0f8b42d7b12a1c250c8a095af4b171eea4762caea4cdd40347a6382ba21c4f20` | 3.64s | 22 | **PASS** |
| **`02_Model_Development.ipynb`** | `5f61ed891fca8972ead5f9de4c62bad0f4e1aaadb0cd3ebdc6379ff8d2e7d0bf` | 4.22s | 25 | **PASS** |
| **`03_Model_Selection.ipynb`** | `6a038d0883bfe01cf6659a05c4359210943c93893cf62aa1b2f013c126e400a0` | 3.72s | 23 | **PASS** |
| **`04_Final_Test_Evaluation.ipynb`** | `2f3a63b32910ddca5714b75b3dd46b5b8008c436ce6927fff0326f9f2eadb7bc` | 3.88s | 22 | **PASS** |

---

## 2. Notebook-by-Notebook Reproduction Results

### Notebook 01: `01_NHANES_Data_Preparation.ipynb`
- **Phase Represented:** Phase 3 Canonical Dataset Construction
- **Execution Mode:** Full in-memory reproduction and read-only verification
- **Result:** **Development experiment reproducible and verified**.
- **Audit Concordance:** Replicated canonical expanded cohort ($N = 4,044$) and core cohort ($N = 4,194$) with 100% SEQN set equality and zero predictor missingness discrepancies. Verified the 22-participant `PAD680` sentinel code reconciliation ($N = 4,066 	o 4,044$).

### Notebook 02: `02_Model_Development.ipynb`
- **Phase Represented:** Phase 4 Benchmark Modeling
- **Execution Mode:** Verified replay and recalculation of audited Phase-4 OOF predictions
- **Result:** **Development experiment reproducible and verified**.
- **Audit Concordance:** Reconciled pooled and fold-level cross-validation metrics across all 12 candidate configurations to 4 decimal places against `reports_phase4/cv_model_summary.csv` (GAM Expanded: ROC-AUC $0.7382$, PR-AUC $0.4207$, Brier $0.1561$).

### Notebook 03: `03_Model_Selection.ipynb`
- **Phase Represented:** Phase 4.1 Pre-Final Model Selection & Operating-Point Audit
- **Execution Mode:** Read-only selection hierarchy and bootstrap verification
- **Result:** **Development selection reproducible and verified**.
- **Audit Concordance:** Verified selection hierarchy ranks, 2,000 paired bootstrap confidence intervals, calibration diagnostics, and sensitivity floor analysis ($80\%, 85\%, 90\%, 95\%$). Reconciled the primary GAM decision threshold at **`0.1389`** targeting the $\ge 90\%$ development sensitivity floor.

### Notebook 04: `04_Final_Test_Evaluation.ipynb`
- **Phase Represented:** Phase 5 Confirmatory Held-Out Final Test Evaluation
- **Execution Mode:** Strictly read-only metric calculation on frozen predictions (Zero model fitting or inference calls)
- **Result:** **Frozen Phase-5 result verification reproducible**.
- **Audit Concordance:** Verified prediction hash `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923`. Confirmed test discrimination (GAM ROC-AUC $0.7277$, PR-AUC $0.4503$) and frozen-threshold performance ($86.39\%$ sensitivity, $42.51\%$ specificity, $522$ referred, $165$ captured, $26$ missed).

---

## 3. Cryptographic Verification of Locked Canonical Artifacts

To guarantee that executing the notebook suite did not alter the scientific record, all 10 locked source-of-truth artifacts were cryptographically verified before and after execution:

| Locked Artifact Name | Expected Reference SHA256 | Observed Post-Execution SHA256 | Verification Status |
|:---|:---|:---|:---:|
| **`analytic_expanded_complete.parquet`** | `6fa1dd5c9212359271de03285806044f3d8a8f817c774bdd1e8c054fe75d1679` | `6fa1dd5c9212359271de03285806044f3d8a8f817c774bdd1e8c054fe75d1679` | **PASS** |
| **`master_split.csv`** | `685b4a15a1ab5ea83647f91f6c335a8a44b2179e47eaab186bdd1960a583f9ed` | `685b4a15a1ab5ea83647f91f6c335a8a44b2179e47eaab186bdd1960a583f9ed` | **PASS** |
| **`development_folds.csv`** | `0bfacfaba04ffaa02ea0f82294478c0d2790012c0d5466490e85956fabd028e1` | `0bfacfaba04ffaa02ea0f82294478c0d2790012c0d5466490e85956fabd028e1` | **PASS** |
| **`FINAL_MODEL_SPECIFICATION_LOCKED.md`** | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | **PASS** |
| **`COMPARATOR_SPECIFICATION_LOCKED.md`** | `b2527b0681cc0ab31b0d38d67f98233d65e308c237870312cdd4d9229b47bbd1` | `b2527b0681cc0ab31b0d38d67f98233d65e308c237870312cdd4d9229b47bbd1` | **PASS** |
| **`PHASE5_EVALUATION_PROTOCOL_LOCKED.md`** | `13bc7de29cde2d6ba0da1b408a3b579e90758a96dfbe0bd4de24a8f1fdf51910` | `13bc7de29cde2d6ba0da1b408a3b579e90758a96dfbe0bd4de24a8f1fdf51910` | **PASS** |
| **`final_test_predictions.csv`** | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` | **PASS** |
| **`gam_final.pkl`** | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` | **PASS** |
| **`logistic_final.pkl`** | `4260bef53a88fb4ed3ac30605eaf09c3684b203988e3d1b8e93e4fcc86ea78e6` | `4260bef53a88fb4ed3ac30605eaf09c3684b203988e3d1b8e93e4fcc86ea78e6` | **PASS** |
| **`dlnn_final.keras`** | `e084f7c8711c3dd91515f915ba16b3a5c4893bc7222b25f35e2f46d3f8f11bde` | `e084f7c8711c3dd91515f915ba16b3a5c4893bc7222b25f35e2f46d3f8f11bde` | **PASS** |

---

## 4. Final Scientific Governance Attestation

1. **Prediction Immutability:** The final test prediction file (`predictions_phase5/final_test_predictions.csv`) remained **100% byte-identical** before and after execution.
2. **Zero Post-Test Tuning:** No model was retrained, no hyperparameters were altered, no thresholds were shifted, and no post-hoc calibration was applied.
3. **Reproducibility Guarantee:** All 4 notebooks execute cleanly top-to-bottom from a clean Python 3 kernel in under 20 seconds combined runtime.
