# Research Claim Matrix & Permitted Scientific Wording

**Purpose:** Prevents overclaiming, premature conclusions, and methodological distortion in thesis writing and scientific reports.  
**Governing Standard:** `research-governance` Skill

---

## Global Claim Boundaries

| Domain / Claim Topic | Evidence Source | Allowed Scientific Wording | Strictly Prohibited Wording | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Model Discrimination** | Phase-5 held-out final test (`final_test_predictions.csv`) | *"GAM achieved ROC-AUC 0.7277 and PR-AUC 0.4503 on the held-out test cohort."* | *"GAM is highly accurate"*, *"GAM is clinically superior"*, *"GAM diagnoses diabetes"* | **LOCKED & VERIFIED** |
| **Model Comparison** | Phase-5 final evaluation report | *"GAM (ROC-AUC 0.7277) and baseline Logistic Regression (ROC-AUC 0.7291) demonstrated broadly comparable discrimination; GAM was selected for exact shape interpretability."* | *"GAM outperformed Logistic Regression"*, *"GAM is the most accurate model"* | **LOCKED & VERIFIED** |
| **Operating Threshold** | Phase 4/5 evaluation protocol | *"Operating threshold 0.1389 was selected on development cross-validation to target ≥90% sensitivity."* | *"0.1389 is the clinical optimum"*, *"The threshold is universally optimal"* | **LOCKED & VERIFIED** |
| **Sensitivity Target** | Phase-5 held-out final test | *"Final held-out sensitivity point estimate was 86.39% (95% CI: 81.19%–90.96%); while the CI encompasses the 90% target, the point estimate was lower."* | *"The model met the ≥90% sensitivity target on the test set"* | **LOCKED & VERIFIED** |
| **XAI Fidelity** | Phase D2.5 reconstruction testing | *"GAM-native additive decomposition reconstructs the model log-odds output within 1e-10 numerical tolerance."* | *"The explanation proves the model is medically correct"*, *"The explanation identifies the true biological causes"* | **LOCKED & VERIFIED** |
| **Human Override** | System functional testing (Phases D2.7, D3) | *"The prototype supports auditable human overrides with structured rationale recording."* | *"Human override improves patient outcomes"*, *"Doctor correction fixes AI errors"* | **LOCKED & VERIFIED** |
| **Human–AI Agreement** | Operational analytics (Phase D2.10) | *"Measures decision concordance between the AI recommendation and the final human determination."* | *"Measures AI accuracy"*, *"Measures clinical ground truth"* | **LOCKED & VERIFIED** |
| **Stage-2 Lab Ranges** | Phase D2.8 implementation | *"Categorizes entered laboratory HbA1c values according to standard ADA 2026 reference cutoffs."* | *"Confirms true population prevalence"*, *"Validates Stage-1 diagnostic accuracy"* | **LOCKED & VERIFIED** |
| **System Usability (SUS)** | Formal User Evaluation (NOT YET CONDUCTED) | *"Not yet collected; pending formal user evaluation protocol."* | *"The dashboard is easy to use"*, *"Clinicians prefer this interface"* | **CURRENT STATUS: NOT YET AVAILABLE** |
