# Hybrid Evaluation & Data Collection Architecture (Phase E2)
## Decoupled Multi-Source Measurement Framework

**Document Identifier:** `E2-HYBRID-ARCH-V1.0`  
**Evaluation Phase:** `E2` (Pilot Instrument Package & Operationalization)  
**Governing Protocol:** `v1.0.3` (`E1-PROTOCOL-2026-V1.0.3`)  
**Stimulus Software:** `research-prototype-v1.0` (Frozen Release)  
**Package Version:** `1.0`  
**Date:** 2026-09-05  

---

## 1. Executive Architectural Overview

Phase E2 establishes the operational data collection architecture for evaluating `research-prototype-v1.0`. To preserve the strict **Feature Freeze Principle** and guarantee zero modification to the validated 144-test prototype, the evaluation adopts a **Decoupled Hybrid Architecture (Option C)**:

```
+----------------------------------------------------------------------------------------------------+
|                             DECOUPLED HYBRID EVALUATION ARCHITECTURE                               |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|    [ PARTICIPANT ]                                                                                 |
|           │                                                                                        |
|           ├───► 1. LOCAL TASK APPARATUS: research-prototype-v1.0 (Django, Frozen)                  |
|           │        - Tasks 1–6 Execution (Intake -> XAI -> Review -> Override -> Stage 2 -> Audit)|
|           │        - Isolated Per-Participant Database: db_study.sqlite3                           |
|           │        - Participant Code entered in Reviewer Code field                               |
|           │                                                                                        |
|           ├───► 2. EXTERNAL MEASUREMENT PLATFORM: Platform-Agnostic Web Form                       |
|           │        - Closed-Book Administration post-Task 6                                        |
|           │        - Participant Code entered as first required field                              |
|           │        - Section 2: 8 Objective Comprehension Items (Protocol-Defined)                 |
|           │        - Section 3: 10 Indonesian SUS Items (Sharfina & Santoso, 2016)                 |
|           │        - Section 4: 5 Exploratory Clarity Items                                        |
|           │        - Section 5: 3 Open-Ended Qualitative Feedback Items                            |
|           │                                                                                        |
|    [ MODERATOR ]                                                                                   |
|           │                                                                                        |
|           └───► 3. STANDARDIZED OBSERVATION TOOL: Printed Sheet / Observer Ledger                  |
|                    - Participant Code recorded at header                                           |
|                    - Real-time Task Success logging (Binary 0 / 1)                                 |
|                    - Assistance Level tracking (0, 1, 2, 3)                                        |
|                    - Behavioral Error Taxonomy categorization                                      |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
                                      │
                                      ▼
                        [ DETERMINISTIC LINKAGE KEY ]
                             participant_code
                       (e.g., PILOT001 or P001)
                                      │
                                      ▼
+----------------------------------------------------------------------------------------------------+
|                                    OFFLINE RELATIONAL CSV INTEGRATION                              |
|   participants.csv | task_results.csv | comprehension_responses.csv | sus_responses.csv            |
|   perception_responses.csv | qualitative_feedback.csv | session_manifest.csv                       |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Methodological & Technical Rationale

The hybrid architecture was formally selected over an embedded Django survey module (Option A) or fully synthetic simulation (Option B) for the following reasons:

1. **Preservation of the Frozen Software Release:**
   Embedding survey forms, SUS Likert scales, or quiz models inside the Django application would violate the completed Phase D3 / E1 software audit. It would require modifying database models, templates, routing tables, and view controllers, invalidating the 144 automated unit/integration tests and baseline SHA-256 hashes.
2. **Elimination of Software Regression Risks:**
   Adding new database tables and view forms creates a risk of regression defects in the clinical decision-support pipeline (Stage-1 intake, PyGAM inference, native decomposition, and override ledger).
3. **Decoupled Data Governance & Privacy:**
   Subjective psychometric ratings, objective quiz answers, and task observations are collected outside the operational screening prototype database. This maintains a clean separation of concerns between operational screening/review workflow logs and psychometric evaluation instruments.
4. **Resilient Offline Data Export:**
   Standard external survey instruments export directly to clean relational CSV formats, eliminating custom database migration logic and complex database extraction scripts.

---

## 3. Strict Environment Separation

To prevent cross-contamination of evaluation data, three completely separated environments are enforced:

```
+----------------------------------------------------------------------------------------------------+
|                                   DATA ENVIRONMENT SEPARATION RULES                                |
+--------------------+----------------------------+--------------------------------------------------+
| Environment        | Active Database            | Governed Purpose & Isolation Rule                |
+--------------------+----------------------------+--------------------------------------------------+
| DEVELOPMENT / DEMO | db.sqlite3                 | Development testing, QA runs, and regression     |
|                    |                            | checks. Records MUST NEVER mix with study data.  |
+--------------------+----------------------------+--------------------------------------------------+
| PILOT STUDY        | db_study.sqlite3 (Active)  | 3–5 participant operational feasibility trial.   |
|                    | Restored per session from  | Isolated per-session archives: PILOT001..PILOT005|
|                    | db_session_template.sqlite3| Records MUST NEVER be pooled into formal study.  |
+--------------------+----------------------------+--------------------------------------------------+
| FORMAL USER STUDY  | db_study.sqlite3 (Active)  | 24–30 participant formal thesis evaluation.      |
| (Future Phase)     | Restored per session from  | Isolated per-session archives: P001..P030.       |
|                    | db_session_template.sqlite3| Initiated only after formal supervisor signoff.  |
+--------------------+----------------------------+--------------------------------------------------+
```

### Absolute Isolation Mandates:
- **No Shared Records:** Under no circumstances may a development or QA record appear in a pilot or formal study database.
- **No Pilot Pooling:** Pilot participants (`PILOT001`–`PILOT005`) are evaluated strictly for operational stress-testing, session timing, and instruction clarity. Pilot data **must not** be pooled into the final formal study analytical dataset ($N = 24\text{--}30$).
- **No Dry-Run Contamination:** The synthetic researcher dry-run (`DRYRUN001`) utilizes a dedicated dry-run database (`db_dryrun.sqlite3`), leaving `db_study.sqlite3` completely unseeded.

---

## 4. Relational Data Linkage & Cardinality

All three evaluation instruments link deterministically via the pseudonymous `participant_code`:
1. **Local Prototype:** Captured in `HumanReview.reviewer_code` during Task 3 (`CASE-ALPHA`) and Task 4 (`CASE-BETA`).
2. **External Questionnaire:** Captured as the first mandatory text field (`SECTION 1`).
3. **Moderator Observation Sheet:** Recorded in the page header and per-task rows.
4. **Session Archive Manifest:** Logged alongside the SQLite archive hash and export filenames.

### Expected Relational Cardinality per Completed Session:
For every completed synthetic task session (Tasks 1–6), the active session database must reflect the following exact entity counts:
- **`ScreeningRecord`:** Exactly **2** (One for `CASE-ALPHA`, one for `CASE-BETA`).
- **`ScreeningExplanation`:** Exactly **2** (Additive GAM explanations for Alpha and Beta).
- **`HumanReview`:** Exactly **2** (`reviewer_code = participant_code` for both):
  - `CASE-ALPHA`: `review_action = 'accepted'` (Decision: `Refer`).
  - `CASE-BETA`: `review_action = 'overridden'` (AI: `No Referral` $\to$ Decision: `Refer`, reason: `precautionary_referral`).
- **`Stage2Assessment`:** Exactly **1** (`CASE-ALPHA` only, HbA1c $6.1\%$, `prediabetes_range`, status: `completed_stage2`).
- **`CASE-BETA` Lifecycle State:** **`Pending Stage-2 Assessment`** (`pending_stage2`, verifying that HbA1c was not entered for Case Beta).

---

## 5. Epistemic Governance Summary

1. **Non-Clinical Software Evaluation:** All instruments evaluate software ergonomics, interface comprehensibility, and workflow naturalness. No clinical diagnostic accuracy or patient health outcomes are evaluated.
2. **Offline Scoring:** External questionnaires do not compute or display scores to participants. All SUS and comprehension aggregations are computed offline during formal analysis.
3. **No Direct PII in Analytical Datasets:** No direct PII is collected in the analytical questionnaire, dashboard workflow records, moderator analytical dataset, or analysis exports. Any identity information required for consent/recruitment is stored separately under administrative governance (Vault A).
