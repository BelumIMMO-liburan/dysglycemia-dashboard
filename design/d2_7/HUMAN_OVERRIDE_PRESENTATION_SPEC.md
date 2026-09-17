# Human Override Presentation Specification: UI/UX & Interaction Design

**Document Version:** 1.0  
**Phase:** D2.7  
**Status:** Approved  
**Governing Skills:** `dashboard-design`, `frontend-quality`, `research-governance`  

---

## 1. UI Information Architecture & Flow

In accordance with the **Evidence-First Guided Review** philosophy, the interaction flow guarantees that evidence precedes action:

$$\text{Stage-1 Result Card} \longrightarrow \text{GAM-Native "Why this result?"} \longrightarrow \text{Human Review Card} \longrightarrow \text{Accessible Modal Dialog}$$

The Human Review card sits directly below the additive factor decomposition. The user is presented with two explicit choices:
1. **Accept Recommendation:** Submits immediate decision concordance.
2. **Override Recommendation:** Opens a focused, accessible modal dialog to document decision disagreement and structured rationale.

---

## 2. Component Layout & Visual Specifications

### 2.1 Action Buttons (Pending State)
- **Container:** Flex container at bottom of `#human-review-card-pending`.
- **Accept Button:**
  - Element ID: `#accept-recommendation-btn`
  - Style: High-contrast primary button (`ui-btn ui-btn-primary`, dark slate / primary background).
  - Icon: Checkmark.
  - Label: `"Accept Recommendation"`
- **Override Button:**
  - Element ID: `#open-override-btn`
  - Style: Secondary outline button (`ui-btn ui-btn-outline`, border with subtle hover background).
  - Icon: Shuffle / Reversal arrows.
  - Label: `"Override Recommendation"`
  - **Prohibition:** Must **NOT** be styled with destructive red (`ui-btn-destructive`), as override is an authorized governance action, not a destructive deletion.

---

### 2.2 Accessible Override Modal Dialog (`#override-modal-backdrop`)

- **Modal Backdrop:** `position: fixed; inset: 0; background: rgba(0,0,0,0.55); backdrop-filter: blur(4px); z-index: 1000;`
- **Dialog Container (`#override-dialog-container`):**
  - Card surface: `max-width: 580px; width: 100%; max-height: 92vh; border-radius: var(--radius); padding: 1.5rem; background: hsl(var(--card)); color: hsl(var(--card-foreground));`
  - Accessibility attributes: `role="dialog"`, `aria-modal="true"`, `aria-labelledby="override-dialog-title"`, `aria-describedby="override-dialog-desc"`.
- **Header:**
  - Title (`#override-dialog-title`): `"Override Recommendation"`
  - Subtitle (`#override-dialog-desc`): `"Record an auditable review decision that differs from the AI referral recommendation."`
  - Close button (`#close-override-x-btn`): Top-right dismiss icon (`aria-label="Close override dialog"`).
- **Comparison Summary Grid (`#override-comparison-grid`):**
  - **Original AI Recommendation (`#dialog-original-rec`):** Displays `"Refer for Stage-2 HbA1c"` or `"No Referral Recommended"`.
  - **Your Final Decision (`#dialog-final-decision`):** Prominently displays the opposite derived action (`"Do not refer at this time"` or `"Refer for Stage-2 HbA1c assessment"`).
- **Reason Fieldset (`#override-reason-fieldset`):**
  - Semantic `<fieldset>` with `<legend>Reason for override *</legend>`.
  - Radio options rendered dynamically based on active recommendation branch.
- **Additional Context Note:**
  - Textarea (`#override-note-input`): 3 rows, `maxlength="500"`.
  - Live character counter (`#override-note-counter`): Displays `X / 500 chars`.
  - Helper text (`#override-note-help`): `"Optional context. Do not enter names or other identifying information. Required if selecting 'Other reason'."`
- **Reviewer Code:**
  - Input (`#override-reviewer-code-input`): Monospace, `maxlength="32"`, required.
  - Helper text (`#override-reviewer-code-help`): `"Use the reviewer code assigned for this study. Do not enter your name or other identifying information."`
- **Dialog Action Buttons:**
  - Cancel (`#cancel-override-btn`): `"Cancel"` (`ui-btn ui-btn-outline`).
  - Confirm (`#confirm-override-btn`): `"Confirm Override"` (`ui-btn ui-btn-primary`).

---

### 2.3 Completed / Overridden Result State

Rendered in `#human-review-card-finalized` when `review_action == 'overridden'`:
- **Status Badge (`#review-status-badge`):**
  - Styling: Restrained attention styling (`ui-badge`, muted background, border, font-weight 600; never alarmist red).
  - Icon: Reversal / exchange icon.
  - Copy: `"Recommendation Overridden"`
- **Grid Layout:**
  1. `Original AI Recommendation`: Displays initial AI output.
  2. `Final Human Decision`: Displays final decision text with `(Overridden)` indicator.
  3. `Override Reason` (`#override-reason-display`): Full text of the selected reason.
  4. `Additional Context Note` (`#override-note-display`): Italicized quote block (if note present).
  5. `Reviewer Code`: Monospace pseudonymized code.
  6. `Reviewed Timestamp`: Formatted date/time with UTC suffix.
- **Audit Callout (`#review-immutable-notice`):**
  > *"Research Audit Guarantee: Human override records an explicit reviewer decision differing from the AI referral recommendation along with structured rationale. It does not alter the underlying model probability or establish biological truth. Original AI model output remains permanently recorded and immutable."*

---

## 3. Prohibited Language & Anti-Patterns

| Prohibited UI Phrasing | Approved Research Phrasing | Rationale |
| :--- | :--- | :--- |
| "AI wrong" / "Model error" | "Recommendation Overridden" | Override reflects decision disagreement, not verified ground truth error. |
| "Corrected diagnosis" | "Final Human Decision: Do not refer / Refer" | Stage-1 screening evaluates referral, not clinical disease diagnosis. |
| "Clinical Note" / "Doctor's Chart" | "Additional Context Note" | Prevents conflating research rationale with EHR medical records. |
| "Save" / "Submit" | "Confirm Override" | Explicit confirmation prevents accidental or ambiguous action. |
| "Re-infer" / "Update Model" | *(Action prohibited)* | The frozen model and threshold are immutable. |
