# Phase E2 Instrumentation Requirements & Survey Delivery Architecture
## Comparative Trade-off Analysis & Implementation Backlog

**Document Identifier:** `E2-INSTRUMENTATION-REQ-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Context & Architectural Boundary

In strict accordance with the **Feature Freeze Principle** established in Phase D3 and reinforced in Phase E1:
- **ZERO software instrumentation** (no survey templates, no SUS database models, no question delivery views) was implemented inside the Django application during Phase E1.
- This document defines the engineering requirements and comparative trade-off analysis for Phase E2 (Instrumentation & Preparation), evaluating whether survey delivery should be integrated into Django or managed externally.

---

## 2. Comparative Analysis: Questionnaire Delivery Options

Three architectural configurations were evaluated for administering the post-task evaluation instruments (8-item Comprehension Quiz, 10-item SUS, 5-item Custom Likert, 3 Qualitative items):

| Evaluation Dimension | Option A: Full Django Integration | Option B: Fully External Survey Platform | Option C (Recommended): Hybrid Decoupled Architecture |
| :--- | :--- | :--- | :--- |
| **Architectural Concept** | Build custom Django survey views, database models (`ParticipantSurvey`, `SusResponse`), and form templates directly into the prototype. | Run tasks on the prototype, but collect all participant data, task logs, and survey responses on an external platform (e.g. Qualtrics/Google Forms). | **Prototype runs tasks untouched**; external validated survey tool administers consent & questionnaires; deterministic linkage via **`participant_code`**. |
| **Impact on Frozen Prototype** | **High Risk:** Violates the feature freeze. Adds new database migrations, routes, views, forms, and templates to `research-prototype-v1.0`. | **Zero Risk:** Prototype code remains 100% frozen. | **Zero Risk:** Prototype code remains 100% frozen. Release baseline is untouched. |
| **Test Suite Stability** | Requires writing 20–30 new automated tests; risks destabilizing the verified 144-test baseline. | Baseline 144 automated tests remain completely unchanged. | Baseline 144 automated tests remain completely unchanged. |
| **Audit Trail Integration** | Audit logs and survey scores live in the same SQLite file (`db_study.sqlite3`). | Audit logs live in SQLite; survey responses live in external CSV/spreadsheet. | Audit logs live in `db_study.sqlite3` (`reviewer_code = P012`); survey responses live in external CSV with matching `participant_code = P012`. |
| **Questionnaire Ergonomics** | Must hand-code Likert radio matrices, mobile responsiveness, and validation in CSS/JS. | Commercial/institutional survey platforms provide battle-tested question presentation and validation. | Professional survey platform handles Likert rendering; zero development overhead. |
| **Risk of Data Contamination** | Mixing survey submission traffic into the screening decision-support database. | Complete isolation between experimental stimulus and response capture. | Complete isolation between screening domain data and survey perception data. |
| **Overall Feasibility** | Unnecessary complexity for an undergraduate thesis prototype. | Viable, but requires manual task logging. | **Optimal:** Combines prototype fidelity with survey reliability. |

---

## 3. Formal Architectural Recommendation: Option C (Hybrid Decoupled Architecture)

### Core Operational Mechanism:
1. **The Prototype Remains Frozen:**  
   `research-prototype-v1.0` operates in its approved, verified state running against `db_study.sqlite3`.
2. **Deterministic Linkage via `participant_code`:**  
   - When the participant begins Task 3 (Human Review) and Task 4 (Override), the scenario card instructs them to enter their assigned participant code (e.g., `P012`) into the `Reviewer Code` field.
   - When the participant transitions to the post-task questionnaire, the survey platform prompts: *"Enter your Participant Code: [ P012 ]"*.
3. **Automated Merging:**  
   A simple Python analysis script performs an inner join between `HumanReview.reviewer_code` in SQLite and `participant_code` in the survey export CSV, creating an integrated, auditable dataset with 100% referential integrity.

---

## 4. Phase E2 Implementation Backlog (If Option C is Executed)

When Phase E2 is initiated, the following non-intrusive preparation tasks will be executed:

- [ ] **E2.1 — Digital Survey Instrument Construction:**  
  Build the external digital questionnaire (Google Forms or institutional Qualtrics instance) containing:
  - Participant Code validation (regex `^(P[0-9]{3}|E[0-9]{3})$`).
  - Broad demographic categorizations (Age bracket, education).
  - 8-Item Objective Comprehension Quiz with randomized option presentation.
  - 10-Item standard System Usability Scale (1–5 Likert).
  - 5-Item Exploratory Clarity scale (1–5 Likert).
  - 3 Open-ended qualitative feedback fields.
- [ ] **E2.2 — Physical Scenario & Code Card Packets:**  
  Print/prepare laminated participant code cards (`P001` through `P030`, `E001` through `E005`) and Case Scenario Cards (`CASE-ALPHA` and `CASE-BETA`).
- [ ] **E2.3 — Moderator Observation Sheet:**  
  Produce paper/digital observation logs formatted to capture start/stop times, error taxonomy codes, and assistance levels (0–3) per task.
- [ ] **E2.4 — Data Ingestion & Scoring Script (`scripts/e2_score_eval.py`):**  
  Develop a Python analysis script that:
  - Reads raw survey CSV export.
  - Computes individual and summary SUS scores (Brooke formula).
  - Computes objective quiz scores against the keyed item bank.
  - Queries `db_study.sqlite3` to verify that `HumanReview` records match participant codes.
  - Generates summary demographic and performance tables.
- [ ] **E2.5 — Pilot Verification Session:**  
  Execute the 3–5 participant pilot study as defined in `E1_PILOT_PLAN.md` using `db_pilot.sqlite3`.
