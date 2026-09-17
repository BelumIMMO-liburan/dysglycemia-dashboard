# Protocol Version & Modification Changelog (Phase E1)
## Formal Protocol Versioning & Governance Audit Trail

**Current Protocol Version:** `1.0.3`  
**Protocol Release Tag:** `E1-PROTOCOL-2026-V1.0.3`  
**Date of Current Version:** 2026-09-05  
**Governing Authority:** Academic Thesis Candidate & Advisory Committee  

---

## 1. Versioning Policy & Immutability Rules

To protect the internal validity of the research evaluation, all documents within `evaluation/e1/` are subject to strict version control:

1. **Pre-Pilot Status:** Version `1.0` was the initial drafted protocol; it was superseded by Version `1.0.1` following pre-review factual reconciliation, which was subsequently superseded by Version `1.0.2` following runtime stimulus verification, and finally superseded by Version `1.0.3` to achieve 100% cross-document stimulus consistency prior to pilot participant contact.
2. **Pilot Revisions:** Minor textual adjustments or instruction clarifications resulting from the pilot study ($N = 3\text{--}5$) may be incorporated under Version `1.1`, accompanied by an explicit changelog entry.
3. **Formal Evaluation Freeze:** The moment formal data collection begins with participant `P001`, **THE PROTOCOL IS PERMANENTLY FROZEN**. No subsequent changes to tasks, questions, scoring formulas, or inclusion criteria are permitted without invalidating the active cohort.

---

## 2. Formal Changelog History

| Version | Release Date | Author | Classification | Status | Summary of Changes / Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **v1.0** | 2026-09-05 | Felix (Student Investigator) | INITIAL PROTOCOL LOCK | **SUPERSEDED BEFORE FORMAL DATA COLLECTION** | Initial creation of protocol suite. Contained stale draft values (N=1,418 test split, ROC-AUC CI [0.6901, 0.7634], "Confirmatory Intake" phrasing). Superseded prior to any participant contact. |
| **v1.0.1** | 2026-09-05 | Felix (Student Investigator) | FACTUAL / TERMINOLOGY CORRECTION | **SUPERSEDED BEFORE PILOT** | Factual & terminology pre-review reconciliation against frozen Phase-5 evidence: corrected N=812, ROC-AUC CI [0.6875, 0.7656], Stage-2 HbA1c Lab phrasing, synthetic screening profiles, and final referral decision semantics. |
| **v1.0.2** | 2026-09-05 | Felix (Student Investigator) | INSTRUMENT / STIMULUS CONSISTENCY CORRECTION | **SUPERSEDED BEFORE PILOT** | Comprehensive instrument and runtime stimulus reconciliation (`E1_2_INSTRUMENT_CORRECTION_REPORT.md`): runtime verification logs, Sharfina & Santoso (2016) Indonesian SUS, objective comprehension battery refinement, and task state flow fixes. Superseded by v1.0.3 to eliminate remaining cross-document stimulus contradictions. |
| **v1.0.3** | 2026-09-05 | Felix (Student Investigator) | **FINAL CROSS-DOCUMENT STIMULUS RECONCILIATION** | **READY FOR SUPERVISOR / INSTITUTIONAL PILOT REVIEW** | Final stimulus and terminology reconciliation across entire suite (`E1_3_FINAL_RECONCILIATION_REPORT.md`):<br>1. **Single Source of Truth:** Created `E1_STIMULUS_LOCK.md` establishing authoritative fingerprint for Case Alpha ($p=0.272969$, Refer, Elevated Screening Signal) and Case Beta ($p=0.054663$, No Referral, Lower Screening Signal).<br>2. **Contradictory Data Expunged:** Removed all stale demographic numbers (58, 27.4, 92.0, 34, 21.8, 68.0) and non-model variables (SBP, DBP, medication, cigarettes/day, exercise min/wk). Restricted task cards strictly to Canonical Seven Predictors.<br>3. **Canonical UI Copy:** Standardized all UI references to frozen labels: `Elevated Screening Signal`, `Lower Screening Signal`, `Refer`, `No Referral`, `Stage-2 HbA1c Laboratory Assessment`.<br>4. **Clinical Wording Audit:** Standardized `synthetic screening profile narrative`, `final human referral decision authority`, and `screening/referral workflow`.<br>5. **Pilot / Ethics Sequencing:** Explicitly declared that READY FOR PILOT REVIEW does not authorize participant contact; ethics and supervisor clearances must precede pilot execution.<br>6. **Suite Audit:** Physically audited all 21 files in `evaluation/e1/`.<br>*Note: Zero participant data collected; zero pilot participants contacted; zero prototype code modified.* |

---

## 3. Protocol Amendment Template (For Future Revisions)

If an amendment becomes necessary following pilot execution, it must be recorded using the following schema:

```
================================================================================
PROTOCOL AMENDMENT RECORD
================================================================================
Amendment Number: AMEND-[YYYY]-[NN]
Target Version:   v[X.Y]
Date:             YYYY-MM-DD
Target Document:  [e.g. E1_COMPREHENSION_ITEM_BANK.md]
Section Affected: [e.g. Section 2, Item 4]

Description of Modification:
[Exact before and after wording of modified text]

Scientific Rationale:
[Empirical finding from pilot study justifying the change]

Impact Assessment:
- Impact on task completion: [None / Minor]
- Impact on statistical comparability: [None / Explain]
- Approved by Supervisor: [Yes / Date]
================================================================================
```
