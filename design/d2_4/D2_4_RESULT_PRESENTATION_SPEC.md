# Phase D2.4 Result Presentation Specification: Evidence-First Clinical UI Design

**Phase:** D2.4  
**Status:** Frozen & Approved  
**Governing Skill:** `research-governance`  
**Supporting Skills:** `dashboard-design`, `frontend-quality`  

---

## 1. Design Philosophy: Evidence-First Guided Review

The Dysglycemia Screening Dashboard adheres to the Evidence-First philosophy. The Stage-1 Screening Result presents AI recommendations as assistive decision-support signals rather than automated clinical decrees.

### Guiding Principles:
1. **Calm Attention, Not Alarmism:** High-risk outputs must alert the user without inducing panic.
2. **Restrained Lower Signals:** Lower risk outputs must never guarantee normality or claim disease absence.
3. **No Misleading Progress Bars:** Probability is displayed as an unembellished tabular numeral rather than a colored 0–100% progress meter that might be misinterpreted as diagnostic certainty.
4. **Permanent Disclaimers:** Research prototype disclaimers remain visible across all states.

---

## 2. Visual State Specifications

### State A: Elevated Screening Signal ($\hat{p} \ge 0.1389$)

* **Status Badge:**
  - Token Family: Amber / Attention (`ui-badge-warning`)
  - Icon: Warning triangle (`alert-triangle` SVG)
  - Text Label: `"Elevated screening signal"`
  - Prohibited Styling: Destructive red, siren icons, pulsing animations.
* **Screening Probability:**
  - Typography: Large tabular bold numeral (`font-variant-numeric: tabular-nums`, font size `2.75rem`).
  - Label: `"Screening probability"`
  - Subtitle: `"Calculated non-laboratory probability"`
* **AI Recommendation:**
  - Phrasing: `"Referral for Stage-2 HbA1c assessment is recommended."`
  - Footnote: `"This screening result is not a diagnosis."`
* **Clinical Interpretation:**
  - Phrasing: `"The model identified a screening signal above the pre-specified research operating point. Stage-2 HbA1c assessment is recommended for further laboratory evaluation."`

---

### State B: Lower Screening Signal ($\hat{p} < 0.1389$)

* **Status Badge:**
  - Token Family: Neutral / Secondary (`ui-badge-secondary` on muted surface)
  - Icon: Info circle (`info` SVG)
  - Text Label: `"Lower screening signal"`
  - Prohibited Styling: Vibrant green checkboxes that imply total health or disease absence.
* **Screening Probability:**
  - Typography: Large tabular bold numeral (`font-variant-numeric: tabular-nums`, font size `2.75rem`).
  - Label: `"Screening probability"`
* **AI Recommendation:**
  - Phrasing: `"The screening model does not recommend referral for Stage-2 HbA1c assessment at the current research operating point."`
* **Clinical Interpretation (Crucial Restraint):**
  - Phrasing: `"The model did not identify a screening signal above the pre-specified research operating point. A lower screening signal does not rule out dysglycemia. This result reflects the screening model's recommendation at the pre-specified research operating point."`

---

## 3. Prohibited Visual Language

The following phrases, visual cues, and patterns are strictly forbidden:

| Prohibited Element | Why Forbidden | Approved Alternative |
| :--- | :--- | :--- |
| **"Normal" / "Healthy"** | Model is a non-laboratory screen; it cannot confirm normal glycemic control. | *"Lower screening signal"* |
| **"Negative for diabetes"** | Implies diagnostic certainty. | *"Does not recommend referral at the current research operating point."* |
| **"Disease absent" / "Safe"** | False reassurance; miss rate exists. | *"A lower screening signal does not rule out dysglycemia."* |
| **"Diabetes Probability: XX%"** | Model predicts HbA1c-defined dysglycemia risk, not definitive diabetes. | *"Screening probability"* |
| **Destructive Red Alert Banner** | Induces unnecessary clinical panic for a non-acute screening triage. | Restrained amber attention badge (`ui-badge-warning`). |
| **0–100% Progress Bar Meter** | Conveys certainty or disease severity rather than statistical probability. | Restrained tabular numerical callout. |
| **Headline Decision Threshold** | Overwhelms the primary clinical signal with technical details. | Internal provenance storage; visible only in collapsed research details. |

---

## 4. Collapsible Disclosures Architecture

To keep the primary result card focused while preserving complete transparency:
1. **Screening Inputs (`#screening-inputs-disclosure`):**
   - HTML `<details>` element with accessible summary.
   - Displays all 7 intake parameters in a clean grid with units (e.g., `52 years`, `Male`, `28.4 kg/m²`, `98.5 cm`, `Yes`, `No`, `480 min/day (8.0 hours/day)`).
2. **Research & Provenance Details (`#research-details-disclosure`):**
   - Displays record UUID, execution timestamp (UTC), model architecture (`Phase-5 GAM`), frozen decision threshold (`0.1389`), and SHA-256 hashes for `gam_final.pkl` and `preprocessor.pkl`.
   - Explanatory note confirming that AI screening outputs are immutable.

---

## 5. Result Navigation Actions

The page provides two clear actions:
1. **`[ Start New Screening ]` (`#start-new-screening-btn`):** Primary action button linking to `predictor:new_screening`.
2. **`[ Return to Overview ]` (`#return-overview-btn`):** Secondary outline button linking to `predictor:overview`.

**Scope Rule:** No functional *Override*, *Accept AI*, *Explain Result*, or *Order HbA1c* buttons are presented in Phase D2.4.
