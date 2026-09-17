# D3 Data Environment Isolation & Study Baseline Architecture

**Audit Date:** 2026-09-05  
**Core Objective:** Absolute separation between development/demo records and clean formal user-study data (Requirement P0).

---

## 1. Architecture of Database Separation

To prevent accidental mixing of QA/test data with formal participant responses, the application implements environment-driven database isolation:

```
                  ┌──────────────────────────────────────────────┐
                  │   Application Configuration (settings.py)    │
                  │   APP_DATA_MODE = os.environ.get(...)        │
                  └──────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     [ APP_DATA_MODE=development ]                    [ APP_DATA_MODE=study ]
                 │                                               │
                 ▼                                               ▼
       Active DB: db.sqlite3                           Active DB: db_study.sqlite3
  - Contains 29 QA/demo screenings               - Clean zero-state baseline
  - Archived copy preserved:                     - Exactly 0 ScreeningRecords
    db_development_archive_d2_10.sqlite3         - Exactly 0 ScreeningExplanations
  - Discreet UI notice on Analytics              - Exactly 0 HumanReviews
  - Design System UI link visible                - Exactly 0 Stage2Assessments
                                                 - Discreet UI notice suppressed
                                                 - Design System UI link hidden
```

---

## 2. Preserved Development Evidence Archive

Before creating any clean study database, the populated development database containing 29 demonstration cases from Phases D2.1–D2.10 was permanently archived:

- **Archived Filename:** `dashboard/db_development_archive_d2_10.sqlite3`
- **File Size:** 249,856 bytes
- **SHA-256 Hash:** `8b11a9ffbdc4641cd9164f16697a565ee8de027407f4257c3437bb8fc525c566`
- **Timestamp:** 2026-09-05T03:30:00Z
- **Purpose:** Audit record and baseline evidence for D2.1–D2.10 implementation reports.
- **Privacy Audit:** Contains zero participant PII.

---

## 3. Formal Study Database Initialization & Zero-State

The formal study database was initialized from zero using clean Django migrations without synthetic seeding:

- **Database Filename:** `dashboard/db_study.sqlite3`
- **File Size:** 249,856 bytes
- **SHA-256 Hash:** `865b75f6fd511effde7d6e0f84f4b2e17d9e69af2f3eebc3e19d63dffe537e77`
- **Table Record Counts Verified:**
  - `predictor_screeningrecord`: **0**
  - `predictor_screeningexplanation`: **0**
  - `predictor_humanreview`: **0**
  - `predictor_stage2assessment`: **0**
  - `predictor_prediction` (legacy): **0**
  - `predictor_override` (legacy): **0**

---

## 4. UI Safeguards Against Data Mixing

1. **Development Warning Banner:** In development mode (`APP_DATA_MODE='development'`), `/analytics/` displays a persistent, visible alert:
   > *"Development Environment Notice: Development environment — displayed records may include synthetic or QA data."*
   This ensures that screenshots or demo figures (e.g. 29 screenings) are never mistaken for research findings.
2. **Zero-State Display in Study Mode:** In study mode (`APP_DATA_MODE='study'`), `/analytics/` displays empty-state cards (*"Total Screenings: 0"*, rates displayed as *"Not available"*), preventing ungrounded claims before study commencement.
3. **No Destructive Reset Buttons:** No web UI button exists to wipe or flush the database. Study data cannot be deleted from the browser.
