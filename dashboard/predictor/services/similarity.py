"""
Similar-Case Definition Service for Human Feedback Learning Loop.

Provides a reproducible, transparent similarity metric between two screening
cases based on the 7 non-laboratory Stage-1 predictors.

DESIGN PRINCIPLES:
1. Uses ONLY the 7 Stage-1 predictors. HbA1c is EXCLUDED (leakage protection).
2. Normalized Euclidean distance with documented normalization bounds.
3. Categorical features use exact-match distance (0 or 1).
4. Similarity score in [0, 1] where 1 = identical.
5. Threshold ≥ 0.85 is a documented operational definition, NOT a universal threshold.
6. All parameters (method, bounds, version, features) are stored for reproducibility.

METHOD:
    For continuous features: normalize to [0, 1] using development-domain min/max.
    For categorical features: 0 if match, 1 if mismatch.
    Distance = sqrt(sum((x_i - y_i)^2) / n_features)
    Similarity = 1 - distance
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from ..screening_schema import STAGE1_INPUT_SCHEMA, CANONICAL_PREDICTOR_ORDER


# Normalization bounds derived from STAGE1_INPUT_SCHEMA development domain
# These are the frozen research-domain bounds for normalization.
NORMALIZATION_BOUNDS_VERSION = "1.0"

NORMALIZATION_BOUNDS: Dict[str, Dict[str, float]] = {
    "age": {"min": 18.0, "max": 80.0},
    "bmi": {"min": 11.1, "max": 69.9},
    "waist_cm": {"min": 60.0, "max": 187.0},
    "sedentary_minutes_day": {"min": 0.0, "max": 1200.0},
}

CONTINUOUS_FEATURES: Tuple[str, ...] = ("age", "bmi", "waist_cm", "sedentary_minutes_day")
CATEGORICAL_FEATURES: Tuple[str, ...] = ("sex", "hypertension_history", "smoking_history")

# Documented operational similarity threshold
DEFAULT_SIMILARITY_THRESHOLD: float = 0.85

# Similarity method identifier
SIMILARITY_METHOD: str = "normalized_euclidean_7feat"


@dataclass(frozen=True)
class SimilarityResult:
    """Immutable container for a pairwise similarity computation."""
    similarity_score: float                    # [0, 1] where 1 = identical
    distance: float                            # Raw normalized Euclidean distance
    is_similar: bool                           # True if score >= threshold
    threshold_used: float                      # Similarity threshold applied
    method: str                                # Method identifier
    normalization_bounds_version: str           # Version of normalization bounds
    features_used: List[str]                    # Feature names used
    feature_distances: Dict[str, float]         # Per-feature distance contributions
    case_a_values: Dict[str, Any]              # Case A feature values (for audit)
    case_b_values: Dict[str, Any]              # Case B feature values (for audit)

    def to_dict(self) -> dict:
        return {
            "similarity_score": round(self.similarity_score, 4),
            "distance": round(self.distance, 4),
            "is_similar": self.is_similar,
            "threshold_used": self.threshold_used,
            "method": self.method,
            "normalization_bounds_version": self.normalization_bounds_version,
            "features_used": self.features_used,
            "feature_distances": {k: round(v, 4) for k, v in self.feature_distances.items()},
        }


def _normalize_continuous(value: float, feature_name: str) -> float:
    """Normalize a continuous feature value to [0, 1] using development bounds."""
    bounds = NORMALIZATION_BOUNDS.get(feature_name)
    if bounds is None:
        raise ValueError(f"No normalization bounds for feature '{feature_name}'.")
    min_val = bounds["min"]
    max_val = bounds["max"]
    range_val = max_val - min_val
    if range_val == 0:
        return 0.0
    # Clip to bounds before normalizing
    val = max(min_val, min(max_val, float(value)))
    return (val - min_val) / range_val


def _categorical_distance(val_a: str, val_b: str) -> float:
    """Binary distance: 0 if match, 1 if mismatch."""
    return 0.0 if str(val_a).strip().lower() == str(val_b).strip().lower() else 1.0


def _extract_feature_values(record_or_dict) -> Dict[str, Any]:
    """
    Extract the 7 Stage-1 predictor values from a ScreeningRecord or dict.
    Returns a dict with canonical keys.
    """
    if isinstance(record_or_dict, dict):
        return {f: record_or_dict.get(f) for f in CANONICAL_PREDICTOR_ORDER}

    # Assume ScreeningRecord model instance
    return {
        "age": getattr(record_or_dict, "age", None),
        "sex": getattr(record_or_dict, "sex", None),
        "bmi": float(getattr(record_or_dict, "bmi", 0)),
        "waist_cm": float(getattr(record_or_dict, "waist_cm", 0)),
        "hypertension_history": getattr(record_or_dict, "hypertension_history", None),
        "smoking_history": getattr(record_or_dict, "smoking_history", None),
        "sedentary_minutes_day": getattr(record_or_dict, "sedentary_minutes_day", None),
    }


def compute_similarity(
    case_a,
    case_b,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> SimilarityResult:
    """
    Compute similarity between two screening cases.

    Parameters:
        case_a: ScreeningRecord instance or dict with 7 predictor values
        case_b: ScreeningRecord instance or dict with 7 predictor values
        threshold: Similarity threshold (default 0.85)

    Returns:
        SimilarityResult with score, distance, per-feature breakdown
    """
    vals_a = _extract_feature_values(case_a)
    vals_b = _extract_feature_values(case_b)

    # Validate all features present
    for feat in CANONICAL_PREDICTOR_ORDER:
        if vals_a.get(feat) is None:
            raise ValueError(f"Case A missing feature '{feat}'.")
        if vals_b.get(feat) is None:
            raise ValueError(f"Case B missing feature '{feat}'.")

    # Compute per-feature distances
    feature_distances: Dict[str, float] = {}
    n_features = len(CANONICAL_PREDICTOR_ORDER)

    for feat in CONTINUOUS_FEATURES:
        norm_a = _normalize_continuous(float(vals_a[feat]), feat)
        norm_b = _normalize_continuous(float(vals_b[feat]), feat)
        feature_distances[feat] = abs(norm_a - norm_b)

    for feat in CATEGORICAL_FEATURES:
        feature_distances[feat] = _categorical_distance(
            str(vals_a[feat]), str(vals_b[feat])
        )

    # Normalized Euclidean distance
    sum_sq = sum(d ** 2 for d in feature_distances.values())
    distance = math.sqrt(sum_sq / n_features)

    # Similarity = 1 - distance (clamped to [0, 1])
    similarity = max(0.0, min(1.0, 1.0 - distance))

    return SimilarityResult(
        similarity_score=similarity,
        distance=distance,
        is_similar=similarity >= threshold,
        threshold_used=threshold,
        method=SIMILARITY_METHOD,
        normalization_bounds_version=NORMALIZATION_BOUNDS_VERSION,
        features_used=list(CANONICAL_PREDICTOR_ORDER),
        feature_distances=feature_distances,
        case_a_values=vals_a,
        case_b_values=vals_b,
    )


def find_similar_cases(
    target_case,
    candidate_cases: list,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    max_results: int = 10,
) -> List[Tuple[Any, SimilarityResult]]:
    """
    Find cases from candidate_cases that are similar to target_case.

    Returns list of (case, SimilarityResult) tuples sorted by similarity descending.
    """
    results = []
    for candidate in candidate_cases:
        try:
            sim = compute_similarity(target_case, candidate, threshold=threshold)
            if sim.is_similar:
                results.append((candidate, sim))
        except (ValueError, AttributeError) as e:
            # Skip cases with missing/invalid features
            continue

    results.sort(key=lambda x: x[1].similarity_score, reverse=True)
    return results[:max_results]
