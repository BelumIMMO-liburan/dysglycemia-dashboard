# NHANES August 2021–August 2023 Feasibility Audit Report (Version 2)

**Purpose:** Assess whether official CDC/NCHS NHANES 2021–2023 public-use data can support a
two-stage diabetes screening study using non-laboratory Stage-1 predictors
and laboratory-based Stage-2 reference outcomes.

**Audit Version 2 Corrections:**
1. Normalized SAS/XPT floating-point zero underflow (`~5.3976e-79` to `0.0`) and reconciled fasting subsample weights against official CDC codebook.
2. Preserved 2-year phlebotomy weight (`WTPH2YR`) for HbA1c and blood analytes.
3. Added Cohort E (`no_known_dysglycemia`: adults age ≥ 18 with `DIQ010 == 2` AND `DIQ160 == 2`) with complete exclusion breakdown.
4. Corrected physical activity variable descriptions (`PAD790Q/U`, `PAD800`, `PAD810Q/U`, `PAD820`, `PAD680`) against official CDC/NCHS documentation.
5. Recalculated all fasting glucose metrics using analytically valid observations only (`LBXGLU.notna() & WTSAF2YR > 0`).

**This report contains factual findings only. It does not recommend a final
research design, target variable, feature set, or model.**

---
## 1. Data Files and Provenance

All 8 XPT files were downloaded exclusively from official CDC/NCHS endpoints:
`https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/`

| filename   | exists   |   size_bytes | sha256                                                           | manifest_sha256                                                  | hash_status   |
|:-----------|:---------|-------------:|:-----------------------------------------------------------------|:-----------------------------------------------------------------|:--------------|
| DEMO_L.xpt | True     |      2582160 | ca4374a158b493b8b0163e1388da21d57a18d1b9cecff2aa4e2fa2bec494fe23 | ca4374a158b493b8b0163e1388da21d57a18d1b9cecff2aa4e2fa2bec494fe23 | MATCH         |
| BMX_L.xpt  | True     |      1563200 | 44440c416d9ad709e8b1708a5975378ab4d5b18edc39eb5015c2ae7186500170 | 44440c416d9ad709e8b1708a5975378ab4d5b18edc39eb5015c2ae7186500170 | MATCH         |
| BPQ_L.xpt  | True     |       409680 | 0acde3af0526c375942fe0735e3bf69a0422bcbc606f98a478209d2f47baa4b5 | 0acde3af0526c375942fe0735e3bf69a0422bcbc606f98a478209d2f47baa4b5 | MATCH         |
| SMQ_L.xpt  | True     |       651120 | abbefebfa5585b1e19c079fa14be20c113a4649318070197214b258d05b93c50 | abbefebfa5585b1e19c079fa14be20c113a4649318070197214b258d05b93c50 | MATCH         |
| PAQ_L.xpt  | True     |       409520 | de34acfed4523f10f52bea06e64ed33c8db973cb38d3539eeceb2b68039248c8 | de34acfed4523f10f52bea06e64ed33c8db973cb38d3539eeceb2b68039248c8 | MATCH         |
| DIQ_L.xpt  | True     |       847600 | 9535a023673ae869afae19d842d8679e06f6a464606ac15900686b41ef05090f | 9535a023673ae869afae19d842d8679e06f6a464606ac15900686b41ef05090f | MATCH         |
| GHB_L.xpt  | True     |       174000 | 67aee0353160e2392dc0a33bece99b90764a630c76d82415ac4639105ad9dd03 | 67aee0353160e2392dc0a33bece99b90764a630c76d82415ac4639105ad9dd03 | MATCH         |
| GLU_L.xpt  | True     |       129200 | 70f773ab37e3d8485341f32137e280e05b9279e5fe9b6f0362e4052d8fe9a201 | 70f773ab37e3d8485341f32137e280e05b9279e5fe9b6f0362e4052d8fe9a201 | MATCH         |


SHA256 hashes match `file_manifest.csv` exactly. Zero duplicate `SEQN` values exist in any file.
## 2. Raw Participant Counts

| source_file   | description                                         |   source_n |   matched |   unmatched_in_source |
|:--------------|:----------------------------------------------------|-----------:|----------:|----------------------:|
| DEMO_L.xpt    | Demographics (base)                                 |      11933 |     11933 |                     0 |
| BMX_L.xpt     | Body Measures                                       |       8860 |      8860 |                     0 |
| BPQ_L.xpt     | Blood Pressure / Cholesterol Questionnaire          |       8501 |      8501 |                     0 |
| SMQ_L.xpt     | Smoking Questionnaire                               |       9015 |      9015 |                     0 |
| PAQ_L.xpt     | Physical Activity Questionnaire                     |       8153 |      8153 |                     0 |
| DIQ_L.xpt     | Diabetes Questionnaire                              |      11744 |     11744 |                     0 |
| GHB_L.xpt     | Glycohemoglobin (HbA1c + Phlebotomy Weight WTPH2YR) |       7199 |      7199 |                     0 |
| GLU_L.xpt     | Fasting Glucose (FPG + Fasting Weight WTSAF2YR)     |       3996 |      3996 |                     0 |


Every participant in component files successfully matched onto the baseline `DEMO_L` table.
## 3. Variable Availability & Definitions

