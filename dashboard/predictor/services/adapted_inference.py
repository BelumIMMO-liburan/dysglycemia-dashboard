"""
Adapted Inference Service for Human Feedback Learning Loop.

Wraps the FROZEN screening_inference module to provide version-aware prediction
that optionally applies a feedback-driven adaptation layer.

ARCHITECTURE:
    Input features
        → Frozen GAM (screening_inference.predict_screening)
        → base_probability, base_log_odds
        → IF active version has adaptation layer:
            → Load adaptation model
            → Compute delta_log_odds
            → adapted_probability = sigmoid(base_log_odds + delta_log_odds)
            → Apply threshold 0.1389
        → ELSE:
            → Use base_probability directly

GOVERNANCE:
    1. The original screening_inference.py is NEVER modified.
    2. The frozen GAM is ALWAYS called first — baseline output is always available.
    3. Both baseline and adapted outputs are returned for comparison.
    4. The adaptation layer may produce zero correction (valid outcome).
    5. The threshold (0.1389) is the same for both baseline and adapted paths.
"""

import logging
import math
from dataclasses import dataclass
from typing import Dict, Any, Optional

import numpy as np

from . import screening_inference
from .screening_inference import (
    FROZEN_DECISION_THRESHOLD,
    ScreeningInferenceResult,
    predict_screening,
    encode_and_order_inputs,
    load_model_and_preprocessor,
)
from . import model_versioning
from .feedback_learning import load_adaptation_model, compute_adaptation_delta

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AdaptedInferenceResult:
    """
    Container for version-aware inference output.
    Always includes both baseline and adapted results.
    """
    # Baseline (frozen GAM) output — always present
    baseline_probability: float
    baseline_recommendation: bool
    baseline_version_label: str

    # Adapted output — may equal baseline if no adaptation layer
    adapted_probability: float
    adapted_recommendation: bool
    adapted_version_label: str

    # Adaptation metadata
    has_adaptation: bool             # True if adaptation layer was applied
    delta_log_odds: float            # Log-odds correction applied (0.0 if none)
    delta_probability: float         # Probability difference (adapted - baseline)
    recommendation_changed: bool     # Whether recommendation differs

    # Threshold used
    threshold: float = FROZEN_DECISION_THRESHOLD

    @property
    def is_baseline(self) -> bool:
        return not self.has_adaptation

    def to_dict(self) -> dict:
        return {
            "baseline_probability": round(self.baseline_probability, 6),
            "baseline_recommendation": self.baseline_recommendation,
            "baseline_version_label": self.baseline_version_label,
            "adapted_probability": round(self.adapted_probability, 6),
            "adapted_recommendation": self.adapted_recommendation,
            "adapted_version_label": self.adapted_version_label,
            "has_adaptation": self.has_adaptation,
            "delta_log_odds": round(self.delta_log_odds, 6),
            "delta_probability": round(self.delta_probability, 6),
            "recommendation_changed": self.recommendation_changed,
            "threshold": self.threshold,
        }


def _probability_to_log_odds(p: float) -> float:
    """Convert probability to log-odds (logit). Clamp to avoid infinity."""
    p = max(1e-10, min(1.0 - 1e-10, p))
    return math.log(p / (1.0 - p))


def _log_odds_to_probability(lo: float) -> float:
    """Convert log-odds to probability (sigmoid)."""
    return 1.0 / (1.0 + math.exp(-lo))


def predict_adapted(
    cleaned_data: Dict[str, Any],
    version_label: Optional[str] = None,
) -> AdaptedInferenceResult:
    """
    Execute version-aware inference.

    1. Always runs the frozen GAM (baseline prediction).
    2. If the active version (or specified version) has an adaptation layer,
       applies the correction to produce an adapted prediction.
    3. Returns both results for comparison.

    Parameters:
        cleaned_data: Dict with 7 Stage-1 predictor values
        version_label: Optional specific version to use (defaults to active version)

    Returns:
        AdaptedInferenceResult with baseline and adapted outputs
    """
    # Step 1: Always compute baseline prediction using frozen GAM
    baseline_result = predict_screening(cleaned_data)
    baseline_prob = baseline_result.probability
    baseline_rec = baseline_result.referral_recommended
    baseline_version = model_versioning.BASELINE_VERSION_LABEL

    # Step 2: Determine which version to use
    if version_label:
        version = model_versioning.get_version_by_label(version_label)
    else:
        version = model_versioning.get_active_version()

    if version is None:
        version_label_used = baseline_version
    else:
        version_label_used = version.version_label

    # Step 3: Check if version has an adaptation layer
    has_adaptation = False
    delta_lo = 0.0
    adapted_prob = baseline_prob
    adapted_rec = baseline_rec

    if (
        version is not None
        and version.adaptation_artifact_path
        and version.version_type in ('active', 'candidate')
    ):
        # Load adaptation model
        adaptation = load_adaptation_model(version.adaptation_artifact_path)
        if adaptation is not None:
            has_adaptation = True

            # Compute correction delta using only the case's own features
            delta_lo = compute_adaptation_delta(adaptation, cleaned_data)

            # Apply correction to baseline log-odds
            base_lo = _probability_to_log_odds(baseline_prob)
            adapted_lo = base_lo + delta_lo
            adapted_prob = _log_odds_to_probability(adapted_lo)

            # Clamp to [0, 1] (should already be, but safety)
            adapted_prob = max(0.0, min(1.0, adapted_prob))

            # Apply threshold
            adapted_rec = adapted_prob >= FROZEN_DECISION_THRESHOLD

    delta_prob = adapted_prob - baseline_prob
    rec_changed = (adapted_rec != baseline_rec)

    return AdaptedInferenceResult(
        baseline_probability=baseline_prob,
        baseline_recommendation=baseline_rec,
        baseline_version_label=baseline_version,
        adapted_probability=adapted_prob,
        adapted_recommendation=adapted_rec,
        adapted_version_label=version_label_used,
        has_adaptation=has_adaptation,
        delta_log_odds=delta_lo,
        delta_probability=delta_prob,
        recommendation_changed=rec_changed,
        threshold=FROZEN_DECISION_THRESHOLD,
    )


def compare_case_across_versions(
    cleaned_data: Dict[str, Any],
    baseline_label: str = "GAM-v1",
    adapted_label: str = "",
) -> AdaptedInferenceResult:
    """
    Compare a case's AI output between baseline and a specific adapted version.
    If adapted_label is empty, uses the currently active version.
    """
    if not adapted_label:
        active = model_versioning.get_active_version()
        adapted_label = active.version_label if active else baseline_label

    # Get baseline result
    baseline_result = predict_screening(cleaned_data)
    baseline_prob = baseline_result.probability
    baseline_rec = baseline_result.referral_recommended

    # If same version, no adaptation
    if adapted_label == baseline_label:
        return AdaptedInferenceResult(
            baseline_probability=baseline_prob,
            baseline_recommendation=baseline_rec,
            baseline_version_label=baseline_label,
            adapted_probability=baseline_prob,
            adapted_recommendation=baseline_rec,
            adapted_version_label=adapted_label,
            has_adaptation=False,
            delta_log_odds=0.0,
            delta_probability=0.0,
            recommendation_changed=False,
        )

    # Get adapted result
    return predict_adapted(cleaned_data, version_label=adapted_label)
