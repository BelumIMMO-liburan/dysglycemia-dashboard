#!/usr/bin/env python3
"""
Phase 4 — Script 6/7: Out-of-Fold Evaluation, Calibration, Thresholds & Plotting
Computes:
1. predictions_phase4/oof_predictions.csv (master pooled predictions)
2. reports_phase4/cv_model_summary.csv & cv_fold_metrics.csv
3. reports_phase4/core_vs_expanded_common_cohort.csv (fair paired comparison)
4. reports_phase4/calibration_summary.csv
5. reports_phase4/threshold_tradeoffs.csv & screening_efficiency.csv
6. plots_phase4/ (ROC, PR, Calibration, Threshold curves)
"""
import csv, sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    roc_curve, precision_recall_curve, confusion_matrix
)
from sklearn.calibration import calibration_curve

BASE = Path(__file__).resolve().parent.parent
PREDICTIONS = BASE / "predictions_phase4"
REPORTS = BASE / "reports_phase4"
PLOTS = BASE / "plots_phase4"
REPORTS.mkdir(parents=True, exist_ok=True)
PLOTS.mkdir(parents=True, exist_ok=True)


def compute_binary_metrics_at_threshold(y_true, y_prob, threshold=0.50):
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    f1 = 2 * (ppv * sens) / (ppv + sens) if (ppv + sens) > 0 else 0.0
    bal_acc = (sens + spec) / 2.0
    pos_rate = (tp + fp) / len(y_true)
    neg_rate = (tn + fn) / len(y_true)
    nnt = 1.0 / ppv if ppv > 0 else np.nan
    return {
        "threshold": threshold, "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
        "sensitivity": sens, "specificity": spec, "ppv": ppv, "npv": npv,
        "f1": f1, "balanced_accuracy": bal_acc,
        "predicted_positive_rate": pos_rate, "predicted_negative_rate": neg_rate,
        "nnt": nnt,
    }


def find_operating_point(y_true, y_prob, target_sens):
    """Find threshold that achieves at least target_sens (or closest)."""
    thresholds = np.linspace(0.01, 0.99, 500)
    best_m = None
    best_diff = float("inf")
    for t in thresholds:
        m = compute_binary_metrics_at_threshold(y_true, y_prob, threshold=t)
        if m["sensitivity"] >= target_sens:
            diff = m["sensitivity"] - target_sens
            if diff < best_diff:
                best_diff = diff
                best_m = m
    if best_m is None:
        best_m = compute_binary_metrics_at_threshold(y_true, y_prob, threshold=0.01)
    return best_m


