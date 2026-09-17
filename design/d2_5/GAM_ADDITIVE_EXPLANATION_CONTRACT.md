# Phase D2.5 — GAM-Native Additive Explanation Contract
**Document Version:** 1.0  
**Status:** AUTHORITATIVE & FROZEN  
**Date:** September 2026  
**Governing Skills:** `research-governance` (Highest Precedence), `dashboard-design`, `frontend-quality`

---

## 1. Mathematical Formulation

The frozen Stage-1 clinical decision-support model is a Generalized Additive Model (GAM) fitted via `pygam.LogisticGAM` with parameters $n\_splines=10, \lambda=10.0$ on the NHANES 2021–2023 development set.

The model defines the relationship between the seven non-laboratory predictors and the screening probability through the canonical logit link function:

$$\eta = g(p) = \text{logit}(p) = \ln\left(\frac{p}{1 - p}\right) = \beta_0 + \sum_{i=1}^{7} f_i(x_i)$$

Where:
- $\beta_0 \in \mathbb{R}$ is the frozen model intercept on the logit scale ($-0.72914687$).
- $f_i(x_i)$ is the individual additive term contribution of predictor $i$.
  - For continuous predictors ($i \in \{\text{age}, \text{bmi}, \text{waist\_cm}, \text{sedentary\_minutes\_day}\}$), $f_i$ is a penalized B-spline basis function ($10$ splines) evaluated after development-domain StandardScaler transformation.
  - For categorical predictors ($i \in \{\text{sex}, \text{hypertension\_history}, \text{smoking\_history}\}$), $f_i$ is a discrete factor term with $2$ levels.
- $\eta$ is the reconstructed linear predictor (log-odds score).
- $p = \sigma(\eta) = \frac{1}{1 + e^{-\eta}}$ is the model's predicted Stage-1 screening probability.

---

## 2. Canonical Term Decomposition Mapping

The additive terms in `gam_final.pkl` are indexed in exact correspondence with the preprocessed feature matrix:

| Term Index | Term Type | Predictor Canonical Name | Preprocessing Transformation | Basis Coefs | Link Evaluation Method |
|:---:|:---:|:---|:---|:---:|:---|
| `0` | `SplineTerm` | `age` | `StandardScaler` (z-score) | 10 | `gam.partial_dependence(term=0, X=X_trans)[0]` |
| `1` | `FactorTerm` | `sex` | Binary encoded (0/1) | 2 | `gam.partial_dependence(term=1, X=X_trans)[0]` |
| `2` | `SplineTerm` | `bmi` | `StandardScaler` (z-score) | 10 | `gam.partial_dependence(term=2, X=X_trans)[0]` |
| `3` | `FactorTerm` | `hypertension_history` | Binary encoded (0/1) | 2 | `gam.partial_dependence(term=3, X=X_trans)[0]` |
| `4` | `FactorTerm` | `smoking_history` | Binary encoded (0/1) | 2 | `gam.partial_dependence(term=4, X=X_trans)[0]` |
| `5` | `SplineTerm` | `waist_cm` | `StandardScaler` (z-score) | 10 | `gam.partial_dependence(term=5, X=X_trans)[0]` |
| `6` | `SplineTerm` | `sedentary_minutes_day` | `StandardScaler` (z-score) | 10 | `gam.partial_dependence(term=6, X=X_trans)[0]` |
| `7` | `Intercept` | `intercept` | N/A | 1 | `gam.coef_[-1]` ($-0.72914687$) |

---

## 3. Strict Mathematical Invariants

Every generated explanation must satisfy the following invariant conditions:

1. **Link-Scale Invariant:**
   $$\eta_{\text{recon}} = \beta_0 + \sum_{i=1}^{7} c_i$$
   Must equal `gam._linear_predictor(X_trans)[0]` within machine epsilon ($< 10^{-14}$).

2. **Probability Fidelity Invariant:**
   $$p_{\text{recon}} = \frac{1}{1 + e^{-\eta_{\text{recon}}}}$$
   $$|p_{\text{recon}} - p_{\text{gam}}| \le 10^{-10}$$
   If $|p_{\text{recon}} - p_{\text{gam}}| > 10^{-10}$, `ScreeningExplanationFidelityError` is raised and the explanation status is recorded as `failed`. Observed empirical error is $\le 5.55 \times 10^{-17}$.

3. **Additive Independence Invariant:**
   The contribution $c_i = f_i(x_i)$ depends strictly on feature $x_i$ and the frozen parameters of term $i$. There are no cross-feature interaction terms in this frozen model specification.

4. **Zero-SHAP Invariant:**
   No heuristic sampling, background perturbation, or legacy SHAP estimation is used. All explanations are computed directly from the model equations.

---

## 4. Persisted JSON Data Schema

The `contributions_json` field on `ScreeningExplanation` stores an array of exactly seven contribution objects:

```json
[
  {
    "feature_name": "sedentary_minutes_day",
    "display_name": "Sedentary Time",
    "raw_value": 480,
    "formatted_value": "480 min/day",
    "contribution": -0.4729124,
    "direction": "lower",
    "abs_contribution": 0.4729124
  },
  {
    "feature_name": "age",
    "display_name": "Age",
    "raw_value": 52,
    "formatted_value": "52 years",
    "contribution": 0.2713849,
    "direction": "higher",
    "abs_contribution": 0.2713849
  },
  {
    "feature_name": "waist_cm",
    "display_name": "Waist Circumference",
    "raw_value": 98.5,
    "formatted_value": "98.5 cm",
    "contribution": -0.2316741,
    "direction": "lower",
    "abs_contribution": 0.2316741
  }
]
```

---

## 5. UI Presentation Contract

1. **Ordering:** Factors are sorted by $|c_i|$ descending so the user sees the strongest drivers first.
2. **Progressive Disclosure:** Top 3 factors are visible on initial render; remaining 4 factors are revealed on clicking `[ Show all 7 factors ]`.
3. **Directional Semantics:**
   - $c_i > 0$: `"Pushes screening score higher (+X.XXX)"`
   - $c_i < 0$: `"Pushes screening score lower (-X.XXX)"`
4. **Visual Bar Width:** Normalized to the maximum observed absolute factor for that screening event:
   $$\text{width} = \frac{|c_i|}{\max_k |c_k|} \times 100\%$$
   The bar is strictly relative strength; it is not presented as a percentage of total probability.
5. **Non-Causal Language Mandate:**
   The UI must state explicitly:
   *"These values represent the mathematical term contributions of the frozen GAM model on the logit scale. They explain how the statistical model formed its screening score, not biological causation. A factor pushing the score higher or lower does not constitute personalized medical advice."*
