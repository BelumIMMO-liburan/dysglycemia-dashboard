# Verification Bias & Epistemic Safeguards in Operational Analytics

**Document Reference:** `design/d2_10/D2_10_VERIFICATION_BIAS_NOTE.md`  
**Phase:** D2.10 — Research Analytics + Human–AI Decision Flow  
**Thesis Defense Point:** Distinguishing Operational Decision-Support Surveillance from Frozen Machine Learning Evaluation

---

## 1. The Core Methodological Reality
In the research prototype's two-stage dysglycemia screening architecture:
$$\text{Stage-1 Non-Lab Intake} \longrightarrow \text{Frozen GAM} \longrightarrow \text{Human Review} \longrightarrow \text{Final Human Decision} \longrightarrow \text{If Refer: Stage-2 HbA1c Lab}$$

Stage-2 laboratory blood assessment (venous HbA1c measurement) is indicated and recorded **strictly when the final human decision recommends referral** (`final_referral_recommended == True`).

Conversely, when the finalized clinician decision is "Do not refer" (`final_referral_recommended == False`), the case terminates at Stage 1. Under real-world screening ethics and standard clinical workflows, non-referred individuals do **not** receive unnecessary, invasive laboratory blood draws.

---

## 2. Selective Verification (Ascertainment) Bias
Because laboratory confirmatory testing is selectively administered only to referred cases, the observed operational Stage-2 cohort ($N_{\text{stage2\_completed}}$) represents a **non-random, post-decision sub-sample** of the screening population.

Specifically:
1. **Missing Counterfactuals:** The true laboratory dysglycemia status of cases where the human reviewer decided "Do not refer" is unobserved in the operational database.
2. **Selective Ascertainment:** Individuals with high risk scores or clinical features concerning to reviewers are systematically enriched in the Stage-2 sub-cohort, while low-risk individuals are excluded.
3. **Conditioning on Human Decision:** Stage 2 reflects the joint filter of machine triage and human clinical judgment, not the isolated operating characteristics of the GAM model.

---

## 3. Strictly Prohibited Operational Computations
To maintain strict scientific integrity and prevent invalid clinical claims, the system enforces hard architectural and testing prohibitions. Operational Stage-2 records **MUST NEVER** be used to calculate:

- **Sensitivity:** Requires knowing true positive status for all dysglycemic cases in the screened population, including those not referred.
- **Specificity:** Requires knowing true negative status for all euglycemic cases, including those not referred.
- **Negative Predictive Value (NPV):** Completely uncomputable when non-referred outcomes are missing.
- **Positive Predictive Value (PPV):** Operational referral reflects both machine and clinician selection, not model PPV.
- **Receiver Operating Characteristic (ROC-AUC):** Requires complete outcome ground truth across all operating points.
- **Precision-Recall Area (PR-AUC):** Distorted by selective verification.
- **Confusion Matrix:** Neither the AI recommendation nor the human referral disposition represents biological ground truth.
- **AI Accuracy:** Operational agreement between AI and clinician is concordance, not accuracy.

---

## 4. Authoritative ML Evaluation vs. Operational Surveillance

| Dimension | Authoritative Evaluation (Phase 5) | Operational Surveillance (Phase D2.10) |
| :--- | :--- | :--- |
| **Data Source** | Locked Held-Out Test Split (`final_test_predictions.csv`, NHANES 2021–2023) | Operational Screening Database (`ScreeningRecord`, `HumanReview`, `Stage2Assessment`) |
| **Outcome Completeness** | 100% verified: laboratory HbA1c measured for all test participants regardless of prediction | Selective: laboratory HbA1c recorded only for final referred cases |
| **Statistical Validity** | Unbiased estimation of Sensitivity (0.9032), Specificity, ROC-AUC (0.7674), PR-AUC | Descriptive decision-support throughput, human-AI concordance, and observed intake ranges |
| **Permitted Metrics** | Sensitivity, Specificity, AUC, Brier Score, Calibration Curves | Volume, Agreement Rate, Override Rate, Referral Rate, Direction & Structured Rationale |
| **Epistemic Meaning** | Scientific predictive validity of the frozen mathematical model | Ergonomic and workflow behavior of the human-AI decision-support system |

---

## 5. Defense Alignment & Supervisory Reassurance
During thesis defense and supervision reviews, the candidate should explicitly articulate:
> *"In our operational dashboard, Stage-2 HbA1c is only obtained when the human clinician confirms or initiates a referral. Computing diagnostic sensitivity or specificity from this operational data would introduce severe selective verification bias. Therefore, our research analytics strictly monitor workflow throughput and human–AI decision concordance, while our frozen Phase-5 held-out evaluation remains the single authoritative analysis of predictive accuracy."*
