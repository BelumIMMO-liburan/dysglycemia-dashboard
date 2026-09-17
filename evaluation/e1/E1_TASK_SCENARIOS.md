# Standardized Synthetic Task Scenarios (Phase E1)
## Scripted User-Study Task Set & Fictional Case Profiles

**Document Identifier:** `E1-TASK-SCENARIOS-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  
**Canonical Stimulus Source of Truth:** [`E1_STIMULUS_LOCK.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_STIMULUS_LOCK.md)  

---

## 1. Scenario Design Principles

To ensure that the evaluation measures **system usability, workflow clarity, and mental model comprehension** rather than the participant's independent clinical diagnostic competence, the following rules govern all task scenarios:

1. **Synthetic Data Exclusively:**  
   All inputs are fictitious cases derived to exercise specific model states (elevated vs. lower screening signal). Under no circumstances are participants asked to enter personal medical information.
2. **Procedural Action Instructions:**  
   Participants are **NOT** asked: *"In your clinical opinion, does this person require referral?"*  
   Instead, instructions provide explicit scenario guidance: *"For this exercise, accept the displayed recommendation"* or *"For this exercise, perform an override using the supplied scenario rationale."*
3. **Deterministic State Progression:**  
   The scenarios are sequenced so that participants experience the complete two-stage lifecycle: Intake $\to$ Explanation $\to$ Review $\to$ Override $\to$ Stage-2 HbA1c Lab Assessment $\to$ Historical Audit.
4. **Single Source of Truth:**  
   All case values and expected runtime outputs are locked in [`E1_STIMULUS_LOCK.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_STIMULUS_LOCK.md) and [`E1_SCENARIO_RUNTIME_VERIFICATION.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_SCENARIO_RUNTIME_VERIFICATION.md). Only the Canonical Seven Predictors are presented on task stimulus cards.

---

## 2. Fictional Synthetic Screening Profiles

### Synthetic Profile Alpha (Case Code: `CASE-ALPHA`)
- **Synthetic Screening Profile Narrative:** Middle-aged individual with elevated non-laboratory metabolic indicators.
- **Canonical Seven Model Inputs:**
  1. `Age`: **56** years
  2. `Sex`: **Male** (`male`)
  3. `BMI`: **31.2** kg/m²
  4. `Hypertension History`: **Yes** (`yes`, Doctor diagnosed high blood pressure)
  5. `Smoking History`: **No** (`no`, Smoked fewer than 100 cigarettes in lifetime)
  6. `Waist Circumference`: **102.0** cm
  7. `Sedentary Time`: **480** minutes/day (8.0 hours/day)
- **Verified Frozen Model Behavior (`E1_STIMULUS_LOCK.md`):**
  - Calculated probability = **0.272969 (27.30%)** ($> 0.1389$ operating threshold).
  - Output: **Elevated Screening Signal** / **AI Referral Recommendation: Refer**.
  - Top Positive Factor: **Age (+0.417980, rounded +0.418)** pushes score higher the most; **Hypertension (+0.103343, rounded +0.103)** and **BMI (+0.004917, rounded +0.005)** also push higher.
  - Moderating / Negative Factors: **Sedentary Time (-0.472934, rounded -0.473)**, **Waist Circumference (-0.159560, rounded -0.160)**, **Smoking History: Non-smoker (-0.117616, rounded -0.118)**, and **Biological Sex: Male (-0.026593, rounded -0.027)** push score lower.

### Synthetic Profile Beta (Case Code: `CASE-BETA`)
- **Synthetic Screening Profile Narrative:** Younger adult with lower non-laboratory indicators.
- **Canonical Seven Model Inputs:**
  1. `Age`: **32** years
  2. `Sex`: **Female** (`female`)
  3. `BMI`: **23.5** kg/m²
  4. `Hypertension History`: **No** (`no`)
  5. `Smoking History`: **Yes** (`yes`, Has smoked $\ge 100$ cigarettes in lifetime)
  6. `Waist Circumference`: **74.0** cm
  7. `Sedentary Time`: **300** minutes/day (5.0 hours/day)
