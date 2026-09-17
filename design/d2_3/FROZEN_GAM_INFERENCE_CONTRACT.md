# Frozen GAM Inference Contract: Mathematical & Semantic Specification

**Document Version:** 1.0  
**Phase:** D2.3  
**Status:** Frozen & Approved  
**Governing Skill:** `research-governance`  

---

## 1. Specification Overview

This document specifies the exact, immutable mathematical and programmatic contract between the validated Stage-1 screening intake layer and the frozen Phase-5 Generalized Additive Model (GAM) inference service.

Any modification to predictor sequence, categorical encoding, continuous feature scaling, logit link evaluation, or decision threshold comparison constitutes a governance violation.

---

## 2. Input Parameter Contract

The adapter requires an associative mapping containing exactly the following 7 parameters:

| Parameter Key | Python Type | Unit / Representation | Allowed Range / Domain | Clinical Meaning |
| :--- | :--- | :--- | :--- | :--- |
| `age` | `float` or `int` | Years | $[18, 80]$ (top-coded at 80) | Participant chronological age |
| `sex` | `str` | Clinical categorical | `male`, `female` | Biological sex as recorded in NHANES |
| `bmi` | `float` | $\text{kg/m}^2$ | $[11.1, 69.9]$ | Body Mass Index |
| `waist_cm` | `float` | Centimeters ($\text{cm}$) | $[60.0, 187.0]$ | Waist circumference |
| `hypertension_history` | `str` | Binary history | `yes`, `no` | Self-reported history of hypertension (BPQ020) |
| `smoking_history` | `str` | Binary history | `yes`, `no` | $\ge 100$ lifetime cigarettes (SMQ020) |
| `sedentary_minutes_day` | `float` or `int` | Minutes / day | $[0, 1200]$ | Typical daily sitting/reclining time (PAD680) |

---

## 3. Canonical Feature Vector & Ordering

The preprocessor and GAM model expect features in an immutable, 0-indexed column order:

$$\mathbf{x} = [x_0, x_1, x_2, x_3, x_4, x_5, x_6]^T$$

Where:
- $x_0$: `age` (continuous)
- $x_1$: `sex` (categorical indicator: `male` $= 1.0$, `female` $= 0.0$)
- $x_2$: `bmi` (continuous)
- $x_3$: `hypertension_history` (categorical indicator: `yes` $= 1.0$, `no` $= 0.0$)
- $x_4$: `smoking_history` (categorical indicator: `yes` $= 1.0$, `no` $= 0.0$)
- $x_5$: `waist_cm` (continuous)
- $x_6$: `sedentary_minutes_day` (continuous)

---

## 4. Continuous Feature Preprocessing & Scaling

Continuous features $\mathbf{x}_{\text{cont}} = [x_0, x_2, x_5, x_6]^T$ are standardized using the frozen development parameters:

$$z_j = \frac{x_j - \mu_j}{\sigma_j}$$

Where the development constants frozen inside `preprocessor.pkl` are:

| Index $j$ | Feature Name | Development Mean $\mu_j$ | Development Scale $\sigma_j$ |
| :---: | :--- | :--- | :--- |
| $0$ | `age` | $49.19090347$ | $18.45598870$ |
| $2$ | `bmi` | $28.54173886$ | $6.74569627$ |
| $5$ | `waist_cm` | $97.37762995$ | $16.06987924$ |
| $6$ | `sedentary_minutes_day` | $354.37407178$ | $201.38201865$ |

**Strict Rule:** No recalculation, batch re-estimation, or refitting is permitted. Categorical features ($x_1, x_3, x_4$) pass through unscaled.

---

## 5. GAM Mathematical Formulation & Link Function

The model is a Logistic Generalized Additive Model with penalized B-spline bases:

$$\eta(\mathbf{z}) = \beta_0 + \sum_{j \in \text{cont}} f_j(z_j) + \sum_{k \in \text{cat}} \beta_k x_k$$

Where:
- $\beta_0$: Model intercept term.
- $f_j(z_j)$: Smooth univariate penalized spline functions ($n_{\text{splines}} = 10, \lambda = 10.0$).
- $\beta_k$: Linear coefficients for categorical factor indicators.

The predicted screening probability $\hat{p}$ is obtained via the logit link inverse (logistic function):

$$\hat{p} = \text{predict\_mu}(\mathbf{z}) = \frac{1}{1 + e^{-\eta(\mathbf{z})}}$$

---

## 6. Decision Boundary & Threshold Rule

The screening referral classification is evaluated at full 64-bit floating-point precision:

$$\hat{y} = \begin{cases} \text{REFER}, & \text{if } \hat{p} \ge 0.1389 \\ \text{ROUTINE}, & \text{if } \hat{p} < 0.1389 \end{cases}$$

### Permitted Clinical Actions & Language:
- When $\hat{y} = \text{REFER}$:
  - Recommendation: *"Refer for Stage-2 Confirmatory HbA1c Assessment"*
  - Signal category: *Elevated screening risk*
- When $\hat{y} = \text{ROUTINE}$:
  - Recommendation: *"Routine Care / Re-screen in 3 Years"*
  - Signal category: *Lower screening risk*

**Prohibited Actions:** No diagnostic claims (e.g., "Patient has diabetes"), no threshold adjustments by end-users, and no automated scheduling without human clinician review.

---

## 7. Output Result Schema

The inference service returns an immutable `ScreeningInferenceResult` dataclass:

```python
@dataclass(frozen=True)
class ScreeningInferenceResult:
    probability: float                  # Floating point in [0.0, 1.0]
    referral_recommended: bool          # True iff probability >= 0.1389
    threshold: float = 0.1389           # Locked threshold constant
    model_name: str = "GAM"
    model_version: str = "Phase-5 GAM (λ=10.0, Splines=10)"
    preprocessor_version: str = "FrozenPreprocessor (Phase-5 StandardScaler)"
    execution_timestamp: str            # ISO/readable timestamp of execution
    formatted_probability: str          # e.g., "21.6%"
    formatted_recommendation: str       # Approved recommendation string
    raw_transformed_vector: List[float] # Standardized feature row passed to GAM
```
