# NHANES August 2021–August 2023 Feasibility Audit Report

**Purpose:** Assess whether NHANES 2021-2023 public-use data can support a
two-stage diabetes screening study using non-laboratory Stage-1 predictors
and laboratory-based Stage-2 reference outcomes.

**This report contains factual findings only. It does not recommend a final
research design, target variable, feature set, or model.**

---

## 1. Data Files and Provenance

All files were downloaded from official CDC/NCHS endpoints:
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


SHA256 hashes were verified against `file_manifest.csv` generated at download time.

## 2. Raw Participant Counts

| source_file   | description                                |   source_n |   matched |   unmatched_in_source |
|:--------------|:-------------------------------------------|-----------:|----------:|----------------------:|
| DEMO_L.xpt    | Demographics (base)                        |      11933 |     11933 |                     0 |
| BMX_L.xpt     | Body Measures                              |       8860 |      8860 |                     0 |
| BPQ_L.xpt     | Blood Pressure / Cholesterol Questionnaire |       8501 |      8501 |                     0 |
| SMQ_L.xpt     | Smoking Questionnaire                      |       9015 |      9015 |                     0 |
| PAQ_L.xpt     | Physical Activity Questionnaire            |       8153 |      8153 |                     0 |
| DIQ_L.xpt     | Diabetes Questionnaire                     |      11744 |     11744 |                     0 |
| GHB_L.xpt     | Glycohemoglobin (HbA1c)                    |       7199 |      7199 |                     0 |
| GLU_L.xpt     | Fasting Glucose                            |       3996 |      3996 |                     0 |


All SEQN values are unique within each component file (zero duplicates).

## 3. Variable Availability

