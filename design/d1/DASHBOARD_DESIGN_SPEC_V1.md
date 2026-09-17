# Master Dashboard Design & Architectural Specification (Version 1.0)

**Project:** Two-Stage Non-Laboratory Screening System for Previously Unrecognized HbA1c-Defined Dysglycemia  
**Phase:** D1 — Design Foundation, UI Reference Research, and Application Architecture  
**Date:** 2026-09-04  
**Status:** COMPLETE — READY FOR HUMAN REVIEW  

---

## 1. Executive Summary & Document Authority

This master document unifies and synthesizes the complete design foundation for the clinical dashboard redesign (`Phase D1`). The machine-learning research experimentation is **closed and immutable**. The dashboard represents the translation and human-interaction layer: a clinical decision-support system (CDSS) designed to operationalize the research findings for healthcare practitioners and study evaluators.

This specification consolidates fifteen detailed architectural deliverables located in `design/d1/`:
- [`01_EXISTING_APPLICATION_AUDIT.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/01_EXISTING_APPLICATION_AUDIT.md)
- [`02_RESEARCH_GOVERNANCE_AUDIT.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/02_RESEARCH_GOVERNANCE_AUDIT.md)
- [`03_UI_REFERENCE_RESEARCH.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/03_UI_REFERENCE_RESEARCH.md)
- [`04_SHADCN_COMPONENT_MAPPING.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/04_SHADCN_COMPONENT_MAPPING.md)
- [`05_DASHBOARD_DESIGN_PHILOSOPHY.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/05_DASHBOARD_DESIGN_PHILOSOPHY.md)
- [`06_INFORMATION_ARCHITECTURE.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/06_INFORMATION_ARCHITECTURE.md)
- [`07_CORE_USER_FLOW.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/07_CORE_USER_FLOW.md)
- [`08_TEXTUAL_WIREFRAMES.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/08_TEXTUAL_WIREFRAMES.md)
- [`09_DESIGN_TOKENS.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/09_DESIGN_TOKENS.md)
- [`10_ACCESSIBILITY_REQUIREMENTS.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/10_ACCESSIBILITY_REQUIREMENTS.md)
- [`11_XAI_PRESENTATION_OPTIONS.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/11_XAI_PRESENTATION_OPTIONS.md)
- [`12_HUMAN_OVERRIDE_DESIGN.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/12_HUMAN_OVERRIDE_DESIGN.md)
- [`13_RESEARCH_ANALYTICS_DESIGN.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/13_RESEARCH_ANALYTICS_DESIGN.md)
- [`14_FRONTEND_ARCHITECTURE_RECOMMENDATION.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/14_FRONTEND_ARCHITECTURE_RECOMMENDATION.md)
- [`15_IMPLEMENTATION_PLAN_D2.md`](file:///c:/Users/Felix/Documents/Skripsi/design/d1/15_IMPLEMENTATION_PLAN_D2.md)

---

## 2. Research Governance & Methodological Immutability

The dashboard is strictly constrained by the frozen empirical outputs of the completed thesis research:
1. **Primary Model:** Generalized Additive Model (GAM), $n\_splines=10, \lambda=10.0$ (`nhanes_feasibility_2021_2023/models_phase5/gam_final.pkl`).
2. **Predictor Set (Exactly 7 Non-Laboratory Features):** `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`.
3. **Strict Exclusion of Laboratory Biomarkers:** `HbA1c` and fasting `glucose` are **strictly prohibited** from Stage-1 screening intake.
4. **Frozen Operating Threshold:** Exactly **$0.1389$** (derived on development data to enforce $\ge 90\%$ screening sensitivity). No user slider or runtime threshold modification is permitted.
5. **Held-Out Confirmatory Performance:** Sensitivity $86.39\%$, Specificity $42.51\%$, ROC-AUC $0.7277$, PR-AUC $0.4503$.
6. **Screening vs Diagnosis:** The system outputs an elevated screening signal that recommends referral for Stage-2 laboratory HbA1c assessment; it never diagnoses diabetes.
7. **Human Override Semantics:** Human review applies to the **referral decision**, never to biological disease labels. Overriding does not alter the machine's calculated probability or signal.

---

## 3. Core Design Philosophy: "Evidence-First Guided Review"

The application rejects the authoritarian "AI Oracle" paradigm in favor of **Evidence-First Guided Review**:

$$\text{SYSTEM SCREENS} \longrightarrow \text{SYSTEM EXPLAINS} \longrightarrow \text{HUMAN REVIEWS} \longrightarrow \text{HUMAN DECIDES ACTION}$$

### Ten Foundational Principles
1. **Screening, Not Diagnosis:** Calm triage replacing diagnostic claims.
2. **Human Authority Remains Explicit:** Machine recommends; human decides.
3. **Explanation Precedes Override:** Clinicians inspect factor decomposition before taking action.
4. **Progressive Disclosure:** Essential summary first; statistical spline details on demand.
5. **Low Cognitive Load:** Scannable in $<5$ seconds during clinical consultations.
6. **Uncertainty is Visible but Non-Alarmist:** Probability percentage and threshold line; zero flashing alerts.
7. **Multi-Modal State Presentation:** Every state couples color tint + text + distinct icon.
8. **Research Limitations Remain Visible:** Explicit disclosure of US NHANES origin and unweighted survey design.
9. **Model Complexity Hidden from Primary Users:** No model selection menus or hyperparameter dials.
10. **Immutable Auditability:** Every input, term contribution, review disposition, reason, and timestamp is permanently recorded.

---

## 4. Primary Visual Reference: shadcn/ui

The visual system translates the design character of **`shadcn/ui`** into a robust clinical environment:
- **Surfaces:** Clean, neutral slate foundation with high whitespace and low cognitive fatigue.
- **Borders:** Crisp 1px borders (`--border: 214 32% 91%` light, `217 33% 20%` dark) replacing heavy shadows.
- **Typography:** `Inter` with tabular numerals (`.tabular-nums`) for precise alignment of clinical statistics.
- **Status Badges:** Compact rounded pills with muted background tints (e.g., Amber for elevated signal, Slate for non-elevated).
- **Icons:** Restrained, accessible SVG icons (Lucide-style), replacing legacy Unicode emojis.
- **Anti-Patterns Eliminated:** Complete removal of glassmorphism, neumorphism, saturated neon gradients, and decorative AI sparkle graphics.

---

## 5. End-to-End Primary User Flow

```
[ INTAKE ]
Clinician enters 7 non-laboratory predictors at /screening/new/
Deterministic validation ensures biological validity
       │
       ▼
[ SCREENING RESULT ]
Frozen GAM executes: logit(p) = β0 + Σ f_i(x_i)
Probability (p) evaluated against frozen 0.1389 threshold
Displays: Elevated Signal vs Non-Elevated Signal + Non-alarmist meter
       │
       ▼
[ TRANSPARENT XAI EXPLANATION ]
Model-Native Additive Term Decomposition (Option A)
Displays Factors Elevating vs Factors Moderating log-odds score
       │
       ▼
[ CLINICIAN GUIDED REVIEW ]
Reviewer inspects recommendation: "Refer for Stage-2 HbA1c"
├── [ Accept Recommendation ]  ──→ Confirmed; advances to Stage-2 Queue
└── [ Override Recommendation ] ──→ Triggers accessible AlertDialog modal
                                   Requires structured clinical reason + note
                                   Logs override disposition without flipping machine probability
       │
       ▼ (For Referred Participants)
[ STAGE-2 CONFIRMATORY INTAKE ]
Venous blood collected; laboratory reports HbA1c value (%)
Clinician records HbA1c at /screening/<id>/stage2/
Categorizes into reference ranges: Normal (<5.7%), Prediabetes (5.7%-6.4%), Diabetes (≥6.5%)
Case permanently closed and archived in Audit History
```

---

## 6. Information Architecture & Sitemap

```
Application Root (/)
├── Screening Domain
│   ├── /screening/new/          (Stage-1 7-Predictor Intake Form)
│   ├── /screening/<id>/         (Result Surface + Native XAI Decomposition + Review Card)
│   ├── /review/                 (Triage Queue for Pending Clinician Reviews)
│   ├── /review/<id>/            (Focused Review & Override Workspace)
│   ├── /screening/<id>/stage2/  (Stage-2 Confirmatory HbA1c Intake)
│   └── /history/                (Complete Searchable Audit History Table)
│       └── /history/<id>/       (3-Part Case Detail: Intake + Review + Laboratory)
└── Governance Domain
    ├── /analytics/              (Research Surveillance: Throughput, Concordance, Yield)
    └── /about/                  (Methodology, NHANES Cohort, Locked Metrics & Limitations)
```

---

## 7. Component Strategy & Architecture Recommendation

### Technology Stack: Option B (Enhanced Django Templates + Native shadcn CSS System)
- **Backend:** Python 3.10 / Django 5.2.12.
- **Persistence:** SQLite 3 (`db.sqlite3`).
- **Styling:** Custom vanilla CSS (`design_system.css`) replicating shadcn's HSL tokens, 4px grid, and typography. Zero Node.js build dependency.
- **Primitives:** Native HTML5 `<dialog>` for modal focus traps, native `<details>` for factor accordions, and native `<select>` for form controls.
- **Analytics Visualization:** Lightweight Chart.js v4.4.0 configured with monochrome/neutral palettes.
- **XAI Engine:** **Option A (GAM-Native Additive Term Decomposition)**. Evaluates spline curves $f_i(x_i)$ directly in $<1\text{ms}$ with zero sampling error, permanently retiring the slow, unfaithful KernelSHAP pipeline.

### Visual Directions Supported
- **Direction A: "Clinical Neutral" (Default):** Slate/Stone neutral surfaces with cool blue primary. Formal, dependable, and institutional.
- **Direction B: "Research Teal" (Alternative):** Zinc neutral surfaces with muted teal primary. Modern and research-oriented.

---

## 8. Phased Implementation Roadmap (Phase D2)

| Phase Package | Target Milestone | Primary Governance Check |
| :--- | :--- | :--- |
| **D2.1** | Application Shell, Navigation & Design Tokens | Purge legacy glassmorphism & emojis; install shadcn HSL tokens. |
| **D2.2** | Stage-1 New Screening Form | Verify exactly 7 non-lab predictors; zero lab biomarkers. |
| **D2.3** | Frozen GAM Inference Integration | Verify model SHA256; hardcode $0.1389$ threshold; purge Kaggle models. |
| **D2.4** | Screening Result Surface | Verify calm, non-alarmist status; enforce diagnostic disclaimers. |
| **D2.5** | Model-Native Additive XAI Engine | Decompose spline terms; purge `shap` library dependency. |
| **D2.6** | Clinician Guided Review Workspace | Enforce review of referral; ensure AI probability remains immutable. |
| **D2.7** | Structured Override Dialog Modal | Native `<dialog>` focus trap; mandatory structured clinical justification. |
| **D2.8** | Stage-2 Confirmatory Laboratory Intake | Independent lab entry form; standard clinical HbA1c ranges. |
| **D2.9** | Screening History & Case Audit Detail | Comprehensive 3-part audit log; high-density Data Table. |
| **D2.10** | Research Analytics & Quality Surveillance | Fix denominator bug; prevent labeling agreement as "accuracy". |
| **D2.11** | WCAG 2.1 AA Accessibility Audit | $100\%$ keyboard operable; text contrast $\ge 4.5:1$; multi-modal status. |
| **D2.12** | Responsive Hardening | Fluid adaptation on Desktop, Tablet ($44\text{px}$ touch targets), and Mobile. |
| **D2.13** | Usability-Study-Ready Freeze | Passive telemetry hooks pre-wired; automated test suite passing. |

---

## 9. Tool & Environment Availability Report

Per project governance, this section explicitly documents the availability of external integration tools during Phase D1:

| Tool / MCP Server | Declared Availability | Actual Status & Usage in D1 |
| :--- | :---: | :--- |
| **Context7 MCP** | **Not Available** | No tool declaration present. Native Django 5.2 and web standards referenced directly. |
| **Mobbin MCP** | **Not Available** | No tool declaration present. Health assessment interaction patterns synthesized from established CDSS clinical literature. |
| **Chrome DevTools MCP** | **Not Available** | No tool declaration present. Application structure and DOM audit conducted directly on Django source files and templates. |
| **Figma MCP** | **Not Available** | No tool declaration present. Wireframing executed via comprehensive ASCII textual wireframes. |

*Compliance Statement: No tool was simulated or falsely claimed as active.*

---

## 10. Open Questions for Human Review Prior to Phase D2

Before triggering implementation in Phase D2, human evaluator sign-off is requested on the following design choices:
1. **Default Visual Direction:** Confirm whether **Direction A ("Clinical Neutral" — Blue/Slate)** is preferred over **Direction B ("Research Teal" — Teal/Zinc)** for the primary demonstration.
2. **Override Clinical Reason Codes:** Review the 5 proposed standardized clinical justification categories for overrides (Recent Normal Lab, Severe Frailty, Acute Confounding Illness, Patient Refusal, Alternative Clinical Care).
3. **Database Migration Strategy:** Confirm whether to create new clean tables for `ScreeningSession` and `ClinicalReview` alongside legacy tables, or execute a clean reset migration of `db.sqlite3`.