- **Verified Frozen Model Behavior (`E1_STIMULUS_LOCK.md`):**
  - Calculated probability = **0.054663 (5.47%)** ($< 0.1389$ operating threshold).
  - Output: **Lower Screening Signal** / **AI Referral Recommendation: No Referral**.
  - Positive Factors: **Smoking History (+0.117616, rounded +0.118)** and **Sex: Female (+0.026593, rounded +0.027)** push score slightly higher.
  - Moderating / Negative Factors: **Age (-0.784738, rounded -0.785)**, **Waist Circumference (-0.773908, rounded -0.774)**, **Sedentary Time (-0.344656, rounded -0.345)**, **BMI (-0.258779, rounded -0.259)**, and **Hypertension: No (-0.103343, rounded -0.103)** push score lower.

---

## 3. Detailed Step-by-Step Task Set

### TASK 1: Stage-1 Non-Laboratory Screening Intake
- **Target Profile:** `CASE-ALPHA`
- **Participant Instruction:**  
  *"Please navigate to 'New Screening' in the sidebar navigation. Enter all seven values provided on Case Card Alpha into the form. Click 'Review Inputs' to inspect the confirmation card, and then click 'Run Screening' to generate the screening result."*
- **Required Participant Actions:**
  1. Clicks `New Screening` in the sidebar navigation.
  2. Fills out all 7 form inputs with Case Alpha values.
  3. Clicks `Review Inputs` (`#submit-screening-btn`) to view the confirmation summary card.
  4. Clicks `Run Screening` (`#run-screening-submit-btn`).
- **Target Outcome:** Screening record created; browser redirects via HTTP 302 to `/screening/<uuid>/result/`.

---

### TASK 2: Screening Result & GAM-Native XAI Interpretation
- **Target Profile:** `CASE-ALPHA` (continued from Task 1)
- **Participant Instruction:**  
  *"Inspect the screening result page for Case Alpha. Review the screening signal badge and the AI referral recommendation. Under the 'Why this result?' section, click 'Show all 7 factors' to expand the complete explanation. Identify which factor pushes the screening score higher the most, and identify at least one factor that moderates or lowers the score."*
- **Required Participant Actions:**
  1. Locates the primary recommendation card (identifies signal as 'Elevated Screening Signal' and recommendation as 'Refer').
  2. Under the `Why this result?` card, clicks `Show all 7 factors` (`#toggle-all-factors-btn`).
  3. Inspects the term contribution bar charts and factor values.
  4. Correctly identifies **Age (+0.418)** as the top positive contributor pushing the score higher.
  5. Correctly identifies a moderating factor pushing the score lower (e.g., **Sedentary Time (-0.473)**, **Waist Circumference (-0.160)**, **Non-smoker (-0.118)**, or **Biological Sex: Male (-0.027)**).
- **Target Outcome:** Participant verbally identifies the recommendation and correctly names at least one elevating and one moderating factor.

---

### TASK 3: Human Guided Review (Accept Recommendation)
- **Target Profile:** `CASE-ALPHA` (continued from Task 2)
- **Participant Instruction:**  
  *"For Case Alpha, the protocol instructs you to accept the AI recommendation. In the Human Review workspace at the bottom of the page, enter your assigned Participant Code into the 'Reviewer Code' field. Then, click 'Accept Recommendation' to finalize your decision."*
- **Required Participant Actions:**
  1. Locates the `Human Review` section on the result page.
  2. Enters assigned code (e.g., `P012`) into the `Reviewer Code` input (`#reviewer_code_accept`).
  3. Clicks `Accept Recommendation` (`#accept-recommendation-btn`).
- **Target Outcome:** Review finalized with `review_action = 'accepted'`; status badge reflects `Accepted: Referral Recommended`; workflow advances with option to proceed to Stage 2.

---

