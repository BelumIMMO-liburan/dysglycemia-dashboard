# Scenario Runtime Verification Report (Phase E1.2)
## Frozen Runtime Execution & Mathematical Verification for Fictional Case Profiles

**Document Identifier:** `E1-SCENARIO-RUNTIME-VERIFICATION-V1.0.3`  
**Protocol Version:** `1.0.3` (Final Cross-Document Stimulus Reconciliation)  
**Verification Date:** 2026-09-05  
**Runtime Target:** `research-prototype-v1.0` (Development Mode Execution)  
**Model Architecture:** Generalized Additive Model (GAM) with PyGAM `predict_mu`  
**Operating Decision Threshold:** `0.1389` (Frozen)  
**Canonical Stimulus Fingerprint:** [`E1_STIMULUS_LOCK.md`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e1/E1_STIMULUS_LOCK.md)  

---

## 1. Executive Summary

To guarantee absolute consistency between task scenario documentation and software behavior during formal user evaluation, `CASE-ALPHA` and `CASE-BETA` were executed through the frozen Stage-1 screening inference service (`screening_inference.py`) and GAM-native additive explanation service (`screening_explanation.py`).

Both executions passed invariant mathematical fidelity verification:
$$\left|\sigma\left(\beta_0 + \sum_{i=1}^7 f_i(x_i)\right) - \hat{p}\right| \le 10^{-10}$$

### Key Findings & Corrections to Task Documentation:
1. **Case Alpha Probability:** Exact runtime probability is **0.272969 (27.30%)**, which is well above the `0.1389` operating threshold, yielding **AI Recommendation: Refer** / **Elevated Screening Signal**. The preliminary task draft estimated $0.38\text{--}0.45$; the task documentation is now corrected to state the exact point estimate ($\approx 0.273$).
2. **Case Alpha Factor Directions:**
   - In the actual spline calculation for Case Alpha ($102.0\text{ cm}$ waist circumference and $480\text{ min/day}$ sedentary time), **Sedentary Time** contributes $-0.472934$ (moderates/lowers score) and **Waist Circumference** contributes $-0.159560$ (moderates/lowers score).
   - The top positive contributor pushing the score higher is **Age (+0.417980)**, followed by **Hypertension (+0.103343)** and **BMI (+0.004917)**.
   - Moderating/negative contributors pushing the score lower are **Sedentary Time (-0.472934)**, **Waist Circumference (-0.159560)**, **Smoking History (Non-smoker, -0.117616)**, and **Biological Sex (Male, -0.026593)**.
   - Task 2 expected answers have been updated to align strictly with these empirical runtime values.
3. **Case Beta Probability & Factors:**
   - Exact runtime probability is **0.054663 (5.47%)**, well below `0.1389`, yielding **AI Recommendation: No Referral** / **Lower Screening Signal**.
   - Positive contributors: **Smoking History (+0.117616)** and **Biological Sex (Female, +0.026593)**.
   - Negative contributors: **Age (-0.784738)**, **Waist Circumference (-0.773908)**, **Sedentary Time (-0.344656)**, **BMI (-0.258779)**, and **Hypertension (-0.103343)**.

---

## 2. Case Alpha Runtime Audit

### 2.1 Input Predictors
- `Age`: **56** years
- `Biological Sex`: **Male** (`male`)
- `Body Mass Index (BMI)`: **31.2** kg/m²
- `History of Hypertension`: **Yes** (`yes`)
- `Smoking History`: **No** (`no`)
- `Waist Circumference`: **102.0** cm
- `Sedentary Time`: **480** minutes/day (8.0 hours)

### 2.2 Inference Output
- **Screening Probability:** `0.272969` ($27.30\%$)
- **Operating Threshold:** `0.1389`
- **AI Referral Recommendation:** **Refer** ($p \ge 0.1389$)
- **Screening Signal:** **Elevated Screening Signal**

### 2.3 GAM Decomposition & Additive Contributions (Link Scale)
- **Model Intercept ($\beta_0$):** `-0.729147`
- **Sum of Contributions ($\sum f_i$):** `-0.250464`
- **Reconstructed Linear Predictor ($\eta = \beta_0 + \sum f_i$):** `-0.979611`
- **Reconstructed Probability ($\sigma(\eta)$):** `0.272969`
- **Mathematical Reconstruction Error:** `0.00e+00` (Exact match)

#### All 7 GAM Contributions (Canonical Order):
| Predictor Name | Feature Code | Raw Value | Contribution ($\text{logit}$) | Direction | Sign |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Age | `age` | 56 years | `+0.417980` | Higher | Positive ($+$) |
| Biological Sex | `sex` | Male | `-0.026593` | Lower | Negative ($-$) |
| Body Mass Index (BMI) | `bmi` | 31.2 kg/m² | `+0.004917` | Higher | Positive ($+$) |
| History of Hypertension | `hypertension_history` | Yes | `+0.103343` | Higher | Positive ($+$) |
| Smoking History | `smoking_history` | No | `-0.117616` | Lower | Negative ($-$) |
| Waist Circumference | `waist_cm` | 102.0 cm | `-0.159560` | Lower | Negative ($-$) |
| Sedentary Time | `sedentary_minutes_day` | 480 min/day | `-0.472934` | Lower | Negative ($-$) |

