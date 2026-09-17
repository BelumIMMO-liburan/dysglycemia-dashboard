# Canonical NHANES Analytic Dataset Construction Report (Phase 3)

**Study:** Two-Stage Diabetes Screening Using Non-Laboratory Predictors and Laboratory Reference Standards
**Source Data:** Official CDC/NCHS NHANES August 2021–August 2023 Public-Use Release
**Status:** Construction and Validation Complete — **NO MACHINE LEARNING MODEL TRAINED**

---

## 1. Cohort Construction

The primary research population is **Cohort E (True No Known Dysglycemia)**, defined as:
- Age ≥ 18 at screening (`RIDAGEYR >= 18`)
- No self-reported history of diabetes (`DIQ010 == 2`)
- No self-reported history of prediabetes or borderline diabetes (`DIQ160 == 2`)

| Step | Criteria | Subsample N | Excluded N |
|:---|:---|---:|---:|
| 1. Full NHANES 2021–2023 | All participants | 11,933 | - |
| 2. Adult Base | `RIDAGEYR >= 18` | 8,153 | 3,780 children/adolescents |
| 3. Exclude Known Diabetes | `DIQ010 == 1` | 7,080 | 1,073 known diabetes |
| 4. Exclude Borderline Diabetes | `DIQ010 == 3` | 6,808 | 272 borderline diabetes |
| 5. Exclude Known Prediabetes | `DIQ160 == 1` | 5,924 | 884 known prediabetes |
| 6. Exclude Missing/Refused/DK | `DIQ010/DIQ160 in [7, 9, NaN]` | **5,907** | 17 missing/DK responses |
| 7. Require Valid HbA1c | `LBXGH.notna() & WTPH2YR > 0` | **4,260** | 1,647 without phlebotomy exam |

## 2. Primary Outcome Definition

The primary laboratory reference outcome is **Glycohemoglobin (HbA1c)** from `GHB_L.xpt`, validated by positive phlebotomy weight (`WTPH2YR > 0`).

### Continuous Reference Variable
- **`LBXGH`**: Glycohemoglobin (%)

### Primary Binary Screening Target
- **`hba1c_dysglycemia`**:
  - `0 = normal_range` (`LBXGH < 5.7%`)
  - `1 = dysglycemia_range` (`LBXGH ≥ 5.7%`)

### 3-Class Categorical Outcome
- **`hba1c_category`**:
  - `0 = normal_range` (`LBXGH < 5.7%`)
  - `1 = prediabetes_range` (`5.7% ≤ LBXGH < 6.5%`)
  - `2 = diabetes_range` (`LBXGH ≥ 6.5%`)

*(Terminology: These are laboratory RANGE labels. They represent laboratory-identified dysglycemia in a screening context, not confirmed clinical diagnoses.)*

## 3. Secondary Outcome Definition

Fasting plasma glucose (`LBXGLU` from `GLU_L.xpt`) is preserved for sensitivity and concordance analyses.
- **Analytic Validity Rule:** Valid ONLY when `LBXGLU` is non-missing AND fasting subsample weight `WTSAF2YR > 0`.
- **`fpg_dysglycemia`**: `0 = normal` (`< 100 mg/dL`), `1 = dysglycemia_range` (`≥ 100 mg/dL`).
- **`fpg_category`**: `0 = normal` (`< 100`), `1 = prediabetes_range` (`100–125.9`), `2 = diabetes_range` (`≥ 126 mg/dL`).
- *FPG is secondary and is NEVER required for inclusion in the primary HbA1c datasets.*

## 4. Predictor Definitions

### Core Stage-1 Candidate Predictors (Non-Laboratory Only)
1. **`age`** (`RIDAGEYR`): Participant age at screening (continuous, years, 18–80).
2. **`sex`** (`RIAGENDR`): Biological sex (`1 = Male`, `2 = Female`). Preserved with categorical semantics.
3. **`bmi`** (`BMXBMI`): Body mass index measured at MEC physical exam (continuous, kg/m²).
4. **`hypertension_history`** (`BPQ020`): Ever told had high blood pressure (`1 = Yes`, `2 = No`).
5. **`smoking_history`** (`SMQ020`): Smoked ≥100 cigarettes in lifetime (`1 = Yes`, `2 = No`). Strictly represents lifetime history.

### Expanded Stage-1 Candidate Predictors
6. **`waist_cm`** (`BMXWAIST`): Waist circumference measured at MEC physical exam (continuous, cm).
7. **`sedentary_minutes_day`** (`PAD680`): Self-reported minutes of sedentary activity per day (continuous, 0–1440 min).

