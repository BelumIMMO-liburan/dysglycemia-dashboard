# Dashboard Design Philosophy: Evidence-First Guided Review

**Phase:** D1 — Design Foundation  
**System Class:** Clinical Decision Support System (CDSS) for Health Screening  
**Core Motto:** "Evidence-First Guided Review"  
**Date:** 2026-09-04  

---

## 1. The Interaction Model: Evidence-First Guided Review

Traditional health AI applications often adopt an authoritarian **"Oracle Model"** where the algorithm outputs a definitive diagnostic verdict (e.g., *"Patient has Diabetes — 94% confidence"*) and forces the clinician into a passive role. 

In contrast, this system operates under the **"Evidence-First Guided Review"** paradigm:

```
┌─────────────────────────────────────────────────────────────┐
│                      1. SYSTEM SCREENS                      │
│   Evaluates non-laboratory predictors using frozen GAM.     │
│   Calculates screening probability relative to threshold.   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     2. SYSTEM EXPLAINS                      │
│   Decomposes log-odds score into additive term splines.     │
│   Identifies key elevating and moderating risk factors.     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      3. HUMAN REVIEWS                       │
│   Clinician inspects screening signal and explanations.     │
│   Synthesizes AI output with clinical context & history.    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   4. HUMAN DECIDES ACTION                   │
│   Clinician accepts referral or executes logged override.   │
│   Confirmatory Stage-2 HbA1c is ordered if indicated.       │
└─────────────────────────────────────────────────────────────┘
```

**Core Axiom:**  
The algorithm does NOT diagnose the patient. The algorithm **screens** and **recommends referral**; the clinician **reviews**, **interprets**, and **decides clinical action**.

---

## 2. Ten Core Design Principles

### Principle 1: Screening, Not Diagnosis
- **Rule:** The system must never claim to determine disease state.
- **Implementation:** The output is designated as a **"Screening Signal"** (Elevated vs Non-Elevated), and the resulting clinical pathway is **"Refer for Stage-2 HbA1c Assessment"**. Disclaimers highlighting that definitive diagnosis requires laboratory testing are prominently placed on every screening result surface.

### Principle 2: Human Authority Remains Explicit
- **Rule:** The machine makes recommendations; the human makes decisions.
- **Implementation:** The UI distinguishes between **"System Recommendation"** and **"Clinical Decision"**. The system never automatically enrolls a patient into treatment or closes a case without clinician review.

### Principle 3: Explanation Precedes Override
- **Rule:** A clinician should understand why the model reached a conclusion before deciding whether to overturn it.
- **Implementation:** The override action is co-located with or positioned immediately following the factor contribution breakdown. Overriding requires reviewing the primary elevating factors to prevent reflex dismissals.

### Principle 4: Progressive Disclosure
- **Rule:** Keep primary surfaces uncluttered; reveal deep statistical detail on demand.
- **Implementation:** The result card displays high-level factor directions (e.g., *"Waist Circumference: Strong Elevating Factor"*). Clinicians or researchers wishing to inspect raw spline shapes, confidence intervals, or log-odds values can expand details via accessible accordions.

### Principle 5: Low Cognitive Load
- **Rule:** Information must be scannable in under 5 seconds during clinical consultations.
- **Implementation:** High whitespace, strict visual hierarchy, 4-card semantic form grouping, and scannable tabular queues. Eliminates non-essential decorative animations, gradients, and secondary widgets.

### Principle 6: Uncertainty is Visible but Non-Alarmist
- **Rule:** Convey model uncertainty calmly without inducing clinical panic.
- **Implementation:** Screening probability is presented as a percentage alongside the calibrated decision threshold ($0.1389$). The system rejects blinking banners, siren emojis (🚨), and bright red warning boxes, employing calm amber and slate badges.

### Principle 7: Multi-Modal State Presentation (Text + Icon + Color)
- **Rule:** Never communicate critical clinical information using color alone (WCAG 2.1 AA Compliance).
- **Implementation:** Every status indicator pairs a semantic color token with an explicit textual label and a distinct SVG icon:
  - *Elevated Signal:* Amber tint + AlertTriangle icon + text `"Elevated Screening Signal"`
  - *Non-Elevated Signal:* Slate tint + CheckCircle icon + text `"Non-Elevated Screening Signal"`
  - *Overridden:* Indigo tint + Edit icon + text `"Clinical Override Logged"`

### Principle 8: Research Limitations Remain Visible
- **Rule:** The academic boundaries of the research must not be hidden behind slick marketing visuals.
- **Implementation:** The dedicated **"About the Model"** section and contextual information modals explicitly document:
  - Model derived from US NHANES 2021–2023 data.
  - Lack of external Indonesian population validation.
  - Unweighted survey regression design.
  - Research prototype classification.

### Principle 9: Model Complexity is Hidden from Primary Users
- **Rule:** Clinical end-users should not be burdened with internal ML mechanics during routine screening.
- **Implementation:** End-users are not shown model selection toggles, threshold adjustment sliders, hyperparameter controls, or loss function comparisons. The system executes the single pre-specified, locked primary model (GAM).

### Principle 10: Every Major Interaction is Auditable
- **Rule:** Reproducibility and clinical accountability require an immutable audit trail.
- **Implementation:** All inputs, model inferences, term contributions, reviewer identities, override decisions, structured reasons, clinical notes, and timestamps are recorded in the database and surfaced in the Screening History and Detail views.
