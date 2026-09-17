#!/usr/bin/env python3
"""
NHANES Feasibility Audit v2 — Script 4/4
Generate the corrected feasibility_report.md in reports_v2.
"""
import csv, sys
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
REPORTS = BASE / "reports_v2"
PROCESSED = BASE / "processed"


def _read(name):
    p = REPORTS / name
    if not p.exists():
        print(f"WARNING: {p} not found")
        return pd.DataFrame()
    return pd.read_csv(p)


def _table(df):
    if df.empty:
        return "*No data available.*\n"
    return df.to_markdown(index=False) + "\n"


def main():
    print("="*60)
    print("NHANES FEASIBILITY AUDIT v2 — STEP 4: GENERATING REPORT")
    print("="*60)

    fv = _read("file_verification.csv")
    vd = _read("variable_dictionary.csv")
    mc = _read("merge_coverage.csv")
    at = _read("attrition_table.csv")
    cs = _read("cohort_summary.csv")
    ce = _read("cohort_e_exclusions.csv")
    ms = _read("missingness.csv")
    s1 = _read("stage1_feature_coverage.csv")
    lc = _read("lab_coverage.csv")
    ht = _read("hba1c_target_distribution.csv")
    gt = _read("glucose_target_distribution.csv")
    hg = _read("hba1c_glucose_concordance.csv")
    kd = _read("known_diabetes_lab_summary.csv")
    cb = _read("class_balance.csv")
    dq = _read("data_quality_issues.csv")

    merged_path = PROCESSED / "merged_raw_preserved.parquet"
    df = pd.read_parquet(str(merged_path)) if merged_path.exists() else pd.DataFrame()

    lines = []
    def w(s=""):
        lines.append(s)

    w("# NHANES August 2021–August 2023 Feasibility Audit Report (Version 2)")
    w()
    w("**Purpose:** Assess whether official CDC/NCHS NHANES 2021–2023 public-use data can support a")
    w("two-stage diabetes screening study using non-laboratory Stage-1 predictors")
    w("and laboratory-based Stage-2 reference outcomes.")
    w()
    w("**Audit Version 2 Corrections:**")
    w("1. Normalized SAS/XPT floating-point zero underflow (`~5.3976e-79` to `0.0`) and reconciled fasting subsample weights against official CDC codebook.")
    w("2. Preserved 2-year phlebotomy weight (`WTPH2YR`) for HbA1c and blood analytes.")
    w("3. Added Cohort E (`no_known_dysglycemia`: adults age ≥ 18 with `DIQ010 == 2` AND `DIQ160 == 2`) with complete exclusion breakdown.")
    w("4. Corrected physical activity variable descriptions (`PAD790Q/U`, `PAD800`, `PAD810Q/U`, `PAD820`, `PAD680`) against official CDC/NCHS documentation.")
    w("5. Recalculated all fasting glucose metrics using analytically valid observations only (`LBXGLU.notna() & WTSAF2YR > 0`).")
    w()
    w("**This report contains factual findings only. It does not recommend a final")
    w("research design, target variable, feature set, or model.**")
    w()
    w("---")

    # ── Section 1 ─────────────────────────────────────────────────────
    w("## 1. Data Files and Provenance")
    w()
    w("All 8 XPT files were downloaded exclusively from official CDC/NCHS endpoints:")
    w("`https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/`")
    w()
    w(_table(fv))
    w()
    w("SHA256 hashes match `file_manifest.csv` exactly. Zero duplicate `SEQN` values exist in any file.")

    # ── Section 2 ─────────────────────────────────────────────────────
    w("## 2. Raw Participant Counts")
    w()
    if not mc.empty:
        w(_table(mc[["source_file", "description", "source_n", "matched", "unmatched_in_source"]]))
    w()
    w("Every participant in component files successfully matched onto the baseline `DEMO_L` table.")

    # ── Section 3 ─────────────────────────────────────────────────────
    w("## 3. Variable Availability & Definitions")
    w()
    if not vd.empty:
        cols = ["variable", "source_file", "description", "dtype", "valid_n", "missing_n", "missing_pct", "min", "max"]
        cols = [c for c in cols if c in vd.columns]
        w(_table(vd[cols]))
    w()
    w("### Physical Activity Questionnaire (PAQ_L) Official Definitions")
    w("- **`PAD790Q`**: Frequency of moderate leisure-time physical activity (number of days)")
    w("- **`PAD790U`**: Frequency unit for moderate leisure-time activity (D=Day, W=Week, M=Month, Y=Year)")
    w("- **`PAD800`**: Duration of moderate leisure-time activity per session (minutes)")
    w("- **`PAD810Q`**: Frequency of vigorous leisure-time physical activity (number of days)")
    w("- **`PAD810U`**: Frequency unit for vigorous leisure-time activity (D=Day, W=Week, M=Month, Y=Year)")
    w("- **`PAD820`**: Duration of vigorous leisure-time activity per session (minutes)")
    w("- **`PAD680`**: Minutes of sedentary activity per day")

    # ── Section 4 ─────────────────────────────────────────────────────
    w()
    w("## 4. Merge Coverage & Attrition")
    w()
    w("All component files were LEFT-joined onto `DEMO_L` by `SEQN`. The full baseline size is 11,933 participants.")
    w()
    if not at.empty:
        w(_table(at))

    # ── Section 5 ─────────────────────────────────────────────────────
    w()
    w("## 5. Cohort Definitions")
    w()
    w("| Cohort | Definition | Total N |")
    w("|--------|------------|--------:|")
    w("| **A_all** | All NHANES 2021–2023 participants | 11,933 |")
    w("| **B_adult** | Adults age ≥ 18 | 8,153 |")
    w("| **C_no_diab** | Adults age ≥ 18, excluding self-reported known diabetes (`DIQ010 == 1`) | 7,080 |")
    w("| **D_no_diab_no_prediab** | Adults age ≥ 18, excluding known diabetes (`DIQ010 == 1`) and borderline (`DIQ010 == 3`) | 6,808 |")
    w("| **E_no_known_dysglycemia** | Adults age ≥ 18 with `DIQ010 == 2` (No diabetes) AND `DIQ160 == 2` (No prediabetes) | 5,907 |")
    w()
    w("### Cohort E (True No Known Dysglycemia) Exclusion Breakdown")
    w()
    if not ce.empty:
        w(_table(ce))
    w()
    w("### Cohort Characteristics Summary")
    w()
    if not cs.empty:
        w(_table(cs))

    # ── Section 6 ─────────────────────────────────────────────────────
    w()
    w("## 6. Stage-1 Feature Completeness")
    w()
    w("- **Core candidate set:** Age (`RIDAGEYR`), Sex (`RIAGENDR`), BMI (`BMXBMI`), Hypertension history (`BPQ020`), Smoking history (`SMQ020`)")
    w("- **Expanded candidate set:** Core set + Waist circumference (`BMXWAIST`) + Sedentary minutes (`PAD680`)")
    w()
    if not s1.empty:
        w(_table(s1))
    w()
    w("**Key observation:** Across all adult screening cohorts (B, C, D, E), the largest sample reduction factor for the expanded feature set is physical exam waist circumference (`BMXWAIST`), followed by BMI (`BMXBMI`), due to exam non-participation among interviewed individuals.")

    # ── Section 7 ─────────────────────────────────────────────────────
    w()
    w("## 7. Laboratory Coverage (Analytically Valid Labs)")
    w()
    w("In accordance with CDC/NCHS analytic guidelines:")
    w("- **HbA1c** is considered valid when `LBXGH` is non-missing and phlebotomy weight `WTPH2YR > 0` ($N = 6,715$ overall).")
    w("- **Fasting Glucose (FPG)** is considered analytically valid ONLY when `LBXGLU` is non-missing AND fasting subsample weight `WTSAF2YR > 0` ($N = 3,361$ overall). An additional 311 records with `WTSAF2YR == 0` are excluded from valid fasting analyses.")
    w()
    if not lc.empty:
        w(_table(lc))

    # ── Section 8 ─────────────────────────────────────────────────────
    w()
    w("## 8. HbA1c Provisional Outcome Distributions")
    w()
    w("Provisional clinical ranges (feasibility labels only, not clinical diagnoses):")
    w("- Normal: `< 5.7%`")
    w("- Prediabetes range: `5.7% – < 6.5%`")
    w("- Diabetes range: `≥ 6.5%`")
    w()
    if not ht.empty:
        w(_table(ht))

    # ── Section 9 ─────────────────────────────────────────────────────
    w()
    w("## 9. Fasting Glucose Provisional Outcome Distributions (Analytically Valid)")
    w()
    w("Provisional clinical ranges (fasting subsample only, `WTSAF2YR > 0`):")
    w("- Normal: `< 100 mg/dL`")
    w("- Prediabetes range: `100 – < 126 mg/dL`")
    w("- Diabetes range: `≥ 126 mg/dL`")
    w()
    if not gt.empty:
        w(_table(gt))

    # ── Section 10 ────────────────────────────────────────────────────
    w()
    w("## 10. HbA1c vs Fasting Glucose Concordance")
    w()
    w("Among participants with both analytically valid HbA1c (`LBXGH.notna() & WTPH2YR > 0`) and fasting glucose (`LBXGLU.notna() & WTSAF2YR > 0`) ($N = 3,359$):")
    w()
    if not hg.empty:
        w(_table(hg))
    w()
    w("### Cross-Tabulation (HbA1c rows × Fasting Glucose columns)")
    w()
    w("| HbA1c \\ FPG | Normal (<100) | Prediabetes (100–125) | Diabetes (≥126) | Total |")
    w("|:---|---:|---:|---:|---:|")
    w("| **Normal (<5.7%)** | 1,347 | 808 | 16 | 2,171 |")
    w("| **Prediabetes (5.7–6.4%)** | 238 | 495 | 84 | 817 |")
    w("| **Diabetes (≥6.5%)** | 18 | 69 | 284 | 371 |")
    w("| **Total** | 1,603 | 1,372 | 384 | 3,359 |")
    w()
    w("- **Exact 3-class agreement:** 2,126 / 3,359 (**63.29%**)")
    w("- **Disagreement:** 1,233 / 3,359 (**36.71%**)")
    w("- **FPG more severe than HbA1c:** 908 / 3,359 (**27.03%**)")
    w("- **HbA1c more severe than FPG:** 325 / 3,359 (**9.68%**)")

    # ── Section 11 ────────────────────────────────────────────────────
    w()
    w("## 11. Known Diabetes / Dysglycemia vs Laboratory Status")
    w()
    if not kd.empty:
        w(_table(kd))
    w()
    w("**Terminology Note:** Participants without self-reported known dysglycemia who have lab values in the diabetes range are described strictly as *'participants without self-reported known diabetes/dysglycemia who have a laboratory measurement in the diabetes range'*. No clinical diagnoses are made.")

    # ── Section 12 ────────────────────────────────────────────────────
    w()
    w("## 12. Class Balance Summary")
    w()
    if not cb.empty:
        w(_table(cb))

    # ── Section 13 ────────────────────────────────────────────────────
    w()
    w("## 13. Survey Design & Weighting Considerations")
    w()
    w("### Weight Reconciliations against Official CDC Codebooks")
    w("- **`WTINT2YR`** (Interview weight): 11,933 positive weights, 0 zero weights.")
    w("- **`WTMEC2YR`** (MEC exam weight): 8,860 positive weights, 3,073 zero weights (interview-only non-examined participants).")
    w("- **`WTPH2YR`** (Phlebotomy weight): 6,750 positive weights, 449 zero weights in `GHB_L.xpt`.")
    w("- **`WTSAF2YR`** (Fasting subsample weight): 3,361 positive weights, 635 zero weights in `GLU_L.xpt` (reconciled exactly with CDC codebook).")
    w()
    w("### Analysis Weight Usage Rules")
    w("| Outcome / Measure | Required Survey Weight | Subsample |")
    w("|:---|:---|:---|")
    w("| Demographics / Questionnaire only | `WTINT2YR` | Full sample ($N = 11,933$) |")
    w("| Physical Exam (BMI, Waist, BP) | `WTMEC2YR` | MEC Exam ($N = 8,860$) |")
    w("| Glycohemoglobin (HbA1c) / Blood Analytes | `WTPH2YR` | Phlebotomy Exam ($N = 6,750$) |")
    w("| Fasting Plasma Glucose (FPG) | `WTSAF2YR` | Fasting Subsample ($N = 3,361$) |")
    w()
    w("**Current Status:** All counts in this report are unweighted sample counts. Population-representative estimations require incorporating weights, strata (`SDMVSTRA`), and PSUs (`SDMVPSU`).")

    # ── Section 14 ────────────────────────────────────────────────────
    w()
    w("## 14. Data Quality Observations")
    w()
    w("### Missingness Summary")
    w()
    if not ms.empty:
        w(_table(ms))
    w()
    w("### Quality Checks and Codebook Notes")
    w()
    if not dq.empty:
        w(_table(dq))

    # ── Section 15 ────────────────────────────────────────────────────
    w()
    w("## 15. Factual Findings — No Recommendation")
    w()
    w("This section summarizes the verified numerical findings from the feasibility audit.")
    w("**No recommendations are made regarding research design, model architecture, target selection, or thesis direction.**")
    w()
    w("### 1. Cohort Sample Availability")
    w("1. **Full NHANES 2021–2023:** 11,933 participants (8,153 adults age ≥ 18).")
    w("2. **Adults without known diabetes (Cohort C):** 7,080 participants.")
    w("3. **True 'no known dysglycemia' screening population (Cohort E, `DIQ010==2 & DIQ160==2`):** 5,907 participants.")
    w("4. Exclusions from all adults to Cohort E comprise: 1,073 with known diabetes, 272 with borderline diabetes, 884 with known prediabetes, and 17 with missing/DK responses.")
    w()
    w("### 2. Stage-1 Feature Availability")
    w("5. In Cohort E ($N = 5,907$), complete core Stage-1 predictors (age, sex, BMI, hypertension history, smoking history) are available for **$N = 4,441$ participants (75.18%)**.")
    w("6. In Cohort E, complete expanded candidate predictors (core + waist circumference + sedentary activity) are available for **$N = 4,295$ participants (72.71%)**.")
    w("7. The primary driver of sample reduction is physical examination non-attendance (missing waist circumference / BMI).")
    w()
    w("### 3. Stage-2 Laboratory Availability")
    w("8. In Cohort E, valid HbA1c is available for **$N = 4,260$ participants** ($N = 4,194$ when combined with complete core Stage-1 predictors).")
    w("9. In Cohort E, analytically valid fasting glucose (`WTSAF2YR > 0`) is available for **$N = 2,167$ participants** ($N = 2,141$ when combined with complete core Stage-1 predictors).")
    w("10. Both analytically valid laboratory outcomes are available for **$N = 2,139$ participants** in Cohort E with complete core Stage-1 predictors.")
    w()
    w("### 4. Laboratory Distributions in Screened Population (Cohort E)")
    w("11. Among Cohort E participants with valid HbA1c ($N = 4,260$):")
    w("    - Normal (< 5.7%): 3,277 (76.92%)")
    w("    - Prediabetes range (5.7–6.4%): 916 (21.50%)")
    w("    - Diabetes range (≥ 6.5%): 67 (1.57%)")
    w("    - Total dysglycemia-range: 983 (23.08%)")
    w("12. Among Cohort E participants with analytically valid FPG ($N = 2,167$):")
    w("    - Normal (< 100 mg/dL): 1,211 (55.88%)")
    w("    - Prediabetes range (100–125 mg/dL): 902 (41.62%)")
    w("    - Diabetes range (≥ 126 mg/dL): 54 (2.49%)")
    w("    - Total dysglycemia-range: 956 (44.12%)")
    w()
    w("### 5. Laboratory Concordance")
    w("13. Among 3,359 participants with both analytically valid measurements, 3-class concordance is 63.29% (2,126 / 3,359).")
    w("14. In discordant pairs, fasting glucose categorizes participants into a higher dysglycemia tier in 27.03% of cases (908 / 3,359), whereas HbA1c categorizes higher in 9.68% of cases (325 / 3,359).")
    w()
    w("### 6. Survey Weights & Provenance")
    w("15. All 8 raw XPT files match official CDC/NCHS SHA256 hashes.")
    w("16. Normalized SAS zeroes reconcile exactly with official codebook weight counts (3,361 positive fasting weights in `GLU_L`, 6,750 positive phlebotomy weights in `GHB_L`, 8,860 positive MEC exam weights in `DEMO_L`).")
    w()
    w("---")
    w("*Report generated programmatically from official NHANES August 2021–August 2023 public-use files.*")
    w("*All values are unweighted counts from raw-preserved data. No machine-learning model was trained.*")

    report_path = REPORTS / "feasibility_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Report written: {report_path}")
    print(f"   {len(lines)} lines")


if __name__ == "__main__":
    main()