### Preserved Raw Physical Activity Questionnaire Items (Un-Engineered)
- `PAD790Q`: Frequency of moderate leisure-time activity
- `PAD790U`: Unit for moderate leisure-time activity frequency
- `PAD800`: Duration of moderate leisure-time activity per session (minutes)
- `PAD810Q`: Frequency of vigorous leisure-time activity
- `PAD810U`: Unit for vigorous leisure-time activity frequency
- `PAD820`: Duration of vigorous leisure-time activity per session (minutes)

## 5. Recoding Rules & Transparency

- **Sex:** Retains official coding `1 = Male`, `2 = Female` (no arbitrary zero-reversal or artificial ordinal interpretation).
- **Hypertension (`BPQ020`):** `1 = Yes`, `2 = No`. Special codes `7` (Refused) and `9` (Don't Know) are explicitly set to `NaN`.
- **Smoking (`SMQ020`):** `1 = Yes`, `2 = No`. Special codes `7` and `9` are explicitly set to `NaN`.
- **Sedentary Activity (`PAD680`):** Special codes `7777` (Refused) and `9999` (Don't Know) are explicitly set to `NaN`.
- **SAS Floating-Point Zeroes:** Float underflow values (`~5.3976e-79`) normalized to exact `0.0` across all numeric fields.

## 6. Missing-Value Handling

- No missing-value imputation was performed.
- In `canonical_screening_population.parquet`, all Cohort E participants with valid HbA1c are preserved ($N = 4,260$) regardless of predictor completeness.
- In `analytic_core_complete.parquet`, complete-case filtering on the 5 core predictors yields $N = 4,194$ (98.45% of screening population).
- In `analytic_expanded_complete.parquet`, complete-case filtering on the 7 expanded predictors yields $N = 4,044$ (94.93% of screening population).

## 7. Core Analytic Dataset (`analytic_core_complete.parquet`)

- **Sample Size:** $N = 4,194$
- **Predictors Included:** `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`
- **Primary Binary Target:** `hba1c_dysglycemia`
  - Normal (`0`): **3,224 (76.87%)**
  - Dysglycemia (`1`): **970 (23.13%)**
- **3-Class Target:** `hba1c_category`
  - Normal (`0`): 3,224 (76.87%)
  - Prediabetes-range (`1`): 904 (21.55%)
  - Diabetes-range (`2`): 66 (1.57%)
- **Imbalance Ratio:** 3.32 : 1 (Normal : Dysglycemia)

## 8. Expanded Analytic Dataset (`analytic_expanded_complete.parquet`)

- **Sample Size:** $N = 4,044$
- **Predictors Included:** `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`
- **Primary Binary Target:** `hba1c_dysglycemia`
  - Normal (`0`): **3,106 (76.81%)**
  - Dysglycemia (`1`): **938 (23.19%)**
- **3-Class Target:** `hba1c_category`
  - Normal (`0`): 3,106 (76.81%)
  - Prediabetes-range (`1`): 872 (21.56%)
  - Diabetes-range (`2`): 66 (1.63%)
- **Imbalance Ratio:** 3.31 : 1 (Normal : Dysglycemia)

## 9. Summary of Class Distributions Across Datasets

| Dataset | Total N | Normal N (%) | Dysglycemia N (%) | Prediabetes N (%) | Diabetes N (%) |
|:---|---:|---:|---:|---:|---:|
| **canonical_screening_population** | 4,260 | 3,277 (76.92%) | 983 (23.08%) | 916 (21.50%) | 67 (1.57%) |
| **analytic_core_complete** | 4,194 | 3,224 (76.87%) | 970 (23.13%) | 904 (21.55%) | 66 (1.57%) |
| **analytic_expanded_complete** | 4,044 | 3,106 (76.81%) | 938 (23.19%) | 872 (21.56%) | 66 (1.63%) |

## 10. Survey Design Metadata Retained

The following survey design variables are preserved in all datasets for survey-weighted evaluation, domain analysis, and design effect estimation:
- **`WTINT2YR`**: 2-year full-sample interview weight
- **`WTMEC2YR`**: 2-year MEC examination weight
- **`WTPH2YR`**: 2-year phlebotomy weight (required for HbA1c / blood analytes)
- **`WTSAF2YR`**: 2-year fasting subsample weight (required for fasting glucose)
- **`SDMVSTRA`**: Masked variance pseudo-stratum
- **`SDMVPSU`**: Masked variance pseudo-PSU

*(All survey design variables are marked `allowed_as_predictor = FALSE` and must never enter the feature matrix X during model training).*

## 11. Leakage-Protection Verification

Strict data leakage guards were enforced during dataset construction:
- **Reference standard isolation:** `LBXGH`, `LBXGLU`, `hba1c_category`, `fpg_category`, `hba1c_dysglycemia`, `fpg_dysglycemia` are isolated as outcome variables.
- **Cohort definition isolation:** `DIQ010`, `DIQ160`, `DIQ180` are isolated as cohort tracking metadata and excluded from predictor sets.
- **Weights isolation:** `WTINT2YR`, `WTMEC2YR`, `WTPH2YR`, `WTSAF2YR`, `SDMVSTRA`, `SDMVPSU` are isolated as survey design metadata.
- **Verification:** Zero leakage variables appear in the core or expanded predictor lists.

## 12. Hashes and Reproducibility Status

### Output File Manifest

| filename                               |   row_count |   column_count |   target_positive_n |   target_negative_n | SHA256                                                           | creation_timestamp               | script_version   |
|:---------------------------------------|------------:|---------------:|--------------------:|--------------------:|:-----------------------------------------------------------------|:---------------------------------|:-----------------|
| canonical_screening_population.parquet |        4260 |             31 |                 983 |                3277 | 6d93adab4d74c9df8eea3c535d19bace4c7ff9c50cfb05f74280d67c6ae7656b | 2026-09-01T17:58:31.820016+00:00 | v1.0-phase3      |
| analytic_core_complete.parquet         |        4194 |             31 |                 970 |                3224 | facac5ae6aff9ce021956795ccb884ec0d1e95eaed34aeeb1f72e3127a5c7f42 | 2026-09-01T17:58:31.820016+00:00 | v1.0-phase3      |
| analytic_expanded_complete.parquet     |        4044 |             31 |                 938 |                3106 | 6fa1dd5c9212359271de03285806044f3d8a8f817c774bdd1e8c054fe75d1679 | 2026-09-01T17:58:31.820016+00:00 | v1.0-phase3      |
| raw/DEMO_L.xpt                         |       11933 |             27 |                 nan |                 nan | ca4374a158b493b8b0163e1388da21d57a18d1b9cecff2aa4e2fa2bec494fe23 | 2026-09-01T17:58:31.820016+00:00 | official_cdc_raw |
| raw/BMX_L.xpt                          |        8860 |             22 |                 nan |                 nan | 44440c416d9ad709e8b1708a5975378ab4d5b18edc39eb5015c2ae7186500170 | 2026-09-01T17:58:31.820016+00:00 | official_cdc_raw |
| raw/BPQ_L.xpt                          |        8501 |              6 |                 nan |                 nan | 0acde3af0526c375942fe0735e3bf69a0422bcbc606f98a478209d2f47baa4b5 | 2026-09-01T17:58:31.820016+00:00 | official_cdc_raw |
| raw/SMQ_L.xpt                          |        9015 |              9 |                 nan |                 nan | abbefebfa5585b1e19c079fa14be20c113a4649318070197214b258d05b93c50 | 2026-09-01T17:58:31.820016+00:00 | official_cdc_raw |
| raw/PAQ_L.xpt                          |        8153 |              8 |                 nan |                 nan | de34acfed4523f10f52bea06e64ed33c8db973cb38d3539eeceb2b68039248c8 | 2026-09-01T17:58:31.820016+00:00 | official_cdc_raw |
| raw/DIQ_L.xpt                          |       11744 |              9 |                 nan |                 nan | 9535a023673ae869afae19d842d8679e06f6a464606ac15900686b41ef05090f | 2026-09-01T17:58:31.820016+00:00 | official_cdc_raw |
| raw/GHB_L.xpt                          |        7199 |              3 |                 nan |                 nan | 67aee0353160e2392dc0a33bece99b90764a630c76d82415ac4639105ad9dd03 | 2026-09-01T17:58:31.820016+00:00 | official_cdc_raw |
| raw/GLU_L.xpt                          |        3996 |              4 |                 nan |                 nan | 70f773ab37e3d8485341f32137e280e05b9279e5fe9b6f0362e4052d8fe9a201 | 2026-09-01T17:58:31.820016+00:00 | official_cdc_raw |


### Integrity & Reproducibility Verification
- All 8 raw CDC/NCHS XPT files remain 100% untouched and verified against official SHA256 hashes.
- The construction pipeline was executed from clean state and confirmed 100% deterministic and reproducible.
- All row counts, target counts, and column schemas reconcile with the audit specifications.

---

### DATASET CONSTRUCTION COMPLETE — NO MODEL TRAINED