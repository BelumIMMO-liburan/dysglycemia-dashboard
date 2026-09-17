# Phase D2 Implementation Plan: Phased Engineering Blueprint

**Phase:** D2 — Dashboard Implementation & Refactoring  
**Execution Governance:** Sequenced Phased Rollout with Strict Definition of Done (DoD)  
**Date:** 2026-09-04  

---

## 1. Overview & Phased Roadmap

Phase D2 executes the architectural and design specifications established in Phase D1. The implementation is broken into 13 discrete, sequential work packages. No package may commence until its predecessor satisfies all research-governance checks and Definitions of Done.

```
D2.1 Shell & Tokens
       ↓
D2.2 Intake Form ───→ D2.3 GAM Engine
                             ↓
                      D2.4 Result Surface
                             ↓
                      D2.5 XAI Decomposition
                             ↓
                      D2.6 Human Review ───→ D2.7 Override Modal
                                                    ↓
                                             D2.8 Stage-2 Lab Intake
                                                    ↓
                                             D2.9 Audit History
                                                    ↓
                                             D2.10 Research Analytics
                                                    ↓
                      D2.11 A11y & D2.12 Responsive Audits
                             ↓
                      D2.13 User-Study Ready Freeze
```

---

## 2. Phase-by-Phase Execution Specifications

### D2.1: Application Shell, Navigation & Design Tokens
- **Scope:** Replace legacy `style.css` with modular `design_system.css` containing Direction A ("Clinical Neutral") HSL tokens. Refactor `base.html` to implement the shadcn-inspired left sidebar, header breadcrumbs, active route resolver, and Lucide SVG icon system.
- **Definition of Done:**
  - Complete elimination of legacy emojis and blur-heavy glassmorphism.
  - Sidebar correctly highlights active route and collapses gracefully on narrow viewports.
  - Theme toggle switches seamlessly between Light and Dark mode using CSS custom properties.
- **Governance Check:** Verify no marketing KPI widgets or obsolete model links exist in navigation.

### D2.2: Stage-1 New Screening Form (7 Predictors)
- **Scope:** Implement the 4-card semantic form in `index.html` accepting **only the seven non-laboratory predictors**: `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`.
- **Definition of Done:**
  - Total removal of `HbA1c`, `glucose`, model selection dropdown, and threshold slider from the form.
  - Field-tied deterministic client and server-side validation with inline error messages.
  - Clear visual hierarchy with primary `[ Run Screening ]` and secondary `[ Clear Form ]`.
- **Governance Check:** Confirm that no laboratory biomarkers are requested or accepted.

### D2.3: Frozen GAM Inference Integration
- **Scope:** Refactor `predictor/model_loader.py` to point exclusively to the canonical Phase-5 research model: `nhanes_feasibility_2021_2023/models_phase5/gam_final.pkl` using `preprocessor.pkl`. Remove all Kaggle models and scalers. Hardcode operating threshold to `0.1389`.
- **Definition of Done:**
  - Python inference pipeline executes in $<5\text{ms}$.
  - Unit tests verify that identical inputs produce exact probabilities matching Phase-5 evaluation data.
  - Model selection parameters are completely purged from backend code.
- **Governance Check:** SHA256 checksum verification of `gam_final.pkl` against locked Phase-4.2 manifest.

### D2.4: Screening Result Surface
- **Scope:** Refactor `result.html` to present the decision-support status:
  - If $p \ge 0.1389 \rightarrow$ `Elevated Screening Signal` (Amber badge) + `Refer for Stage-2 HbA1c`.
  - If $p < 0.1389 \rightarrow$ `Non-Elevated Screening Signal` (Slate badge) + `Routine Monitoring`.
  - Restrained probability meter indicating score relative to the $13.9\%$ threshold.
- **Definition of Done:**
  - Elimination of alarmist words ("High Risk", "Suspek", "Diabetic") and siren icons.
  - Mandatory disclaimer visible: *"This screening tool does not provide a medical diagnosis."*
- **Governance Check:** Threshold is hardcoded; no sliders or user overrides of probability exist.

### D2.5: Model-Native Additive XAI Explanation
- **Scope:** Implement GAM-native additive term decomposition in `predictor/xai_engine.py`. Evaluate individual spline term values $f_i(x_i)$ relative to population mean. Render two-column list: Factors Elevating vs Factors Moderating.
- **Definition of Done:**
  - Deletion of legacy `shap_explainer.py` and removal of `shap` from runtime dependencies.
  - Zero sampling latency; instant rendering alongside result card.
  - Expandable accordion exposing underlying spline basis details for clinical researchers.
