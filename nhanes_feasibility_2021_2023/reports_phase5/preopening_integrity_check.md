# Pre-Opening Integrity Check (Phase 5)

**Gate Execution Date:** 2026-09-02  
**Gate Status:** PASSED - AUTHORIZED TO OPEN FINAL TEST  

---

## Cryptographic Hash Verification Manifest

| Artifact Name | Path | Expected SHA256 | Actual SHA256 | Status |
|:---|:---|:---|:---|:---:|
| `master_split.csv` | `splits_phase4\master_split.csv` | `685b4a15a1ab5ea83647f91f6c335a8a44b2179e47eaab186bdd1960a583f9ed` | `685b4a15a1ab5ea83647f91f6c335a8a44b2179e47eaab186bdd1960a583f9ed` | **PASS** |
| `development_folds.csv` | `splits_phase4\development_folds.csv` | `0bfacfaba04ffaa02ea0f82294478c0d2790012c0d5466490e85956fabd028e1` | `0bfacfaba04ffaa02ea0f82294478c0d2790012c0d5466490e85956fabd028e1` | **PASS** |
| `analytic_expanded_complete.parquet` | `processed_phase3\analytic_expanded_complete.parquet` | `6fa1dd5c9212359271de03285806044f3d8a8f817c774bdd1e8c054fe75d1679` | `6fa1dd5c9212359271de03285806044f3d8a8f817c774bdd1e8c054fe75d1679` | **PASS** |
| `FINAL_MODEL_SPECIFICATION_LOCKED.md` | `lock_phase4_2\FINAL_MODEL_SPECIFICATION_LOCKED.md` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | **PASS** |
| `FINAL_TEST_OPENING_AUTHORIZATION.txt` | `lock_phase4_2\FINAL_TEST_OPENING_AUTHORIZATION.txt` | `549d01da760fd23ec42eaf422a891e8c2406c5232698f215009d094f193f41cc` | `549d01da760fd23ec42eaf422a891e8c2406c5232698f215009d094f193f41cc` | **PASS** |
| `final_model_specification.json` | `lock_phase4_2\final_model_specification.json` | `422c45977100359ca955100194ab1e97e9edf9a7326a0c56eb95a800a6067fbb` | `422c45977100359ca955100194ab1e97e9edf9a7326a0c56eb95a800a6067fbb` | **PASS** |
| `COMPARATOR_SPECIFICATION_LOCKED.md` | `lock_phase4_2\COMPARATOR_SPECIFICATION_LOCKED.md` | `b2527b0681cc0ab31b0d38d67f98233d65e308c237870312cdd4d9229b47bbd1` | `b2527b0681cc0ab31b0d38d67f98233d65e308c237870312cdd4d9229b47bbd1` | **PASS** |
| `comparator_specification.json` | `lock_phase4_2\comparator_specification.json` | `0449e0dd8fe8def6e63bccd6123771264dcbe88c8a2b949b92a09d17910fd80b` | `0449e0dd8fe8def6e63bccd6123771264dcbe88c8a2b949b92a09d17910fd80b` | **PASS** |
| `PHASE5_EVALUATION_PROTOCOL_LOCKED.md` | `lock_phase4_2\PHASE5_EVALUATION_PROTOCOL_LOCKED.md` | `13bc7de29cde2d6ba0da1b408a3b579e90758a96dfbe0bd4de24a8f1fdf51910` | `13bc7de29cde2d6ba0da1b408a3b579e90758a96dfbe0bd4de24a8f1fdf51910` | **PASS** |

---

## Gate Verdict

- **Core Datasets & Splits:** Verified identical to locked Phase 4 protocol.
- **Primary & Comparator Specifications:** Verified immutable and intact.
- **Authorization:** Final test set partition is authorized for single-batch Phase 5 evaluation.
