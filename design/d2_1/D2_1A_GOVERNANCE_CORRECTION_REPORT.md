# Phase D2.1A Governance Correction Report
**Thesis Project:** Research Decision Support Prototype for Dysglycemia Non-Laboratory Screening  
**Status:** COMPLETED & VERIFIED  
**Date:** September 4, 2026  
**Governing Documents:**
- `research-governance` (Highest Precedence)
- `dashboard-design`
- `frontend-quality`
- `DASHBOARD_DESIGN_SPEC_V1.md`

---

## 1. Executive Summary

Phase D2.1A applies targeted research governance and reproducibility corrections to the completed Phase D2.1 UI foundation before implementing the Stage-1 non-laboratory intake form (Phase D2.2).

Scope is strictly preserved:
- No screening inference implemented.
- No model execution or feature engineering introduced.
- Research assets (`gam_final.pkl`, `preprocessor.pkl`) verified bitwise identical.
- Zero fake metrics or ungrounded statistics displayed.

---

## 2. Probability Meter Correction

### Audit Findings
In Phase D2.1 component demonstration, the visual primitive for the probability gauge included phrasing referencing `"13.9% sensitivity floor threshold"`.

### Correction Applied
1. **Removed Erroneous Terminology:** The terminology "sensitivity floor threshold" conflated the sensitivity target with the decision threshold.
2. **Correct Scientific Terminology Established:**
   - **0.1389** is defined strictly as the **"development-derived decision threshold"**.
   - The threshold was empirically selected based on a development operating-point target of **$\ge 90\%$ sensitivity**.
3. **Illustrative Demonstration Status:**
   - The component demo (`/components/`) explicitly states that all rendered gauge values and indicator positions are **static demonstration data** for visual layout verification only.
   - The threshold indicator is marked as locked (read-only reference marker) and cannot be adjusted by the user.
4. **Primary UI Exposure:**
   - $0.1389$ is not prominently featured as an application metric or KPI card in the primary navigation or overview header.
   - It is housed strictly in context within the model methodology page (`/about/`) and designated result explanation gauges when inference is activated in later phases.

---

## 3. Neutral Terminology Audit (Clinical Role De-escalation)

### Policy Constraint
Under the `research-governance` skill, the dashboard is a **research decision-support prototype** developed for academic evaluation on NHANES survey data. It is not clinically validated, nor is it deployed in a clinical setting.

### Replacements Applied Across Templates and Views

| Premature / Disallowed Term | Approved Neutral Term | Files Modified |
| :--- | :--- | :--- |
| `clinical decision-support system` | `screening decision-support prototype` | `base.html`, `about.html` |
| `clinical dashboard` | `research screening dashboard` | `base.html`, `overview.html` |
| `clinician triage` / `clinician review` | `human review` / `screening review` | `review_queue.html`, `views.py` |
| `clinical recommendation` | `screening recommendation` | `new_screening.html`, `about.html` |
| `clinical workflow` | `guided review workflow` | `base.html`, `overview.html` |
| `Clinician Review Queue` | `Screening Review Queue` | `base.html`, `review_queue.html`, `views.py` |
| `Clinician Disposition` | `Review Disposition` | `history.html` |
| `Clinical Reason` | `Documented Rationale` | `history.html` |
| `Doctor's override` | `Reviewer override` | `views.py` |

### Disclaimer Verification
The persistent disclaimer is preserved in `base.html` and displayed across all views:
> **"Research prototype — not a diagnostic tool."**

---

## 4. Font & Offline Reproducibility Strategy

### Audit Findings
Phase D2.1 included an external stylesheet link referencing Google Fonts CDN (`fonts.googleapis.com` / `fonts.gstatic.com`) for the `Inter` font family.

### Problem
An active external CDN link causes:
1. Network roundtrips and blocking render delays when offline or behind institutional firewalls.
2. Layout shifts or rendering failures during thesis defense, user studies, or offline supervision environments without internet connectivity.

