# PROJECT MASTER RECAP
## Skripsi — Two-Stage Explainable Screening Dashboard with Human Review & Override

**Owner:** Felik  
**Status date:** 2026-09-04  
**Role of this file:** Living recap for learning, supervision, implementation continuity, and defense preparation.

> This is a navigation/learning document. Locked scientific artifacts remain the authoritative source for exact model specifications, hashes, split assignments, and final-test results.

---

## 1. Project in One Paragraph

The thesis develops a **research screening dashboard** for previously unrecognized **HbA1c-defined dysglycemia** using seven non-laboratory predictors. The frozen primary model is a **Generalized Additive Model (GAM)** developed from NHANES August 2021–August 2023. The dashboard follows a **two-stage architecture**: Stage 1 produces a screening probability and referral recommendation; a GAM-native explanation shows how the model used the inputs; Human Review can accept or override the **referral recommendation** without altering the original AI output; Stage 2 will present HbA1c laboratory-range information. The prototype is **not a diagnostic tool**.

---

## 2. How the Research Evolved

### Original proposal
Working title originally focused on an Explainable AI dashboard with Human Override for diabetes-risk prediction in Indonesia, with SKI/Kemenkes intended as the main data source.

### Data-access adaptation
SKI/Kemenkes access stalled for roughly four months. The correct thesis framing is:

> **kendala akses data eksternal yang menyebabkan adaptasi metodologis**

Keep evidence of the original request, follow-ups, timeline, and supervisor direction.

### Consequence
Because the final predictive experiment uses NHANES, the thesis must not claim:

- Indonesian external validation
- nationally representative Indonesian performance
- clinical deployment readiness
- prospective/future diabetes incidence prediction

The final task is:

> **non-laboratory screening for currently unrecognized HbA1c-defined dysglycemia**

---

## 3. Final Two-Stage Concept

### Stage 1 — Non-Laboratory Screening

Exactly seven predictors:

1. `age`
2. `sex`
3. `bmi`
4. `hypertension_history`
5. `smoking_history`
6. `waist_cm`
7. `sedentary_minutes_day`

Outputs:

- screening probability
- referral recommendation
- GAM-native local explanation

### Human Review

The reviewer evaluates the **referral recommendation**.

The reviewer does not overwrite:

- biological truth
- HbA1c
- GAM probability
- decision threshold
- model coefficients
- diagnosis

Actions:

- Accept Recommendation
- Override Recommendation

### Stage 2 — HbA1c Laboratory Assessment

Stage 2 accepts a measured HbA1c laboratory percentage and presents the corresponding laboratory range.

Frozen clinical reference:
- **Reference Standard:** American Diabetes Association (ADA) *Standards of Care in Diabetes — 2026 (Section 2)*
- **Rule Identifier:** `ADA_2026_A1C_RANGE_V1`
- **Ranges (Exact Decimal arithmetic):**
  - `<5.7%`: normal-range (`normal_range`)
  - `5.7% to <6.5%`: prediabetes-range (`prediabetes_range`)
  - `>=6.5%`: diabetes-range (`diabetes_range`)

Epistemic constraint: Stage 2 is explicitly presented as **laboratory-range presentation, not automated diagnosis**. In the absence of unequivocal hyperglycemia, clinical diagnosis generally requires appropriate confirmatory testing. The prototype does not evaluate whether confirmatory criteria have been satisfied. Stage 2 executes 0 GAM inference and 0 XAI calls.

---

## 4. Dataset and Cohort

Dataset: official CDC/NCHS NHANES August 2021–August 2023.

Files joined by `SEQN`:

- `DEMO_L`
- `BMX_L`
- `BPQ_L`
- `SMQ_L`
- `PAQ_L`
- `DIQ_L`
- `GHB_L`
- `GLU_L`

Relevant labs:

- `LBXGH` — HbA1c
- `LBXGLU` — fasting glucose

Target cohort:

- adults `>=18`
- `DIQ010 == 2` — no self-reported diabetes
- `DIQ160 == 2` — no self-reported prediabetes

Primary binary outcome:

- `0`: `LBXGH < 5.7`
- `1`: `LBXGH >= 5.7`

Key counts:

- Raw NHANES: `11,933`
- Adults: `8,153`
- Cohort E: `5,907`
- Valid HbA1c: `4,260`
- Analytic Core complete: `4,194`
- Analytic Expanded complete: `4,044`
- Expanded normal-range: `3,106`
- Expanded dysglycemia-range: `938`

Earlier `4,066` expanded count was reconciled to 22 invalid PAD680 special codes: 21 values `9999` and 1 value `7777`, correctly converted to missing.

---

## 5. Stage-1 Input Contract

Canonical order is immutable:

```text
age
sex
bmi
hypertension_history
smoking_history
waist_cm
sedentary_minutes_day
```

Supported UI contract:

| Predictor | Source | UI semantics | Supported domain |
|---|---|---|---|
| Age | RIDAGEYR | integer years | 18–80 |
| Sex | RIAGENDR | male / female | 2 modeled categories |
| BMI | BMXBMI | kg/m² | 11.1–69.9 |
| Hypertension history | BPQ020 | yes / no | binary |
| Smoking history | SMQ020 | yes / no; ≥100 lifetime cigarettes | binary |
| Waist | BMXWAIST | cm | 60.0–187.0 |
| Sedentary time | PAD680 | minutes/day | 0–1200 |

UI semantic encoding is separate from the template. Current model mapping:

- male → 1; female → 0
- yes → 1; no → 0

No silent imputation is allowed.

---

## 6. Predictive Methodology

Master split:

- seed `42`
- stratified
- 80% development / 20% final
- common Expanded final test `N=812`

Development:

- fixed 5-fold stratified CV
- primary metrics: ROC-AUC, PR-AUC, Brier
- sensitivity operating-point analysis: 80%, 85%, 90%, 95%

Candidate models:

### Logistic Regression
- L2
- `C=0.1`

### GAM
- `pygam.LogisticGAM`
- `n_splines=10`
- `lambda=10`
- continuous spline terms + binary factor terms
- `max_iter=200`

### DLNN
- 7 inputs
- Dense 16 ReLU
- Dense 8 ReLU
- sigmoid
- BCE
- Adam `lr=0.001`
- batch 32
- 200 max epochs
- early stopping patience 15
- 15% internal validation from development only

---

## 7. Development Model Selection

Expanded Common development results:

| Model | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|
| Logistic Regression | 0.7345 | 0.4087 | 0.1574 |
| GAM | 0.7382 | 0.4207 | 0.1561 |
| DLNN | 0.7306 | 0.4115 | 0.1577 |

Pre-specified selection hierarchy:

1. pooled OOF PR-AUC
2. ROC-AUC
3. lower Brier
4. simpler model

GAM became the **pre-specified primary model**. This does not mean final testing proved universal superiority.

---

## 8. Frozen Operating Threshold

Frozen GAM threshold:

> **0.1389**

This is a **probability decision threshold**.

It was chosen on development data at an operating point targeting:

> **sensitivity >=90%**

Do not confuse these quantities.

```text
development sensitivity target >=90%
            ↓
operating-point search
            ↓
probability cutoff = 0.1389
```

---

## 9. Final Held-Out Test

Final test:

- `N=812`
- normal-range `621`
- dysglycemia-range `191`

Threshold-independent:

| Model | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|
| GAM | 0.7277 | 0.4503 | 0.1587 |
| Logistic Regression | 0.7288 | 0.4407 | 0.1587 |
| DLNN | 0.7200 | 0.4214 | 0.1609 |

GAM at frozen threshold `0.1389`:

- sensitivity `86.39%`
- specificity `42.51%`
- PPV `31.61%`
- NPV `91.03%`
- F1 `0.4628`
- balanced accuracy `0.6445`
- referral rate `64.29%`
- missed dysglycemia `13.61%`
- HbA1c tests per case detected `3.16`

Confusion matrix:

- TN 264
- FP 357
- FN 26
- TP 165

Critical interpretation:

> The development-derived operating threshold targeting >=90% sensitivity achieved **86.39% sensitivity** on the held-out final test. Therefore, the 90% development sensitivity target was **not reproduced at the final-test point estimate**.

The CI includes 90%, so sampling variability is compatible with the observation, but it must not be asserted as the definite cause.

---

## 10. Model-Comparison and Calibration Interpretation

GAM and Logistic Regression were broadly comparable on final testing.

Do not say GAM was definitively superior.

DLNN did not demonstrate a clear predictive advantage that justified its additional complexity.

Final calibration:

- GAM slope `0.9425`, ECE `0.0238`
- LR slope `1.0013`, ECE `0.0124`
- DLNN slope `0.9208`, ECE `0.0113`

Slope `<1` means predictions are somewhat too extreme / overconfident.

Do not claim GAM had the best final calibration.

---

## 11. Scientific Freeze

The predictive experiment is **CLOSED**.

The final test was opened once and is burned.

The dashboard may consume the frozen artifacts but may not:

- retrain
- retune
- recalibrate
- alter feature definitions
- change threshold
- use final-test outcomes for new primary development

Any new model analysis must be labeled exploratory/post-hoc.

---

## 12. Dashboard Philosophy

Primary philosophy:

> **EVIDENCE-FIRST GUIDED REVIEW**

```text
SYSTEM SCREENS
      ↓
SYSTEM EXPLAINS
      ↓
HUMAN REVIEWS
      ↓
HUMAN DECIDES ACTION
```

Principles:

- screening, not diagnosis
- explanation before human action
- human authority over referral
- progressive disclosure
- visible uncertainty
- auditability
- low cognitive load
- research-safe language
- accessibility
- no unnecessary model complexity in the end-user UI

---

## 13. UI / Technical Direction

Primary component and visual reference:

> **shadcn/ui**

This is a visual/component reference, not a reason to force React.

Current implementation architecture:

- Django Templates
- vanilla CSS design system
- vanilla JavaScript
- shadcn-inspired component language
- no Node/Vite/Webpack build chain

Visual character:

- calm
- restrained
- neutral
- modern
- professional
- research-oriented
- non-alarmist

Avoid giant red risk cards, glassmorphism, finance SaaS styling, hospital ERP styling, AI sparkle aesthetics, and color-only status meaning.

Project skills:

- `research-governance`
- `dashboard-design`
- `frontend-quality`

Precedence:

```text
research-governance
>
approved design specification
>
dashboard-design
>
frontend-quality
>
generic skills
```

---

## 14. Current Domain Architecture

```text
ScreeningRecord
│
├── seven semantic inputs
├── immutable GAM probability
├── immutable AI referral recommendation
├── threshold
├── model provenance
└── created timestamp
│
├── ScreeningExplanation
│    ├── GAM-native additive contributions
│    ├── method/version
│    ├── reconstruction evidence
│    └── explanation status
│
└── HumanReview
     ├── reviewer code
     ├── accepted / overridden
     ├── final referral decision
     ├── override reason
     ├── optional note
     └── review timestamp
```

Meaning:

- **ScreeningRecord** = what the AI produced.
- **ScreeningExplanation** = how the frozen GAM produced it.
- **HumanReview** = what the reviewer decided.

