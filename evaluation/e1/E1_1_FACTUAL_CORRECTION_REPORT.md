# Phase E1.1 Factual & Terminology Correction Report
## Protocol Version 1.0.1 Pre-Review Reconciliation

**Document Identifier:** `E1-1-FACTUAL-CORRECTION-REPORT-V1.0.1`  
**Protocol Version:** `1.0.1` (Factual & Terminology Pre-Review Correction)  
**Superseded Version:** `1.0` (Superseded prior to formal data collection)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  
**Lock Status:** **PROTOCOL v1.0.1 READY FOR SUPERVISOR / INSTITUTIONAL REVIEW**  

---

## 1. Executive Summary & Purpose

During independent pre-supervisor review of the frozen Phase E1 Evaluation Protocol (Version 1.0), several factual discrepancies relating to Phase-5 model evaluation statistics and clinical terminology choices were identified.

This document records the systematic audit, corrections executed, and verification results across all evaluation protocol documents. 

**Core Governance Principles Upheld:**
- **No Study Redesign:** Zero changes were made to participant sampling strategy ($N=24\text{--}30$ primary, $N=3\text{--}5$ expert), task scenarios structure, System Usability Scale (SUS) instrument, comprehension quiz constructs, or statistical analysis plan.
- **Zero Participant Contact:** Absolutely no participant data have been collected. No experimental outcomes were observed prior to this correction.
- **Zero Prototype Modifications:** The dashboard application code, model files, preprocessor, frozen operating threshold (`0.1389`), and Stage-2 reference ranges remain 100% untouched.

---

## 2. Files Audited

A comprehensive audit was conducted across all 16 evaluation documents in `evaluation/e1/` as well as project documentation:

1. `evaluation/e1/E1_EVALUATION_PROTOCOL.md`
2. `evaluation/e1/E1_RQ_CLAIM_EVIDENCE_MATRIX.md`
3. `evaluation/e1/E1_PARTICIPANT_AND_SAMPLING_PLAN.md`
4. `evaluation/e1/E1_TASK_SCENARIOS.md`
5. `evaluation/e1/E1_TASK_CONSTRUCT_MATRIX.md`
6. `evaluation/e1/E1_MEASUREMENT_INSTRUMENT_SPEC.md`
7. `evaluation/e1/E1_COMPREHENSION_ITEM_BANK.md`
8. `evaluation/e1/E1_ANALYSIS_PLAN.md`
9. `evaluation/e1/E1_STUDY_DATA_SCHEMA.md`
10. `evaluation/e1/E1_CONSENT_DATA_GOVERNANCE_SPEC.md`
11. `evaluation/e1/E1_ETHICS_DEPENDENCY_CHECKLIST.md`
12. `evaluation/e1/E1_PILOT_PLAN.md`
13. `evaluation/e1/E1_MODERATOR_GUIDE.md`
14. `evaluation/e1/E1_PROTOCOL_CHANGELOG.md`
15. `evaluation/e1/E1_PROTOCOL_LOCK_REPORT.md`
16. `evaluation/e1/E2_INSTRUMENTATION_REQUIREMENTS.md`
17. `PROJECT_MASTER_RECAP.md`
18. `docs/PROJECT_MASTER_RECAP.md`

---

## 3. Factual Values Audited & Corrected

All quantitative performance metrics copied from Phase 5 into Phase E1 were reconciled directly against the authoritative Phase-5.1 frozen evaluation report:

| Metric / Parameter | Stale / Incorrect Value Found | Authoritative Corrected Value | Source of Truth |
| :--- | :--- | :--- | :--- |
| **Held-Out Final Test Cohort Size** | $N = 1,418$ / $1418$ | **$N = 812$** ($621$ normal-range, $191$ dysglycemia-range) | Phase 5.1 Expanded Test Cohort |
| **GAM ROC-AUC 95% Bootstrap CI** | `[0.6901, 0.7634]` | **`[0.6875, 0.7656]`** (Point estimate: `0.7277`) | Phase 5.1 Final Evaluation Report |
| **GAM PR-AUC** | Stale / Unspecified | **$0.4503$** | Phase 5.1 Final Evaluation Report |
| **GAM Brier Score** | Stale / Unspecified | **$0.1587$** | Phase 5.1 Final Evaluation Report |
| **Frozen Operating Threshold** | $0.1389$ | **$0.1389$** (Verified consistent) | Phase 5.1 & `screening_inference.py` |
| **Held-Out Final Test Sensitivity** | $86.39\%$ | **$86.39\%$** (Verified consistent) | Phase 5.1 Final Evaluation Report |
| **Held-Out Final Test Specificity** | $42.51\%$ | **$42.51\%$** (Verified consistent) | Phase 5.1 Final Evaluation Report |

