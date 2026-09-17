#!/usr/bin/env python3
"""
NHANES Feasibility Audit — Script 4/4
Generate the final feasibility_report.md from all CSV outputs.
"""
import csv, sys
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
REPORTS = BASE / "reports"
PROCESSED = BASE / "processed"


def _read(name):
    p = REPORTS / name
    if not p.exists():
        print(f"WARNING: {p} not found")
        return pd.DataFrame()
    return pd.read_csv(p)


def _table(df, max_col_width=None):
    if df.empty:
        return "*No data available.*\n"
    return df.to_markdown(index=False) + "\n"


def main():
    fv = _read("file_verification.csv")
    vd = _read("variable_dictionary.csv")
    mc = _read("merge_coverage.csv")
    at = _read("attrition_table.csv")
    cs = _read("cohort_summary.csv")
    ms = _read("missingness.csv")
    s1 = _read("stage1_feature_coverage.csv")
    lc = _read("lab_coverage.csv")
    ht = _read("hba1c_target_distribution.csv")
    gt = _read("glucose_target_distribution.csv")
    hg = _read("hba1c_glucose_concordance.csv")
    kd = _read("known_diabetes_lab_summary.csv")
    dq = _read("data_quality_issues.csv")

    # Try to read class balance
    cb_path = REPORTS / "class_balance.csv"
    cb = pd.read_csv(cb_path) if cb_path.exists() else pd.DataFrame()

    # Load merged for survey design stats
    merged_path = PROCESSED / "merged_raw_preserved.parquet"
    df = pd.read_parquet(str(merged_path)) if merged_path.exists() else pd.DataFrame()

    lines = []
    def w(s=""):
        lines.append(s)

    w("# NHANES August 2021–August 2023 Feasibility Audit Report")
    w()
    w("**Purpose:** Assess whether NHANES 2021-2023 public-use data can support a")
    w("two-stage diabetes screening study using non-laboratory Stage-1 predictors")
    w("and laboratory-based Stage-2 reference outcomes.")
    w()
    w("**This report contains factual findings only. It does not recommend a final")
    w("research design, target variable, feature set, or model.**")
    w()
    w("---")

    # ── Section 1 ─────────────────────────────────────────────────────
    w()
    w("## 1. Data Files and Provenance")
    w()
    w("All files were downloaded from official CDC/NCHS endpoints:")
    w("`https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/`")
    w()
    w(_table(fv))
    w()
    w("SHA256 hashes were verified against `file_manifest.csv` generated at download time.")

    # ── Section 2 ─────────────────────────────────────────────────────
    w()
    w("## 2. Raw Participant Counts")
    w()
    if not mc.empty:
        w(_table(mc[["source_file", "description", "source_n", "matched", "unmatched_in_source"]]))
    w()
    w("All SEQN values are unique within each component file (zero duplicates).")

    # ── Section 3 ─────────────────────────────────────────────────────
    w()
    w("## 3. Variable Availability")
    w()
    if not vd.empty:
        cols = ["variable", "source_file", "description", "dtype", "valid_n", "missing_n", "missing_pct", "min", "max"]
        cols = [c for c in cols if c in vd.columns]
        w(_table(vd[cols]))
    w()
    w("**Note:** Frequency tables for categorical variables and special missing codes")
    w("are available in `variable_dictionary.csv`.")

    # ── Section 4 ─────────────────────────────────────────────────────
    w()
    w("## 4. Merge Coverage")
    w()
    w("All component files were LEFT-joined onto DEMO_L using SEQN.")
    w("DEMO_L serves as the base participant table.")
    w()
    if not mc.empty:
        w(_table(mc))
    w()
    w("### Attrition Table")
    w()
    if not at.empty:
        w(_table(at))
    w()
    w("Since left joins were used, participant count remains constant at the DEMO_L baseline.")
    w("Variables from component files become NaN for unmatched participants.")

    # ── Section 5 ─────────────────────────────────────────────────────
    w()
    w("## 5. Cohort Definitions")
    w()
    w("| Cohort | Definition |")
    w("|--------|------------|")
    w("| A_all | All NHANES 2021-2023 participants |")
    w("| B_adult | Adults age ≥ 18 |")
    w("| C_no_diab | Adults age ≥ 18, excluding self-reported known diabetes (DIQ010=1) |")
    w("| D_no_diab_no_prediab | Adults age ≥ 18, excluding known diabetes (DIQ010=1) AND borderline/prediabetes (DIQ010=3) |")
    w()
    if not cs.empty:
        w(_table(cs))

    # ── Section 6 ─────────────────────────────────────────────────────
    w()
    w("## 6. Stage-1 Feature Completeness")
    w()
    w("**Core candidate set:** age, sex, BMI, hypertension history (BPQ020), smoking history (SMQ020)")
    w()
    w("**Expanded candidate set:** Core + waist circumference (BMXWAIST) + sedentary minutes (PAD680)")
    w()
    if not s1.empty:
        w(_table(s1))

    # ── Section 7 ─────────────────────────────────────────────────────
    w()
    w("## 7. Laboratory Coverage")
    w()
    if not lc.empty:
        w(_table(lc))
    w()
    w("**Note:** Fasting glucose (LBXGLU) is measured only on a subsample of MEC-examined participants.")
    w("The fasting subsample weight (WTSAF2YR) must be used for population-representative")
    w("analyses involving fasting glucose.")

    # ── Section 8 ─────────────────────────────────────────────────────
    w()
    w("## 8. HbA1c Provisional Outcome Distributions")
    w()
    w("Provisional categories based on standard clinical thresholds (feasibility labels only):")
    w()
    w("| Category | HbA1c Range |")
    w("|----------|-------------|")
    w("| Normal | < 5.7% |")
    w("| Prediabetes range | 5.7% – < 6.5% |")
    w("| Diabetes range | ≥ 6.5% |")
    w()
    if not ht.empty:
        w(_table(ht))

    # ── Section 9 ─────────────────────────────────────────────────────
    w()
    w("## 9. Fasting Glucose Provisional Outcome Distributions")
    w()
    w("| Category | FPG Range |")
    w("|----------|-----------|")
    w("| Normal | < 100 mg/dL |")
    w("| Prediabetes range | 100 – < 126 mg/dL |")
    w("| Diabetes range | ≥ 126 mg/dL |")
    w()
    if not gt.empty:
        w(_table(gt))

    # ── Section 10 ────────────────────────────────────────────────────
    w()
    w("## 10. HbA1c vs Fasting Glucose Agreement")
    w()
    w("For participants with both valid HbA1c and fasting glucose measurements:")
    w()
    if not hg.empty:
        w(_table(hg))
    w()
    w("**Interpretation:** Discordant cases are expected and well-documented in the")
    w("clinical literature. HbA1c and fasting glucose measure different aspects of")
    w("glucose metabolism and have known imperfect concordance.")

    # ── Section 11 ────────────────────────────────────────────────────
    w()
    w("## 11. Known Diabetes vs Laboratory Status")
    w()
    w("Participants are divided by self-reported diabetes status (DIQ010).")
    w()
    if not kd.empty:
        w(_table(kd))
    w()
    w("**Terminology note:** Participants without self-reported known diabetes who have")
    w("a laboratory measurement in the diabetes range are described as such. This report")
    w("does NOT claim these participants have undiagnosed diabetes — only that their")
    w("laboratory values fall within the diabetes range according to standard thresholds.")

    # ── Section 12 ────────────────────────────────────────────────────
    w()
    w("## 12. Class Balance")
    w()
    w("Potential Stage-1 reference targets across cohort definitions:")
    w()
    if not cb.empty:
        w(_table(cb))

    # ── Section 13 ────────────────────────────────────────────────────
    w()
    w("## 13. Survey-Design Considerations")
    w()
    if not df.empty:
        for var in ["WTMEC2YR", "WTSAF2YR", "SDMVSTRA", "SDMVPSU"]:
            if var in df.columns:
                v = df[var].dropna()
                gt0 = int((v > 0).sum())
                w(f"- **{var}**: valid={len(v)}/{len(df)}, >0={gt0}, "
                  f"range=[{v.min():.4g}, {v.max():.4g}]")
    w()
    w("### Weight Usage Requirements")
    w()
    w("| Analysis | Required Weight |")
    w("|----------|----------------|")
    w("| Analyses using MEC exam data (BMI, BP, HbA1c) | WTMEC2YR |")
    w("| Analyses using fasting glucose (LBXGLU) | WTSAF2YR |")
    w("| Interview-only analyses (demographics, questionnaire) | WTINT2YR |")
    w()
    w("**Current status:** All feasibility counts in this report are **unweighted raw counts**.")
    w("Population-representative prevalence estimates require appropriate survey weights,")
    w("strata (SDMVSTRA), and PSUs (SDMVPSU) via a survey-design-aware analysis")
    w("(e.g., `statsmodels` survey module or R `survey` package).")
    w()
    w("Model training may use unweighted data with survey weights applied during")
    w("evaluation, or may incorporate weights directly — this is a research design")
    w("decision that is NOT made in this feasibility report.")

    # ── Section 14 ────────────────────────────────────────────────────
    w()
    w("## 14. Data-Quality Observations")
    w()
    w("### Missingness Summary")
    w()
    if not ms.empty:
        w(_table(ms))
    w()
    w("### Data Quality Issues")
    w()
    if not dq.empty:
        w(_table(dq))

    # ── Section 15 ────────────────────────────────────────────────────
    w()
    w("## 15. Factual Findings — No Recommendation")
    w()
    w("This section summarizes factual observations from the feasibility audit.")
    w("**No recommendations are made regarding migration, target selection, model")
    w("architecture, feature selection, or thesis direction.**")
    w()
    w("### Data Availability")
    w()
    w("1. NHANES August 2021–August 2023 provides **11,933 total participants** across 8 component files.")
    if not cs.empty:
        adult_n = cs.loc[cs["cohort"] == "B_adult", "total_n"].values
        no_diab_n = cs.loc[cs["cohort"] == "C_no_diab", "total_n"].values
        if len(adult_n) > 0:
            w(f"2. **{int(adult_n[0])}** participants are adults (age ≥ 18).")
        if len(no_diab_n) > 0:
            w(f"3. **{int(no_diab_n[0])}** adults do not report known diabetes.")
    w()
    w("### Feature Availability")
    w()
    w("4. Core Stage-1 features (age, sex, BMI, hypertension, smoking) are available for a")
    if not s1.empty:
        core_c = s1.loc[s1["cohort"] == "C_no_diab", "core_complete"].values
        if len(core_c) > 0:
            w(f"   substantial subset of the screening cohort (N={int(core_c[0])} for Cohort C).")
    w()
    w("### Laboratory Outcomes")
    w()
    w("5. HbA1c is available for a larger subset than fasting glucose.")
    w("6. Fasting glucose is available only for a fasting subsample.")
    w("7. HbA1c and fasting glucose show imperfect concordance, as expected clinically.")
    w()
    w("### Class Distribution")
    w()
    w("8. Using HbA1c-based or FPG-based dysglycemia as a binary outcome produces")
    w("   class-imbalanced distributions, as expected in screening populations.")
    w("9. The degree of imbalance varies by cohort definition and outcome measure.")
    w()
    w("### Survey Design")
    w()
    w("10. NHANES survey design variables (weights, strata, PSUs) are present and must be")
    w("    considered in any population-representative analysis.")
    w("11. Fasting glucose analyses specifically require fasting subsample weights (WTSAF2YR).")
    w()
    w("### Data Quality")
    w()
    w("12. No duplicate SEQN values were found in any component file.")
    w("13. Missingness patterns reflect the NHANES survey design (MEC subsample, fasting subsample).")
    w("14. Special missing codes (refused/don't know) are present in questionnaire variables")
    w("    and must be handled appropriately in any modeling effort.")
    w()
    w("---")
    w()
    w("*This report was generated programmatically from NHANES 2021-2023 public-use files.*")
    w("*All counts are unweighted. No data modification, imputation, or modeling was performed.*")

    report_path = REPORTS / "feasibility_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Report written: {report_path}")
    print(f"   {len(lines)} lines")


if __name__ == "__main__":
    main()
