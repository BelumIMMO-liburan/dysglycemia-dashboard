# Explainable AI (XAI) Presentation Options & Architectural Trade-offs

**Phase:** D1 — Design Foundation  
**Target Model:** Frozen Phase-5 Generalized Additive Model (`gam_final.pkl`)  
**Scope:** Interface Design & Methodological Comparison (No Implementation in D1)  
**Date:** 2026-09-04  

---

## 1. Executive Summary

In clinical decision support, the explanation must accurately reflect the mathematical reasoning of the underlying model while remaining intuitive to medical professionals. Because our locked primary model is a **Generalized Additive Model (GAM)**, we possess an intrinsically interpretable architecture. 

Unlike black-box neural networks or random forests where feature interactions must be post-hoc approximated using computationally intensive sampling methods, a GAM's prediction is an exact linear sum of smooth non-linear univariate functions:

$$\text{logit}(P(Y=1 \mid X)) = \beta_0 + \sum_{i=1}^{7} f_i(x_i)$$

This document evaluates three architectural options for presenting explanations in the dashboard and formalizes the definitive design recommendation.

---

## 2. Technical Comparison of XAI Approaches

| Dimension | Option A: GAM-Native Additive Term Decomposition | Option B: Post-Hoc SHAP (KernelSHAP / TreeSHAP) | Option C: Hybrid Presentation (Decomposition + Global SHAP Context) |
| :--- | :--- | :--- | :--- |
| **Mathematical Formulation** | Exact evaluation of fitted spline terms: $\Delta_i = f_i(x_i) - \mathbb{E}[f_i(X_i)]$. | Permutation or kernel sampling estimating Shapley values $\phi_i$ relative to background data. | Evaluates GAM term locally; displays global NHANES SHAP importance distributions alongside. |
| **Conceptual Validity** | **Flawless.** The model is literally an additive spline model. The decomposed term is the exact quantity entering the logistic sigmoid. | **Compromised.** KernelSHAP on GAM introduces sampling variance and approximation noise to explain an already additive model. | **Good.** High local validity with added epidemiological context. |
| **Computational Latency** | **Instantaneous ($< 1\text{ms}$).** Requires single matrix evaluation against pre-fitted spline knots. Zero background sampling. | **High ($3,000\text{ms} - 15,000\text{ms}$).** Sampling 100 background rows with 100 permutations freezes server threads. | **Instantaneous.** Local term is exact; global distribution is statically pre-computed. |
| **Faithfulness to Final Model** | **100% Faithful.** Zero approximation error. Exactly matches what produced the probability. | **Approximation Error.** KernelSHAP can yield non-zero values for features with zero true contribution. | **100% Faithful locally.** |
| **User Comprehension** | **High.** Visualized as clean, directional levers (Factors Elevating vs Factors Moderating). | **Moderate to Low.** Clinicians often misunderstand game-theoretic Shapley marginal values. | **Moderate.** Risk of cognitive overload if both local and global views are simultaneously exposed. |
| **Implementation Burden** | **Very Low.** Built directly on the native methods of `pygam` / `scikit-learn` without external dependencies. | **High.** Requires heavy `shap` library, background dataset caching, and thread management. | **Moderate.** Requires static asset compilation for background distributions. |

---

## 3. Detailed Architectural Evaluation

### Option A: GAM-Native Additive Term Decomposition (Recommended)
- **Mechanics:** 
  The GAM log-odds score is computed as:
  $$\text{score} = \beta_0 + f_{\text{age}}(\text{age}) + f_{\text{bmi}}(\text{bmi}) + f_{\text{waist}}(\text{waist}) + \dots + f_{\text{sedentary}}(\text{sedentary})$$
  The mean baseline log-odds in the training population is $\overline{s}$. The contribution of feature $i$ for an individual is:
  $$\text{term\_contribution}_i = f_i(x_i) - \text{mean}(f_i)$$
  - If $\text{term\_contribution}_i > 0$: The feature pushes the individual's score **above the population average** (Elevating Factor).
  - If $\text{term\_contribution}_i < 0$: The feature moderates the risk **below the population average** (Moderating Factor).
- **Interface Design:**
  - Divided into two clear cards:
    1. *Factors Elevating Screening Score* (sorted by descending magnitude)
    2. *Factors Moderating Screening Score* (sorted by ascending magnitude)
  - Each item displays:
    - Feature Name (e.g., "Waist Circumference")
    - Patient Value & Units (e.g., "98.5 cm")
    - Qualitative Strength Tag (`Strong`, `Moderate`, `Low` based on log-odds quartile)
    - Clean horizontal magnitude bar.
  - Progressive disclosure via expandable accordion revealing the exact spline curve position for researchers.

### Option B: Post-Hoc SHAP (KernelSHAP)
- **Mechanics:** Treats GAM as a black box and estimates Shapley values using a synthetic background matrix.
- **Why Rejected:** 
  1. *Redundant Complexity:* Using a black-box explainer on an intrinsically interpretable white-box model is considered an anti-pattern in medical informatics.
  2. *Performance Degradation:* KernelSHAP takes several seconds per prediction, creating unacceptable latency during clinical intake.
  3. *Unstable Estimates:* Sampling variance causes slight differences in SHAP values across consecutive runs on identical patient data, confusing evaluators.

### Option C: Hybrid Presentation
- **Mechanics:** Displays local GAM-native contributions, but embeds a small sparkline showing where this patient sits relative to the overall NHANES population distribution.
- **Why Deferred:** While academically rich, user testing in clinical CDSS shows that presenting simultaneous local and population-level distributions increases cognitive load for screening personnel. Deferred to future research updates.

---

## 4. Definitive Recommendation: Option A

We formally adopt **Option A: GAM-Native Additive Term Decomposition** for Phase D2 implementation.

### Benefits to the Thesis
1. **Mathematical Purity:** Matches the core theoretical contribution of Chapter 3 and Chapter 4 (utilizing GAMs for interpretable dysglycemia screening).
2. **Speed & Reliability:** Eliminates server-side timeouts and eliminates all runtime dependencies on the `shap` Python package.
3. **Clinical Intelligibility:** Translates complex non-linear splines into straightforward directional clinical drivers that directly inform clinician review and override deliberation.