| variable   | source_file   | description                                                                       | dtype   |   valid_n |   missing_n |   missing_pct |            min |      max |
|:-----------|:--------------|:----------------------------------------------------------------------------------|:--------|----------:|------------:|--------------:|---------------:|---------:|
| SEQN       | DEMO_L.xpt    | Respondent sequence number                                                        | float64 |     11933 |           0 |          0    | 130400         | 142300   |
| RIDAGEYR   | DEMO_L.xpt    | Age in years at screening (0-80; 80 = 80+)                                        | float64 |     11933 |           0 |          0    |      5.398e-79 |     80   |
| RIAGENDR   | DEMO_L.xpt    | Gender (1=Male, 2=Female)                                                         | float64 |     11933 |           0 |          0    |    nan         |    nan   |
| WTMEC2YR   | DEMO_L.xpt    | Full sample 2-year MEC exam weight                                                | float64 |     11933 |           0 |          0    |      5.398e-79 | 227100   |
| SDMVSTRA   | DEMO_L.xpt    | Masked variance pseudo-stratum                                                    | float64 |     11933 |           0 |          0    |    173         |    187   |
| SDMVPSU    | DEMO_L.xpt    | Masked variance pseudo-PSU                                                        | float64 |     11933 |           0 |          0    |      1         |      2   |
| BMXBMI     | BMX_L.xpt     | Body mass index (kg/m²)                                                           | float64 |      8471 |         389 |          4.39 |     11.1       |     74.8 |
| BMXWAIST   | BMX_L.xpt     | Waist circumference (cm)                                                          | float64 |      8190 |         670 |          7.56 |     39.8       |    187   |
| BPQ020     | BPQ_L.xpt     | Ever told you had high blood pressure (1=Yes,2=No,7=Refused,9=DK)                 | float64 |      8498 |           3 |          0.04 |    nan         |    nan   |
| BPQ150     | BPQ_L.xpt     | Had blood cholesterol checked in past 5 years (1=Yes,2=No,7=Refused,9=DK)         | float64 |      2969 |        5532 |         65.07 |    nan         |    nan   |
| SMQ020     | SMQ_L.xpt     | Smoked at least 100 cigarettes in life (1=Yes,2=No,7=Refused,9=DK)                | float64 |      8135 |         880 |          9.76 |    nan         |    nan   |
| SMQ040     | SMQ_L.xpt     | Do you now smoke cigarettes (1=Every day,2=Some days,3=Not at all,7=Refused,9=DK) | float64 |      3243 |        5772 |         64.03 |    nan         |    nan   |
| PAD790Q    | PAQ_L.xpt     | Hours/minutes vigorous work activity per day (quantity)                           | float64 |      8135 |          18 |          0.22 |      5.398e-79 |   9999   |
| PAD790U    | PAQ_L.xpt     | Vigorous work activity unit (1=Hours,2=Minutes)                                   | object  |      8153 |           0 |          0    |    nan         |    nan   |
| PAD800     | PAQ_L.xpt     | Walk or bicycle to get places (1=Yes,2=No,7=Refused,9=DK)                         | float64 |      6390 |        1763 |         21.62 |    nan         |    nan   |
| PAD810Q    | PAQ_L.xpt     | Hours/minutes moderate work activity per day (quantity)                           | float64 |      8139 |          14 |          0.17 |      5.398e-79 |   9999   |
| PAD810U    | PAQ_L.xpt     | Moderate work activity unit (1=Hours,2=Minutes)                                   | object  |      8153 |           0 |          0    |    nan         |    nan   |
| PAD820     | PAQ_L.xpt     | Moderate recreational activities (1=Yes,2=No,7=Refused,9=DK)                      | float64 |      3687 |        4466 |         54.78 |    nan         |    nan   |
| PAD680     | PAQ_L.xpt     | Minutes sedentary activity per day                                                | float64 |      8138 |          15 |          0.18 |      5.398e-79 |   9999   |
| DIQ010     | DIQ_L.xpt     | Doctor told you have diabetes (1=Yes,2=No,3=Borderline,7=Refused,9=DK)            | float64 |     11740 |           4 |          0.03 |    nan         |    nan   |
| DIQ160     | DIQ_L.xpt     | Ever told you have prediabetes (1=Yes,2=No,7=Refused,9=DK)                        | float64 |      8022 |        3722 |         31.69 |    nan         |    nan   |
| DIQ180     | DIQ_L.xpt     | Had blood tested past three years (1=Yes,2=No,7=Refused,9=DK)                     | float64 |      8304 |        3440 |         29.29 |    nan         |    nan   |
| LBXGH      | GHB_L.xpt     | Glycohemoglobin / HbA1c (%)                                                       | float64 |      6715 |         484 |          6.72 |      3.2       |     17.1 |
| LBXGLU     | GLU_L.xpt     | Fasting glucose (mg/dL)                                                           | float64 |      3672 |         324 |          8.11 |     59         |    561   |
| WTSAF2YR   | GLU_L.xpt     | Fasting subsample 2-year MEC weight                                               | float64 |      3996 |           0 |          0    |      5.398e-79 | 561900   |


**Note:** Frequency tables for categorical variables and special missing codes
are available in `variable_dictionary.csv`.

## 4. Merge Coverage

All component files were LEFT-joined onto DEMO_L using SEQN.
DEMO_L serves as the base participant table.

| step          | source_file   | description                                |   source_n |   matched |   unmatched_in_source |   unmatched_in_base |   resulting_rows |
|:--------------|:--------------|:-------------------------------------------|-----------:|----------:|----------------------:|--------------------:|-----------------:|
| 0_base_DEMO_L | DEMO_L.xpt    | Demographics (base)                        |      11933 |     11933 |                     0 |                   0 |            11933 |
| 1_merge_BMX_L | BMX_L.xpt     | Body Measures                              |       8860 |      8860 |                     0 |                3073 |            11933 |
| 2_merge_BPQ_L | BPQ_L.xpt     | Blood Pressure / Cholesterol Questionnaire |       8501 |      8501 |                     0 |                3432 |            11933 |
| 3_merge_SMQ_L | SMQ_L.xpt     | Smoking Questionnaire                      |       9015 |      9015 |                     0 |                2918 |            11933 |
| 4_merge_PAQ_L | PAQ_L.xpt     | Physical Activity Questionnaire            |       8153 |      8153 |                     0 |                3780 |            11933 |
| 5_merge_DIQ_L | DIQ_L.xpt     | Diabetes Questionnaire                     |      11744 |     11744 |                     0 |                 189 |            11933 |
| 6_merge_GHB_L | GHB_L.xpt     | Glycohemoglobin (HbA1c)                    |       7199 |      7199 |                     0 |                4734 |            11933 |
| 7_merge_GLU_L | GLU_L.xpt     | Fasting Glucose                            |       3996 |      3996 |                     0 |                7937 |            11933 |