Never collapse these into one mutable row.

---

## 15. Dashboard Phase Recap

### D1 — Design Foundation
Completed:

- design philosophy
- UI reference research
- shadcn component mapping
- IA
- textual wireframes
- design tokens
- accessibility
- XAI design options
- Human Override design
- implementation plan

### D1.5 — Agent Capability Setup
Completed:

- custom project skills
- MCP capability strategy
- research-governance precedence

### D2.1 — Application Shell
Completed:

- shadcn-inspired Django shell
- sidebar
- mobile navigation
- design tokens
- reusable primitives
- accessibility foundation

### D2.1A — Governance Correction
Completed:

- threshold/probability-meter terminology cleanup
- premature clinical language audit
- offline/font review
- fake placeholder metric audit
- no-inference verification

### D2.2 — Stage-1 Form
Completed:

- exactly seven predictors
- server-side validation
- research-domain bounds
- semantic categorical values
- no silent imputation
- input review state
- no model inference

### D2.3 — Frozen GAM Inference
Completed:

- artifact hash verification
- canonical feature order
- deterministic semantic encoding
- frozen preprocessing
- frozen GAM inference
- threshold `0.1389`
- parity with the research pipeline
- fail-closed behavior

Core invariant:

> same input → same preprocessing → same GAM → same probability

### D2.4 — Screening Result + Persistence
Completed:

- immutable `ScreeningRecord`
- UUID result
- original inputs
- full probability
- AI referral recommendation
- model provenance
- PRG result workflow
- result GET does not rerun inference

Result language:

- **Elevated screening signal**
- **Lower screening signal**
- **Research prototype — not a diagnostic tool**

### D2.5 — GAM-Native XAI
Completed and fidelity verified.

Primary explanation:

> **GAM-native additive decomposition**

Not legacy SHAP.

Concept:

```text
η(x) = intercept + Σ f_i(x_i)
p(x) = sigmoid(η(x))
```

Continuous terms use `n_splines=10`; do not casually call this “10 knots.”

Reconstruction error reported at machine precision, approximately:

> `<= 5.55 × 10^-17`

User-facing language:

- pushes screening score higher
- pushes screening score lower

Never causal language.

### D2.6 — Human Review / Accept
Completed.

`HumanReview` is separate from `ScreeningRecord`.

Accept invariant:

```text
final_referral_recommended
=
ai_referral_recommended
```

Acceptance means **agreement**, not accuracy or clinical truth.

Reviewer Code is pseudonymous by study instruction. Regex restrictions do not prove that a submitted string is not a personal name.

### D2.7 — Human Override
**COMPLETED & AUDITED.**

Override definition:

> a reviewer finalizes a referral decision different from the AI recommendation.

Server-derived invariant:

```text
final_referral_recommended
=
NOT ai_referral_recommended
```

Allowed `review_action` values:

- `accepted`
- `overridden`

No implicit default acceptance remains.

#### AI REFER → Human DO NOT REFER reasons
- `additional_context_reduces_concern`
- `input_quality_concern`
- `repeat_assessment_preferred`
- `other`

#### AI DO NOT REFER → Human REFER reasons
- `additional_context_increases_concern`
- `input_quality_concern`
- `precautionary_referral`
- `other`

`other` requires an override note.

D2.7 full test suite:

> **65 tests — OK**

Human Override never changes:

- GAM probability
- AI recommendation
- threshold
- model hashes
- GAM terms
- HbA1c
- diagnosis
- biological truth

---

## 16. XAI Learning Note

GAM terms are additive on the **link/logit scale**, not directly on probability.

Therefore this is unsafe:

> “BMI increased diabetes probability by 8%.”

Prefer:

> “BMI pushes the model screening score higher.”

The logic is:

```text
feature term contributions
        ↓
sum on link scale
        ↓
logistic transformation
        ↓
screening probability
```

Explanation fidelity means the explanation reconstructs the model calculation. It does not mean the model is clinically correct.

---

## 17. Human Override Learning Note

Wrong legacy framing:

```text
AI predicts disease = 1
doctor changes disease = 0
```

Current framing:

```text
AI:
Refer for Stage-2 HbA1c

Human:
Do not refer at this time

Status:
Overridden
```

The original AI recommendation remains preserved.

Override records **decision disagreement**. It does not prove that either the AI or human is correct.

---

## 18. Things We Must Never Claim

Do not claim:

- validated for Indonesia
- clinical diagnosis
- “you have diabetes”
- future diabetes prediction
- clinical optimum threshold
- GAM definitively superior
- GAM best calibrated on final test
- final sensitivity achieved 90%
- Human Override improves decisions unless separately demonstrated
- human-AI agreement = accuracy
- override = AI wrong
- XAI proves correctness
- XAI contributions are causal
- laboratory range = automated diagnosis
- NHANES predictive results are nationally representative US performance

---

## 19. Research-Safe Wording

Prefer:

- screening
- screening probability
- elevated screening signal
- lower screening signal
- referral recommendation
- Stage-2 HbA1c assessment
- HbA1c-defined dysglycemia
- laboratory range
- model contribution
- Human Review
- Human Override
- agreement
- disagreement
- research prototype
- not a diagnostic tool

---

## 20. Current End-to-End Workflow

```text
NEW SCREENING
      ↓
7 NON-LAB INPUTS
      ↓
INPUT REVIEW
      ↓
FROZEN GAM
      ↓
SCREENING RECORD
      ↓
SCREENING RESULT
      ↓
GAM-NATIVE EXPLANATION
      ↓
HUMAN REVIEW
      ↓
┌────────────────────────────┐
│ ACCEPT                     │
│ final = AI recommendation  │
│                            │
│ OR                         │
│                            │
│ OVERRIDE                   │
│ final = opposite decision  │
│ + structured rationale     │
└────────────────────────────┘
      ↓
NEXT: STAGE-2 HbA1c
```

---

## 21. Next Planned Work

### D2.8 — Stage-2 HbA1c

Goals:

- complete the two-stage workflow
- preserve Stage-1 evidence
- preserve final Human Review decision
- accept HbA1c
- present laboratory range
- keep laboratory data separate from model output
- no automated diagnosis
- establish clean Stage-2 persistence
- verify authoritative source for range definitions

### D2.9 — Review Queue + History

Later goals:

- pending-review queue
- immutable case history
- separate AI output / human decision / Stage-2 state
- auditable detail view

### D2.10 — Research Analytics

Possible metrics:

- screenings
- AI referrals
- reviewed records
- acceptances
- overrides
- human-AI agreement
- Stage-2 completion

Agreement must not be labeled accuracy.

### User-study freeze

Before evaluation:

- functional QA
- accessibility QA
- responsive QA
- legacy-route audit
- model hash verification
- final wording audit
- study instrumentation only after protocol design

---

## 22. Evaluation Strategy

Separate claims:

### Predictive performance
Already evaluated on held-out final test.

### Software correctness
Includes:

- input validation
- model parity
- persistence
- no rerun on GET
- anti-tampering
- audit trail

### XAI fidelity
Tests whether the displayed local explanation faithfully reconstructs the GAM calculation.

### Usability / comprehension
Potential:

- task completion
- task error
- time-on-task
- XAI comprehension
- referral-decision comprehension
- Human Override interaction
- SUS

General users/students can support usability/comprehension findings, but not clinical decision-improvement claims.

Health professionals, if available, can support face-validity/workflow feedback, not a clinical trial claim.

---

## 23. Working RQ Direction — Not Yet Locked

Possible revised direction:

**RQ1** — How well does the non-laboratory GAM discriminate and calibrate HbA1c-defined dysglycemia in the held-out NHANES cohort?

**RQ2** — How can GAM-native explanation and Human Review / Override be integrated into a two-stage screening dashboard while preserving the original AI output and audit trail?

**RQ3** — How usable and understandable is the dashboard for intended study users?

**RQ4** — How do users understand and interact with model explanations and the Human Review / Override mechanism?

Do not lock these until Stage 2 and the user-study protocol are finalized.

---

## 24. Thesis Contribution — Working Interpretation

The strongest contribution is not a novel neural architecture.

A stronger contribution is:

> integration of a frozen interpretable screening model, faithful local explanation, structured Human Review / Override, and a two-stage screening workflow into an auditable research dashboard.

Potential system contributions:

- reproducible frozen inference
- model-native XAI fidelity
- clear decision provenance
- separation of AI output and human action
- structured override rationale
- two-stage screening-to-laboratory workflow
- usability/comprehension evaluation

---

## 25. Defense Learning Roadmap

After dashboard development is mature, revisit all material deliberately.

### A. Project story
Understand:

- SKI access problem
- why NHANES was chosen
- why claims narrowed
- screening vs diagnosis
- two-stage rationale

### B. Data
Understand:

- Cohort E
- known diabetes/prediabetes exclusions
- HbA1c outcome
- why no labs in Stage 1
- seven predictors
- special/missing values

### C. ML methodology
Understand:

- development vs final test
- cross-validation
- why final test opened once
- PR-AUC vs ROC-AUC
- Brier score
- calibration
- threshold selection

### D. Final results
Know and understand:

- GAM ROC-AUC `0.7277`
- GAM PR-AUC `0.4503`
- GAM Brier `0.1587`
- sensitivity `86.39%`
- specificity `42.51%`
- threshold `0.1389`

### E. GAM
Explain:

- additive model
- splines
- factor terms
- logit link
- why GAM was chosen
- interpretability advantage

### F. XAI
Explain:

- native decomposition
- why not legacy SHAP
- positive/negative contributions
- reconstruction fidelity
- non-causality

### G. Human Review / Override
Explain:

- accept
- override
- immutable AI output
- agreement ≠ accuracy
- structured reason taxonomy

### H. Dashboard architecture
Explain:

- ScreeningRecord
- ScreeningExplanation
- HumanReview
- why separate entities
- server authority
- anti-tampering
- PRG result pattern

### I. Evaluation
Distinguish:

- predictive validation
- software validation
- XAI fidelity
- usability
- comprehension
- clinical validation

Planned later learning session:

1. Notebook 01 — Data preparation
2. Notebook 02 — Model development
3. Notebook 03 — Model selection
4. Notebook 04 — Final test
5. Dashboard architecture
6. GAM/XAI walkthrough
7. Human Override walkthrough
8. methodology oral drill
9. supervisor-question drill
10. mock thesis defense

---

## 26. Likely Defense Questions

### Why NHANES if the proposal originally targeted Indonesia?
Answer direction:

- SKI access became a documented external constraint.
- the methodology was adapted transparently.
- claims were narrowed.
- NHANES supports prototype development but not Indonesian external validity.

### Why not deep learning?
Answer direction:

- DLNN was evaluated.
- it did not show a clear final predictive advantage.
- GAM was selected under the pre-specified development protocol.
- GAM is substantially easier to explain faithfully.

### Why is the threshold only 0.1389?
Answer direction:

- it is a decision threshold, not prevalence or diagnosis cutoff.
- it came from a high-sensitivity development operating point.
- the final held-out sensitivity was 86.39%.

### Why is specificity low?
Answer direction:

