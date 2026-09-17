# Phase 3 Expanded Count Discrepancy Reconciliation

**Audit Question:** Why did the V2 Feasibility Report indicate $N \approx 4,066$ for expanded Stage-1 complete + HbA1c, while the Phase 3 canonical dataset `analytic_expanded_complete.parquet` contains $N = 4,044$?

**Status:** **100% RECONCILED AND VERIFIED.** $N = 4,044$ is the exact, methodologically correct count.

---

## 1. Quantitative Discrepancy Overview

| Stage | Dataset / Condition | Total N | Normal (< 5.7%) | Dysglycemia (≥ 5.7%) |
|:---|:---|---:|---:|---:|
| **Feasibility V2 Audit** | `core_complete & BMXWAIST.notna() & PAD680.notna()` | **4,066** | 3,120 | 946 |
| **Phase 3 Canonical** | `core_complete & waist_cm.notna() & sedentary_minutes_day.notna()` | **4,044** | 3,106 | 938 |
| **Difference** | Excluded special-code participants | **22** | **14** | **8** |

---

## 2. Root Cause Analysis

In the NHANES Physical Activity Questionnaire (`PAQ_L`), variable `PAD680` measures self-reported minutes of sedentary activity per day:
- Valid physical measurements range from $0$ to $1,440$ minutes ($24$ hours).
- `7777` is the official CDC/NCHS missing-value code for **"Refused"**.
- `9999` is the official CDC/NCHS missing-value code for **"Don't Know"**.

During the Phase 2/V2 feasibility audit, exploratory script `feasibility_analysis_v2.py` checked simple missingness via `cdf['PAD680'].notna()`, which retained raw sentinel numeric values ($7,777$ and $9,999$) as "non-missing."

During Phase 3 canonical construction, data integrity rules required sentinel non-response codes to be properly converted to `NaN`:
```python
df["sedentary_minutes_day"] = merged["PAD680"].replace({7777: np.nan, 9999: np.nan})
```
Treating $9,999$ minutes as a valid measurement would falsely claim that a participant spent $166.65$ hours per day sitting, severely distorting any continuous modeling, feature scaling, or spline fitting.

---

## 3. The 22 Affected Participants

All 22 participants have complete core Stage-1 predictors, valid physical exam waist circumference, and valid HbA1c, but answered "Don't Know" ($N=21$) or "Refused" ($N=1$) on `PAD680`:

| SEQN | Age | Sex | BMI (kg/m²) | Waist (cm) | Raw PAD680 | Cleaned `sedentary_minutes_day` | HbA1c (%) | `hba1c_dysglycemia` |
|---:|---:|:---|---:|---:|---:|:---|---:|:---|
| 130628 | 22 | Male | 19.7 | 75.5 | 9999.0 | `NaN` (Don't Know) | 5.7 | 1 (Dysglycemia) |
| 131510 | 61 | Female | 23.2 | 92.7 | 9999.0 | `NaN` (Don't Know) | 5.3 | 0 (Normal) |
| 132284 | 76 | Female | 28.7 | 105.9 | 9999.0 | `NaN` (Don't Know) | 6.0 | 1 (Dysglycemia) |
| 132296 | 68 | Female | 38.8 | 130.9 | 9999.0 | `NaN` (Don't Know) | 5.3 | 0 (Normal) |
| 133077 | 69 | Male | 33.3 | 110.5 | 9999.0 | `NaN` (Don't Know) | 5.4 | 0 (Normal) |
| 133195 | 33 | Male | 40.4 | 131.8 | 9999.0 | `NaN` (Don't Know) | 4.5 | 0 (Normal) |
| 133314 | 34 | Male | 25.5 | 96.8 | 9999.0 | `NaN` (Don't Know) | 5.3 | 0 (Normal) |
| 133628 | 53 | Male | 28.7 | 96.0 | 9999.0 | `NaN` (Don't Know) | 5.5 | 0 (Normal) |
| 135198 | 80 | Male | 24.4 | 97.6 | 9999.0 | `NaN` (Don't Know) | 5.8 | 1 (Dysglycemia) |
| 135960 | 75 | Female | 29.3 | 98.8 | 9999.0 | `NaN` (Don't Know) | 5.6 | 0 (Normal) |
| 136106 | 44 | Female | 19.7 | 78.1 | 9999.0 | `NaN` (Don't Know) | 5.0 | 0 (Normal) |
| 137936 | 72 | Female | 19.1 | 74.7 | 9999.0 | `NaN` (Don't Know) | 5.5 | 0 (Normal) |
| 138050 | 75 | Female | 43.6 | 129.5 | 7777.0 | `NaN` (Refused) | 6.1 | 1 (Dysglycemia) |
| 138240 | 78 | Male | 37.7 | 122.5 | 9999.0 | `NaN` (Don't Know) | 6.4 | 1 (Dysglycemia) |
| 138600 | 34 | Female | 35.3 | 117.4 | 9999.0 | `NaN` (Don't Know) | 5.4 | 0 (Normal) |
| 139525 | 47 | Male | 27.0 | 98.6 | 9999.0 | `NaN` (Don't Know) | 4.9 | 0 (Normal) |
| 139527 | 68 | Female | 28.8 | 92.7 | 9999.0 | `NaN` (Don't Know) | 6.0 | 1 (Dysglycemia) |
| 139856 | 35 | Male | 32.0 | 100.5 | 9999.0 | `NaN` (Don't Know) | 6.0 | 1 (Dysglycemia) |
| 140458 | 22 | Male | 23.2 | 82.3 | 9999.0 | `NaN` (Don't Know) | 5.1 | 0 (Normal) |
| 140527 | 68 | Female | 20.4 | 81.5 | 9999.0 | `NaN` (Don't Know) | 5.5 | 0 (Normal) |
| 141249 | 45 | Female | 27.8 | 104.2 | 9999.0 | `NaN` (Don't Know) | 5.1 | 0 (Normal) |
| 141750 | 59 | Female | 36.5 | 116.8 | 9999.0 | `NaN` (Don't Know) | 6.3 | 1 (Dysglycemia) |

---

## 4. Conclusion & Verification

- **Confirmation:** The discrepancy of 22 participants between Phase 2 feasibility ($N = 4,066$) and Phase 3 canonical ($N = 4,044$) is 100% accounted for by 21 instances of `PAD680 == 9999` and 1 instance of `PAD680 == 7777`.
- **Methodological Verdict:** $N = 4,044$ is the **correct and valid** sample size for `analytic_expanded_complete.parquet`.
- **Approval:** Proceeding with Phase 4 experimental protocol.
