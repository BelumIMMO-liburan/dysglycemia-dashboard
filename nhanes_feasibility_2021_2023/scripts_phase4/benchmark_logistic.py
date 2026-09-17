#!/usr/bin/env python3
"""
Phase 4 — Script 3/7: Logistic Regression Benchmark
Evaluates L2 regularized Logistic Regression over C in [0.01, 0.1, 1.0, 10.0]
across 5 folds on:
1. CORE-FULL
2. CORE-COMMON
3. EXPANDED-COMMON
Produces out-of-fold probability predictions for every development participant.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

import sys
sys.path.append(str(Path(__file__).resolve().parent))
from preprocessing import Preprocessor, assert_no_leakage

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "processed_phase3"
SPLITS = BASE / "splits_phase4"
PREDICTIONS = BASE / "predictions_phase4"
PREDICTIONS.mkdir(parents=True, exist_ok=True)

C_GRID = [0.01, 0.1, 1.0, 10.0]


def run_logistic_cv(df: pd.DataFrame, feature_set: str, variant_name: str) -> pd.DataFrame:
    print(f"\n--- Running Logistic Regression CV: {variant_name} ({feature_set} features, N={len(df)}) ---")
    results = []

    for c_val in C_GRID:
        config_name = f"L2_C{c_val}"
        fold_aucs = []
        oof_df = df[["SEQN", "fold", "hba1c_dysglycemia"]].copy()
        oof_df["dataset_variant"] = variant_name
        oof_df["model_family"] = "Logistic_Regression"
        oof_df["model_configuration"] = config_name
        oof_df["probability"] = np.nan

        for fold_num in range(1, 6):
            train_mask = df["fold"] != fold_num
            val_mask = df["fold"] == fold_num

            train_df = df[train_mask]
            val_df = df[val_mask]

            # Fit preprocessor strictly on train fold
            prep = Preprocessor(feature_set=feature_set)
            X_train, feat_names = prep.fit_transform(train_df)
            X_val = prep.transform(val_df)
            y_train = train_df["hba1c_dysglycemia"].values
            y_val = val_df["hba1c_dysglycemia"].values

            model = LogisticRegression(C=c_val, penalty="l2", solver="lbfgs", max_iter=1000, random_state=42)
            model.fit(X_train, y_train)

            # Predict probabilities
            val_probs = model.predict_proba(X_val)[:, 1]
            oof_df.loc[val_mask, "probability"] = val_probs

            fold_auc = roc_auc_score(y_val, val_probs)
            fold_aucs.append(fold_auc)

        mean_auc = np.mean(fold_aucs)
        std_auc = np.std(fold_aucs)
        pooled_auc = roc_auc_score(oof_df["hba1c_dysglycemia"], oof_df["probability"])
        print(f"  C={c_val:<5}: Mean CV ROC-AUC = {mean_auc:.4f} (+/- {std_auc:.4f}) | Pooled OOF ROC-AUC = {pooled_auc:.4f}")
        results.append((c_val, config_name, mean_auc, std_auc, pooled_auc, oof_df))

    # Pick best C by mean CV ROC-AUC
    results.sort(key=lambda x: x[2], reverse=True)
    best_c, best_cfg, best_mean, best_std, best_pooled, best_oof = results[0]
    print(f"  -> Best Configuration for {variant_name}: {best_cfg} (Mean ROC-AUC = {best_mean:.4f})")

    # Return OOF for all C values so full exploration is saved
    all_oof = pd.concat([r[5] for r in results], ignore_index=True)
    all_oof = all_oof.rename(columns={"hba1c_dysglycemia": "y_true"})
    return all_oof[["SEQN", "dataset_variant", "model_family", "model_configuration", "y_true", "probability", "fold"]]


def main():
    print("="*60)
    print("PHASE 4 — STEP 3: BENCHMARK LOGISTIC REGRESSION")
    print("="*60)

    # Load data and splits
    df_core = pd.read_parquet(str(PROCESSED / "analytic_core_complete.parquet"))
    df_exp = pd.read_parquet(str(PROCESSED / "analytic_expanded_complete.parquet"))
    folds_df = pd.read_csv(str(SPLITS / "development_folds.csv"))
    master_split = pd.read_csv(str(SPLITS / "master_split.csv"))

    # Filter to development partition only
    dev_seqns = set(master_split[master_split["split"] == "development"]["SEQN"])
    df_core_dev = df_core[df_core["SEQN"].isin(dev_seqns)].merge(folds_df, on="SEQN")
    df_exp_dev = df_exp[df_exp["SEQN"].isin(dev_seqns)].merge(folds_df, on="SEQN")

    # Common cohort: participants present in both datasets
    common_seqns = set(df_exp_dev["SEQN"])
    df_core_common_dev = df_core_dev[df_core_dev["SEQN"].isin(common_seqns)].copy()

    print(f"Core-Full Development:   N = {len(df_core_dev)}")
    print(f"Core-Common Development: N = {len(df_core_common_dev)}")
    print(f"Expanded-Common Dev:     N = {len(df_exp_dev)}")

    # 1. CORE-FULL
    oof_core_full = run_logistic_cv(df_core_dev, "core", "CORE_FULL")

    # 2. CORE-COMMON
    oof_core_common = run_logistic_cv(df_core_common_dev, "core", "CORE_COMMON")

    # 3. EXPANDED-COMMON
    oof_exp_common = run_logistic_cv(df_exp_dev, "expanded", "EXPANDED_COMMON")

    combined_oof = pd.concat([oof_core_full, oof_core_common, oof_exp_common], ignore_index=True)
    out_path = PREDICTIONS / "oof_logistic_regression.csv"
    combined_oof.to_csv(out_path, index=False)
    print(f"\n[OK] Logistic Regression OOF predictions written: {out_path} ({len(combined_oof):,} rows)")


if __name__ == "__main__":
    main()
