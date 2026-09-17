# Textual Wireframes: Complete UI Blueprint

**Phase:** D1 — Design Foundation  
**Reference Design System:** `shadcn/ui` Layout & Spacing Principles  
**Date:** 2026-09-04  

---

## Wireframe A: Application Shell Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  SIDEBAR (260px)           │  TOPBAR & MAIN CONTENT AREA                                    │
├────────────────────────────┼────────────────────────────────────────────────────────────────┤
│  [✦] DYSPREDICT            │  Breadcrumb: Screening / New Screening          [Theme: ☼/☾]   │
│  Clinical Screening CDS    ├────────────────────────────────────────────────────────────────┤
│                            │                                                                │
│  SCREENING                 │  Page Title: New Stage-1 Screening                             │
│  • New Screening    [●]    │  Subtitle: Enter 7 non-laboratory predictors for triage.       │
│  • Review Queue     [3]    │                                                                │
│  • History                 │  ┌──────────────────────────────────────────────────────────┐  │
│                            │  │                                                          │  │
│  RESEARCH & GOVERNANCE     │  │                  [ MAIN CONTENT BLOCK ]                  │  │
│  • Analytics               │  │                                                          │  │
│  • About the Model         │  │                                                          │  │
│                            │  └──────────────────────────────────────────────────────────┘  │
│  ────────────────────────  │                                                                │
│  Reviewer: Dr. F. Susanto  │                                                                │
│  Role: Clinical Evaluator  │  Footer: NHANES 2021-2023 Locked GAM Protocol · v1.0.0         │
└────────────────────────────┴────────────────────────────────────────────────────────────────┘
```

---

## Wireframe B: New Screening Form (Stage 1)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  New Screening · Stage 1 Non-Laboratory Assessment                                          │
│  Complete all seven non-laboratory parameters. Laboratory markers are strictly excluded.   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─ 1. Demographic ──────────────────────┐  ┌─ 2. Body Measurements ─────────────────────┐  │
│  │ Age                                   │  │ Body Mass Index (BMI)                      │  │
│  │ [ 52.0                            ] yr│  │ [ 29.40                        ] kg/m²     │  │
│  │ Valid range: 18.0 - 85.0              │  │ Valid range: 14.0 - 70.0                   │  │
│  │                                       │  │                                            │  │
│  │ Biological Sex                        │  │ Waist Circumference                        │  │
│  │ (●) Female      ( ) Male              │  │ [ 98.5                         ] cm        │  │
│  │                                       │  │ Valid range: 50.0 - 180.0                  │  │
│  └───────────────────────────────────────┘  └────────────────────────────────────────────┘  │
│                                                                                             │
│  ┌─ 3. Medical History ──────────────────┐  ┌─ 4. Daily Physical Activity ───────────────┐  │
│  │ History of Hypertension               │  │ Sedentary Time                             │  │
│  │ [ Yes, Doctor-Diagnosed         ▼ ]   │  │ [ 480                          ] min/day   │  │
│  │ Self-reported hypertension history.   │  │ [?] Minutes spent sitting/reclining.       │  │
│  │                                       │  │ Valid range: 0 - 1440 min (8.0 hours/day)  │  │
│  │ History of Smoking                    │  │                                            │  │
│  │ [ Yes (≥ 100 cigarettes lifetime) ▼ ] │  │                                            │  │
│  └───────────────────────────────────────┘  └────────────────────────────────────────────┘  │
│                                                                                             │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  [ Clear Form ]                                                     [ Run Screening  → ]    │
│  (Secondary Outline)                                                (Primary Brand Action)  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe C: Screening Result Screen

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Screening Result · Case #1048                                                              │
│  Evaluated: Sep 04, 2026, 12:45 · Model: Phase-5 GAM (Locked)                               │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─ DECISION SUPPORT STATUS ─────────────────────────────────────────────────────────────┐  │
│  │                                                                                       │  │
│  │  [▲] ELEVATED SCREENING SIGNAL                        Screening Probability: 24.7%    │  │
│  │  Status: [ Referral Recommended ]                     Frozen Threshold:      13.9%    │  │
│  │                                                                                       │  │
│  │  Recommendation: Refer for Stage-2 Confirmatory HbA1c Assessment                      │  │
│  │                                                                                       │  │
│  │  Probability Meter:                                                                   │  │
│  │  0% ─────────────[13.9% Floor]──────[24.7% Score]────────────────────────────── 100%  │  │
│  │  [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  │  │
│  │                                                                                       │  │
│  │  [i] Disclaimer: This screening tool does not provide a definitive diagnosis.         │  │
│  │      Elevated signals identify individuals who warrant venous laboratory testing.     │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  ┌─ PARTICIPANT INPUT SUMMARY ───────────────────────────────────────────────────────────┐  │
│  │ Age: 52 yr   · Sex: Female · BMI: 29.4 kg/m² · Waist: 98.5 cm                         │  │
│  │ Hypertension: Yes · Smoking: Yes (≥100 cigs) · Sedentary: 480 min/day                 │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  [ Review Explanations Below ↓ ]                                [ Proceed to Review ]       │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe D: Explanation Interface (GAM-Native Additive Factors)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Why This Result? · Model-Native Additive Term Decomposition                                │
│  Relative contribution of each predictor to the overall log-odds screening score.           │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  FACTORS ELEVATING SCREENING SCORE (Pushes Toward Referral)                                 │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  • Waist Circumference (98.5 cm)          [▲ Strong]     Log-Odds: +0.482  [=========>   ]  │
│  • Age (52.0 years)                       [▲ Moderate]   Log-Odds: +0.341  [======>      ]  │
│  • Body Mass Index (29.4 kg/m²)           [▲ Moderate]   Log-Odds: +0.289  [=====>       ]  │
│  • Hypertension History (Yes)             [▲ Low]        Log-Odds: +0.145  [==>          ]  │
│                                                                                             │
│  FACTORS MODERATING SCREENING SCORE (Pushes Away From Referral)                             │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  • Sedentary Time (480 min/day)           [▼ Low]        Log-Odds: -0.062  [   <==       ]  │
│  • Biological Sex (Female)                [▼ Low]        Log-Odds: -0.041  [    <=       ]  │
│                                                                                             │
│  ▶ [▼] Inspect Spline Curvature Details (Research Verification)                             │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ GAM Spline Term: f_waist(98.5) = +0.482 | Spline Knots: 10 | Smoothing Lambda: 10.0  │  │
│  │ Linear Basis Term: sex_female = -0.041                                                │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe E: Human Review Card

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Clinician Guided Review · Case #1048                                                       │
│  Synthesize AI screening evidence with clinical judgment to determine referral action.      │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  System Screening Signal:           ELEVATED (Probability: 24.7% vs Floor: 13.9%)          │
│  System Referral Recommendation:    REFER FOR STAGE-2 HbA1c ASSESSMENT                      │
│                                                                                             │
│  Select Clinical Action:                                                                    │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                                       │  │
│  │  [ ✔ Accept Recommendation ]                       [ ✖ Override Recommendation ]      │  │
│  │  Confirms referral for Stage-2 HbA1c.               Rejects referral based on         │  │
│  │  Orders laboratory requisition.                     documented clinical rationale.    │  │
│  │                                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  [i] Note: Overrides require structured justification and are logged for research audit.    │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe F: Human Override Dialog Modal

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  [!] Confirm Clinical Override · Case #1048                                            [✕]  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  You are modifying the automated referral recommendation.                                   │
│  This action will be logged in the permanent clinical audit repository.                     │
│                                                                                             │
│  COMPARISON:                                                                                │
│  System Recommendation:   [ Refer for Stage-2 HbA1c ]  (Elevated Signal, p=24.7%)           │
│  Proposed Human Action:   [ Do Not Refer At This Time ]                                     │
│                                                                                             │
│  PRIMARY CLINICAL JUSTIFICATION (Required):                                                 │
│  [ Patient has recent documented normal HbA1c (< 30 days)                               ▼ ] │
│                                                                                             │
│  CLINICAL RATIONALE / NOTES (Required):                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Patient completed venous HbA1c test on Aug 18, 2026 showing 5.2%. No acute changes   │  │
│  │ in clinical presentation warranting repeat laboratory testing at this time.          │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  Reviewer Identification: Dr. F. Susanto (Logged Session ID: REV-8821)                      │
│                                                                                             │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  [ Cancel ]                                                  [ Confirm & Log Override ]     │
│  (Secondary Outline)                                         (Solid Destructive / Brand)    │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe G: Stage-2 HbA1c Confirmatory Intake

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Stage-2 Confirmatory Laboratory Assessment · Case #1048                                    │
│  Record venous blood laboratory findings to complete the two-stage screening cycle.         │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  STAGE-1 SUMMARY:                                                                           │
│  Screening Signal: Elevated (p=24.7%) · Reviewer Action: Referral Confirmed (Dr. Susanto)   │
│                                                                                             │
│  LABORATORY INTAKE:                                                                         │
│  Measured Venous HbA1c Level                                                                │
│  [ 6.1                                ] %                                                   │
│  Reference: <5.7% Normal | 5.7%-6.4% Prediabetes | ≥6.5% Diabetes                           │
│                                                                                             │
│  Date of Laboratory Collection                                                              │
│  [ 2026-09-04                         ]                                                     │
│                                                                                             │
│  Laboratory Reference / Sample ID (Optional)                                                │
│  [ LAB-JKT-88219                      ]                                                     │
│                                                                                             │
│  ┌─ PREVIEW CATEGORIZATION ──────────────────────────────────────────────────────────────┐  │
│  │ Current Range: [ PREDIABETES RANGE · 5.7% - 6.4% ]                                    │  │
│  │ Dysglycemia Screening True Positive: Confirmed HbA1c ≥ 5.7%                            │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  [ Cancel ]                                                  [ Save & Complete Cycle ]      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe H: Review Queue Data Table

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Clinician Review Queue                                                                     │
│  Active cases requiring clinical evaluation and referral disposition.                       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Filter: [ All Pending (3) ▼ ]   Search: [ Search Case ID / Date...         ] [ Export CSV ]│
│                                                                                             │
│  Case ID  Date & Time      Signal    Prob.   Top Factor       Status          Action        │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  #1048    09/04 12:45      Elevated  24.7%   Waist (98.5cm)   Pending Review  [ Review → ]  │
│  #1047    09/04 11:20      Elevated  18.2%   Age (64.0yr)     Pending Review  [ Review → ]  │
│  #1045    09/04 09:15      Elevated  31.0%   BMI (34.2kg/m²)  Pending Review  [ Review → ]  │
│                                                                                             │
│  Showing 3 of 3 pending cases · Page 1 of 1                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe I: Screening History & Audit Log

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Screening History & Audit Repository                                                       │
│  Immutable log of all completed screenings, clinician actions, and laboratory outcomes.     │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Filters: [ Status: All ▼ ] [ Signal: All ▼ ] [ Date: Last 30 Days ▼ ]   [ Search...      ] │
│                                                                                             │
│  ID    Date         Stage 1 Signal  Prob    Human Decision  Stage 2 Lab   Final Outcome     │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  1048  2026-09-04   Elevated        24.7%   Referral Conf.  HbA1c: 6.1%   Prediabetes       │
│  1046  2026-09-04   Non-Elevated    08.4%   Auto-Discharge  Not Reqd      Normal (Screened) │
│  1044  2026-09-03   Elevated        19.1%   Overridden [!]  Declined      Overridden (Clin) │
│  1043  2026-09-03   Elevated        22.5%   Referral Conf.  Pending Lab   Referred          │
│  1042  2026-09-02   Non-Elevated    11.2%   Auto-Discharge  Not Reqd      Normal (Screened) │
│                                                                                             │
│  [< Previous]  Page 1 of 18  [Next >]                                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe J: Screening Detail View

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Case Audit Detail · Case #1048                                             [ Print Report ]│
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─ 1. STAGE-1 AUTOMATED SCREENING OUTPUT ───────────────────────────────────────────────┐  │
│  │ Intake Timestamp: 2026-09-04 12:45:10 UTC · Model: NHANES GAM (n_splines=10, λ=10.0) │  │
│  │ Inputs: Age 52, Sex F, BMI 29.4, HTN Yes, Smoke Yes, Waist 98.5cm, Sedentary 480m/d   │  │
│  │ Screening Score (Log-Odds): -1.114  ·  Screening Probability: 24.72%                   │  │
│  │ Operating Floor: 13.89%  ·  Signal: ELEVATED  ·  Recommendation: REFER FOR HbA1c      │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  ┌─ 2. HUMAN CLINICIAN REVIEW & OVERRIDE RECORD ─────────────────────────────────────────┐  │
│  │ Review Timestamp: 2026-09-04 12:49:22 UTC · Reviewer: Dr. F. Susanto (ID: REV-8821)   │  │
│  │ Action Taken: ACCEPTED RECOMMENDATION (Referred to Stage-2 HbA1c)                     │  │
│  │ Clinical Note: "High central adiposity combined with HTN warrants venous testing."    │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  ┌─ 3. STAGE-2 CONFIRMATORY LABORATORY FINDINGS ─────────────────────────────────────────┐  │
│  │ Collection Date: 2026-09-04 · Lab Reference: LAB-JKT-88219                            │  │
│  │ Measured Venous HbA1c: 6.10%                                                          │  │
│  │ Categorization: PREDIABETES RANGE (Dysglycemia True Positive Identified)               │  │
│  │ Status: CASE COMPLETE & ARCHIVED                                                      │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  [ ← Back to History ]                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe K: Research Analytics Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Research Analytics & Operational Oversight                                                 │
│  Real-time surveillance of screening yield, concordance, and override patterns.             │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─ TOTAL SESSIONS ────┐  ┌─ REFERRAL RATE ──────┐  ┌─ CONCORDANCE RATE ───┐  ┌─ STAGE 2 YIELD ───────┐  │
│  │ 184 Screenings      │  │ 34.2% (63/184)       │  │ 91.8% Agreement      │  │ 74.4% Confirmed Dys. │  │
│  │ All Stage-1 intakes │  │ Elevated AI signals  │  │ Human vs AI referral │  │ 32/43 Lab-tested     │  │
│  └─────────────────────┘  └──────────────────────┘  └──────────────────────┘  └───────────────────────┘  │
│                                                                                             │
│  ┌─ OVERRIDE DISTRIBUTION (N = 5 Overrides) ───┐  ┌─ STAGE-2 GLYCEMIC STRATIFICATION ────────┐  │
│  │ • Recent Normal Lab:             3 (60.0%)  │  │ • Normal (<5.7%):              11 (25.6%) │  │
│  │ • Severe Frailty / Palliation:   1 (20.0%)  │  │ • Prediabetes (5.7% - 6.4%):   24 (55.8%) │  │
│  │ • Patient Refusal:               1 (20.0%)  │  │ • Diabetes Range (≥6.5%):       8 (18.6%) │  │
│  └─────────────────────────────────────────────┘  └───────────────────────────────────────────┘  │
│                                                                                             │
│  [i] Methodological Guardrail: Clinician-AI agreement is a measure of operational           │
│      concordance and must not be reported as empirical model accuracy.                      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe L: About the Model (Academic Transparency)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  About the Model · Scientific Specification & Governance                                    │
│  Complete disclosure of mathematical architecture, development cohort, and limitations.    │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─ MODEL ARCHITECTURE ──────────────────────────────────────────────────────────────────┐  │
│  │ Model Family:       Generalized Additive Model (GAM) with Spline Terms                │  │
│  │ Formulation:        logit(P(Y=1)) = β0 + Σ f_i(X_i)                                   │  │
│  │ Hyperparameters:    n_splines = 10, smoothing penalty λ = 10.0                        │  │
│  │ Training Dataset:   NHANES 2021-August 2023 Pre-Pandemic Feasibility Cohort           │  │
│  │ Predictors (7):     Age, Sex, BMI, Waist, HTN History, Smoke History, Sedentary Time │  │
│  │ Target Outcome:     HbA1c-Defined Dysglycemia (HbA1c ≥ 5.7% [39 mmol/mol])            │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  ┌─ FROZEN DECISION POINT & HELD-OUT PERFORMANCE ────────────────────────────────────────┐  │
│  │ Operating Threshold:  0.1389 (Optimized on Development data to enforce ≥90% Sens)     │  │
│  │ Confirmatory Test:    Sensitivity: 86.39% (95% CI: 81.19% - 90.96%)                   │  │
│  │                       Specificity: 42.51% (95% CI: 37.84% - 47.31%)                   │  │
│  │                       ROC-AUC:     0.7277 (95% CI: 0.6901 - 0.7634)                   │  │
│  │                       PR-AUC:      0.4503 (95% CI: 0.3951 - 0.5098)                   │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  ┌─ EXPLICIT RESEARCH LIMITATIONS ───────────────────────────────────────────────────────┐  │
│  │ 1. Population: Developed on US NHANES survey participants; no external Indonesian     │  │
│  │    population validation has yet been conducted.                                      │  │
│  │ 2. Triage Classification: Designed exclusively for first-stage community screening;   │  │
│  │    cannot replace laboratory diagnosis.                                               │  │
│  │ 3. Survey Weighting: Fitted as unweighted predictive models for feasibility analysis. │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```