### Critical Sensitivity Reproduction Statement
Every document describing offline model performance was audited to ensure inclusion of the critical epistemic boundary:
> *"The development-derived operating threshold targeting $\ge 90\%$ sensitivity achieved $86.39\%$ sensitivity on the held-out final test. Therefore the $90\%$ development sensitivity target was not reproduced at the final-test point estimate."*

---

## 4. Terminology Audit & Corrections

To prevent overclaiming and maintain strict non-diagnostic research boundaries, specific wording across the protocol was standardized:

| Domain | Previous / Deprecated Phrasing | Corrected Research-Safe Phrasing | Epistemic Rationale |
| :--- | :--- | :--- | :--- |
| **Stage-2 Workflow** | *"Stage-2 Confirmatory Intake"* / *"Confirmatory Lab"* | **"Stage-2 HbA1c Laboratory Assessment"** | Prevents implying that the software or intake form itself provides or confirms a clinical diagnosis. |
| **Evaluation Cases** | *"patient profile"* / *"fictional patient"* | **"synthetic screening profile"** / **"fictional screening case"** | The study evaluates software usability and mental-model comprehension, not clinical patient-care simulation. |
| **Expert Evaluation Scope** | *"clinical referral logic"* | **"perceived plausibility of the screening/referral workflow"** | Expert practitioner feedback provides professional face validity and workflow naturalness, not clinical efficacy or medical accuracy. |
| **Human Override Action** | *"modifies clinical referral"* / *"clinical referral"* | **"modifies the final human referral decision"** | Human Override alters the operational referral decision in the screening workflow; it does not establish clinical correctness or medical ground truth. |

---

## 5. Protocol Versioning & Governance Status

- **Previous Status:** Version 1.0 (`E1-PROTOCOL-2026-V1.0`), marked **`SUPERSEDED BEFORE FORMAL DATA COLLECTION`**.
- **Current Status:** Version 1.0.1 (`E1-PROTOCOL-2026-V1.0.1`), classification **`FACTUAL / TERMINOLOGY CORRECTION`**.
- **Gate Determination:** **PROTOCOL v1.0.1 READY FOR SUPERVISOR / INSTITUTIONAL REVIEW**.

*(Note: Explicitly adhering to governance guidelines, the protocol is declared ready for supervisor and institutional review; it is NOT declared "institutionally approved" or "authorized for recruitment" prior to external administrative signoff).*

---

## 6. Verification Confirmation

1. **Zero Participant Data Collected:** Confirmed. No participants have been contacted, recruited, or consented. Zero survey responses exist.
2. **Zero Prototype Code Changes:** Confirmed. No files in `dashboard/` or model pickle artifacts were modified.
3. **Automated Test Suite Status:** Verified passing 144 / 144 tests (`python manage.py test predictor`).
4. **Model Artifact Hashes:** All 4 protected model hashes remain byte-identical:
   - GAM Model: `204a94ff072ef4f1edecebf5a643738c6426466f8d3896ed8f75b7b9ef08a90a`
   - Preprocessor: `6e56a01993a4a6971eb62c82699c49daae8b8c2d152788e0ee65ebf64c12666a`
   - Spec: `7d2a5eb9c349dabfca4f5387161c78833075c3ef940ef87a4debf0b3e5a31a55`
   - Test Preds: `fac969a00df57d6686c36b09e3de65859eecf1349f4c3ecceeb99dfbeec5f206`

---

PHASE E1.1 COMPLETE — PROTOCOL v1.0.1 FACTUALLY RECONCILED WITH FROZEN PHASE-5 EVIDENCE
