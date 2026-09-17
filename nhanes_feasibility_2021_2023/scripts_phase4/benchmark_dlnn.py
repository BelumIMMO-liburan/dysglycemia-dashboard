#!/usr/bin/env python3
"""
Phase 4 — Script 5/7: Deep Learning Neural Network (DLNN) Benchmark
Evaluates intentionally small feedforward networks:
- Config A: Dense(16, relu) -> Dense(8, relu) -> Dense(1, sigmoid)
- Config B: Dense(32, relu) -> Dense(16, relu) -> Dense(1, sigmoid)
With Dropout in [0.0, 0.2]
Using Adam (lr=0.001), batch_size=32, max_epochs=200, EarlyStopping(patience=15).
Internal stratified validation split from training fold for early stopping.
Outer validation fold remains strictly untouched until prediction.
Runs on:
1. CORE-FULL
2. CORE-COMMON
3. EXPANDED-COMMON
Produces out-of-fold probability predictions for every development participant.
"""
import os, random, sys
from pathlib import Path
import pandas as pd
import numpy as np

# Set seeds and deterministic ops before TF import
os.environ["PYTHONHASHSEED"] = "42"
os.environ["TF_DETERMINISTIC_OPS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
random.seed(42)
np.random.seed(42)

import tensorflow as tf
tf.random.set_seed(42)
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

sys.path.append(str(Path(__file__).resolve().parent))
from preprocessing import Preprocessor, assert_no_leakage

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "processed_phase3"
SPLITS = BASE / "splits_phase4"
PREDICTIONS = BASE / "predictions_phase4"
PREDICTIONS.mkdir(parents=True, exist_ok=True)

CONFIGURATIONS = [
    {"name": "DLNN_16_8_drop0.0", "layers": [16, 8], "dropout": 0.0},
    {"name": "DLNN_16_8_drop0.2", "layers": [16, 8], "dropout": 0.2},
    {"name": "DLNN_32_16_drop0.0", "layers": [32, 16], "dropout": 0.0},
    {"name": "DLNN_32_16_drop0.2", "layers": [32, 16], "dropout": 0.2},
]


def build_dlnn(input_dim: int, hidden_layers: list, dropout_rate: float, seed: int = 42) -> keras.Model:
    tf.keras.utils.set_random_seed(seed)
    model = keras.Sequential()
    model.add(layers.Input(shape=(input_dim,)))

    for idx, units in enumerate(hidden_layers):
        model.add(layers.Dense(units, activation="relu", name=f"dense_{idx+1}"))
        if dropout_rate > 0.0:
            model.add(layers.Dropout(dropout_rate, name=f"dropout_{idx+1}"))

    model.add(layers.Dense(1, activation="sigmoid", name="output"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["AUC"],
    )
    return model


def run_dlnn_cv(df: pd.DataFrame, feature_set: str, variant_name: str) -> pd.DataFrame:
    print(f"\n--- Running DLNN CV: {variant_name} ({feature_set} features, N={len(df)}) ---")
    results = []

    for cfg in CONFIGURATIONS:
        config_name = cfg["name"]
        h_layers = cfg["layers"]
        drop_rate = cfg["dropout"]

        fold_aucs = []
        oof_df = df[["SEQN", "fold", "hba1c_dysglycemia"]].copy()
        oof_df["dataset_variant"] = variant_name
        oof_df["model_family"] = "DLNN"
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

            # Internal stratified validation split for early stopping (outer validation strictly untouched!)
            X_sub_train, X_int_val, y_sub_train, y_int_val = train_test_split(
                X_train, y_train, test_size=0.15, random_state=42 + fold_num, stratify=y_train
            )

            # Build and train model
            model_seed = 42 + fold_num * 10
            model = build_dlnn(
                input_dim=X_train.shape[1],
                hidden_layers=h_layers,
                dropout_rate=drop_rate,
                seed=model_seed,
            )

            early_stop = keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=15,
                restore_best_weights=True,
                verbose=0,
            )

            model.fit(
                X_sub_train,
                y_sub_train,
                validation_data=(X_int_val, y_int_val),
                epochs=200,
                batch_size=32,
                callbacks=[early_stop],
                verbose=0,
            )

            # Predict on untouched outer validation fold
            val_probs = model.predict(X_val, verbose=0).flatten()
            oof_df.loc[val_mask, "probability"] = val_probs

            fold_auc = roc_auc_score(y_val, val_probs)
            fold_aucs.append(fold_auc)

        mean_auc = np.mean(fold_aucs)
        std_auc = np.std(fold_aucs)
        pooled_auc = roc_auc_score(oof_df["hba1c_dysglycemia"], oof_df["probability"])
        print(f"  {config_name:<20}: Mean CV ROC-AUC = {mean_auc:.4f} (+/- {std_auc:.4f}) | Pooled OOF ROC-AUC = {pooled_auc:.4f}")
        results.append((config_name, mean_auc, std_auc, pooled_auc, oof_df))

    # Pick best DLNN configuration by mean CV ROC-AUC
    results.sort(key=lambda x: x[1], reverse=True)
    best_cfg, best_mean, best_std, best_pooled, best_oof = results[0]
    print(f"  -> Best DLNN Configuration for {variant_name}: {best_cfg} (Mean ROC-AUC = {best_mean:.4f})")

    # Return OOF for all configurations
    all_oof = pd.concat([r[4] for r in results], ignore_index=True)
    all_oof = all_oof.rename(columns={"hba1c_dysglycemia": "y_true"})
    return all_oof[["SEQN", "dataset_variant", "model_family", "model_configuration", "y_true", "probability", "fold"]]


def main():
    print("="*60)
    print("PHASE 4 — STEP 5: BENCHMARK DEEP LEARNING NEURAL NETWORKS (DLNN)")
    print(f"TensorFlow Version: {tf.__version__} | Keras Version: {keras.__version__}")
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
    oof_core_full = run_dlnn_cv(df_core_dev, "core", "CORE_FULL")

    # 2. CORE-COMMON
    oof_core_common = run_dlnn_cv(df_core_common_dev, "core", "CORE_COMMON")

    # 3. EXPANDED-COMMON
    oof_exp_common = run_dlnn_cv(df_exp_dev, "expanded", "EXPANDED_COMMON")

    combined_oof = pd.concat([oof_core_full, oof_core_common, oof_exp_common], ignore_index=True)
    out_path = PREDICTIONS / "oof_dlnn.csv"
    combined_oof.to_csv(out_path, index=False)
    print(f"\n[OK] DLNN OOF predictions written: {out_path} ({len(combined_oof):,} rows)")


if __name__ == "__main__":
    main()
