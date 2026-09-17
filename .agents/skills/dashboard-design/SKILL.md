---
name: dashboard-design
description: >-
  Guides all dashboard UI/UX implementation using the approved Evidence-First
  Guided Review philosophy and shadcn/ui visual reference. Encodes the approved
  information architecture, primary user flow, prohibited UI patterns, and
  design token strategy. Activate when building templates, styling components,
  designing layouts, or making any visual/interaction decision.
---

# Dashboard Design — Evidence-First Guided Review

This skill encodes the approved design specification from Phase D1
(`design/d1/DASHBOARD_DESIGN_SPEC_V1.md`). All UI implementation must
conform to these rules.

--------------------------------------------------------------------------------

## 1. Design Philosophy: Evidence-First Guided Review

The core interaction model:

```
SYSTEM SCREENS → SYSTEM EXPLAINS → HUMAN REVIEWS → HUMAN DECIDES ACTION
```

The algorithm does NOT diagnose the patient. The algorithm screens and
recommends referral; the clinician reviews, interprets, and decides clinical
action.

### Ten Core Principles

1. **Screening, Not Diagnosis** — Calm triage replacing diagnostic claims
2. **Human Authority Remains Explicit** — Machine recommends; human decides
3. **Explanation Precedes Override** — Inspect factors before taking action
4. **Progressive Disclosure** — Essential summary first; details on demand
5. **Low Cognitive Load** — Scannable in <5 seconds during consultation
6. **Uncertainty Visible but Non-Alarmist** — Percentage + threshold line; zero flashing
7. **Multi-Modal State** — Every status uses text + icon + color (never color alone)
8. **Research Limitations Visible** — Explicit NHANES origin and study limitations
9. **Model Complexity Hidden** — No model selectors or hyperparameter dials
10. **Immutable Auditability** — Every input, inference, and decision is recorded

--------------------------------------------------------------------------------

## 2. Primary Visual Reference: shadcn/ui

Translate shadcn/ui's visual character into Django templates:

- **Neutral surfaces** — Slate/stone backgrounds, clean white cards
- **Strong hierarchy** — Clear typographic scale (Inter font, tabular numerics)
- **Restrained borders** — Crisp 1px borders, not heavy shadows or blur
- **Moderate radius** — 6–8px (0.375–0.5rem) border radius
- **High whitespace** — Generous padding (p-6, p-8) reducing cognitive clutter
- **Clear focus states** — Visible 2px focus ring on all interactive elements
- **Calm status presentation** — Muted semantic badges, not neon alerts
- **Minimal decorative styling** — Professional density, not marketing flash

**IMPORTANT:** Do NOT automatically migrate to React just to use shadcn.
The approved stack is Django Templates + Native shadcn-Inspired CSS.

--------------------------------------------------------------------------------

## 3. Primary User Flow

```
Stage-1 Non-Lab Intake (/screening/new/)
    7 predictors entered
        ↓
Screening Result (/screening/<id>/)
    Elevated vs Non-Elevated signal
    Screening probability vs frozen threshold (0.1389)
        ↓
Explanation (GAM-native term decomposition)
    Factors Elevating vs Factors Moderating
        ↓
Human Guided Review (/review/<id>/)
    Accept Recommendation vs Override Recommendation
        ↓
Override Dialog (if overriding)
    Structured reason + clinical notes + confirmation
        ↓
Stage-2 HbA1c Intake (/screening/<id>/stage2/)
    Laboratory result → Clinical range categorization
        ↓
Audit History (/history/<id>/)
    3-part immutable record (Intake + Review + Lab)
```

--------------------------------------------------------------------------------

## 4. Information Architecture

### Sidebar Navigation Structure

```
SCREENING
  • New Screening
  • Review Queue [count badge]
  • History

RESEARCH & GOVERNANCE
  • Analytics
  • About the Model
```

### Route Mapping

| Route | Purpose |
|:---|:---|
| `/` | Overview / entry point |
| `/screening/new/` | Stage-1 intake form |
| `/screening/<id>/` | Result + explanation + review |
| `/review/` | Pending review queue |
| `/review/<id>/` | Focused review workspace |
| `/screening/<id>/stage2/` | Stage-2 lab entry |
| `/history/` | Searchable audit history |
| `/history/<id>/` | Case detail (3-part audit) |
| `/analytics/` | Research surveillance metrics |
| `/about/` | Methodology & limitations |

--------------------------------------------------------------------------------

## 5. Prohibited UI Patterns

The following are STRICTLY PROHIBITED in any implementation:

- [ ] Model selector dropdown (GAM / DLNN / Logistic)
- [ ] Threshold slider or threshold input control
- [ ] DLNN/GAM switch or model toggle
- [ ] Multi-model consensus badges
- [ ] Giant alarmist risk cards with siren emojis (🚨)
- [ ] Finance-dashboard styling (vanity KPI cards with trend arrows)
- [ ] AI sparkle aesthetics (✨, robot icons, pulsing brains)
- [ ] Decorative medical graphics (EKG heartbeat lines)
- [ ] Glassmorphism / heavy backdrop blur
- [ ] Neumorphism / soft extruded shadows
- [ ] Large saturated neon gradients
- [ ] Marketing landing page hero sections
- [ ] Diagnostic language ("You have diabetes", "Diabetic")

--------------------------------------------------------------------------------

## 6. Component Reference Strategy

| Interface Element | shadcn Reference | Django Strategy |
|:---|:---|:---|
| Sidebar | Sidebar | Server-rendered `<aside>` with route-aware active states |
| Cards | Card | Semantic `<div class="ui-card">` with 1px border |
| Inputs | Input | `<input class="ui-input">` with unit badges |
| Selects | Select | Native `<select class="ui-select">` |
| Buttons | Button | Variant classes: `.ui-btn-primary`, `.ui-btn-outline` |
| Badges | Badge | `<span class="ui-badge ui-badge-amber">` |
| Dialogs | AlertDialog | HTML5 `<dialog>` with `.showModal()` |
| Accordions | Accordion | Native `<details>/<summary>` |
| Tables | DataTable | Semantic `<table class="ui-table">` |
| Tooltips | Tooltip | CSS tooltips with `data-tooltip` |

--------------------------------------------------------------------------------

## 7. Design Token Direction

Default direction: **"Clinical Neutral"** (Direction A)

- Primary: Cool blue (`hsl(221, 83%, 53%)`)
- Background: Soft slate-white (`hsl(210, 40%, 98%)`)
- Card: Pure white (`hsl(0, 0%, 100%)`)
- Border: Crisp slate (`hsl(214, 32%, 91%)`)
- Success: Muted emerald
- Warning: Amber
- Destructive: Restrained red
- Radius: 0.5rem (8px)
- Font: Inter with tabular numerics

Dark mode supported via `[data-theme="dark"]` CSS custom property overrides.

--------------------------------------------------------------------------------

## 8. Reference Documents

Full specifications are in `design/d1/`:
- `DASHBOARD_DESIGN_SPEC_V1.md` — Master specification
- `08_TEXTUAL_WIREFRAMES.md` — ASCII wireframes for all 12 screens
- `09_DESIGN_TOKENS.md` — Complete HSL token definitions
- `04_SHADCN_COMPONENT_MAPPING.md` — Component translation guide
