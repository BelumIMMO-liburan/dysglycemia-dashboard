#!/usr/bin/env python3
"""
Phase 5 — Step 2/3: Bootstrap Uncertainty & Paired Model Comparison
Computes 2,000 participant-level bootstrap resamples on frozen final-test predictions.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix
)

BASE = Path(__file__).resolve().parent.parent
PRED_PATH = BASE / "predictions_phase5" / "final_test_predictions.csv"
REPORTS_DIR = BASE / "reports_phase5"

N_BOOTSTRAP = 2000
RANDOM_SEED = 42

FROZEN_THRESHOLDS = {
    "GAM": 0.1389,
    "Logistic_Regression": 0.1389,
    "DLNN": 0.1419,
}


def calc_metrics_for_eval(y_true, y_prob, threshold):
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    roc = roc_auc_score(y_true, y_prob)
    pr = average_precision_score(y_true, y_prob)
    brier = brier_score_loss(y_true, y_prob)
    return {
        "roc_auc": roc, "pr_auc": pr, "brier": brier,
        "sensitivity": sens, "specificity": spec, "ppv": ppv, "npv": npv
    }


def main():
    print("="*70)
    print(f"PHASE 5: BOOTSTRAP UNCERTAINTY & PAIRED COMPARISON (N={N_BOOTSTRAP})")
    print("="*70)

    assert PRED_PATH.exists(), f"Missing prediction file: {PRED_PATH}"
    df_preds = pd.read_csv(PRED_PATH)
    n = len(df_preds)
    print(f"Loaded frozen predictions: N = {n} final-test participants.")

    y_true = df_preds["y_true"].values
    probs = {
        "GAM": df_preds["gam_probability"].values,
        "Logistic_Regression": df_preds["logistic_probability"].values,
        "DLNN": df_preds["dlnn_probability"].values,
    }

    # Point estimates
    point_estimates = {}
    for m_name, p_vec in probs.items():
        t = FROZEN_THRESHOLDS[m_name]
        point_estimates[m_name] = calc_metrics_for_eval(y_true, p_vec, t)

    # Bootstrap
    np.random.seed(RANDOM_SEED)
    boot_results = {m: {k: [] for k in point_estimates[m].keys()} for m in probs.keys()}

    # Paired differences: GAM - Logistic, GAM - DLNN
    paired_keys = ["roc_auc", "pr_auc", "brier", "sensitivity", "specificity"]
    boot_paired = {
        "GAM_minus_Logistic": {k: [] for k in paired_keys},
        "GAM_minus_DLNN": {k: [] for k in paired_keys},
    }

    invalid_replicates = 0

    for b in range(N_BOOTSTRAP):
        idx = np.random.choice(n, size=n, replace=True)
        y_b = y_true[idx]

        # Check validity (must contain both classes)
        if len(np.unique(y_b)) < 2:
            invalid_replicates += 1
            continue

        b_metrics = {}
        for m_name, p_vec in probs.items():
            t = FROZEN_THRESHOLDS[m_name]
            p_b = p_vec[idx]
            m_res = calc_metrics_for_eval(y_b, p_b, t)
            b_metrics[m_name] = m_res
            for k, val in m_res.items():
                boot_results[m_name][k].append(val)

        # Paired differences
        for k in paired_keys:
            diff_gl = b_metrics["GAM"][k] - b_metrics["Logistic_Regression"][k]
            diff_gd = b_metrics["GAM"][k] - b_metrics["DLNN"][k]
            boot_paired["GAM_minus_Logistic"][k].append(diff_gl)
            boot_paired["GAM_minus_DLNN"][k].append(diff_gd)

    print(f"Completed {N_BOOTSTRAP} iterations. Invalid replicates excluded: {invalid_replicates}.")

    # Compile Individual Model CIs
    ci_rows = []
    metric_order = ["roc_auc", "pr_auc", "brier", "sensitivity", "specificity", "ppv", "npv"]
    for m_name in probs.keys():
        for k in metric_order:
            pe = point_estimates[m_name][k]
            dist = boot_results[m_name][k]
            ci_low = np.percentile(dist, 2.5)
            ci_high = np.percentile(dist, 97.5)
            ci_rows.append({
                "model_family": m_name,
                "metric": k,
                "point_estimate": round(pe, 4),
                "ci_95": f"[{ci_low:.4f}, {ci_high:.4f}]",
                "ci_lower": round(ci_low, 4),
                "ci_upper": round(ci_high, 4),
                "invalid_replicates_excluded": invalid_replicates
            })

    ci_df = pd.DataFrame(ci_rows)
    ci_path = REPORTS_DIR / "final_test_bootstrap_ci.csv"
    ci_df.to_csv(ci_path, index=False)
    print(f"[OK] Saved: {ci_path}")

    # Compile Paired Model Comparison CIs
    paired_rows = []
    pairs = [
        ("GAM vs Logistic_Regression", "GAM_minus_Logistic", "GAM", "Logistic_Regression"),
        ("GAM vs DLNN", "GAM_minus_DLNN", "GAM", "DLNN"),
    ]

    for label, pair_key, m1, m2 in pairs:
        for k in paired_keys:
            pe_diff = point_estimates[m1][k] - point_estimates[m2][k]
            dist = boot_paired[pair_key][k]
            ci_low = np.percentile(dist, 2.5)
            ci_high = np.percentile(dist, 97.5)
            paired_rows.append({
                "comparison": label,
                "model_1": m1,
                "model_2": m2,
                "metric": f"delta_{k}",
                "point_difference": round(pe_diff, 4),
                "ci_95": f"[{ci_low:.4f}, {ci_high:.4f}]",
                "ci_lower": round(ci_low, 4),
                "ci_upper": round(ci_high, 4),
                "invalid_replicates_excluded": invalid_replicates
            })

    paired_df = pd.DataFrame(paired_rows)
    paired_path = REPORTS_DIR / "final_test_paired_model_comparisons.csv"
    paired_df.to_csv(paired_path, index=False)
    print(f"[OK] Saved: {paired_path}")


if __name__ == "__main__":
    main()
