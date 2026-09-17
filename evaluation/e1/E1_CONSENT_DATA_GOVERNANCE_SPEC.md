# Informed Consent & Data Governance Specification (Phase E1)
## Participant Protection, Privacy Architecture & Ethical Framework

**Document Identifier:** `E1-CONSENT-SPEC-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Ethical Framework & Institutional Disclaimer

This specification establishes the participant rights, informed consent elements, and data governance policies governing the user evaluation of `research-prototype-v1.0`.

**INSTITUTIONAL DISCLAIMER:**  
This document specifies the *technical and methodological requirements* for informed consent and participant privacy. It **DOES NOT** substitute for formal institutional ethics review. Formal data collection with human participants may proceed **ONLY AFTER** obtaining required institutional or faculty supervisor authorization as tracked in `E1_ETHICS_DEPENDENCY_CHECKLIST.md`.

---

## 2. Mandatory Informed Consent Elements

Every prospective participant must receive an Information Sheet and execute a Written or Digital Consent Form containing the following ten mandatory disclosures:

1. **Research Purpose:**  
   The study evaluates the software usability, workflow layout, and user understanding of an academic research prototype for two-stage diabetes screening.
2. **Explicit Non-Diagnostic Disclosure:**  
   The software is an experimental decision-support research prototype. It is **NOT** a certified diagnostic medical device, does not provide medical diagnoses, and has not been validated for real-world clinical deployment in Indonesia.
3. **Voluntary Participation & Right to Withdraw:**  
   Participation is entirely voluntary. Participants may decline to answer any question, pause the session, or withdraw at any moment without providing a reason and without academic, personal, or financial penalty.
4. **Nature of Experimental Tasks:**  
   Participants will interact with a web dashboard using fictional, pre-written screening profiles on a computer. Under no circumstances will participants be asked to provide their own medical history, glucose measurements, or biological samples.
5. **Session Duration:**  
   The entire study procedure requires approximately **30 to 45 minutes**.
6. **Types of Data Collected:**  
   - Broad demographic categories (age bracket, education level).
   - Task completion outcomes and moderator assistance levels.
   - Objective multiple-choice comprehension quiz answers.
   - 10-item System Usability Scale ratings.
   - Qualitative feedback remarks regarding interface clarity.
7. **Privacy & Pseudonymization (Two-Vault Model):**  
   All experimental records are linked exclusively to a pseudonymous participant code (e.g., `P012`). Real names and email addresses are never entered into the prototype database or public analysis datasets.
8. **Risks and Discomforts:**  
   Risks are minimal and do not exceed those encountered during ordinary office computer use (mild visual fatigue or cognitive effort). Breaks are provided upon request.
9. **Benefits:**  
   No direct medical or personal benefit is promised. Participants contribute to academic knowledge in human-centered explainable AI and clinical decision support.
10. **Investigator Contact Information:**  
    Contact details of the primary student investigator and academic thesis supervisor are provided for inquiries or ethical concerns.

---

## 3. Standardized Participant Information Sheet Template

```
================================================================================
PARTICIPANT INFORMATION & INFORMED CONSENT SHEET
Study Title: Usability and Comprehension Evaluation of a Two-Stage Non-Laboratory
             Diabetes Screening Decision-Support Research Prototype
Investigator: Felix (Undergraduate Thesis Candidate, Computer Science)
Supervisor: [Academic Thesis Advisor Name], Department of Computer Science
================================================================================

1. WHAT IS THE PURPOSE OF THIS STUDY?
You are invited to participate in an undergraduate research study evaluating the
usability and user comprehension of a research prototype dashboard. The dashboard
is designed to assist human reviewers in evaluating machine learning screening
recommendations and recording Stage-2 HbA1c laboratory assessment results.

2. WHAT WILL I BE ASKED TO DO?
- You will receive a brief 5-minute walkthrough of the software interface.
- You will perform 5 short tasks on a computer using fictional screening profiles
  (e.g., entering sample data, reviewing charts, and accepting/overriding prompts).
- You will complete a short multiple-choice quiz and a usability questionnaire.
- The session will take approximately 30 to 45 minutes.

3. ARE THERE ANY MEDICAL RISKS OR DATA COLLECTION?
No. You will NOT be asked to enter any personal medical information, health
measurements, or biological data. The prototype is an academic computer science
prototype and NOT a clinical diagnostic tool.

4. IS MY PARTICIPATION CONFIDENTIAL?
Yes. Your responses and actions will be identified solely by an anonymous study
code (such as P001). Your name will never appear in any thesis publication,
database export, or public report.

5. DO I HAVE TO PARTICIPATE?
No. Your participation is completely voluntary. You may stop or withdraw at any
time with zero penalty.

================================================================================
CONSENT DECLARATION (To be signed prior to session)
- I confirm that I have read and understood the information sheet above.
- I understand that the software is an academic research prototype, not a medical device.
- I understand that my participation is voluntary and that I may withdraw at any time.
- I agree to take part in this usability evaluation.

Participant Code: [ __________ ]
Participant Signature: [ ___________________________ ] Date: [ ______________ ]
Researcher Signature:  [ ___________________________ ] Date: [ ______________ ]
================================================================================
```

---

## 4. Data Storage, Retention & Destruction Policy

1. **Storage Security:**  
   - Raw survey CSVs and database files are stored on an encrypted local storage volume (BitLocker / FileVault).
   - No participant data are stored in unencrypted third-party public repositories.
2. **Access Control:**  
   - Access to raw survey responses and the master identity sheet is restricted exclusively to the primary thesis researcher.
3. **Retention Period:**  
   - Anonymous research datasets (`participants.csv`, `task_results.csv`, `sus_responses.csv`, etc.) will be retained for 5 years following thesis publication in accordance with standard academic reproducibility standards.
   - The master identity linking sheet (Vault A) will be securely shredded immediately upon formal thesis defense approval.
