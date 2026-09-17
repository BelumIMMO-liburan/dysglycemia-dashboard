# Pilot Study Evaluation Plan (Phase E1)
## Pre-Evaluation Feasibility & Protocol Refinement

**Document Identifier:** `E1-PILOT-PLAN-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  
**Canonical Stimulus Authority:** [`E1_STIMULUS_LOCK.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_STIMULUS_LOCK.md)  

---

## 1. Pilot Purpose & Rationale

Before launching the full formal evaluation ($N = 24\text{--}30$), a small-scale, tightly controlled **Pilot Study** ($N = 3\text{ to }5$) will be conducted.

> [!IMPORTANT]
> **Pilot / Ethics Sequencing Notice:**  
> Protocol readiness does NOT authorize contacting pilot participants. Pilot execution may begin only after applicable academic supervisor and institutional ethics requirements for pilot participant involvement have been formally satisfied. If institutional ethics approval is required before pilot data collection, obtain it first.

The pilot study does **NOT** collect data for final thesis hypothesis or descriptive reporting. Its sole purpose is **procedural stress-testing**:
1. Verifying that task scenario instructions are interpreted unambiguously by lay users.
2. Confirming that total session duration remains within the target 30–45 minute envelope.
3. Identifying any confusing or double-barreled comprehension question wording.
4. Ensuring that moderator assistance rules function smoothly in real time.
5. Testing the end-to-end data linkage from browser $\to$ `db_study.sqlite3` $\to$ survey CSV export.

---

## 2. Pilot Cohort Specifications

- **Sample Size:** $N = 3\text{ to }5$ participants (e.g., student peers or departmental colleagues).
- **Coding Scheme:** `PILOT-01`, `PILOT-02`, `PILOT-03`, `PILOT-04`, `PILOT-05`.
- **Absolute Non-Reuse Rule:**  
  Pilot participants **MUST NOT BE RE-RECRUITED** or included in the final formal evaluation dataset. Familiarity with the scenario outcomes or comprehension quiz would introduce severe learning bias.
- **Database Segregation:**  
  Pilot sessions run on a temporary test database (`db_pilot.sqlite3`). Following completion of the pilot, `db_pilot.sqlite3` is archived and the formal study database (`db_study.sqlite3`) is freshly verified at zero state.

---

## 3. Pilot Verification Gate Criteria

| Dimension | Pilot Test Objective | Verification Standard | Failure Remediation Action |
| :--- | :--- | :--- | :--- |
| **Instruction Clarity** | Task instructions are clear and actionable without moderator improvisation. | 100% of pilot users understand Task 1–6 objectives without asking for basic clarification. | Rewrite scenario text cards; clarify phrasing. |
| **Session Timing** | Total duration is realistic and manageable. | Mean session duration between 30 and 45 minutes; no session exceeding 50 minutes. | Streamline orientation walkthrough or reduce redundant scenario reading. |
| **Comprehension Items** | Quiz items test conceptual understanding rather than linguistic tricks. | No pilot participant reports confusion over question grammar; item distractors appear plausible. | Refine question stem; revise ambiguous options; update item bank. |
| **Moderator Protocol** | Moderator adheres strictly to Level 0–3 assistance hierarchy without spontaneous hints. | Moderator maintains standardized script; assistance triggers recorded accurately. | Re-train moderator; tighten scripting in Moderator Guide. |
| **Data Linkage** | Reviewer code successfully connects database record to survey questionnaire. | SQL query confirms `HumanReview.reviewer_code == participant_code`; zero orphan records. | Fix participant coding instructions or survey ID validation rule. |
| **Technical Stability** | Prototype runs locally with zero crashes, unhandled 500 errors, or database lockups. | 0 server exceptions in Django console log; 0 JavaScript browser console errors. | Log bug report; if P0/P1 defect discovered, patch with version bump before study lock. |

---

## 4. Protocol Change Policy & Versioning Rules

### 4.1 Permitted Post-Pilot Modifications
Modifications to the evaluation protocol are **explicitly permitted** following the pilot evaluation, provided they are documented:
- Clarifications to scenario instructions.
- Phrasing improvements to comprehension items in `E1_COMPREHENSION_ITEM_BANK.md`.
- Layout refinements to external survey forms.
- Re-calibration of time estimates.

### 4.2 Strict Post-Launch Freeze Rule
Once the **first formal study participant (`P001`)** signs consent and begins Task 1:
- **FEATURE & PROTOCOL FREEZE:**  
  No changes to task scenarios, comprehension items, SUS administration, scoring rules, or inclusion criteria are allowed.
- **Protocol Version Lock:**  
  If an unforeseen critical defect mandates a protocol change mid-study, data collection must be halted immediately, the protocol version bumped (e.g., `Version 1.1`), existing data isolated, and the change fully documented in `E1_PROTOCOL_CHANGELOG.md`. Under no circumstances may a study protocol be modified silently.
