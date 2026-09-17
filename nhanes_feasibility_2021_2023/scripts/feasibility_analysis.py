#!/usr/bin/env python3
"""
NHANES Feasibility Audit — Script 3/4
Steps 4-12: Cohort feasibility, feature/lab coverage, provisional labels,
HbA1c-FPG agreement, known diabetes vs labs, class balance, survey design, data quality.
"""
import csv, sys, warnings
from pathlib import Path
import pandas as pd
import numpy as np
warnings.filterwarnings("ignore", category=FutureWarning)

BASE = Path(__file__).resolve().parent.parent
REPORTS = BASE / "reports"
PROCESSED = BASE / "processed"
REPORTS.mkdir(parents=True, exist_ok=True)

# ── helpers ───────────────────────────────────────────────────────────
def _w(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

def _pct(n, total):
    return round(n / total * 100, 2) if total > 0 else 0.0

def _valid(s):
    return int(s.notna().sum())

def _describe_age(df):
    a = df["RIDAGEYR"].dropna()
    if len(a) == 0:
        return "n/a"
    return f"mean={a.mean():.1f}, median={a.median():.0f}, min={a.min():.0f}, max={a.max():.0f}"

def _sex_dist(df):
    g = df["RIAGENDR"].dropna()
    m = int((g == 1).sum())
    f = int((g == 2).sum())
    return f"Male={m}({_pct(m,len(g)):.1f}%), Female={f}({_pct(f,len(g)):.1f}%)"

# ── NHANES special codes ──────────────────────────────────────────────
REFUSED_DK = {7, 9, 77, 99, 777, 999, 7777, 9999}

def _clean_cat(s, valid_codes):
    """Return series with refused/DK set to NaN for analytic purposes (non-destructive)."""
    out = s.copy()
    for c in REFUSED_DK:
        if c not in valid_codes:
            out = out.replace(c, np.nan)
    return out

# ── Stage-1 feature definitions ──────────────────────────────────────
CORE_FEATURES = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "BPQ020_clean", "SMQ020_clean"]
EXPANDED_FEATURES = CORE_FEATURES + ["BMXWAIST", "PAD680"]


