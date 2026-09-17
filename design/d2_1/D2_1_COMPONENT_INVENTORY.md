# Phase D2.1 Component Inventory & Design Token Catalog

**Phase:** D2.1 — Application Shell & Design System Foundation  
**Reference Design System:** `shadcn/ui` CSS Custom Properties & Component Primitives  
**Date:** 2026-09-04  

---

## 1. Design Token Groups

### 1.1 Color Tokens (Direction A: Clinical Neutral)
| CSS Variable | HSL Value | Hex Equivalent | Semantic Purpose |
| :--- | :--- | :--- | :--- |
| `--background` | `210 40% 98%` | `#f8fafc` | Application canvas surface |
| `--foreground` | `222 47% 11%` | `#0f172a` | Primary text and headings |
| `--card` | `0 0% 100%` | `#ffffff` | Elevated card and container background |
| `--card-foreground` | `222 47% 11%` | `#0f172a` | Card text and title color |
| `--primary` | `221 83% 53%` | `#2563eb` | Primary brand accent and dominant actions |
| `--primary-foreground` | `210 40% 98%` | `#f8fafc` | Text on primary buttons |
| `--secondary` | `210 40% 96%` | `#f1f5f9` | Subtle background for hover states & secondary buttons |
| `--secondary-foreground` | `222 47% 11%` | `#0f172a` | Text on secondary elements |
| `--muted` | `210 40% 96%` | `#f1f5f9` | Muted element background |
| `--muted-foreground` | `215 16% 47%` | `#64748b` | Secondary captions, unit labels, and hints |
| `--accent` | `210 40% 93%` | `#e2e8f0` | Highlight background for active selections |
| `--border` | `214 32% 91%` | `#e2e8f0` | Crisp 1px borders replacing heavy shadows |
| `--input` | `214 32% 91%` | `#e2e8f0` | Form control borders |
| `--ring` | `221 83% 53%` | `#2563eb` | Accessible focus ring indicator |
| `--warning` | `38 92% 50%` | `#d97706` | Elevated screening signal and queue alerts |
| `--warning-muted` | `48 96% 96%` | `#fefce8` | Light amber background tint for elevated badges |
| `--success` | `142 71% 45%` | `#16a34a` | Confirmed referrals and normal lab results |
| `--success-muted` | `142 76% 96%` | `#f0fdf4` | Light green background tint for confirmed badges |
| `--destructive` | `0 72% 51%` | `#dc2626` | True destructive actions and critical alerts |
| `--destructive-muted` | `0 86% 97%` | `#fef2f2` | Light red background tint |

---

## 2. Structural Primitives

### 2.1 Application Shell (`.ui-app-layout`)
- **Desktop Grid:** Permanent left sidebar (`width: 260px`, fixed) + main workspace (`margin-left: 260px`, `flex: 1`).
- **Topbar (`.ui-topbar`):** Sticky header (`height: 56px`, `border-bottom: 1px solid var(--border)`).
- **Container (`.ui-container`):** Max width `1200px` with auto centering.
- **Footer (`.ui-footer`):** Bottom landmark displaying protocol version and threshold notice.

### 2.2 Navigation (`.ui-sidebar-nav` & `.ui-mobile-sheet`)
- **Nav Link (`.ui-nav-link`):** Interactive flex item with SVG icon, label, and hover transition.
- **Active State (`.ui-nav-link.active`, `[aria-current="page"]`):** Highlighted background with 3px primary vertical indicator bar.
- **Mobile Drawer (`.ui-mobile-sheet`):** Accessible off-canvas sheet (`width: 280px`, `max-width: 85vw`), triggered by hamburger button, dismissed via ESC or close button.

---

## 3. UI Component Primitives

| Component Name | Primary CSS Selector | Attributes / Modifiers | Description & Interaction Behavior |
| :--- | :--- | :--- | :--- |
| **Card** | `.ui-card` | `.ui-card-header`, `.ui-card-title`, `.ui-card-description`, `.ui-card-content`, `.ui-card-footer` | Clean, 1px bordered white surface grouping semantic content blocks. |
| **Primary Button** | `.ui-btn .ui-btn-primary` | `.ui-btn-sm`, `.ui-btn-lg`, `:disabled` | Single dominant page action (e.g. `[ Run Stage-1 Screening ]`). |
| **Secondary Button** | `.ui-btn .ui-btn-secondary` | `.ui-btn-sm`, `.ui-btn-lg` | Supporting actions on light background. |
| **Outline Button** | `.ui-btn .ui-btn-outline` | `.ui-btn-sm`, `.ui-btn-lg` | Bordered button for secondary choices (`[ Clear Form ]`, `[ Override ]`). |
| **Ghost Button** | `.ui-btn .ui-btn-ghost` | `.ui-btn-sm` | Transparent navigation triggers. |
| **Destructive Button** | `.ui-btn .ui-btn-destructive`| `:disabled` | Reserved strictly for permanent deletions or high-risk administrative operations. |
| **Status Badge** | `.ui-badge` | `.ui-badge-amber`, `.ui-badge-slate`, `.ui-badge-emerald`, `.ui-badge-destructive`, `.ui-badge-outline` | Compact pill combining SVG icon + label + semantic background tint. |
| **Alert Callout** | `.ui-alert` | `.ui-alert-info`, `.ui-alert-warning`, `.ui-alert-success`, `.ui-alert-destructive` | Non-alarmist callout with icon, title, and descriptive body text. |
| **Text/Number Input**| `.ui-input` | `type="number"`, `.tabular-nums`, `:focus` | 38px height input with subtle border and focus ring. |
| **Input Unit Group** | `.ui-input-group` | `.ui-input-unit` | Embeds unit badges (`kg/m²`, `cm`, `years`, `min/day`) inside right padding. |
| **Select Dropdown** | `.ui-select` | `:focus` | Native select styled with custom SVG chevron background. |
| **Radio Group** | `.ui-radio-group` | `.ui-radio-label`, `input[type="radio"]` | Accessible radio button set with custom brand accent color. |
| **Data Table** | `.ui-table-container` | `.ui-table`, `th`, `td`, `tbody tr:hover` | High-density audit table with uppercase headers and row hover highlights. |
| **Dialog Modal** | `.ui-dialog` | `<dialog>`, `::backdrop`, `.ui-dialog-header`, `.ui-dialog-footer` | Native HTML5 modal with focus trap, backdrop blur, and ESC listener. |
| **Probability Meter**| `.ui-meter-container`| `.ui-meter-track`, `.ui-meter-fill`, `.ui-meter-threshold` | Quantitative bar showing calculated probability and 13.9% floor line. |
| **Metric Card** | `.ui-metric-card` | `.ui-metric-label`, `.ui-metric-value`, `.ui-metric-helper` | High-impact quantitative presentation block. |
| **Empty State** | `.ui-empty-state` | `.ui-empty-icon`, `.ui-empty-title`, `.ui-empty-description` | Restrained fallback for empty queues and zero-result filters. |
| **Skeleton Loader** | `.ui-skeleton` | Pulsing animation | Accessible loading placeholder. |
| **Skip Link** | `.ui-skip-link` | `:focus` | WCAG 2.1 AA keyboard skip navigation element. |