def main():
    print("="*60)
    print("PHASE 4 — STEP 6: EVALUATE OOF PREDICTIONS, CALIBRATION & THRESHOLDS")
    print("="*60)

    # 1. Combine all OOF predictions
    f_log = PREDICTIONS / "oof_logistic_regression.csv"
    f_gam = PREDICTIONS / "oof_gam.csv"
    f_dlnn = PREDICTIONS / "oof_dlnn.csv"

    assert f_log.exists(), f"Missing {f_log}"
    assert f_gam.exists(), f"Missing {f_gam}"
    assert f_dlnn.exists(), f"Missing {f_dlnn}"

    df_log = pd.read_csv(f_log)
    df_gam = pd.read_csv(f_gam)
    df_dlnn = pd.read_csv(f_dlnn)

    master_oof = pd.concat([df_log, df_gam, df_dlnn], ignore_index=True)
    master_oof_path = PREDICTIONS / "oof_predictions.csv"
    master_oof.to_csv(master_oof_path, index=False)
    print(f"[OK] Master OOF predictions saved: {master_oof_path} ({len(master_oof):,} rows)")

    # 2. Fold Metrics and Model Summary
    fold_metric_rows = []
    summary_rows = []

    groups = master_oof.groupby(["dataset_variant", "model_family", "model_configuration"])

    for (variant, family, config), group in groups:
        y_pooled = group["y_true"].values
        p_pooled = group["probability"].values

        pooled_auc = roc_auc_score(y_pooled, p_pooled)
        pooled_pr_auc = average_precision_score(y_pooled, p_pooled)
        pooled_brier = brier_score_loss(y_pooled, p_pooled)
        pooled_thresh = compute_binary_metrics_at_threshold(y_pooled, p_pooled, 0.50)

        fold_aucs, fold_praucs, fold_briers = [], [], []
        fold_sens, fold_specs, fold_f1s = [], [], []

        for fold_num in range(1, 6):
            f_sub = group[group["fold"] == fold_num]
            y_f = f_sub["y_true"].values
            p_f = f_sub["probability"].values

            f_auc = roc_auc_score(y_f, p_f)
            f_prauc = average_precision_score(y_f, p_f)
            f_brier = brier_score_loss(y_f, p_f)
            f_th = compute_binary_metrics_at_threshold(y_f, p_f, 0.50)

            fold_aucs.append(f_auc)
            fold_praucs.append(f_prauc)
            fold_briers.append(f_brier)
            fold_sens.append(f_th["sensitivity"])
            fold_specs.append(f_th["specificity"])
            fold_f1s.append(f_th["f1"])

            fold_metric_rows.append(dict(
                dataset_variant=variant, model_family=family, model_configuration=config,
                fold=fold_num, n=len(f_sub),
                roc_auc=round(f_auc, 4), pr_auc=round(f_prauc, 4), brier_score=round(f_brier, 4),
                sensitivity_05=round(f_th["sensitivity"], 4), specificity_05=round(f_th["specificity"], 4),
                ppv_05=round(f_th["ppv"], 4), npv_05=round(f_th["npv"], 4), f1_05=round(f_th["f1"], 4),
            ))

        summary_rows.append(dict(
            dataset_variant=variant, model_family=family, model_configuration=config,
            n_dev=len(group),
            mean_cv_roc_auc=round(np.mean(fold_aucs), 4), std_cv_roc_auc=round(np.std(fold_aucs), 4),
            pooled_oof_roc_auc=round(pooled_auc, 4),
            mean_cv_pr_auc=round(np.mean(fold_praucs), 4), std_cv_pr_auc=round(np.std(fold_praucs), 4),
            pooled_oof_pr_auc=round(pooled_pr_auc, 4),
            pooled_brier_score=round(pooled_brier, 4),
            sensitivity_at_05=round(pooled_thresh["sensitivity"], 4),
            specificity_at_05=round(pooled_thresh["specificity"], 4),
            ppv_at_05=round(pooled_thresh["ppv"], 4),
            npv_at_05=round(pooled_thresh["npv"], 4),
            f1_at_05=round(pooled_thresh["f1"], 4),
            balanced_acc_at_05=round(pooled_thresh["balanced_accuracy"], 4),
            tp=pooled_thresh["tp"], fp=pooled_thresh["fp"], tn=pooled_thresh["tn"], fn=pooled_thresh["fn"],
        ))

    # Save summary and fold CSVs
    sum_df = pd.DataFrame(summary_rows).sort_values(by=["dataset_variant", "pooled_oof_roc_auc"], ascending=[True, False])
    sum_df.to_csv(REPORTS / "cv_model_summary.csv", index=False)
    pd.DataFrame(fold_metric_rows).to_csv(REPORTS / "cv_fold_metrics.csv", index=False)
    print(f"[OK] Saved: {REPORTS / 'cv_model_summary.csv'}")
    print(f"[OK] Saved: {REPORTS / 'cv_fold_metrics.csv'}")

    # 3. Fair Core vs Expanded Paired Comparison
    # Identify best configuration per model family on CORE_COMMON and EXPANDED_COMMON
    common_sub = sum_df[sum_df["dataset_variant"].isin(["CORE_COMMON", "EXPANDED_COMMON"])].copy()
    paired_rows = []

    for fam in ["Logistic_Regression", "GAM", "DLNN"]:
        c_fam = common_sub[(common_sub["model_family"] == fam) & (common_sub["dataset_variant"] == "CORE_COMMON")].sort_values(by="pooled_oof_roc_auc", ascending=False).iloc[0]
        e_fam = common_sub[(common_sub["model_family"] == fam) & (common_sub["dataset_variant"] == "EXPANDED_COMMON")].sort_values(by="pooled_oof_roc_auc", ascending=False).iloc[0]

        delta_auc = e_fam["pooled_oof_roc_auc"] - c_fam["pooled_oof_roc_auc"]
        delta_prauc = e_fam["pooled_oof_pr_auc"] - c_fam["pooled_oof_pr_auc"]
        delta_brier = e_fam["pooled_brier_score"] - c_fam["pooled_brier_score"]

        paired_rows.append(dict(
            model_family=fam,
            common_cohort_n=c_fam["n_dev"],
            core_best_config=c_fam["model_configuration"],
            core_roc_auc=c_fam["pooled_oof_roc_auc"],
            core_pr_auc=c_fam["pooled_oof_pr_auc"],
            core_brier=c_fam["pooled_brier_score"],
            expanded_best_config=e_fam["model_configuration"],
            expanded_roc_auc=e_fam["pooled_oof_roc_auc"],
            expanded_pr_auc=e_fam["pooled_oof_pr_auc"],
            expanded_brier=e_fam["pooled_brier_score"],
            delta_roc_auc=round(delta_auc, 4),
            delta_pr_auc=round(delta_prauc, 4),
            delta_brier_score=round(delta_brier, 4),
        ))

    paired_df = pd.DataFrame(paired_rows)
    paired_df.to_csv(REPORTS / "core_vs_expanded_common_cohort.csv", index=False)
    print(f"[OK] Saved: {REPORTS / 'core_vs_expanded_common_cohort.csv'}")

    # 4. Calibration Analysis & Summary
    calib_rows = []
    for (variant, family, config), group in groups:
        # Check primary best models only for table brevity, or all
        y_true = group["y_true"].values
        y_prob = group["probability"].values
        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy="uniform")
        brier = brier_score_loss(y_true, y_prob)

        for b_idx, (pt, pp) in enumerate(zip(prob_true, prob_pred)):
            calib_rows.append(dict(
                dataset_variant=variant, model_family=family, model_configuration=config,
                bin_idx=b_idx + 1, mean_predicted_prob=round(pp, 4), fraction_of_positives=round(pt, 4),
                brier_score=round(brier, 4)
            ))

    pd.DataFrame(calib_rows).to_csv(REPORTS / "calibration_summary.csv", index=False)
    print(f"[OK] Saved: {REPORTS / 'calibration_summary.csv'}")

    # 5. Screening Threshold Exploration & Efficiency Analysis
    # Evaluate representative best configuration per variant & family
    thresh_targets = [0.80, 0.85, 0.90, 0.95]
    thresh_rows = []
    efficiency_rows = []

    # Pick representative best configs
    rep_configs = [
        ("CORE_FULL", "Logistic_Regression", "L2_C10.0"),
        ("CORE_FULL", "GAM", "GAM_splines10_lam10.0"),
        ("CORE_FULL", "DLNN", "DLNN_16_8_drop0.0"),
        ("CORE_COMMON", "Logistic_Regression", "L2_C10.0"),
        ("EXPANDED_COMMON", "Logistic_Regression", "L2_C10.0"),
        ("EXPANDED_COMMON", "GAM", "GAM_splines10_lam10.0"),
        ("EXPANDED_COMMON", "DLNN", "DLNN_16_8_drop0.0"),
    ]

    for variant, family, cfg in rep_configs:
        sub_grp = master_oof[(master_oof["dataset_variant"] == variant) &
                             (master_oof["model_family"] == family) &
                             (master_oof["model_configuration"] == cfg)]
        if sub_grp.empty:
            continue
        y_true = sub_grp["y_true"].values
        y_prob = sub_grp["probability"].values
        total_pos = (y_true == 1).sum()
        total_pop = len(y_true)

        for target_s in thresh_targets:
            m = find_operating_point(y_true, y_prob, target_s)
            thresh_rows.append(dict(
                dataset_variant=variant, model_family=family, model_configuration=cfg,
                target_sensitivity=target_s,
                achieved_threshold=round(m["threshold"], 4),
                sensitivity=round(m["sensitivity"], 4),
                specificity=round(m["specificity"], 4),
                ppv=round(m["ppv"], 4), npv=round(m["npv"], 4), f1=round(m["f1"], 4),
                predicted_positive_rate=round(m["predicted_positive_rate"], 4),
                predicted_negative_rate=round(m["predicted_negative_rate"], 4),
                nnt_screening=round(m["nnt"], 2) if not np.isnan(m["nnt"]) else "n/a",
            ))

            referred_pct = round(m["predicted_positive_rate"] * 100, 2)
            not_referred_pct = round(m["predicted_negative_rate"] * 100, 2)
            captured_pct = round(m["tp"] / total_pos * 100, 2)
            missed_pct = round(m["fn"] / total_pos * 100, 2)

            efficiency_rows.append(dict(
                dataset_variant=variant, model_family=family, model_configuration=cfg,
                target_sensitivity=target_s,
                screening_threshold=round(m["threshold"], 4),
                percent_referred_for_hba1c=referred_pct,
                percent_not_referred=not_referred_pct,
                true_dysglycemia_captured_pct=captured_pct,
                true_dysglycemia_missed_pct=missed_pct,
                nnt=round(m["nnt"], 2) if not np.isnan(m["nnt"]) else "n/a",
                narrative=f"At threshold {m['threshold']:.2f}, {referred_pct}% of the screening population is referred for Stage-2 HbA1c testing, capturing {captured_pct}% of true dysglycemia cases while missing {missed_pct}%."
            ))

    pd.DataFrame(thresh_rows).to_csv(REPORTS / "threshold_tradeoffs.csv", index=False)
    pd.DataFrame(efficiency_rows).to_csv(REPORTS / "screening_efficiency.csv", index=False)
    print(f"[OK] Saved: {REPORTS / 'threshold_tradeoffs.csv'}")
    print(f"[OK] Saved: {REPORTS / 'screening_efficiency.csv'}")

    # 6. Plots Generation
    print("\nGenerating publication-quality figures...")
    plt.rcParams.update({"font.size": 11, "figure.autolayout": True})

    # Plot 1: ROC Curves (CORE-FULL models)
    plt.figure(figsize=(8, 6))
    for fam, col in [("Logistic_Regression", "#1f77b4"), ("GAM", "#2ca02c"), ("DLNN", "#d62728")]:
        sub = master_oof[(master_oof["dataset_variant"] == "CORE_FULL") & (master_oof["model_family"] == fam)]
        # Pick top configuration
        top_cfg = sub_grp = sub.groupby("model_configuration").apply(lambda g: roc_auc_score(g["y_true"], g["probability"])).idxmax()
        top_data = sub[sub["model_configuration"] == top_cfg]
        fpr, tpr, _ = roc_curve(top_data["y_true"], top_data["probability"])
        auc = roc_auc_score(top_data["y_true"], top_data["probability"])
        plt.plot(fpr, tpr, label=f"{fam.replace('_',' ')} (AUC = {auc:.3f})", color=col, lw=2)

    plt.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.7, label="Chance (AUC = 0.500)")
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Sensitivity)")
    plt.title("Development Out-of-Fold ROC Curves (CORE-FULL, N=3,355)")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.savefig(PLOTS / "development_roc_curves.png", dpi=300)
    plt.close()
    print(f"  [OK] {PLOTS / 'development_roc_curves.png'}")

    # Plot 2: PR Curves
    plt.figure(figsize=(8, 6))
    for fam, col in [("Logistic_Regression", "#1f77b4"), ("GAM", "#2ca02c"), ("DLNN", "#d62728")]:
        sub = master_oof[(master_oof["dataset_variant"] == "CORE_FULL") & (master_oof["model_family"] == fam)]
        top_cfg = sub.groupby("model_configuration").apply(lambda g: average_precision_score(g["y_true"], g["probability"])).idxmax()
        top_data = sub[sub["model_configuration"] == top_cfg]
        prec, rec, _ = precision_recall_curve(top_data["y_true"], top_data["probability"])
        prauc = average_precision_score(top_data["y_true"], top_data["probability"])
        plt.plot(rec, prec, label=f"{fam.replace('_',' ')} (PR-AUC = {prauc:.3f})", color=col, lw=2)

    base_prev = 776 / 3355
    plt.axhline(base_prev, color="k", linestyle="--", lw=1, alpha=0.7, label=f"Prevalence Baseline ({base_prev:.3f})")
    plt.xlabel("Recall (Sensitivity)")
    plt.ylabel("Precision (PPV)")
    plt.title("Development Out-of-Fold Precision-Recall Curves (CORE-FULL)")
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)
    plt.savefig(PLOTS / "development_pr_curves.png", dpi=300)
    plt.close()
    print(f"  [OK] {PLOTS / 'development_pr_curves.png'}")

    # Plot 3: Calibration Curves
    plt.figure(figsize=(8, 6))
    for fam, col in [("Logistic_Regression", "#1f77b4"), ("GAM", "#2ca02c"), ("DLNN", "#d62728")]:
        sub = master_oof[(master_oof["dataset_variant"] == "CORE_FULL") & (master_oof["model_family"] == fam)]
        top_cfg = sub.groupby("model_configuration").apply(lambda g: roc_auc_score(g["y_true"], g["probability"])).idxmax()
        top_data = sub[sub["model_configuration"] == top_cfg]
        prob_true, prob_pred = calibration_curve(top_data["y_true"], top_data["probability"], n_bins=10, strategy="uniform")
        brier = brier_score_loss(top_data["y_true"], top_data["probability"])
        plt.plot(prob_pred, prob_true, "s-", label=f"{fam.replace('_',' ')} (Brier = {brier:.4f})", color=col, lw=2)

    plt.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.7, label="Perfect Calibration")
    plt.xlabel("Mean Predicted Probability")
    plt.ylabel("Observed Fraction of Positives")
    plt.title("Development Calibration Curves (CORE-FULL, 10 Bins)")
    plt.legend(loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.savefig(PLOTS / "development_calibration_curves.png", dpi=300)
    plt.close()
    print(f"  [OK] {PLOTS / 'development_calibration_curves.png'}")

    # Plot 4: Threshold vs Sensitivity & Specificity Trade-off
    plt.figure(figsize=(9, 6))
    log_sub = master_oof[(master_oof["dataset_variant"] == "CORE_FULL") & (master_oof["model_family"] == "Logistic_Regression")]
    top_cfg = log_sub.groupby("model_configuration").apply(lambda g: roc_auc_score(g["y_true"], g["probability"])).idxmax()
    log_data = log_sub[log_sub["model_configuration"] == top_cfg]

    t_eval = np.linspace(0.05, 0.60, 100)
    sens_curve, spec_curve, ppv_curve = [], [], []
    for t in t_eval:
        m = compute_binary_metrics_at_threshold(log_data["y_true"].values, log_data["probability"].values, t)
        sens_curve.append(m["sensitivity"])
        spec_curve.append(m["specificity"])
        ppv_curve.append(m["ppv"])

    plt.plot(t_eval, sens_curve, label="Sensitivity (Recall)", color="#1f77b4", lw=2)
    plt.plot(t_eval, spec_curve, label="Specificity", color="#2ca02c", lw=2)
    plt.plot(t_eval, ppv_curve, label="PPV (Precision)", color="#ff7f0e", lw=2, linestyle=":")

    plt.axvline(0.50, color="gray", linestyle="--", alpha=0.6, label="Default Threshold (0.50)")
    plt.xlabel("Decision Threshold")
    plt.ylabel("Metric Value")
    plt.title("Screening Threshold Trade-off Curve (Core Logistic Regression)")
    plt.legend(loc="center right")
    plt.grid(True, alpha=0.3)
    plt.savefig(PLOTS / "threshold_sensitivity_specificity.png", dpi=300)
    plt.close()
    print(f"  [OK] {PLOTS / 'threshold_sensitivity_specificity.png'}")

    print("\n[OK] Phase 4 Out-of-fold Evaluation completed successfully.")


if __name__ == "__main__":
    main()
