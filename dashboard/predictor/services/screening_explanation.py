"""
Stage-1 Non-Laboratory Screening Explanation Service
Phase D2.5 Implementation — GAM-Native Additive Decomposition

Authoritative Service for:
1. Deriving mathematically faithful local feature contributions directly from the
   fitted Generalized Additive Model's additive structure on the link (log-odds) scale.
2. Invariant additive fidelity verification:
   assert abs(sigmoid(intercept + sum(contributions)) - gam_probability) <= 1e-10
3. Complete exclusion of legacy SHAP approximations.
4. Non-causal presentation structuring.

GOVERNANCE NOTICE:
This module explains the mathematical calculation of the frozen GAM model.
It does NOT establish medical etiology, biological causation, or clinical diagnosis.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from decimal import Decimal
import numpy as np
import pandas as pd

from . import screening_inference


# Canonical predictor order matching Phase 4/5 evaluation
CANONICAL_PREDICTOR_ORDER = screening_inference.CANONICAL_PREDICTOR_ORDER

# Strict mathematical fidelity tolerance (link-scale & probability-scale)
FIDELITY_TOLERANCE: float = 1e-10


class ScreeningExplanationError(Exception):
    """Base exception for all Stage-1 screening explanation failures."""
    pass


class ScreeningExplanationFidelityError(ScreeningExplanationError):
    """Raised when the additive reconstruction fails mathematical fidelity tolerance."""
    pass


# Alias for concise import
ExplanationFidelityError = ScreeningExplanationFidelityError


@dataclass(frozen=True)
class ScreeningContribution:
    """Container for a single factor's additive contribution on the link scale."""
    feature_name: str
    display_name: str
    raw_value: Any
    formatted_value: str
    contribution: float
    direction: str  # 'higher' or 'lower'
    abs_contribution: float

    def to_dict(self) -> Dict[str, Any]:
        val = float(self.raw_value) if isinstance(self.raw_value, Decimal) else self.raw_value
        return {
            'feature_name': self.feature_name,
            'display_name': self.display_name,
            'raw_value': val,
            'formatted_value': self.formatted_value,
            'contribution': self.contribution,
            'direction': self.direction,
            'abs_contribution': self.abs_contribution,
        }


@dataclass(frozen=True)
class ScreeningExplanationResult:
    """
    Deterministic, immutable container for GAM-native explanation output.
    All feature contributions are on the model's additive log-odds (link) scale.
    """
    method: str
    method_version: str
    link_function: str
    intercept: float
    contributions: list  # List[ScreeningContribution]
    reconstructed_linear_predictor: float
    reconstructed_probability: float
    original_probability: float
    reconstruction_error: float
    fidelity_passed: bool
    model_sha256: str


FEATURE_DISPLAY_METADATA = {
    'age': ('Age', lambda v: f"{v} years"),
    'sex': ('Biological Sex', lambda v: 'Male' if str(v).lower() in ['male', '1', '1.0'] else 'Female'),
    'bmi': ('Body Mass Index (BMI)', lambda v: f"{float(v):.1f} kg/m²"),
    'waist_cm': ('Waist Circumference', lambda v: f"{float(v):.1f} cm"),
    'hypertension_history': ('History of Hypertension', lambda v: 'Yes' if str(v).lower() in ['yes', '1', '1.0'] else 'No'),
    'smoking_history': ('Smoking History', lambda v: 'Yes (≥100 cigarettes)' if str(v).lower() in ['yes', '1', '1.0'] else 'No'),
    'sedentary_minutes_day': ('Sedentary Time', lambda v: f"{int(v)} min/day"),
}


