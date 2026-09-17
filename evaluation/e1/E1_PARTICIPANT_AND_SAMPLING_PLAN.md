# Participant & Sampling Plan (Phase E1)
## Two-Layer Participant Strategy & Linkage Governance

**Document Identifier:** `E1-SAMPLING-PLAN-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Participant Strategy Overview

To rigorously evaluate the decision-support prototype without making unsupported clinical claims, this study establishes a **Two-Layer Evaluation Architecture**:

```
+-----------------------------------------------------------------------------------+
|                        TWO-LAYER PARTICIPANT ARCHITECTURE                         |
+-----------------------------------------------------------------------------------+
| LAYER 1: PRIMARY USABILITY & COMPREHENSION COHORT                                 |
| - Target N: 24 to 30 completed sessions (Practical thesis minimum: N = 20)        |
| - Population: University students, staff, general adult computer users            |
| - Focus: Workflow usability, interaction friction, mental model comprehension     |
| - Coding Scheme: P001, P002, ..., P030                                            |
+-----------------------------------------------------------------------------------+
| LAYER 2: OPTIONAL HEALTH-PROFESSIONAL FACE-VALIDITY COHORT                        |
| - Target N: 3 to 5 clinical practitioners / public health trainees                |
| - Focus: Terminology face validity, perceived plausibility of workflow            |
| - Coding Scheme: E001, E002, ..., E005                                            |
| - Isolation: STRICTLY SEPARATED from Primary SUS statistical calculations         |
+-----------------------------------------------------------------------------------+
```

---

## 2. Sample Size Justification & Feasibility

### 2.1 Primary Usability Cohort ($N = 24\text{ to }30$)
- **Methodological Justification:**  
  According to foundational usability engineering literature (Virzi, 1992; Nielsen & Landauer, 1993; Faulkner, 2003), a sample size of $N = 20$ participants discovers over 95% of usability defects in a complex user interface. In System Usability Scale (SUS) research, Sauro (2011) demonstrates that sample sizes of $N \ge 20\text{--}25$ provide stable mean estimates with a standard error of the mean below 3 SUS points.
- **Thesis Pragmatism:**  
  For an undergraduate computer science skripsi, recruiting 24–30 participants represents an optimal trade-off between statistical stability and practical recruitment feasibility.
- **Fallacy Prevention:**  
  This sample size **IS NOT POWERED** for clinical subgroup analysis or epidemiological generalizations. It is strictly powered for usability problem discovery and descriptive score estimation.

### 2.2 Optional Expert Review Cohort ($N = 3\text{ to }5$)
- **Purpose:** Qualitative appraisal of the perceived plausibility of the screening/referral workflow and domain terminology.
- **Justification:** Nielsen (1994) heuristic review methodology indicates that 3–5 domain experts uncover the vast majority of domain-specific workflow inconsistencies.
- **Strict Rule:** Expert ratings are reported exclusively as qualitative observations or exploratory item distributions; they are never pooled with lay-user SUS metrics.

---

## 3. Sampling Method & Recruitment Procedures

### 3.1 Sampling Methodology
- **Classification:** **Non-probability Purposive and Convenience Sampling**.
- **Transparency Mandate:** The study methodology must explicitly document this sampling technique. The cohort **MUST NEVER BE DESCRIBED AS A "NATIONALLY REPRESENTATIVE POPULATION SAMPLE"** or "representative clinical cohort."

### 3.2 Primary Cohort Eligibility Criteria

#### Inclusion Criteria:
1. Age $\ge 18$ years at the time of the study.
2. Fluent in written and spoken English (the prototype interface language).
3. Basic computer literacy (regularly uses a web browser on a laptop or desktop).
4. Normal or corrected-to-normal vision.
5. Provides formal informed consent.

#### Exclusion Criteria:
1. Direct prior involvement in the software engineering or design of the prototype.
2. Participation in the Phase E1 pilot study (to eliminate learning/familiarity bias).
3. Inability or unwillingness to complete the full 30–45 minute evaluation protocol.
4. Requiring assistive screen-reading technology (the prototype's visual explainability layout has not yet been audited for full non-visual screen-reader equivalence).

*Note: Diabetes status, HbA1c history, or clinical backgrounds are neither required nor recorded for the primary cohort.*

### 3.3 Expert Cohort Eligibility Criteria
- **Inclusion:** Medical doctor, registered nurse, public health specialist, or medical/nursing student in clinical clerkship years.
- **Exclusion:** Previous developer or designer of the system.

---

## 4. Participant Identifier & Data Linkage Architecture

### 4.1 Resolution of D3 Linkage Governance (Formal Lock)
In Phase D3 (`docs/USER_STUDY_DATA_LINKAGE_DECISION.md`), the status of participant linkage was marked as `NOT YET LOCKED`.  
**Under Protocol Version 1.0, this decision is formally LOCKED as follows:**

```
+------------------------------------------------------------------------------------+
|                      DETERMINISTIC LINKAGE ARCHITECTURE                            |
+------------------------------------------------------------------------------------+
| Physical ID Card:    "Participant Code: P012"                                      |
|                                |                                                   |
|        +-----------------------+-----------------------+                           |
|        |                                               |                           |
|        v                                               v                           |
| Dashboard Interface:                           Survey Form (External):             |
| Operator enters Reviewer Code:                 Participant enters Code:            |
| [ P012 ]                                       [ P012 ]                            |
|        |                                               |                           |
|        v                                               v                           |
| Database Table: `HumanReview`                  Survey Dataset:                     |
| `reviewer_code = "P012"`                       `participant_code = "P012"`         |
| `screening_id = 8a4c1f...`                     `sus_score = 77.5`                  |
+------------------------------------------------------------------------------------+
```

1. **Unified Pseudonymous Code:**  
   Every participant is assigned an immutable alphanumeric code:
   - Primary group: `P001` through `P030`.
   - Expert group: `E001` through `E005`.
2. **Reviewer Code Reuse:**  
   During Task 3 (Human Review Accept) and Task 4 (Human Override), participants are explicitly instructed to enter their assigned participant code (e.g., `P012`) into the prototype's `Reviewer Code` input field.
3. **Database Integration:**  
   This populates `HumanReview.reviewer_code` directly in `db_study.sqlite3`, enabling 100% deterministic SQL join between database audit records and post-task survey responses **without requiring any database schema modifications or Django UI alterations**.
4. **Identity Segregation (Two-Vault Model):**  
   - **Vault A (Master Identity Sheet):** Maps participant full name and email to `participant_code`. Stored on an encrypted, password-protected offline drive accessible solely to the primary investigator. Never uploaded or shared.
   - **Vault B (De-identified Research Dataset):** Contains only `participant_code`, database logs, task logs, and survey responses. All thesis tables, charts, and public repositories use Vault B data exclusively.
   - **Destruction Schedule:** Vault A is permanently shredded upon formal thesis defense approval.

---

## 5. Hardware, Browser & Environmental Controls

To eliminate confounding hardware variability during task observation:

| Environmental Variable | Specification Standard | Enforcement Mechanism |
| :--- | :--- | :--- |
| **Device Form Factor** | Laptop or Desktop workstation (Minimum screen width: 1280px) | Sessions conducted on a dedicated study laptop provided by the researcher (or participant's personal laptop verified before session). |
| **Operating System** | Windows 10/11, macOS, or Linux | Documented in session metadata. |
| **Web Browser** | Google Chrome or Mozilla Firefox (latest stable release) | Researcher verifies clean browser profile (no extensions or custom CSS). |
| **Display Resolution** | Recommended: $1920 \times 1080$ px; Minimum: $1280 \times 800$ px | Scale set to 100% (no browser zoom). |
| **Input Modality** | Physical mouse or touchpad + physical keyboard | No touchscreens used as primary input. |
| **Network & Server** | Localhost execution (`127.0.0.1:8000`) against clean `db_study.sqlite3` | Zero latency variability; completely offline research runtime. |
