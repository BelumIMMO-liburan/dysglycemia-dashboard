# Participant Coding & Pseudonymization Scheme (Phase E2)
## Standardized Linkage Identifiers & Privacy Boundaries

**Document Identifier:** `E2-CODE-SCHEME-V1.0`  
**Evaluation Phase:** `E2` (Pilot Instrument Package & Operationalization)  
**Governing Protocol:** `v1.0.3` (`E1-PROTOCOL-2026-V1.0.3`)  
**Package Version:** `1.0`  
**Date:** 2026-09-05  

---

## 1. Purpose & Core Principles

This specification defines the syntax, uniqueness constraints, and privacy boundaries for participant codes used across all evaluation instruments.

### Key Governance Principles:
1. **Deterministic Multi-Source Linkage:** The same pseudonymous identifier serves as the relational foreign key linking the local prototype database, the external post-task questionnaire, the moderator observation sheet, and the session archive manifest.
2. **Pseudonymous Identifier (Zero Direct PII in Analysis):** The participant code is a pseudonymous research identifier that contains zero direct personally identifying information (no initials, birth dates, phone digits, or student ID numbers). It prevents direct identity exposure within analytical datasets.
3. **Strict Cohort Disambiguation:** Prefix schemes explicitly separate pilot feasibility subjects, formal study participants, expert practitioners, and researcher dry-runs.

---

## 2. Standardized Code Syntax & Prefix Hierarchy

```
+----------------------------------------------------------------------------------------------------+
|                                  PARTICIPANT CODE PREFIX TAXONOMY                                  |
+----------------+--------------------+----------------+--------------------+------------------------+
| Cohort Type    | Prefix Syntax      | Sequence Range | Target Size        | Purpose / Scope        |
+----------------+--------------------+----------------+--------------------+------------------------+
| RESEARCHER     | DRYRUN[NNN]        | DRYRUN001 to   | N = 1–2 runs       | Operational validation |
| DRY-RUN        |                    | DRYRUN010      |                    | of scripts & templates |
+----------------+--------------------+----------------+--------------------+------------------------+
| FEASIBILITY    | PILOT[NNN]         | PILOT001 to    | N = 3–5 subjects   | Procedural stress-test |
| PILOT STUDY    |                    | PILOT005       | (Max: PILOT010)    | & instruction clarity  |
+----------------+--------------------+----------------+--------------------+------------------------+
| FORMAL STUDY   | P[NNN]             | P001 to        | N = 24–30 subjects | Primary formal thesis  |
| PRIMARY LAYER  |                    | P030           | (Min: P020)        | usability evaluation   |
+----------------+--------------------+----------------+--------------------+------------------------+
| FORMAL STUDY   | E[NNN]             | E001 to        | N = 3–5 clinicians | Optional professional  |
| EXPERT LAYER   |                    | E005           |                    | face validity review   |
+----------------+--------------------+----------------+--------------------+------------------------+
```

### Syntax Specifications:
- **Format:** Alphanumeric, uppercase, zero-padded 3-digit serial number.
- **Regular Expression:** `^(DRYRUN\d{3}|PILOT\d{3}|P\d{3}|E\d{3})$`
- **Case Sensitivity:** Evaluated strictly as case-insensitive but stored and displayed in uppercase (e.g., `PILOT001`).

---

## 3. Operational Touchpoints (Where the Code Appears)

For any given session, the participant code must be entered identically at four operational touchpoints:

```
+----------------------------------------------------------------------------------------------------+
|                                    TOUCHPOINT ALIGNMENT MATRIX                                     |
+------------------------------------+-----------------------------+---------------------------------+
| System Touchpoint                  | Interface Location          | Operational Rule                |
+------------------------------------+-----------------------------+---------------------------------+
| 1. Local Prototype (Task 3)        | Reviewer Code input field   | Mandatory input prior to        |
|    `CASE-ALPHA` Guided Review      | `#reviewer_code_accept`     | clicking 'Accept Recommendation'|
+------------------------------------+-----------------------------+---------------------------------+
| 2. Local Prototype (Task 4)        | Reviewer Code input field   | Mandatory input in modal dialog |
|    `CASE-BETA` Human Override      | `#reviewer_code_override`   | prior to 'Confirm Override'     |
+------------------------------------+-----------------------------+---------------------------------+
| 3. External Web Questionnaire      | Section 1, Question 1       | Required single-line text field |
|    (Post-Task Battery)             | Form Validation Rule        | Regex validated before Section 2|
+------------------------------------+-----------------------------+---------------------------------+
| 4. Moderator Observation Sheet     | Sheet Header & Per-Task     | Pre-filled by facilitator on    |
|    (Observer Ledger)               | Identification Rows         | physical sheet before session   |
+------------------------------------+-----------------------------+---------------------------------+
| 5. Session Archive Manifest        | Primary CSV column          | Logged during post-session DB   |
|    `session_manifest.csv`          | `participant_code`          | archival and hash verification  |
+------------------------------------+-----------------------------+---------------------------------+
```

---

## 4. Privacy Boundaries & Two-Vault Linkage Governance

To protect participant privacy while enabling academic integrity and institutional ethics compliance:

1. **Pseudonymous Analytical Dataset (Vault B / Vault 2):**  
   All evaluation data files (`participants.csv`, `task_results.csv`, `comprehension_responses.csv`, `sus_responses.csv`, `perception_responses.csv`, `qualitative_feedback.csv`, and SQLite archives) contain **ONLY the pseudonymous participant code**. They contain zero names, student IDs, email addresses, or phone numbers. Access to Vault B is strictly restricted to authorized members of the research team and is **never open/public by default**.
2. **Administrative Identity Vault (Vault A / Vault 1):**  
   Physical signed consent forms, attendance sheets, or administrative logs that link participant identity to their assigned Participant Code:
   - Must be maintained strictly within Vault A (Administrative Restricted Vault).
   - Must be stored in a physical locked cabinet or an encrypted, password-protected directory entirely separate from the analytical dataset and code repositories.
   - Must never be committed to source control, published in open repositories, or embedded within analytical export CSVs.
3. **Pseudonymization Semantics vs Irreversible Anonymization:**  
   The Participant Code functions as a **pseudonymous research identifier**. It does NOT constitute irreversible anonymization so long as the separate identity-to-code administrative link exists in Vault A. Therefore, research data collected during active evaluation must be accurately described as **pseudonymous research data**, not fully or irreversibly anonymous.
4. **Data Retention & Eventual Post-Study Anonymization:**  
   Once formal thesis examination, academic verification, and mandatory institutional retention periods conclude, the administrative linkage records in Vault A may be securely shredded/destroyed according to institutional ethics guidelines. Only after this destructive step is completed does the residual research dataset in Vault B transition from pseudonymous records into permanently anonymized research data.
