#!/usr/bin/env python3
"""
NHANES Feasibility Audit — Script 2/4
Left-join merge all component files onto DEMO_L. Report coverage.
"""
import csv, sys
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "raw"
REPORTS = BASE / "reports"
PROCESSED = BASE / "processed"
REPORTS.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

COMPONENT_FILES = [
    ("BMX_L.xpt",  "Body Measures"),
    ("BPQ_L.xpt",  "Blood Pressure / Cholesterol Questionnaire"),
    ("SMQ_L.xpt",  "Smoking Questionnaire"),
    ("PAQ_L.xpt",  "Physical Activity Questionnaire"),
    ("DIQ_L.xpt",  "Diabetes Questionnaire"),
    ("GHB_L.xpt",  "Glycohemoglobin (HbA1c)"),
    ("GLU_L.xpt",  "Fasting Glucose"),
]


def main():
    # Load base (DEMO_L)
    demo = pd.read_sas(str(RAW / "DEMO_L.xpt"), format="xport")
    print(f"Base: DEMO_L.xpt — {len(demo)} participants, SEQN unique={demo['SEQN'].nunique()}")
    assert demo["SEQN"].is_unique, "DEMO_L SEQN not unique!"

    merged = demo.copy()
    coverage_rows = []
    coverage_rows.append(dict(
        step="0_base_DEMO_L", source_file="DEMO_L.xpt",
        description="Demographics (base)",
        source_n=len(demo), matched=len(demo),
        unmatched_in_source=0, unmatched_in_base=0,
        resulting_rows=len(merged),
    ))

    attrition_rows = [dict(step="Base (DEMO_L)", n=len(demo), lost=0, pct_of_base=100.0)]

    for fname, desc in COMPONENT_FILES:
        path = RAW / fname
        comp = pd.read_sas(str(path), format="xport")
        assert comp["SEQN"].is_unique, f"{fname} SEQN not unique!"

        source_n = len(comp)
        pre_merge = len(merged)

        # Identify overlapping columns (except SEQN) to avoid _x/_y
        overlap_cols = set(merged.columns) & set(comp.columns) - {"SEQN"}
        if overlap_cols:
            print(f"  [WARN] Overlapping columns with {fname}: {overlap_cols} — keeping base version")
            comp = comp.drop(columns=list(overlap_cols))

        merged = merged.merge(comp, on="SEQN", how="left")

        matched = merged[merged["SEQN"].isin(comp["SEQN"])].shape[0]
        # How many source rows had no match in base
        unmatched_source = source_n - comp["SEQN"].isin(demo["SEQN"]).sum()
        unmatched_base = len(merged) - matched

        coverage_rows.append(dict(
            step=f"{len(coverage_rows)}_merge_{fname.replace('.xpt','')}",
            source_file=fname, description=desc,
            source_n=source_n, matched=matched,
            unmatched_in_source=int(unmatched_source),
            unmatched_in_base=unmatched_base,
            resulting_rows=len(merged),
        ))

        lost = pre_merge - len(merged)  # should be 0 with left join
        attrition_rows.append(dict(
            step=f"+ {fname}", n=len(merged),
            lost=lost, pct_of_base=round(len(merged) / len(demo) * 100, 2),
        ))

        print(f"  + {fname}: source={source_n}, matched={matched}, "
              f"unmatched_source={int(unmatched_source)}, unmatched_base={unmatched_base}, "
              f"resulting={len(merged)}")

    # Verify one row per participant
    assert merged["SEQN"].is_unique, "Merged dataset has duplicate SEQN!"
    assert len(merged) == len(demo), f"Row count changed: {len(demo)} → {len(merged)}"

    # Save
    out_path = PROCESSED / "merged_raw_preserved.parquet"
    merged.to_parquet(str(out_path), index=False)
    print(f"\n[OK] Merged dataset: {out_path} — {merged.shape[0]} rows × {merged.shape[1]} cols")

    # Write CSVs
    _write_csv(REPORTS / "merge_coverage.csv", coverage_rows)
    _write_csv(REPORTS / "attrition_table.csv", attrition_rows)
    print(f"[OK] {REPORTS / 'merge_coverage.csv'}")
    print(f"[OK] {REPORTS / 'attrition_table.csv'}")


def _write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