def explain_screening(cleaned_data: Dict[str, Any]) -> ScreeningExplanationResult:
    """
    Compute faithful GAM-native local additive contributions for a validated Stage-1 intake.

    Mathematical Pipeline:
    1. Reuse verified D2.3 encoding & canonical ordering.
    2. Retrieve cached frozen GAM and preprocessor (with SHA-256 integrity check).
    3. Transform continuous predictors using pre-fitted development StandardScaler.
    4. Compute term contributions on link scale:
       c_i = gam.partial_dependence(term=i, X=X_trans)[0] for i in 0..6
    5. Extract intercept term:
       c_intercept = float(gam.coef_[-1])
    6. Reconstruct linear predictor and probability:
       eta_recon = c_intercept + sum(c_i)
       p_recon = 1.0 / (1.0 + exp(-eta_recon))
    7. Verify additive fidelity:
       abs(p_recon - p_gam) <= 1e-10
    8. Return typed ScreeningExplanationResult.
    """
    # 1. Enforce canonical input contract and order
    df_input = screening_inference.encode_and_order_inputs(cleaned_data)

    # 2. Retrieve verified frozen artifacts
    gam_model, preprocessor = screening_inference.load_model_and_preprocessor()

    # 3. Standardize continuous features via pre-fitted scaler (transform only)
    try:
        X_trans = preprocessor.transform(df_input)
    except Exception as e:
        raise ScreeningExplanationError(f"Preprocessing transformation failure during explanation: {str(e)}") from e

    # 4. Evaluate original GAM probability
    try:
        original_prob = float(gam_model.predict_mu(X_trans)[0])
    except Exception as e:
        raise ScreeningExplanationError(f"GAM probability evaluation error: {str(e)}") from e

    # 5. Extract term contributions on link scale
    # Terms 0 to 6 correspond exactly to CANONICAL_PREDICTOR_ORDER:
    # Term 0: age (spline)
    # Term 1: sex (factor)
    # Term 2: bmi (spline)
    # Term 3: hypertension_history (factor)
    # Term 4: smoking_history (factor)
    # Term 5: waist_cm (spline)
    # Term 6: sedentary_minutes_day (spline)
    contributions_list = []
    term_values = []
    try:
        for term_idx, feature_name in enumerate(CANONICAL_PREDICTOR_ORDER):
            # Evaluate native term contribution on link scale
            val = float(gam_model.partial_dependence(term=term_idx, X=X_trans)[0])
            if not np.isfinite(val):
                raise ScreeningExplanationError(f"Non-finite contribution returned for term '{feature_name}': {val}")
            
            term_values.append(val)
            raw_val = cleaned_data.get(feature_name)
            meta = FEATURE_DISPLAY_METADATA.get(feature_name, (feature_name.replace('_', ' ').title(), str))
            disp_name = meta[0]
            fmt_val = meta[1](raw_val) if raw_val is not None else ""
            direction = 'higher' if val >= 0 else 'lower'

            contributions_list.append(ScreeningContribution(
                feature_name=feature_name,
                display_name=disp_name,
                raw_value=raw_val,
                formatted_value=fmt_val,
                contribution=val,
                direction=direction,
                abs_contribution=abs(val),
            ))
    except Exception as e:
        if isinstance(e, ScreeningExplanationError):
            raise
        raise ScreeningExplanationError(f"Failed to evaluate GAM term contributions: {str(e)}") from e

    # 6. Extract intercept (Term 7)
    intercept = float(gam_model.coef_[-1])
    if not np.isfinite(intercept):
        raise ScreeningExplanationError(f"Non-finite model intercept: {intercept}")

    # 7. Additive reconstruction
    eta_recon = intercept + sum(term_values)
    prob_recon = float(1.0 / (1.0 + np.exp(-eta_recon)))
    recon_error = float(abs(prob_recon - original_prob))

    # 8. Strict mathematical fidelity check
    if recon_error > FIDELITY_TOLERANCE:
        raise ScreeningExplanationFidelityError(
            f"GAM additive reconstruction error ({recon_error:.2e}) exceeded tolerance ({FIDELITY_TOLERANCE:.2e}). "
            f"Reconstructed p={prob_recon:.8f}, Original p={original_prob:.8f}. Failing closed."
        )

    return ScreeningExplanationResult(
        method="gam_native_additive",
        method_version="1.0",
        link_function="logit",
        intercept=intercept,
        contributions=contributions_list,
        reconstructed_linear_predictor=eta_recon,
        reconstructed_probability=prob_recon,
        original_probability=original_prob,
        reconstruction_error=recon_error,
        fidelity_passed=True,
        model_sha256=screening_inference.EXPECTED_GAM_SHA256,
    )
