# Information Architecture & Sitemap Specification

**Phase:** D1 — Design Foundation  
**Scope:** Navigation Structure, View Hierarchies, and Route Architecture  
**Date:** 2026-09-04  

---

## 1. Information Architecture Overview

The information architecture is designed around two functional domains:
1. **Screening & Clinical Workflow:** Direct operational tasks performed by screening personnel and reviewing clinicians (Intake, Decision Support, Override Review, Confirmatory Lab Tracking, and Audit).
2. **Research & Governance:** Administrative oversight, methodological transparency, and quality assurance for research investigators and clinical supervisors.

```
Dashboard Architecture
├── Screening (Operational Domain)
│   ├── New Screening (Stage 1 Non-Lab Intake)
│   │   └── Screening Result & Explanation (Immediate Output)
│   ├── Review Queue (Pending Clinician Action)
│   │   └── Case Review & Override Workspace
│   ├── Stage-2 Confirmatory Intake (HbA1c Lab Result Entry)
│   └── Screening History & Audit Log (Full Case Repository)
│       └── Case Audit Detail View
└── Research & Governance (Governance Domain)
    ├── Research Analytics (Quality, Concordance & Throughput Metrics)
    └── About the Model (Methodology, Held-Out Performance & Limitations)
```

---

## 2. Navigation Structure & Sidebar Taxonomy

The primary navigation resides in a permanent left sidebar, organized into two restrained semantic sections:

### Section A: Screening (Primary Clinical Operations)
- **New Screening** (`/screening/new/`): Primary entry point for participant intake. Focuses purely on Stage-1 non-laboratory predictors.
- **Review Queue** (`/review/`): Filtered list of cases requiring clinician review (specifically cases with elevated signals or pending confirmatory referral decisions). Shows count badge (e.g., `Review Queue [3]`).
- **Screening History** (`/history/`): Complete, searchable, and filterable repository of all processed screenings, override records, and Stage-2 outcomes.

### Section B: Research & Governance (Audit & Methodology)
- **Research Analytics** (`/analytics/`): High-level operational metrics, referral rates, clinician-AI concordance rates, and override distributions.
- **About the Model** (`/about/`): Complete academic transparency page detailing the Phase 4/5 GAM model, training cohort (NHANES 2021–2023), locked $0.1389$ threshold, held-out test performance, and explicit clinical limitations.

---

## 3. URL Route Specifications & View Mapping

| URL Pattern | View Function / Class | Page Title | Primary Intent & Functionality |
| :--- | :--- | :--- | :--- |
| `/` | `overview_view` | Overview | High-level clinical orientation: quick-start screening trigger, pending queue status, recent screening feed. |
| `/screening/new/` | `new_screening_view` | New Screening | Stage-1 non-laboratory input form (7 predictors). Deterministic validation. |
| `/screening/<int:pk>/` | `screening_result_view` | Screening Result #ID | Decision-support display: signal, probability, factor decomposition (XAI), review trigger. |
| `/review/` | `review_queue_view` | Review Queue | Tabular triage queue displaying unreviewed cases and pending referrals. |
| `/review/<int:pk>/` | `case_review_view` | Review Case #ID | Guided review workspace: accept referral or launch structured override modal. |
| `/screening/<int:pk>/stage2/` | `stage2_entry_view` | Stage-2 Lab Intake #ID | Recording laboratory venous HbA1c value ($\%$) and date for referred participants. |
| `/history/` | `history_view` | Screening History | Tabular audit log with multi-criteria filtering (status, date, reviewer). |
| `/history/<int:pk>/` | `history_detail_view` | Case Detail #ID | Comprehensive 3-part audit view: System Output + Human Action + Lab Outcome. |
| `/analytics/` | `analytics_view` | Research Analytics | Aggregate research metrics, override statistics, and concordance rates. |
| `/about/` | `about_model_view` | About the Model | Methodological documentation, held-out test metrics, and clinical limitations. |

---

## 4. Protected Governance Boundaries (What is Excluded from Users)

To protect research integrity and prevent user confusion, the following elements are **strictly excluded from all user-facing interfaces**:
1. **Model Selection Menu:** No capability to switch to DLNN, Logistic Regression, or legacy Kaggle models. The GAM is permanently executed.
2. **Threshold Slider:** The operating threshold ($0.1389$) is locked in code. No slider, dial, or input is provided to change it.
3. **Hyperparameter / Training Controls:** No runtime model fitting, retraining, or parameter tuning.
4. **Multi-Model Consensus Badges:** No adversarial model comparisons displayed to clinicians.

---

## 5. Breadcrumb & Page Context Hierarchy

All subpages implement a standard breadcrumb navigation pattern to maintain contextual awareness:
- *Screening Intake:* `Screening / New Screening`
- *Screening Result:* `Screening / Result #1042`
- *Review Queue:* `Screening / Review Queue`
- *Case Review:* `Screening / Review Queue / Case #1042`
- *Stage-2 Entry:* `Screening / History / Case #1042 / Stage-2 Lab Entry`
- *History Detail:* `Screening / History / Case #1042 (Audit Detail)`