### Attrition Table

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


Since left joins were used, participant count remains constant at the DEMO_L baseline.
Variables from component files become NaN for unmatched participants.

## 5. Cohort Definitions

| Cohort | Definition |
|--------|------------|
| A_all | All NHANES 2021-2023 participants |
| B_adult | Adults age ≥ 18 |
| C_no_diab | Adults age ≥ 18, excluding self-reported known diabetes (DIQ010=1) |
| D_no_diab_no_prediab | Adults age ≥ 18, excluding known diabetes (DIQ010=1) AND borderline/prediabetes (DIQ010=3) |

| cohort               |   total_n | age_distribution                     | sex_distribution                     |   available_bmi |   available_waist |   available_hypertension_bpq020 |   available_smoking_smq020 |   available_phys_activity_pad680 |   available_hba1c |   available_fasting_glucose |
|:---------------------|----------:|:-------------------------------------|:-------------------------------------|----------------:|------------------:|--------------------------------:|---------------------------:|---------------------------------:|------------------:|----------------------------:|
| A_all                |     11933 | mean=38.3, median=37, min=0, max=80  | Male=5575(46.7%), Female=6358(53.3%) |            8471 |              8190 |                            8487 |                       8121 |                             8138 |              6715 |                        3672 |
| B_adult              |      8153 | mean=52.1, median=55, min=18, max=80 | Male=3657(44.9%), Female=4496(55.1%) |            6235 |              6019 |                            8139 |                       8121 |                             8138 |              6002 |                        3329 |
| C_no_diab            |      7080 | mean=50.4, median=52, min=18, max=80 | Male=3139(44.3%), Female=3941(55.7%) |            5390 |              5223 |                            7068 |                       7051 |                             7066 |              5182 |                        2880 |
| D_no_diab_no_prediab |      6808 | mean=50.0, median=51, min=18, max=80 | Male=3018(44.3%), Female=3790(55.7%) |            5170 |              5012 |                            6796 |                       6779 |                             6794 |              4967 |                        2753 |


## 6. Stage-1 Feature Completeness

**Core candidate set:** age, sex, BMI, hypertension history (BPQ020), smoking history (SMQ020)

**Expanded candidate set:** Core + waist circumference (BMXWAIST) + sedentary minutes (PAD680)

| cohort               |   total_n |   valid_RIDAGEYR |   valid_RIAGENDR |   valid_BMXBMI |   valid_BPQ020_clean |   valid_SMQ020_clean |   valid_BMXWAIST |   valid_PAD680 |   core_complete |   core_complete_pct |   expanded_complete |   expanded_complete_pct | largest_reduction_feature   |   largest_reduction_missing_n |
|:---------------------|----------:|-----------------:|-----------------:|---------------:|---------------------:|---------------------:|-----------------:|---------------:|----------------:|--------------------:|--------------------:|------------------------:|:----------------------------|------------------------------:|
| A_all                |     11933 |            11933 |            11933 |           8471 |                 8487 |                 8121 |             8190 |           8138 |            6222 |               52.14 |                5985 |                   50.16 | SMQ020_clean                |                          3812 |
| B_adult              |      8153 |             8153 |             8153 |           6235 |                 8139 |                 8121 |             6019 |           8138 |            6222 |               76.32 |                5985 |                   73.41 | BMXWAIST                    |                          2134 |
| C_no_diab            |      7080 |             7080 |             7080 |           5390 |                 7068 |                 7051 |             5223 |           7066 |            5379 |               75.97 |                5197 |                   73.4  | BMXWAIST                    |                          1857 |
| D_no_diab_no_prediab |      6808 |             6808 |             6808 |           5170 |                 6796 |                 6779 |             5012 |           6794 |            5159 |               75.78 |                4986 |                   73.24 | BMXWAIST                    |                          1796 |