| variable   | source_file   | description                                                                           | dtype   |   valid_n |   missing_n |   missing_pct |      min |      max |
|:-----------|:--------------|:--------------------------------------------------------------------------------------|:--------|----------:|------------:|--------------:|---------:|---------:|
| SEQN       | DEMO_L.xpt    | Respondent sequence number                                                            | float64 |     11933 |           0 |          0    | 130400   | 142300   |
| RIDAGEYR   | DEMO_L.xpt    | Age in years at screening (0-80; 80 = 80+)                                            | float64 |     11933 |           0 |          0    |      0   |     80   |
| RIAGENDR   | DEMO_L.xpt    | Gender (1=Male, 2=Female)                                                             | float64 |     11933 |           0 |          0    |    nan   |    nan   |
| WTINT2YR   | DEMO_L.xpt    | Full sample 2-year interview weight                                                   | float64 |     11933 |           0 |          0    |   4584   | 171000   |
| WTMEC2YR   | DEMO_L.xpt    | Full sample 2-year MEC exam weight                                                    | float64 |     11933 |           0 |          0    |      0   | 227100   |
| SDMVSTRA   | DEMO_L.xpt    | Masked variance pseudo-stratum                                                        | float64 |     11933 |           0 |          0    |    173   |    187   |
| SDMVPSU    | DEMO_L.xpt    | Masked variance pseudo-PSU                                                            | float64 |     11933 |           0 |          0    |      1   |      2   |
| BMXBMI     | BMX_L.xpt     | Body mass index (kg/m²)                                                               | float64 |      8471 |         389 |          4.39 |     11.1 |     74.8 |
| BMXWAIST   | BMX_L.xpt     | Waist circumference (cm)                                                              | float64 |      8190 |         670 |          7.56 |     39.8 |    187   |
| BPQ020     | BPQ_L.xpt     | Ever told you had high blood pressure (1=Yes, 2=No, 7=Refused, 9=DK)                  | float64 |      8498 |           3 |          0.04 |    nan   |    nan   |
| BPQ150     | BPQ_L.xpt     | Had blood cholesterol checked in past 5 years (1=Yes, 2=No, 7=Refused, 9=DK)          | float64 |      2969 |        5532 |         65.07 |    nan   |    nan   |
| SMQ020     | SMQ_L.xpt     | Smoked at least 100 cigarettes in life (1=Yes, 2=No, 7=Refused, 9=DK)                 | float64 |      8135 |         880 |          9.76 |    nan   |    nan   |
| SMQ040     | SMQ_L.xpt     | Do you now smoke cigarettes (1=Every day, 2=Some days, 3=Not at all, 7=Refused, 9=DK) | float64 |      3243 |        5772 |         64.03 |    nan   |    nan   |
| PAD790Q    | PAQ_L.xpt     | Frequency of moderate leisure-time physical activity (number of days)                 | float64 |      8135 |          18 |          0.22 |      0   |   9999   |
| PAD790U    | PAQ_L.xpt     | Frequency unit for moderate leisure-time activity (D=Day, W=Week, M=Month, Y=Year)    | object  |      8153 |           0 |          0    |    nan   |    nan   |
| PAD800     | PAQ_L.xpt     | Duration of moderate leisure-time activity per session (minutes)                      | float64 |      6390 |        1763 |         21.62 |      1   |   9999   |
| PAD810Q    | PAQ_L.xpt     | Frequency of vigorous leisure-time physical activity (number of days)                 | float64 |      8139 |          14 |          0.17 |      0   |   9999   |
| PAD810U    | PAQ_L.xpt     | Frequency unit for vigorous leisure-time activity (D=Day, W=Week, M=Month, Y=Year)    | object  |      8153 |           0 |          0    |    nan   |    nan   |
| PAD820     | PAQ_L.xpt     | Duration of vigorous leisure-time activity per session (minutes)                      | float64 |      3687 |        4466 |         54.78 |      1   |   9999   |
| PAD680     | PAQ_L.xpt     | Minutes of sedentary activity per day                                                 | float64 |      8138 |          15 |          0.18 |      0   |   9999   |
| DIQ010     | DIQ_L.xpt     | Doctor told you have diabetes (1=Yes, 2=No, 3=Borderline, 7=Refused, 9=DK)            | float64 |     11740 |           4 |          0.03 |    nan   |    nan   |
| DIQ160     | DIQ_L.xpt     | Ever told you have prediabetes / borderline diabetes (1=Yes, 2=No, 7=Refused, 9=DK)   | float64 |      8022 |        3722 |         31.69 |    nan   |    nan   |
| DIQ180     | DIQ_L.xpt     | Had blood tested past three years (1=Yes, 2=No, 7=Refused, 9=DK)                      | float64 |      8304 |        3440 |         29.29 |    nan   |    nan   |
| LBXGH      | GHB_L.xpt     | Glycohemoglobin / HbA1c (%)                                                           | float64 |      6715 |         484 |          6.72 |      3.2 |     17.1 |
| WTPH2YR    | GHB_L.xpt     | 2-year phlebotomy exam weight (blood analytes subsample weight)                       | float64 |      7199 |           0 |          0    |      0   | 241700   |
| LBXGLU     | GLU_L.xpt     | Fasting glucose (mg/dL)                                                               | float64 |      3672 |         324 |          8.11 |     59   |    561   |
| WTSAF2YR   | GLU_L.xpt     | Fasting subsample 2-year MEC weight                                                   | float64 |      3996 |           0 |          0    |      0   | 561900   |