- **Governance Check:** Verify terms sum exactly to the log-odds score (zero approximation error).

### D2.6: Human Guided Review Workspace
- **Scope:** Implement the review card on the result page presenting the automated referral recommendation with explicit choices: `[ Accept Recommendation ]` vs `[ Override Recommendation ]`.
- **Definition of Done:**
  - Clicking `[ Accept ]` updates review status and advances referred participants to the Stage-2 queue.
  - Clinician identity and review timestamp are recorded.
- **Governance Check:** AI probability and signal remain completely immutable in the database.

### D2.7: Structured Override Dialog Modal
- **Scope:** Implement accessible HTML5 `<dialog>` for overrides. Display comparison panel (AI Recommendation vs Proposed Human Action). Require mandatory structured reason dropdown and clinical note textarea.
- **Definition of Done:**
  - Traps keyboard focus; closes on `Escape` without side-effects.
  - Form requires both categorical reason code and explanatory note before submission.
  - In backend: records `ClinicalReview` row; never inverts biological disease labels.
- **Governance Check:** Ensure `override_value` does NOT flip disease classes (fixing P0-5).

### D2.8: Stage-2 Confirmatory Laboratory Intake
- **Scope:** Create dedicated Stage-2 form (`/screening/<id>/stage2/`) allowing clinicians to record venous blood HbA1c value ($\%$) and test date for referred participants.
- **Definition of Done:**
  - Categorizes measured HbA1c against clinical reference standards: Normal ($<5.7\%$), Prediabetes ($5.7\%-6.4\%$), Diabetes ($\ge 6.5\%$).
  - Updates case status to `Stage 2 Complete`.
- **Governance Check:** Prominent clinical note: *"Laboratory categorization follows clinical guidelines and requires doctor confirmation."*

### D2.9: Screening History & Case Audit Detail
- **Scope:** Refactor `history.html` into a high-density shadcn Data Table with status filters (Pending, Accepted, Overridden, Stage 2 Complete). Build dedicated Case Detail view (`/history/<id>/`) displaying complete 3-part audit log (Intake + Review + Lab).
- **Definition of Done:**
  - Full search and pagination preserving filter query parameters.
  - Case Detail provides complete, unalterable historical provenance.
- **Governance Check:** All historical records preserve immutable model versions and thresholds.

### D2.10: Research Analytics & Quality Surveillance
- **Scope:** Refactor `analytics.html` to compute correct research metrics: total sessions, reviewed cases, AI referral rate, concordance rate, and Stage-2 confirmatory yield. Render 3 focused charts via Chart.js.
- **Definition of Done:**
  - Fix mathematical denominator bug: $\text{Override Rate} = N_{\text{overrides}} / N_{\text{reviewed}}$.
  - Strict prohibition against labeling concordance as "AI accuracy".
- **Governance Check:** Metric calculations verified against manual database query counts.

### D2.11: Accessibility (WCAG 2.1 AA) Audit & Remediation
- **Scope:** Conduct keyboard navigation, contrast, and screen reader verification across all views.
- **Definition of Done:**
  - 100% of interactive controls reachable via keyboard with visible focus rings.
  - Text contrast ratios exceed $4.5:1$ across both light and dark themes.
  - Multi-modal status representation (text + icon + color) verified on all status badges.

### D2.12: Responsive Design & Tablet/Mobile Hardening
- **Scope:** Verify layout adaptation on Desktop ($1280\text{px}+$), Tablet ($768\text{px}-1024\text{px}$), and Mobile ($375\text{px}-430\text{px}$).
- **Definition of Done:**
  - Sidebar collapses to mobile drawer/sheet on screens $<1024\text{px}$.
  - Tables employ horizontal scroll containers or stacked cards without layout breakage.
  - Touch targets maintain minimum $44 \times 44\text{px}$ dimensions.

### D2.13: Usability-Study-Ready Freeze
- **Scope:** Embed passive telemetry data hooks (`data-telemetry-event`) across all critical workflow transitions. Final code freeze and comprehensive walkthrough documentation.
- **Definition of Done:**
  - Complete automated test suite covering model inference, form validation, review logging, and analytics.
  - Creation of `D2_COMPLETION_WALKTHROUGH.md` and user testing protocol.
- **Governance Check:** Final sign-off by research supervisor.