### TASK 4: Human Override Workflow
- **Target Profile:** `CASE-BETA`
- **Participant Instruction:**  
  *"Now navigate to 'New Screening' and enter the seven values for Case Beta. Once the result appears (AI recommends 'No Referral'), the protocol instructs you to OVERRIDE the AI recommendation to REFER. Click 'Override Recommendation' to open the dialog, enter your Participant Code, select the reason 'Referral is preferred as a precaution', enter the scenario note ('Individual reports unrecorded family history of early diabetes'), and click 'Confirm Override'."*
- **Required Participant Actions:**
  1. Enters and submits Case Beta inputs; verifies AI recommends `No Referral` (`Lower Screening Signal`).
  2. In the `Human Review` section, clicks `Override Recommendation` (`#open-override-btn`) to open the modal dialog.
  3. Verifies that the dialog clearly displays the transition: Original AI = `No Referral` $\to$ New Human Decision = `Refer`.
  4. Enters assigned Participant Code into the dialog's `Reviewer Code` field (`#reviewer_code_override`).
  5. Selects the exact deployed structured reason: `Referral is preferred as a precaution` (`code: precautionary_referral`).
  6. Enters the supplied note into the notes field and clicks `Confirm Override` (`#confirm-override-btn`).
- **Target Outcome:** Record saved with `review_action = 'overridden'`; status badge updates to `Overridden to Refer`; original AI recommendation (`No Referral`) remains visibly displayed in the audit trail.

---

### TASK 5: Stage-2 HbA1c Laboratory Assessment
- **Target Profile:** `CASE-ALPHA` ONLY
  *(Note: Case Alpha must be used for Stage 2 so that Case Beta remains in the 'Pending Stage-2 Assessment' state required for Task 6).*
- **Participant Instruction:**  
  *"Navigate back to Case Alpha (either via browser back/history or the screening link). Because Case Alpha has a finalized decision of 'Refer', click 'Proceed to Stage-2 HbA1c Assessment'. Enter a laboratory HbA1c result of 6.1%. Click 'Review HbA1c Value', and then click 'Confirm Laboratory Result'. Observe the displayed laboratory reference range."*
- **Required Participant Actions:**
  1. Opens Case Alpha result view (`/screening/<uuid>/result/`).
  2. Clicks `Proceed to Stage-2 HbA1c Assessment` (`#enter-stage2-btn`).
  3. Enters `6.1` in the HbA1c input field (`#id_hba1c_percent`).
  4. Clicks `Review HbA1c Value` (`#review-hba1c-btn`) to view the verification card.
  5. Clicks `Confirm Laboratory Result` (`#confirm-stage2-btn`).
  6. Observes the resulting categorization: `Prediabetes range (5.7% – 6.4%)`.
  7. Acknowledges the prominent banner stating that this is a clinical reference range, not an automated diagnosis.
- **Target Outcome:** `Stage2Assessment` persisted; laboratory range categorized as `prediabetes_range`; Case Alpha reaches `completed_stage2`.

---

### TASK 6: Audit History & Provenance Traceability
- **Target Profile:** `CASE-BETA` (Historical Audit Ledger)
- **Participant Instruction:**  
  *"Navigate to 'History' in the sidebar navigation. In the audit table, locate the row for Case Beta and click 'View Case'. In the case view, verify whether the original AI recommendation is still visible, identify the recorded human decision, and observe the Stage-2 status."*
- **Required Participant Actions:**
  1. Clicks `History` in the sidebar navigation.
  2. Locates Case Beta in the audit table (identifies `Overridden to Refer` badge).
  3. Clicks `View Case` in the actions column.
  4. In the detailed view, inspects the 3-part timeline and audit ledger:
     - Part 1: Stage-1 Inputs & Original AI Recommendation (`No Referral`, $p \approx 5.5\%$).
     - Part 2: Human Review Decision (`Overridden to Refer` by participant code with timestamp, reason `Referral is preferred as a precaution`, and override note).
     - Part 3: Stage-2 Status (`Pending Stage-2 Assessment` — confirms Case Beta was NOT advanced to Stage 2).
- **Target Outcome:** Participant independently identifies and confirms that the original AI recommendation was permanently preserved and never overwritten by the human override.
