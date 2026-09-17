# User-Study Data Linkage Decision

**Document Status:** CURRENT STATUS: NOT YET LOCKED  
**Date:** 2026-09-05  
**Context:** Preparation for formal user-study protocol design following the D3 feature freeze.

---

## 1. Problem Statement

In the completed prototype, the human review interaction captures:
- `reviewer_code` (anonymous alphanumeric code, max 32 characters, e.g. `R001`, `HP-03`)
- `screening_id` (UUIDv4)
- `created_at` (timestamp)

A critical architectural decision must be addressed before formal participant evaluation:
**Is the existing `reviewer_code` field sufficient to connect system interactions to the planned external evaluation dataset, or does the study protocol require a distinct participant identifier structure?**

---

## 2. Distinction Between Identifiers

| Identifier Type | Current System Manifestation | Intended Scope |
| :--- | :--- | :--- |
| **Reviewer Code** | `HumanReview.reviewer_code` (max 32 chars) | Identifies the operator acting as reviewer on a screening record. Suitable for pseudonymous role assignment. |
| **Research Participant ID** | Not stored in database | Identifies the human research subject participating in the controlled usability trial (e.g. `P01`, `P02`). |
| **Evaluation Session ID** | Not stored in database | Identifies a specific experimental block or scenario assigned to a participant. |

---

## 3. Linkage Options Under Consideration

### Option A: Direct Mapping via Reviewer Code
- The study protocol assigns each research subject a unique anonymous `reviewer_code` (e.g., `PARTICIPANT-01`).
- The participant enters this code when submitting reviews.
- Survey responses (SUS, qualitative feedback) collected in external instruments (e.g. Google Forms / Qualtrics) record the matching identifier.
- **Advantage:** Requires zero database schema changes or UI modification.
- **Limitation:** Relies on manual input compliance; does not track multi-task ordering within the database itself.

### Option B: External Session Orchestration
- The application remains completely uninstrumented for survey logic.
- An external protocol manager or researcher logs task completion times and maps screening UUIDs to participant trial logs.
- **Advantage:** Preserves maximum prototype cleanliness and zero survey-bias in the software itself.
- **Limitation:** Requires protocol supervisor to log case UUIDs during sessions.

---

## 4. Current Formal Status

**CURRENT STATUS: NOT YET LOCKED.**

This decision is deferred to the formal user-study protocol design phase. The prototype is frozen without premature survey instrumentation or hardcoded participant tracking.
