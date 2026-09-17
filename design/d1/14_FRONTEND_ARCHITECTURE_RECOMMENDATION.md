# Frontend Architecture Recommendation & Technology Stack Decision

**Phase:** D1 — Design Foundation  
**Evaluation Target:** Implementation Strategy for Phase D2 Dashboard Redesign  
**Date:** 2026-09-04  

---

## 1. Executive Summary & Problem Framing

A central objective of Phase D1 is to establish an implementation architecture that achieves the high visual fidelity and component rigor of **`shadcn/ui`** without incurring unnecessary architectural complexity, framework churn, or deployment fragility.

We evaluate three candidate architectures against seven pre-defined academic and software engineering criteria:
- **Option A:** Django Templates + Bootstrap / Tabler Structural Primitives + Custom shadcn CSS Layer
- **Option B:** Django Server-Rendered Templates + Native shadcn-Inspired CSS Tokens & Primitives (Vanilla CSS + HTML5 `<dialog>` + Lightweight JS)
- **Option C:** Decoupled Architecture (Django REST Framework API Backend + React Frontend + Literal `shadcn/ui`)

---

## 2. Decision Criteria & Evaluation Matrix

Each option is scored from $1$ (Poor / High Risk) to $5$ (Exceptional / Ideal):

| Criterion | Evaluation Dimension | Option A: Django + Bootstrap | Option B: Django + Native shadcn CSS System | Option C: Django API + React (shadcn/ui) |
| :--- | :--- | :---: | :---: | :---: |
| **1. Preserves Existing Backend** | Reuses tested Django 5.2 models, views, routing, and Python ML loading. | **5** | **5** | **2** (Requires rewriting views as REST endpoints, serializing models, CORS, token auth). |
| **2. Implementation Simplicity** | Minimal tooling, zero unnecessary build steps, no multi-process dev servers. | **4** (Bootstrap introduces duplicate styling overrides). | **5** (Zero Node.js dependency, pure CSS variables, native browser primitives). | **2** (Vite/Next.js, Node.js runtime, npm package management, build pipeline). |
| **3. Maintainability** | Long-term code clarity for single undergraduate thesis author. | **3** (Fighting Bootstrap specificity wars against shadcn tokens). | **5** (Clean, self-contained CSS token file; modular Django template partials). | **3** (Managing two separate language ecosystems: Python 3.10 and Node/TypeScript). |
| **4. Research Reproducibility** | Ease with which examiners or future researchers can clone and run `manage.py runserver`. | **5** | **5** (100% reproducible via `pip install -r requirements.txt`). | **2** (Requires Node.js, npm install, matching versions, cross-origin configuration). |
| **5. Usability-Study Reliability** | Deterministic form submissions, zero client-side hydration crashes, rock-solid session state. | **4** | **5** (Server-rendered HTML is immune to client-side JS runtime crashes). | **4** (Single-page app state bugs can corrupt study timestamps). |
| **6. Visual Quality (Fidelity to shadcn)** | Ability to achieve clean, restrained, high-whitespace shadcn aesthetics. | **3** (Bootstrap components look like Bootstrap unless heavily skinned). | **5** (Exact translation of HSL color tokens, 4px grid, and typography). | **5** (Literal copy of React components). |
| **7. Development Time** | Delivery speed within undergraduate thesis schedule. | **4** | **5** (Direct drop-in refactor of existing templates). | **2** (Full frontend rebuild consumes 3–4 weeks of engineering time). |
| **TOTAL SCORE** | *(Out of 35)* | **28** | **35** | **20** |

---

## 3. In-Depth Architectural Analysis

### Option A: Django Templates + Bootstrap / Tabler
- **Strengths:** Rapid grid scaffolding; accessible dropdowns.
- **Fatal Weakness:** Bootstrap's opinionated CSS classes (e.g., `.btn`, `.card`, `.modal`) carry heavy default styles, borders, and shadows that directly clash with the minimalist aesthetic of `shadcn/ui`. Overriding Bootstrap to look like shadcn results in bloated CSS with hundreds of `!important` declarations.

### Option C: Decoupled Django REST API + React (`shadcn/ui`)
- **Strengths:** Literal adoption of the official `shadcn/ui` CLI components in TypeScript.
- **Fatal Weakness:** Completely unjustified architectural complexity for this project. The current repository does not have a React frontend, Node.js toolchain, or REST API layer. Migrating to React would require:
  1. Installing Node.js, npm, Vite, and TypeScript.
  2. Converting all Django views into Django REST Framework (DRF) serializers and viewsets.
  3. Configuring CORS headers, CSRF token handling, and JWT/session authentication.
  4. Managing state in React and building a duplicate data fetching layer.
  *Conclusion:* Choosing React solely because shadcn is React-native violates good software engineering principles.

### Option B: Django Server-Rendered Templates + Native shadcn-Inspired CSS Design System (Recommended)
- **Strengths:**
  1. **Zero External Build Pipeline:** Uses pure, modern CSS with HSL custom properties. Operates natively in any browser with zero compilation step.
  2. **100% Python/Django Native:** Seamlessly interfaces with existing Django forms, CSRF protection, URL reversers, template tags, and SQLite persistence.
  3. **Direct Integration with ML Artifacts:** The view layer directly invokes `joblib.load()` on the frozen Phase-5 GAM artifact, computes additive spline decompositions in $<1\text{ms}$, and passes clean context directly to the template.
  4. **Native Browser Accessibility:** Utilizes native HTML5 elements (`<dialog>` for the override modal, `<details>` for factor accordions, `<select>` for accessible dropdowns), providing rock-solid keyboard navigation with zero bundle weight.

---

## 4. Definitive Technology Stack Recommendation

We formally recommend **Option B: Enhanced Django Templates + Custom shadcn-Inspired CSS Design System**.

### The Chosen Stack
- **Backend:** Django 5.2.12 on Python 3.10.
- **Database:** SQLite 3 (`BASE_DIR / 'db.sqlite3'`).
- **Templating:** Django Template Language (DTL) using modular partials (`{% include 'predictor/components/card.html' %}`).
- **Styling:** Modular Vanilla CSS using exact `shadcn/ui` design tokens (`design_system.css`).
- **Interactive Primitives:** Native HTML5 `<dialog>` for modals, accessible native ARIA attributes, and lightweight vanilla JavaScript (`app.js`, $<300$ lines).
- **Visual Analytics:** Lightweight Chart.js v4.4.0 (CDN) configured with monochrome/neutral palette matching shadcn tokens.
- **Icons:** Inline accessible SVG icons (Lucide-style), replacing all legacy Unicode emojis.
