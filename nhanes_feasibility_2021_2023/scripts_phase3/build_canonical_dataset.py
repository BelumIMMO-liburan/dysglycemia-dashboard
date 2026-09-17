#!/usr/bin/env python3
"""
Phase 3 — Script 1/2: Build Canonical NHANES Analytic Datasets
Constructs:
1. canonical_screening_population.parquet (Cohort E + valid HbA1c, N=4260)
2. analytic_core_complete.parquet (Cohort E + valid HbA1c + complete core predictors, N=4194)
3. analytic_expanded_complete.parquet (Cohort E + valid HbA1c + complete expanded predictors, N=4044)

Generates:
- reports_phase3/canonical_data_dictionary.csv
- reports_phase3/canonical_dataset_manifest.csv
"""
import csv, hashlib, sys
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "raw"
PROCESSED = BASE / "processed_phase3"
REPORTS = BASE / "reports_phase3"
PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

SCRIPT_VERSION = "v1.0-phase3"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_sas_zeros(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = np.where((df[col].notna()) & (df[col].abs() < 1e-10), 0.0, df[col])
    return df


def main():
    print("="*60)
    print("PHASE 3 — BUILD CANONICAL NHANES ANALYTIC DATASETS")
    print("="*60)

    # ── 1. Read Raw XPT Files ─────────────────────────────────────────
    raw_files = [
        "DEMO_L.xpt", "BMX_L.xpt", "BPQ_L.xpt", "SMQ_L.xpt",
        "PAQ_L.xpt", "DIQ_L.xpt", "GHB_L.xpt", "GLU_L.xpt",
    ]
    raw_hashes = {}
    for f in raw_files:
        p = RAW / f
        assert p.exists(), f"Raw file {f} missing!"
        raw_hashes[f] = sha256_file(p)
        print(f"  [RAW] {f}: {p.stat().st_size:,} bytes | SHA256={raw_hashes[f][:16]}...")

    demo = normalize_sas_zeros(pd.read_sas(str(RAW / "DEMO_L.xpt"), format="xport"))
    bmx = normalize_sas_zeros(pd.read_sas(str(RAW / "BMX_L.xpt"), format="xport"))
    bpq = normalize_sas_zeros(pd.read_sas(str(RAW / "BPQ_L.xpt"), format="xport"))
    smq = normalize_sas_zeros(pd.read_sas(str(RAW / "SMQ_L.xpt"), format="xport"))
    paq = normalize_sas_zeros(pd.read_sas(str(RAW / "PAQ_L.xpt"), format="xport"))
    diq = normalize_sas_zeros(pd.read_sas(str(RAW / "DIQ_L.xpt"), format="xport"))
    ghb = normalize_sas_zeros(pd.read_sas(str(RAW / "GHB_L.xpt"), format="xport"))
    glu = normalize_sas_zeros(pd.read_sas(str(RAW / "GLU_L.xpt"), format="xport"))

    # ── 2. Left-Join Merge onto DEMO_L ────────────────────────────────
    merged = demo.copy()
    for comp in [bmx, bpq, smq, paq, diq, ghb, glu]:
        overlap = set(merged.columns) & set(comp.columns) - {"SEQN"}
        if overlap:
            comp = comp.drop(columns=list(overlap))
        merged = merged.merge(comp, on="SEQN", how="left")

    merged = normalize_sas_zeros(merged)
    print(f"\nMerged Base: {merged.shape[0]} participants × {merged.shape[1]} raw columns")

    # ── 3. Define Canonical Variables & Recodings ──────────────────────
    df = pd.DataFrame()
    df["SEQN"] = merged["SEQN"].astype(int)

    # Cohort definition raw variables (preserved for transparency)
    df["DIQ010"] = merged["DIQ010"]
    df["DIQ160"] = merged["DIQ160"]
    df["DIQ180"] = merged["DIQ180"]

    # Stage-1 Core Predictor Candidates
    df["age"] = merged["RIDAGEYR"]
    df["sex"] = merged["RIAGENDR"]  # 1=Male, 2=Female
    df["bmi"] = merged["BMXBMI"]
    df["hypertension_history"] = merged["BPQ020"].replace({7: np.nan, 9: np.nan})  # 1=Yes, 2=No
    df["smoking_history"] = merged["SMQ020"].replace({7: np.nan, 9: np.nan})  # 1=Yes (>=100 cigs), 2=No (<100 cigs)

    # Stage-1 Expanded Candidate Predictors
    df["waist_cm"] = merged["BMXWAIST"]
    df["sedentary_minutes_day"] = merged["PAD680"].replace({7777: np.nan, 9999: np.nan})

    # Preserved raw PAQ items (un-engineered)
    for col in ["PAD790Q", "PAD790U", "PAD800", "PAD810Q", "PAD810U", "PAD820"]:
        if col in merged.columns:
            if col in ["PAD790U", "PAD810U"]:
                df[col] = merged[col].apply(lambda x: x.decode("utf-8").strip() if isinstance(x, bytes) else str(x) if pd.notna(x) else "")
            else:
                df[col] = merged[col]

    # Primary Outcome: HbA1c
    df["LBXGH"] = merged["LBXGH"]
    valid_hba1c_mask = merged["LBXGH"].notna() & (merged["WTPH2YR"] > 0)
    df["valid_hba1c"] = valid_hba1c_mask.astype(int)

    # hba1c_category (0=normal_range, 1=prediabetes_range, 2=diabetes_range)
    df["hba1c_category"] = np.where(
        valid_hba1c_mask,
        pd.cut(merged["LBXGH"], bins=[-np.inf, 5.7, 6.5, np.inf], labels=[0, 1, 2], right=False).astype(float),
        np.nan
    )

    # Primary Binary Screening Target: hba1c_dysglycemia (0=normal_range <5.7%, 1=dysglycemia_range >=5.7%)
    df["hba1c_dysglycemia"] = np.where(
        valid_hba1c_mask,
        np.where(merged["LBXGH"] < 5.7, 0, 1),
        np.nan
    )

    # Secondary Outcome: Fasting Plasma Glucose (FPG)
    df["LBXGLU"] = merged["LBXGLU"]
    valid_fpg_mask = merged["LBXGLU"].notna() & (merged["WTSAF2YR"] > 0)
    df["valid_fasting_subsample"] = valid_fpg_mask.astype(int)

    df["fpg_category"] = np.where(
        valid_fpg_mask,
        pd.cut(merged["LBXGLU"], bins=[-np.inf, 100, 126, np.inf], labels=[0, 1, 2], right=False).astype(float),
        np.nan
    )
    df["fpg_dysglycemia"] = np.where(
        valid_fpg_mask,
        np.where(merged["LBXGLU"] < 100, 0, 1),
        np.nan
    )

    # Survey Design Metadata (METADATA ONLY — NEVER STAGE-1 PREDICTORS)
    df["WTINT2YR"] = merged["WTINT2YR"]
    df["WTMEC2YR"] = merged["WTMEC2YR"]
    df["WTPH2YR"] = merged["WTPH2YR"]
    df["WTSAF2YR"] = merged["WTSAF2YR"]
    df["SDMVSTRA"] = merged["SDMVSTRA"]
    df["SDMVPSU"] = merged["SDMVPSU"]

    # ── 4. Apply Cohort E Filtering ───────────────────────────────────
    cohort_e_mask = (df["age"] >= 18) & (df["DIQ010"] == 2) & (df["DIQ160"] == 2)
    cohort_e_df = df[cohort_e_mask].copy()
    print(f"\nCohort E Population (Adults with DIQ010=2 & DIQ160=2): N = {len(cohort_e_df)}")

    # ── 5. Construct 3 Canonical Analytic Datasets ─────────────────────

    # 1. canonical_screening_population.parquet
    # Cohort E + valid HbA1c
    ds1 = cohort_e_df[cohort_e_df["valid_hba1c"] == 1].copy()
    print(f"\n1. canonical_screening_population: N = {len(ds1)} (Expected: 4260)")
    assert len(ds1) == 4260, f"Cohort E + HbA1c mismatch: {len(ds1)} != 4260"

    # 2. analytic_core_complete.parquet
    # Cohort E + valid HbA1c + complete core Stage-1 predictors
    core_cols = ["age", "sex", "bmi", "hypertension_history", "smoking_history"]
    core_mask = ds1[core_cols].notna().all(axis=1)
    ds2 = ds1[core_mask].copy()
    print(f"2. analytic_core_complete: N = {len(ds2)} (Expected: 4194)")
    assert len(ds2) == 4194, f"Core complete mismatch: {len(ds2)} != 4194"
    ds2_neg = int((ds2["hba1c_dysglycemia"] == 0).sum())
    ds2_pos = int((ds2["hba1c_dysglycemia"] == 1).sum())
    print(f"   Target: normal={ds2_neg} (expected 3224), dysglycemia={ds2_pos} (expected 970)")
    assert ds2_neg == 3224 and ds2_pos == 970, f"Target mismatch in core complete: neg={ds2_neg}, pos={ds2_pos}"

    # 3. analytic_expanded_complete.parquet
    # Cohort E + valid HbA1c + complete expanded Stage-1 predictors
    exp_cols = core_cols + ["waist_cm", "sedentary_minutes_day"]
    exp_mask = ds1[exp_cols].notna().all(axis=1)
    ds3 = ds1[exp_mask].copy()
    print(f"3. analytic_expanded_complete: N = {len(ds3)} (N=4044 with clean PAD680, N=4066 before special code removal)")
    assert len(ds3) == 4044, f"Expanded complete mismatch: {len(ds3)} != 4044"
    ds3_neg = int((ds3["hba1c_dysglycemia"] == 0).sum())
    ds3_pos = int((ds3["hba1c_dysglycemia"] == 1).sum())
    print(f"   Target: normal={ds3_neg} (expected 3106), dysglycemia={ds3_pos} (expected 938)")
    assert ds3_neg == 3106 and ds3_pos == 938, f"Target mismatch in expanded complete: neg={ds3_neg}, pos={ds3_pos}"

    # ── 6. Save Datasets to Parquet ────────────────────────────────────
    p1 = PROCESSED / "canonical_screening_population.parquet"
    p2 = PROCESSED / "analytic_core_complete.parquet"
    p3 = PROCESSED / "analytic_expanded_complete.parquet"

    ds1.to_parquet(str(p1), index=False)
    ds2.to_parquet(str(p2), index=False)
    ds3.to_parquet(str(p3), index=False)

    print(f"\n[OK] Saved: {p1} ({p1.stat().st_size:,} bytes)")
    print(f"[OK] Saved: {p2} ({p2.stat().st_size:,} bytes)")
    print(f"[OK] Saved: {p3} ({p3.stat().st_size:,} bytes)")

    # ── 7. Generate Data Dictionary ───────────────────────────────────
    dict_rows = [
        # Identifier
        dict(canonical_name="SEQN", source_variable="SEQN", source_file="DEMO_L.xpt",
             role="identifier", raw_coding="Numeric float ID", canonical_coding="Integer ID",
             missing_handling="None (never missing)", unit="dimensionless",
             included_in_core="Yes", included_in_expanded="Yes", allowed_as_predictor="No",
             notes="Respondent sequence number; primary merge and tracking key"),

        # Cohort Definition Variables
        dict(canonical_name="DIQ010", source_variable="DIQ010", source_file="DIQ_L.xpt",
             role="cohort_definition", raw_coding="1=Yes, 2=No, 3=Borderline, 7=Refused, 9=DK", canonical_coding="1, 2, 3, 7, 9",
             missing_handling="Included only if == 2", unit="category",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Self-reported diabetes diagnosis. Cohort E requires DIQ010 == 2"),
        dict(canonical_name="DIQ160", source_variable="DIQ160", source_file="DIQ_L.xpt",
             role="cohort_definition", raw_coding="1=Yes, 2=No, 7=Refused, 9=DK", canonical_coding="1, 2, 7, 9",
             missing_handling="Included only if == 2", unit="category",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Self-reported prediabetes diagnosis. Cohort E requires DIQ160 == 2"),
        dict(canonical_name="DIQ180", source_variable="DIQ180", source_file="DIQ_L.xpt",
             role="cohort_definition", raw_coding="1=Yes, 2=No, 7=Refused, 9=DK", canonical_coding="1, 2, 7, 9",
             missing_handling="Preserved as metadata", unit="category",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Had blood tested for diabetes past 3 years; retained as metadata"),

        # Stage-1 Core Predictor Candidates
        dict(canonical_name="age", source_variable="RIDAGEYR", source_file="DEMO_L.xpt",
             role="predictor_candidate", raw_coding="0-80 (80 = 80+)", canonical_coding="Continuous float (18-80)",
             missing_handling="Must be non-missing and >= 18", unit="years",
             included_in_core="Yes", included_in_expanded="Yes", allowed_as_predictor="Yes",
             notes="Age at screening interview"),
        dict(canonical_name="sex", source_variable="RIAGENDR", source_file="DEMO_L.xpt",
             role="predictor_candidate", raw_coding="1=Male, 2=Female", canonical_coding="1=Male, 2=Female",
             missing_handling="Must be non-missing", unit="category",
             included_in_core="Yes", included_in_expanded="Yes", allowed_as_predictor="Yes",
             notes="Biological sex; preserved without arbitrary ordinal scaling"),
        dict(canonical_name="bmi", source_variable="BMXBMI", source_file="BMX_L.xpt",
             role="predictor_candidate", raw_coding="Continuous float", canonical_coding="Continuous float",
             missing_handling="Missing if MEC exam skipped", unit="kg/m²",
             included_in_core="Yes", included_in_expanded="Yes", allowed_as_predictor="Yes",
             notes="Body mass index measured during MEC physical exam"),
        dict(canonical_name="hypertension_history", source_variable="BPQ020", source_file="BPQ_L.xpt",
             role="predictor_candidate", raw_coding="1=Yes, 2=No, 7=Refused, 9=DK", canonical_coding="1=Yes, 2=No",
             missing_handling="7, 9, missing recoded to NaN", unit="category",
             included_in_core="Yes", included_in_expanded="Yes", allowed_as_predictor="Yes",
             notes="Ever told by health professional had high blood pressure"),
        dict(canonical_name="smoking_history", source_variable="SMQ020", source_file="SMQ_L.xpt",
             role="predictor_candidate", raw_coding="1=Yes, 2=No, 7=Refused, 9=DK", canonical_coding="1=Yes, 2=No",
             missing_handling="7, 9, missing recoded to NaN", unit="category",
             included_in_core="Yes", included_in_expanded="Yes", allowed_as_predictor="Yes",
             notes="Smoked at least 100 cigarettes in lifetime; strictly lifetime history"),

        # Stage-1 Expanded Candidate Predictors
        dict(canonical_name="waist_cm", source_variable="BMXWAIST", source_file="BMX_L.xpt",
             role="predictor_candidate", raw_coding="Continuous float", canonical_coding="Continuous float",
             missing_handling="Missing if MEC exam skipped", unit="cm",
             included_in_core="No", included_in_expanded="Yes", allowed_as_predictor="Yes",
             notes="Waist circumference measured during MEC physical exam"),
        dict(canonical_name="sedentary_minutes_day", source_variable="PAD680", source_file="PAQ_L.xpt",
             role="predictor_candidate", raw_coding="0-1440, 7777=Refused, 9999=DK", canonical_coding="Continuous float (0-1440)",
             missing_handling="7777, 9999 recoded to NaN", unit="minutes/day",
             included_in_core="No", included_in_expanded="Yes", allowed_as_predictor="Yes",
             notes="Minutes of sedentary activity per day; special codes 7777/9999 treated as missing"),

        # Preserved Raw Physical Activity Items
        dict(canonical_name="PAD790Q", source_variable="PAD790Q", source_file="PAQ_L.xpt",
             role="predictor_candidate", raw_coding="Days/frequency, 7777=Refused, 9999=DK", canonical_coding="Raw numeric",
             missing_handling="Preserved as raw item", unit="days",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Moderate leisure physical activity frequency; un-engineered raw item"),
        dict(canonical_name="PAD790U", source_variable="PAD790U", source_file="PAQ_L.xpt",
             role="predictor_candidate", raw_coding="D=Day, W=Week, M=Month, Y=Year", canonical_coding="D, W, M, Y",
             missing_handling="Preserved as raw item", unit="unit",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Moderate leisure activity frequency unit; un-engineered raw item"),
        dict(canonical_name="PAD800", source_variable="PAD800", source_file="PAQ_L.xpt",
             role="predictor_candidate", raw_coding="Minutes per session, 7777=Refused, 9999=DK", canonical_coding="Raw numeric",
             missing_handling="Preserved as raw item", unit="minutes",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Moderate leisure activity duration per session; un-engineered raw item"),
        dict(canonical_name="PAD810Q", source_variable="PAD810Q", source_file="PAQ_L.xpt",
             role="predictor_candidate", raw_coding="Days/frequency, 7777=Refused, 9999=DK", canonical_coding="Raw numeric",
             missing_handling="Preserved as raw item", unit="days",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Vigorous leisure physical activity frequency; un-engineered raw item"),
        dict(canonical_name="PAD810U", source_variable="PAD810U", source_file="PAQ_L.xpt",
             role="predictor_candidate", raw_coding="D=Day, W=Week, M=Month, Y=Year", canonical_coding="D, W, M, Y",
             missing_handling="Preserved as raw item", unit="unit",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Vigorous leisure activity frequency unit; un-engineered raw item"),
        dict(canonical_name="PAD820", source_variable="PAD820", source_file="PAQ_L.xpt",
             role="predictor_candidate", raw_coding="Minutes per session, 7777=Refused, 9999=DK", canonical_coding="Raw numeric",
             missing_handling="Preserved as raw item", unit="minutes",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Vigorous leisure activity duration per session; un-engineered raw item"),

        # Primary Reference Outcome: HbA1c
        dict(canonical_name="LBXGH", source_variable="LBXGH", source_file="GHB_L.xpt",
             role="primary_outcome", raw_coding="Continuous float (%)", canonical_coding="Continuous float (%)",
             missing_handling="Required for primary analytic datasets", unit="%",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Glycohemoglobin (HbA1c); laboratory reference standard"),
        dict(canonical_name="valid_hba1c", source_variable="LBXGH + WTPH2YR", source_file="GHB_L.xpt",
             role="primary_outcome", raw_coding="Binary (0/1)", canonical_coding="1=Valid (LBXGH notna & WTPH2YR > 0), 0=Invalid",
             missing_handling="Must equal 1", unit="binary",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Phlebotomy-validated HbA1c indicator"),
        dict(canonical_name="hba1c_category", source_variable="LBXGH", source_file="GHB_L.xpt",
             role="primary_outcome", raw_coding="0=<5.7, 1=5.7-6.4, 2=>=6.5", canonical_coding="0=normal_range, 1=prediabetes_range, 2=diabetes_range",
             missing_handling="NaN if invalid HbA1c", unit="category",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Provisional 3-class laboratory range label"),
        dict(canonical_name="hba1c_dysglycemia", source_variable="LBXGH", source_file="GHB_L.xpt",
             role="primary_outcome", raw_coding="0=<5.7, 1=>=5.7", canonical_coding="0=normal_range, 1=dysglycemia_range",
             missing_handling="NaN if invalid HbA1c", unit="binary",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="PRIMARY BINARY SCREENING TARGET (Stage-1 reference label)"),

        # Secondary Outcome: Fasting Plasma Glucose (FPG)
        dict(canonical_name="LBXGLU", source_variable="LBXGLU", source_file="GLU_L.xpt",
             role="secondary_outcome", raw_coding="Continuous float (mg/dL)", canonical_coding="Continuous float (mg/dL)",
             missing_handling="Preserved where valid, not required for inclusion", unit="mg/dL",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Fasting plasma glucose; secondary reference standard"),
        dict(canonical_name="valid_fasting_subsample", source_variable="LBXGLU + WTSAF2YR", source_file="GLU_L.xpt",
             role="secondary_outcome", raw_coding="Binary (0/1)", canonical_coding="1=Analytically valid fasting (LBXGLU notna & WTSAF2YR > 0), 0=Invalid",
             missing_handling="Optional flag", unit="binary",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Fasting subsample weight validated glucose indicator"),
        dict(canonical_name="fpg_category", source_variable="LBXGLU", source_file="GLU_L.xpt",
             role="secondary_outcome", raw_coding="0=<100, 1=100-125, 2=>=126", canonical_coding="0=normal, 1=prediabetes_range, 2=diabetes_range",
             missing_handling="NaN if not in fasting subsample", unit="category",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Provisional 3-class fasting glucose category"),
        dict(canonical_name="fpg_dysglycemia", source_variable="LBXGLU", source_file="GLU_L.xpt",
             role="secondary_outcome", raw_coding="0=<100, 1=>=100", canonical_coding="0=normal, 1=dysglycemia_range",
             missing_handling="NaN if not in fasting subsample", unit="binary",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Secondary binary screening target for sensitivity analysis"),

        # Survey Design Metadata
        dict(canonical_name="WTINT2YR", source_variable="WTINT2YR", source_file="DEMO_L.xpt",
             role="survey_design_metadata", raw_coding="Continuous weight float", canonical_coding="Continuous weight float",
             missing_handling="Normalized float", unit="weight",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Full sample 2-year interview weight; survey metadata only"),
        dict(canonical_name="WTMEC2YR", source_variable="WTMEC2YR", source_file="DEMO_L.xpt",
             role="survey_design_metadata", raw_coding="Continuous weight float (0 if non-MEC)", canonical_coding="Continuous weight float",
             missing_handling="Normalized float (0.0 for non-MEC)", unit="weight",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Full sample 2-year MEC exam weight; survey metadata only"),
        dict(canonical_name="WTPH2YR", source_variable="WTPH2YR", source_file="GHB_L.xpt",
             role="survey_design_metadata", raw_coding="Continuous weight float (0 if non-phlebotomy)", canonical_coding="Continuous weight float",
             missing_handling="Normalized float (0.0 for non-phlebotomy)", unit="weight",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="2-year phlebotomy exam weight for HbA1c/blood analytes; survey metadata only"),
        dict(canonical_name="WTSAF2YR", source_variable="WTSAF2YR", source_file="GLU_L.xpt",
             role="survey_design_metadata", raw_coding="Continuous weight float (0 if non-fasting)", canonical_coding="Continuous weight float",
             missing_handling="Normalized float (0.0 for non-fasting)", unit="weight",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Fasting subsample 2-year MEC weight; survey metadata only"),
        dict(canonical_name="SDMVSTRA", source_variable="SDMVSTRA", source_file="DEMO_L.xpt",
             role="survey_design_metadata", raw_coding="Integer pseudo-stratum (173-187)", canonical_coding="Integer pseudo-stratum (173-187)",
             missing_handling="Never missing", unit="stratum ID",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Masked variance pseudo-stratum; survey metadata only"),
        dict(canonical_name="SDMVPSU", source_variable="SDMVPSU", source_file="DEMO_L.xpt",
             role="survey_design_metadata", raw_coding="Integer pseudo-PSU (1-2)", canonical_coding="Integer pseudo-PSU (1-2)",
             missing_handling="Never missing", unit="PSU ID",
             included_in_core="No", included_in_expanded="No", allowed_as_predictor="No",
             notes="Masked variance pseudo-PSU; survey metadata only"),
    ]

    dict_path = REPORTS / "canonical_data_dictionary.csv"
    with dict_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=dict_rows[0].keys())
        w.writeheader()
        w.writerows(dict_rows)
    print(f"[OK] Data Dictionary written: {dict_path}")

    # ── 8. Generate Dataset Manifest ───────────────────────────────────
    now_utc = datetime.now(timezone.utc).isoformat()
    manifest_rows = [
        dict(filename="canonical_screening_population.parquet",
             row_count=len(ds1), column_count=ds1.shape[1],
             target_positive_n=int((ds1["hba1c_dysglycemia"] == 1).sum()),
             target_negative_n=int((ds1["hba1c_dysglycemia"] == 0).sum()),
             SHA256=sha256_file(p1), creation_timestamp=now_utc, script_version=SCRIPT_VERSION),
        dict(filename="analytic_core_complete.parquet",
             row_count=len(ds2), column_count=ds2.shape[1],
             target_positive_n=int((ds2["hba1c_dysglycemia"] == 1).sum()),
             target_negative_n=int((ds2["hba1c_dysglycemia"] == 0).sum()),
             SHA256=sha256_file(p2), creation_timestamp=now_utc, script_version=SCRIPT_VERSION),
        dict(filename="analytic_expanded_complete.parquet",
             row_count=len(ds3), column_count=ds3.shape[1],
             target_positive_n=int((ds3["hba1c_dysglycemia"] == 1).sum()),
             target_negative_n=int((ds3["hba1c_dysglycemia"] == 0).sum()),
             SHA256=sha256_file(p3), creation_timestamp=now_utc, script_version=SCRIPT_VERSION),
    ]

    # Also record raw files in manifest
    for rfname, rhash in raw_hashes.items():
        rpath = RAW / rfname
        manifest_rows.append(dict(
            filename=f"raw/{rfname}", row_count=pd.read_sas(str(rpath), format="xport").shape[0],
            column_count=pd.read_sas(str(rpath), format="xport").shape[1],
            target_positive_n="", target_negative_n="",
            SHA256=rhash, creation_timestamp=now_utc, script_version="official_cdc_raw"
        ))

    manifest_path = REPORTS / "canonical_dataset_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=manifest_rows[0].keys())
        w.writeheader()
        w.writerows(manifest_rows)
    print(f"[OK] Manifest written: {manifest_path}")

    print("\n[OK] Build canonical datasets step completed successfully.")


if __name__ == "__main__":
    main()