## 7. Laboratory Coverage

| cohort               |   total_n |   valid_hba1c |   valid_fpg |   valid_wtsaf2yr_gt0 |   valid_fpg_and_wtsaf |   valid_both_labs |   core_plus_hba1c |   core_plus_fpg |   core_plus_both_labs |   expanded_plus_hba1c |   expanded_plus_fpg |   expanded_plus_both_labs |
|:---------------------|----------:|--------------:|------------:|---------------------:|----------------------:|------------------:|------------------:|----------------:|----------------------:|----------------------:|--------------------:|--------------------------:|
| A_all                |     11933 |          6715 |        3672 |                 3996 |                  3672 |              3670 |              5902 |            3279 |                  3277 |                  5692 |                3159 |                      3157 |
| B_adult              |      8153 |          6002 |        3329 |                 3562 |                  3329 |              3327 |              5902 |            3279 |                  3277 |                  5692 |                3159 |                      3157 |
| C_no_diab            |      7080 |          5182 |        2880 |                 3074 |                  2880 |              2878 |              5105 |            2844 |                  2842 |                  4944 |                2752 |                      2750 |
| D_no_diab_no_prediab |      6808 |          4967 |        2753 |                 2942 |                  2753 |              2751 |              4893 |            2719 |                  2717 |                  4739 |                2630 |                      2628 |


**Note:** Fasting glucose (LBXGLU) is measured only on a subsample of MEC-examined participants.
The fasting subsample weight (WTSAF2YR) must be used for population-representative
analyses involving fasting glucose.

## 8. HbA1c Provisional Outcome Distributions

Provisional categories based on standard clinical thresholds (feasibility labels only):

| Category | HbA1c Range |
|----------|-------------|
| Normal | < 5.7% |
| Prediabetes range | 5.7% – < 6.5% |
| Diabetes range | ≥ 6.5% |

| cohort               |   total_n |   hba1c_normal |   hba1c_prediabetes_range |   hba1c_diabetes_range |   hba1c_missing |   pct_normal |   pct_prediab |   pct_diab |
|:---------------------|----------:|---------------:|--------------------------:|-----------------------:|----------------:|-------------:|--------------:|-----------:|
| A_all                |     11933 |           4354 |                      1640 |                    721 |            5218 |        64.84 |         24.42 |      10.74 |
| B_adult              |      8153 |           3691 |                      1590 |                    721 |            2151 |        61.5  |         26.49 |      12.01 |
| C_no_diab            |      7080 |           3626 |                      1404 |                    152 |            1898 |        69.97 |         27.09 |       2.93 |
| D_no_diab_no_prediab |      6808 |           3565 |                      1286 |                    116 |            1841 |        71.77 |         25.89 |       2.34 |


## 9. Fasting Glucose Provisional Outcome Distributions

| Category | FPG Range |
|----------|-----------|
| Normal | < 100 mg/dL |
| Prediabetes range | 100 – < 126 mg/dL |
| Diabetes range | ≥ 126 mg/dL |

| cohort               |   total_n |   fpg_normal |   fpg_prediabetes_range |   fpg_diabetes_range |   fpg_missing |   pct_normal |   pct_prediab |   pct_diab |
|:---------------------|----------:|-------------:|------------------------:|---------------------:|--------------:|-------------:|--------------:|-----------:|
| A_all                |     11933 |         1766 |                    1476 |                  430 |          8261 |        48.09 |         40.2  |      11.71 |
| B_adult              |      8153 |         1499 |                    1401 |                  429 |          4824 |        45.03 |         42.08 |      12.89 |
| C_no_diab            |      7080 |         1467 |                    1269 |                  144 |          4200 |        50.94 |         44.06 |       5    |
| D_no_diab_no_prediab |      6808 |         1440 |                    1201 |                  112 |          4055 |        52.31 |         43.63 |       4.07 |


