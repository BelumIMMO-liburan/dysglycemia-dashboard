# Stage-2 Presentation Specification — UI/UX & Information Architecture

## 1. Primary Design Principles
1. **Restrained Clinical Tone:** High contrast, accessible typography, muted neutrals, and semantic border accents rather than alarmist red/green diagnostic badges.
2. **Two-Stage Workflow Visibility:** Visual timeline clearly separates Stage-1 Non-Laboratory Screening, Human Review Decision, and Stage-2 Laboratory Assessment.
3. **Transparent Epistemic Role:** HbA1c is presented as an objective laboratory measurement categorized by standard clinical reference ranges, accompanied by mandatory diagnostic confirmation notices.
4. **Zero Confusion with Machine Learning:** Stage-2 displays contain no probabilities, model bars, or AI badges.

---

## 2. Two-Stage Workflow Timeline Component
Displayed prominently on Screening Result, Stage-2 Entry, Review, and Result views:

```
[✓ Stage 1: Non-Lab Screening] ─── [✓ Human Review] ─── [● Stage 2: HbA1c Lab Assessment]
```

### Visual Step States
- **Completed:** Green circular badge with checkmark (`✓`), 600-weight title, concise status summary.
- **Current / In Progress:** Primary blue or warning amber circular badge with solid dot (`●`), highlighted label.
- **Unavailable / No Referral:** Muted circle with dash (`—`), explanatory note ("Unavailable (No Referral)").
- **Pending Prior Step:** Muted circle with hollow dot (`○`), "Awaiting Review Decision".

---

## 3. Stage-2 Result Card Layout
Complies with Section 22 specification:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 2 · HbA1c Laboratory Assessment             [ Prediabetes-range ]│
│                                                                        │
│ ENTERED HbA1c                                                          │
│ 6.10%                                                                  │
│                                                                        │
│ LABORATORY RANGE CATEGORY                                              │
│ Prediabetes-range                                                      │
│                                                                        │
│ Entered HbA1c falls within the 5.7% to <6.5% laboratory range.         │
│                                                                        │
│ ℹ Diagnostic Confirmation Notice                                       │
│ This range presentation is not an automated diagnosis. In the absence   │
│ of unequivocal hyperglycemia, clinical diagnosis generally requires    │
│ appropriate confirmatory testing. This prototype does not evaluate      │
│ whether confirmation has occurred.                                     │
│                                                                        │
│ Reference Standard: ADA Standards of Care in Diabetes — 2026          │
│ Reference Rule Identifier: ADA_2026_A1C_RANGE_V1                       │
│ Confirmed Timestamp: 05 September 2026 · 07:41 UTC                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Range-Specific Copy Rules

| Range Code | Display Title | Permitted Context Copy | Prohibited Language |
| :--- | :--- | :--- | :--- |
| `normal_range` | **Normal-range** | *"Entered HbA1c falls below the 5.7% prediabetes-range threshold."* | "You are healthy", "Negative", "Normal therefore safe" |
| `prediabetes_range` | **Prediabetes-range** | *"Entered HbA1c falls within the 5.7% to <6.5% laboratory range."* | "You have prediabetes", "Prediabetic condition confirmed" |
| `diabetes_range` | **Diabetes-range** | *"Entered HbA1c falls within the ≥6.5% laboratory range used in diabetes diagnostic criteria. This prototype does not establish a diagnosis; clinical diagnosis may require confirmatory testing and additional clinical context."* | "You have diabetes", "Diabetes confirmed", "Positive for diabetes" |

---

## 5. Lineage & Back-Reference Architecture
The Stage-2 result page embeds a dedicated **Two-Stage Cascade Lineage** card:
- Stage-1 Screening Signal (Elevated / Lower, p = 0.XXXX)
- Stage-1 AI Referral Recommendation
- Human Review Decision (Accepted / Overridden by Reviewer Code)
- Stage-2 Laboratory Range Category and entered value

This guarantees that the user understands the exact sequence of evidence without collapsing different epistemic steps into a singular "Final Diagnosis".
