# Human Review & Override Interaction Design

**Phase:** D1 — Design Foundation  
**Workflow:** Clinical Oversight, Referral Disposition, and Override Governance  
**Date:** 2026-09-04  

---

## 1. Theoretical Foundation: Reviewing Referral, Not Biology

A critical conceptual error identified in early CDSS prototypes is allowing clinicians to "override" the AI's prediction of a patient's biological state (e.g., flipping a prediction from "Diabetic" to "Not Diabetic"). A patient's underlying glycemic pathology cannot be altered by administrative fiat.

In this research prototype:
1. **The System Outputs:** A **Screening Signal** (Elevated vs Non-Elevated) and an automated **Referral Recommendation** (*"Refer for Stage-2 Confirmatory HbA1c"*).
2. **The Human Reviews:** The **Referral Recommendation**, synthesizing automated evidence with real-world patient history, co-morbidities, and clinical context.
3. **The Human Decides:** The **Referral Disposition** (*"Confirm Referral"* vs *"Decline Referral"* vs *"Deferred / Repeat Assessment"*).

Under no circumstance is the AI's calculated screening score or probability modified. The database preserves both the machine's initial inference and the clinician's subsequent clinical action.

---

## 2. Decision Taxonomy for Research Variables

To generate clean, publishable research data for the thesis, the human review outcomes are standardized into three discrete clinical dispositions:

| Human Decision Code | Label in Interface | Clinical Definition | Research Variable Value |
| :--- | :--- | :--- | :--- |
| `REFER_CONFIRMED` | **Confirm Referral for Stage-2 HbA1c** | Clinician agrees that venous laboratory testing is clinically indicated. Case advances to the Stage-2 Intake queue. | Concordant (if AI Elevated) / Discordant-Elevated (if AI Non-Elevated) |
| `REFER_DECLINED` | **Decline Referral at this Time** | Clinician decides that laboratory testing is not indicated (e.g., recent normal lab exists, or patient is in palliative care). Case is closed without Stage-2. | Discordant-Overridden (if AI Elevated) / Concordant (if AI Non-Elevated) |
| `ASSESS_REPEAT` | **Repeat Screening / Defer Decision** | Clinician suspects transient acute condition (e.g., severe temporary illness affecting sedentary time) and orders re-screening in 30 days. | Deferred-Indeterminate |

---

## 3. The Guided Review Workspace Layout

The review interface is positioned directly below the Factor Explanation (XAI) breakdown, enforcing the principle that **explanation precedes override**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  CLINICIAN GUIDED REVIEW                                                                    │
│  Case #1048 · Intake: 2026-09-04 12:45 UTC                                                  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  System Screening Signal:           [▲] ELEVATED (Probability: 24.7% vs Floor: 13.9%)       │
│  System Recommendation:             REFER FOR STAGE-2 HbA1c ASSESSMENT                      │
│                                                                                             │
│  Primary Contributing Factors:      Waist (+0.482), Age (+0.341), BMI (+0.289)             │
│                                                                                             │
│  ┌─ DISPOSITION SELECTION ───────────────────────────────────────────────────────────────┐  │
│  │                                                                                       │  │
│  │  [ ✔ Accept Recommendation ]                       [ ✖ Override Recommendation ]      │  │
│  │  Confirm Stage-2 HbA1c referral.                   Decline or modify referral based   │  │
│  │  Advances case to laboratory queue.                on documented clinical context.    │  │
│  │                                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  Logged Reviewer: Dr. F. Susanto (Session: REV-8821)                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Structured Override Dialog (`AlertDialog` Pattern)

Clicking `[ ✖ Override Recommendation ]` opens an accessible, high-friction modal dialog. The modal prevents accidental overrides and enforces structured data entry:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Confirm Clinical Override · Case #1048                                                [✕]  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  You are overriding the automated referral recommendation.                                  │
│  Please document your clinical justification for the research record.                       │
│                                                                                             │
│  ┌─ RECOMMENDATION COMPARISON ───────────────────────────────────────────────────────────┐  │
│  │ System Recommendation:     [ Refer for Stage-2 HbA1c ]  (Elevated Signal, p=24.7%)     │  │
│  │ Human Decision:            [ Decline Referral at this Time ]                          │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  PRIMARY CLINICAL REASON (Required):                                                        │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ [ Select standardized clinical justification...                                    ▼ ]│  │
│  │ ├─ Recent documented normal HbA1c (< 30 days)                                         │  │
│  │ ├─ Severe frailty / limited clinical utility of screening                             │  │
│  │ ├─ Acute confounding medical illness or medication                                     │  │
│  │ ├─ Patient declines venous blood collection after counseling                          │  │
│  │ └─ Alternative clinical management pathway indicated                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  CLINICAL NOTES & RATIONALE (Required):                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Patient had normal HbA1c (5.2%) on Aug 18, 2026. Glycemic testing not indicated at   │  │
│  │ present time. Follow-up scheduled for routine annual review.                          │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  Reviewer Identity: Dr. F. Susanto (Logged Session ID: REV-8821)                            │
│                                                                                             │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  [ Cancel ]                                                  [ Confirm & Log Override ]     │
│  (Secondary Outline)                                         (Brand Solid Action)           │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Audit Trail & Data Model Specification

When an override is confirmed, the system creates an immutable record in the `ClinicalReview` database table:

```python
# Conceptual Schema for Phase D2 Implementation
class ClinicalReview(models.Model):
    screening = models.ForeignKey(ScreeningSession, on_delete=models.CASCADE, related_name='reviews')
    review_timestamp = models.DateTimeField(auto_now_add=True)
    reviewer_id = models.CharField(max_length=100)
    reviewer_name = models.CharField(max_length=200)
    
    # Review Disposition
    decision = models.CharField(
        max_length=20,
        choices=[
            ('accept', 'Accepted AI Recommendation'),
            ('override_decline', 'Overridden: Declined Referral'),
            ('override_refer', 'Overridden: Ordered Referral'),
            ('defer', 'Deferred: Repeat Assessment'),
        ]
    )
    
    # Structured Justification (Mandatory on override)
    primary_reason_code = models.CharField(max_length=50, blank=True)
    clinical_notes = models.TextField(blank=True)
    
    # Audit Preservation (Snapshots state at time of review)
    ai_recommendation_snapshot = models.CharField(max_length=50)
    ai_probability_snapshot = models.FloatField()
```

### Safety & Governance Guarantees
1. **Never Silently Invert Machine Output:** `screening.ai_probability` and `screening.ai_signal` are completely immutable.
2. **Deterministic Validation:** The modal form cannot be submitted if either `primary_reason_code` or `clinical_notes` is empty.
3. **Multi-Review Handling:** If multiple clinicians review the same case, each review is appended as a new row in `ClinicalReview`. The UI shows the latest review status while displaying the complete chronological review log in the Case Detail view.