## 10. HbA1c vs Fasting Glucose Agreement

For participants with both valid HbA1c and fasting glucose measurements:

|   participants_with_both |   exact_agreement_n |   exact_agreement_pct |   disagreement_n |   disagreement_pct |   hba1c_more_severe |   fpg_more_severe |
|-------------------------:|--------------------:|----------------------:|-----------------:|-------------------:|--------------------:|------------------:|
|                     3670 |                2321 |                 63.24 |             1349 |              36.76 |                 369 |               980 |


**Interpretation:** Discordant cases are expected and well-documented in the
clinical literature. HbA1c and fasting glucose measure different aspects of
glucose metabolism and have known imperfect concordance.

## 11. Known Diabetes vs Laboratory Status

Participants are divided by self-reported diabetes status (DIQ010).

| group             |   total_n |   hba1c_valid |   hba1c_normal |   hba1c_prediab_range |   hba1c_diab_range |   hba1c_missing |   fpg_valid |   fpg_normal |   fpg_prediab_range |   fpg_diab_range |   fpg_missing |
|:------------------|----------:|--------------:|---------------:|----------------------:|-------------------:|----------------:|------------:|-------------:|--------------------:|-----------------:|--------------:|
| known_diabetes    |      1073 |           820 |             65 |                   186 |                569 |             253 |         449 |           32 |                 132 |              285 |           624 |
| no_known_diabetes |      7080 |          5182 |           3626 |                  1404 |                152 |            1898 |        2880 |         1467 |                1269 |              144 |          4200 |


**Terminology note:** Participants without self-reported known diabetes who have
a laboratory measurement in the diabetes range are described as such. This report
does NOT claim these participants have undiagnosed diabetes — only that their
laboratory values fall within the diabetes range according to standard thresholds.

## 12. Class Balance

Potential Stage-1 reference targets across cohort definitions:

| cohort                                 | target       |   total_n |   valid_n |   missing_outcome |   n_diabetes_range |   n_dysglycemia_range |   n_normal |   n_prediabetes_range |   pct_diabetes_range |   pct_dysglycemia_range |   pct_normal |   pct_prediabetes_range |
|:---------------------------------------|:-------------|----------:|----------:|------------------:|-------------------:|----------------------:|-----------:|----------------------:|---------------------:|------------------------:|-------------:|------------------------:|
| adults_ge18                            | hba1c_binary |      8153 |      6002 |              2151 |                nan |                  2311 |       3691 |                   nan |               nan    |                   38.5  |        61.5  |                  nan    |
| adults_ge18                            | fpg_binary   |      8153 |      3329 |              4824 |                nan |                  1830 |       1499 |                   nan |               nan    |                   54.97 |        45.03 |                  nan    |
| adults_ge18                            | hba1c_cat3   |      8153 |      6002 |              2151 |                721 |                   nan |       3691 |                  1590 |                12.01 |                  nan    |        61.5  |                   26.49 |
| adults_ge18                            | fpg_cat3     |      8153 |      3329 |              4824 |                429 |                   nan |       1499 |                  1401 |                12.89 |                  nan    |        45.03 |                   42.08 |
| adults_no_known_diab                   | hba1c_binary |      7080 |      5182 |              1898 |                nan |                  1556 |       3626 |                   nan |               nan    |                   30.03 |        69.97 |                  nan    |
| adults_no_known_diab                   | fpg_binary   |      7080 |      2880 |              4200 |                nan |                  1413 |       1467 |                   nan |               nan    |                   49.06 |        50.94 |                  nan    |
| adults_no_known_diab                   | hba1c_cat3   |      7080 |      5182 |              1898 |                152 |                   nan |       3626 |                  1404 |                 2.93 |                  nan    |        69.97 |                   27.09 |
| adults_no_known_diab                   | fpg_cat3     |      7080 |      2880 |              4200 |                144 |                   nan |       1467 |                  1269 |                 5    |                  nan    |        50.94 |                   44.06 |
| adults_no_known_diab_core_complete     | hba1c_binary |      5379 |      5105 |               274 |                nan |                  1537 |       3568 |                   nan |               nan    |                   30.11 |        69.89 |                  nan    |
| adults_no_known_diab_core_complete     | fpg_binary   |      5379 |      2844 |              2535 |                nan |                  1394 |       1450 |                   nan |               nan    |                   49.02 |        50.98 |                  nan    |
| adults_no_known_diab_core_complete     | hba1c_cat3   |      5379 |      5105 |               274 |                150 |                   nan |       3568 |                  1387 |                 2.94 |                  nan    |        69.89 |                   27.17 |
| adults_no_known_diab_core_complete     | fpg_cat3     |      5379 |      2844 |              2535 |                143 |                   nan |       1450 |                  1251 |                 5.03 |                  nan    |        50.98 |                   43.99 |
| adults_no_known_diab_expanded_complete | hba1c_binary |      5197 |      4944 |               253 |                nan |                  1491 |       3453 |                   nan |               nan    |                   30.16 |        69.84 |                  nan    |
| adults_no_known_diab_expanded_complete | fpg_binary   |      5197 |      2752 |              2445 |                nan |                  1359 |       1393 |                   nan |               nan    |                   49.38 |        50.62 |                  nan    |
| adults_no_known_diab_expanded_complete | hba1c_cat3   |      5197 |      4944 |               253 |                144 |                   nan |       3453 |                  1347 |                 2.91 |                  nan    |        69.84 |                   27.25 |
| adults_no_known_diab_expanded_complete | fpg_cat3     |      5197 |      2752 |              2445 |                136 |                   nan |       1393 |                  1223 |                 4.94 |                  nan    |        50.62 |                   44.44 |


