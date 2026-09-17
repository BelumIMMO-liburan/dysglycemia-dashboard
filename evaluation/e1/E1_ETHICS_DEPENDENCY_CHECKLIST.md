# Ethics & Institutional Dependency Checklist (Phase E1)
## Prerequisite Verification for Human Subject Data Collection

**Document Identifier:** `E1-ETHICS-CHECKLIST-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Dual-Status Determination

In accordance with rigorous research governance, this evaluation maintains an explicit separation between **Technical/Methodological Readiness** and **Institutional Authorization for Data Collection**.

```
+-----------------------------------------------------------------------------------+
|                        ETHICS & AUTHORIZATION STATUS GATE                         |
+-----------------------------------------------------------------------------------+
| 1. TECHNICAL & METHODOLOGICAL READINESS:       [ X ] READY                        |
|    - Software frozen (research-prototype-v1.0)                                    |
|    - Clean study DB initialized (db_study.sqlite3)                                |
|    - 144 automated tests passing                                                  |
|    - Protocol-defined task scenarios, item bank, Indonesian SUS, and analysis plan|
+-----------------------------------------------------------------------------------+
| 2. INSTITUTIONAL AUTHORIZATION FOR DATA COLLECTION: [   ] PENDING AUTHORIZATION   |
|    - Academic thesis supervisor protocol review and signoff                       |
|    - Departmental / institutional ethics approval or formal exemption             |
|    - Participant information and consent sheet institutional stamping            |
+-----------------------------------------------------------------------------------+
```

**CRITICAL MANDATE:**  
Under **NO CIRCUMSTANCES** may recruitment of human participants or formal respondent data collection begin until Status Gate 2 is formally marked as **AUTHORIZED** by the academic thesis supervisor and relevant institutional authority.

---

## 2. Institutional Prerequisite Checklist

| Gate Item | Requirement Description | Verification Artifact | Current Status | Responsible Role |
| :--- | :--- | :--- | :--- | :--- |
| **Item 1: Technical Freeze** | Verification that prototype software and model are 100% frozen with zero open P0/P1 defects. | `docs/SYSTEM_RELEASE_MANIFEST.md`<br>`docs/USER_STUDY_READINESS_CHECKLIST.md` | **COMPLETED** | Student Researcher |
| **Item 2: Protocol Design Lock** | Complete specification of evaluation protocol, task scenarios, comprehension items, and analysis plan. | Phase E1 Document Suite (`evaluation/e1/*.md`) | **COMPLETED** | Student Researcher |
| **Item 3: Supervisor Review** | Formal review of Phase E1 protocol design by the academic thesis supervisor. | Signed Supervisor Approval Memo / Email Confirmation | **PENDING REVIEW** | Academic Supervisor |
| **Item 4: Institutional Review** | Submission of protocol to Faculty/Department Ethics Review Board or institutional research committee (as required by university policy). | Institutional Ethics Clearance Number OR Formal Exemption Notice | **PENDING SUBMISSION** | Faculty Committee / Supervisor |
| **Item 5: Consent Stamping** | Finalization of Participant Information & Consent Form with institutional contact details. | Stamped / Approved Consent Form PDF | **PENDING AUTHORIZATION** | Student Researcher |
| **Item 6: Pilot Clearance** | Authorization to conduct small-scale (3–5 participant) pilot testing prior to formal study. | Pilot Study Authorization Memo | **PENDING SUPERVISOR SIGNOFF** | Academic Supervisor |

---

## 3. Required Institutional Signoff Matrix

Prior to logging Participant `P001`:

```
================================================================================
INSTITUTIONAL AUTHORIZATION SIGN-OFF
================================================================================

Student Researcher Declaration:
I confirm that the research protocol, task scenarios, measurement instruments, and
data governance specifications are fully prepared, frozen, and compliant with
academic integrity and non-diagnostic research prototype boundaries.

Signature: ___________________________ Date: ____________________


Academic Thesis Supervisor Approval:
I have reviewed the Phase E1 evaluation protocol (E1-PROTOCOL-2026-V1.0.3) and
confirm technical/methodological readiness. Pilot execution may begin only after
applicable supervisor/institutional requirements for pilot participant involvement
have been formally satisfied.

Supervisor Name: _____________________________________________
Signature:       ___________________________ Date: ____________________
Institutional Clearance Code (if applicable): ________________________
================================================================================
```
