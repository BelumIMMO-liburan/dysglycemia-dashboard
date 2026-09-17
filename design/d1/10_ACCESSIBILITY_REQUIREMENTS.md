# Accessibility Requirements & User Study Instrumentation Readiness

**Phase:** D1 — Design Foundation  
**Standard:** Web Content Accessibility Guidelines (WCAG) 2.1 Level AA  
**Context:** Clinical Information Systems & Research Evaluation Prototype  
**Date:** 2026-09-04  

---

## 1. WCAG 2.1 AA Compliance Requirements

Medical and screening interfaces must remain fully usable and error-resistant across diverse physical, visual, and cognitive capabilities. The following mandatory requirements govern all components implemented in Phase D2:

### 1.1 Contrast & Color Representation (Criteria 1.4.1, 1.4.3)
- **Minimum Text Contrast:** Standard body text must achieve a contrast ratio of $\ge 4.5:1$ against its background. Large text ($\ge 18\text{pt}$ or bold $\ge 14\text{pt}$) must achieve $\ge 3.0:1$.
- **Non-Text UI Contrast:** Essential interface components (input borders, active tab outlines, focus indicators, icons) must achieve $\ge 3.0:1$ against adjacent backgrounds.
- **Never Color-Alone (Multi-Modal Status):** Clinical risk states must never be communicated purely by green, yellow, or red background tints. Every status state must combine:
  1. Semantic color tint
  2. Clear textual label (e.g., `"Elevated Screening Signal"`)
  3. SVG Icon with accessible title or `aria-hidden="true"` accompanied by screen-reader text.

### 1.2 Deterministic Keyboard Navigation & Focus Management (Criteria 2.1.1, 2.4.7)
- **Full Tab Order:** Every interactive control (inputs, selects, buttons, links, collapsible summaries, dialogs) must be reachable and operable using `Tab`, `Shift+Tab`, `Enter`, and `Space`.
- **Visible Focus Ring:** A prominent, unbroken focus indicator (`box-shadow: 0 0 0 2px var(--background), 0 0 0 4px var(--ring)`) must appear on interactive elements upon keyboard focus.
- **Modal Focus Trap (`<dialog>`):** When the Human Override confirmation modal is triggered:
  - Focus must immediately move to the modal's primary interactive control or title.
  - Tabbing must cycle strictly within the modal container.
  - Pressing `Escape` must close the modal without submitting changes and return focus to the triggering button.

### 1.3 Semantic Forms & Error Associations (Criteria 1.3.1, 3.3.1, 3.3.2)
- **Explicit Label Associations:** Every input must have an explicit `<label for="field_id">`.
- **Field-Tied Validation:** Error messages must be programmatic siblings to the invalid input, using `aria-invalid="true"` and `aria-describedby="error_field_id"`.
- **Contextual Units:** Units of measurement (`kg/m²`, `cm`, `min/day`) must be included in the accessible input description so screen reader users hear: `"Body Mass Index, required, kilograms per square meter"`.

### 1.4 Touch Target Size & Spatial Density (Criterion 2.5.5)
- **Minimum Target Dimension:** All interactive controls (buttons, select triggers, table action links) must have an active hit area of at least $44 \times 44\text{px}$ on tablet and touch interfaces.
- **Spacing Buffers:** Form rows maintain a minimum $12\text{px}$ vertical buffer to prevent accidental double taps during rapid clinical entry.

### 1.5 Motion Sensitivity & Cognitive Load (Criterion 2.3.3)
- **Reduced Motion Support:** Respect system-level accessibility settings via CSS:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
  ```

---

## 2. Accessibility Checklist for Phase D2 Implementation

| Component | Accessibility Implementation Technique | Verification Criteria |
| :--- | :--- | :--- |
| **New Screening Form** | Native `<label>`, `<input>`, `required`, `aria-describedby`. | Screen reader reads label + units + validation error without visual cues. |
| **Probability Meter** | `<div role="meter" aria-valuenow="24.7" aria-valuemin="0" aria-valuemax="100" aria-label="Screening probability 24.7%, threshold 13.9%">`. | Accessible to assistive tech; threshold position clearly stated in label. |
| **Factor Explanation** | Native `<details>` and `<summary>` or ARIA accordion (`aria-expanded="false"`, `aria-controls="panel-id"`). | Can be expanded/collapsed entirely via keyboard `Space`/`Enter`. |
| **Override Dialog** | HTML5 `<dialog>` element with `.showModal()`. | Traps keyboard focus; prevents interaction with underlying page; closes on `Escape`. |
| **Review Queue Table** | Semantic `<table>`, `<thead>`, `<th scope="col">`, `<tbody>`. | Column headers announce correctly when traversing cells via screen reader. |

---

## 3. Future Usability Study Readiness & Telemetry Hooks

To evaluate the prototype in a formal undergraduate usability study (e.g., System Usability Scale [SUS] and Task-Load Index [NASA-TLX]), the front-end architecture must be designed to support precise telemetry event logging without modifying clinical workflows.

### Structured Telemetry Schema (Pre-wired Data Hooks)
The following data attributes (`data-telemetry-event`) will be embedded in DOM elements during D2 implementation to allow seamless future integration with study loggers:

```html
<!-- Example: Form Submission Telemetry Hook -->
<form method="POST" data-telemetry-action="screening_submission" data-telemetry-case-id="{{ case_id }}">
  ...
  <button type="submit" data-telemetry-event="screen_submitted">Run Screening</button>
</form>
```

### Pre-Defined Loggable Study Events
1. `screen_started`: Timestamp when user focuses the first input on the New Screening form.
2. `screen_submitted`: Timestamp when valid form is submitted. (Calculates *Time-on-Task for Intake*).
3. `result_viewed`: Timestamp when screening result surface renders.
4. `explanation_opened`: Timestamp when user expands the GAM factor detail or spline curves. (Measures *Clinician Engagement with XAI*).
5. `review_started`: Timestamp when user navigates to a case from the Review Queue.
6. `recommendation_accepted`: Timestamp when user clicks `[ Accept Recommendation ]`.
7. `override_started`: Timestamp when user clicks `[ Override Recommendation ]` (triggers modal).
8. `override_reason_selected`: The specific categorical reason selected from dropdown.
9. `override_confirmed`: Timestamp when override form is validated and submitted. (Calculates *Deliberation Time on Override*).
10. `stage2_entered`: Timestamp when confirmatory HbA1c value is recorded.

*Note: Telemetry hooks in D1/D2 will remain purely passive data attributes in the markup, introducing zero external tracker dependencies or third-party analytics scripts.*
