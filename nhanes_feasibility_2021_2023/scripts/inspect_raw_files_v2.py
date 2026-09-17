#!/usr/bin/env python3
"""
NHANES Feasibility Audit v2 — Script 1/4
Inspect raw XPT files, verify integrity, audit target variables with SAS zero normalization
and official CDC/NCHS PAQ/weight descriptions.
"""
import csv, hashlib, sys
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "raw"
REPORTS = BASE / "reports_v2"
MANIFEST = BASE / "file_manifest.csv"
REPORTS.mkdir(parents=True, exist_ok=True)

XPT_FILES = [
    "DEMO_L.xpt", "BMX_L.xpt", "BPQ_L.xpt", "SMQ_L.xpt",
    "PAQ_L.xpt", "DIQ_L.xpt", "GHB_L.xpt", "GLU_L.xpt",
]

# Variables to audit, grouped by source file
AUDIT_VARS = {
    "DEMO_L.xpt": ["SEQN","RIDAGEYR","RIAGENDR","WTINT2YR","WTMEC2YR","SDMVSTRA","SDMVPSU"],
    "BMX_L.xpt":  ["BMXBMI","BMXWAIST"],
    "BPQ_L.xpt":  ["BPQ020","BPQ150"],
    "SMQ_L.xpt":  ["SMQ020","SMQ040"],
    "PAQ_L.xpt":  ["PAD790Q","PAD790U","PAD800","PAD810Q","PAD810U","PAD820","PAD680"],
    "DIQ_L.xpt":  ["DIQ010","DIQ160","DIQ180"],
    "GHB_L.xpt":  ["LBXGH","WTPH2YR"],
    "GLU_L.xpt":  ["LBXGLU","WTSAF2YR"],
}

CATEGORICAL = {
    "RIAGENDR","BPQ020","BPQ150","SMQ020","SMQ040",
    "PAD790U","PAD810U",
    "DIQ010","DIQ160","DIQ180",
}

