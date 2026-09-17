# Phase D2.4 Database Audit Report: Legacy Table Evaluation & Schema Strategy

**Phase:** D2.4  
**Status:** Complete & Verified  
**Date:** September 2026  
**Governing Skill:** `research-governance`  

---

## 1. Audit Mandate

Section 12 of the Phase D2.4 specification requires a rigorous architectural audit of all existing database models prior to executing any migrations:
> *"Before creating a migration: inspect the existing database models. Specifically audit any legacy model named Prediction, Result, RiskPrediction, Assessment or equivalent... DO NOT automatically reuse a legacy table simply because it exists."*

This report details the audit findings, classifications, and justification for the schema design implemented in Phase D2.4.

---

## 2. Legacy Table Inspection

An inspection of `dashboard/predictor/models.py` identified two legacy database entities: `Prediction` and `Override`.

### A. Model: `Prediction`
* **Fields:**
  - `id`: Auto-incrementing big integer.
  - `timestamp`: DateTime (`auto_now_add=True`).
  - `patient_data`: JSONField (`gender, age, hypertension, heart_disease, smoking, bmi, HbA1c, glucose`).
  - `model_used`: CharField (`'DLNN Baseline', 'DLNN + Focal Loss'`).
  - `prediction`: IntegerField (`0 = Not Diabetic, 1 = Diabetic`).
  - `confidence`: FloatField.
  - `threshold`: FloatField (`default=0.5`).
  - `shap_values`: JSONField.
  - `is_reviewed`: BooleanField (`default=False`).
* **Governance & Architectural Defects:**
  1. **Obsolete Kaggle Features:** Stores laboratory markers (`HbA1c`, `glucose`) and obsolete clinical variables (`heart_disease`), which violate the Stage-1 non-laboratory scope.
  2. **Diagnostic Claims:** Field `prediction` defines binary diabetes state (`"Diabetic"` vs `"Not Diabetic"`), violating the screening non-diagnostic boundary.
  3. **Multi-Model Contamination:** Explicitly supports non-approved deep learning baselines (`DLNN Baseline`).
  4. **Arbitrary Threshold:** Defaults to threshold `0.5`, violating the frozen research threshold `0.1389`.
  5. **Sequential IDs:** Exposes auto-incrementing integer IDs.
* **Classification:** **Class C: LEGACY — DO NOT USE**

---

### B. Model: `Override`
* **Fields:**
  - `id`: Auto-incrementing big integer.
  - `prediction`: ForeignKey to legacy `Prediction`.
  - `timestamp`: DateTime.
  - `doctor_name`: CharField (personal identifier).
  - `decision`: CharField (`'accept', 'reject'`).
  - `override_value`: IntegerField (`0 or 1`, doctor's corrected diabetes diagnosis).
  - `reason`: TextField.
  - `flagged_features`: JSONField.
* **Governance & Architectural Defects:**
  1. **Disease Overwrite:** Field `override_value` flips a disease diagnosis rather than adjusting a screening referral recommendation.
  2. **Privacy Violation:** Directly persists `doctor_name` as an unindexed string without role-based access control.
  3. **Coupled to Legacy Prediction:** Foreign key points to the obsolete Kaggle-based table.
* **Classification:** **Class C: LEGACY — DO NOT USE**

---

## 3. Schema Strategy: Dedicated `ScreeningRecord` Entity

Because the legacy tables violate core thesis governance rules, attempting to coerce or migrate them would risk silent regression and schema corruption. 

### Selected Strategy: Option C / Isolated Entity
1. **Retain Legacy Tables:** Leave `Prediction` and `Override` in `models.py` untouched to support ongoing historical audit endpoints without breaking existing routes (`/index/`, `/predict/`, `/prediction/<int:pk>/`).
2. **Create Dedicated Model:** Introduce `ScreeningRecord` representing exclusively the Stage-1 screening event:
   - **UUID Primary Key:** Completely eliminates sequential integer IDs.
   - **Strict Typed Inputs:** Individual fields for all 7 NHANES non-laboratory predictors.
   - **Provenance Tracking:** Stores SHA-256 hashes of `gam_final.pkl` and `preprocessor.pkl`.
   - **Immutability:** Designed as a permanent historical record that future human reviews reference rather than overwrite.
3. **Migration:** Applied clean Django migration `0002_screeningrecord.py`.

---

## 4. Migration Execution & Verification

Migration `predictor\migrations\0002_screeningrecord.py` was generated and executed:
```powershell
& python manage.py makemigrations predictor
& python manage.py migrate
& python manage.py check
```
Result: Zero migration conflicts, clean application to SQLite database, and zero silenced system check warnings.
