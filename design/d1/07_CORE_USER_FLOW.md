# Core User Journey & Interaction Flow

**Phase:** D1 — Design Foundation  
**Workflow Class:** Two-Stage Non-Laboratory Screening to Confirmatory Laboratory Follow-Up  
**Date:** 2026-09-04  

---

## 1. The End-to-End Primary Flow

The dashboard's interaction architecture is anchored by a single primary clinical pathway. All auxiliary views (History, Analytics, About) exist solely to support and audit this sequential journey:

```
[ STEP 1: INTAKE ]
Clinician opens New Screening (/screening/new/)
Enters 7 non-laboratory predictors (Demographic, Body, History, Activity)
Clicks [ Run Screening ]
       │
       ▼
[ STEP 2: SCREENING RESULT ]
System executes frozen GAM model (nhanes_feasibility_2021_2023/models_phase5/gam_final.pkl)
Calculates screening probability (p) relative to frozen threshold (0.1389)
Displays calm status: Elevated Signal vs Non-Elevated Signal
       │
       ▼
[ STEP 3: EXPLANATION (XAI) ]
Decomposes log-odds into additive factor contributions:
- Factors elevating score (e.g., Waist circumference, Age, BMI)
- Factors moderating score (e.g., Sedentary time, Non-smoking)
Clinician reviews explanation before taking action
       │
       ▼
[ STEP 4: HUMAN REVIEW & CLINICAL DISPOSITION ]
Clinician evaluates System Referral Recommendation:
├── Pathway A: Accept Recommendation
│   - Referral confirmed for Stage-2 HbA1c
│   - Case moves to "Referred / Pending Stage 2" queue
└── Pathway B: Override Recommendation
    - Opens accessible Override Dialog
    - Clinician selects structured reason + enters clinical note
    - Override logged; case marked "Overridden: Referral Declined"
       │
       ▼ (For Referred Participants)
[ STEP 5: STAGE-2 CONFIRMATORY LABORATORY INTAKE ]
Participant undergoes venous blood collection
Laboratory reports HbA1c value (%)
Clinician enters laboratory result in Stage-2 Intake Form (/screening/<id>/stage2/)
       │
       ▼
[ STEP 6: LABORATORY RANGE CATEGORIZATION & CASE CLOSURE ]
System categorizes HbA1c based on standard clinical guidelines:
- Normal (< 5.7%)
- Prediabetes Range (5.7% - 6.4%)
- Diabetes Range (≥ 6.5%)
Case record is permanently closed and archived in immutable Audit History
```

---

## 2. Detailed Step Specifications

### Step 1: Stage-1 Non-Laboratory Intake
- **Actor:** Screening Nurse, Health Worker, or Research Assistant.
- **Inputs:** Exactly seven non-laboratory variables:
  1. `age` (Years: 18.0 – 85.0)
  2. `sex` (Biological Sex: Male / Female)
  3. `bmi` (Body Mass Index: 14.0 – 70.0 kg/m²)
  4. `hypertension_history` (Doctor-diagnosed hypertension: Yes / No)
  5. `smoking_history` (History of smoking $\ge 100$ cigarettes: Yes / No)
  6. `waist_cm` (Waist circumference: 50.0 – 180.0 cm)
  7. `sedentary_minutes_day` (Daily sedentary duration: 0 – 1440 min/day)
- **Validation Rules:** All 7 inputs are strictly required. Out-of-range numerical entries trigger immediate inline error feedback below the specific input. Form cannot be submitted with missing or invalid fields.
- **Actions:**
  - `[ Run Screening ]` (Primary solid button)
  - `[ Clear Form ]` (Secondary outline button with confirmation alert if dirty)