## 13. Survey-Design Considerations

- **WTMEC2YR**: valid=11933/11933, >0=11933, range=[5.398e-79, 2.271e+05]
- **WTSAF2YR**: valid=3996/11933, >0=3996, range=[5.398e-79, 5.619e+05]
- **SDMVSTRA**: valid=11933/11933, >0=11933, range=[173, 187]
- **SDMVPSU**: valid=11933/11933, >0=11933, range=[1, 2]

### Weight Usage Requirements

| Analysis | Required Weight |
|----------|----------------|
| Analyses using MEC exam data (BMI, BP, HbA1c) | WTMEC2YR |
| Analyses using fasting glucose (LBXGLU) | WTSAF2YR |
| Interview-only analyses (demographics, questionnaire) | WTINT2YR |

**Current status:** All feasibility counts in this report are **unweighted raw counts**.
Population-representative prevalence estimates require appropriate survey weights,
strata (SDMVSTRA), and PSUs (SDMVPSU) via a survey-design-aware analysis
(e.g., `statsmodels` survey module or R `survey` package).

Model training may use unweighted data with survey weights applied during
evaluation, or may incorporate weights directly — this is a research design
decision that is NOT made in this feasibility report.

## 14. Data-Quality Observations

### Missingness Summary

| variable   |   total |   missing |   missing_pct |
|:-----------|--------:|----------:|--------------:|
| RIDAGEYR   |   11933 |         0 |          0    |
| RIAGENDR   |   11933 |         0 |          0    |
| BMXBMI     |   11933 |      3462 |         29.01 |
| BMXWAIST   |   11933 |      3743 |         31.37 |
| BPQ020     |   11933 |      3435 |         28.79 |
| SMQ020     |   11933 |      3798 |         31.83 |
| SMQ040     |   11933 |      8690 |         72.82 |
| PAD680     |   11933 |      3795 |         31.8  |
| DIQ010     |   11933 |       193 |          1.62 |
| LBXGH      |   11933 |      5218 |         43.73 |
| LBXGLU     |   11933 |      8261 |         69.23 |
| WTMEC2YR   |   11933 |         0 |          0    |
| WTSAF2YR   |   11933 |      7937 |         66.51 |
| SDMVSTRA   |   11933 |         0 |          0    |
| SDMVPSU    |   11933 |         0 |          0    |