- the operating point prioritized sensitivity for screening.
- this produces more referrals / false positives.
- it is a reported tradeoff, not a claimed clinical optimum.

### What does Human Override do?
Answer direction:

- it changes the final referral action.
- it preserves original AI evidence.
- it does not overwrite biological truth.

### If human overrides, who is correct?
Answer:

> The system does not assume either side is automatically correct. Override records decision disagreement, not ground-truth correctness.

### Why not SHAP?
Answer direction:

- the deployed model is a GAM.
- GAM has a native additive structure.
- its local terms can reconstruct the model output directly.
- native decomposition is therefore a more direct primary explanation for this frozen model.

---

## 27. Protected Artifact Hashes

Latest repeatedly verified:

**GAM**
`204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d`

**Preprocessor**
`6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d`

**Final Model Specification**
`7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5`

**Final Test Predictions**
`fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923`

These are provenance controls, not performance measures.

---

## 28. Legacy Components That Must Stay Isolated

Do not reconnect:

- old Kaggle pipeline
- old model selector
- threshold slider
- multi-model consensus
- legacy SHAP path
- zero-SHAP fallback
- legacy disease-class `Prediction` semantics
- old `Override` model using `doctor_name`
- `override_value` disease flipping

Historical migrations should not be casually deleted.

---

## 29. Current Status Snapshot

**Date:** 2026-09-05

- ML experiment: **CLOSED**
- Final test: **OPENED ONCE / BURNED**
- Frozen primary model: **GAM**
- Stage-1 form: **COMPLETE**
- GAM inference adapter: **COMPLETE**
- Screening persistence: **COMPLETE**
- GAM-native XAI: **COMPLETE / FIDELITY VERIFIED**
- Human Review Accept: **COMPLETE**
- Human Override: **COMPLETE & AUDITED**
- Stage-2 HbA1c: **COMPLETE & VERIFIED (D2.8)**
- Two-Stage Screening Cascade: **COMPLETE & VERIFIED**
- Latest reported test suite: **89 tests OK**
- History / Review Queue: **PENDING (NEXT: D2.9)**
- Research Analytics: **PENDING**
- User Study: **PENDING**
- Final Learning / Defense Drill: **REQUIRED LATER**

---

## 30. Update Protocol

Every future phase should append:

```text
DATE:
PHASE:
STATUS:

WHAT CHANGED:
-

NEW FILES / CONTRACTS:
-

DATABASE MIGRATION:
-

TEST RESULT:
-

RESEARCH-GOVERNANCE IMPACT:
-

NEW LEARNING POINT:
-

NEXT:
-
```

---

## 31. Master Thesis Story

The defensible thesis story is:

> I developed and evaluated an auditable research prototype for two-stage dysglycemia screening. A frozen non-laboratory GAM generates a screening probability and referral recommendation. A model-native additive explanation shows how the GAM used the seven inputs. A separate Human Review layer allows the referral recommendation to be accepted or overridden without changing the original AI output. Stage-2 laboratory assessment then provides HbA1c range information. Predictive performance, explanation fidelity, software behavior, human interaction, and usability are treated as separate claims.

This distinction should remain the backbone of the thesis, dashboard, learning recap, and defense.

---

## 32. Phase D2.8 Log — Stage-2 HbA1c Laboratory Assessment & Two-Stage Cascade Completion

**DATE:** 2026-09-05  
**PHASE:** D2.8 — Stage-2 HbA1c Laboratory Assessment & Two-Stage Cascade Completion  
**STATUS:** COMPLETE & VERIFIED  

### WHAT CHANGED:
- Completed the research prototype's two-stage screening cascade:
  $$\text{Stage-1 Non-Lab Intake} \longrightarrow \text{Frozen GAM Inference} \longrightarrow \text{Additive Explanation} \longrightarrow \text{Human Review} \longrightarrow \text{Final Human Referral Decision} \longrightarrow \text{Stage-2 HbA1c Lab Assessment} \longrightarrow \text{Laboratory Range}$$
- Locked Stage-2 medical reference against the American Diabetes Association (ADA) *Standards of Care in Diabetes — 2026 (Section 2)* and cross-checked with NIDDK guidelines.
- Implemented deterministic Decimal range classification service (`classify_hba1c_range`) using rule version `ADA_2026_A1C_RANGE_V1`:
  - Normal-range: $\text{HbA1c} < 5.7\%$
  - Prediabetes-range: $5.7\% \le \text{HbA1c} < 6.5\%$
  - Diabetes-range: $\text{HbA1c} \ge 6.5\%$
- Added `Stage2Assessment` model linked via `OneToOneField(on_delete=PROTECT)` to `HumanReview`.
- Enforced four-branch eligibility gating: Stage 2 is accessible **only** when `HumanReview.final_referral_recommended == True` (reachable via Accept Refer or Override to Refer). Blocked if final human decision is Do Not Refer.
- Implemented two-step input review workflow: Enter HbA1c $\to$ Server Validation $\to$ Review Value & Preliminary Range $\to$ Confirm $\to$ Persist.
- Enforced strict immutability post-confirmation (read-only in normal UI; no editing/deletion; double submission duplicate protection).
- Enforced anti-tampering: client cannot inject spoofed ranges or diagnosis fields; derived server-side.
- Zero-ML / Zero-XAI execution: Stage 2 executes 0 GAM inference calls and 0 XAI calculations; consumes persisted Stage-1 and Human Review evidence.
- Integrated Two-Stage Workflow Timeline component across Screening Result and Stage-2 pages.

### NEW FILES / CONTRACTS:
- `design/d2_8/HBA1C_REFERENCE_LOCK.md` (Authoritative medical reference lock)
- `design/d2_8/STAGE2_ASSESSMENT_CONTRACT.md` (Stage-2 domain contract and governance rules)
- `design/d2_8/STAGE2_PRESENTATION_SPEC.md` (UI presentation and information architecture specification)
- `design/d2_8/D2_8_DATABASE_AUDIT.md` (Database schema and migration audit)
- `design/d2_8/D2_8_ACCESSIBILITY_AUDIT.md` (WCAG 2.1 AA accessibility audit)
- `design/d2_8/D2_8_RESPONSIVE_AUDIT.md` (Responsive multi-viewport audit across 1440px, 1280px, 768px, 390px)
- `design/d2_8/D2_8_MEDICAL_LANGUAGE_AUDIT.md` (Epistemic boundaries and medical copy audit)
- `design/d2_8/D2_8_IMPLEMENTATION_REPORT.md` (Comprehensive D2.8 implementation report)
- `dashboard/predictor/services/hba1c_range.py` (Deterministic range classification service)
- `dashboard/predictor/templates/predictor/stage2_entry.html` (Stage-2 entry form template)
- `dashboard/predictor/templates/predictor/stage2_review.html` (Stage-2 input review template)
- `dashboard/predictor/templates/predictor/stage2_result.html` (Stage-2 result template)
- `design/d2_8/screenshots/` (8 Visual QA screenshots)

### DATABASE MIGRATION:
- Migration `predictor.0006_stage2assessment`: Creates `Stage2Assessment` table with UUIDv4 PK, OneToOne relation to `HumanReview` (`on_delete=PROTECT`), `hba1c_percent` (DecimalField), `laboratory_range` (CharField), `range_rule_version` (CharField), `entry_method` (CharField), and `created_at` (DateTimeField).

### TEST RESULT:
- **89 tests passing** (`manage.py test predictor`, 0 failures, 0 errors in 0.486s).
- 24 new automated tests covering exact Decimal boundary conditions (5.69, 5.70, 6.49, 6.50, 5.7, 6.5), domain safety, four-branch eligibility matrix (Cases A, B, C, D, E, F), anti-tampering, duplicate defense, immutability of prior stages, and zero ML/XAI verification.

### RESEARCH-GOVERNANCE IMPACT:
- Complete epistemic separation preserved: Stage 2 presents **Laboratory Range Categories**, NOT automated clinical diagnoses.
- Mandatory Diagnostic Confirmation Caveat visible in all Stage-2 views:
  > *"This range presentation is not an automated diagnosis. In the absence of unequivocal hyperglycemia, clinical diagnosis generally requires appropriate confirmatory testing. This prototype does not evaluate whether confirmation has occurred."*
- Methodological assay limitation note presented transparently.
- Original `ScreeningRecord` and `HumanReview` remain 100% immutable and unmutated.
- Protected research artifact hashes verified byte-identical.

### NEW LEARNING POINT:
- A clinical range classification is fundamentally a laboratory reporting event, not a predictive model. By tying Stage-2 intake directly to the authorizing `HumanReview` entity rather than the GAM model, the architecture cleanly mirrors clinical decision-support reality: the laboratory test is ordered and recorded because the human reviewer decided to refer, preserving the distinct epistemic authority of each step.

### NEXT:
- **Phase D2.9:** Review Queue & Screening History Experience.

---

## 33. PHASE D2.9 — CASE LIFECYCLE, REVIEW QUEUE & SCREENING HISTORY NAVIGATION (COMPLETED)

### PURPOSE:
Implement operational navigation across the two-stage screening cascade, transforming persisted records into an actionable Review Queue, an auditable Screening History ledger, and a centralized deterministic lifecycle-state derivation engine without executing new prediction logic or research analytics.

### ARCHITECTURE & LIFECYCLE SPECIFICATION:
- **Centralized Lifecycle Service:** `dashboard/predictor/services/screening_lifecycle.py`
  - Lifecycle state is **strictly derived dynamically** from persisted relations (`ScreeningRecord`, `ScreeningExplanation`, `HumanReview`, `Stage2Assessment`).
  - No mutable `status` column added to `ScreeningRecord`.
  - Deterministic Precedence Hierarchy:
    1. Integrity check -> `integrity_error`
    2. Explanation missing/failed -> `explanation_unavailable` ("Needs System Attention", actionable=False)
    3. HumanReview absent -> `pending_review` ("Pending Human Review", actionable=True -> `/result/`)
    4. Final referral recommended is False -> `reviewed_no_referral` ("Reviewed — No Stage 2", actionable=False, Stage 2="Not applicable")
    5. Stage2Assessment absent -> `pending_stage2` ("Pending Stage 2", actionable=True -> `/stage2/`, Stage 2="Pending")
    6. Stage2Assessment present -> `completed_stage2` ("Completed Two-Stage", actionable=False, Stage 2="Completed")
- **Review Queue (`/review/`):**
  - Displays **actionable cases only**.
  - Section A (`tab=review`): Pending Human Review (verified XAI, no review). Links directly to authoritative `/result/`.
  - Section B (`tab=stage2`): Pending Stage 2 (final referral recommended, no Stage 2). Links directly to authoritative `/stage2/`.
  - Excluded from queue: Fully completed cases and non-referred screenings.
  - Explanation failure handling: Restrained system attention section; human review locked.
