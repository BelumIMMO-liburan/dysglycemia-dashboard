---
name: research-governance
description: >-
  Prevents dashboard implementation from violating the completed thesis methodology.
  Encodes the frozen GAM model specification, locked threshold, permitted language,
  and human override semantics. This skill has the HIGHEST precedence among all
  project skills. Activate whenever writing or modifying prediction logic, model
  loading, threshold application, clinical language, override semantics, or
  analytics metric definitions.
---

# Research Governance — Frozen Thesis Methodology Guard

This skill encodes the immutable research protocol established by the completed
Phase 4.2 / Phase 5 evaluation. Every implementation decision must comply with
these constraints. No generic skill, external template, or aesthetic preference
may override research governance.

--------------------------------------------------------------------------------

## 1. Primary Model Specification

- **Model Family:** Generalized Additive Model (GAM)
- **Configuration:** n_splines = 10, smoothing penalty λ = 10.0
- **Artifact Path:** `nhanes_feasibility_2021_2023/models_phase5/gam_final.pkl`
- **Preprocessor:** `nhanes_feasibility_2021_2023/models_phase5/preprocessor.pkl`
- **Training Data:** NHANES 2021–August 2023, EXPANDED_COMMON development split

## 2. Stage-1 Predictors (Exactly 7 Non-Laboratory Features)

1. `age` — continuous, years
2. `sex` — binary (Male / Female)
3. `bmi` — continuous, kg/m²
4. `hypertension_history` — binary (Yes / No)
5. `smoking_history` — binary (Yes / No, ≥100 lifetime cigarettes)
6. `waist_cm` — continuous, centimeters
7. `sedentary_minutes_day` — continuous, minutes per day

**Strictly Excluded from Stage-1 Intake:**
- HbA1c (laboratory biomarker — this IS the Stage-2 confirmatory outcome)
- Fasting glucose
- Heart disease
- Any other variable not in the list above

## 3. Frozen Operating Threshold

```
THRESHOLD = 0.1389
```

- Derived on development data to target ≥90% screening sensitivity.
- Development sensitivity achieved: 90.23%.
- This threshold MUST NOT be recalculated, adjusted, or exposed as a user control.
- It may appear in read-only methodology documentation (About the Model page).

## 4. Held-Out Final Test Performance (Read-Only Reference)

| Metric | Value | 95% Bootstrap CI |
|:---|:---|:---|
| Sensitivity | 86.39% | 81.19% – 90.96% |
| Specificity | 42.51% | 37.84% – 47.31% |
| ROC-AUC | 0.7277 | 0.6901 – 0.7634 |
| PR-AUC | 0.4503 | 0.3951 – 0.5098 |

The 90% development sensitivity target was NOT achieved on the held-out test
(86.39%). Do not claim the final test "satisfied" the development target.

## 5. Absolute Prohibitions

The dashboard may CONSUME the frozen model. It may NEVER:

- [ ] Retrain the model
- [ ] Tune or adjust the threshold (0.1389 is immutable)
- [ ] Add or remove predictors
- [ ] Use final-test data for any development purpose
- [ ] Recalibrate probabilities from test data
- [ ] Silently substitute another model (DLNN, Logistic, etc.)
- [ ] Expose a model-selector dropdown to users
- [ ] Display multi-model consensus badges
- [ ] Allow threshold slider controls

## 6. Required Clinical Language

### USE:
- "Screening" / "Screening signal"
- "Screening probability"
- "Referral recommendation"
- "Refer for Stage-2 HbA1c assessment"
- "HbA1c-defined dysglycemia"
- "Laboratory range" / "Laboratory categorization"
- "Research prototype"
- "Non-laboratory screening"

### AVOID:
- "Diagnosis" / "Diagnoses"
- "You have diabetes"
- "Guaranteed risk" / "Disease certainty"
- "Future diabetes prediction"
- "Validated for Indonesia" / "Validated for clinical use"
- "Clinical optimum" / "Clinically proven"
- "AI accuracy" (when referring to human-AI agreement)

## 7. Human Override Semantics

Human override applies to the **referral/recommendation decision**.

It does NOT change:
- The AI's calculated screening probability
- The patient's biological HbA1c status
- Any clinical diagnosis

Override decisions must record:
- Structured categorical reason (required)
- Clinical notes (required)
- Reviewer identity
- Timestamp

Override must NEVER silently flip a disease label (e.g., `0 if pred == 1 else 1`).

## 8. Stage-2 Confirmatory Protocol

Stage-2 is a separate, independent laboratory intake step — NOT another AI prediction.

HbA1c clinical reference ranges (read-only presentation):
- Normal: < 5.7%
- Prediabetes range: 5.7% – 6.4%
- Diabetes range: ≥ 6.5%

These thresholds require authoritative clinical-source verification before final
implementation. They must be presented as standard clinical guidelines, NOT as
AI-generated classifications.

## 9. Analytics Governance

- Override rate denominator = reviewed cases (NOT total intakes)
- Human-AI agreement = "concordance", never "AI accuracy"
- Ground-truth accuracy requires Stage-2 laboratory verification
- Do not make unsupported decision-improvement claims
