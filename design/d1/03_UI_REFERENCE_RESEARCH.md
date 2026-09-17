# UI Reference Research & Interaction Pattern Analysis

**Phase:** D1 — Design Foundation  
**Primary Visual Reference:** `shadcn/ui`  
**Domain:** Clinical Decision Support & Public Health Screening Interfaces  
**Date:** 2026-09-04  

---

## 1. Executive Summary & Design Rationale

Modern clinical decision-support systems (CDSS) frequently suffer from cognitive overload, ambiguous visual hierarchies, and alarmist aesthetics. When artificial intelligence or predictive models are integrated into clinical workflows, poorly designed interfaces risk either:
1. **Automation bias:** Clinicians passively accepting model outputs without critical evaluation.
2. **Algorithm aversion:** Clinicians completely rejecting decision support due to visual clutter, alarm fatigue, or perceived opacity.

To address these challenges, this research adopts **shadcn/ui** as its primary design and component reference. Originating in the modern web ecosystem, `shadcn/ui` champions:
- **Restrained, neutral surfaces** (monochrome foundation, high whitespace, low visual noise)
- **Subtle border hierarchy** (1px crisp borders using semantic HSL tokens rather than heavy drop shadows)
- **Calm status presentation** (avoiding neon warning banners; pairing color with explicit textual status and iconography)
- **Clear interaction states** (predictable focus, hover, disabled, and active visual feedback)

This document establishes the UI patterns researched, evaluates their clinical and research fitness, and formalizes how they are adapted for this project.

---

## 2. shadcn/ui Component Pattern Study

| shadcn/ui Component | Core Interaction Pattern | Clinical Screening Utility |
| :--- | :--- | :--- |
| **Sidebar** | Collapsible, semantic left navigation with clear section groupings and active indicator. | Provides persistent orientation across the 5 core views (Screening, Queue, History, Analytics, About). |
| **Card** | Content surface bounded by a 1px border (`border-border`), subtle background (`bg-card`), and structured header/content/footer. | Encapsulates distinct semantic chunks (Demographic inputs, Body measurements, Screening results, Factor decomposition). |
| **Badge** | Small rounded pill/tag with muted semantic background and contrasting text. | Displays non-alarmist status indicators (`Elevated Signal`, `Non-Elevated`, `Pending Review`, `Overridden`). |
| **Button** | Highly predictable variants (`default`, `secondary`, `outline`, `destructive`, `ghost`). | Establishes clear action hierarchy: primary submit action vs secondary reset/cancel actions. |
| **Input / Select** | 40px standard height, subtle border, clear placeholder, visible focus ring (`ring-2 ring-primary`). | Enforces deterministic data intake for numerical predictors (`age`, `bmi`, `waist_cm`, `sedentary_minutes_day`). |
| **Alert / Callout** | Muted callout box with icon, title, and body text. | Communicates critical medical and methodology disclaimers without interrupting workflow. |
| **Accordion / Collapsible** | Smooth vertical expand/collapse mechanism for progressive disclosure. | Hides detailed statistical spline curves or historical notes until requested by the clinician. |
| **Dialog / AlertDialog** | Modal overlay with dimmed backdrop, keyboard trap, and explicit two-button confirmation. | Safeguards the **Human Override** workflow to prevent accidental overrides. |
| **Sheet / Drawer** | Slide-over lateral panel preserving page context. | Enables deep inspection of patient audit history without navigating away from the Review Queue. |
| **Data Table** | Dense, structured tabular layout with sorting, filtering, and pagination. | Manages the Review Queue and Screening History with high information clarity. |
| **Progress / Meter** | Restrained horizontal track indicating proportion. | Displays screening probability relative to the operating threshold without implying certainty. |
| **Tooltip** | Hover/focus micro-card explaining technical terms. | Clarifies research variables (e.g., CDC definition of sedentary minutes, HbA1c diagnostic cutoffs). |

---

## 3. Clinical Interaction Patterns (Mobbin & Health Informatics Research)

Below is the structured analysis of observed interaction patterns in modern health intake, decision support, and clinical review interfaces:

### Pattern 1: Multi-Category Structured Clinical Intake
- **Observed Pattern:** Splitting patient intake into clearly delineated clinical categories (Demographic, Anthropometric, Historical, Lifestyle) within a single unified page rather than a fragmented multi-step wizard.
- **Why It Fits:** Our Stage-1 screening requires exactly seven inputs. A multi-step wizard adds unnecessary clicks and cognitive friction for clinicians. A single clean page divided into logical sections allows rapid entry and immediate visual verification.
- **What We Adapt:** Grouping the 7 predictors into 4 clean cards:
  1. *Demographics* (Age, Sex)
  2. *Anthropometrics* (BMI, Waist Circumference)
  3. *Medical History* (Hypertension History, Smoking History)
  4. *Daily Activity* (Sedentary Minutes/Day)
- **What We Reject:** Long, endless scrolling questionnaires; multi-step wizard progress steps that hide previous inputs; floating conversational chatbot inputs.

