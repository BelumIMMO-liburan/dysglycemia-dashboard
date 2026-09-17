# System Release Manifest — Research Prototype v1.0

**Release Identifier:** `research-prototype-v1.0`  
**Release Date:** 2026-09-05  
**Institution:** Undergraduate Information Systems Research  
**Authoritative Environment:** Local Python 3.10 / Django 5.2 Research Environment  
**Repository State:** Frozen for User-Study Protocol Design

---

## 1. Runtime Environment & Dependencies

| Component / Package | Exact Version | Semantic Purpose |
| :--- | :--- | :--- |
| **Python** | 3.10.11 (64-bit AMD64) | Base Python runtime |
| **Django** | 5.2.17 | Web framework & ORM |
| **pyGAM** | 0.12.0 | Frozen Generalized Additive Model runtime |
| **scikit-learn** | 1.7.2 | StandardScaler unpickling & preprocessing |
| **NumPy** | 2.2.6 | Array computation & numeric validation |
| **SciPy** | 1.15.3 | Numerical spline computation dependency |
| **pandas** | 2.3.3 | DataFrame serialization for preprocessor input |
| **joblib** | 1.6.0 | Serialized pipeline dependency |
| **Database Engine** | SQLite 3.x | Lightweight, file-based research database |

---

## 2. Protected Model & Evaluation Artifacts

| Artifact | Relative Path | Canonical SHA-256 Hash |
| :--- | :--- | :--- |
| **Frozen GAM Model** | `nhanes_feasibility_2021_2023/models_phase5/gam_final.pkl` | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` |
| **Preprocessor** | `nhanes_feasibility_2021_2023/models_phase5/preprocessor.pkl` | `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` |
| **Locked Model Spec** | `nhanes_feasibility_2021_2023/lock_phase4_2/FINAL_MODEL_SPECIFICATION_LOCKED.md` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` |
| **Final Test Predictions** | `nhanes_feasibility_2021_2023/predictions_phase5/final_test_predictions.csv` | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` |

---

## 3. Database State & Migrations

- **Migration Head:** `predictor.0006_stage2assessment`
- **Active Routes:** 12 production-research routes (Overview, New Screening, Run, Result, Accept Review, Override Review, Stage 2, Stage 2 Confirm, Review Queue, History, Analytics, About the Model).
- **Environment Modes:** `APP_DATA_MODE=development` (default, links to `db.sqlite3`), `APP_DATA_MODE=study` (links to clean `db_study.sqlite3`).
- **Total Passing Automated Tests:** 144 tests.

---

## 4. Known Methodological Limitations

1. **Population Generalizability:** Developed on US NHANES 2021–August 2023; not validated on Indonesian or local Asian cohorts.
2. **Non-Diagnostic Nature:** Provides a risk-stratified referral signal; not a medical device or definitive diagnosis.
3. **Verification Bias in Stage 2:** Stage 2 laboratory assessments represent a non-random referred subpopulation and cannot be used to calculate unbiased sensitivity or disease prevalence.