### Physical Activity Questionnaire (PAQ_L) Official Definitions
- **`PAD790Q`**: Frequency of moderate leisure-time physical activity (number of days)
- **`PAD790U`**: Frequency unit for moderate leisure-time activity (D=Day, W=Week, M=Month, Y=Year)
- **`PAD800`**: Duration of moderate leisure-time activity per session (minutes)
- **`PAD810Q`**: Frequency of vigorous leisure-time physical activity (number of days)
- **`PAD810U`**: Frequency unit for vigorous leisure-time activity (D=Day, W=Week, M=Month, Y=Year)
- **`PAD820`**: Duration of vigorous leisure-time activity per session (minutes)
- **`PAD680`**: Minutes of sedentary activity per day

## 4. Merge Coverage & Attrition

All component files were LEFT-joined onto `DEMO_L` by `SEQN`. The full baseline size is 11,933 participants.

| step          |     n |   lost |   pct_of_base |
|:--------------|------:|-------:|--------------:|
| Base (DEMO_L) | 11933 |      0 |           100 |
| + BMX_L.xpt   | 11933 |      0 |           100 |
| + BPQ_L.xpt   | 11933 |      0 |           100 |
| + SMQ_L.xpt   | 11933 |      0 |           100 |
| + PAQ_L.xpt   | 11933 |      0 |           100 |
| + DIQ_L.xpt   | 11933 |      0 |           100 |
| + GHB_L.xpt   | 11933 |      0 |           100 |
| + GLU_L.xpt   | 11933 |      0 |           100 |


## 5. Cohort Definitions

| Cohort | Definition | Total N |
|--------|------------|--------:|
| **A_all** | All NHANES 2021–2023 participants | 11,933 |
| **B_adult** | Adults age ≥ 18 | 8,153 |
| **C_no_diab** | Adults age ≥ 18, excluding self-reported known diabetes (`DIQ010 == 1`) | 7,080 |
| **D_no_diab_no_prediab** | Adults age ≥ 18, excluding known diabetes (`DIQ010 == 1`) and borderline (`DIQ010 == 3`) | 6,808 |
| **E_no_known_dysglycemia** | Adults age ≥ 18 with `DIQ010 == 2` (No diabetes) AND `DIQ160 == 2` (No prediabetes) | 5,907 |

### Cohort E (True No Known Dysglycemia) Exclusion Breakdown

| step                                                         |   count |   pct_of_adults | description                                                    |
|:-------------------------------------------------------------|--------:|----------------:|:---------------------------------------------------------------|
| Adults Base (Age >= 18)                                      |    8153 |          100    | All adult participants                                         |
| Excluded: Known diabetes (DIQ010=1)                          |    1073 |           13.16 | Doctor told you have diabetes                                  |
| Excluded: Borderline diabetes (DIQ010=3)                     |     272 |            3.34 | Doctor told you have borderline diabetes                       |
| Excluded: Known prediabetes (DIQ160=1)                       |     884 |           10.84 | Told you have prediabetes among DIQ010=2                       |
| Excluded: Missing / Refused / Don't Know on DIQ010 or DIQ160 |      17 |            0.21 | DIQ010 missing/DK=5, DIQ160 missing/DK=12                      |
| Cohort E: No Known Dysglycemia (DIQ010=2 & DIQ160=2)         |    5907 |           72.45 | True screening population without prior recognized dysglycemia |


### Cohort Characteristics Summary

| cohort                 |   total_n | age_distribution                     | sex_distribution                     |   available_bmi |   available_waist |   available_hypertension_bpq020 |   available_smoking_smq020 |   available_phys_activity_pad680 |   available_hba1c |   available_fasting_glucose |
|:-----------------------|----------:|:-------------------------------------|:-------------------------------------|----------------:|------------------:|--------------------------------:|---------------------------:|---------------------------------:|------------------:|----------------------------:|
| A_all                  |     11933 | mean=38.3, median=37, min=0, max=80  | Male=5575(46.7%), Female=6358(53.3%) |            8471 |              8190 |                            8487 |                       8121 |                             8138 |              6715 |                        3361 |
| B_adult                |      8153 | mean=52.1, median=55, min=18, max=80 | Male=3657(44.9%), Female=4496(55.1%) |            6235 |              6019 |                            8139 |                       8121 |                             8138 |              6002 |                        3063 |
| C_no_diab              |      7080 | mean=50.4, median=52, min=18, max=80 | Male=3139(44.3%), Female=3941(55.7%) |            5390 |              5223 |                            7068 |                       7051 |                             7066 |              5182 |                        2654 |
| D_no_diab_no_prediab   |      6808 | mean=50.0, median=51, min=18, max=80 | Male=3018(44.3%), Female=3790(55.7%) |            5170 |              5012 |                            6796 |                       6779 |                             6794 |              4967 |                        2542 |
| E_no_known_dysglycemia |      5907 | mean=48.7, median=48, min=18, max=80 | Male=2654(44.9%), Female=3253(55.1%) |            4451 |              4315 |                            5898 |                       5883 |                             5898 |              4260 |                        2167 |


## 6. Stage-1 Feature Completeness

