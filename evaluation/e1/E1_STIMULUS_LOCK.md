# Synthetic Stimulus Lock Specification (Phase E1.3)
## Single Canonical Source of Truth for Evaluation Case Stimuli

**Document Identifier:** `E1-STIMULUS-LOCK-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Governing Authority:** `E1_SCENARIO_RUNTIME_VERIFICATION.md` (Frozen Runtime Execution Evidence)  
**Runtime Target:** `research-prototype-v1.0` (Development Mode Invariant Verification)  
**Operating Decision Threshold:** `0.1389` (Immutable)  

---

## 1. Governance & Single Source of Truth Mandate

This document serves as the **exclusive, authoritative specification** for all synthetic case stimuli utilized within the formal evaluation protocol suite (`evaluation/e1/`). 

### Mandatory Rules for Protocol Artifacts:
1. **Zero Contradictory Stimulus Data:** All task scenario cards, participant-facing instructions, moderator scripts, scoring rubrics, and data logging schemas must derive their case values exclusively from this document.
2. **Canonical Seven Predictors Exclusively:** Synthetic cases present only the seven active features ingested by the frozen machine learning model. No non-model medical variables (e.g., blood pressure numbers, medication lists, physical activity minutes/week) may be presented to participants or described as model inputs.
3. **Exact Mathematical Provenance:** All probabilities, risk signals, and additive contributions recorded here represent the verified runtime output of `research-prototype-v1.0` as proven in [`E1_SCENARIO_RUNTIME_VERIFICATION.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_SCENARIO_RUNTIME_VERIFICATION.md).

---

## 2. Canonical Stimulus Profiles

### 2.1 Synthetic Case Alpha (`CASE-ALPHA`)

```
========================================================================================
CANONICAL STIMULUS SPECIFICATION: CASE-ALPHA
========================================================================================
Protocol Version:                v1.0.3
Case Code:                       CASE-ALPHA
Workflow Assignment:             Task 1 (Screening Intake), Task 2 (XAI Review), 
                                 Task 3 (Accept Review), Task 5 (Stage-2 HbA1c Entry)

--- EXACT SEVEN MODEL INPUTS ---
1. Age:                          56 years
2. Biological Sex:               Male (Form Value: 'male')
3. Body Mass Index (BMI):        31.2 kg/m²
4. History of Hypertension:      Yes (Doctor diagnosed high blood pressure; Value: 'yes')
5. Smoking History:              No (Smoked <100 cigarettes in lifetime; Value: 'no')
6. Waist Circumference:          102.0 cm
7. Sedentary Time:               480 minutes/day (8.0 hours/day)

--- FROZEN RUNTIME INFERENCE OUTPUT ---
Model Link-Scale Intercept (β0): -0.729147
Model Linear Predictor (η):      -0.979611
Screening Probability (p̂):       0.272969 (27.30%)
Operating Threshold:             0.1389
AI Referral Recommendation:      Refer (p̂ >= 0.1389)
Screening Signal:                Elevated Screening Signal

--- ADDITIVE CONTRIBUTIONS (LOG-ODDS SCALE) ---
- Age (56 years):                +0.417980  [Higher / Elevating]
- Biological Sex (Male):         -0.026593  [Lower / Moderating]
- BMI (31.2 kg/m²):              +0.004917  [Higher / Elevating]
- History of Hypertension (Yes): +0.103343  [Higher / Elevating]
- Smoking History (No):          -0.117616  [Lower / Moderating]
- Waist Circumference (102.0 cm):-0.159560  [Lower / Moderating]
- Sedentary Time (480 min/day):  -0.472934  [Lower / Moderating]

--- FACTOR IDENTIFICATION CRITERIA (TASK 2 RUBRIC) ---
Top Positive Contributor:        Age (+0.417980) -- Largest factor elevating the score
Valid Lowering Factors:          Sedentary Time (-0.472934)
                                 Waist Circumference (-0.159560)
                                 Smoking History: Non-smoker (-0.117616)
                                 Biological Sex: Male (-0.026593)

--- STAGE-2 WORKFLOW PROGRESSION ---
Stage-2 Trigger:                 Participant accepts AI recommendation to Refer in Task 3
Stage-2 Laboratory HbA1c:        6.1% (Entered in Task 5)
Stage-2 Clinical Range:          Prediabetes range (5.7% - 6.4%)
Final Case State:                Completed Stage-2 Assessment (completed_stage2)
========================================================================================
```

---

### 2.2 Synthetic Case Beta (`CASE-BETA`)