### Pattern 2: Calm, Non-Alarmist Screening Result Presentation
- **Observed Pattern:** Presenting screening signals using calm, neutral cards with distinct status badges (e.g., "Elevated Screening Signal") supported by contextual probabilities and explicit next steps.
- **Why It Fits:** Prevents panic and alarm fatigue. A non-laboratory screening test is an initial triage mechanism, not a medical diagnosis. The visual tone must reflect scientific rigor rather than emergency triage.
- **What We Adapt:** 
  - Restrained amber badge for elevated signal ($p \ge 0.1389$): `Elevated Screening Signal · Referral Recommended`
  - Restrained neutral/slate badge for non-elevated signal ($p < 0.1389$): `Non-Elevated Screening Signal · Routine Monitoring`
  - Explicit prominent action: `Refer for Stage-2 HbA1c Assessment`
- **What We Reject:** Flashing red banners, neon warning sirens (🚨), "HIGH RISK / DANGER" labels, decorative heart-rate EKG lines, and large speedometer gauges implying diagnostic certainty.

### Pattern 3: Additive Factor Contribution (Transparent AI)
- **Observed Pattern:** Showing horizontal diverging contribution bars that visualize which patient features elevated or lowered the screening score relative to baseline.
- **Why It Fits:** Directly matches the mathematical formulation of Generalized Additive Models (GAM). Because GAM is additive in log-odds, each spline term $f_i(x_i)$ contributes a specific positive or negative amount to the patient's log-odds score.
- **What We Adapt:** 
  - A two-section list: *"Factors Elevating Screening Score"* and *"Factors Moderating Screening Score"*.
  - For each factor: feature name, patient's value with units, qualitative weight (Strong, Moderate, Low), and directional indicator.
  - Expandable detail displaying the underlying spline curve for clinical researchers.
- **What We Reject:** Complex multidimensional scatter plots, raw unscaled regression coefficients, or black-box KernelSHAP waterfalls that take 10+ seconds to compute.

### Pattern 4: Two-Stage Guided Override Flow
- **Observed Pattern:** In high-stakes medical AI systems, overriding an automated recommendation requires a two-step confirmation dialog showing a side-by-side comparison of the AI recommendation versus the human decision, with mandatory structured justification.
- **Why It Fits:** Protects data integrity and research audibility. It prevents clinicians from casually dismissing recommendations without documenting clinical rationale.
- **What We Adapt:** 
  - Clicking "Override Recommendation" opens an accessible `AlertDialog`.
  - The modal explicitly displays:
    - *System Recommendation:* "Refer for Stage-2 HbA1c"
    - *Human Disposition:* "Do Not Refer At This Time"
    - *Mandatory Coded Reason:* (Dropdown of validated clinical reasons, e.g., "Recent HbA1c normal within 30 days", "Active corticosteroid therapy", "Severe frailty")
    - *Mandatory Clinical Note:* Free-text area.
    - *Reviewer Attribution:* Logged clinician identity and timestamp.
- **What We Reject:** Single-click destructive overrides; silent background overrides; overriding patient biological status (flipping disease label).

### Pattern 5: Decoupled Stage-2 Confirmatory Workflow
- **Observed Pattern:** Separating screening triage from laboratory confirmation while maintaining a linked case record.
- **Why It Fits:** In clinical reality, Stage-1 non-laboratory screening happens at an initial contact or community health post, while Stage-2 HbA1c laboratory testing occurs days or weeks later upon venous blood collection.
- **What We Adapt:**
  - Cases with elevated Stage-1 signals enter a `Referred for Stage-2` queue.
  - A dedicated Stage-2 form allows entering the laboratory HbA1c value ($\%$) and date of test.
  - The system displays standard laboratory reference ranges (Normal, Prediabetes, Diabetes) strictly as laboratory standards, completing the case file.
- **What We Reject:** Blending Stage-1 inputs and Stage-2 laboratory results into a single simultaneous form.

---

## 4. Visual Character & Anti-Patterns

### Desired Visual Attributes
- **Restrained & Neutral:** Backgrounds built on neutral slate (`#f8fafc` light, `#09090b` dark).
- **High Whitespace:** Generous padding (`p-6`, `p-8`) to prevent cognitive clutter.
- **Typographic Authority:** Clean hierarchy using `Inter` with tabular numerals (`tabular-nums`) for medical statistics.
- **Subtle Borders:** Consistent 1px borders (`#e2e8f0` light, `#27272a` dark).

### Explicitly Prohibited Anti-Patterns
1. **No Glassmorphism / Heavy Blurs:** Blurring effects reduce text legibility in clinical settings.
2. **No Neumorphism:** Soft extruded shadows create muddy contrast and fail accessibility standards.
3. **No Decorative AI Tropes:** No sparkle stars (✨), robot avatars, or pulsing brain animations.
4. **No Marketing Dashboard Aesthetics:** No giant vanity KPI cards with trend arrows comparing arbitrary weekly percentages.
5. **No Cluttered Multi-Model Selectors:** No menus that let end-users toggle between deep learning and GAM models.
