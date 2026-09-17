# External Survey Platform Comparative Analysis & Deployment Specification (Phase E2)
## Platform-Agnostic Web Form Administration

**Document Identifier:** `E2-SURVEY-PLATFORM-DECISION-V1.0`  
**Evaluation Phase:** `E2` (Pilot Instrument Package & Operationalization)  
**Governing Protocol:** `v1.0.3` (`E1-PROTOCOL-2026-V1.0.3`)  
**Package Version:** `1.0`  
**Date:** 2026-09-05  
**Platform Selection Status:** **PENDING SUPERVISOR / INSTITUTIONAL PLATFORM CHOICE**  

---

## 1. Context & Architectural Mandate

In accordance with the **Hybrid Decoupled Evaluation Architecture** established in [`E2_HYBRID_COLLECTION_ARCHITECTURE.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/E2_HYBRID_COLLECTION_ARCHITECTURE.md), the post-task evaluation battery (8 comprehension questions, 10 Indonesian SUS items, 5 clarity items, and 3 open-ended feedback prompts) is administered via an **external web survey platform**.

To ensure that the scientific methodology is resilient to institutional tooling requirements, the questionnaire design is strictly platform-agnostic:
- Scientific items, wording, item order, and scales are defined in [`E2_EXTERNAL_QUESTIONNAIRE_BLUEPRINT_ID.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/forms/E2_EXTERNAL_QUESTIONNAIRE_BLUEPRINT_ID.md).
- Privacy and administration rules are codified in [`E2_EXTERNAL_FORM_CONFIGURATION.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/forms/E2_EXTERNAL_FORM_CONFIGURATION.md).
- No commercial vendor is hard-coded into the scientific protocol.

---

## 2. Comparative Analysis of Candidate Platforms

```
+----------------------------------------------------------------------------------------------------+
|                               CANDIDATE SURVEY PLATFORM COMPARISON MATRIX                          |
+-------------------+-------------------+--------------------+-------------------+-------------------+
| Feature / Demand  | Google Forms      | Microsoft Forms    | Qualtrics XM      | Institutional LMS |
+-------------------+-------------------+--------------------+-------------------+-------------------+
| Institutional     | Widely accessible | Common in MS 365   | Industry standard | Highly integrated |
| Availability      | via personal/edu  | university domains | if campus-licensed| with course portals|
+-------------------+-------------------+--------------------+-------------------+-------------------+
| Zero-Login Direct | YES (if email     | YES (if set to     | YES (anonymous    | NO (usually       |
| Access Capability | collection off)   | "Anyone can reply")| survey link)      | requires student) |
+-------------------+-------------------+--------------------+-------------------+-------------------+
| Participant Code  | YES (Regex text   | YES (Single-line   | YES (Text input   | YES (Form field)  |
| Validation        | pattern matching) | text validation)   | + regex check)    |                   |
+-------------------+-------------------+--------------------+-------------------+-------------------+
| Section Page-     | YES (Enforces     | YES (Branching /   | YES (Page breaks  | Variable          |
| Breaks (Progression) sequential flow) | Section blocks)    | + block timing)   |                   |
+-------------------+-------------------+--------------------+-------------------+-------------------+
| Mandatory Item    | YES (Toggle per   | YES (Toggle per    | YES ('Force       | YES               |
| Enforcement       | question)         | question)          | response' option) |                   |
+-------------------+-------------------+--------------------+-------------------+-------------------+
| Clean CSV Export  | YES (Standard     | YES (Excel export  | YES (CSV / TSV    | Variable (often   |
| Compatibility     | Google Sheet/CSV) | converted to CSV)  | with clean headers)| proprietary format|
+-------------------+-------------------+--------------------+-------------------+-------------------+
| Administrative    | Near zero         | Near zero          | Moderate setup    | High overhead     |
| Overhead          |                   |                    |                   |                   |
+-------------------+-------------------+--------------------+-------------------+-------------------+
```

---

## 3. Platform Configuration Recipes

Whichever candidate platform is approved by the academic thesis supervisor and faculty ethics committee, the deployment must comply with the following settings:

### 3.1 Google Forms Deployment Recipe
1. **Settings $\to$ Responses:**
   - `Collect email addresses` = **Do not collect**.
   - `Send responders a copy of their response` = **Off**.
   - `Allow response editing` = **Off**.
   - `Limit to 1 response` = **Off** *(Critical: turning this on forces participants to log into a Google Account, capturing user identities without authorization)*.
2. **Settings $\to$ Presentation:**
   - `Show progress bar` = **On**.
   - `Shuffle question order` = **Off** *(Strict requirement: SUS items alternate positive/negative and must preserve standard order)*.
   - `Confirmation message` = *"Terima kasih. Respons kuesioner Anda telah berhasil direkam. Silakan beri tahu fasilitator bahwa Anda telah selesai."*
   - `Show link to submit another response` = **Off**.
   - `View results summary` = **Off**.
3. **Settings $\to$ Quizzes:**
   - `Make this a quiz` = **Off** *(Do not display correct answers or immediate scores to participants; scoring is conducted offline during data analysis)*.

### 3.2 Microsoft Forms Deployment Recipe
1. **Settings $\to$ Who can fill out this form:**
   - Select **"Anyone can respond"** *(Prevents institutional domain login requirements)*.
2. **Settings $\to$ Options for responses:**
   - `Accept responses` = **Checked**.
   - `Show progress bar` = **Checked**.
   - `Shuffle questions` = **Unchecked** *(Order must remain fixed)*.
3. **Response Validation:**
   - Configure question 1 (`participant_code`) with text restrictions ensuring valid code syntax (e.g., `PILOT001` or `P001`).

### 3.3 Qualtrics XM Deployment Recipe
1. **Survey Flow:**
   - Organize into 5 sequential blocks matching Blueprint sections.
   - Set Response Requirements to **Force Response** for all items in Sections 1–4.
2. **Survey Options $\to$ Security:**
   - `Anonymize responses` = **Enabled** *(Strips IP addresses and location coordinates)*.
   - `Prevent ballot box stuffing` = **Off** *(To allow researcher multiple sequential terminal uses)*.
   - Set distribution channel to **Anonymous Link**.

---

## 4. Current Approval Status

- **Status:** **PENDING SUPERVISOR / INSTITUTIONAL PLATFORM CHOICE**
- **Recommendation:** **Google Forms** or **Microsoft Forms** is recommended for rapid, low-friction pilot feasibility testing ($N = 3\text{--}5$), provided all email/login collection toggles are verified as disabled.
- **Action Required:** The student investigator will present this document and [`E2_EXTERNAL_QUESTIONNAIRE_BLUEPRINT_ID.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/forms/E2_EXTERNAL_QUESTIONNAIRE_BLUEPRINT_ID.md) to the academic supervisor for formal tool selection prior to pilot launch.
