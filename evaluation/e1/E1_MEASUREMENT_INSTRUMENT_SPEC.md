# Measurement Instrument Specification (Phase E1)
## Psychometric & Usability Survey Architecture

**Document Identifier:** `E1-INSTRUMENT-SPEC-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Date:** 2026-09-05  
**Stimulus Target:** `research-prototype-v1.0`  

---

## 1. Instrument Overview & Study Language Lock

The evaluation utilizes four post-task measurement instruments administered in immediate sequence following task execution:

```
[Completed Tasks 1-6]
        |
        v
[Instrument A: Protocol-Defined 8-Item Objective Comprehension Quiz] (Binary Scoring: 0 to 8)
        |
        v
[Instrument B: System Usability Scale — Indonesian Adaptation] (Sharfina & Santoso 2016: 0 to 100)
        |
        v
[Instrument C: 5 Custom Exploratory Clarity Items] (5-Point Likert: 1 to 5)
        |
        v
[Instrument D: 3 Open-Ended Qualitative Feedback Items] (Text)
```

### Primary Study Language Lock:
- **Locked Language:** **Bahasa Indonesia** (for the primary cohort of Indonesian university students, staff, and general users).
- **Governance Mandate:** An ad-hoc, unvalidated translation of psychometric instruments is **strictly prohibited**. 
- To preserve psychometric integrity, Instrument B adopts the published, peer-reviewed Indonesian adaptation of the System Usability Scale by **Sharfina & Santoso (2016)**.
- Instruments A, C, and D are provided in carefully translated Indonesian versions aligned with the frozen prototype's UI terminology, with English source texts maintained for research documentation.

---

## 2. Instrument A: Objective Comprehension Quiz

- **Construct:** Participant mental model alignment with system semantics, XAI directions, and research governance boundaries (RQ4).
- **Format:** 8 multiple-choice items, each with 4 options and 1 keyed correct answer.
- **Administration:** Closed-book, administered immediately post-task via the digital survey tool.
- **Question Bank:** Complete English and Bahasa Indonesia items detailed in `E1_COMPREHENSION_ITEM_BANK.md`.
- **Response Enforcement:** All 8 items are **MANDATORY (Required)** in the questionnaire platform. Routine neutral imputation is avoided. Technical dropouts are handled under `E1_ANALYSIS_PLAN.md`.
- **Scoring:** Binary (1 = Correct, 0 = Incorrect); Total Score: $0 \le S_{\text{comp}} \le 8$.

---

## 3. Instrument B: System Usability Scale (SUS)

### 3.1 Methodological Grounding & Literature Citations
The evaluation implements the System Usability Scale originally formulated by **John Brooke (1996)**, utilizing the validated Indonesian language adaptation published by **Sharfina & Santoso (2016)**.

*Authoritative Literature Citations:*
- Brooke, J. (1996). *SUS: A 'quick and dirty' usability scale*. Usability evaluation in industry, 189(194), 4-7.
- Sharfina, Z., & Santoso, H. B. (2016). *An Indonesian adaptation of the System Usability Scale (SUS)*. In 2016 International Conference on Advanced Computer Science and Information Systems (ICACSIS) (pp. 145-148). IEEE. DOI: 10.1109/ICACSIS.2016.7872776.
- Bangor, A., Kortum, P. T., & Miller, J. T. (2008). *An empirical evaluation of the System Usability Scale*. International Journal of Human-Computer Interaction, 24(6), 574-594.
- Bangor, A., Kortum, P., & Miller, J. (2009). *Determining what individual SUS scores mean: Adding an adjective rating scale*. Journal of Usability Studies, 4(3), 114-123.
- Sauro, J., & Lewis, J. R. (2016). *Quantifying the user experience: Practical statistics for user research* (2nd ed.). Morgan Kaufmann.

### 3.2 Exact Item Wording (English Source vs. Administered Indonesian Adaptation)
*Scale:* 5-Point Likert ($1 = \text{Sangat Tidak Setuju / Strongly Disagree}$ to $5 = \text{Sangat Setuju / Strongly Agree}$).

| # | Item Polarity | English Source Wording (Brooke, 1996) | Administered Indonesian Adaptation (Sharfina & Santoso, 2016) |
| :- | :--- | :--- | :--- |
| 1 | Odd (+) | *I think that I would like to use this system frequently.* | *Saya berpikir bahwa saya ingin sering menggunakan sistem ini.* |
| 2 | Even (-) | *I found the system unnecessarily complex.* | *Saya merasa sistem ini rumit untuk digunakan.* |
| 3 | Odd (+) | *I thought the system was easy to use.* | *Saya merasa sistem ini mudah digunakan.* |
| 4 | Even (-) | *I think that I would need the support of a technical person to be able to use this system.* | *Saya membutuhkan bantuan dari orang lain atau teknisi dalam menggunakan sistem ini.* |
| 5 | Odd (+) | *I found the various functions in this system were well integrated.* | *Saya merasa fungsi-fungsi dalam sistem ini bekerja dengan baik.* |
| 6 | Even (-) | *I thought there was too much inconsistency in this system.* | *Saya merasa ada banyak hal yang tidak konsisten pada sistem ini.* |
| 7 | Odd (+) | *I would imagine that most people would learn to use this system very quickly.* | *Saya merasa bahwa orang lain akan memahami cara menggunakan sistem ini dengan cepat.* |
| 8 | Even (-) | *I found the system very cumbersome to use.* | *Saya merasa sistem ini membingungkan.* |
| 9 | Odd (+) | *I felt very confident using the system.* | *Saya merasa tidak ada hambatan dalam menggunakan sistem ini.* |
| 10 | Even (-) | *I needed to learn a lot of things before I could get going with this system.* | *Saya perlu membiasakan diri terlebih dahulu sebelum menggunakan sistem ini.* |

### 3.3 Authoritative Scoring Formula
For each participant $i$:
1. For odd-numbered items ($k \in \{1, 3, 5, 7, 9\}$): $s_{i,k} = R_{i,k} - 1$
2. For even-numbered items ($k \in \{2, 4, 6, 8, 10\}$): $s_{i,k} = 5 - R_{i,k}$
3. Cumulative Individual SUS Score:
   $$\text{SUS}_i = 2.5 \times \sum_{k=1}^{10} s_{i,k}$$
   *Score Range:* $0 \le \text{SUS}_i \le 100$.

### 3.4 Missing Response Protocol: Prevention First
- **Instrument Requirement:** In the digital questionnaire platform, **all 10 SUS items are marked REQUIRED**. A participant cannot submit the questionnaire with missing items.
- **Avoidance of Routine Imputation:** Routine neutral-value (3) imputation is explicitly **prohibited** when responses are enforced digitally.
- **Technical Failure Handling:** If a network or platform error produces an incomplete record ($\ge 1$ missing item), the session is flagged and handled under the missing data protocol in `E1_ANALYSIS_PLAN.md`.

### 3.5 SUS Interpretation Framework & Governance Boundaries
- **NOT A PERCENTAGE:** An SUS score of 70 is an index score; it **does NOT mean** "70% usable" or "70% accuracy."
- **Reference Distributions & Benchmarks:**  
  SUS scores will be described relative to explicitly cited benchmark and adjective-rating reference distributions:
  - *Empirical Cross-Study Mean:* Bangor et al. (2008) observed an empirical cross-industry mean score of **68.0** ($SD \approx 12.5$) across 2,324 software and system evaluations.
  - *Adjective Rating Distribution:* Bangor et al. (2009) established empirical mean SUS scores associated with 7-point subjective adjective categories:
    - Worst Imaginable: $\text{Mean} \approx 12.5$
    - Poor: $\text{Mean} \approx 35.7$
    - OK: $\text{Mean} \approx 50.9$
    - Good: $\text{Mean} \approx 71.4$
    - Excellent: $\text{Mean} \approx 85.5$
    - Best Imaginable: $\text{Mean} \approx 90.9$
    *(Note: These adjective means serve as descriptive reference points from empirical literature, NOT universal categorical pass/fail cut-points).*
  - *Sauro & Lewis (2016) Percentiles:* $\text{SUS} \approx 68.0$ represents the 50th percentile rank; $\text{SUS} \approx 74.1$ represents the 70th percentile (Grade B-); $\text{SUS} \approx 78.9$ represents the 90th percentile (Grade A-).
- **Prohibited Claim:** The study will **NOT** claim that "SUS $\ge 68$ confirms acceptable software ergonomics" or proves clinical acceptability. Results will state: *"The prototype achieved a mean SUS score of X, which falls within the [Good / OK] reference range relative to the Bangor et al. (2008, 2009) empirical software distribution."*

---

## 4. Instrument C: Custom Exploratory Clarity Items

To evaluate architectural clarity specific to two-stage screening workflows that generic SUS items cannot capture, five exploratory items are administered.

*Scale:* 5-Point Likert ($1 = \text{Sangat Tidak Setuju / Strongly Disagree}$ to $5 = \text{Sangat Setuju / Strongly Agree}$).  
*Response Rule:* All 5 items are REQUIRED.

| Item Code | Target Construct | English Source Statement | Administered Bahasa Indonesia Statement |
| :--- | :--- | :--- | :--- |
| `CLAR_01` | Screening Signal Clarity | *"The difference between a non-laboratory screening signal and a formal medical diagnosis was clearly presented."* | *"Perbedaan antara sinyal skrining non-laboratorium dan diagnosis medis formal disajikan dengan jelas."* |
| `CLAR_02` | XAI Factor Direction | *"The 'Why this result?' explanation made it clear which input factors increased or decreased the screening score."* | *"Penjelasan 'Why this result?' memperjelas faktor-faktor input mana yang meningkatkan atau menurunkan skor skrining."* |
| `CLAR_03` | AI vs. Human Decision | *"The interface clearly distinguished the machine's initial recommendation from the final human referral decision."* | *"Antarmuka secara jelas membedakan rekomendasi awal mesin dari keputusan rujukan akhir oleh manusia."* |
| `CLAR_04` | Review / Override Control | *"I felt in control when reviewing or overriding the machine's referral recommendation."* | *"Saya merasa memegang kendali ketika meninjau atau mengesampingkan (override) rekomendasi rujukan mesin."* |
| `CLAR_05` | Stage-2 Lab Meaning | *"The Stage-2 HbA1c result clearly indicated a laboratory reference range rather than an automatic clinical diagnosis."* | *"Hasil HbA1c Tahap-2 secara jelas menunjukkan rentang acuan laboratorium dan bukan diagnosis klinis otomatis."* |

### Methodological Rule on Custom Items:
These items **DO NOT CONSTITUTE A VALIDATED PSYCHOMETRIC SCALE**.  
They must **NEVER** be summed or averaged into a composite "Clarity Index." Each item must be analyzed and reported individually using descriptive frequency distributions, medians, and interquartile ranges (IQR).

---

## 5. Instrument D: Qualitative Open-Ended Feedback

Administered as free-text input fields:

1. `QUAL_01`:  
   - *English:* *"What aspect of the screening and review workflow did you find most confusing or difficult to navigate?"*  
   - *Indonesian:* *"Bagian mana dari alur kerja skrining dan peninjauan yang paling membingungkan atau sulit untuk dinavigasi?"*
2. `QUAL_02`:  
   - *English:* *"What, if anything, could be changed to make the 'Why this result?' factor explanation easier to understand?"*  
   - *Indonesian:* *"Apa hal yang dapat diubah untuk membuat penjelasan faktor 'Why this result?' lebih mudah dipahami?"*
3. `QUAL_03`:  
   - *English:* *"Did you encounter any moments where you were unsure whether the computer or the human was responsible for a decision? If so, please describe."*  
   - *Indonesian:* *"Apakah Anda mengalami momen di mana Anda tidak yakin apakah komputer atau manusia yang bertanggung jawab atas suatu keputusan? Jika ya, mohon jelaskan."*

*Analytical Handling:* Evaluated via **lightweight thematic/category analysis informed by Braun & Clarke (2006)**. Used strictly by a single coder to categorize concrete user experience (UX) friction points and mental model ambiguities for the thesis discussion, not for statistical generalizability or formal grounded theory claims.