- **Core candidate set:** Age (`RIDAGEYR`), Sex (`RIAGENDR`), BMI (`BMXBMI`), Hypertension history (`BPQ020`), Smoking history (`SMQ020`)
- **Expanded candidate set:** Core set + Waist circumference (`BMXWAIST`) + Sedentary minutes (`PAD680`)

| cohort                 |   total_n |   valid_RIDAGEYR |   valid_RIAGENDR |   valid_BMXBMI |   valid_BPQ020_clean |   valid_SMQ020_clean |   valid_BMXWAIST |   valid_PAD680 |   core_complete |   core_complete_pct |   expanded_complete |   expanded_complete_pct | largest_reduction_feature   |   largest_reduction_missing_n |
|:-----------------------|----------:|-----------------:|-----------------:|---------------:|---------------------:|---------------------:|-----------------:|---------------:|----------------:|--------------------:|--------------------:|------------------------:|:----------------------------|------------------------------:|
| A_all                  |     11933 |            11933 |            11933 |           8471 |                 8487 |                 8121 |             8190 |           8138 |            6222 |               52.14 |                5985 |                   50.16 | SMQ020_clean                |                          3812 |
| B_adult                |      8153 |             8153 |             8153 |           6235 |                 8139 |                 8121 |             6019 |           8138 |            6222 |               76.32 |                5985 |                   73.41 | BMXWAIST                    |                          2134 |
| C_no_diab              |      7080 |             7080 |             7080 |           5390 |                 7068 |                 7051 |             5223 |           7066 |            5379 |               75.97 |                5197 |                   73.4  | BMXWAIST                    |                          1857 |
| D_no_diab_no_prediab   |      6808 |             6808 |             6808 |           5170 |                 6796 |                 6779 |             5012 |           6794 |            5159 |               75.78 |                4986 |                   73.24 | BMXWAIST                    |                          1796 |
| E_no_known_dysglycemia |      5907 |             5907 |             5907 |           4451 |                 5898 |                 5883 |             4315 |           5898 |            4441 |               75.18 |                4295 |                   72.71 | BMXWAIST                    |                          1592 |


**Key observation:** Across all adult screening cohorts (B, C, D, E), the largest sample reduction factor for the expanded feature set is physical exam waist circumference (`BMXWAIST`), followed by BMI (`BMXBMI`), due to exam non-participation among interviewed individuals.

## 7. Laboratory Coverage (Analytically Valid Labs)

In accordance with CDC/NCHS analytic guidelines:
- **HbA1c** is considered valid when `LBXGH` is non-missing and phlebotomy weight `WTPH2YR > 0` ($N = 6,715$ overall).
- **Fasting Glucose (FPG)** is considered analytically valid ONLY when `LBXGLU` is non-missing AND fasting subsample weight `WTSAF2YR > 0` ($N = 3,361$ overall). An additional 311 records with `WTSAF2YR == 0` are excluded from valid fasting analyses.

| cohort                 |   total_n |   valid_hba1c |   valid_fpg_analytically_valid |   valid_both_labs |   core_plus_hba1c |   core_plus_fpg |   core_plus_both_labs |   expanded_plus_hba1c |   expanded_plus_fpg |   expanded_plus_both_labs |
|:-----------------------|----------:|--------------:|-------------------------------:|------------------:|------------------:|----------------:|----------------------:|----------------------:|--------------------:|--------------------------:|
| A_all                  |     11933 |          6715 |                           3361 |              3359 |              5902 |            3020 |                  3018 |                  5692 |                2919 |                      2917 |
| B_adult                |      8153 |          6002 |                           3063 |              3061 |              5902 |            3020 |                  3018 |                  5692 |                2919 |                      2917 |
| C_no_diab              |      7080 |          5182 |                           2654 |              2652 |              5105 |            2624 |                  2622 |                  4944 |                2546 |                      2544 |
| D_no_diab_no_prediab   |      6808 |          4967 |                           2542 |              2540 |              4893 |            2513 |                  2511 |                  4739 |                2437 |                      2435 |
| E_no_known_dysglycemia |      5907 |          4260 |                           2167 |              2165 |              4194 |            2141 |                  2139 |                  4066 |                2079 |                      2077 |


## 8. HbA1c Provisional Outcome Distributions

Provisional clinical ranges (feasibility labels only, not clinical diagnoses):
- Normal: `< 5.7%`
- Prediabetes range: `5.7% – < 6.5%`
- Diabetes range: `≥ 6.5%`

| cohort                 |   total_n |   valid_n |   missing_n |   hba1c_normal |   hba1c_prediabetes_range |   hba1c_diabetes_range |   pct_normal |   pct_prediab |   pct_diab |   dysglycemia_total |   pct_dysglycemia |
|:-----------------------|----------:|----------:|------------:|---------------:|--------------------------:|-----------------------:|-------------:|--------------:|-----------:|--------------------:|------------------:|
| A_all                  |     11933 |      6715 |        5218 |           4354 |                      1640 |                    721 |        64.84 |         24.42 |      10.74 |                2361 |             35.16 |
| B_adult                |      8153 |      6002 |        2151 |           3691 |                      1590 |                    721 |        61.5  |         26.49 |      12.01 |                2311 |             38.5  |
| C_no_diab              |      7080 |      5182 |        1898 |           3626 |                      1404 |                    152 |        69.97 |         27.09 |       2.93 |                1556 |             30.03 |
| D_no_diab_no_prediab   |      6808 |      4967 |        1841 |           3565 |                      1286 |                    116 |        71.77 |         25.89 |       2.34 |                1402 |             28.23 |
| E_no_known_dysglycemia |      5907 |      4260 |        1647 |           3277 |                       916 |                     67 |        76.92 |         21.5  |       1.57 |                 983 |             23.08 |


