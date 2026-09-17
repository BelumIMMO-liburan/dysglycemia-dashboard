# Authoritative Source-of-Truth Index

**Objective:** Map every key research question, parameter, and system contract to its single authoritative artifact.

---

## 1. Research Question & Claim Mapping

| Research Area / Question | Authoritative Source-of-Truth Artifact | Key Authorized Values / Rules |
| :--- | :--- | :--- |
| **Model Mathematical Specification** | `nhanes_feasibility_2021_2023/lock_phase4_2/FINAL_MODEL_SPECIFICATION_LOCKED.md` | Splines=10, λ=10.0, Family=binomial, Link=logit, 7 non-lab predictors |
| **Final Confirmatory Model Performance** | `nhanes_feasibility_2021_2023/reports_phase5/phase5_final_evaluation_report_v1_1.md` | Sensitivity: 86.39%, Specificity: 42.51%, ROC-AUC: 0.7277, PR-AUC: 0.4503 |
| **Operating Decision Threshold** | `dashboard/predictor/services/screening_inference.py` (`FROZEN_DECISION_THRESHOLD`) | `0.1389` (Development-derived operating threshold; Single decision authority) |
| **Canonical Predictor Order** | `dashboard/predictor/screening_schema.py` (`CANONICAL_PREDICTOR_ORDER`) | `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day` |
| **Stage-1 Input Validation Bounds** | `dashboard/predictor/screening_schema.py` (`STAGE1_INPUT_SCHEMA`) | Age 18–85, BMI 10.0–70.0, Waist 40.0–200.0, Sedentary 0–1200 min/day |
| **GAM-Native Explainability Contract** | `dashboard/predictor/services/screening_explanation.py` | Additive decomposition on link scale, tolerance `1e-10`, zero legacy SHAP |
| **Human Review & Override Semantics** | `dashboard/predictor/models.py` (`HumanReview`) | Actions: `accepted` (concordance), `overridden` (with structured taxonomy) |
| **Stage-2 Confirmatory Laboratory Reference** | `dashboard/predictor/services/hba1c_range.py` (`RANGE_RULE_VERSION`) | ADA 2026 cutoffs: Normal `< 5.7%`, Prediabetes `5.7%–6.4%`, Diabetes `≥ 6.5%` |
| **Operational Analytics Denominators** | `dashboard/predictor/services/research_analytics.py` | Strict selective verification safeguards; agreement ≠ accuracy |
| **Release System State** | `docs/SYSTEM_RELEASE_MANIFEST.md` | Freeze identifier `research-prototype-v1.0`, Python 3.10.11, Django 5.2.17 |