- **Screening History Ledger (`/history/`):**
  - Invariant: **Exactly 1 row per `ScreeningRecord`**.
  - Mandatory separation: Distinct columns for **AI Recommendation** and **Final Human Decision** (never collapsed into an ambiguous single "Decision" column).
  - Mandatory Stage-2 distinction: "Not applicable" (if final human decision is Do not refer) vs "Pending" (if final human decision is Refer and no Stage 2) vs "Completed".
  - HbA1c laboratory range displayed only when Stage 2 is completed.
  - Server-side pagination (default 25 rows/page) preserving query parameters.
  - Non-PII filters: workflow status, AI recommendation, review action, final human decision, Stage-2 status, HbA1c laboratory range, order.
  - Search: by Screening UUID (full or prefix). Zero participant PII collected or searched.
- **Overview Integration (`/`):**
  - Real operational counts: Total Screenings, Pending Reviews, Pending Stage 2, Completed Two-Stage.
  - Recent Screening Cases table linking to `/screening/<uuid>/result/`.
  - Restrained: Zero research analytics metrics (no override rates, agreement rates, accuracy, or distributions; deferred to D2.10).

### QUERY OPTIMIZATION & PERFORMANCE:
- Eager relational joins using `select_related('explanation', 'human_review__stage2_assessment')`.
- Bounded query execution: Review Queue loads in exactly 1 query; History loads in exactly 2 queries (1 count + 1 dataset). N+1 query loops completely eliminated (a bounded / constant number of SQL queries per rendered page).
- Read-only invariant: GET requests perform **0 GAM inferences**, **0 XAI calculations**, **0 HbA1c reclassifications**, and **0 database writes**.

### NEW FILES & CONTRACTS:
- `design/d2_9/SCREENING_LIFECYCLE_CONTRACT.md` (Formal lifecycle contract and precedence specification)
- `design/d2_9/REVIEW_QUEUE_SPEC.md` (Operational review queue specification)
- `design/d2_9/SCREENING_HISTORY_SPEC.md` (Screening history and case audit ledger specification)
- `design/d2_9/D2_9_DATA_INTEGRITY_AUDIT.md` (Auditing impossible state detection and data consistency)
- `design/d2_9/D2_9_QUERY_PERFORMANCE_AUDIT.md` (Query optimization and N+1 prevention audit)
- `design/d2_9/D2_9_ACCESSIBILITY_AUDIT.md` (WCAG 2.1 AA accessibility audit)
- `design/d2_9/D2_9_RESPONSIVE_AUDIT.md` (Responsive multi-viewport audit across 1440px, 1280px, 768px, 390px)
- `design/d2_9/D2_9_MEDICAL_LANGUAGE_AUDIT.md` (Epistemic boundaries and medical copy audit)
- `design/d2_9/D2_9_IMPLEMENTATION_REPORT.md` (Comprehensive D2.9 implementation report)
- `dashboard/predictor/services/screening_lifecycle.py` (Centralized lifecycle derivation module)
- `design/d2_9/screenshots/` (8 Visual QA screenshots)

### TEST RESULT:
- **112 tests passing** (`manage.py test predictor`, 0 failures, 0 errors in 1.604s).
- 23 new automated tests covering all 6 active lifecycle states, precedence hierarchy, impossible state detection, queue inclusion/exclusion, 1-row history invariant, separate AI/human columns, Stage 2 status distinctions, UUID search, filter combinations, pre/post GET database immutability snapshots, zero ML/XAI execution, and constant bounded query performance.

### RESEARCH-GOVERNANCE IMPACT:
- Pure consumption of persisted evidence: zero predictive inference occurs during list/ledger browsing.
- Clear epistemic hierarchy preserved: machine recommendation remains visible alongside authoritative clinician disposition.
- Zero clinical diagnosis claims; workflow status describes application state exclusively.
- Protected research artifact hashes verified byte-identical.

### NEW LEARNING POINT:
- Workflow state is an emergent property of recorded audit evidence, not a mutable database flag. By deriving lifecycle status deterministically from relational entities rather than storing a mutable `status` string, the system eliminates synchronization drift, guarantees data integrity, and makes the audit trail the single source of truth for application behavior.

### NEXT:
- **Phase D2.10:** Research Analytics & Post-Market Surveillance. (Completed below)

---

## 34. PHASE D2.10 — RESEARCH ANALYTICS + HUMAN–AI DECISION FLOW (COMPLETED)

### PURPOSE:
Implement research-safe aggregate analytics derived strictly from persisted screening workflow records (`ScreeningRecord`, `ScreeningExplanation`, `HumanReview`, `Stage2Assessment`). The surveillance dashboard summarizes screening volume, AI referral decisions, human review completion, human–AI decision concordance, final clinician referral decisions, override rationale, Stage-2 completion, and observed HbA1c laboratory-range distributions without violating epistemic boundaries or introducing selective verification bias.

### PREFLIGHT CORRECTIONS (D2.9 RECONCILIATION):
- **Lifecycle State Count:** Corrected documentation from "7 states" to **6 active lifecycle states** (`explanation_unavailable`, `pending_review`, `reviewed_no_referral`, `pending_stage2`, `completed_stage2`, `integrity_error`). Documented in `design/d2_10/D2_9_PREFLIGHT_CORRECTIONS.md`.
- **Query Complexity Wording:** Replaced "O(1) query execution" with "a bounded / constant number of SQL queries per rendered page", accurately describing the architectural property verified by `assertNumQueries()`.

### METRIC DENOMINATOR PHILOSOPHY & SPECIFICATION:
Every metric enforces an explicit numerator, denominator, and inclusion criteria:
- **Total Screenings ($N_{\text{screenings}}$):** Primary population denominator.
- **AI Referral Rate:** Count of `ai_referral_recommended == True` divided by $N_{\text{screenings}}$. (Never called positive rate, disease rate, or clinical accuracy).
- **Review Completion Rate:** Completed reviews divided strictly by $N_{\text{review\_eligible}}$ (cases with generated explanation). Explanation failure cases are correctly excluded from review eligibility.
- **Human–AI Agreement Rate:** Accepted reviews ($N_{\text{accepted}}$) divided strictly by reviewed cases ($N_{\text{reviewed}}$). **Concordance $\neq$ Accuracy.**
- **Human Override Rate:** Overridden reviews ($N_{\text{overridden}}$) divided strictly by reviewed cases ($N_{\text{reviewed}}$). **Override $\neq$ Machine Error.** Invariant: Agreement Rate + Override Rate $= 1.0$ (or 100%).
- **Final Human Referral Rate:** Final referrals ($N_{\text{final\_refer}}$) divided strictly by reviewed cases ($N_{\text{reviewed}}$).
- **Stage-2 Completion Rate:** Completed Stage-2 assessments divided strictly by eligible final referrals ($N_{\text{stage2\_eligible}} = N_{\text{final\_refer}}$). Never divided by all screenings.
- **Observed HbA1c Laboratory-Range Distribution:** Normal-range ($<5.7\%$), Prediabetes-range ($5.7\text{--}6.4\%$), and Diabetes-range ($\ge 6.5\%$) counts divided strictly by completed Stage-2 assessments ($N_{\text{stage2\_completed}}$). (Never labeled disease prevalence).
- **Division-by-Zero Safety:** When denominator $= 0$, rates strictly return `None` and display as "Not available" / "—", never defaulted to $0\%$.

### SELECTIVE VERIFICATION BIAS SAFEGUARD:
- Stage-2 venous HbA1c is selectively observed only for cases that reached a final human REFER decision under this clinical workflow. Non-referred individuals correctly do not receive blood tests.
- **Strict Prohibition:** D2.10 strictly prohibits computing sensitivity, specificity, PPV, NPV, ROC-AUC, PR-AUC, confusion matrices, or "override success rates" from operational Stage-2 records.
- The frozen held-out Phase-5 evaluation remains the sole authoritative source of predictive performance. Documented in `design/d2_10/D2_10_VERIFICATION_BIAS_NOTE.md`.

### HUMAN–AI DECISION TRANSITION MATRIX (2×2):
- Cross-tabulation of AI recommendations (Refer, Do not refer) vs Final Human Decisions (Refer, Do not refer) scoped strictly to reviewed cases ($N_{\text{reviewed}}$).
- Cells represent accepted referral, override away from referral, accepted non-referral, and override toward referral.
- Labeled **Decision Transition Matrix**, NOT confusion matrix (neither axis is biological ground truth).
- Invariants: sum of 4 cells $== N_{\text{reviewed}}$, diagonal sum $== N_{\text{accepted}}$, off-diagonal sum $== N_{\text{overridden}}$.

### OVERRIDE DIRECTION & STRUCTURED REASONS:
- Directional split: Override away from referral (AI Refer $\rightarrow$ Human No Refer) vs Override toward referral (AI No Refer $\rightarrow$ Human Refer), with denominator $N_{\text{overridden}}$.
- Standardized taxonomy reason distributions tracked by branch using clean human-readable labels.
- Automated NLP and text-mining of free-text override notes is strictly prohibited.

### ARCHITECTURE & QUERY EFFICIENCY:
- **Centralized Service:** `dashboard/predictor/services/research_analytics.py` returning typed immutable `ResearchAnalyticsSnapshot`.
- **Bounded SQL Execution:** Computed via exactly 2 bounded SQL queries per rendered page using Django ORM `Count(filter=Q(...))` conditional aggregation. Zero N+1 query loops.
- **Zero ML/XAI & Zero Writes:** GET `/analytics/` causes 0 GAM inferences, 0 XAI calculations, 0 HbA1c reclassifications, and 0 database writes.

### NEW FILES & CONTRACTS:
- `design/d2_10/D2_10_IMPLEMENTATION_REPORT.md` (Comprehensive implementation report)
- `design/d2_10/RESEARCH_ANALYTICS_CONTRACT.md` (Typed contracts and query boundaries)
- `design/d2_10/ANALYTICS_DENOMINATOR_SPEC.md` (Exhaustive denominator and interpretation specification)
- `design/d2_10/ANALYTICS_PRESENTATION_SPEC.md` (UI/UX presentation tokens and neutral moral palette)
- `design/d2_10/D2_10_VERIFICATION_BIAS_NOTE.md` (Authoritative verification-bias rationale and defense point)
- `design/d2_10/D2_10_DATA_INTEGRITY_AUDIT.md` (Invariants and legacy isolation audit)
- `design/d2_10/D2_10_QUERY_PERFORMANCE_AUDIT.md` (2-query bounded optimization audit)
- `design/d2_10/D2_10_ACCESSIBILITY_AUDIT.md` (WCAG 2.1 AA compliance audit)
- `design/d2_10/D2_10_RESPONSIVE_AUDIT.md` (Multi-viewport responsive audit across 1440px, 1280px, 768px, 390px)
- `design/d2_10/D2_9_PREFLIGHT_CORRECTIONS.md` (Preflight documentation reconciliation)
- `dashboard/predictor/services/research_analytics.py` (Centralized analytics computation service)
- `dashboard/predictor/templates/predictor/analytics.html` (Complete research analytics template)
- `design/d2_10/screenshots/` (8 Visual QA screenshots)

### TEST RESULT:
- **132 tests passing** (`manage.py test predictor`, 0 failures, 0 errors in 1.519s).
- 20 new automated tests covering all mathematical denominators, agreement + override invariant, transition matrix invariants, direction counts, structured reasons, division-by-zero handling, date filtering, legacy record isolation, bounded SQL queries, read-only GET requests, zero ML/XAI execution, and prohibited performance metrics AST inspection.