DESCRIPTIONS = {
    "SEQN":     "Respondent sequence number",
    "RIDAGEYR": "Age in years at screening (0-80; 80 = 80+)",
    "RIAGENDR": "Gender (1=Male, 2=Female)",
    "WTINT2YR": "Full sample 2-year interview weight",
    "WTMEC2YR": "Full sample 2-year MEC exam weight",
    "SDMVSTRA": "Masked variance pseudo-stratum",
    "SDMVPSU":  "Masked variance pseudo-PSU",
    "BMXBMI":   "Body mass index (kg/m²)",
    "BMXWAIST": "Waist circumference (cm)",
    "BPQ020":   "Ever told you had high blood pressure (1=Yes, 2=No, 7=Refused, 9=DK)",
    "BPQ150":   "Had blood cholesterol checked in past 5 years (1=Yes, 2=No, 7=Refused, 9=DK)",
    "SMQ020":   "Smoked at least 100 cigarettes in life (1=Yes, 2=No, 7=Refused, 9=DK)",
    "SMQ040":   "Do you now smoke cigarettes (1=Every day, 2=Some days, 3=Not at all, 7=Refused, 9=DK)",
    "PAD790Q":  "Frequency of moderate leisure-time physical activity (number of days)",
    "PAD790U":  "Frequency unit for moderate leisure-time activity (D=Day, W=Week, M=Month, Y=Year)",
    "PAD800":   "Duration of moderate leisure-time activity per session (minutes)",
    "PAD810Q":  "Frequency of vigorous leisure-time physical activity (number of days)",
    "PAD810U":  "Frequency unit for vigorous leisure-time activity (D=Day, W=Week, M=Month, Y=Year)",
    "PAD820":   "Duration of vigorous leisure-time activity per session (minutes)",
    "PAD680":   "Minutes of sedentary activity per day",
    "DIQ010":   "Doctor told you have diabetes (1=Yes, 2=No, 3=Borderline, 7=Refused, 9=DK)",
    "DIQ160":   "Ever told you have prediabetes / borderline diabetes (1=Yes, 2=No, 7=Refused, 9=DK)",
    "DIQ180":   "Had blood tested past three years (1=Yes, 2=No, 7=Refused, 9=DK)",
    "LBXGH":    "Glycohemoglobin / HbA1c (%)",
    "WTPH2YR":  "2-year phlebotomy exam weight (blood analytes subsample weight)",
    "LBXGLU":   "Fasting glucose (mg/dL)",
    "WTSAF2YR": "Fasting subsample 2-year MEC weight",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_sas_zeros(series):
    """Normalize SAS float underflow (~5.3976e-79) to exact 0.0 for numeric columns."""
    if np.issubdtype(series.dtype, np.number):
        return pd.Series(np.where((series.notna()) & (series.abs() < 1e-10), 0.0, series), index=series.index)
    return series


def main():
    print("="*60)
    print("NHANES FEASIBILITY AUDIT v2 — STEP 1: FILE & VARIABLE INSPECTION")
    print("="*60)

    # ── 1. File verification ──────────────────────────────────────────
    manifest_hashes = {}
    if MANIFEST.exists():
        with open(MANIFEST, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                manifest_hashes[row["filename"]] = row["sha256"]

    verif_rows = []
    for fname in XPT_FILES:
        path = RAW / fname
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        digest = sha256(path) if exists else ""
        expected = manifest_hashes.get(fname, "")
        match = "MATCH" if digest == expected else ("MISMATCH" if expected else "NO_MANIFEST_ENTRY")
        verif_rows.append(dict(filename=fname, exists=exists, size_bytes=size,
                               sha256=digest, manifest_sha256=expected, hash_status=match))
        status = "[OK]" if match == "MATCH" else ("[WARN]" if match == "NO_MANIFEST_ENTRY" else "[FAIL]")
        print(f"{status} {fname}: {size:,} bytes  [{match}]")

    _write_csv(REPORTS / "file_verification.csv", verif_rows)

    # ── 2. Read all XPT files ─────────────────────────────────────────
    dfs = {}
    file_info_rows = []
    for fname in XPT_FILES:
        path = RAW / fname
        df = pd.read_sas(str(path), format="xport")
        # Normalize SAS zeros for all numeric columns
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = normalize_sas_zeros(df[col])
        dfs[fname] = df
        seqn_unique = df["SEQN"].nunique() if "SEQN" in df.columns else -1
        seqn_dupes = int(df["SEQN"].duplicated().sum()) if "SEQN" in df.columns else -1
        print(f"\n{fname}: {df.shape[0]} rows × {df.shape[1]} cols | SEQN unique={seqn_unique} dupes={seqn_dupes}")
        file_info_rows.append(dict(
            filename=fname, rows=df.shape[0], cols=df.shape[1],
            seqn_unique=seqn_unique, seqn_duplicates=seqn_dupes,
            columns=";".join(df.columns),
        ))
        if seqn_dupes > 0:
            print(f"  *** DUPLICATE SEQN DETECTED: {seqn_dupes} ***")
            sys.exit(1)

    # ── Weight Reconciliation Check ───────────────────────────────────
    print("\n" + "-"*50)
    print("WEIGHT NORMALIZATION & CODEBOOK RECONCILIATION:")
    glu_df = dfs["GLU_L.xpt"]
    wtsaf = glu_df["WTSAF2YR"]
    pos_wtsaf = int((wtsaf > 0).sum())
    zero_wtsaf = int((wtsaf == 0).sum())
    print(f"  GLU_L.xpt WTSAF2YR: positive={pos_wtsaf} (expected 3361), zero={zero_wtsaf} (expected 635)")
    assert pos_wtsaf == 3361 and zero_wtsaf == 635, f"WTSAF2YR mismatch! pos={pos_wtsaf}, zero={zero_wtsaf}"
    print("  [OK] WTSAF2YR matches official CDC codebook exactly (3,361 positive, 635 zero).")

    ghb_df = dfs["GHB_L.xpt"]
    wtph = ghb_df["WTPH2YR"]
    pos_wtph = int((wtph > 0).sum())
    zero_wtph = int((wtph == 0).sum())
    print(f"  GHB_L.xpt WTPH2YR: positive={pos_wtph} (expected 6750), zero={zero_wtph} (expected 449)")
    assert pos_wtph == 6750 and zero_wtph == 449, f"WTPH2YR mismatch! pos={pos_wtph}, zero={zero_wtph}"
    print("  [OK] WTPH2YR matches official CDC codebook exactly (6,750 positive, 449 zero).")
    print("-"*50)

    # ── 3. Variable-level audit ───────────────────────────────────────
    var_rows = []
    for fname, varlist in AUDIT_VARS.items():
        df = dfs[fname]
        for var in varlist:
            if var not in df.columns:
                print(f"  [WARN] {var} NOT FOUND in {fname}")
                var_rows.append(dict(
                    variable=var, source_file=fname,
                    description=DESCRIPTIONS.get(var, ""),
                    dtype="NOT_FOUND", total_n=df.shape[0],
                    valid_n=0, missing_n=df.shape[0],
                    missing_pct=100.0, min="", max="",
                    frequency_table="", notes="Variable not present in this cycle",
                ))
                continue

            col = df[var]
            total = len(col)
            missing = int(col.isna().sum())
            valid = total - missing
            mpct = round(missing / total * 100, 2) if total > 0 else 0.0
            dtype_str = str(col.dtype)
            vmin = vmax = ""
            freq_str = ""
            notes_parts = []

            if var in CATEGORICAL:
                vc = col.dropna().value_counts().sort_index()
                def _fmt_k(k):
                    if isinstance(k, bytes):
                        k = k.decode("utf-8", errors="replace").strip()
                    try:
                        f = float(k)
                        if f.is_integer():
                            return str(int(f))
                        return f"{f:.2f}"
                    except (ValueError, TypeError):
                        return str(k)
                freq_str = "; ".join(f"{_fmt_k(k)}={int(v)}" for k, v in vc.items())
                # Check for special missing codes
                for code in [7, 9, 77, 99, 777, 999]:
                    if code in vc.index or str(code) in vc.index or f"{code}.0" in vc.index:
                        cnt = vc.get(code, vc.get(str(code), 0))
                        notes_parts.append(f"special_code_{code}_present(n={int(cnt)})")
            else:
                valid_vals = col.dropna()
                if len(valid_vals) > 0:
                    vmin = f"{valid_vals.min():.4g}"
                    vmax = f"{valid_vals.max():.4g}"
                    if var in ["WTMEC2YR", "WTSAF2YR", "WTPH2YR", "WTINT2YR"]:
                        zero_cnt = int((valid_vals == 0).sum())
                        pos_cnt = int((valid_vals > 0).sum())
                        notes_parts.append(f"positive_weights={pos_cnt}; zero_weights={zero_cnt}")
                    # Flag extreme values
                    if var == "BMXBMI" and valid_vals.max() > 80:
                        notes_parts.append("extreme_BMI_above_80")
                    if var == "LBXGH" and valid_vals.max() > 20:
                        notes_parts.append("extreme_HbA1c_above_20")
                    if var == "LBXGLU" and valid_vals.max() > 600:
                        notes_parts.append("extreme_glucose_above_600")

            if mpct > 50:
                notes_parts.append("HIGH_MISSINGNESS_>50%")
            elif mpct > 30:
                notes_parts.append("HIGH_MISSINGNESS_>30%")
            elif mpct > 20:
                notes_parts.append("MODERATE_MISSINGNESS_>20%")

            var_rows.append(dict(
                variable=var, source_file=fname,
                description=DESCRIPTIONS.get(var, ""),
                dtype=dtype_str, total_n=total,
                valid_n=valid, missing_n=missing,
                missing_pct=mpct, min=vmin, max=vmax,
                frequency_table=freq_str,
                notes="; ".join(notes_parts) if notes_parts else "",
            ))
            tag = "[CAT]" if var in CATEGORICAL else "[NUM]"
            miss_flag = f" [MISS:{mpct:.1f}%]" if mpct > 5 else ""
            rng = f" range=[{vmin},{vmax}]" if vmin else ""
            print(f"  {tag} {var}: valid={valid}/{total}{miss_flag}{rng}")
            if freq_str:
                print(f"       freq: {freq_str}")

    _write_csv(REPORTS / "variable_dictionary.csv", var_rows)
    print(f"\n[OK] Outputs: {REPORTS / 'file_verification.csv'}")
    print(f"[OK] Outputs: {REPORTS / 'variable_dictionary.csv'}")


def _write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