### Data Quality Issues

| issue_type                | variable       | detail                                                                                                                                                      | severity   |
|:--------------------------|:---------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------|
| high_missingness          | BMXBMI         | 29.0% missing (3462/11933)                                                                                                                                  | moderate   |
| high_missingness          | BMXWAIST       | 31.4% missing (3743/11933)                                                                                                                                  | moderate   |
| high_missingness          | BPQ020         | 28.8% missing (3435/11933)                                                                                                                                  | moderate   |
| high_missingness          | SMQ020         | 31.8% missing (3798/11933)                                                                                                                                  | moderate   |
| high_missingness          | SMQ040         | 72.8% missing (8690/11933)                                                                                                                                  | high       |
| high_missingness          | PAD680         | 31.8% missing (3795/11933)                                                                                                                                  | moderate   |
| high_missingness          | LBXGH          | 43.7% missing (5218/11933)                                                                                                                                  | moderate   |
| high_missingness          | LBXGLU         | 69.2% missing (8261/11933)                                                                                                                                  | high       |
| high_missingness          | WTSAF2YR       | 66.5% missing (7937/11933)                                                                                                                                  | high       |
| special_missing_code      | BPQ020         | Code 7 appears 1 times (refused/don't know)                                                                                                                 | info       |
| special_missing_code      | BPQ020         | Code 9 appears 10 times (refused/don't know)                                                                                                                | info       |
| special_missing_code      | SMQ020         | Code 7 appears 7 times (refused/don't know)                                                                                                                 | info       |
| special_missing_code      | SMQ020         | Code 9 appears 7 times (refused/don't know)                                                                                                                 | info       |
| special_missing_code      | DIQ010         | Code 9 appears 4 times (refused/don't know)                                                                                                                 | info       |
| special_missing_code      | DIQ160         | Code 9 appears 15 times (refused/don't know)                                                                                                                | info       |
| sample_availability_range | all_components | Component sizes range from 3672 to 11933 (diff=8261). Details: {'DEMO_L': 11933, 'BMX_L': 8471, 'BPQ_L': 8498, 'SMQ_L': 8135, 'GHB_L': 6715, 'GLU_L': 3672} | info       |


## 15. Factual Findings — No Recommendation

This section summarizes factual observations from the feasibility audit.
**No recommendations are made regarding migration, target selection, model
architecture, feature selection, or thesis direction.**

### Data Availability

1. NHANES August 2021–August 2023 provides **11,933 total participants** across 8 component files.
2. **8153** participants are adults (age ≥ 18).
3. **7080** adults do not report known diabetes.

### Feature Availability

4. Core Stage-1 features (age, sex, BMI, hypertension, smoking) are available for a
   substantial subset of the screening cohort (N=5379 for Cohort C).

### Laboratory Outcomes

5. HbA1c is available for a larger subset than fasting glucose.
6. Fasting glucose is available only for a fasting subsample.
7. HbA1c and fasting glucose show imperfect concordance, as expected clinically.

### Class Distribution

8. Using HbA1c-based or FPG-based dysglycemia as a binary outcome produces
   class-imbalanced distributions, as expected in screening populations.
9. The degree of imbalance varies by cohort definition and outcome measure.

### Survey Design

10. NHANES survey design variables (weights, strata, PSUs) are present and must be
    considered in any population-representative analysis.
11. Fasting glucose analyses specifically require fasting subsample weights (WTSAF2YR).

### Data Quality

12. No duplicate SEQN values were found in any component file.
13. Missingness patterns reflect the NHANES survey design (MEC subsample, fasting subsample).
14. Special missing codes (refused/don't know) are present in questionnaire variables
    and must be handled appropriately in any modeling effort.

---

*This report was generated programmatically from NHANES 2021-2023 public-use files.*
*All counts are unweighted. No data modification, imputation, or modeling was performed.*