### RESEARCH-GOVERNANCE IMPACT:
- Decision concordance cleanly distinguished from predictive accuracy.
- Verification bias explicitly prevented in code, tests, and user-facing copy.
- Immutable relational audit trail remains the single source of truth.
- Protected research artifact hashes verified byte-identical.

### NEXT:
- **Phase D3:** Final System Audit, Environment Isolation & Release Freeze. (Completed below)

---

## 35. PHASE D3 — FINAL SYSTEM AUDIT + USER-STUDY READINESS + RELEASE FREEZE (COMPLETED)

### PURPOSE:
Perform a comprehensive, exhaustive final system audit across the complete two-stage screening research prototype before any formal human user-study data are collected. D3 establishes that the completed software is scientifically consistent, functionally correct, reproducible, auditable, accessible (WCAG 2.1 AA), responsive (390px–1440px), secure, isolated from legacy workflows, completely free from development/demo-data contamination, and formally frozen for study evaluation.

### KEY ACCOMPLISHMENTS & AUDIT FINDINGS:

1. **Development Data vs Formal Study Data Separation (Requirement P0):**
   - Preserved existing development database containing 29 demonstration cases as a permanent audit baseline: `dashboard/db_development_archive_d2_10.sqlite3` (SHA256: `8b11a9ffbdc4641cd9164f16697a565ee8de027407f4257c3437bb8fc525c566`). Contains zero participant PII.
   - Initialized a clean, reproducible formal study database from zero migrations: `dashboard/db_study.sqlite3` (SHA256: `865b75f6fd511effde7d6e0f84f4b2e17d9e69af2f3eebc3e19d63dffe537e77`). Verified exactly 0 ScreeningRecords, 0 Explanations, 0 HumanReviews, 0 Stage2Assessments, and 0 legacy rows.
   - Introduced environment-driven switching via `APP_DATA_MODE` (`development` vs `study`) in `dashboard/dashboard/settings.py` and `predictor/context_processors.py`.
   - In development mode, `/analytics/` displays a persistent warning banner (*"Development environment — displayed records may include synthetic or QA data."*). In formal study mode, this warning is suppressed and analytics starts from clean zero-state.
   - Suppressed developer design system demo route (`/components/`) from active navigation when running in study mode.
   - Strictly prohibited synthetic study data seeding or destructive browser-accessible reset buttons.

2. **Route, Path & Navigation Audit:**
   - Audited all 18 registered URLs in `dashboard/predictor/urls.py`.
   - 12 active production-research routes verified: `/` (Overview), `/screening/new/`, `/screening/run/`, `/screening/<uuid>/result/`, `/screening/<uuid>/review/accept/`, `/screening/<uuid>/review/override/`, `/screening/<uuid>/stage2/`, `/screening/<uuid>/stage2/confirm/`, `/review/`, `/history/`, `/analytics/`, `/about/`.
   - 1 development-only route isolated: `/components/` (omitted from navigation in study mode).
   - 5 legacy D1 routes quarantined: `index/`, `predict/`, `prediction/<pk>/`, `override/`, `evaluation/` (zero calls from active navigation or templates; dead code).

3. **Global Language & Research Governance Audit:**
   - Full text search across all templates and services confirmed zero occurrences of ungrounded diagnostic language (*"patient has diabetes"*, *"AI correct"*, *"AI incorrect"*, *"doctor corrected"*, *"clinical truth"*, *"future diabetes risk"*, *"clinical optimum"*, *"13.9% sensitivity"*).
   - All occurrences of "diagnosis" explicitly disclaim diagnostic authority (*"This screening result is not a diagnosis"*, *"does not provide medical diagnosis"*).
   - Prominently declared in `about.html` Section 4: Model developed on US NHANES 2021–2023 is **not validated for Indonesia**; GAM (ROC-AUC 0.7277) and Logistic Regression (ROC-AUC 0.7291) showed broadly comparable discrimination; sensitivity point estimate 86.39% did not reproduce the ≥90% development cross-validation target at point estimate, though 95% CI (81.19%–90.96%) encompasses it.

4. **Model Execution, XAI & Threshold Single Authority:**
   - Verified that ONLY `screening_inference.py` executes GAM `predict_mu` inference and ONLY at Stage-1 screening run time (`run_screening_view`).
   - Verified that Result GET, Review Queue, History, Analytics, Review Accept, Override, and Stage 2 execute 0 GAM inferences.
   - Verified that GAM-native additive XAI (`explain_screening`) is generated once at screening intake, verified within `1e-10` fidelity tolerance, and persisted. Result GET reads persisted explanations; legacy SHAP is completely quarantined.
   - Operating threshold `0.1389` is defined exclusively as `FROZEN_DECISION_THRESHOLD` in `screening_inference.py`. Zero user sliders, client JavaScript thresholds, or alternative decision branches exist.

5. **Canonical Order & Input Encoding:**
   - Canonical feature order strictly asserted globally: `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`.
   - Semantic input values (`male`/`female`, `yes`/`no`) stored in database; numeric encoding occurs strictly inside `screening_inference.encode_and_order_inputs`. Templates are never authoritative for numeric feature encoding.

6. **Complete End-to-End Scenario Matrix (Scenarios A–H):**
   - **Scenario A (Refer → Accept → Stage2 Normal):** Verified full pipeline to `completed_stage2`.
   - **Scenario B (Refer → Accept → Stage2 Prediabetes):** Verified ADA prediabetes categorization.
   - **Scenario C (Refer → Override → Do Not Refer):** Verified Stage2 blocked; state `reviewed_no_referral`.
   - **Scenario D (No Refer → Accept → Do Not Refer):** Verified Stage2 blocked; state `reviewed_no_referral`.
   - **Scenario E (No Refer → Override → Refer → Stage2 Diabetes):** Verified override enables Stage2; ADA diabetes-range derived.
   - **Scenario F (XAI Failure):** Verified ScreeningRecord preserved, explanation status `failed`, Human Review blocked.
   - **Scenario G (Inference Failure):** Verified atomic rollback; zero records persisted.
   - **Scenario H (Invalid Stage2 Input):** Out-of-bounds HbA1c (<2.0%) rejected; zero Stage2Assessments persisted.

7. **Database Schema & Clean Migration Reproducibility:**
   - Successfully executed full migration sequence from scratch against an empty SQLite database. All 24 migrations applied cleanly.
   - System check (`python manage.py check`) confirmed: `0 issues (0 silenced)`.
   - Deletion protection (`on_delete=models.PROTECT`) verified on all downstream evidence.

8. **Security, Privacy & Failure Modes:**
   - POST-only enforcement verified for all mutating endpoints; GET requests are strictly read-only.
   - CSRF protection active on all state-changing forms; zero forms exempt.
   - Server authority enforced: browser cannot dictate AI probabilities, recommendations, threshold, or laboratory ranges.
   - Free-text fields (`override_note`, `reviewer_code`) rendered using standard template auto-escaping; zero unsafe rendering.
   - Zero patient PII collected across the application.
   - Browser console audit clean: 0 uncaught JavaScript errors, 0 failed asset requests.
   - Zero silent fallbacks: all exceptions raise typed domain errors and fail closed.

9. **Accessibility & Responsive QA:**
   - WCAG 2.1 AA compliant: full keyboard navigability, skip-to-content link, visible focus rings, ARIA landmarks, single `<h1>` hierarchy, explicit error association, dialog focus trapping/restoration, color independence.
   - Multi-viewport responsive verification across 1440px, 1280px, 768px, 390px: zero horizontal page overflow.

10. **Release Manifest & Readiness Determination:**
    - Assigned research prototype release identifier: **`research-prototype-v1.0`**.
    - Created comprehensive documentation pack: 11 audit documents in `design/d3/` and 5 documents in `docs/`.
    - Captured 11 reference screenshots in `design/d3/screenshots/` (including clean study zero-state).
    - User-Study Readiness Checklist: **READY FOR FORMAL EVALUATION PROTOCOL LOCK**.
    - Deferred user-study questionnaire logic (SUS, Likert scales, task timers) to prevent premature instrumentation before protocol lock.

### CRITICAL LEARNING POINTS RECORDED:
> **"Development dashboard analytics are not study results."**  
> Operational records generated during testing, QA, and screenshot creation represent demonstration evidence only. They must never be conflated with or cited as empirical evaluation findings from human respondents.

> **"Predictive validation, XAI fidelity, functional validation, and usability evaluation are separate evidence layers."**  
> Held-out cross-validation establishes predictive performance; mathematical reconstruction establishes XAI fidelity; end-to-end integration tests establish software correctness; and human respondent trials establish usability and decision interaction. None can substitute for another.

### TEST SUITE SUMMARY:
- **144 tests passing** (`manage.py test predictor`, 0 failures, 0 errors in 1.305s).
- All 12 new Phase D3 system audit tests passing.

### PROTECTED ARTIFACT HASH VERIFICATION:
- **GAM (`gam_final.pkl`):** `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` (VERIFIED MATCH)
- **Preprocessor (`preprocessor.pkl`):** `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` (VERIFIED MATCH)
- **Model Spec (`FINAL_MODEL_SPECIFICATION_LOCKED.md`):** `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` (VERIFIED MATCH)
- **Final Test Predictions (`final_test_predictions.csv`):** `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` (VERIFIED MATCH)

### RELEASE STATUS:
**FEATURE DEVELOPMENT IS FROZEN.**  
The software prototype is completely frozen under `research-prototype-v1.0`. Only documented defect corrections are allowed until the evaluation protocol is completed.

### NEXT STEP:
- Formal User-Study Protocol Design (Participant sampling, task scenario scripts, evaluation questionnaire design, ethical review, supervisor alignment). (Completed below)

---

## 36. PHASE E1 — FORMAL USER-STUDY PROTOCOL DESIGN + RESEARCH-QUESTION / CLAIM LOCK (COMPLETED)

### PURPOSE:
Design and freeze the formal evaluation protocol for `research-prototype-v1.0` before questionnaire implementation, participant recruitment, formal respondent data collection, or statistical analysis. Phase E1 is a pure METHODOLOGY phase; the frozen dashboard software and machine learning artifacts remained 100% untouched.

### PROTOCOL VERSION & IDENTIFIER:
- **Protocol Document Identifier:** `E1-PROTOCOL-2026-V1.0.1` (supersedes `V1.0` prior to any participant contact)
- **Protocol Version:** `1.0.1` (Ready for Supervisor / Institutional Review)
- **Stimulus Target:** `research-prototype-v1.0` (144 automated tests passing; 4 protected artifact hashes byte-identical)

### REVISED RESEARCH QUESTION & EVIDENCE MAPPING:
1. **RQ1 (Predictive Discrimination & Calibration):**
   *How well does the frozen non-laboratory GAM discriminate and calibrate HbA1c-defined dysglycemia in the held-out NHANES test cohort?*
   - **Evidence Source:** Phase 5 held-out Expanded test cohort ($N=812$: 621 normal-range, 191 dysglycemia-range; ROC-AUC 0.7277, 95% bootstrap CI [0.6875, 0.7656], PR-AUC 0.4503, Brier 0.1587, sensitivity 86.39%, specificity 42.51% at frozen threshold 0.1389).
   - **Critical Epistemic Boundary:** The development-derived operating threshold targeting >=90% sensitivity achieved 86.39% sensitivity on the held-out final test. Therefore the 90% development sensitivity target was not reproduced at the final-test point estimate.
   - **User-Study Analysis Required:** **NONE.** Purely offline quantitative validation.
