#!/usr/bin/env python3
"""
Phase 4 — Script 1/7: Create Locked Train/Test Split & Development Folds
Creates:
1. splits_phase4/master_split.csv (80% development, 20% final test locked)
2. splits_phase4/development_folds.csv (5-fold stratified CV within development partition)
3. splits_phase4/FINAL_TEST_LOCKED.txt (lock guarantee)
4. reports_phase4/dataset_split_summary.csv (partition statistics)
"""
import csv, sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, train_test_split

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "processed_phase3"
SPLITS = BASE / "splits_phase4"
REPORTS = BASE / "reports_phase4"
SPLITS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42


def main():
    print("="*60)
    print("PHASE 4 — STEP 1: CREATE LOCKED MASTER SPLIT & CV FOLDS")
    print("="*60)

    # Load master cohort
    core_path = PROCESSED / "analytic_core_complete.parquet"
    exp_path = PROCESSED / "analytic_expanded_complete.parquet"
    assert core_path.exists(), f"Core dataset missing: {core_path}"
    assert exp_path.exists(), f"Expanded dataset missing: {exp_path}"

    df_core = pd.read_parquet(str(core_path))
    df_exp = pd.read_parquet(str(exp_path))

    print(f"Master Core Cohort: N = {len(df_core)} (Normal: {(df_core['hba1c_dysglycemia']==0).sum()}, Dysglycemia: {(df_core['hba1c_dysglycemia']==1).sum()})")
    print(f"Expanded Cohort:    N = {len(df_exp)} (Normal: {(df_exp['hba1c_dysglycemia']==0).sum()}, Dysglycemia: {(df_exp['hba1c_dysglycemia']==1).sum()})")

    # Master 80/20 Stratified Split on SEQN
    seqns = df_core["SEQN"].values
    y = df_core["hba1c_dysglycemia"].values

    seqn_dev, seqn_test, y_dev, y_test = train_test_split(
        seqns, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )

    split_map = {s: "development" for s in seqn_dev}
    split_map.update({s: "final_test" for s in seqn_test})

    df_core["split"] = df_core["SEQN"].map(split_map)
    master_split_df = df_core[["SEQN", "split"]].copy()

    master_split_path = SPLITS / "master_split.csv"
    master_split_df.to_csv(master_split_path, index=False)
    print(f"\n[OK] Master Split written: {master_split_path}")
    print(f"     Development (80%): N = {len(seqn_dev)} (Normal: {(y_dev==0).sum()}, Dysglycemia: {(y_dev==1).sum()})")
    print(f"     Final Test (20%):  N = {len(seqn_test)} (Normal: {(y_test==0).sum()}, Dysglycemia: {(y_test==1).sum()}) [LOCKED]")

    # Create FINAL_TEST_LOCKED.txt
    lock_file = SPLITS / "FINAL_TEST_LOCKED.txt"
    lock_text = """================================================================================
FINAL TEST SET LOCK ENFORCEMENT NOTICE
================================================================================
The final test set (N = 839 participants: 645 normal, 194 dysglycemia)
defined in splits_phase4/master_split.csv is STRICTLY LOCKED.

During Phase 4 Model Development and Benchmarking:
- DO NOT evaluate candidate models on final_test.
- DO NOT calculate test ROC-AUC, PR-AUC, F1, or Brier score.
- DO NOT inspect test prediction errors.
- DO NOT tune hyperparameters or select features using test data.
- DO NOT select screening thresholds using test data.
- DO NOT generate SHAP explanations from test data.
- DO NOT report final test performance.

All model development, tuning, calibration checks, and threshold trade-off
analyses MUST be conducted exclusively using Out-Of-Fold (OOF) predictions
within the 80% development partition (N = 3,355).

FINAL TEST SET REMAINS UNTOUCHED.
================================================================================
"""
    lock_file.write_text(lock_text, encoding="utf-8")
    print(f"[OK] Lock file created: {lock_file}")

    # Stratified 5-Fold Cross-Validation on Development Partition
    dev_df = df_core[df_core["split"] == "development"].reset_index(drop=True)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    dev_df["fold"] = -1
    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(dev_df, dev_df["hba1c_dysglycemia"])):
        dev_df.loc[val_idx, "fold"] = fold_idx + 1

    folds_df = dev_df[["SEQN", "fold"]].copy()
    folds_path = SPLITS / "development_folds.csv"
    folds_df.to_csv(folds_path, index=False)
    print(f"[OK] Development Folds written: {folds_path}")

    # Check fold distribution
    for f in range(1, 6):
        f_sub = dev_df[dev_df["fold"] == f]
        pos = (f_sub["hba1c_dysglycemia"] == 1).sum()
        neg = (f_sub["hba1c_dysglycemia"] == 0).sum()
        print(f"     Fold {f}: N = {len(f_sub)} (Normal: {neg}, Dysglycemia: {pos}, Prev: {pos/len(f_sub)*100:.2f}%)")

    # Common Cohort Mapping
    common_seqns = set(df_exp["SEQN"])
    df_core["in_expanded_common"] = df_core["SEQN"].isin(common_seqns).astype(int)

    # Split Summary Table
    summary_rows = [
        dict(partition="Full Master Core Cohort", total_n=len(df_core),
             normal_n=int((df_core["hba1c_dysglycemia"]==0).sum()),
             dysglycemia_n=int((df_core["hba1c_dysglycemia"]==1).sum()),
             prevalence_pct=round((df_core["hba1c_dysglycemia"]==1).mean()*100, 2),
             status="Full sample"),
        dict(partition="Core-Full Development (80%)", total_n=len(dev_df),
             normal_n=int((dev_df["hba1c_dysglycemia"]==0).sum()),
             dysglycemia_n=int((dev_df["hba1c_dysglycemia"]==1).sum()),
             prevalence_pct=round((dev_df["hba1c_dysglycemia"]==1).mean()*100, 2),
             status="Used for 5-fold CV"),
        dict(partition="Core-Full Final Test (20%)", total_n=len(seqn_test),
             normal_n=int((y_test==0).sum()),
             dysglycemia_n=int((y_test==1).sum()),
             prevalence_pct=round((y_test==1).mean()*100, 2),
             status="LOCKED — NO EVALUATION"),
        dict(partition="Common Cohort Total (Expanded)", total_n=len(df_exp),
             normal_n=int((df_exp["hba1c_dysglycemia"]==0).sum()),
             dysglycemia_n=int((df_exp["hba1c_dysglycemia"]==1).sum()),
             prevalence_pct=round((df_exp["hba1c_dysglycemia"]==1).mean()*100, 2),
             status="Common participant subset"),
        dict(partition="Common Development (80%)",
             total_n=int((dev_df["SEQN"].isin(common_seqns)).sum()),
             normal_n=int(((dev_df["SEQN"].isin(common_seqns)) & (dev_df["hba1c_dysglycemia"]==0)).sum()),
             dysglycemia_n=int(((dev_df["SEQN"].isin(common_seqns)) & (dev_df["hba1c_dysglycemia"]==1)).sum()),
             prevalence_pct=round(dev_df.loc[dev_df["SEQN"].isin(common_seqns), "hba1c_dysglycemia"].mean()*100, 2),
             status="Used for paired Core-vs-Expanded CV"),
        dict(partition="Common Final Test (20%)",
             total_n=int((pd.Series(seqn_test).isin(common_seqns)).sum()),
             normal_n=int(((pd.Series(seqn_test).isin(common_seqns)) & (pd.Series(y_test)==0)).sum()),
             dysglycemia_n=int(((pd.Series(seqn_test).isin(common_seqns)) & (pd.Series(y_test)==1)).sum()),
             prevalence_pct=round(pd.Series(y_test)[pd.Series(seqn_test).isin(common_seqns)].mean()*100, 2),
             status="LOCKED — NO EVALUATION"),
    ]

    sum_path = REPORTS / "dataset_split_summary.csv"
    with sum_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        w.writeheader()
        w.writerows(summary_rows)
    print(f"[OK] Split Summary written: {sum_path}")


if __name__ == "__main__":
    main()
