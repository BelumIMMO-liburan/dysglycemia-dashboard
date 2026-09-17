# Stage-1 Screening Input Contract
**Phase:** D2.2 — Stage-1 Non-Laboratory Screening Form  
**Governing Documents:**
- `FINAL_MODEL_SPECIFICATION_LOCKED.md` (Section 3.2: Seven Frozen Non-Laboratory Predictors)
- `research-governance` (Strict Research Boundary; Immutable Model & Features)
- `dashboard-design` (Evidence-First Architecture & Human-Readable Semantics)

---

## 1. Executive Summary & Purpose

This document defines the authoritative, deterministic input contract between the **Stage-1 Screening Form** (Phase D2.2) and the **Frozen GAM Model Inference Adapter** (Phase D2.3).

In strict accordance with the thesis methodology:
- Exactly **seven non-laboratory predictors** are accepted.
- Laboratory biomarkers (venous plasma glucose, capillary blood glucose, HbA1c) and extraneous physical measurements (heart disease, weight, height, cholesterol, blood pressure readings) are **strictly excluded** from Stage-1 intake.
- Missing values are **strictly prohibited** (no imputation exists in the frozen model).
- The UI captures human-readable semantic values; conversion to the model's numerical representations is performed strictly in Phase D2.3.

---

## 2. Canonical Predictor Order

The seven predictors must always be processed in this immutable canonical order:
1. `age`
2. `sex`
3. `bmi`
4. `hypertension_history`
5. `smoking_history`
6. `waist_cm`
7. `sedentary_minutes_day`

---

## 3. Predictor Specification Table

| Canonical Name | UI Label | NHANES Source | Meaning & Research Definition | UI Datatype | Model Datatype / D2.3 Contract | Unit | Req. | Supported Range / Choices | Validation Error Behavior | Example Valid | Example Invalid |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **`age`** | Age | `RIDAGEYR` | Completed years of age at exam. Adults $\ge 18$. Age 80 is top-coded in NHANES. | Integer | `float64` continuous, transformed by `preprocessor.pkl` `StandardScaler` | years | Yes | `18` to `80` (inclusive) | Rejects $<18$, $>80$, decimals, strings. "Enter an age within the model-supported research range (18 to 80 years)." | `52` | `17`, `85`, `52.5` |
| **`sex`** | Biological Sex | `RIAGENDR` | Biological sex as recorded in the NHANES research protocol. | String (`'male'`, `'female'`) | Binary factor $f(1)$: `male` $\rightarrow 1$, `female` $\rightarrow 0$ | None | Yes | `['male', 'female']` | Rejects missing, empty, or unmodeled categories ("other", "unknown"). "Select a valid choice (Male or Female)." | `male` | `'other'`, `None` |
| **`bmi`** | Body Mass Index (BMI) | `BMXBMI` | Measured at MEC physical exam: $\text{weight (kg)} / \text{height (m)}^2$. | Float (1 decimal) | `float64` continuous, transformed by `preprocessor.pkl` `StandardScaler` | $\text{kg/m}^2$ | Yes | `11.1` to `69.9` (inclusive) | Rejects $<11.1$, $>69.9$, non-numeric. Rounds to 1 decimal. "BMI is outside the range supported by the research model (11.1 to 69.9 kg/m²)." | `28.4` | `10.5`, `75.0`, `'obese'` |
| **`hypertension_history`** | History of Hypertension | `BPQ020` | Self-reported prior diagnosis: "Ever told by doctor/health professional that you have high blood pressure." | String (`'yes'`, `'no'`) | Binary factor $f(3)$: `yes` $\rightarrow 1$, `no` $\rightarrow 0$ | None | Yes | `['yes', 'no']` | Rejects non-binary options. "Select a valid choice (Yes or No)." | `yes` | `'borderline'`, `None` |
| **`smoking_history`** | Smoking History | `SMQ020` | Lifetime smoking history: smoked at least 100 cigarettes in lifetime (NHANES criterion). | String (`'yes'`, `'no'`) | Binary factor $f(4)$: `yes` $\rightarrow 1$, `no` $\rightarrow 0$ | None | Yes | `['yes', 'no']` | Rejects non-binary options. "Select a valid choice (Yes or No)." | `no` | `'former'`, `None` |
| **`waist_cm`** | Waist Circumference | `BMXWAIST` | Measured waist circumference at MEC physical exam. | Float (1 decimal) | `float64` continuous, transformed by `preprocessor.pkl` `StandardScaler` | cm | Yes | `60.0` to `187.0` (inclusive) | Rejects $<60.0$, $>187.0$, strings. Rounds to 1 decimal. "Waist circumference is outside the range supported by the research model (60.0 to 187.0 cm)." | `98.5` | `55.0`, `195.0`, `'38 inches'` |
| **`sedentary_minutes_day`** | Sedentary Time | `PAD680` | Self-reported minutes spent sitting or reclining per typical day (excluding sleep). | Integer | `float64` continuous, transformed by `preprocessor.pkl` `StandardScaler` | min/day | Yes | `0` to `1200` (0 to 20 hours/day) | Rejects $<0$, $>1200$, NHANES sentinels (`7777`, `9999`). "Sedentary time is outside the range supported by the research model (0 to 1200 minutes/day)." | `480` | `-15`, `1440`, `7777`, `9999` |

---

## 4. Phase D2.3 Inference Preprocessing Contract

When Phase D2.3 activates model inference:
1. **Input Delivery:** Form inputs will be delivered from `Stage1ScreeningForm.cleaned_data`.
2. **Deterministic Encodings:**
   - `sex_code = 1 if data['sex'] == 'male' else 0`
   - `hyp_code = 1 if data['hypertension_history'] == 'yes' else 0`
   - `smk_code = 1 if data['smoking_history'] == 'yes' else 0`
3. **Feature Vector Order:**
   The features must be assembled into a DataFrame matching the columns used during model training:
   ```python
   ['age', 'sex', 'bmi', 'hypertension_history', 'smoking_history', 'waist_cm', 'sedentary_minutes_day']
   ```
4. **StandardScaler Transformation:**
   Continuous columns (`age`, `bmi`, `waist_cm`, `sedentary_minutes_day`) are transformed using `preprocessor.pkl` fitted exclusively on development data ($N = 3,232$).
5. **GAM Prediction:**
   Probability is generated using `gam_final.predict_mu(X_transformed)[0]` and compared against the frozen threshold `0.1389`.

---

## 5. Excluded Variables (Strict Boundary Enforcement)

The following variables are explicitly barred from the Stage-1 interface:
- `LBXGH` (HbA1c) — Stage-2 confirmatory laboratory outcome only.
- `LBXGLU` (Fasting Glucose) — Laboratory biomarker excluded from non-laboratory screening.
- `BMXWT`, `BMXHT` (Weight, Height) — Redundant with BMI; not included in the 7-predictor model.
- `BPXSY1`, `BPXDI1` (Measured Blood Pressure) — Office clinical measurements; model relies exclusively on self-reported hypertension history.
- `MCQ160C` (Coronary Heart Disease) — Not selected in the final parsimonious model.
- `DIQ010`, `DIQ160` (Prior Diabetes Diagnosis) — Exclusion criteria defining the target screening population (previously undiagnosed individuals).