## 9. Fasting Glucose Provisional Outcome Distributions (Analytically Valid)

Provisional clinical ranges (fasting subsample only, `WTSAF2YR > 0`):
- Normal: `< 100 mg/dL`
- Prediabetes range: `100 – < 126 mg/dL`
- Diabetes range: `≥ 126 mg/dL`

| cohort                 |   total_n |   valid_n |   missing_n |   fpg_normal |   fpg_prediabetes_range |   fpg_diabetes_range |   pct_normal |   pct_prediab |   pct_diab |   dysglycemia_total |   pct_dysglycemia |
|:-----------------------|----------:|----------:|------------:|-------------:|------------------------:|---------------------:|-------------:|--------------:|-----------:|--------------------:|------------------:|
| A_all                  |     11933 |      3361 |        8572 |         1604 |                    1373 |                  384 |        47.72 |         40.85 |      11.43 |                1757 |             52.28 |
| B_adult                |      8153 |      3063 |        5090 |         1369 |                    1311 |                  383 |        44.69 |         42.8  |      12.5  |                1694 |             55.31 |
| C_no_diab              |      7080 |      2654 |        4426 |         1340 |                    1188 |                  126 |        50.49 |         44.76 |       4.75 |                1314 |             49.51 |
| D_no_diab_no_prediab   |      6808 |      2542 |        4266 |         1321 |                    1124 |                   97 |        51.97 |         44.22 |       3.82 |                1221 |             48.03 |
| E_no_known_dysglycemia |      5907 |      2167 |        3740 |         1211 |                     902 |                   54 |        55.88 |         41.62 |       2.49 |                 956 |             44.12 |


## 10. HbA1c vs Fasting Glucose Concordance

Among participants with both analytically valid HbA1c (`LBXGH.notna() & WTPH2YR > 0`) and fasting glucose (`LBXGLU.notna() & WTSAF2YR > 0`) ($N = 3,359$):

|   participants_with_both_valid_labs |   exact_agreement_n |   exact_agreement_pct |   disagreement_n |   disagreement_pct |   hba1c_more_severe_n |   hba1c_more_severe_pct |   fpg_more_severe_n |   fpg_more_severe_pct |
|------------------------------------:|--------------------:|----------------------:|-----------------:|-------------------:|----------------------:|------------------------:|--------------------:|----------------------:|
|                                3359 |                2126 |                 63.29 |             1233 |              36.71 |                   325 |                    9.68 |                 908 |                 27.03 |


### Cross-Tabulation (HbA1c rows × Fasting Glucose columns)

| HbA1c \ FPG | Normal (<100) | Prediabetes (100–125) | Diabetes (≥126) | Total |
|:---|---:|---:|---:|---:|
| **Normal (<5.7%)** | 1,347 | 808 | 16 | 2,171 |
| **Prediabetes (5.7–6.4%)** | 238 | 495 | 84 | 817 |
| **Diabetes (≥6.5%)** | 18 | 69 | 284 | 371 |
| **Total** | 1,603 | 1,372 | 384 | 3,359 |

- **Exact 3-class agreement:** 2,126 / 3,359 (**63.29%**)
- **Disagreement:** 1,233 / 3,359 (**36.71%**)
- **FPG more severe than HbA1c:** 908 / 3,359 (**27.03%**)
- **HbA1c more severe than FPG:** 325 / 3,359 (**9.68%**)

## 11. Known Diabetes / Dysglycemia vs Laboratory Status

| group                                      |   total_n |   hba1c_valid |   hba1c_normal |   hba1c_prediab_range |   hba1c_diab_range |   hba1c_missing |   fpg_valid |   fpg_normal |   fpg_prediab_range |   fpg_diab_range |   fpg_missing |
|:-------------------------------------------|----------:|--------------:|---------------:|----------------------:|-------------------:|----------------:|------------:|-------------:|--------------------:|-----------------:|--------------:|
| known_diabetes (DIQ010=1)                  |      1073 |           820 |             65 |                   186 |                569 |             253 |         409 |           29 |                 123 |              257 |           664 |
| no_known_diabetes (DIQ010!=1)              |      7080 |          5182 |           3626 |                  1404 |                152 |            1898 |        2654 |         1340 |                1188 |              126 |          4426 |
| no_known_dysglycemia (DIQ010=2 & DIQ160=2) |      5907 |          4260 |           3277 |                   916 |                 67 |            1647 |        2167 |         1211 |                 902 |               54 |          3740 |


**Terminology Note:** Participants without self-reported known dysglycemia who have lab values in the diabetes range are described strictly as *'participants without self-reported known diabetes/dysglycemia who have a laboratory measurement in the diabetes range'*. No clinical diagnoses are made.

## 12. Class Balance Summary