2. **RQ2 (System Integration & Auditability):**
   *How can GAM-native explanation and Human Review / Human Override be integrated into an auditable two-stage screening dashboard while preserving the original AI output and decision provenance?*
   - **Evidence Source:** Phase D2.3–D2.8 contracts, D3 final system audit, 144 automated tests, End-to-End Scenarios A–H.
   - **User-Study Analysis Required:** **NONE.** System architecture, software correctness, and audit trail immutability verification.
3. **RQ3 (Dashboard Usability & Operability):**
   *How usable is the frozen two-stage screening dashboard for participants performing the defined screening-review tasks?*
   - **Evidence Source:** Formal user study with primary cohort ($N=24\text{--}30$): Standard 10-item System Usability Scale (SUS), task completion rates, task assistance levels (0–3), error taxonomy frequencies.
4. **RQ4 (User Comprehension & Mental Model Fidelity):**
   *How well do participants understand the Stage-1 screening result, GAM-native explanation, Human Review / Override semantics, and Stage-2 laboratory-range output?*
   - **Evidence Source:** Formal user study with primary cohort ($N=24\text{--}30$): 8-item objective multiple-choice comprehension quiz, exploratory custom clarity items (5-point Likert), lightweight thematic qualitative feedback.

### TWO-LAYER PARTICIPANT STRATEGY & SAMPLING PLAN:
- **Layer 1: Primary Usability & Comprehension Group:**
  - Target Sample Size: $N = 24\text{ to }30$ completed sessions (Practical thesis minimum: $N = 20$).
  - Population: University students, staff, and general adult computer users.
  - Sampling Method: Non-probability purposive and convenience sampling (explicitly documented as non-representative).
  - Permitted Claims: Interface usability, task completion, layout clarity, conceptual understanding of screening results, XAI factor directions, and override mechanics.
  - Prohibited Claims: Clinical usability, clinician acceptance, diagnostic efficacy, or appropriateness for real-world hospital deployment.
- **Layer 2: Optional Health-Professional Face-Validity Group:**
  - Target Sample Size: $N = 3\text{ to }5$ healthcare practitioners (physicians, nurses, or clinical trainees).
  - Permitted Claims: Professional face validity, terminology naturalness, and perceived plausibility of the screening/referral workflow.
  - Prohibited Claims: Clinical trial findings, diagnostic validation, patient benefit, or medical error reduction.
  - Methodological Isolation: Expert ratings **MUST NOT** be pooled into the primary lay-cohort SUS calculations.

### PARTICIPANT IDENTIFIER & LINKAGE LOCK:
- Formally resolves D3's `USER_STUDY_DATA_LINKAGE_DECISION.md` (status: LOCKED).
- Unified pseudonymous code: `P001`–`P030` for primary cohort; `E001`–`E005` for expert cohort.
- In prototype: Participant enters assigned code as `Reviewer Code` in Task 3 and Task 4, populating `HumanReview.reviewer_code`.
- In external survey: Participant enters matching code.
- Deterministic 100% SQL inner-join linkage without requiring any database schema migrations or UI modifications.
- Two-Vault Privacy Model: Master identity linking sheet (Vault A) kept encrypted offline and destroyed upon thesis defense; public analysis datasets (Vault B) use pseudonymous codes exclusively.

### STANDARDIZED SYNTHETIC TASK SET:
- Fictional synthetic screening profile cards exclusively (`CASE-ALPHA` [elevated signal] and `CASE-BETA` [lower signal]). Zero personal health data collected.
- Procedural instructions only ("accept the recommendation", "record an override using supplied reason"); participants are never asked for independent clinical judgment.
- 6 Scripted Tasks:
  - Task 1: Stage-1 Non-Laboratory Screening Intake (Form entry, live validation, review card).
  - Task 2: Screening Result & GAM-Native XAI Interpretation (Recommendation badge, factor direction, moderating factor).
  - Task 3: Human Guided Review (Accept recommendation, enter reviewer code, verify finalized state).
  - Task 4: Human Override Workflow (Modal dialog, structured reason selection, notes textarea, finalize opposite referral decision).
  - Task 5: Stage-2 HbA1c Laboratory Assessment (Enter 6.1%, identify Prediabetes laboratory reference range, verify non-diagnostic caveat).
  - Task 6: Audit History & Traceability (Locate case in history ledger, verify original AI recommendation was never erased).
- Standardized 4-level assistance hierarchy: Level 0 (Independent), Level 1 (General Prompt), Level 2 (Directional Hint), Level 3 (Procedural Demonstration = Task Failure).

### MEASUREMENT INSTRUMENT SPECIFICATIONS:
1. **8-Item Objective Comprehension Quiz:**
   - 4-option multiple-choice testing minimum domains A–H: Screening meaning (not diagnosis), Lower signal (not zero risk), XAI direction (additive model score push), XAI causality (correlation not biological cause), Human Override (changes final referral decision, not probability), Stage-2 meaning (clinical reference range, not automated diagnosis), AI vs Human persistence (original AI never erased), Agreement interpretation (concordance, not accuracy).
   - Binary scoring (1/0), total score 0–8.
2. **Standard System Usability Scale (SUS):**
   - Exact 10 items from Brooke (1996); standard scoring formula: $\text{SUS} = 2.5 \times (\sum \text{odd}-1 + \sum 5-\text{even})$, range 0–100.
   - Descriptive metrics: N, mean, SD, median, IQR, min, max, 95% CI.
   - Empirical benchmark comparison: Bangor et al. (2008, 2009) average benchmark 68.0.
   - Explicit rule: SUS is an index score, NOT a percentage or measure of clinical efficacy.
3. **5 Custom Exploratory Clarity Items:**
   - 5-point Likert covering screening clarity, XAI clarity, AI vs human distinction, perceived review control, and Stage-2 lab meaning.
   - Analyzed strictly as individual distributions (median, IQR); never averaged into a composite score.
4. **Qualitative Feedback:**
   - 3 open-ended questions analyzed via lightweight inductive thematic coding (Braun & Clarke, 2006).

### FROZEN STATISTICAL ANALYSIS PLAN:
- Primary approach: Descriptive statistics (frequencies, percentages, means, SDs, medians, IQRs).
- No post-hoc hypothesis generation or small-sample inferential overreach.
- Analysis environment pre-defined: Python 3.10 with `pandas`, `numpy`, `scipy`.
- Missing data handling pre-specified: single missing SUS item imputed with neutral 3 (Sauro & Lewis, 2016); $\ge 2$ missing items treated as missing; omitted comprehension items scored 0.
- Post-collection exclusion criteria pre-specified: technical failure or procedural error only; zero exclusions based on unfavorable usability ratings.

### ETHICS & INSTITUTIONAL DEPENDENCY STATUS:
- **Technical & Methodological Readiness:** **READY** (Software frozen, study DB initialized, 144 tests passing, protocol locked).
- **Institutional Authorization for Data Collection:** **PENDING AUTHORIZATION** (Awaiting formal academic supervisor signoff and faculty ethics clearance prior to participant contact).

### PILOT STUDY PLAN:
- Sample size: $N = 3\text{ to }5$ participants using `db_pilot.sqlite3`.
- Strict non-reuse rule: Pilot participants excluded from final formal evaluation cohort.
- Change policy: Protocol wording and timing adjustments permitted post-pilot under Version 1.1; permanent freeze enforced once Participant `P001` starts formal evaluation.

### E2 INSTRUMENTATION DECISION (OPTION C - HYBRID DECOUPLED):
- Explicitly compared Option A (Django-integrated), Option B (fully external), and Option C (hybrid).
- **Recommended Option C (Hybrid):** Leaves `research-prototype-v1.0` 100% frozen; tasks performed on local prototype; post-task consent and survey battery administered via external professional survey tool (Google Forms / Qualtrics) linked deterministically by `participant_code`. Eliminates software risk and preserves the 144-test baseline.

### 16 COMPLETE PROTOCOL DOCUMENTS PRODUCED (`evaluation/e1/`):
1. `E1_EVALUATION_PROTOCOL.md` (Master evaluation protocol)
2. `E1_RQ_CLAIM_EVIDENCE_MATRIX.md` (RQ to evidence mapping and permitted/prohibited claim matrix)
3. `E1_PARTICIPANT_AND_SAMPLING_PLAN.md` (Two-layer sampling plan and linkage governance)
4. `E1_TASK_SCENARIOS.md` (Standardized synthetic task set and fictional profiles Alpha & Beta)
5. `E1_TASK_CONSTRUCT_MATRIX.md` (Behavioral error taxonomy and assistance hierarchy)
6. `E1_MEASUREMENT_INSTRUMENT_SPEC.md` (Psychometric specifications for SUS, quiz, Likert, and feedback)
7. `E1_COMPREHENSION_ITEM_BANK.md` (8 objective quiz items covering domains A–H with keyed rationales)
8. `E1_ANALYSIS_PLAN.md` (Frozen statistical analysis plan and missing data rules)
9. `E1_STUDY_DATA_SCHEMA.md` (6 relational CSV data dictionaries and ERD)
10. `E1_CONSENT_DATA_GOVERNANCE_SPEC.md` (Informed consent elements and privacy disclosures)
11. `E1_ETHICS_DEPENDENCY_CHECKLIST.md` (Dual-status readiness vs authorization checklist)
12. `E1_PILOT_PLAN.md` (Small-scale feasibility pilot plan and change policy)
13. `E1_MODERATOR_GUIDE.md` (Verbatim facilitator script, orientation boundaries, and debriefing)
14. `E1_PROTOCOL_CHANGELOG.md` (Version tracking and pre-review changelog)
15. `E1_PROTOCOL_LOCK_REPORT.md` (Formal protocol lock gate signoff)
16. `E2_INSTRUMENTATION_REQUIREMENTS.md` (Phase E2 preparation backlog and survey delivery analysis)

### CRITICAL LEARNING POINT RECORDED:
> **"User evaluation does not validate predictive performance."**  
> High System Usability Scale (SUS) scores or task completion rates demonstrate effective user-interface ergonomics, workflow clarity, and low cognitive friction. They do not validate the sensitivity, specificity, calibration, or clinical diagnostic efficacy of the underlying machine learning algorithm.

---

## 37. PHASE E1.1 — PRE-REVIEW FACTUAL CORRECTION (PROTOCOL VERSION 1.0.1)

### PURPOSE:
Perform rigorous factual and terminology pre-review reconciliation across all Phase E1 evaluation protocol artifacts following an independent audit before submission to academic supervisor review. Corrects stale evaluation sample sizes, confidence intervals, and clinical terminology while preserving all experimental designs, task structures, psychometric constructs, sampling plans, and frozen code.

