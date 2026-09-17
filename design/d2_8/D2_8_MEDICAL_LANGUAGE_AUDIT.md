# Phase D2.8 Medical Language & Epistemic Boundaries Audit

## 1. Audit Scope & Protocol
Every active user-facing string across Stage-1, Human Review, and Stage-2 templates was audited to ensure full compliance with the Research Governance skill.

### Core Epistemic Principles
1. Stage-2 HbA1c is presented as a **Laboratory Range Assessment**, not an automated clinical diagnosis.
2. The system does not decide whether clinical diagnostic criteria are satisfied.
3. Reviewer assumptions default to anonymous **Reviewer / Human Review**, avoiding unnecessary clinical titles.
4. Language equivalent to "diagnostic laboratory" is replaced with "laboratory assessment".

---

## 2. Forbidden Phrases & Remediation Check

| Scanned Forbidden Phrase | Status in Stage 2 | Remediation / Approved Replacement |
| :--- | :--- | :--- |
| `diagnosed` / `diagnosis` | **Absent from results** | Replaced with *"Laboratory Range Category"* |
| `diagnosis confirmed` | **Prohibited & Absent** | Explicit caveat added: *"Clinical diagnosis generally requires confirmatory testing."* |
| `positive for diabetes` | **Prohibited & Absent** | Replaced with *"Diabetes-range"* |
| `you have prediabetes` | **Prohibited & Absent** | Replaced with *"Entered HbA1c falls within the 5.7% to <6.5% laboratory range."* |
| `you have diabetes` | **Prohibited & Absent** | Replaced with *"Entered HbA1c falls within the ≥6.5% laboratory range used in diabetes diagnostic criteria."* |
| `normal therefore healthy` | **Prohibited & Absent** | Replaced with *"Entered HbA1c falls below the 5.7% prediabetes-range threshold."* |
| `ground truth` / `true disease` | **Prohibited & Absent** | UI copy uses *"Laboratory measurement"*, *"Confirmatory laboratory assessment"* |
| `doctor` / `clinician` in active UI | **Replaced** | Active UI uses *"Reviewer"*, *"Review decision"*, *"Human Review"* |
| `Stage-2 diagnostic laboratory` | **Replaced** | Replaced with *"Stage-2 HbA1c laboratory assessment"* |

---

## 3. Mandatory Caveat Wording Verification
Verified present verbatim on all Stage-2 review and result views:
> *"This range presentation is not an automated diagnosis. In the absence of unequivocal hyperglycemia, clinical diagnosis generally requires appropriate confirmatory testing. This prototype does not evaluate whether confirmation has occurred."*

## 4. Assay Limitation Note Verification
Verified present verbatim on all Stage-2 views:
> *"HbA1c interpretation can depend on laboratory method and clinical context. This research prototype categorizes the entered numeric value only."*