| cohort                                 | target       |   total_n |   valid_n |   missing_outcome |   n_diabetes_range |   n_dysglycemia_range |   n_normal |   n_prediabetes_range |   pct_diabetes_range |   pct_dysglycemia_range |   pct_normal |   pct_prediabetes_range |
|:---------------------------------------|:-------------|----------:|----------:|------------------:|-------------------:|----------------------:|-----------:|----------------------:|---------------------:|------------------------:|-------------:|------------------------:|
| adults_ge18                            | hba1c_binary |      8153 |      6002 |              2151 |                nan |                  2311 |       3691 |                   nan |               nan    |                   38.5  |        61.5  |                  nan    |
| adults_ge18                            | fpg_binary   |      8153 |      3063 |              5090 |                nan |                  1694 |       1369 |                   nan |               nan    |                   55.31 |        44.69 |                  nan    |
| adults_ge18                            | hba1c_cat3   |      8153 |      6002 |              2151 |                721 |                   nan |       3691 |                  1590 |                12.01 |                  nan    |        61.5  |                   26.49 |
| adults_ge18                            | fpg_cat3     |      8153 |      3063 |              5090 |                383 |                   nan |       1369 |                  1311 |                12.5  |                  nan    |        44.69 |                   42.8  |
| adults_no_known_diab                   | hba1c_binary |      7080 |      5182 |              1898 |                nan |                  1556 |       3626 |                   nan |               nan    |                   30.03 |        69.97 |                  nan    |
| adults_no_known_diab                   | fpg_binary   |      7080 |      2654 |              4426 |                nan |                  1314 |       1340 |                   nan |               nan    |                   49.51 |        50.49 |                  nan    |
| adults_no_known_diab                   | hba1c_cat3   |      7080 |      5182 |              1898 |                152 |                   nan |       3626 |                  1404 |                 2.93 |                  nan    |        69.97 |                   27.09 |
| adults_no_known_diab                   | fpg_cat3     |      7080 |      2654 |              4426 |                126 |                   nan |       1340 |                  1188 |                 4.75 |                  nan    |        50.49 |                   44.76 |
| adults_no_known_diab_core_complete     | hba1c_binary |      5379 |      5105 |               274 |                nan |                  1537 |       3568 |                   nan |               nan    |                   30.11 |        69.89 |                  nan    |
| adults_no_known_diab_core_complete     | fpg_binary   |      5379 |      2624 |              2755 |                nan |                  1296 |       1328 |                   nan |               nan    |                   49.39 |        50.61 |                  nan    |
| adults_no_known_diab_core_complete     | hba1c_cat3   |      5379 |      5105 |               274 |                150 |                   nan |       3568 |                  1387 |                 2.94 |                  nan    |        69.89 |                   27.17 |
| adults_no_known_diab_core_complete     | fpg_cat3     |      5379 |      2624 |              2755 |                125 |                   nan |       1328 |                  1171 |                 4.76 |                  nan    |        50.61 |                   44.63 |
| adults_no_known_diab_expanded_complete | hba1c_binary |      5197 |      4944 |               253 |                nan |                  1491 |       3453 |                   nan |               nan    |                   30.16 |        69.84 |                  nan    |
| adults_no_known_diab_expanded_complete | fpg_binary   |      5197 |      2546 |              2651 |                nan |                  1264 |       1282 |                   nan |               nan    |                   49.65 |        50.35 |                  nan    |
| adults_no_known_diab_expanded_complete | hba1c_cat3   |      5197 |      4944 |               253 |                144 |                   nan |       3453 |                  1347 |                 2.91 |                  nan    |        69.84 |                   27.25 |
| adults_no_known_diab_expanded_complete | fpg_cat3     |      5197 |      2546 |              2651 |                118 |                   nan |       1282 |                  1146 |                 4.63 |                  nan    |        50.35 |                   45.01 |
| cohort_e_no_known_dysglycemia          | hba1c_binary |      5907 |      4260 |              1647 |                nan |                   983 |       3277 |                   nan |               nan    |                   23.08 |        76.92 |                  nan    |
| cohort_e_no_known_dysglycemia          | fpg_binary   |      5907 |      2167 |              3740 |                nan |                   956 |       1211 |                   nan |               nan    |                   44.12 |        55.88 |                  nan    |
| cohort_e_no_known_dysglycemia          | hba1c_cat3   |      5907 |      4260 |              1647 |                 67 |                   nan |       3277 |                   916 |                 1.57 |                  nan    |        76.92 |                   21.5  |
| cohort_e_no_known_dysglycemia          | fpg_cat3     |      5907 |      2167 |              3740 |                 54 |                   nan |       1211 |                   902 |                 2.49 |                  nan    |        55.88 |                   41.62 |
| cohort_e_core_complete                 | hba1c_binary |      4441 |      4194 |               247 |                nan |                   970 |       3224 |                   nan |               nan    |                   23.13 |        76.87 |                  nan    |
| cohort_e_core_complete                 | fpg_binary   |      4441 |      2141 |              2300 |                nan |                   942 |       1199 |                   nan |               nan    |                   44    |        56    |                  nan    |
| cohort_e_core_complete                 | hba1c_cat3   |      4441 |      4194 |               247 |                 66 |                   nan |       3224 |                   904 |                 1.57 |                  nan    |        76.87 |                   21.55 |
| cohort_e_core_complete                 | fpg_cat3     |      4441 |      2141 |              2300 |                 54 |                   nan |       1199 |                   888 |                 2.52 |                  nan    |        56    |                   41.48 |
| cohort_e_expanded_complete             | hba1c_binary |      4295 |      4066 |               229 |                nan |                   946 |       3120 |                   nan |               nan    |                   23.27 |        76.73 |                  nan    |
| cohort_e_expanded_complete             | fpg_binary   |      4295 |      2079 |              2216 |                nan |                   919 |       1160 |                   nan |               nan    |                   44.2  |        55.8  |                  nan    |
| cohort_e_expanded_complete             | hba1c_cat3   |      4295 |      4066 |               229 |                 66 |                   nan |       3120 |                   880 |                 1.62 |                  nan    |        76.73 |                   21.64 |
| cohort_e_expanded_complete             | fpg_cat3     |      4295 |      2079 |              2216 |                 51 |                   nan |       1160 |                   868 |                 2.45 |                  nan    |        55.8  |                   41.75 |