### Solution Implemented
1. **Removed Remote CDN Links:** Removed all `<link rel="preconnect" ...>` and Google Fonts `<link rel="stylesheet" ...>` tags from `dashboard/predictor/templates/predictor/base.html`.
2. **Robust System Font Stack:** Relies on local font installations and system font primitives via `design_system.css`:
   ```css
   font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
   ```
3. **Offline Zero-Dependency Guarantee:** All routes render 100% locally with zero external network requests. Confirmed via programmatic test client run.

---

## 5. Placeholder & Empty-State Audit

### Audit Findings
Prior templates contained hardcoded mockup rows (e.g. participant `#1048`, `#1047`) and hardcoded metrics that risked being misinterpreted as real clinical research evidence.

### Corrections Applied
1. **Overview Page (`/`):**
   - Removed hardcoded participant mockup records `#1048` and `#1047`.
   - Connected recent activity table directly to Django database query (`recent_predictions`).
   - Implemented an empty-state illustration when database record count is zero (`"No screening records in database yet."`).
   - Removed hardcoded threshold metric card.
2. **Review Queue (`/review/`):**
   - Removed hardcoded mockup row `#1048`.
   - Wired to `pending_screenings` context with empty state: `"No cases currently awaiting human review. New high-risk screenings will automatically appear here."`
3. **Analytics Page (`/analytics/`):**
   - Replaced premature terminology (`"Clinician Overrides"` $\rightarrow$ `"Human Overrides"`).
   - Added conditional empty state when total override records equal zero.
4. **History Page (`/history/`):**
   - Clean empty state displayed when no prediction records exist.

---

## 6. Inference & Model Artifact Integrity Audit

### Code Audit
Programmatic review confirmed that no Phase D2.1/D2.1A views or templates:
- Call `predict_mu`, `predict_proba`, or `predict` for active screening.
- Load or invoke `nhanes_feasibility_2021_2023/models_phase5/gam_final.pkl`.
- Calculate or compare screening probabilities against $0.1389$.
- Generate SHAP or InterpretML explanations.

### SHA-256 Checksum Verification
Both frozen research artifacts were verified using PowerShell `Get-FileHash`:

| Artifact | Canonical SHA-256 Hash | Status |
| :--- | :--- | :--- |
| `nhanes_feasibility_2021_2023/models_phase5/gam_final.pkl` | `204A94FF072EF4F1EDECEBF5A643738C006BBF010F3817B4BB798D3EA6FEF41D` | **MATCH (Byte-identical)** |
| `nhanes_feasibility_2021_2023/models_phase5/preprocessor.pkl` | `6E56A01993A4A6971EB62C82699C49DA6F31A3ACEC2A1169E07862409F42824D` | **MATCH (Byte-identical)** |

---

## 7. QA Verification Summary

- `python manage.py check`: Passed (0 issues).
- `python manage.py makemigrations --check --dry-run`: No changes detected (0 migrations created).
- **Automated Route Test (Django Test Client):**
  - `/` (Overview) $\rightarrow$ HTTP 200 (Clean, No CDN links)
  - `/screening/new/` (New Screening) $\rightarrow$ HTTP 200 (Clean, No CDN links)
  - `/review/` (Review Queue) $\rightarrow$ HTTP 200 (Clean, No CDN links)
  - `/history/` (History) $\rightarrow$ HTTP 200 (Clean, No CDN links)
  - `/analytics/` (Analytics) $\rightarrow$ HTTP 200 (Clean, No CDN links)
  - `/about/` (About Model) $\rightarrow$ HTTP 200 (Clean, No CDN links)
  - `/components/` (Component Demo) $\rightarrow$ HTTP 200 (Clean, No CDN links)
- **Local Server Daemon:** Active and responding on `http://127.0.0.1:8000/`.

---

**PHASE D2.1A COMPLETE — FOUNDATION GOVERNANCE CLEAN**