def main():
    print("Loading merged dataset...")
    df = pd.read_parquet(str(PROCESSED / "merged_raw_preserved.parquet"))
    print(f"  {df.shape[0]} rows × {df.shape[1]} cols")

    # ── Clean categorical variables for analysis (keep originals) ─────
    df["BPQ020_clean"] = _clean_cat(df["BPQ020"], {1, 2})
    df["SMQ020_clean"] = _clean_cat(df["SMQ020"], {1, 2})
    df["SMQ040_clean"] = _clean_cat(df["SMQ040"], {1, 2, 3})
    df["DIQ010_clean"] = _clean_cat(df["DIQ010"], {1, 2, 3})
    df["DIQ160_clean"] = _clean_cat(df["DIQ160"], {1, 2})

    # ================================================================
    # STEP 4 — COHORT FEASIBILITY
    # ================================================================
    print("\n" + "="*60)
    print("STEP 4 — COHORT FEASIBILITY")
    print("="*60)

    cohorts = {}
    # Cohort A: All participants
    cohorts["A_all"] = df.copy()
    # Cohort B: Adults >= 18
    cohorts["B_adult"] = df[df["RIDAGEYR"] >= 18].copy()
    # Cohort C: Adults >= 18, no known diabetes (DIQ010 != 1)
    cohorts["C_no_diab"] = df[(df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1)].copy()
    # Cohort D: Adults >= 18, no known diabetes, also report excluding prediabetes/borderline
    cohorts["D_no_diab_no_prediab"] = df[
        (df["RIDAGEYR"] >= 18) & (~df["DIQ010_clean"].isin([1, 3]))
    ].copy()

    cohort_rows = []
    for label, cdf in cohorts.items():
        n = len(cdf)
        row = dict(
            cohort=label, total_n=n,
            age_distribution=_describe_age(cdf),
            sex_distribution=_sex_dist(cdf),
            available_bmi=_valid(cdf["BMXBMI"]),
            available_waist=_valid(cdf["BMXWAIST"]),
            available_hypertension_bpq020=_valid(cdf["BPQ020_clean"]),
            available_smoking_smq020=_valid(cdf["SMQ020_clean"]),
            available_phys_activity_pad680=_valid(cdf["PAD680"]),
            available_hba1c=_valid(cdf["LBXGH"]),
            available_fasting_glucose=_valid(cdf["LBXGLU"]),
        )
        cohort_rows.append(row)
        print(f"\n  {label}: N={n}")
        print(f"    Age: {row['age_distribution']}")
        print(f"    Sex: {row['sex_distribution']}")
        print(f"    BMI: {row['available_bmi']}, Waist: {row['available_waist']}")
        print(f"    Hypertension(BPQ020): {row['available_hypertension_bpq020']}")
        print(f"    Smoking(SMQ020): {row['available_smoking_smq020']}")
        print(f"    PhysActivity(PAD680): {row['available_phys_activity_pad680']}")
        print(f"    HbA1c: {row['available_hba1c']}, FPG: {row['available_fasting_glucose']}")

    _w(REPORTS / "cohort_summary.csv", cohort_rows)

    # ================================================================
    # STEP 5 — STAGE-1 FEATURE COVERAGE
    # ================================================================
    print("\n" + "="*60)
    print("STEP 5 — STAGE-1 FEATURE COVERAGE")
    print("="*60)

    feat_rows = []
    for label, cdf in cohorts.items():
        n = len(cdf)
        row = dict(cohort=label, total_n=n)

        # Individual feature completeness
        for feat in EXPANDED_FEATURES:
            col = feat
            row[f"valid_{feat}"] = _valid(cdf[col]) if col in cdf.columns else 0

        # Core complete
        core_mask = cdf[CORE_FEATURES].notna().all(axis=1)
        row["core_complete"] = int(core_mask.sum())
        row["core_complete_pct"] = _pct(int(core_mask.sum()), n)

        # Expanded complete
        exp_cols = [c for c in EXPANDED_FEATURES if c in cdf.columns]
        exp_mask = cdf[exp_cols].notna().all(axis=1)
        row["expanded_complete"] = int(exp_mask.sum())
        row["expanded_complete_pct"] = _pct(int(exp_mask.sum()), n)

        # Which feature causes largest reduction?
        biggest_loss_feat = ""
        biggest_loss_n = 0
        for feat in EXPANDED_FEATURES:
            if feat in cdf.columns:
                miss = int(cdf[feat].isna().sum())
                if miss > biggest_loss_n:
                    biggest_loss_n = miss
                    biggest_loss_feat = feat
        row["largest_reduction_feature"] = biggest_loss_feat
        row["largest_reduction_missing_n"] = biggest_loss_n

        feat_rows.append(row)
        print(f"\n  {label}: core_complete={row['core_complete']}/{n} "
              f"({row['core_complete_pct']}%), expanded_complete={row['expanded_complete']}/{n} "
              f"({row['expanded_complete_pct']}%)")
        print(f"    Biggest reduction: {biggest_loss_feat} (missing {biggest_loss_n})")

    _w(REPORTS / "stage1_feature_coverage.csv", feat_rows)

    # ================================================================
    # STEP 6 — LAB COVERAGE
    # ================================================================
    print("\n" + "="*60)
    print("STEP 6 — LAB COVERAGE")
    print("="*60)

    lab_rows = []
    for label, cdf in cohorts.items():
        n = len(cdf)
        hba1c_valid = cdf["LBXGH"].notna()
        fpg_valid = cdf["LBXGLU"].notna()
        wtsaf_valid = cdf["WTSAF2YR"].notna() & (cdf["WTSAF2YR"] > 0)
        fpg_and_wt = fpg_valid & wtsaf_valid
        both_labs = hba1c_valid & fpg_valid

        core_mask = cdf[CORE_FEATURES].notna().all(axis=1)
        exp_cols = [c for c in EXPANDED_FEATURES if c in cdf.columns]
        exp_mask = cdf[exp_cols].notna().all(axis=1)

        row = dict(
            cohort=label, total_n=n,
            valid_hba1c=int(hba1c_valid.sum()),
            valid_fpg=int(fpg_valid.sum()),
            valid_wtsaf2yr_gt0=int(wtsaf_valid.sum()),
            valid_fpg_and_wtsaf=int(fpg_and_wt.sum()),
            valid_both_labs=int(both_labs.sum()),
            core_plus_hba1c=int((core_mask & hba1c_valid).sum()),
            core_plus_fpg=int((core_mask & fpg_valid).sum()),
            core_plus_both_labs=int((core_mask & both_labs).sum()),
            expanded_plus_hba1c=int((exp_mask & hba1c_valid).sum()),
            expanded_plus_fpg=int((exp_mask & fpg_valid).sum()),
            expanded_plus_both_labs=int((exp_mask & both_labs).sum()),
        )
        lab_rows.append(row)
        print(f"\n  {label}: HbA1c={row['valid_hba1c']}, FPG={row['valid_fpg']}, "
              f"Both={row['valid_both_labs']}")
        print(f"    Core+HbA1c={row['core_plus_hba1c']}, Core+FPG={row['core_plus_fpg']}, "
              f"Core+Both={row['core_plus_both_labs']}")
        print(f"    Exp+HbA1c={row['expanded_plus_hba1c']}, Exp+FPG={row['expanded_plus_fpg']}, "
              f"Exp+Both={row['expanded_plus_both_labs']}")

    _w(REPORTS / "lab_coverage.csv", lab_rows)

    # ================================================================
    # STEP 7 — PROVISIONAL LAB-BASED LABELS
    # ================================================================
    print("\n" + "="*60)
    print("STEP 7 — PROVISIONAL LAB-BASED LABELS")
    print("="*60)

    # HbA1c categories
    df["hba1c_cat3"] = pd.cut(
        df["LBXGH"],
        bins=[-np.inf, 5.7, 6.5, np.inf],
        labels=["normal", "prediabetes_range", "diabetes_range"],
        right=False,
    )
    df["hba1c_binary"] = df["hba1c_cat3"].map(
        {"normal": "normal", "prediabetes_range": "dysglycemia_range",
         "diabetes_range": "dysglycemia_range"}
    )

    # FPG categories (only where valid)
    df["fpg_cat3"] = pd.cut(
        df["LBXGLU"],
        bins=[-np.inf, 100, 126, np.inf],
        labels=["normal", "prediabetes_range", "diabetes_range"],
        right=False,
    )
    df["fpg_binary"] = df["fpg_cat3"].map(
        {"normal": "normal", "prediabetes_range": "dysglycemia_range",
         "diabetes_range": "dysglycemia_range"}
    )

    # Recalculate cohorts on updated df
    cohorts_updated = {
        "A_all": df,
        "B_adult": df[df["RIDAGEYR"] >= 18],
        "C_no_diab": df[(df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1)],
        "D_no_diab_no_prediab": df[(df["RIDAGEYR"] >= 18) & (~df["DIQ010_clean"].isin([1, 3]))],
    }

    hba1c_rows = []
    fpg_rows = []
    for label, cdf in cohorts_updated.items():
        n = len(cdf)
        # HbA1c distribution
        h3 = cdf["hba1c_cat3"].value_counts(dropna=False).to_dict()
        h_miss = int(cdf["hba1c_cat3"].isna().sum())
        hba1c_rows.append(dict(
            cohort=label, total_n=n,
            hba1c_normal=int(h3.get("normal", 0)),
            hba1c_prediabetes_range=int(h3.get("prediabetes_range", 0)),
            hba1c_diabetes_range=int(h3.get("diabetes_range", 0)),
            hba1c_missing=h_miss,
            pct_normal=_pct(int(h3.get("normal", 0)), n - h_miss) if n > h_miss else 0,
            pct_prediab=_pct(int(h3.get("prediabetes_range", 0)), n - h_miss) if n > h_miss else 0,
            pct_diab=_pct(int(h3.get("diabetes_range", 0)), n - h_miss) if n > h_miss else 0,
        ))

        # FPG distribution
        f3 = cdf["fpg_cat3"].value_counts(dropna=False).to_dict()
        f_miss = int(cdf["fpg_cat3"].isna().sum())
        fpg_rows.append(dict(
            cohort=label, total_n=n,
            fpg_normal=int(f3.get("normal", 0)),
            fpg_prediabetes_range=int(f3.get("prediabetes_range", 0)),
            fpg_diabetes_range=int(f3.get("diabetes_range", 0)),
            fpg_missing=f_miss,
            pct_normal=_pct(int(f3.get("normal", 0)), n - f_miss) if n > f_miss else 0,
            pct_prediab=_pct(int(f3.get("prediabetes_range", 0)), n - f_miss) if n > f_miss else 0,
            pct_diab=_pct(int(f3.get("diabetes_range", 0)), n - f_miss) if n > f_miss else 0,
        ))

        print(f"\n  {label} (N={n}):")
        h_valid = n - h_miss
        print(f"    HbA1c (valid={h_valid}): normal={h3.get('normal',0)}, "
              f"prediab={h3.get('prediabetes_range',0)}, diab={h3.get('diabetes_range',0)}")
        f_valid = n - f_miss
        print(f"    FPG   (valid={f_valid}): normal={f3.get('normal',0)}, "
              f"prediab={f3.get('prediabetes_range',0)}, diab={f3.get('diabetes_range',0)}")

    _w(REPORTS / "hba1c_target_distribution.csv", hba1c_rows)
    _w(REPORTS / "glucose_target_distribution.csv", fpg_rows)

    # ================================================================
    # STEP 8 — HbA1c vs FPG AGREEMENT
    # ================================================================
    print("\n" + "="*60)
    print("STEP 8 — HbA1c vs FPG AGREEMENT")
    print("="*60)

    both = df.dropna(subset=["hba1c_cat3", "fpg_cat3"])
    print(f"  Participants with both HbA1c and FPG: {len(both)}")

    ct = pd.crosstab(both["hba1c_cat3"], both["fpg_cat3"], margins=True, margins_name="Total")
    print("\n  Cross-tabulation (HbA1c rows × FPG columns):")
    print(ct.to_string())

    exact_agree = int((both["hba1c_cat3"] == both["fpg_cat3"]).sum())
    disagree = len(both) - exact_agree
    hba1c_more_severe = 0
    fpg_more_severe = 0
    severity = {"normal": 0, "prediabetes_range": 1, "diabetes_range": 2}
    for _, row in both.iterrows():
        h = severity.get(row["hba1c_cat3"], -1)
        f = severity.get(row["fpg_cat3"], -1)
        if h > f:
            hba1c_more_severe += 1
        elif f > h:
            fpg_more_severe += 1

    concord_rows = [dict(
        participants_with_both=len(both),
        exact_agreement_n=exact_agree,
        exact_agreement_pct=_pct(exact_agree, len(both)),
        disagreement_n=disagree,
        disagreement_pct=_pct(disagree, len(both)),
        hba1c_more_severe=hba1c_more_severe,
        fpg_more_severe=fpg_more_severe,
    )]
    _w(REPORTS / "hba1c_glucose_concordance.csv", concord_rows)
    print(f"\n  Agreement: {exact_agree} ({_pct(exact_agree, len(both))}%)")
    print(f"  Disagreement: {disagree} ({_pct(disagree, len(both))}%)")
    print(f"  HbA1c more severe: {hba1c_more_severe}, FPG more severe: {fpg_more_severe}")

    # ================================================================
    # STEP 9 — KNOWN DIABETES vs LAB VALUES
    # ================================================================
    print("\n" + "="*60)
    print("STEP 9 — KNOWN DIABETES vs LAB VALUES")
    print("="*60)

    adults = df[df["RIDAGEYR"] >= 18].copy()
    known_diab = adults[adults["DIQ010_clean"] == 1]
    no_known_diab = adults[adults["DIQ010_clean"] != 1]

    kd_rows = []
    for group_label, gdf in [("known_diabetes", known_diab), ("no_known_diabetes", no_known_diab)]:
        n = len(gdf)
        h3 = gdf["hba1c_cat3"].value_counts(dropna=False).to_dict()
        h_miss = int(gdf["hba1c_cat3"].isna().sum())
        f3 = gdf["fpg_cat3"].value_counts(dropna=False).to_dict()
        f_miss = int(gdf["fpg_cat3"].isna().sum())

        kd_rows.append(dict(
            group=group_label, total_n=n,
            hba1c_valid=n - h_miss,
            hba1c_normal=int(h3.get("normal", 0)),
            hba1c_prediab_range=int(h3.get("prediabetes_range", 0)),
            hba1c_diab_range=int(h3.get("diabetes_range", 0)),
            hba1c_missing=h_miss,
            fpg_valid=n - f_miss,
            fpg_normal=int(f3.get("normal", 0)),
            fpg_prediab_range=int(f3.get("prediabetes_range", 0)),
            fpg_diab_range=int(f3.get("diabetes_range", 0)),
            fpg_missing=f_miss,
        ))
        print(f"\n  {group_label} (N={n}):")
        print(f"    HbA1c (valid={n-h_miss}): normal={h3.get('normal',0)}, "
              f"prediab_range={h3.get('prediabetes_range',0)}, diab_range={h3.get('diabetes_range',0)}")
        print(f"    FPG   (valid={n-f_miss}): normal={f3.get('normal',0)}, "
              f"prediab_range={f3.get('prediabetes_range',0)}, diab_range={f3.get('diabetes_range',0)}")

    _w(REPORTS / "known_diabetes_lab_summary.csv", kd_rows)

    # ================================================================
    # STEP 10 — CLASS BALANCE
    # ================================================================
    print("\n" + "="*60)
    print("STEP 10 — CLASS BALANCE")
    print("="*60)

    core_mask_all = df[CORE_FEATURES].notna().all(axis=1)
    exp_cols = [c for c in EXPANDED_FEATURES if c in df.columns]
    exp_mask_all = df[exp_cols].notna().all(axis=1)

    balance_cohorts = {
        "adults_ge18": df[df["RIDAGEYR"] >= 18],
        "adults_no_known_diab": df[(df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1)],
        "adults_no_known_diab_core_complete": df[
            (df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1) & core_mask_all
        ],
        "adults_no_known_diab_expanded_complete": df[
            (df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1) & exp_mask_all
        ],
    }

    balance_rows = []
    targets = [
        ("hba1c_binary", ["normal", "dysglycemia_range"]),
        ("fpg_binary", ["normal", "dysglycemia_range"]),
        ("hba1c_cat3", ["normal", "prediabetes_range", "diabetes_range"]),
        ("fpg_cat3", ["normal", "prediabetes_range", "diabetes_range"]),
    ]

    for coh_label, cdf in balance_cohorts.items():
        for tgt, classes in targets:
            vc = cdf[tgt].value_counts(dropna=False)
            miss = int(cdf[tgt].isna().sum())
            valid = len(cdf) - miss
            row = dict(cohort=coh_label, target=tgt, total_n=len(cdf),
                       valid_n=valid, missing_outcome=miss)
            for cls in classes:
                cnt = int(vc.get(cls, 0))
                row[f"n_{cls}"] = cnt
                row[f"pct_{cls}"] = _pct(cnt, valid)
            balance_rows.append(row)

        print(f"\n  {coh_label} (N={len(cdf)}):")
        for tgt, _ in targets:
            vc = cdf[tgt].value_counts(dropna=True)
            print(f"    {tgt}: {dict(vc)}")

    # Write as a single comprehensive CSV
    # Normalize column set
    all_cols = set()
    for r in balance_rows:
        all_cols.update(r.keys())
    for r in balance_rows:
        for c in all_cols:
            r.setdefault(c, "")

    ordered = ["cohort", "target", "total_n", "valid_n", "missing_outcome"]
    extra = sorted(all_cols - set(ordered))
    _w(REPORTS / "class_balance.csv", [{k: r.get(k, "") for k in ordered + extra} for r in balance_rows])

    # ================================================================
    # STEP 11 — SURVEY DESIGN VARIABLES (descriptive only)
    # ================================================================
    print("\n" + "="*60)
    print("STEP 11 — SURVEY DESIGN VARIABLES")
    print("="*60)

    for var in ["WTMEC2YR", "WTSAF2YR", "SDMVSTRA", "SDMVPSU"]:
        if var in df.columns:
            col = df[var]
            valid = _valid(col)
            gt0 = int((col > 0).sum()) if col.dtype in ["float64", "int64"] else "n/a"
            print(f"  {var}: valid={valid}/{len(df)}, >0={gt0}, "
                  f"min={col.min():.4g}, max={col.max():.4g}")
        else:
            print(f"  {var}: NOT FOUND")

    # ================================================================
    # STEP 12 — DATA QUALITY CHECKS
    # ================================================================
    print("\n" + "="*60)
    print("STEP 12 — DATA QUALITY CHECKS")
    print("="*60)

    quality_rows = []

    # Missingness per variable
    miss_rows = []
    key_vars = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "BMXWAIST", "BPQ020",
                "SMQ020", "SMQ040", "PAD680", "DIQ010", "LBXGH", "LBXGLU",
                "WTMEC2YR", "WTSAF2YR", "SDMVSTRA", "SDMVPSU"]
    for var in key_vars:
        if var in df.columns:
            miss = int(df[var].isna().sum())
            total = len(df)
            miss_rows.append(dict(variable=var, total=total, missing=miss,
                                  missing_pct=_pct(miss, total)))
            if _pct(miss, total) > 20:
                quality_rows.append(dict(
                    issue_type="high_missingness",
                    variable=var,
                    detail=f"{_pct(miss,total):.1f}% missing ({miss}/{total})",
                    severity="high" if _pct(miss, total) > 50 else "moderate",
                ))

    _w(REPORTS / "missingness.csv", miss_rows)

    # Duplicate SEQN
    dup_seqn = int(df["SEQN"].duplicated().sum())
    if dup_seqn > 0:
        quality_rows.append(dict(issue_type="duplicate_seqn", variable="SEQN",
                                 detail=f"{dup_seqn} duplicated SEQN values", severity="critical"))

    # Out-of-range checks
    range_checks = [
        ("RIDAGEYR", 0, 85, "Age"),
        ("BMXBMI", 10, 90, "BMI"),
        ("BMXWAIST", 30, 200, "Waist circumference"),
        ("LBXGH", 2, 20, "HbA1c"),
        ("LBXGLU", 20, 700, "Fasting glucose"),
    ]
    for var, lo, hi, label in range_checks:
        if var in df.columns:
            vals = df[var].dropna()
            below = int((vals < lo).sum())
            above = int((vals > hi).sum())
            if below > 0:
                quality_rows.append(dict(
                    issue_type="out_of_range_low", variable=var,
                    detail=f"{below} values below {lo} (min={vals.min():.2f})",
                    severity="warning",
                ))
            if above > 0:
                quality_rows.append(dict(
                    issue_type="out_of_range_high", variable=var,
                    detail=f"{above} values above {hi} (max={vals.max():.2f})",
                    severity="warning",
                ))

    # Special missing codes in questionnaire variables
    cat_checks = [
        ("BPQ020", {1, 2}),
        ("SMQ020", {1, 2}),
        ("SMQ040", {1, 2, 3}),
        ("DIQ010", {1, 2, 3}),
        ("DIQ160", {1, 2}),
    ]
    for var, valid_codes in cat_checks:
        if var in df.columns:
            vals = df[var].dropna()
            for code in [7, 9, 77, 99]:
                cnt = int((vals == code).sum())
                if cnt > 0:
                    quality_rows.append(dict(
                        issue_type="special_missing_code", variable=var,
                        detail=f"Code {code} appears {cnt} times (refused/don't know)",
                        severity="info",
                    ))

    # Sample size differences across components
    comp_sizes = {
        "DEMO_L": len(df),
        "BMX_L": _valid(df["BMXBMI"]) if "BMXBMI" in df.columns else 0,
        "BPQ_L": _valid(df["BPQ020"]) if "BPQ020" in df.columns else 0,
        "SMQ_L": _valid(df["SMQ020"]) if "SMQ020" in df.columns else 0,
        "GHB_L": _valid(df["LBXGH"]) if "LBXGH" in df.columns else 0,
        "GLU_L": _valid(df["LBXGLU"]) if "LBXGLU" in df.columns else 0,
    }
    max_diff = max(comp_sizes.values()) - min(comp_sizes.values())
    quality_rows.append(dict(
        issue_type="sample_availability_range", variable="all_components",
        detail=f"Component sizes range from {min(comp_sizes.values())} to "
               f"{max(comp_sizes.values())} (diff={max_diff}). "
               f"Details: {comp_sizes}",
        severity="info",
    ))

    _w(REPORTS / "data_quality_issues.csv", quality_rows)
    print(f"  Data quality issues found: {len(quality_rows)}")
    for r in quality_rows:
        print(f"    [{r['severity']}] {r['issue_type']}: {r['variable']} — {r['detail']}")

    # ── Save updated df with provisional labels ───────────────────────
    df.to_parquet(str(PROCESSED / "merged_raw_preserved.parquet"), index=False)

    print(f"\n[OK] All Step 4-12 outputs written to {REPORTS}")
    print("[OK] Merged dataset updated with provisional labels.")


if __name__ == "__main__":
    main()