### Step 2: System Screening Result
- **Actor:** Reviewing Clinician or Screening Operator.
- **Evaluation Engine:** Preprocessor standardizes inputs $\rightarrow$ GAM calculates log-odds score $s = f_0 + \sum_{i=1}^7 f_i(x_i) \rightarrow$ Logistic transformation yields probability $p = \frac{1}{1 + e^{-s}}$.
- **Signal Logic:**
  - If $p \ge 0.1389 \rightarrow$ **Elevated Screening Signal**
    - Badge: Amber (`ui-badge-amber`)
    - System Recommendation: **Refer for Stage-2 HbA1c Assessment**
  - If $p < 0.1389 \rightarrow$ **Non-Elevated Screening Signal**
    - Badge: Slate (`ui-badge-slate`)
    - System Recommendation: **Routine Lifestyle Monitoring / No Immediate Lab Referral**
- **Disclaimers:** Mandatory visible notice: *"This screening result is not a medical diagnosis. Confirmatory testing requires venous HbA1c measurement."*

### Step 3: Transparent Factor Explanation (XAI)
- **Visual Presentation:** Clean additive factor cards.
- **Top Elevating Factors:** Ranked by positive contribution to log-odds.
- **Top Moderating Factors:** Ranked by negative contribution to log-odds.
- **Progressive Detail:** Clinician can click `"Inspect Spline Decomposition"` to view the exact partial dependence position for that patient.

### Step 4: Human Guided Review & Override Flow
- **Review Options:**
  1. **Accept Recommendation:**
     - Submits immediate confirmation.
     - Logs review timestamp, reviewer identifier, and decision (`accepted`).
  2. **Override Recommendation:**
     - Triggers accessible modal overlay (`AlertDialog`).
     - Shows side-by-side: `AI: Refer for Stage-2 HbA1c` vs `Human: Do Not Refer`.
     - Prompts for mandatory structured clinical reason:
       - *Recent Normal HbA1c within 30 days*
       - *Severe Frailty / Limited Screening Utility*
       - *Acute Confounding Medical Condition*
       - *Patient Refusal After Counseling*
       - *Alternative Clinical Management Indicated*
     - Requires free-text clinical justification.
     - Submits override: logs `decision = 'override'`, records reason and note, leaves AI recommendation and screening probability untouched.

### Step 5: Stage-2 Confirmatory Laboratory Intake
- **Actor:** Laboratory Specialist, Doctor, or Research Coordinator.
- **Trigger:** Accessible for any case with a status of `Referred for Stage-2` (either AI-recommended and accepted, or clinically overridden to referral).
- **Inputs:**
  - `hba1c_measured_pct` (Floating point, e.g., `6.1%`, range 3.0% – 18.0%)
  - `lab_test_date` (Date picker, defaults to today)
  - `lab_identifier` (Optional laboratory facility or sample ID)

### Step 6: Laboratory Range Presentation & Case Archive
- **Presentation:**
  - The measured HbA1c is classified against clinical standards:
    - `< 5.7%`: **Normal Glycemic Range**
    - `5.7% – 6.4%`: **Prediabetes Range (Dysglycemia Positive)**
    - `≥ 6.5%`: **Diabetes Range (Dysglycemia Positive)**
  - Prominent notice: *"Laboratory categorization is presented according to standard clinical diagnostic criteria. Clinical diagnosis must be confirmed by an authorized medical practitioner."*
- **Final Case State:** Case status is updated to `Stage 2 Complete — Normal` or `Stage 2 Complete — Dysglycemia Identified`. Record is archived in the searchable `Screening History` database.

---

## 3. Edge Cases & Safety Fallbacks

1. **Unrealistic Input Values:** If an entry is biologically extreme (e.g., BMI = 95 kg/m² or Waist = 210 cm), the form accepts the entry only after displaying a soft warning callout (`"Value is outside typical 99th percentile NHANES distribution. Please verify entry."`).
2. **Duplicate Submissions:** Submitting a screening form generates an idempotent case token to prevent duplicate database creation if the user double-clicks.
3. **Pending Review Timeout:** If a case with an elevated screening signal remains unreviewed for $> 72$ hours, it receives an urgent visual tag in the Review Queue (`Attention Required: > 72h Unreviewed`).
4. **Multiple Reviewers:** If a case is reviewed multiple times, the database stores all historical review entries chronologically. The interface displays the latest decision while preserving the complete audit history.
