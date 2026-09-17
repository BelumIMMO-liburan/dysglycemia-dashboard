#!/usr/bin/env python3
"""
NHANES Feasibility Audit v2 — Script 3/4
Steps 4-12: Corrected feasibility analysis with SAS zero normalization,
Cohort E (no known dysglycemia), phlebotomy weight WTPH2YR preservation,
and analytically valid fasting glucose calculations.
"""
import csv, sys, warnings
from pathlib import Path
import pandas as pd
import numpy as np
warnings.filterwarnings("ignore", category=FutureWarning)

BASE = Path(__file__).resolve().parent.parent
REPORTS = BASE / "reports_v2"
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

REFUSED_DK = {7, 9, 77, 99, 777, 999, 7777, 9999}

def _clean_cat(s, valid_codes):
    out = s.copy()
    for c in REFUSED_DK:
        if c not in valid_codes:
            out = out.replace(c, np.nan)
    return out

# Stage-1 features
CORE_FEATURES = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "BPQ020_clean", "SMQ020_clean"]
EXPANDED_FEATURES = CORE_FEATURES + ["BMXWAIST", "PAD680"]


def main():
    print("="*60)
    print("NHANES FEASIBILITY AUDIT v2 — STEP 3: FEASIBILITY CALCULATIONS")
    print("="*60)

    print("Loading merged dataset...")
    df = pd.read_parquet(str(PROCESSED / "merged_raw_preserved.parquet"))
    print(f"  {df.shape[0]} rows × {df.shape[1]} cols")

    # Clean categorical variables for analysis
    df["BPQ020_clean"] = _clean_cat(df["BPQ020"], {1, 2})
    df["SMQ020_clean"] = _clean_cat(df["SMQ020"], {1, 2})
    df["SMQ040_clean"] = _clean_cat(df["SMQ040"], {1, 2, 3})
    df["DIQ010_clean"] = _clean_cat(df["DIQ010"], {1, 2, 3})
    df["DIQ160_clean"] = _clean_cat(df["DIQ160"], {1, 2})

    # Analytically valid lab flags
    # HbA1c: valid result and positive phlebotomy weight WTPH2YR
    df["valid_hba1c"] = df["LBXGH"].notna() & (df["WTPH2YR"] > 0)
    # Fasting glucose: valid result and positive fasting subsample weight WTSAF2YR
    df["valid_fpg"] = df["LBXGLU"].notna() & (df["WTSAF2YR"] > 0)

    # Provisional outcome categories (Feasibility labels only)
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

    df["fpg_cat3"] = np.where(
        df["valid_fpg"],
        pd.cut(
            df["LBXGLU"],
            bins=[-np.inf, 100, 126, np.inf],
            labels=["normal", "prediabetes_range", "diabetes_range"],
            right=False,
        ),
        np.nan
    )
    df["fpg_binary"] = pd.Series(df["fpg_cat3"]).map(
        {"normal": "normal", "prediabetes_range": "dysglycemia_range",
         "diabetes_range": "dysglycemia_range"}
    )

    core_mask = df[CORE_FEATURES].notna().all(axis=1)
    exp_cols = [c for c in EXPANDED_FEATURES if c in df.columns]
    exp_mask = df[exp_cols].notna().all(axis=1)
    df["core_complete"] = core_mask
    df["exp_complete"] = exp_mask

    # ================================================================
    # STEP 3.1 — COHORT E EXCLUSIONS BREAKDOWN
    # ================================================================
    adults = df[df["RIDAGEYR"] >= 18].copy()
    n_adults = len(adults)
    excl_known_diab = int((adults["DIQ010"] == 1).sum())
    excl_borderline_diab = int((adults["DIQ010"] == 3).sum())
    excl_known_prediab = int(((adults["DIQ010"] == 2) & (adults["DIQ160"] == 1)).sum())

    # Refused / DK / Missing
    diq010_missing_dk = int((adults["DIQ010"].isna() | adults["DIQ010"].isin([7, 9])).sum())
    diq160_missing_dk_among_diq2 = int(
        ((adults["DIQ010"] == 2) & (adults["DIQ160"].isna() | adults["DIQ160"].isin([7, 9]))).sum()
    )
    total_missing_dk = diq010_missing_dk + diq160_missing_dk_among_diq2

    n_cohort_e = int(((adults["DIQ010"] == 2) & (adults["DIQ160"] == 2)).sum())

    cohort_e_excl_rows = [
        dict(step="Adults Base (Age >= 18)", count=n_adults, pct_of_adults=100.0, description="All adult participants"),
        dict(step="Excluded: Known diabetes (DIQ010=1)", count=excl_known_diab, pct_of_adults=_pct(excl_known_diab, n_adults), description="Doctor told you have diabetes"),
        dict(step="Excluded: Borderline diabetes (DIQ010=3)", count=excl_borderline_diab, pct_of_adults=_pct(excl_borderline_diab, n_adults), description="Doctor told you have borderline diabetes"),
        dict(step="Excluded: Known prediabetes (DIQ160=1)", count=excl_known_prediab, pct_of_adults=_pct(excl_known_prediab, n_adults), description="Told you have prediabetes among DIQ010=2"),
        dict(step="Excluded: Missing / Refused / Don't Know on DIQ010 or DIQ160", count=total_missing_dk, pct_of_adults=_pct(total_missing_dk, n_adults), description=f"DIQ010 missing/DK={diq010_missing_dk}, DIQ160 missing/DK={diq160_missing_dk_among_diq2}"),
        dict(step="Cohort E: No Known Dysglycemia (DIQ010=2 & DIQ160=2)", count=n_cohort_e, pct_of_adults=_pct(n_cohort_e, n_adults), description="True screening population without prior recognized dysglycemia"),
    ]
    _w(REPORTS / "cohort_e_exclusions.csv", cohort_e_excl_rows)
    print("\n--- Cohort E Exclusions Breakdown ---")
    for r in cohort_e_excl_rows:
        print(f"  {r['step']}: {r['count']} ({r['pct_of_adults']}%)")

    # ================================================================
    # STEP 4 — COHORT DEFINITIONS & FEASIBILITY
    # ================================================================
    print("\n" + "="*60)
    print("STEP 4 — COHORT FEASIBILITY (A, B, C, D, E)")
    print("="*60)

    cohorts = {
        "A_all": df,
        "B_adult": df[df["RIDAGEYR"] >= 18],
        "C_no_diab": df[(df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1)],
        "D_no_diab_no_prediab": df[(df["RIDAGEYR"] >= 18) & (~df["DIQ010_clean"].isin([1, 3]))],
        "E_no_known_dysglycemia": df[(df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] == 2) & (df["DIQ160_clean"] == 2)],
    }

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
            available_hba1c=int(cdf["valid_hba1c"].sum()),
            available_fasting_glucose=int(cdf["valid_fpg"].sum()),
        )
        cohort_rows.append(row)
        print(f"\n  {label}: N={n}")
        print(f"    Age: {row['age_distribution']}")
        print(f"    Sex: {row['sex_distribution']}")
        print(f"    BMI: {row['available_bmi']}, Waist: {row['available_waist']}")
        print(f"    Hypertension(BPQ020): {row['available_hypertension_bpq020']}")
        print(f"    Smoking(SMQ020): {row['available_smoking_smq020']}")
        print(f"    PhysActivity(PAD680): {row['available_phys_activity_pad680']}")
        print(f"    Valid HbA1c: {row['available_hba1c']}, Valid FPG (analytically valid): {row['available_fasting_glucose']}")

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

        for feat in EXPANDED_FEATURES:
            row[f"valid_{feat}"] = _valid(cdf[feat]) if feat in cdf.columns else 0

        c_mask = cdf[CORE_FEATURES].notna().all(axis=1)
        row["core_complete"] = int(c_mask.sum())
        row["core_complete_pct"] = _pct(int(c_mask.sum()), n)

        e_cols = [c for c in EXPANDED_FEATURES if c in cdf.columns]
        e_mask = cdf[e_cols].notna().all(axis=1)
        row["expanded_complete"] = int(e_mask.sum())
        row["expanded_complete_pct"] = _pct(int(e_mask.sum()), n)

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
        print(f"    Largest reduction: {biggest_loss_feat} (missing {biggest_loss_n})")

    _w(REPORTS / "stage1_feature_coverage.csv", feat_rows)

    # ================================================================
    # STEP 6 — LAB COVERAGE
    # ================================================================
    print("\n" + "="*60)
    print("STEP 6 — LAB COVERAGE (Analytically Valid Labs Only)")
    print("="*60)

    lab_rows = []
    for label, cdf in cohorts.items():
        n = len(cdf)
        hba1c_v = cdf["valid_hba1c"]
        fpg_v = cdf["valid_fpg"]
        both_v = hba1c_v & fpg_v

        c_mask = cdf[CORE_FEATURES].notna().all(axis=1)
        e_cols = [c for c in EXPANDED_FEATURES if c in cdf.columns]
        e_mask = cdf[e_cols].notna().all(axis=1)

        row = dict(
            cohort=label, total_n=n,
            valid_hba1c=int(hba1c_v.sum()),
            valid_fpg_analytically_valid=int(fpg_v.sum()),
            valid_both_labs=int(both_v.sum()),
            core_plus_hba1c=int((c_mask & hba1c_v).sum()),
            core_plus_fpg=int((c_mask & fpg_v).sum()),
            core_plus_both_labs=int((c_mask & both_v).sum()),
            expanded_plus_hba1c=int((e_mask & hba1c_v).sum()),
            expanded_plus_fpg=int((e_mask & fpg_v).sum()),
            expanded_plus_both_labs=int((e_mask & both_v).sum()),
        )
        lab_rows.append(row)
        print(f"\n  {label}: Valid HbA1c={row['valid_hba1c']}, Valid FPG={row['valid_fpg_analytically_valid']}, "
              f"Both Valid={row['valid_both_labs']}")
        print(f"    Core+HbA1c={row['core_plus_hba1c']}, Core+FPG={row['core_plus_fpg']}, "
              f"Core+Both={row['core_plus_both_labs']}")
        print(f"    Exp+HbA1c={row['expanded_plus_hba1c']}, Exp+FPG={row['expanded_plus_fpg']}, "
              f"Exp+Both={row['expanded_plus_both_labs']}")

    _w(REPORTS / "lab_coverage.csv", lab_rows)

    # ================================================================
    # STEP 7 — PROVISIONAL LAB-BASED LABELS
    # ================================================================
    print("\n" + "="*60)
    print("STEP 7 — PROVISIONAL LAB-BASED LABELS (A, B, C, D, E)")
    print("="*60)

    hba1c_rows = []
    fpg_rows = []
    for label, cdf in cohorts.items():
        n = len(cdf)
        # HbA1c
        h_valid_df = cdf[cdf["valid_hba1c"]]
        h3 = h_valid_df["hba1c_cat3"].value_counts().to_dict()
        h_valid_n = len(h_valid_df)
        h_miss = n - h_valid_n
        hba1c_rows.append(dict(
            cohort=label, total_n=n, valid_n=h_valid_n, missing_n=h_miss,
            hba1c_normal=int(h3.get("normal", 0)),
            hba1c_prediabetes_range=int(h3.get("prediabetes_range", 0)),
            hba1c_diabetes_range=int(h3.get("diabetes_range", 0)),
            pct_normal=_pct(int(h3.get("normal", 0)), h_valid_n),
            pct_prediab=_pct(int(h3.get("prediabetes_range", 0)), h_valid_n),
            pct_diab=_pct(int(h3.get("diabetes_range", 0)), h_valid_n),
            dysglycemia_total=int(h3.get("prediabetes_range", 0) + h3.get("diabetes_range", 0)),
            pct_dysglycemia=_pct(int(h3.get("prediabetes_range", 0) + h3.get("diabetes_range", 0)), h_valid_n),
        ))

        # FPG (analytically valid only)
        f_valid_df = cdf[cdf["valid_fpg"]]
        f3 = f_valid_df["fpg_cat3"].value_counts().to_dict()
        f_valid_n = len(f_valid_df)
        f_miss = n - f_valid_n
        fpg_rows.append(dict(
            cohort=label, total_n=n, valid_n=f_valid_n, missing_n=f_miss,
            fpg_normal=int(f3.get("normal", 0)),
            fpg_prediabetes_range=int(f3.get("prediabetes_range", 0)),
            fpg_diabetes_range=int(f3.get("diabetes_range", 0)),
            pct_normal=_pct(int(f3.get("normal", 0)), f_valid_n),
            pct_prediab=_pct(int(f3.get("prediabetes_range", 0)), f_valid_n),
            pct_diab=_pct(int(f3.get("diabetes_range", 0)), f_valid_n),
            dysglycemia_total=int(f3.get("prediabetes_range", 0) + f3.get("diabetes_range", 0)),
            pct_dysglycemia=_pct(int(f3.get("prediabetes_range", 0) + f3.get("diabetes_range", 0)), f_valid_n),
        ))

        print(f"\n  {label} (N={n}):")
        print(f"    HbA1c (valid={h_valid_n}): normal={h3.get('normal',0)}, "
              f"prediab={h3.get('prediabetes_range',0)}, diab={h3.get('diabetes_range',0)} "
              f"| dysglycemia={int(h3.get('prediabetes_range',0)+h3.get('diabetes_range',0))}")
        print(f"    FPG   (valid={f_valid_n}): normal={f3.get('normal',0)}, "
              f"prediab={f3.get('prediabetes_range',0)}, diab={f3.get('diabetes_range',0)} "
              f"| dysglycemia={int(f3.get('prediabetes_range',0)+f3.get('diabetes_range',0))}")

    _w(REPORTS / "hba1c_target_distribution.csv", hba1c_rows)
    _w(REPORTS / "glucose_target_distribution.csv", fpg_rows)

    # ================================================================
    # STEP 8 — HbA1c vs FPG CONCORDANCE
    # ================================================================
    print("\n" + "="*60)
    print("STEP 8 — HbA1c vs FPG CONCORDANCE (Analytically Valid Both Labs)")
    print("="*60)

    both = df[df["valid_hba1c"] & df["valid_fpg"]].copy()
    n_both = len(both)
    print(f"  Participants with both analytically valid HbA1c and FPG: {n_both}")

    ct = pd.crosstab(both["hba1c_cat3"], both["fpg_cat3"], margins=True, margins_name="Total")
    print("\n  Cross-tabulation (HbA1c rows × FPG columns):")
    print(ct.to_string())

    exact_agree = int((both["hba1c_cat3"] == both["fpg_cat3"]).sum())
    disagree = n_both - exact_agree

    severity = {"normal": 0, "prediabetes_range": 1, "diabetes_range": 2}
    h_vals = np.array([severity.get(str(x), -1) for x in both["hba1c_cat3"]])
    f_vals = np.array([severity.get(str(x), -1) for x in both["fpg_cat3"]])
    hba1c_more_severe = int((h_vals > f_vals).sum())
    fpg_more_severe = int((f_vals > h_vals).sum())

    concord_rows = [dict(
        participants_with_both_valid_labs=n_both,
        exact_agreement_n=exact_agree,
        exact_agreement_pct=_pct(exact_agree, n_both),
        disagreement_n=disagree,
        disagreement_pct=_pct(disagree, n_both),
        hba1c_more_severe_n=hba1c_more_severe,
        hba1c_more_severe_pct=_pct(hba1c_more_severe, n_both),
        fpg_more_severe_n=fpg_more_severe,
        fpg_more_severe_pct=_pct(fpg_more_severe, n_both),
    )]
    _w(REPORTS / "hba1c_glucose_concordance.csv", concord_rows)
    print(f"\n  Agreement: {exact_agree} ({_pct(exact_agree, n_both)}%)")
    print(f"  Disagreement: {disagree} ({_pct(disagree, n_both)}%)")
    print(f"  HbA1c more severe: {hba1c_more_severe} ({_pct(hba1c_more_severe, n_both)}%)")
    print(f"  FPG more severe: {fpg_more_severe} ({_pct(fpg_more_severe, n_both)}%)")

    # ================================================================
    # STEP 9 — KNOWN DIABETES vs LAB VALUES
    # ================================================================
    print("\n" + "="*60)
    print("STEP 9 — KNOWN DIABETES / DYSLYCEMIA vs LAB VALUES")
    print("="*60)

    known_diab = adults[adults["DIQ010_clean"] == 1]
    no_known_diab = adults[adults["DIQ010_clean"] != 1]
    no_known_dysglycemia = adults[(adults["DIQ010_clean"] == 2) & (adults["DIQ160_clean"] == 2)]

    kd_groups = [
        ("known_diabetes (DIQ010=1)", known_diab),
        ("no_known_diabetes (DIQ010!=1)", no_known_diab),
        ("no_known_dysglycemia (DIQ010=2 & DIQ160=2)", no_known_dysglycemia),
    ]

    kd_rows = []
    for group_label, gdf in kd_groups:
        n = len(gdf)
        h_df = gdf[gdf["valid_hba1c"]]
        h3 = h_df["hba1c_cat3"].value_counts().to_dict()
        h_valid = len(h_df)
        h_miss = n - h_valid

        f_df = gdf[gdf["valid_fpg"]]
        f3 = f_df["fpg_cat3"].value_counts().to_dict()
        f_valid = len(f_df)
        f_miss = n - f_valid

        kd_rows.append(dict(
            group=group_label, total_n=n,
            hba1c_valid=h_valid,
            hba1c_normal=int(h3.get("normal", 0)),
            hba1c_prediab_range=int(h3.get("prediabetes_range", 0)),
            hba1c_diab_range=int(h3.get("diabetes_range", 0)),
            hba1c_missing=h_miss,
            fpg_valid=f_valid,
            fpg_normal=int(f3.get("normal", 0)),
            fpg_prediab_range=int(f3.get("prediabetes_range", 0)),
            fpg_diab_range=int(f3.get("diabetes_range", 0)),
            fpg_missing=f_miss,
        ))
        print(f"\n  {group_label} (N={n}):")
        print(f"    HbA1c (valid={h_valid}): normal={h3.get('normal',0)}, "
              f"prediab_range={h3.get('prediabetes_range',0)}, diab_range={h3.get('diabetes_range',0)}")
        print(f"    FPG   (valid={f_valid}): normal={f3.get('normal',0)}, "
              f"prediab_range={f3.get('prediabetes_range',0)}, diab_range={f3.get('diabetes_range',0)}")

    _w(REPORTS / "known_diabetes_lab_summary.csv", kd_rows)

    # ================================================================
    # STEP 10 — CLASS BALANCE
    # ================================================================
    print("\n" + "="*60)
    print("STEP 10 — CLASS BALANCE")
    print("="*60)

    balance_cohorts = {
        "adults_ge18": df[df["RIDAGEYR"] >= 18],
        "adults_no_known_diab": df[(df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1)],
        "adults_no_known_diab_core_complete": df[
            (df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1) & df["core_complete"]
        ],
        "adults_no_known_diab_expanded_complete": df[
            (df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] != 1) & df["exp_complete"]
        ],
        "cohort_e_no_known_dysglycemia": df[
            (df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] == 2) & (df["DIQ160_clean"] == 2)
        ],
        "cohort_e_core_complete": df[
            (df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] == 2) & (df["DIQ160_clean"] == 2) & df["core_complete"]
        ],
        "cohort_e_expanded_complete": df[
            (df["RIDAGEYR"] >= 18) & (df["DIQ010_clean"] == 2) & (df["DIQ160_clean"] == 2) & df["exp_complete"]
        ],
    }

    balance_rows = []
    targets = [
        ("hba1c_binary", ["normal", "dysglycemia_range"], "valid_hba1c"),
        ("fpg_binary", ["normal", "dysglycemia_range"], "valid_fpg"),
        ("hba1c_cat3", ["normal", "prediabetes_range", "diabetes_range"], "valid_hba1c"),
        ("fpg_cat3", ["normal", "prediabetes_range", "diabetes_range"], "valid_fpg"),
    ]

    for coh_label, cdf in balance_cohorts.items():
        for tgt, classes, valid_col in targets:
            valid_sub = cdf[cdf[valid_col]]
            vc = valid_sub[tgt].value_counts()
            valid_cnt = len(valid_sub)
            miss_cnt = len(cdf) - valid_cnt

            row = dict(cohort=coh_label, target=tgt, total_n=len(cdf),
                       valid_n=valid_cnt, missing_outcome=miss_cnt)
            for cls in classes:
                cnt = int(vc.get(cls, 0))
                row[f"n_{cls}"] = cnt
                row[f"pct_{cls}"] = _pct(cnt, valid_cnt)
            balance_rows.append(row)

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
    # STEP 11 — SURVEY DESIGN VARIABLES
    # ================================================================
    print("\n" + "="*60)
    print("STEP 11 — SURVEY DESIGN VARIABLES")
    print("="*60)

    for var in ["WTINT2YR", "WTMEC2YR", "WTPH2YR", "WTSAF2YR", "SDMVSTRA", "SDMVPSU"]:
        if var in df.columns:
            col = df[var]
            valid = _valid(col)
            gt0 = int((col > 0).sum())
            zero_cnt = int((col == 0).sum())
            print(f"  {var}: valid={valid}/{len(df)}, >0={gt0}, ==0={zero_cnt}, "
                  f"min={col.min():.4g}, max={col.max():.4g}")

    # ================================================================
    # STEP 12 — DATA QUALITY CHECKS
    # ================================================================
    print("\n" + "="*60)
    print("STEP 12 — DATA QUALITY CHECKS")
    print("="*60)

    quality_rows = []
    miss_rows = []
    key_vars = ["RIDAGEYR", "RIAGENDR", "WTINT2YR", "WTMEC2YR", "WTPH2YR", "WTSAF2YR",
                "SDMVSTRA", "SDMVPSU", "BMXBMI", "BMXWAIST", "BPQ020", "BPQ150",
                "SMQ020", "SMQ040", "PAD790Q", "PAD800", "PAD810Q", "PAD820", "PAD680",
                "DIQ010", "DIQ160", "DIQ180", "LBXGH", "LBXGLU"]

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

    # Out of range
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

    # Special missing codes
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

    # Zero weights note
    for w_col, name in [("WTMEC2YR", "MEC exam weight"), ("WTPH2YR", "Phlebotomy weight"), ("WTSAF2YR", "Fasting weight")]:
        if w_col in df.columns:
            z_cnt = int((df[w_col] == 0).sum())
            p_cnt = int((df[w_col] > 0).sum())
            quality_rows.append(dict(
                issue_type="subsample_zero_weights", variable=w_col,
                detail=f"{name} ({w_col}) has {p_cnt} positive weights and {z_cnt} zero weights (unweighted subsample non-participants)",
                severity="info",
            ))

    _w(REPORTS / "data_quality_issues.csv", quality_rows)
    print(f"  Data quality issues / observations recorded: {len(quality_rows)}")

    # Update processed parquet with flags
    df.to_parquet(str(PROCESSED / "merged_raw_preserved.parquet"), index=False)
    print(f"\n[OK] All v2 outputs written to {REPORTS}")


if __name__ == "__main__":
    main()
