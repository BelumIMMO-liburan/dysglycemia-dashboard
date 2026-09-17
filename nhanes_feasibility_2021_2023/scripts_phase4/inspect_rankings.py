import pandas as pd

df = pd.read_csv("nhanes_feasibility_2021_2023/reports_phase4/cv_model_summary.csv")

for (var, fam), grp in df.groupby(["dataset_variant", "model_family"]):
    sorted_grp = grp.sort_values(
        by=["pooled_oof_pr_auc", "pooled_oof_roc_auc", "pooled_brier_score"],
        ascending=[False, False, True]
    )
    print(f"=== {var} | {fam} ===")
    for idx, r in sorted_grp.iterrows():
        c = r["model_configuration"]
        pr = r["pooled_oof_pr_auc"]
        roc = r["pooled_oof_roc_auc"]
        br = r["pooled_brier_score"]
        print(f"  {c:<25} | PR-AUC: {pr:.4f} | ROC-AUC: {roc:.4f} | Brier: {br:.4f}")
