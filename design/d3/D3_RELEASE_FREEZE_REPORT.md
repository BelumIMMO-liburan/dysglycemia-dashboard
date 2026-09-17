# D3 Release Freeze Report — Research Prototype v1.0

**Release Tag:** `research-prototype-v1.0`  
**Date of Freeze:** 2026-09-05  
**Audit Status:** APPROVED & FROZEN  
**Next Permitted Changes:** Defect corrections directly addressing documented bugs in formal study evaluation protocol.

---

## 1. Scope of the Freeze

With the completion of Phase D3, all active product development is formally frozen.

### Specifically Frozen:
- **Predictor Architecture:** Exactly seven Stage-1 non-laboratory predictors (`age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`).
- **Operating Model:** PyGAM Generalized Additive Model (`gam_final.pkl`, λ=10.0, 10 splines/continuous predictor).
- **Decision Authority:** Operating decision threshold locked at `0.1389`.
- **Explainability Engine:** GAM-native partial dependence on the log-odds scale (`screening_explanation.py`).
- **Human Review Taxonomy:** Locked reason codes for Refer to No-Refer and No-Refer to Refer overrides.
- **Stage-2 Classification:** ADA 2026 reference cutoffs (`< 5.7%` Normal, `5.7%–6.4%` Prediabetes, `≥ 6.5%` Diabetes).
- **Analytics Metrics:** Exact metrics defined in D2.10.

### Strictly Prohibited Post-Freeze:
- No new ML models (no Random Forest, XGBoost, or DLNN reintroduction).
- No threshold sliders or client adjustments.
- No new laboratory parameters (no fasting glucose or oral glucose tolerance tests).
- No speculative UI redesigns.
- No survey instrumentation, SUS scoring, or questionnaire code inside the core application before separate study protocol locking.

---

## 2. Release Verification Artifacts

- **Automated Test Suite:** 144 unit and integration tests passing.
- **Visual Evidence:** 11 reference screenshots in `design/d3/screenshots/`.
- **Clean Study Baseline:** `dashboard/db_study.sqlite3` initialized with zero records.
- **Archived Development DB:** `dashboard/db_development_archive_d2_10.sqlite3` preserved.