### PROTOCOL VERSION TRANSITION:
- **Version v1.0 Status:** `SUPERSEDED BEFORE FORMAL DATA COLLECTION`
- **Version v1.0.1 Status:** `READY FOR SUPERVISOR / INSTITUTIONAL REVIEW`
- **Correction Classification:** `FACTUAL / TERMINOLOGY CORRECTION`
- **Participant Data Status:** Zero participant data collected; zero outcomes observed.
- **Prototype Status:** Zero code changes; zero model modifications; 144/144 automated tests passing; 4 protected artifact hashes byte-identical.

### KEY CORRECTIONS AUDITED & EXECUTED:
1. **Critical Final-Test Cohort Size ($N=812$):**
   - Replaced all draft references claiming $N=1,418$ with authoritative Phase 5.1 held-out test cohort: $N = 812$ ($621$ normal-range, $191$ dysglycemia-range).
2. **ROC-AUC Confidence Interval Reconciled:**
   - Corrected frozen GAM final-test ROC-AUC 95% bootstrap confidence interval from `[0.6901, 0.7634]` to frozen Phase-5.1 value: **`[0.6875, 0.7656]`** (Point estimate: `0.7277`).
3. **Phase-5 Performance Metric Alignment:**
   - Explicitly articulated the critical sensitivity finding: *"The development-derived operating threshold targeting >=90% sensitivity achieved 86.39% sensitivity on the held-out final test. Therefore the 90% development sensitivity target was not reproduced at the final-test point estimate."*
   - Verified GAM performance baseline across documents: ROC-AUC 0.7277, PR-AUC 0.4503, Brier 0.1587, threshold 0.1389, sensitivity 86.39%, specificity 42.51%.
4. **Stage-2 Terminology Alignment:**
   - Replaced active evaluation labels such as *"Stage-2 Confirmatory Intake"* with research-safe wording: **"Stage-2 HbA1c Laboratory Assessment"**. Eliminates any implication that the dashboard or non-laboratory triage confirms a clinical diagnosis.
5. **Synthetic Case Terminology Alignment:**
   - Replaced *"patient profile"* with **"synthetic screening profile"** or **"fictional screening case"** across all task scenarios, participant orientation materials, and comprehension item stems. Reinforces that the study is a software usability/comprehension trial rather than clinical simulation.
6. **Expert Face-Validity Phrasing:**
   - Replaced overly assertive terms (*"clinical referral logic"*) with **"perceived plausibility of the screening/referral workflow"**. Reaffirmed that expert input evaluates face validity and workflow naturalness, not clinical effectiveness.
7. **Human Override Semantics Audit:**
   - Replaced *"modifies clinical referral"* with **"modifies the final human referral decision"**, emphasizing that human override alters workflow disposition without establishing clinical ground truth.

### PROTOCOL LOCK & GOVERNANCE STATUS:
- **Current Locked Protocol:** `E1-PROTOCOL-2026-V1.0.1` (Version 1.0.1)
- **Status:** READY FOR SUPERVISOR / INSTITUTIONAL REVIEW (Not yet institutionally approved or authorized for participant recruitment).
- **Formal Changelog Updated:** `evaluation/e1/E1_PROTOCOL_CHANGELOG.md`
- **Lock Signoff Report Updated:** `evaluation/e1/E1_PROTOCOL_LOCK_REPORT.md`
- **Factual Correction Report Created:** `evaluation/e1/E1_1_FACTUAL_CORRECTION_REPORT.md`

### NEXT STEPS:
- Formal Academic Supervisor Review & Faculty Ethics Submission.
- Phase E2 Instrumentation & Preparation (following institutional authorization).

---

## 38. PHASE E1.2 — INSTRUMENT & STIMULUS VALIDITY CORRECTION (PROTOCOL VERSION 1.0.2)

### PURPOSE:
Resolve remaining instrument-validity and frozen-stimulus consistency issues before pilot testing. Reconcile synthetic stimuli mathematically against the frozen inference/XAI runtime, synchronize evaluation tasks and moderator guides with exact frozen UI routes and button copy, resolve task-state workflow dependencies, adopt the validated Indonesian System Usability Scale (Sharfina & Santoso, 2016), and refine the objective comprehension battery.

### PROTOCOL VERSION TRANSITION:
- **Version v1.0.1 Status:** `SUPERSEDED BEFORE PILOT`
- **Version v1.0.2 Status:** `READY FOR PILOT REVIEW`
- **Correction Classification:** `INSTRUMENT & STIMULUS VALIDITY RECONCILIATION`
- **Participant Data Status:** Zero participant data collected; zero outcomes observed.
- **Prototype Status:** Zero code changes; zero model modifications; 144/144 automated tests passing; 4 protected artifact hashes byte-identical.

### KEY CORRECTIONS AUDITED & EXECUTED:
1. **Runtime Stimulus Mathematical Reconciliation:**
   - Case Alpha executed through frozen D2.3/D2.5 inference service: Link-scale intercept $\beta_0 = -0.729147$, linear predictor $\eta = -0.979611$, probability $\hat{p} = 0.272969$ ($27.30\%$), Recommendation: Referral Recommended (Stage 2 Indicated), Signal: Elevated Risk Signal. Top positive factor: Age (+0.418), Hypertension (+0.103), BMI (+0.005). Negative factors: Sedentary (-0.473), Waist (-0.160), Smoking (-0.118), Sex: Male (-0.027). Link reconstruction error: $0.0$.
   - Case Beta executed: Link-scale intercept $\beta_0 = -0.729147$, linear predictor $\eta = -2.850362$, probability $\hat{p} = 0.054663$ ($5.47\%$), Recommendation: Routine Monitoring (No Referral), Signal: Lower Risk Signal. Positive factors: Smoking (+0.118), Sex: Female (+0.027). Negative factors: Age (-0.785), Waist (-0.774), Sedentary (-0.345), BMI (-0.259), Hypertension (-0.103). Link reconstruction error: $2.08 \times 10^{-17}$.
   - Created comprehensive verification log: `evaluation/e1/E1_SCENARIO_RUNTIME_VERIFICATION.md`.
2. **Task State Consistency & Case Beta Preservation:**
   - Locked Task 5 strictly to **`CASE-ALPHA`** for Stage-2 HbA1c entry ($6.1\%$, Prediabetes range).
   - Preserves `CASE-BETA` in `Pending Stage-2 Assessment` status following the Task 4 override, ensuring the Task 6 audit exercise reflects realistic mixed-state queue rows on the Screening History log.
3. **Frozen UI Route & Button Copy Synchronization:**
   - Canonical screening result route updated to `/screening/<uuid>/result/` across all protocol tasks and moderator guides.
   - Exact frozen UI button copy codified: Intake submission (`Review Inputs` $\to$ `Run Screening`), XAI disclosure (`Show all 7 factors` under `Why this result?`), Human Review (`Accept Recommendation`), Override dialog (`Override Recommendation` $\to$ `Referral is preferred as a precaution` $\to$ `Confirm Override`), Stage-2 flow (`Proceed to Stage-2 HbA1c Assessment` $\to$ `Review HbA1c Value` $\to$ `Confirm Laboratory Result`), and History row navigation (`View Case`).
4. **Comprehension Battery Refinements:**
   - Removed unsupported "Validated" claim; designated as **"Protocol-Defined Objective Comprehension Battery (8 Items)"**.
   - Refined `COMP_03` (aligned with additive link-scale contributions; removed undefined "baseline" phrasing), `COMP_04` (clarified as "model input factor"), and `COMP_06` (clarified laboratory reference standard criteria).
   - Added complete verified Indonesian translations for all 8 items.
5. **Measurement Instrument Specification & Indonesian SUS:**
   - Primary evaluation language locked to **Bahasa Indonesia**.
   - Formally adopted the published, validated Indonesian SUS adaptation by **Sharfina & Santoso (2016)** (*An Indonesian adaptation of the System Usability Scale (SUS)*, IEEE ICACSIS, DOI: 10.1109/ICACSIS.2016.7872776).
   - Disentangled SUS benchmark literature: Bangor et al. (2008) overall empirical mean ($68.0$), Bangor et al. (2009) adjective rating means, and Sauro & Lewis (2016) Curved Grading Scale percentiles. Removed blanket claim that "SUS $\ge 68$ confirms acceptable software ergonomics".
   - Refined custom clarity items (`CLAR_02`, `CLAR_04`) and provided full Indonesian translations.
   - Prevention-first missing data rule codified: mandatory digital completion enforced; single-item neutral imputation (Sauro & Lewis, 2016, p. 203) restricted to emergency paper-fallback administration.
   - Designated post-study qualitative feedback analysis as "lightweight thematic/category analysis informed by Braun & Clarke (2006)".

### PROTOCOL LOCK & GOVERNANCE STATUS:
- **Current Locked Protocol:** `E1-PROTOCOL-2026-V1.0.2` (Version 1.0.2)
- **Status:** **READY FOR PILOT REVIEW** (Formal participant data collection and recruitment remain unauthorized pending pilot review and ethics clearance).
- **All 16 Evaluation Documents Updated to v1.0.2** in `evaluation/e1/`.
- **Instrument Correction Report Created:** `evaluation/e1/E1_2_INSTRUMENT_CORRECTION_REPORT.md`.

### NEXT STEPS:
- Pilot Feasibility Study Review ($N = 3\text{--}5$).
- Academic Supervisor and Faculty Ethics Committee formal submission.

---

## 39. PHASE E1.3 — FINAL CROSS-DOCUMENT STIMULUS RECONCILIATION (PROTOCOL VERSION 1.0.3)

### PURPOSE:
Resolve the remaining contradiction between `E1_SCENARIO_RUNTIME_VERIFICATION.md` and `E1_2_INSTRUMENT_CORRECTION_REPORT.md` before any pilot participant is contacted or recruited. Reconcile all representations of synthetic cases across all evaluation protocol documents against the frozen runtime evidence, establish a single canonical stimulus source of truth, expunge stale draft demographics and non-model variables, restrict task stimulus cards to the Canonical Seven Predictors, enforce frozen UI labels, audit clinical terminology, and clarify pilot/ethics sequencing.

### PROTOCOL VERSION TRANSITION:
- **Version v1.0.2 Status:** `SUPERSEDED BEFORE PILOT`
- **Version v1.0.3 Status:** `READY FOR SUPERVISOR / INSTITUTIONAL PILOT REVIEW`
- **Correction Classification:** `FINAL CROSS-DOCUMENT STIMULUS RECONCILIATION`
- **Participant Data Status:** Formal participants collected = 0; pilot participants contacted = 0.
- **Prototype Status:** Zero code changes; zero model modifications; 144/144 automated tests passing; 4 protected artifact hashes byte-identical.

