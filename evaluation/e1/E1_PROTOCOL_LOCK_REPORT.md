# Protocol Lock & Evaluation Signoff Report (Phase E1)
## Formal Gate Signoff for Protocol Version 1.0.3

**Document Identifier:** `E1-LOCK-REPORT-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  
**Gate Determination:** **PROTOCOL v1.0.3 READY FOR SUPERVISOR / INSTITUTIONAL PILOT REVIEW**  

---

## 1. Executive Protocol Lock Statement

Phase E1 establishes the formal, frozen methodology for evaluating the clinical decision-support research prototype (`research-prototype-v1.0`). Following initial drafting (v1.0), Phase-5 factual reconciliation (v1.0.1), and instrument validity correction (v1.0.2), this final revision (**v1.0.3**) executes exhaustive cross-document reconciliation of synthetic case stimuli against frozen runtime evidence prior to any participant contact.

Specifically, Protocol v1.0.3:
1. Establishes [`E1_STIMULUS_LOCK.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_STIMULUS_LOCK.md) as the single canonical source of truth for all synthetic case profiles.
2. Reconciles all representations of `CASE-ALPHA` ($p = 0.272969$, Refer, Elevated Screening Signal) and `CASE-BETA` ($p = 0.054663$, No Referral, Lower Screening Signal) across all 21 artifacts.
3. Expunges all contradictory stale demographic values and non-model variables (SBP, DBP, blood pressure medication, cigarettes/day, physical activity min/wk).
4. Restricts all task cards exclusively to the Canonical Seven Predictors: `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, and `sedentary_minutes_day`.
5. Enforces frozen UI copy (`Elevated Screening Signal`, `Lower Screening Signal`, `Refer`, `No Referral`) and audited clinical terminology.
6. Codifies explicit pilot/ethics sequencing: technical readiness does NOT authorize participant recruitment or contact prior to necessary supervisor and ethics clearances.

All experimental designs, task scenarios, psychometric instruments, data schemas, and analytical procedures have been documented, cross-referenced, and methodologically locked. In accordance with the **Feature Freeze Principle**, zero lines of application code or model parameters were modified during this phase.

```
+-----------------------------------------------------------------------------------+
|                        PHASE E1 PROTOCOL LOCK VERIFICATION                        |
+-----------------------------------------------------------------------------------+
| Stimulus Software Release:       research-prototype-v1.0                          |
| Automated Test Suite Status:     144 / 144 Passing (0 Errors, 0 Failures)         |
| GAM Final Model Hash (SHA256):   204a94ff072ef4f1edecebf5a643738c... [VERIFIED]  |
| Preprocessor Hash (SHA256):      6e56a01993a4a6971eb62c82699c49da... [VERIFIED]  |
| Model Specification Hash:        7d2a5eb9c349dabfca4f5387161c7883... [VERIFIED]  |
| Final Test Predictions Hash:     fac969a00df57d6686c36b09e3de6585... [VERIFIED]  |
| Frozen Operating Threshold:      0.1389 (Immutable)                               |
| Formal Study Database:           db_study.sqlite3 (0 Domain Records)              |
| Evaluation Protocol Version:     v1.0.3 (E1-PROTOCOL-2026-V1.0.3)                 |
| Total Physical Artifacts:        21 Files (Physically Audited)                    |
| Protocol Status:                 READY FOR SUPERVISOR / INSTITUTIONAL PILOT REVIEW|
+-----------------------------------------------------------------------------------+
```

---

## 2. Evaluation Suite Physical Component Audit (21 Files)

| # | Protocol Artifact File | Governing Scope & Content | Verification Status |
| :--- | :--- | :--- | :--- |
| 1 | `E1_STIMULUS_LOCK.md` | Single canonical source of truth for synthetic stimuli. | **LOCKED (v1.0.3)** |
| 2 | `E1_3_FINAL_RECONCILIATION_REPORT.md` | Phase E1.3 cross-document reconciliation gate report. | **LOCKED (v1.0.3)** |
| 3 | `E1_SCENARIO_RUNTIME_VERIFICATION.md` | Exact runtime mathematical execution and factor decomposition. | **LOCKED (v1.0.3)** |
| 4 | `E1_TASK_SCENARIOS.md` | Standardized synthetic task scenarios (Tasks 1–6) using Case Alpha & Beta. | **LOCKED (v1.0.3)** |
| 5 | `E1_MODERATOR_GUIDE.md` | Bilingual verbatim facilitator script, UI button copy, debriefing protocol. | **LOCKED (v1.0.3)** |
| 6 | `E1_EVALUATION_PROTOCOL.md` | Master evaluation protocol, research questions, experimental flow. | **LOCKED (v1.0.3)** |
| 7 | `E1_RQ_CLAIM_EVIDENCE_MATRIX.md` | Strict mapping of RQs to evidence layers; allowed vs prohibited claims. | **LOCKED (v1.0.3)** |
| 8 | `E1_PARTICIPANT_AND_SAMPLING_PLAN.md` | Two-layer participant plan ($N=24\text{--}30$ primary, $N=3\text{--}5$ expert); linkage lock. | **LOCKED (v1.0.3)** |
| 9 | `E1_TASK_CONSTRUCT_MATRIX.md` | Behavioral error taxonomy, success criteria, 4-level assistance hierarchy. | **LOCKED (v1.0.3)** |
| 10 | `E1_MEASUREMENT_INSTRUMENT_SPEC.md` | Indonesian SUS (Sharfina & Santoso 2016), scoring, and benchmark citations. | **LOCKED (v1.0.3)** |
| 11 | `E1_COMPREHENSION_ITEM_BANK.md` | 8-item protocol-defined objective comprehension battery (EN + ID). | **LOCKED (v1.0.3)** |
| 12 | `E1_ANALYSIS_PLAN.md` | Frozen descriptive statistics plan, missing data rules, benchmark caveats. | **LOCKED (v1.0.3)** |
| 13 | `E1_STUDY_DATA_SCHEMA.md` | 6 relational CSV data dictionaries with complete referential integrity. | **LOCKED (v1.0.3)** |
| 14 | `E1_CONSENT_DATA_GOVERNANCE_SPEC.md` | Informed consent disclosures, voluntary participation, two-vault privacy. | **LOCKED (v1.0.3)** |
| 15 | `E1_ETHICS_DEPENDENCY_CHECKLIST.md` | Dual-status gate (Technically Ready vs Institutionally Authorized). | **LOCKED (v1.0.3)** |
| 16 | `E1_PILOT_PLAN.md` | Small-scale ($N=3\text{--}5$) feasibility pilot study and change policy. | **LOCKED (v1.0.3)** |
| 17 | `E2_INSTRUMENTATION_REQUIREMENTS.md` | Architectural backlog for future survey delivery tooling (Option C recommended). | **LOCKED (v1.0.3)** |
| 18 | `E1_PROTOCOL_LOCK_REPORT.md` | Formal lock signoff report designating READY FOR PILOT REVIEW. | **LOCKED (v1.0.3)** |
| 19 | `E1_PROTOCOL_CHANGELOG.md` | Formal version tracking: v1.0.0 $\to$ v1.0.1 $\to$ v1.0.2 $\to$ v1.0.3. | **LOCKED (v1.0.3)** |
| 20 | `E1_2_INSTRUMENT_CORRECTION_REPORT.md` | Phase E1.2 Instrument Correction Report (Superseded by v1.0.3). | **SUPERSEDED (v1.0.2)** |
| 21 | `E1_1_FACTUAL_CORRECTION_REPORT.md` | Phase E1.1 Factual Correction Report (Superseded by v1.0.2). | **SUPERSEDED (v1.0.1)** |

---

## 3. Epistemic Verification Declarations

The undersigned student investigator formally affirms the following governance principles:
1. **Separation of Concerns:** Usability and comprehension evaluation will not be claimed as clinical diagnostic efficacy or medical accuracy.
2. **Offline Model Freezing:** Model weights, preprocessor parameters, and operating threshold (0.1389) remain permanently immutable.
3. **Data Hygiene:** Study sessions will execute against a pristine, unseeded `db_study.sqlite3` with zero legacy QA records.
4. **Transparent Sampling:** Participant recruitment will be honestly reported as non-probability purposive/convenience sampling, without claiming general population representativeness.
5. **Pilot / Ethics Sequencing:** Designation as READY FOR PILOT REVIEW does NOT authorize participant contact. Pilot execution may begin only after applicable supervisor and institutional ethics requirements for pilot participant involvement have been satisfied.

**Approval Status:**  
Protocol Version 1.0.3 is officially **LOCKED** and designated as **READY FOR SUPERVISOR / INSTITUTIONAL PILOT REVIEW**. (Formal participant data collection and recruitment remain unauthorized pending pilot execution and institutional approvals).
