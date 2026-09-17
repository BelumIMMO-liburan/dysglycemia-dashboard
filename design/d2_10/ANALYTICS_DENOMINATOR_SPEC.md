# Research Analytics Denominator & Metric Specification

**Phase:** D2.10 — Research Analytics + Human–AI Decision Flow  
**Module:** `dashboard/predictor/services/research_analytics.py`  
**Authoritative Scope:** Authoritative relational entities (`ScreeningRecord`, `ScreeningExplanation`, `HumanReview`, `Stage2Assessment`). Legacy entities (`Prediction`, `Override`) strictly excluded.

---

## 1. Core Denominator Philosophy
Under research governance, a percentage rate is never computed merely because two counts exist in the database. Every metric requires an explicit, methodologically justified numerator, denominator, eligible population, undefined handling condition, valid clinical decision-support interpretation, and strictly prohibited misinterpretations.

---

## 2. Complete Metric Specification Ledger

| Metric | Numerator | Denominator | Eligible Population | Display Format | Undefined Condition | Valid Interpretation | Prohibited Misinterpretations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Screenings** | Count of records | None (Absolute Count) | All active `ScreeningRecord` rows matching optional date filter | Integer (`N`) | Never undefined (returns `0`) | Total intake volume recorded in the research prototype. | Patient volume, epidemiological cohort size. |
| **AI Referral Rate** | `ai_referral_recommended == True` | Total Screenings ($N_{\text{screenings}}$) | All active `ScreeningRecord` rows | Percentage (`0.0%`) with subtitle `X of Y` | $N_{\text{screenings}} = 0 \rightarrow \text{None}$ ("Not available") | Fraction of non-laboratory intakes that cross the frozen Stage-1 operating threshold ($\ge 0.1389$). | Disease prevalence, true dysglycemia rate, clinical positive rate, machine diagnostic accuracy. |
| **Explanation Availability Rate** | `explanation__status == 'generated'` | Total Screenings ($N_{\text{screenings}}$) | All active `ScreeningRecord` rows | Percentage (`0.0%`) with count subtitle | $N_{\text{screenings}} = 0 \rightarrow \text{None}$ ("Not available") | Operational completeness of the additive feature contribution service. | XAI explanation truth, feature importance correctness (fidelity is verified by D2.5 unit tests). |
| **Review Completion Rate** | Completed `HumanReview` count | Review-Eligible Screenings ($N_{\text{review\_eligible}}$) | `ScreeningRecord` with `explanation.status == 'generated'` | Percentage (`0.0%`) with count subtitle | $N_{\text{review\_eligible}} = 0 \rightarrow \text{None}$ ("Not available") | Research protocol compliance: fraction of protocol-eligible cases evaluated by clinical reviewer. | Clinical triage speed, reviewer productivity benchmark. |
| **Human–AI Agreement Rate** | `review_action == 'accepted'` | Reviewed Screenings ($N_{\text{reviewed}}$) | Screenings with finalized `HumanReview` | Percentage (`0.0%`) with count subtitle | $N_{\text{reviewed}} = 0 \rightarrow \text{None}$ ("Not available") | Decision concordance: proportion of reviewed cases where final human referral disposition equals machine recommendation. | **AI accuracy, model correctness, human validation rate, true positive concordance.** |
| **Human Override Rate** | `review_action == 'overridden'` | Reviewed Screenings ($N_{\text{reviewed}}$) | Screenings with finalized `HumanReview` | Percentage (`0.0%`) with count subtitle | $N_{\text{reviewed}} = 0 \rightarrow \text{None}$ ("Not available") | Clinician decision modification: proportion of reviewed cases where final human referral decision diverged from machine recommendation. | **AI error rate, machine mistake rate, clinician error, algorithm failure rate.** |
| **Final Human Referral Rate** | `final_referral_recommended == True` | Reviewed Screenings ($N_{\text{reviewed}}$) | Screenings with finalized `HumanReview` | Percentage (`0.0%`) with count subtitle | $N_{\text{reviewed}} = 0 \rightarrow \text{None}$ ("Not available") | Clinical referral disposition: fraction of reviewed screenings authorized for Stage-2 laboratory diagnostic evaluation. | True positive fraction, disease prevalence in reviewed sample. |
| **Stage-2 Completion Rate** | Completed `Stage2Assessment` count | Eligible Referrals ($N_{\text{stage2\_eligible}} = N_{\text{final\_refer}}$) | Authorizing human referrals (`final_referral_recommended == True`) | Percentage (`0.0%`) with count subtitle | $N_{\text{stage2\_eligible}} = 0 \rightarrow \text{None}$ ("Not available") | Laboratory follow-up adherence: fraction of clinically referred participants who completed venous HbA1c testing. | Whole-workflow participant retention (non-referred cases are correctly terminal). |
| **Observed Normal-Range Fraction** | `laboratory_range == 'normal_range'` ($<5.7\%$) | Completed Stage-2 Assessments ($N_{\text{stage2\_completed}}$) | Records with verified `Stage2Assessment` | Percentage (`0.0%`) with count subtitle | $N_{\text{stage2\_completed}} = 0 \rightarrow \text{None}$ ("Not available") | Proportion of completed laboratory tests falling below prediabetes threshold within the referred sub-cohort. | False positive rate, model specificity, population euglycemia prevalence. |
| **Observed Prediabetes-Range Fraction** | `laboratory_range == 'prediabetes_range'` ($5.7\%\text{ to }<6.5\%$) | Completed Stage-2 Assessments ($N_{\text{stage2\_completed}}$) | Records with verified `Stage2Assessment` | Percentage (`0.0%`) with count subtitle | $N_{\text{stage2\_completed}} = 0 \rightarrow \text{None}$ ("Not available") | Proportion of completed laboratory tests falling in ADA prediabetes range within the referred sub-cohort. | Prediabetes prevalence in general population. |
| **Observed Diabetes-Range Fraction** | `laboratory_range == 'diabetes_range'` ($\ge 6.5\%$) | Completed Stage-2 Assessments ($N_{\text{stage2\_completed}}$) | Records with verified `Stage2Assessment` | Percentage (`0.0%`) with count subtitle | $N_{\text{stage2\_completed}} = 0 \rightarrow \text{None}$ ("Not available") | Proportion of completed laboratory tests meeting laboratory threshold for diabetes diagnostic criteria within the referred sub-cohort. | Population diabetes prevalence, positive predictive value (PPV), true positive rate. |
| **Override Away Direction Rate** | AI Refer $\rightarrow$ Human No Refer | Total Overridden Reviews ($N_{\text{overridden}}$) | Reviews with `review_action == 'overridden'` | Percentage (`0.0%`) with count subtitle | $N_{\text{overridden}} = 0 \rightarrow \text{None}$ ("Not available") | Proportion of overrides where human reviewer filtered out an AI-flagged referral. | Clinician skepticism rate, false alarm correction rate. |
| **Override Toward Direction Rate** | AI No Refer $\rightarrow$ Human Refer | Total Overridden Reviews ($N_{\text{overridden}}$) | Reviews with `review_action == 'overridden'` | Percentage (`0.0%`) with count subtitle | $N_{\text{overridden}} = 0 \rightarrow \text{None}$ ("Not available") | Proportion of overrides where human reviewer initiated a referral not flagged by AI. | Clinician sensitivity correction, missed case recovery rate. |
| **Structured Reason Rates** | Specific structured reason code count | Override Direction Total ($N_{\text{override\_away}}$ or $N_{\text{override\_toward}}$) | Overrides within corresponding branch | Percentage (`0.0%`) with count subtitle | Branch total $= 0 \rightarrow \text{None}$ ("—") | Relative prevalence of standardized clinician rationale within override branch. | Universal clinician sentiment, causal justification. |

---

## 3. Mathematical Invariant Requirements
The service guarantees the following mathematical identities across all queries:
1. $N_{\text{accepted}} + N_{\text{overridden}} == N_{\text{reviewed}}$
2. If $N_{\text{reviewed}} > 0$: $\text{Agreement Rate} + \text{Override Rate} \approx 100.0\%$ (exact count sum is $1.0$).
3. $\sum(\text{Transition Matrix Cells}) == N_{\text{reviewed}}$
4. $\text{Transition Diagonal Sum} == N_{\text{accepted}}$
5. $\text{Transition Off-Diagonal Sum} == N_{\text{overridden}}$
6. $N_{\text{stage2\_completed}} \le N_{\text{stage2\_eligible}}$
7. $N_{\text{normal}} + N_{\text{prediabetes}} + N_{\text{diabetes}} == N_{\text{stage2\_completed}}$
8. $\sum(\text{Structured Reasons within Branch}) == N_{\text{branch\_overrides}}$
