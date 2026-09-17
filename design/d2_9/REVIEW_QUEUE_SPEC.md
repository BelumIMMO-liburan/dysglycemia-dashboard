# Screening Review Queue Specification (Phase D2.9)

## 1. Executive Purpose
The Review Queue (`/review/`) provides an actionable operational workspace answering the primary clinical workflow question:
> **"What action is currently required for this screening case?"**

The Review Queue surfaces **actionable cases only**. Fully completed cases and non-referred screenings are recorded in the permanent audit history and excluded from the queue.

---

## 2. Queue Partitioning & Inclusion Rules

The Review Queue is structured into two primary actionable sections accessible via tabbed navigation, plus a restrained system attention section:

### Section A: Pending Human Review (`tab=review`)
- **Inclusion Criteria:**
  1. `ScreeningRecord` exists.
  2. `ScreeningExplanation.status == 'generated'` (verified additive fidelity).
  3. `HumanReview` is absent.
- **Displayed Fields:**
  - `Screening ID`: Truncated UUID prefix linking to case result.
  - `Created Timestamp`: Formatting in UTC.
  - `Screening Signal`: Muted semantic badge (`Elevated` or `Lower`).
  - `AI Recommendation`: Text summary (`Refer` or `Do not refer`).
  - `Calculated Probability`: Display percentage at locked threshold (0.1389).
  - `Workflow Status`: `Pending Review`.
- **Authoritative Action:** `[ Review ]` button linking to `/screening/<uuid>/result/`.
  - The screening result page remains the authoritative surface for Human Review and Override.

### Section B: Pending Stage 2 (`tab=stage2`)
- **Inclusion Criteria:**
  1. `HumanReview` finalized with `final_referral_recommended == True`.
  2. `Stage2Assessment` is absent.
- **Displayed Fields:**
  - `Screening ID`: Truncated UUID prefix.
  - `Reviewed Timestamp`: Review finalization timestamp.
  - `AI Recommendation`: Original baseline recommendation.
  - `Review Action`: `Accepted` or `Overridden`.
  - `Final Human Decision`: `Refer`.
  - `Stage-2 Status`: `Pending`.
- **Authoritative Action:** `[ Enter HbA1c ]` button linking to `/screening/<uuid>/stage2/`.

### Section C: Needs System Attention (`attention_cases`)
- **Inclusion Criteria:** `ScreeningExplanation` missing or `status == 'failed'`, or relational integrity warning detected.
- **Display Treatment:** Restrained warning card at the top or bottom of the queue.
- **Epistemic Guard:** Human review is locked. The UI explicitly informs reviewers that XAI generation failures cannot be manually bypassed.

---

## 3. Exclusion Rules
The Review Queue strictly omits non-actionable records:
1. Cases with finalized `HumanReview` where `final_referral_recommended == False` (reviewed; no further action required).
2. Cases where `Stage2Assessment` is completed (two-stage cascade finished).
3. Legacy `Prediction` and `Override` records from early thesis phases.

---

## 4. Empty State Copy & Dignity
Empty states provide honest, neutral operational status:
- **Pending Review Empty:** *"No screenings are currently awaiting Human Review."*
- **Pending Stage 2 Empty:** *"No referred screenings are currently awaiting Stage-2 HbA1c assessment."*
- **Prohibited:** Celebratory or gamified language (no fireworks, confetti, or "Great job!").

---

## 5. Architectural Authority & Safety
Queue action links are purely navigational. All underlying server-side gate validations remain authoritative:
- A reviewer clicking `[ Review ]` cannot review a case if explanations are missing (enforced by `accept_review_view` and `override_review_view`).
- A user navigating directly to `/stage2/` cannot enter HbA1c for a non-referred case (enforced by `stage2_view`).