```
========================================================================================
CANONICAL STIMULUS SPECIFICATION: CASE-BETA
========================================================================================
Protocol Version:                v1.0.3
Case Code:                       CASE-BETA
Workflow Assignment:             Task 4 (Human Override), Task 6 (Audit History Review)

--- EXACT SEVEN MODEL INPUTS ---
1. Age:                          32 years
2. Biological Sex:               Female (Form Value: 'female')
3. Body Mass Index (BMI):        23.5 kg/m²
4. History of Hypertension:      No (Form Value: 'no')
5. Smoking History:              Yes (Smoked >=100 cigarettes in lifetime; Value: 'yes')
6. Waist Circumference:          74.0 cm
7. Sedentary Time:               300 minutes/day (5.0 hours/day)

--- FROZEN RUNTIME INFERENCE OUTPUT ---
Model Link-Scale Intercept (β0): -0.729147
Model Linear Predictor (η):      -2.850362
Screening Probability (p̂):       0.054663 (5.47%)
Operating Threshold:             0.1389
AI Referral Recommendation:      No Referral (p̂ < 0.1389)
Screening Signal:                Lower Screening Signal

--- ADDITIVE CONTRIBUTIONS (LOG-ODDS SCALE) ---
- Age (32 years):                -0.784738  [Lower / Moderating]
- Biological Sex (Female):       +0.026593  [Higher / Elevating]
- BMI (23.5 kg/m²):              -0.258779  [Lower / Moderating]
- History of Hypertension (No):  -0.103343  [Lower / Moderating]
- Smoking History (Yes):         +0.117616  [Higher / Elevating]
- Waist Circumference (74.0 cm): -0.773908  [Lower / Moderating]
- Sedentary Time (300 min/day):  -0.344656  [Lower / Moderating]

--- FACTOR IDENTIFICATION CRITERIA ---
Top Positive Contributors:       Smoking History (+0.117616)
                                 Biological Sex: Female (+0.026593)
Valid Lowering Factors:          Age (-0.784738)
                                 Waist Circumference (-0.773908)
                                 Sedentary Time (-0.344656)
                                 BMI (-0.258779)
                                 Hypertension: No (-0.103343)

--- HUMAN OVERRIDE & AUDIT WORKFLOW ---
Task 4 Protocol Action:          Override AI 'No Referral' -> Human Decision 'Refer'
Structured Override Reason:      "Referral is preferred as a precaution" (precautionary_referral)
Override Scenario Note:          "Individual reports unrecorded family history of early diabetes"
Post-Override Stage-2 State:     Pending Stage-2 Assessment (pending_stage2)
Task 6 Verification Invariant:   Case Beta MUST remain in 'Pending Stage-2 Assessment' 
                                 (HbA1c is NOT entered for Case Beta prior to Task 6)
========================================================================================
```

---

## 3. Cross-Document Stimulus Fingerprint Table

| Attribute | CASE-ALPHA | CASE-BETA | Verification Source |
| :--- | :--- | :--- | :--- |
| **Case Code** | `CASE-ALPHA` | `CASE-BETA` | Frozen Protocol |
| **Age** | `56` | `32` | Canonical Seven |
| **Sex** | `Male` (`male`) | `Female` (`female`) | Canonical Seven |
| **BMI** | `31.2` | `23.5` | Canonical Seven |
| **Hypertension History** | `Yes` (`yes`) | `No` (`no`) | Canonical Seven |
| **Smoking History** | `No` (`no`) | `Yes` (`yes`) | Canonical Seven |
| **Waist Circumference** | `102.0 cm` | `74.0 cm` | Canonical Seven |
| **Sedentary Time** | `480 min/day` | `300 min/day` | Canonical Seven |
| **Linear Predictor ($\eta$)** | `-0.979611` | `-2.850362` | Frozen Runtime link-scale |
| **Screening Probability ($\hat{p}$)** | **`0.272969` ($27.30\%$)** | **`0.054663` ($5.47\%$)** | Frozen Model `predict_mu` |
| **Operating Threshold** | `0.1389` | `0.1389` | Frozen Threshold |
| **AI Recommendation** | **`Refer`** | **`No Referral`** | Frozen UI String |
| **Screening Signal** | **`Elevated Screening Signal`** | **`Lower Screening Signal`** | Frozen UI Badge String |
| **Top Positive Contributor** | `Age (+0.417980)` | `Smoking History (+0.117616)` | Frozen PyGAM spline |
| **Primary Lowering Contributor** | `Sedentary Time (-0.472934)` | `Age (-0.784738)` | Frozen PyGAM spline |
| **Task Lifecycle Sequence** | Tasks 1, 2, 3, 5 | Tasks 4, 6 | Task Flow Invariant |
| **Task 6 State Invariant** | `Completed Stage-2 Assessment` | `Pending Stage-2 Assessment` | Queue Integrity Invariant |