#### Ranked Absolute Contribution Order:
1. **Sedentary Time** (`sedentary_minutes_day`): $|-0.472934| = 0.472934$ (Direction: Lower / Moderating)
2. **Age** (`age`): $|+0.417980| = 0.417980$ (Direction: Higher / Elevating)
3. **Waist Circumference** (`waist_cm`): $|-0.159560| = 0.159560$ (Direction: Lower / Moderating)
4. **Smoking History** (`smoking_history`): $|-0.117616| = 0.117616$ (Direction: Lower / Moderating)
5. **History of Hypertension** (`hypertension_history`): $|+0.103343| = 0.103343$ (Direction: Higher / Elevating)
6. **Biological Sex** (`sex`): $|-0.026593| = 0.026593$ (Direction: Lower / Moderating)
7. **Body Mass Index (BMI)** (`bmi`): $|+0.004917| = 0.004917$ (Direction: Higher / Elevating)

#### Top Positive Contributor:
- **Age (+0.417980)** is the single largest factor pushing Case Alpha's screening score higher.

#### Available Negative / Moderating Contributors:
- **Sedentary Time (-0.472934)**
- **Waist Circumference (-0.159560)**
- **Smoking History: Non-smoker (-0.117616)**
- **Biological Sex: Male (-0.026593)**

---

## 3. Case Beta Runtime Audit

### 3.1 Input Predictors
- `Age`: **32** years
- `Biological Sex`: **Female** (`female`)
- `Body Mass Index (BMI)`: **23.5** kg/m²
- `History of Hypertension`: **No** (`no`)
- `Smoking History`: **Yes** (`yes`, $\ge 100$ cigarettes)
- `Waist Circumference`: **74.0** cm
- `Sedentary Time`: **300** minutes/day (5.0 hours)

### 3.2 Inference Output
- **Screening Probability:** `0.054663` ($5.47\%$)
- **Operating Threshold:** `0.1389`
- **AI Referral Recommendation:** **No Referral** ($p < 0.1389$)
- **Screening Signal:** **Lower Screening Signal**

### 3.3 GAM Decomposition & Additive Contributions (Link Scale)
- **Model Intercept ($\beta_0$):** `-0.729147`
- **Sum of Contributions ($\sum f_i$):** `-2.121215`
- **Reconstructed Linear Predictor ($\eta = \beta_0 + \sum f_i$):** `-2.850362`
- **Reconstructed Probability ($\sigma(\eta)$):** `0.054663`
- **Mathematical Reconstruction Error:** `2.08e-17` (Machine epsilon)

#### All 7 GAM Contributions (Canonical Order):
| Predictor Name | Feature Code | Raw Value | Contribution ($\text{logit}$) | Direction | Sign |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Age | `age` | 32 years | `-0.784738` | Lower | Negative ($-$) |
| Biological Sex | `sex` | Female | `+0.026593` | Higher | Positive ($+$) |
| Body Mass Index (BMI) | `bmi` | 23.5 kg/m² | `-0.258779` | Lower | Negative ($-$) |
| History of Hypertension | `hypertension_history` | No | `-0.103343` | Lower | Negative ($-$) |
| Smoking History | `smoking_history` | Yes | `+0.117616` | Higher | Positive ($+$) |
| Waist Circumference | `waist_cm` | 74.0 cm | `-0.773908` | Lower | Negative ($-$) |
| Sedentary Time | `sedentary_minutes_day` | 300 min/day | `-0.344656` | Lower | Negative ($-$) |

#### Ranked Absolute Contribution Order:
1. **Age** (`age`): $|-0.784738| = 0.784738$ (Direction: Lower / Moderating)
2. **Waist Circumference** (`waist_cm`): $|-0.773908| = 0.773908$ (Direction: Lower / Moderating)
3. **Sedentary Time** (`sedentary_minutes_day`): $|-0.344656| = 0.344656$ (Direction: Lower / Moderating)
4. **Body Mass Index (BMI)** (`bmi`): $|-0.258779| = 0.258779$ (Direction: Lower / Moderating)
5. **Smoking History** (`smoking_history`): $|+0.117616| = 0.117616$ (Direction: Higher / Elevating)
6. **History of Hypertension** (`hypertension_history`): $|-0.103343| = 0.103343$ (Direction: Lower / Moderating)
7. **Biological Sex** (`sex`): $|+0.026593| = 0.026593$ (Direction: Higher / Elevating)

#### Top Positive Contributors:
1. **Smoking History (+0.117616)**
2. **Biological Sex: Female (+0.026593)**

#### Negative / Moderating Contributors:
1. **Age (-0.784738)**
2. **Waist Circumference (-0.773908)**
3. **Sedentary Time (-0.344656)**
4. **BMI (-0.258779)**
5. **Hypertension: No (-0.103343)**

---

## 4. Reconciliation Action Taken in Protocol Suite

1. `E1_TASK_SCENARIOS.md` Section 2 updated:
   - Case Alpha expected probability updated from `0.38--0.45` to `0.272969 (27.30%)`.
   - Case Alpha factor narrative updated: Age, Hypertension, and BMI push higher; Sedentary time, Waist circumference, Non-smoker, and Male sex push lower.
   - Case Beta expected probability updated to `0.054663 (5.47%)`.
2. Task 2 Participant Instruction & Expected Output updated:
   - Clarified that **Age** is the top positive factor pushing score higher.
   - Clarified that any of **Sedentary Time, Waist Circumference, or Non-smoking history** are valid moderating/lowering factors.
3. In accordance with governance rules, **zero model parameters were retuned or modified**. Task scenario documentation was adapted to the frozen model runtime.
