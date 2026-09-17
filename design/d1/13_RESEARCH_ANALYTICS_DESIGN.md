# Research & Operational Analytics Specification

**Phase:** D1 — Design Foundation  
**Audience:** Clinical Supervisors, Principle Investigators, and Quality Auditors  
**Design Principle:** Clear Research Questions, No Vanity Metrics, No Conflating Agreement with Accuracy  
**Date:** 2026-09-04  

---

## 1. Executive Summary & Governance Boundaries

The Analytics view (`/analytics/`) is an administrative and quality-surveillance portal designed to monitor system throughput, human-AI concordance, override patterns, and confirmatory laboratory yield. 

### Methodological Guardrails
1. **Never Label Concordance as "Accuracy":** Early CDSS prototypes frequently commit the fatal error of labeling Clinician-AI agreement as "AI accuracy". Concordance merely reflects agreement between two decision-makers, both of whom may be mistaken.
2. **True Accuracy Requires Stage-2 Laboratory Verification:** Empirical diagnostic performance (True Positive, False Positive, Positive Predictive Value) can only be evaluated on the subset of participants who complete Stage-2 confirmatory venous HbA1c testing.
3. **Rigorous Denominator Integrity:** Override rates must be calculated strictly against **reviewed cases**, completely avoiding the denominator flaw present in the legacy dashboard (`overrides / total_intakes`).

---

## 2. Quantitative Metric Catalog

| Metric Identifier | Label in Interface | Mathematical Definition | Explicit Research Question Answered |
| :--- | :--- | :--- | :--- |
| `M1_TOTAL_INTAKE` | **Total Screenings** | $N_{\text{total}}$ | What is the total volume of participants evaluated through Stage-1 screening? |
| `M2_REVIEW_STATUS` | **Review Throughput** | $N_{\text{reviewed}} \text{ vs } N_{\text{pending}}$ | How efficiently is the clinical team processing pending screening cases? |
| `M3_AI_REFERRAL_RATE` | **AI Referral Rate** | $\frac{N_{\text{AI\_elevated}}}{N_{\text{total}}} \times 100$ | What proportion of the intake cohort produces an elevated screening signal at the $0.1389$ threshold? |
| `M4_CONCORDANCE_RATE` | **Human-AI Concordance Rate** | $\frac{N_{\text{accepts}}}{N_{\text{reviewed}}} \times 100$ | How often do expert clinicians agree with the automated screening referral recommendation? |
| `M5_OVERRIDE_RATE` | **Clinical Override Rate** | $\frac{N_{\text{overrides}}}{N_{\text{reviewed}}} \times 100$ | What percentage of automated recommendations are overturned by human clinical judgment? |
| `M6_STAGE2_COMPLETION` | **Stage-2 Completion Rate** | $\frac{N_{\text{completed\_lab}}}{N_{\text{referred}}} \times 100$ | What percentage of referred participants successfully complete venous HbA1c testing? |
| `M7_STAGE2_YIELD` | **Confirmatory Dysglycemia Yield** | $\frac{N_{\text{HbA1c} \ge 5.7\%}}{N_{\text{completed\_lab}}} \times 100$ | What percentage of referred and tested individuals have clinically verified dysglycemia (Positive Predictive Value of the two-stage protocol)? |

---

## 3. Structured Research Visualizations (Exactly 3 Focused Charts)

To avoid cognitive overload and dashboard clutter, the analytics view contains exactly three charts, each mapping to a fundamental research question:

### Chart 1: Clinician-AI Concordance & Disposition Waterfall
- **Research Question:** *"How are automated screening referrals handled by reviewing clinicians?"*
- **Chart Type:** Horizontal Segmented Bar / Waterfall
- **Data Series:**
  - AI Recommended Referral $\rightarrow$ Clinician Accepted ($N, \%$)
  - AI Recommended Referral $\rightarrow$ Clinician Overrode / Declined ($N, \%$)
  - AI Non-Elevated Signal $\rightarrow$ Clinician Accepted Routine Care ($N, \%$)
  - AI Non-Elevated Signal $\rightarrow$ Clinician Overrode / Ordered Referral ($N, \%$)

### Chart 2: Primary Clinical Justifications for Override
- **Research Question:** *"What real-world clinical factors cause clinicians to overturn the automated recommendation?"*
- **Chart Type:** Clean Horizontal Bar Chart (Ranked Frequency)
- **Categories:**
  1. *Recent documented normal HbA1c within 30 days*
  2. *Severe frailty / limited clinical utility of screening*
  3. *Acute confounding medical condition or steroid therapy*
  4. *Patient refusal after counseling*
  5. *Alternative clinical management indicated*

### Chart 3: Confirmatory Stage-2 Glycemic Stratification (Empirical Yield)
- **Research Question:** *"Among referred participants who completed laboratory testing, what is the clinical distribution of venous HbA1c?"*
- **Chart Type:** Stacked Distribution Bar
- **Clinical Tiers:**
  - **Normal Glycemia** ($\text{HbA1c} < 5.7\%$): False Positives of Stage-1 screening.
  - **Prediabetes Range** ($5.7\% \le \text{HbA1c} \le 6.4\%$): True Positives (Early detection opportunity).
  - **Undiagnosed Diabetes** ($\text{HbA1c} \ge 6.5\%$): True Positives (High-acuity clinical finding).

---

## 4. UI Layout & Visual Rhythm

The Analytics layout uses the standard `shadcn/ui` Card and Metric hierarchy:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Research Analytics & Clinical Surveillance                                 [ Export CSV ]  │
│  Continuous operational audit of screening volume, concordance, and laboratory yield.       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─ TOTAL INTAKE ──────┐  ┌─ REFERRAL RATE ──────┐  ┌─ CONCORDANCE RATE ───┐  ┌─ STAGE 2 YIELD ───────┐  │
│  │ 184 Screenings      │  │ 34.2% (63/184)       │  │ 91.8%                │  │ 74.4%                 │  │
│  │ 100% Non-Lab inputs │  │ At locked 0.1389     │  │ Reviewed cases       │  │ Confirmed Dysglycemia │  │
│  └─────────────────────┘  └──────────────────────┘  └──────────────────────┘  └───────────────────────┘  │
│                                                                                             │
│  ┌─ CHART 1: CLINICIAN DISPOSITION FLOW ──────────────────────────────────────────────────┐  │
│  │ AI Referral Accepted by Clinician:        [===========================>       ]  88.9% │  │
│  │ AI Referral Overridden (Declined):        [===>                               ]  11.1% │  │
│  └────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  ┌─ CHART 2: OVERRIDE REASONS (N = 5) ─────────┐  ┌─ CHART 3: STAGE-2 CONFIRMED YIELD ────────┐  │
│  │ • Recent Normal Lab:             3 (60.0%)  │  │ [■ Normal: 11] [■ Prediab: 24] [■ Diab: 8]│  │
│  │ • Severe Frailty:                1 (20.0%)  │  │ Total Completed: 43 laboratory tests      │  │
│  │ • Patient Refusal:               1 (20.0%)  │  │ True Positive Yield: 74.4% (32/43)        │  │
│  └─────────────────────────────────────────────┘  └───────────────────────────────────────────┘  │
│                                                                                             │
│  [i] Methodology Note: Concordance reflects human-algorithm agreement. Statistical          │
│      sensitivity and specificity calculations are reserved for Stage-2 laboratory cohorts.  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```
