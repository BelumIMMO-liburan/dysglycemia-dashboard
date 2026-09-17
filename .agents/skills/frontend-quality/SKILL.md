---
name: frontend-quality
description: >-
  Guides frontend implementation quality including accessibility (WCAG 2.1 AA),
  responsive design, component reusability, and visual QA standards. Activate
  when writing CSS, HTML templates, JavaScript, or reviewing frontend output
  for quality and standards compliance.
---

# Frontend Quality — Implementation Standards & Visual QA

This skill enforces implementation quality standards for the dashboard frontend.
It covers accessibility, responsive design, code hygiene, and visual character.

--------------------------------------------------------------------------------

## 1. Accessibility (WCAG 2.1 Level AA)

### Mandatory Requirements

- **Semantic HTML:** Use proper elements (`<nav>`, `<main>`, `<aside>`,
  `<header>`, `<section>`, `<form>`, `<label>`, `<table>`, `<thead>`, `<th>`).
  Do not use `<div>` for everything.

- **Explicit Labels:** Every `<input>`, `<select>`, and `<textarea>` must have
  an associated `<label for="field_id">`. No placeholder-only labels.

- **Keyboard Navigation:** Every interactive control must be reachable and
  operable via `Tab`, `Shift+Tab`, `Enter`, and `Space`. Test this.

- **Visible Focus Ring:** All focusable elements must show a prominent,
  unbroken focus indicator:
  ```css
  :focus-visible {
    outline: 2px solid hsl(var(--ring));
    outline-offset: 2px;
  }
  ```

- **No Color-Only States:** Every status indicator must combine:
  1. Semantic color tint
  2. Explicit text label
  3. Distinct SVG icon
  Never rely solely on green/yellow/red to communicate meaning.

- **Accessible Dialogs:** Override confirmation modals must use HTML5 `<dialog>`
  with `.showModal()`. This provides native focus trapping, backdrop dimming,
  and `Escape` key closing. Do not build custom modal divs with z-index hacks.

- **Sufficient Contrast:** Text contrast ratio ≥ 4.5:1 for normal text,
  ≥ 3.0:1 for large text and UI components. Test in both light and dark themes.

- **Field-Tied Validation:** Error messages must be adjacent to the invalid
  input and linked via `aria-describedby`. Use `aria-invalid="true"` on
  invalid fields.

- **Touch Targets:** Minimum 44×44px active hit area on all buttons, links,
  and interactive controls.

- **Reduced Motion:**
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```

- **Table Semantics:** Use `<th scope="col">` for column headers and
  `<th scope="row">` for row headers. Screen readers must correctly announce
  column context when traversing cells.

- **Screen-Reader Button Labels:** Buttons with only icons must have
  `aria-label="descriptive action name"`.

--------------------------------------------------------------------------------

## 2. Responsive Design

### Target Breakpoints

| Tier | Width Range | Priority | Sidebar Behavior |
|:---|:---|:---|:---|
| Desktop | ≥ 1280px | **Primary** (research workflow) | Persistent left sidebar |
| Tablet | 768px – 1279px | Usable | Collapsible sidebar (Sheet/Drawer) |
| Mobile | < 768px | Functional but secondary | Hidden sidebar, hamburger toggle |

### Responsive Rules

- Form fields stack vertically on screens < 768px
- Data tables use horizontal scroll containers, not layout-breaking wrap
- Touch targets maintain 44×44px on all breakpoints
- Sidebar collapses to slide-over drawer below 1024px
- Cards use `max-width` constraints to maintain readable line lengths
- Images and charts scale proportionally within card containers

--------------------------------------------------------------------------------

## 3. Code Quality & Architecture

### Template Hygiene

- **Reusable Components:** Extract repeated UI patterns into Django template
  partials (`{% include 'predictor/components/card.html' %}`).
- **Centralized Design Tokens:** All colors, spacing, radius, and typography
  values live in CSS custom properties. No hardcoded hex colors in templates.
- **No Arbitrary CSS Duplication:** If two elements need the same style,
  extract a utility class or component class.
- **No Giant Monolithic Templates:** Break templates exceeding 200 lines into
  logical `{% include %}` partials.
- **No Dead Code:** Remove unused CSS classes, commented-out HTML blocks, and
  orphaned JavaScript functions.

### JavaScript Standards

- **No unnecessary JS framework:** The approved stack uses vanilla JavaScript
  and native browser APIs. Do not introduce React, Vue, Alpine, or jQuery
  unless explicitly justified.
- **No framework mixing:** If a lightweight library is adopted (e.g., Alpine.js
  for specific reactive patterns), do not simultaneously use a competing
  approach for the same problem.
- **Progressive Enhancement:** Core form submission and navigation must work
  without JavaScript. JS enhances the experience (e.g., live validation,
  smooth transitions) but must not be required for basic operation.

### CSS Standards

- **CSS Custom Properties:** All theming via `--variable-name` declarations.
- **HSL Color Format:** `hsl(var(--primary))` for consistent token usage.
- **Logical Properties:** Prefer `margin-inline`, `padding-block` where
  appropriate for future RTL support.
- **No `!important`:** Except for accessibility overrides (reduced-motion,
  forced-colors).

--------------------------------------------------------------------------------

## 4. Visual QA — The Application Must Feel:

### Target Character
- **Calm** — Low visual noise, generous whitespace, no alarm fatigue
- **Precise** — Clean alignment, tabular numerics, consistent spacing grid
- **Modern** — Current web conventions, not dated admin template aesthetics
- **Research-Oriented** — Academic credibility, transparent methodology
- **Professional** — Ready for institutional evaluation and thesis defense

### Explicitly NOT:
- Generic admin template (Bootstrap default, Material Dashboard)
- Finance SaaS dashboard (giant KPI cards with sparklines)
- Hospital ERP system (cluttered enterprise forms)
- AI marketing product (sparkle icons, gradient hero, chatbot bubbles)
- Consumer health app (gamification, streaks, achievements)

### Visual Verification Checklist

Before marking any view as complete, verify:

- [ ] Typography hierarchy is clear (page title > section > card > body > helper)
- [ ] Spacing follows 4px grid consistently
- [ ] Status badges use text + icon + color (never color alone)
- [ ] Cards have consistent 1px borders (not heavy shadows)
- [ ] Primary action is visually prominent; secondary actions are subdued
- [ ] No orphaned emojis — use SVG icons exclusively
- [ ] Tabular data uses `font-variant-numeric: tabular-nums`
- [ ] Empty states display helpful guidance (not blank white space)
- [ ] Loading states show skeleton placeholders (not spinners)
- [ ] Light and dark themes both pass contrast checks
- [ ] No horizontal overflow on any breakpoint
- [ ] Disclaimer text is present on screening result surfaces

--------------------------------------------------------------------------------

## 5. No Fake Placeholder Metrics

When building analytics or dashboard views:

- Do NOT hardcode fake numbers (e.g., "1,234 Screenings" when the database
  is empty).
- Display honest counts from the database.
- Show appropriate empty states: "No screenings recorded yet. Start your
  first screening."
- If a metric requires data that does not yet exist, show a clear
  "Awaiting data" indicator rather than zero.