## 13. Survey Design & Weighting Considerations

### Weight Reconciliations against Official CDC Codebooks
- **`WTINT2YR`** (Interview weight): 11,933 positive weights, 0 zero weights.
- **`WTMEC2YR`** (MEC exam weight): 8,860 positive weights, 3,073 zero weights (interview-only non-examined participants).
- **`WTPH2YR`** (Phlebotomy weight): 6,750 positive weights, 449 zero weights in `GHB_L.xpt`.
- **`WTSAF2YR`** (Fasting subsample weight): 3,361 positive weights, 635 zero weights in `GLU_L.xpt` (reconciled exactly with CDC codebook).

### Analysis Weight Usage Rules
| Outcome / Measure | Required Survey Weight | Subsample |
|:---|:---|:---|
| Demographics / Questionnaire only | `WTINT2YR` | Full sample ($N = 11,933$) |
| Physical Exam (BMI, Waist, BP) | `WTMEC2YR` | MEC Exam ($N = 8,860$) |
| Glycohemoglobin (HbA1c) / Blood Analytes | `WTPH2YR` | Phlebotomy Exam ($N = 6,750$) |
| Fasting Plasma Glucose (FPG) | `WTSAF2YR` | Fasting Subsample ($N = 3,361$) |

**Current Status:** All counts in this report are unweighted sample counts. Population-representative estimations require incorporating weights, strata (`SDMVSTRA`), and PSUs (`SDMVPSU`).

## 14. Data Quality Observations

### Missingness Summary

| variable   |   total |   missing |   missing_pct |
|:-----------|--------:|----------:|--------------:|
| RIDAGEYR   |   11933 |         0 |          0    |
| RIAGENDR   |   11933 |         0 |          0    |
| WTINT2YR   |   11933 |         0 |          0    |
| WTMEC2YR   |   11933 |         0 |          0    |
| WTPH2YR    |   11933 |      4734 |         39.67 |
| WTSAF2YR   |   11933 |      7937 |         66.51 |
| SDMVSTRA   |   11933 |         0 |          0    |
| SDMVPSU    |   11933 |         0 |          0    |
| BMXBMI     |   11933 |      3462 |         29.01 |
| BMXWAIST   |   11933 |      3743 |         31.37 |
| BPQ020     |   11933 |      3435 |         28.79 |
| BPQ150     |   11933 |      8964 |         75.12 |
| SMQ020     |   11933 |      3798 |         31.83 |
| SMQ040     |   11933 |      8690 |         72.82 |
| PAD790Q    |   11933 |      3798 |         31.83 |
| PAD800     |   11933 |      5543 |         46.45 |
| PAD810Q    |   11933 |      3794 |         31.79 |
| PAD820     |   11933 |      8246 |         69.1  |
| PAD680     |   11933 |      3795 |         31.8  |
| DIQ010     |   11933 |       193 |          1.62 |
| DIQ160     |   11933 |      3911 |         32.77 |
| DIQ180     |   11933 |      3629 |         30.41 |
| LBXGH      |   11933 |      5218 |         43.73 |
| LBXGLU     |   11933 |      8261 |         69.23 |


### Quality Checks and Codebook Notes

