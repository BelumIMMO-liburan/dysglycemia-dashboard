# Task Construct & Error Matrix (Phase E1)
## Experimental Task Operationalization & Behavioral Metrics

**Document Identifier:** `E1-TASK-CONSTRUCT-MATRIX-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Operational Task Definitions

To eliminate subjective evaluator bias during live study sessions, each task is mapped to an underlying scientific construct with pre-specified criteria for **Success**, **Critical Errors**, and **Non-Critical Errors**.

- **Success (Binary = 1):** The participant completes the required action independently or with Level 1 assistance only.
- **Partial Success (Binary = 0 in primary strict analysis, reported separately):** Completed only after Level 2 directional prompting.
- **Failure (Binary = 0):** The participant cannot complete the task, abandons the task, requires direct Level 3 procedural demonstration, or commits an uncorrected critical error.

---

## 2. Master Task Construct Matrix

| Task ID & Title | Feature Exercised | Research Construct | Success Criterion | Critical Error (Task Failure) | Non-Critical Error (Assistance / Delay) | Observation Fields Logged | Related RQ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Task 1:**<br>Start Screening | `/screening/new/`<br>7-feature form, `Review Inputs`, `Run Screening` | Input Ergonomics, Form Operability & Validation Clarity | Participant enters all 7 fields accurately and submits without uncorrected validation failures. | - Submitting incorrect values and ignoring inline errors.<br>- Abandoning form or navigating away. | - Brief input typing error corrected via inline error message.<br>- Hesitation locating submit button (<15s). | `t1_success` (0/1)<br>`t1_assist_level` (0–3)<br>`t1_input_errors` (count)<br>`t1_time_sec` (opt) | **RQ3** (Usability) |
| **Task 2:**<br>Interpret Result & XAI | `/screening/<uuid>/result/`<br>Recommendation badge, `Why this result?`, `Show all 7 factors` | Explainability Usability, Directional Factor Comprehension | Participant correctly identifies: (a) AI recommendation (Refer), (b) top elevating factor (Age), (c) moderating factor (Sedentary/Waist/Smoking). | - Misidentifying AI recommendation (e.g. reading 'Refer' as 'No Refer').<br>- Asserting moderating factor increases risk. | - Difficulty locating the 'Show all 7 factors' toggle (<20s).<br>- Asking moderator where the chart is located. | `t2_success` (0/1)<br>`t2_recom_correct` (0/1)<br>`t2_xai_top_correct` (0/1)<br>`t2_xai_mod_correct` (0/1) | **RQ3** (Usability)<br>**RQ4** (Comprehension) |
| **Task 3:**<br>Human Review Accept | `/screening/<uuid>/result/`<br>Human Review panel, reviewer code input, `Accept Recommendation` | Review Workflow Learnability, Reviewer Attribution Ergonomics | Participant enters assigned Participant Code into Reviewer Code field and successfully clicks `Accept Recommendation`. | - Submitting without entering Reviewer Code (ignoring validation).<br>- Clicking Override button instead of Accept. | - Entering participant code in lower case or with minor typo.<br>- Hesitation locating Accept button. | `t3_success` (0/1)<br>`t3_assist_level` (0–3)<br>`t3_action_correct` (0/1) | **RQ3** (Usability) |
| **Task 4:**<br>Human Override | Case Beta modal `<dialog>`, reason `Referral is preferred as a precaution`, notes field | Override Transparency, Human Agency, Error-Prevention Guardrails | Participant successfully triggers override modal, selects instructed reason, enters note, and confirms. | - Overriding to wrong referral state.<br>- Failing to enter structured reason or notes.<br>- Canceling modal without completing. | - Selecting wrong reason initially, then correcting.<br>- Attempting to submit empty note before seeing validation message. | `t4_success` (0/1)<br>`t4_assist_level` (0–3)<br>`t4_reason_selected`<br>`t4_override_errors` | **RQ3** (Usability)<br>**RQ4** (Comprehension) |
| **Task 5:**<br>Stage-2 HbA1c Laboratory Assessment | `/screening/<uuid>/stage2/`<br>*(Case Alpha only)*<br>HbA1c entry, `Review HbA1c Value`, `Confirm Laboratory Result` | Two-Stage Progression Operability, Lab Output Comprehension | Participant enters 6.1% HbA1c for Case Alpha, confirms, and correctly identifies category as 'Prediabetes range'. | - Submitting value outside physiological range uncorrected.<br>- Stating that 6.1% means "individual definitely has diabetes". | - Typing comma instead of period in decimal field.<br>- Re-reading disclaimer text multiple times. | `t5_success` (0/1)<br>`t5_assist_level` (0–3)<br>`t5_range_identified` | **RQ3** (Usability)<br>**RQ4** (Comprehension) |
| **Task 6:**<br>Audit History & Traceability | `/history/`<br>Audit table, `View Case` action, Case Beta audit ledger | System Auditability, Temporal Provenance Transparency | Participant locates Case Beta in History, clicks `View Case`, and confirms original AI recommendation is preserved. | - Claiming the AI recommendation was erased or overwritten by the override.<br>- Unable to locate history table. | - Difficulty locating target record in table.<br>- Scrolling past target record initially. | `t6_success` (0/1)<br>`t6_assist_level` (0–3)<br>`t6_ai_preserved_seen` | **RQ2** (Auditability)<br>**RQ3** (Usability) |

---

## 3. Moderator Assistance Hierarchy

Assistance is standardized to ensure cross-participant consistency:

```
[Level 0: Independent] --> Participant completes task with zero prompting.
        |
        v (Participant hesitates >30s or asks a question)
[Level 1: General Prompt] --> "Please continue using the information available on the screen."
        |
        v (Participant remains stuck >30s or attempts incorrect path)
[Level 2: Directional Hint] --> "Look at the options inside the Human Review panel on the right."
        |
        v (Participant completely blocked or expresses distress)
[Level 3: Procedural Demonstration] --> Moderator demonstrates the action. Task scored as FAILURE.
```

- **Strict Logging:** The highest assistance level administered during a task is recorded in the task result schema (`assist_level` $\in \{0, 1, 2, 3\}$).
- **Assisted Completion:** Any task requiring Level 3 assistance is classified as `task_success = 0`.