### KEY ACTIONS & RECONCILIATION EXECUTED:
1. **Single Canonical Stimulus Source of Truth Created:**
   - Created `evaluation/e1/E1_STIMULUS_LOCK.md` as the exclusive cross-document authority.
   - **`CASE-ALPHA`:** Age 56, Male, BMI 31.2, Hypertension History Yes, Smoking History No, Waist 102.0 cm, Sedentary Time 480 min/day. Model linear predictor $\eta = -0.979611$, probability $\hat{p} = 0.272969$ ($27.30\%$), Recommendation: `Refer`, Signal: `Elevated Screening Signal`. Top positive: Age (+0.417980), Valid lowering factors: Sedentary Time (-0.472934), Waist Circumference (-0.159560), Smoking: Non-smoker (-0.117616), Biological Sex: Male (-0.026593). Lifecycle: Tasks 1, 2, 3, 5 (advances to Stage 2 with HbA1c 6.1% $\to$ completed Stage 2).
   - **`CASE-BETA`:** Age 32, Female, BMI 23.5, Hypertension History No, Smoking History Yes, Waist 74.0 cm, Sedentary Time 300 min/day. Model linear predictor $\eta = -2.850362$, probability $\hat{p} = 0.054663$ ($5.47\%$), Recommendation: `No Referral`, Signal: `Lower Screening Signal`. Positive factors: Smoking (+0.117616), Sex: Female (+0.026593). Negative factors: Age (-0.784738), Waist (-0.773908), Sedentary (-0.344656), BMI (-0.258779), Hypertension: No (-0.103343). Lifecycle: Tasks 4, 6 (overridden to Refer $\to$ remains in `Pending Stage-2 Assessment` at Task 6).
2. **Contradictory Stimulus Data Expunged:**
   - Eradicated stale demographic values (`58`, `27.4`, `92.0`, `34`, `21.8`, `68.0`) across all evaluation documents.
   - Removed invented non-model variables (`SBP`, `DBP`, blood pressure medication, cigarettes/day, physical activity min/week).
   - Task cards now feature **exclusively the Canonical Seven Predictors**: `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`.
3. **Canonical UI Terminology Enforced:**
   - Standardized all references to exact frozen strings: `Elevated Screening Signal`, `Lower Screening Signal`, `Refer`, `No Referral`, `Stage-2 HbA1c Laboratory Assessment`.
   - Expunged legacy design labels: *"Elevated Risk Signal"*, *"Tier 1 Positive"*, *"Routine Monitoring"*, *"Routine Check"*, *"Referral Recommended (Stage 2 Indicated)"*.
4. **Clinical Wording Audited:**
   - Replaced *"clinical persona"* with **`synthetic screening profile narrative`**.
   - Replaced *"clinical decision authority"* with **`final human referral decision authority`**.
   - Replaced *"clinical referral logic"* with **`screening/referral workflow`**.
5. **Pilot & Ethics Sequencing Codified:**
   - Explicitly declared that designation as `READY FOR PILOT REVIEW` does NOT authorize contacting pilot participants. Pilot execution may begin only after applicable supervisor and institutional ethics clearances have been satisfied.
6. **Physical Directory Suite Audit (21 Files):**
   - Corrected inaccurate suite count claims; physically audited all 21 markdown files in `evaluation/e1/`.
   - Updated `E1_PROTOCOL_LOCK_REPORT.md` and `E1_PROTOCOL_CHANGELOG.md` to reflect Version 1.0.3 across all artifacts.
   - Created `evaluation/e1/E1_3_FINAL_RECONCILIATION_REPORT.md`.

### PROTOCOL LOCK & GOVERNANCE STATUS:
- **Current Locked Protocol:** `E1-PROTOCOL-2026-V1.0.3` (Version 1.0.3)
- **Status:** **READY FOR SUPERVISOR / INSTITUTIONAL PILOT REVIEW** (Participant contact and data collection strictly unauthorized until institutional ethics clearances are obtained).
- **Automated Tests:** 144 / 144 Passing.
- **Artifact Hashes:** 4 / 4 Verified byte-identical.

---

## 40. PHASE E2 — PILOT INSTRUMENT PACKAGE, HYBRID DATA COLLECTION, & DRY-RUN VERIFICATION (VERSION 1.0)

### PURPOSE:
Prepare the complete operational package required to conduct the future 3–5 participant feasibility pilot defined in E1, without modifying the frozen research prototype (`research-prototype-v1.0`). Establish the decoupled hybrid evaluation architecture, per-session database isolation, participant-code linkage, external survey blueprint, participant-facing materials, moderator tools, CSV export templates, and execute a deterministic researcher-only dry run (`DRYRUN001`).

### KEY HIGHLIGHTS & ARCHITECTURAL DECISIONS:
1. **Hybrid Data Collection Architecture Locked:**
   - **Dashboard Web Prototype:** Acts strictly as the experimental task environment for Tasks 1–6 (`research-prototype-v1.0` remains 100% frozen).
   - **External Digital Questionnaire:** Decoupled post-task psychometric & comprehension measurement platform (Google Forms, MS Forms, or Qualtrics). Absolutely zero questionnaire models or routes inside Django.
   - **Structured Moderator Observation Sheet:** Captures task outcomes, assistance level (0–3), error taxonomy codes, and non-identifying notes.
   - **Participant Code Linkage:** Single pseudonymous linkage key (`PILOT001`, `P001`, `DRYRUN001`) tying together SQLite `HumanReview.reviewer_code`, observer sheets, survey exports, and session manifests.
2. **Per-Participant Database Isolation Strategy:**
   - Operationalized a pristine zero-state template: `evaluation/e2/runtime/db_session_template.sqlite3` (verified 0 rows in `ScreeningRecord`, `ScreeningExplanation`, `HumanReview`, `Stage2Assessment`).
   - Active session database (`dashboard/db_study.sqlite3`) is cloned from the pristine template before every participant session.
   - Post-session: database is archived to `evaluation/pilot_data/sessions/<CODE>/<CODE>_dashboard.sqlite3`, SHA-256 hash is computed and recorded in `session_manifest.csv`, and a fresh pristine template is restored.
   - History view never contains cumulative cases across participants.
3. **Pilot vs. Formal Study Separation:**
   - Pilot codes (`PILOT001`–`PILOT005`) are strictly separated from formal study codes (`P001`–`P030`).
   - Pilot data serve exclusively as feasibility evidence (clarity, timing, linkage, moderator consistency) and are **never automatically pooled** into the final formal study sample.
4. **Complete Participant-Facing Materials Created (Bahasa Indonesia):**
   - `materials/participant/E2_PARTICIPANT_INFORMATION_SHEET_ID.md` (non-clinical disclaimers, synthetic cases disclaimer, explicit governance placeholders).
   - `materials/participant/E2_CONSENT_FORM_DRAFT_ID.md` (content preparation draft with non-clinical disclaimers).
   - `materials/participant/E2_PARTICIPANT_TASK_BOOKLET_ID.md` (Tasks 1–6 instructions using frozen UI labels only; zero answer leakage, zero probabilities, zero contributor rankings).
   - `materials/participant/E2_CASE_CARD_ALPHA_ID.md` (7 canonical inputs only).
   - `materials/participant/E2_CASE_CARD_BETA_ID.md` (7 canonical inputs only).
   - `materials/participant/E2_STAGE2_CASE_ALPHA_CARD_ID.md` (HbA1c 6.1% card without range label).
   - `materials/participant/E2_OVERRIDE_SCENARIO_BETA_ID.md` (simulated override instructions with exact structured reason `"Referral is preferred as a precaution"` and note `"Individual reports unrecorded family history of early diabetes"`).
5. **Moderator Materials & Answer Keys Isolated:**
   - `materials/moderator/E2_MODERATOR_EXPECTED_STATE_KEY.md` (Master answer key with exact probabilities $0.272969$ and $0.054663$, GAM weights, lab range, and 8 comprehension keys; marked strictly `RESEARCHER / MODERATOR ONLY`).
   - `materials/moderator/E2_MODERATOR_OBSERVATION_SHEET.md` (structured observer logging sheet).
   - `materials/moderator/E2_PILOT_MODERATOR_RUNBOOK.md` (13-step operational procedure).
6. **External Questionnaire Blueprint & Privacy Hardening:**
   - `forms/E2_EXTERNAL_QUESTIONNAIRE_BLUEPRINT_ID.md` (5 sections: Code/Demographics, 8 Comprehension items v1.0.3 closed-book, 10 Indonesian SUS items from Sharfina & Santoso 2016, 5 Clarity items, 3 Open-ended feedback items).
   - `forms/E2_EXTERNAL_FORM_CONFIGURATION.md` (privacy guidelines: email collection disabled, login requirement disabled, no public charts, no immediate scoring).
7. **Complete CSV Data Schema Templates:**
   - Generated 9 clean CSV templates in `evaluation/e2/templates/` matching `E1_STUDY_DATA_SCHEMA.md` exactly: `session_manifest.csv`, `moderator_observation_template.csv`, `pilot_incident_log.csv`, `participants.csv`, `task_results.csv`, `comprehension_responses.csv`, `sus_responses.csv`, `perception_responses.csv`, `qualitative_feedback.csv`.
8. **Deterministic Researcher Dry-Run Executed (`DRYRUN001`):**
   - Executed Tasks 1–6 against `dashboard/db_dryrun.sqlite3` via `evaluation/e2/runtime/dryrun_verification.py`.
   - Verified exact inference outputs ($p = 0.272969$, $p = 0.054663$), GAM factor direction, Accept, Override, Stage-2 prediabetes range ($6.10\%$), and relational cardinality (2 records, 2 explanations, 2 reviews, 1 stage2 assessment).
   - Verified database hash (`db_dryrun.sqlite3` SHA-256: `f78d75257068327c10a4e99dde3eabfb89a09d6beaa1a9a3a2f26befe4b365fe`).
   - Verified `dashboard/db_study.sqlite3` remained 100% pristine zero-state (0 rows).
   - Verified deterministic scoring algorithms: SUS scoring formula validated ($50.0$, $100.0$, $75.0$); objective comprehension validated ($7/8$).
   - Verified code linkage: 0 unmatched files, 0 duplicate identifiers, 0 unintended PII across all 7 exported CSV files and SQLite.
9. **Pre-Pilot Authorization Gate Locked:**
   - `evaluation/e2/E2_PRE_PILOT_AUTHORIZATION_GATE.md` locked at 🔴 **NOT AUTHORIZED FOR PARTICIPANT CONTACT** pending supervisor and institutional ethics approvals.

### KEY LEARNING POINTS:
- *"The evaluation instrument is separate from the experimental dashboard."*
- *"Pilot data are feasibility data and must not silently enter the final study sample."*

### CURRENT GOVERNANCE STATUS:
- **E2 Package Version:** `1.0`
- **Protocol Baseline:** `E1-PROTOCOL-2026-V1.0.3` (v1.0.3)
- **Software Target:** `research-prototype-v1.0` (FROZEN)
- **Human Participant Contact:** 🔴 **NOT YET AUTHORIZED** (Awaiting formal institutional review & supervisor approval).
- **Automated Tests:** 144 / 144 Passing.
- **Protected Hashes:** 4 / 4 Verified byte-identical.

### NEXT PHASE:
- Formal submission of E2 operational package to Academic Supervisor and Faculty Ethics Review.
- Transition gate to `AUTHORIZED FOR PILOT CONTACT` upon receipt of written clearances.
- Pilot execution ($N = 3\text{--}5$) following `E2_PILOT_MODERATOR_RUNBOOK.md`.




