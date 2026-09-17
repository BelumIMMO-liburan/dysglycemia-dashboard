# Project Reset Notice

**Reset Timestamp:** 2026-09-04T12:38:45+07:00  
**Status:** Active Workspace Rebuilt — Clean Implementation Skeleton Initialized

---

## 1. Preservation of Historical Research Pipeline

The completed machine learning research, data preparation pipeline, feasibility audits, cross-validation benchmarks, model selection audits, confirmatory final test evaluation, and all frozen model artifacts have been archived and cryptographically verified in an external, immutable location:

- **External Research Archive Path:**  
  `C:\Users\Felix\Documents\Skripsi_Research_Archive_2026-09-04`

This external snapshot contains the complete scientific record (876 files, ~70.29 MB) with 100.0000% SHA256 bitwise parity verified against the pre-reset workspace. All pre-specified research locks, final test predictions (`fac969a00df5...`), and frozen model binaries (`gam_final.pkl`, `logistic_final.pkl`, `dlnn_final.keras`, `preprocessor.pkl`) are preserved in their exact historical state.

---

## 2. Active Workspace Rebuilding Rationale

The active workspace (`C:\Users\Felix\Documents\Skripsi`) has been intentionally cleared and re-initialized to establish a clean, production-grade foundation for the clinical screening dashboard application.

### Key Governance Principles

1. **Consumer Architecture:**  
   The new dashboard application is strictly an **operational consumer** of pre-trained, frozen research artifacts. It does not train, retrain, hyperparameter-tune, or recalibrate machine learning models.
2. **Immutable Historical Source of Truth:**  
   The research archive `C:\Users\Felix\Documents\Skripsi_Research_Archive_2026-09-04` serves as the historical scientific evidence. It must never be edited, overwritten, or used as an active development workspace.
3. **Controlled Artifact Ingestion:**  
   Frozen research artifacts (e.g., `preprocessor.pkl`, `gam_final.pkl`, schema definitions, and operating point thresholds) will be copied into the active project only when explicitly needed by the dashboard runtime service.
4. **Clean Decoupled Implementation:**  
   The application codebase will be structured cleanly without legacy experimental notebooks, temporary scratch files, or intermediate training caches.

---

## 3. Directory Layout

The reset workspace contains only the following top-level components:

```text
Skripsi/
├── README.md                     # Active project overview & architecture notes
├── RESET_COMPLETION_REPORT.md    # Cryptographic snapshot verification & reset audit report
├── docs/                         # Architecture, clinical requirements, and API documentation
│   └── PROJECT_RESET_NOTICE.md   # This notice
├── design/                       # UI/UX design specifications, wireframes, and design system tokens
├── dashboard/                    # Clean clinical screening web application workspace
├── notebooks/                    # Dedicated workspace for presentation/consumption notebooks
└── research_reference/           # Ingested frozen schemas and pre-computed reference artifacts
```
