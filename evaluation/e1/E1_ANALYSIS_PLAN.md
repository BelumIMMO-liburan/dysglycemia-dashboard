# Statistical & Qualitative Analysis Plan (Phase E1)
## Frozen Analytical Procedures for User Evaluation Data

**Document Identifier:** `E1-ANALYSIS-PLAN-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Analysis Philosophy & Epistemic Restraint

This analysis plan is **frozen prior to participant data collection**. It establishes the exact statistical techniques, aggregation rules, and qualitative coding methods that will be applied to the evaluation data.

### Core Principles:
1. **Descriptive Primacy:**  
   The primary quantitative approach is rigorous descriptive statistics (frequencies, percentages, means, standard deviations, medians, and interquartile ranges). For an undergraduate prototype usability evaluation ($N = 24\text{--}30$), descriptive reporting provides authentic, reproducible findings without inflating small-sample statistical tests.
2. **No Post-Hoc Hypothesis Invention:**  
   Hypothesis tests (e.g., inferential p-values comparing subgroups) **MUST NOT** be retroactively conducted simply because a difference appears in the observed dataset.
3. **Statistical Software Environment:**  
   Analyses will be performed using **Python 3.10** with `pandas (>=2.0.0)`, `numpy (>=1.24.0)`, and `scipy (>=1.10.0)`. Scripts will be archived in the thesis repository for complete computational reproducibility.

---

## 2. Primary Usability Analysis (RQ3)

### 2.1 System Usability Scale (SUS) Metrics
- **Dataset:** Valid completed responses to the 10 Indonesian-adapted SUS items ($N = 24\text{ to }30$).
- **Tabulated Metrics:**
  - Sample size ($N$)
  - Mean ($\mu_{\text{SUS}}$) and Standard Deviation ($\sigma_{\text{SUS}}$)
  - Median and Interquartile Range ($\text{IQR} = Q_3 - Q_1$)
  - Minimum and Maximum observed scores
  - 95% Confidence Interval for the mean: $\bar{x} \pm t_{0.975, n-1} \times \frac{s}{\sqrt{n}}$
- **Benchmark Interpretation (Explicit Literature Attribution):**
  - SUS scores will be described relative to explicitly cited benchmark and adjective-rating reference distributions:
    - *Empirical Benchmark Mean:* Bangor et al. (2008) reported an empirical cross-study mean of **68.0** ($SD \approx 12.5$) across 2,324 evaluations.
    - *Adjective Reference Means:* Bangor et al. (2009) established empirical mean scores observed for subjective adjective rating categories:
      - Poor: $\text{Mean} \approx 35.7$
      - OK: $\text{Mean} \approx 50.9$
      - Good: $\text{Mean} \approx 71.4$
      - Excellent: $\text{Mean} \approx 85.5$
      *(Note: These values reflect empirical category means from literature distributions, not rigid universal categorical cut-points).*
    - *Percentile Context:* Sauro & Lewis (2016) note that a score of 68 aligns approximately with the 50th percentile rank across software studies.
- **Scientific Boundary:** The study will **NOT** claim that "SUS $\ge 68$ confirms acceptable software ergonomics" or validates clinical acceptability. The thesis will neutrally describe where the prototype's mean score falls relative to published empirical reference distributions.

### 2.2 Task Performance & Error Metrics
- **Task Success Rate:**
  $$\text{Success Rate}_k = \frac{\sum_{i=1}^{N} \text{task\_success}_{i,k}}{N} \times 100\%$$
  Tabulated separately for Task 1 through Task 6.
- **Assistance Level Distribution:**
  Frequency and percentage breakdown of assistance levels ($0, 1, 2, 3$) per task.
- **Error Taxonomy Breakdown:**
  Frequencies of observed error types (navigation errors, input errors, modal cancellations, interpretation errors).
- **Optional Task Duration:**
  Reported via Median and IQR in seconds. Task duration is strictly an exploratory ergonomic indicator, not a measure of clinical speed.

---

## 3. Primary Comprehension Analysis (RQ4)

### 3.1 Total Comprehension Score
- **Metric Formulation:** Sum of correct responses across the 8 objective items:
  $$S_{\text{comp}} = \sum_{j=1}^{8} \text{correct}_j, \quad S_{\text{comp}} \in [0, 8]$$
- **Reported Descriptive Statistics:**
  - Mean, Standard Deviation, Median, IQR, Minimum, Maximum.

### 3.2 Item-Level Difficulty & Error Patterns
- **Item Correctness Rate:**
  $$P_j = \frac{\sum_{i=1}^{N} \text{correct}_{i,j}}{N} \times 100\%$$
- **Error Pattern Identification:**
  Tabulation of distractor selection frequencies. Items with $P_j < 70\%$ will be highlighted in the thesis discussion as specific mental-model misalignment areas requiring future interface refinement.
- **Prohibited Claim:** Total score **MUST NEVER** be phrased as "X% explainability effectiveness."

---

## 4. Custom Exploratory Likert Analysis

- **Items:** `CLAR_01` through `CLAR_05` (5-point Likert).
- **Permitted Tabulation:**
  - Item frequency distribution: Count and percentage selecting Strongly Disagree (1), Disagree (2), Neutral (3), Agree (4), Strongly Agree (5).
  - Central tendency: Median and IQR per item.
- **Strict Prohibition:** Individual items **MUST NOT** be averaged into a composite total score or treated as interval-scale measurements.

---

## 5. Qualitative Feedback Analysis

- **Items:** `QUAL_01`, `QUAL_02`, `QUAL_03` free-text responses.
- **Methodology:** **Lightweight thematic/category analysis informed by Braun & Clarke (2006)**.
  1. *Familiarization:* Reading all participant open-ended comments in their original language.
  2. *Pragmatic Categorization:* A single investigator tags recurring interface friction points and cognitive ambiguities (e.g., chart terminology, button clarity, review confidence).
  3. *Category Consolidation:* Grouping codes into practical UX refinement categories for discussion.
  4. *Transparent Governance:* Acknowledged honestly as pragmatic single-coder qualitative categorization to contextualize quantitative scores, rather than an exhaustive grounded theory study.
- **Reporting:** Tabulation of categories with representative, de-identified participant quotations.

---

## 6. Missing Data & Session Invalidation Governance

### 6.1 Missing Data Rules: Prevention First
1. **Digital Enforcement (Prevention):**  
   In the formal survey instrument, all 10 SUS items and all 8 objective comprehension items are set as **MANDATORY (Required)** fields. Submission is impossible with missing items, eliminating accidental omission.
2. **Emergency Paper Fallback Exception:**  
   In the event of an emergency paper administration during pilot testing:
   - If a participant inadvertently leaves exactly 1 SUS item blank, single-item neutral imputation ($R = 3$) is permitted following Sauro & Lewis (2016, p. 203).
   - If $\ge 2$ SUS items are blank, the participant's SUS score is treated as missing entirely and excluded from the SUS mean calculation.
   - Any missing comprehension item on paper is verified with the participant immediately during debriefing before coding.
3. **Session Withdrawal:**  
   If a participant withdraws before completing the survey, their task performance data may be retained only if explicitly permitted by their consent form; they are excluded from survey metrics.

### 6.2 Post-Collection Session Exclusion Criteria
A participant's session data may be invalidated and excluded from final reporting **ONLY** under the following pre-specified conditions:
1. Catastrophic technical failure (e.g., local server crash, power loss) that terminates the session before Task 4 is completed.
2. Uncorrectable procedural error by the moderator (e.g., moderator accidentally reads the answer key to the participant during orientation).
3. Discovery that the participant violated eligibility criteria (e.g., participant was a member of the prototype development team).

**ABSOLUTE ETHICAL RULE:**  
Under **NO CIRCUMSTANCES** may a participant's session be excluded or discarded because their SUS rating was low, their task errors were high, or their qualitative feedback was unfavorable. All completed sessions must be honestly accounted for.
