#!/usr/bin/env python3
"""
Phase 4 — Script 4/7: Generalized Additive Model (GAM) Benchmark
Evaluates LogisticGAM with s() for continuous and f() for categorical terms
across predefined smoothing lambda grid [0.01, 0.1, 1.0, 10.0] with n_splines=10
across 5 folds on:
1. CORE-FULL
2. CORE-COMMON
3. EXPANDED-COMMON
Produces out-of-fold probability predictions for every development participant.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from pygam import LogisticGAM, s, f
from sklearn.metrics import roc_auc_score

import sys
sys.path.append(str(Path(__file__).resolve().parent))
from preprocessing import Preprocessor, assert_no_leakage

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "processed_phase3"
SPLITS = BASE / "splits_phase4"
PREDICTIONS = BASE / "predictions_phase4"
PREDICTIONS.mkdir(parents=True, exist_ok=True)

LAMBDA_GRID = [0.01, 0.1, 1.0, 10.0]
N_SPLINES = 10


def build_gam_terms(feature_set: str, lam: float):
    if feature_set == "core":
        # Indices: 0: age, 1: sex, 2: bmi, 3: hypertension_history, 4: smoking_history
        terms = (
            s(0, n_splines=N_SPLINES, lam=lam) +
            f(1, lam=lam) +
            s(2, n_splines=N_SPLINES, lam=lam) +
            f(3, lam=lam) +
            f(4, lam=lam)
        )
    elif feature_set == "expanded":
        # Indices: 0: age, 1: sex, 2: bmi, 3: hypertension_history, 4: smoking_history, 5: waist_cm, 6: sedentary_minutes_day
        terms = (
            s(0, n_splines=N_SPLINES, lam=lam) +
            f(1, lam=lam) +
            s(2, n_splines=N_SPLINES, lam=lam) +
            f(3, lam=lam) +
            f(4, lam=lam) +
            s(5, n_splines=N_SPLINES, lam=lam) +
            s(6, n_splines=N_SPLINES, lam=lam)
        )
    else:
        raise ValueError(f"Unknown feature_set: {feature_set}")
    return terms


def run_gam_cv(df: pd.DataFrame, feature_set: str, variant_name: str) -> pd.DataFrame:
    print(f"\n--- Running GAM CV: {variant_name} ({feature_set} features, N={len(df)}) ---")
    results = []

    for lam in LAMBDA_GRID:
        config_name = f"GAM_splines10_lam{lam}"
        fold_aucs = []
        oof_df = df[["SEQN", "fold", "hba1c_dysglycemia"]].copy()
        oof_df["dataset_variant"] = variant_name
        oof_df["model_family"] = "GAM"
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

            # Build terms and fit LogisticGAM
            terms = build_gam_terms(feature_set, lam)
            gam = LogisticGAM(terms=terms, max_iter=200)
            gam.fit(X_train, y_train)

            # Predict probabilities
            val_probs = gam.predict_proba(X_val)
            # Clip numerical probabilities to [0, 1]
            val_probs = np.clip(val_probs, 0.0, 1.0)
            oof_df.loc[val_mask, "probability"] = val_probs

            fold_auc = roc_auc_score(y_val, val_probs)
            fold_aucs.append(fold_auc)

        mean_auc = np.mean(fold_aucs)
        std_auc = np.std(fold_aucs)
        pooled_auc = roc_auc_score(oof_df["hba1c_dysglycemia"], oof_df["probability"])
        print(f"  lam={lam:<5}: Mean CV ROC-AUC = {mean_auc:.4f} (+/- {std_auc:.4f}) | Pooled OOF ROC-AUC = {pooled_auc:.4f}")
        results.append((lam, config_name, mean_auc, std_auc, pooled_auc, oof_df))

    # Pick best config by mean CV ROC-AUC
    results.sort(key=lambda x: x[2], reverse=True)
    best_lam, best_cfg, best_mean, best_std, best_pooled, best_oof = results[0]
    print(f"  -> Best GAM Configuration for {variant_name}: {best_cfg} (Mean ROC-AUC = {best_mean:.4f})")

    # Return OOF for all configurations
    all_oof = pd.concat([r[5] for r in results], ignore_index=True)
    all_oof = all_oof.rename(columns={"hba1c_dysglycemia": "y_true"})
    return all_oof[["SEQN", "dataset_variant", "model_family", "model_configuration", "y_true", "probability", "fold"]]


def main():
    print("="*60)
    print("PHASE 4 — STEP 4: BENCHMARK GENERALIZED ADDITIVE MODEL (GAM)")
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

    # 1. CORE-FULL
    oof_core_full = run_gam_cv(df_core_dev, "core", "CORE_FULL")

    # 2. CORE-COMMON
    oof_core_common = run_gam_cv(df_core_common_dev, "core", "CORE_COMMON")

    # 3. EXPANDED-COMMON
    oof_exp_common = run_gam_cv(df_exp_dev, "expanded", "EXPANDED_COMMON")

    combined_oof = pd.concat([oof_core_full, oof_core_common, oof_exp_common], ignore_index=True)
    out_path = PREDICTIONS / "oof_gam.csv"
    combined_oof.to_csv(out_path, index=False)
    print(f"\n[OK] GAM OOF predictions written: {out_path} ({len(combined_oof):,} rows)")


if __name__ == "__main__":
    main()
