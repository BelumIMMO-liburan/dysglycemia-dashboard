# Research Question, Claim & Evidence Matrix (Phase E1)
## Methodological Grounding & Epistemic Boundary Mapping

**Document Identifier:** `E1-RQ-CLAIM-MATRIX-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Epistemic Architecture & Purpose

A recurring threat in clinical machine learning and decision-support research is **claim conflation**—the tendency to interpret user satisfaction as clinical efficacy, or algorithmic ROC-AUC as proof of beneficial bedside decisions.

This matrix formally defines the epistemic boundary for every research question (RQ). For each claim, it documents:
1. The exact underlying construct.
2. The authoritative empirical evidence source.
3. The participant group required to produce that evidence.
4. The statistical or qualitative metric.
5. The precise allowed scientific conclusions.
6. The strictly prohibited claims and overgeneralizations.

---

## 2. Master RQ Evidence Mapping Matrix

| Dimension | RQ1: Predictive Discrimination & Calibration | RQ2: System Integration & Auditability | RQ3: Dashboard Usability & Operability | RQ4: User Comprehension & Mental Model |
| :--- | :--- | :--- | :--- | :--- |
| **Research Question** | *How well does the frozen non-laboratory GAM discriminate and calibrate HbA1c-defined dysglycemia in the held-out NHANES test cohort?* | *How can GAM-native explanation and Human Review / Human Override be integrated into an auditable two-stage screening dashboard while preserving the original AI output and decision provenance?* | *How usable is the frozen two-stage screening dashboard for participants performing the defined screening-review tasks?* | *How well do participants understand the Stage-1 screening result, GAM-native explanation, Human Review / Override semantics, and Stage-2 laboratory-range output?* |
| **Target Construct** | Model Discrimination, Calibration, and Operating Sensitivity. | Architectural Integrity, Functional Correctness, and Immutable Traceability. | Interface Usability, Operability, Learnability, and User Task Burden. | Subjective & Objective Mental Model Alignment with System Semantics. |
| **Authoritative Evidence Source** | Phase 5 Held-Out NHANES Test Split ($N = 812$ individuals: normal-range = 621, dysglycemia-range = 191; `nhanes_feasibility_2021_2023`). | Phase D2.3–D2.8 Contracts, D3 Final System Audit Report, 144 Automated Tests. | Formal User Study Session ($N = 24\text{--}30$): 10-Item Indonesian-adapted SUS (Sharfina & Santoso, 2016) + Task Observation. | Formal User Study Session ($N = 24\text{--}30$): 8-Item Protocol-Defined Objective Quiz + Qualitative Items. |
| **Participant Group Required** | **None.** (Offline held-out epidemiological cohort data). | **None.** (Automated software verification suite). | **Primary Usability Group** (University students, staff, adult computer users). | **Primary Usability Group** (University students, staff, adult computer users). |
| **Metric / Indicator** | - ROC-AUC & PR-AUC<br>- Sensitivity & Specificity at threshold 0.1389<br>- Brier Score & Calibration Curve | - 100% test pass rate across Scenarios A–H<br>- Cryptographic hash parity on model artifacts<br>- Zero mutable updates to `ScreeningRecord` | - System Usability Scale (SUS, 0–100)<br>- Task completion rate (% success)<br>- Assistance levels (0–3)<br>- Error occurrence frequency | - Objective Quiz Total Score (0–8)<br>- Item-level accuracy percentages<br>- Likert clarity scores (median, IQR)<br>- Qualitative confusion categories |
| **Analytical Procedure** | Bootstrap 95% confidence intervals (1,000 iterations); offline metric tabulation. | Deterministic test execution (`python manage.py test predictor`); schema immutability assertions. | Descriptive statistics: Mean, SD, Median, IQR of SUS relative to published empirical distributions; task frequencies. | Descriptive item-level proportions; percentage distribution; lightweight category analysis. |
| **Strictly Allowed Conclusions** | - *"The frozen GAM achieved a held-out ROC-AUC of 0.7277 (bootstrap 95% CI: [0.6875, 0.7656])."*<br>- *"At the operating threshold of 0.1389, sensitivity was 86.39% and specificity was 42.51%."*<br>- *"The development-derived operating threshold targeting >=90% sensitivity achieved 86.39% sensitivity on the held-out final test. Therefore the 90% development sensitivity target was not reproduced at the final-test point estimate."*<br>- *"The model was broadly comparable in discrimination to logistic regression."* | - *"The two-stage screening architecture records immutable screening inputs and preserves the original AI recommendation across review actions."*<br>- *"Human Override alters the downstream referral decision without modifying the recorded model probability or inputs."* | - *"Participants achieved a mean SUS score of X (SD = Y), which falls within the [Good / OK] reference range relative to the Bangor et al. (2008, 2009) empirical software distribution."*<br>- *"Task 1 was completed independently by Z% of participants."* | - *"Participants correctly identified that an elevated screening signal does not constitute a diagnosis in X% of evaluations."*<br>- *"X% understood that Human Override modifies the final human referral decision rather than the machine probability."* |
| **Strictly Prohibited Conclusions** | - *PROHIBITED: "The model is clinically accurate or validated for Indonesian populations."*<br>- *PROHIBITED: "The model met its 90% sensitivity target on the test set."* (It achieved 86.39%).<br>- *PROHIBITED: "The model diagnoses diabetes."* | - *PROHIBITED: "The workflow prevents all clinical errors."*<br>- *PROHIBITED: "The system automates clinical triage."*<br>- *PROHIBITED: "The software guarantees zero physician bias."* | - *PROHIBITED: "The dashboard has proven clinical usability in a busy hospital emergency department."*<br>- *PROHIBITED: "SUS >= 68 confirms acceptable clinical ergonomics."*<br>- *PROHIBITED: "The system improves clinical efficiency."* | - *PROHIBITED: "The explainability interface proves that the model's features medically caused diabetes."*<br>- *PROHIBITED: "High comprehension proves clinicians make better therapeutic choices."* |

---

## 3. Secondary / Optional Evidence Layer: Expert Face-Validity Review

If an optional sub-sample of health professionals ($N = 3\text{--}5$) is recruited:

| Dimension | Expert Review Specifications |
| :--- | :--- |
| **Target Construct** | Professional Face Validity, Terminology Naturalness, and Perceived Plausibility of the Screening/Referral Workflow. |
| **Evidence Source** | Semi-structured expert interview + 5 tailored domain Likert items. |
| **Participant Group** | Practicing clinicians, nurses, or clinical academic staff. |
| **Permitted Language** | *"Participating healthcare practitioners reported that the two-stage separation aligns well with primary care referral practices."* |
| **Prohibited Language** | *"The system is clinically endorsed, certified, or proven to improve patient health outcomes."* |
| **Methodological Isolation** | Expert ratings **MUST NOT** be combined into the primary lay-cohort SUS calculations. |

---

## 4. Operationalization of Prohibited Fallacies

To guarantee scientific rigor during thesis drafting and defense, the following specific fallacies are defined as research governance violations:

1. **The Performance-Usability Fallacy:**  
   *Fallacy:* "Because the system scored 82 on the SUS, the underlying machine learning model is effective."  
   *Correction:* Usability measures interface friction; ROC-AUC measures statistical discrimination. They are mathematically orthogonal.

2. **The Explanation-Causality Fallacy:**  
   *Fallacy:* "The GAM-native explanation proves that high BMI caused the individual's elevated screening score."  
   *Correction:* The explanation decomposes additive model log-odds. Statistical association in an observational survey (NHANES) does not establish biological causality.

3. **The Agreement-as-Accuracy Fallacy:**  
   *Fallacy:* "A 95% Human–AI agreement rate means the AI made accurate recommendations in 95% of cases."  
   *Correction:* Agreement reflects concordance between human operator choice and machine recommendation. Neither represents ground truth without Stage-2 laboratory verification.

4. **The Population Generalization Fallacy:**  
   *Fallacy:* "The screening tool is ready for implementation in Indonesian Puskesmas."  
   *Correction:* The model was derived from US NHANES data. Transferability to Indonesian clinical cohorts requires formal local calibration and validation.
