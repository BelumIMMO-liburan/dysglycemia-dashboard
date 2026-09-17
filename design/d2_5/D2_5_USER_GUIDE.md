# Phase D2.5 — Clinical & Research User Guide
## Understanding the "Why this result?" Screening Explanation
**Target Audience:** Clinical investigators, study coordinators, research physicians  
**Governing Principle:** Non-causal model interpretability under research decision-support protocols

---

## 1. Purpose of the Explanation

When reviewing a Stage-1 non-laboratory screening result, the dashboard presents a dedicated **"Why this result?"** section.

The purpose of this section is to answer one question:
> **"Why did the frozen statistical model calculate this specific screening score for this participant?"**

It does **NOT** answer:
> *"What caused this individual to develop dysglycemia?"*

In medical research, statistical model features represent associative correlations identified in population data (NHANES 2021–2023). They do not represent direct biological etiology or lifestyle culpability.

---

## 2. How to Read the Display

### 2.1 The Baseline Score (Model Intercept $\beta_0$)
Every evaluation starts from the population baseline intercept ($\beta_0 = -0.7291$). If all features were at their standardized baseline values, the model's baseline log-odds would be $-0.7291$ (corresponding to a probability of approximately $32.5\%$).

### 2.2 Factor Cards & Directional Badges
Each predictor is shown with its measured value and a directional indicator:

- **Pushes screening score higher (+X.XXX):**
  - Indicated with an amber attention badge and warm accent bar.
  - Indicates that the participant's value for this feature shifted the statistical model's log-odds score in the direction of higher dysglycemia risk relative to baseline.
  - *Example:* `Age (52 years)`: `+0.271` — older age contributed positively to the model's screening log-odds.

- **Pushes screening score lower (-X.XXX):**
  - Indicated with a neutral slate badge and cool muted bar.
  - Indicates that the participant's value shifted the model's log-odds score in the direction of lower dysglycemia risk relative to baseline.
  - *Example:* `Sedentary Time (480 min/day)`: `-0.473` — in the non-linear spline curve fitted by the GAM, 480 minutes/day falls within an associative range that lowered the link score.

### 2.3 Visual Relative Strength Bar
- The length of the horizontal bar shows the relative impact of that factor compared to the single largest factor observed in that screening session ($100\%$).
- This provides visual hierarchy to distinguish primary model drivers from minor contributors.
- **Important:** The bar width is relative strength on the link scale, not a percentage of the participant's disease risk.

---

## 3. Progressive Disclosure (`[ Show all 7 factors ]`)

To prevent cognitive overload during rapid review, the interface presents the **top 3 factors** by default (the three factors with the largest absolute link contribution $|c_i|$).

Clicking the `[ Show all 7 factors ]` button smoothly reveals the remaining 4 predictors. Clicking it again collapses them.

---

## 4. What This Explanation Does NOT Mean (Clinical Constraints)

1. **Not a Lifestyle Prescription:**
   - A negative contribution for sedentary time does not mean prolonged sitting is healthy.
   - A positive contribution for age does not mean aging causes diabetes.
   - Model explanations describe the mathematical mechanics of the algorithm, not clinical therapy.

2. **Not a Diagnostic Confirmation:**
   - High factor contributions do not confirm diabetes.
   - Low factor contributions do not rule out diabetes.
   - Stage-1 is a preliminary screening protocol designed solely to guide referral to Stage-2 laboratory testing (HbA1c).

3. **No Threshold Splitting:**
   - Factor contributions are defined relative to the model baseline ($\beta_0$), not the decision threshold ($0.1389$).