| issue_type             | variable   | detail                                                                                                             | severity   |
|:-----------------------|:-----------|:-------------------------------------------------------------------------------------------------------------------|:-----------|
| high_missingness       | WTPH2YR    | 39.7% missing (4734/11933)                                                                                         | moderate   |
| high_missingness       | WTSAF2YR   | 66.5% missing (7937/11933)                                                                                         | high       |
| high_missingness       | BMXBMI     | 29.0% missing (3462/11933)                                                                                         | moderate   |
| high_missingness       | BMXWAIST   | 31.4% missing (3743/11933)                                                                                         | moderate   |
| high_missingness       | BPQ020     | 28.8% missing (3435/11933)                                                                                         | moderate   |
| high_missingness       | BPQ150     | 75.1% missing (8964/11933)                                                                                         | high       |
| high_missingness       | SMQ020     | 31.8% missing (3798/11933)                                                                                         | moderate   |
| high_missingness       | SMQ040     | 72.8% missing (8690/11933)                                                                                         | high       |
| high_missingness       | PAD790Q    | 31.8% missing (3798/11933)                                                                                         | moderate   |
| high_missingness       | PAD800     | 46.5% missing (5543/11933)                                                                                         | moderate   |
| high_missingness       | PAD810Q    | 31.8% missing (3794/11933)                                                                                         | moderate   |
| high_missingness       | PAD820     | 69.1% missing (8246/11933)                                                                                         | high       |
| high_missingness       | PAD680     | 31.8% missing (3795/11933)                                                                                         | moderate   |
| high_missingness       | DIQ160     | 32.8% missing (3911/11933)                                                                                         | moderate   |
| high_missingness       | DIQ180     | 30.4% missing (3629/11933)                                                                                         | moderate   |
| high_missingness       | LBXGH      | 43.7% missing (5218/11933)                                                                                         | moderate   |
| high_missingness       | LBXGLU     | 69.2% missing (8261/11933)                                                                                         | high       |
| special_missing_code   | BPQ020     | Code 7 appears 1 times (refused/don't know)                                                                        | info       |
| special_missing_code   | BPQ020     | Code 9 appears 10 times (refused/don't know)                                                                       | info       |
| special_missing_code   | SMQ020     | Code 7 appears 7 times (refused/don't know)                                                                        | info       |
| special_missing_code   | SMQ020     | Code 9 appears 7 times (refused/don't know)                                                                        | info       |
| special_missing_code   | DIQ010     | Code 9 appears 4 times (refused/don't know)                                                                        | info       |
| special_missing_code   | DIQ160     | Code 9 appears 15 times (refused/don't know)                                                                       | info       |
| subsample_zero_weights | WTMEC2YR   | MEC exam weight (WTMEC2YR) has 8860 positive weights and 3073 zero weights (unweighted subsample non-participants) | info       |
| subsample_zero_weights | WTPH2YR    | Phlebotomy weight (WTPH2YR) has 6750 positive weights and 449 zero weights (unweighted subsample non-participants) | info       |
| subsample_zero_weights | WTSAF2YR   | Fasting weight (WTSAF2YR) has 3361 positive weights and 635 zero weights (unweighted subsample non-participants)   | info       |


## 15. Factual Findings — No Recommendation

This section summarizes the verified numerical findings from the feasibility audit.
**No recommendations are made regarding research design, model architecture, target selection, or thesis direction.**

### 1. Cohort Sample Availability
1. **Full NHANES 2021–2023:** 11,933 participants (8,153 adults age ≥ 18).
2. **Adults without known diabetes (Cohort C):** 7,080 participants.
3. **True 'no known dysglycemia' screening population (Cohort E, `DIQ010==2 & DIQ160==2`):** 5,907 participants.
4. Exclusions from all adults to Cohort E comprise: 1,073 with known diabetes, 272 with borderline diabetes, 884 with known prediabetes, and 17 with missing/DK responses.

### 2. Stage-1 Feature Availability
5. In Cohort E ($N = 5,907$), complete core Stage-1 predictors (age, sex, BMI, hypertension history, smoking history) are available for **$N = 4,441$ participants (75.18%)**.
6. In Cohort E, complete expanded candidate predictors (core + waist circumference + sedentary activity) are available for **$N = 4,295$ participants (72.71%)**.
7. The primary driver of sample reduction is physical examination non-attendance (missing waist circumference / BMI).

### 3. Stage-2 Laboratory Availability
8. In Cohort E, valid HbA1c is available for **$N = 4,260$ participants** ($N = 4,194$ when combined with complete core Stage-1 predictors).
9. In Cohort E, analytically valid fasting glucose (`WTSAF2YR > 0`) is available for **$N = 2,167$ participants** ($N = 2,141$ when combined with complete core Stage-1 predictors).
10. Both analytically valid laboratory outcomes are available for **$N = 2,139$ participants** in Cohort E with complete core Stage-1 predictors.

### 4. Laboratory Distributions in Screened Population (Cohort E)
11. Among Cohort E participants with valid HbA1c ($N = 4,260$):
    - Normal (< 5.7%): 3,277 (76.92%)
    - Prediabetes range (5.7–6.4%): 916 (21.50%)
    - Diabetes range (≥ 6.5%): 67 (1.57%)
    - Total dysglycemia-range: 983 (23.08%)
12. Among Cohort E participants with analytically valid FPG ($N = 2,167$):
    - Normal (< 100 mg/dL): 1,211 (55.88%)
    - Prediabetes range (100–125 mg/dL): 902 (41.62%)
    - Diabetes range (≥ 126 mg/dL): 54 (2.49%)
    - Total dysglycemia-range: 956 (44.12%)

### 5. Laboratory Concordance
13. Among 3,359 participants with both analytically valid measurements, 3-class concordance is 63.29% (2,126 / 3,359).
14. In discordant pairs, fasting glucose categorizes participants into a higher dysglycemia tier in 27.03% of cases (908 / 3,359), whereas HbA1c categorizes higher in 9.68% of cases (325 / 3,359).

### 6. Survey Weights & Provenance
15. All 8 raw XPT files match official CDC/NCHS SHA256 hashes.
16. Normalized SAS zeroes reconcile exactly with official codebook weight counts (3,361 positive fasting weights in `GLU_L`, 6,750 positive phlebotomy weights in `GHB_L`, 8,860 positive MEC exam weights in `DEMO_L`).

---
*Report generated programmatically from official NHANES August 2021–August 2023 public-use files.*
*All values are unweighted counts from raw-preserved data. No machine-learning model was trained.*