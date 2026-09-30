"""
Master Feedback Taxonomy for Human Feedback Learning Loop.
Taxonomy Version 2.0 — Direction-Aware Structured Learning Signal.

DESIGN PRINCIPLES:
1. Extends (does NOT replace) existing override reason codes in models.py.
2. Provides a clean separation between:
   A. Evaluation Dashboard: Human Override Rationale (descriptive/audit only).
   B. Feedback Lab: Structured Learning Signal (direction-aware, actionable).
3. The canonical learning signal is a structured triple:
   (target_feature, direction, scope)
   NOT a single display-text label.
4. Historical taxonomy values (v1.0) are preserved via backward-compatible mapping.
   bmi_overweighted → target_feature=bmi, direction=reduce, scope=feature_specific.
5. NLP remains supplementary; the canonical signal is explicit.
6. The taxonomy is versioned; categories can be deactivated but never deleted.

GOVERNANCE:
- Categories must not be created at runtime from free text.
- New categories require a taxonomy version bump.
- 'unmapped' category produces no learning signal.
- Evaluation Mode feedback must NEVER trigger adaptation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Current taxonomy version — bumped from 1.0 to 2.0 for direction-aware signals
TAXONOMY_VERSION: str = "2.0"


@dataclass(frozen=True)
class FeedbackCategory:
    """Immutable definition of a single feedback category."""
    category_id: str
    category_name: str
    description: str
    relevant_features: List[str]  # Subset of the 7 Stage-1 predictors, or empty for global
    learning_direction: str       # reduce_influence | increase_influence | contextual_adjustment | reduce_global | increase_global | no_learning
    active: bool = True
    taxonomy_version: str = TAXONOMY_VERSION


# ---------------------------------------------------------------------------
# Learning direction constants
# ---------------------------------------------------------------------------
DIR_REDUCE_INFLUENCE = "reduce_influence"
DIR_INCREASE_INFLUENCE = "increase_influence"
DIR_CONTEXTUAL = "contextual_adjustment"
DIR_REDUCE_GLOBAL = "reduce_global"
DIR_INCREASE_GLOBAL = "increase_global"
DIR_NO_LEARNING = "no_learning"

VALID_DIRECTIONS: Tuple[str, ...] = (
    DIR_REDUCE_INFLUENCE,
    DIR_INCREASE_INFLUENCE,
    DIR_CONTEXTUAL,
    DIR_REDUCE_GLOBAL,
    DIR_INCREASE_GLOBAL,
    DIR_NO_LEARNING,
)

# ---------------------------------------------------------------------------
# Canonical 7 Stage-1 predictors (immutable reference)
# ---------------------------------------------------------------------------
STAGE1_FEATURES: Tuple[str, ...] = (
    "age", "sex", "bmi", "hypertension_history",
    "smoking_history", "waist_cm", "sedentary_minutes_day",
)


# ===========================================================================
# DIRECTION-AWARE CANONICAL SIGNAL (Taxonomy v2.0)
# ===========================================================================

@dataclass(frozen=True)
class CanonicalLearningSignal:
    """
    Explicit direction-aware structured learning signal.

    This is the canonical representation consumed by the residual adaptation layer.
    It is NOT inferred from display text or NLP output.
    """
    target_feature: str   # bmi | age | waist | hypertension | smoking | sedentary | multiple | other | none
    direction: str        # reduce | increase | adjust | contextual | none
    scope: str            # feature_specific | multiple_features | contextual | none

    @property
    def is_actionable(self) -> bool:
        """Return True if this signal should produce an adaptation delta."""
        return self.direction not in ("none", "contextual") and self.target_feature != "none"

    @property
    def is_directional(self) -> bool:
        """Return True if the signal encodes an explicit direction (reduce or increase)."""
        return self.direction in ("reduce", "increase")

    def to_dict(self) -> dict:
        return {
            "target_feature": self.target_feature,
            "direction": self.direction,
            "scope": self.scope,
        }


# Valid values for the canonical signal fields
VALID_TARGET_FEATURES: Tuple[str, ...] = (
    "bmi", "age", "waist", "hypertension", "smoking",
    "sedentary", "global_bias", "multiple", "other", "none",
)

VALID_SIGNAL_DIRECTIONS: Tuple[str, ...] = (
    "reduce", "increase", "adjust", "contextual", "none",
)

VALID_SCOPES: Tuple[str, ...] = (
    "feature_specific", "global", "multiple_features", "contextual", "none",
)

# Null / no-op signal
NULL_SIGNAL = CanonicalLearningSignal(
    target_feature="none", direction="none", scope="none",
)


# ---------------------------------------------------------------------------
# Mapping: target_feature → HumanFeedback.relevant_feature (Stage-1 predictor name)
# ---------------------------------------------------------------------------
TARGET_FEATURE_TO_PREDICTOR: Dict[str, Optional[str]] = {
    "bmi": "bmi",
    "age": "age",
    "waist": "waist_cm",
    "hypertension": "hypertension_history",
    "smoking": "smoking_history",
    "sedentary": "sedentary_minutes_day",
    "global_bias": None,
    "multiple": None,
    "other": None,
    "none": None,
}

# Mapping: target_feature → canonical learning_direction string
SIGNAL_DIRECTION_TO_LEARNING_DIRECTION: Dict[str, str] = {
    "reduce": DIR_REDUCE_INFLUENCE,
    "increase": DIR_INCREASE_INFLUENCE,
    "adjust": DIR_REDUCE_GLOBAL,     # multiple-feature adjustment → global reduce
    "contextual": DIR_CONTEXTUAL,
    "none": DIR_NO_LEARNING,
}


def canonical_signal_to_learning_fields(signal: CanonicalLearningSignal) -> Dict[str, any]:
    """
    Convert a CanonicalLearningSignal to HumanFeedback field values.

    Returns dict with:
        relevant_feature: str or None
        feedback_direction: str (legacy direction string)
    """
    relevant_feature = TARGET_FEATURE_TO_PREDICTOR.get(signal.target_feature)

    # Map direction
    if signal.scope == "global" or signal.target_feature == "global_bias":
        if signal.direction == "reduce":
            feedback_direction = DIR_REDUCE_GLOBAL
        elif signal.direction == "increase":
            feedback_direction = DIR_INCREASE_GLOBAL
        else:
            feedback_direction = DIR_NO_LEARNING
    elif signal.scope == "multiple_features":
        if signal.direction == "reduce":
            feedback_direction = DIR_REDUCE_GLOBAL
        elif signal.direction == "increase":
            feedback_direction = DIR_INCREASE_GLOBAL
        else:
            feedback_direction = SIGNAL_DIRECTION_TO_LEARNING_DIRECTION.get(signal.direction, DIR_NO_LEARNING)
    else:
        feedback_direction = SIGNAL_DIRECTION_TO_LEARNING_DIRECTION.get(signal.direction, DIR_NO_LEARNING)

    return {
        "relevant_feature": relevant_feature,
        "feedback_direction": feedback_direction,
    }


# ===========================================================================
# BACKWARD-COMPATIBLE MAPPING: Legacy v1.0 category_id → CanonicalLearningSignal
# ===========================================================================

LEGACY_CATEGORY_TO_CANONICAL: Dict[str, CanonicalLearningSignal] = {
    # Historical v1.0 override factors → direction-aware canonical signals
    "bmi_overweighted": CanonicalLearningSignal(
        target_feature="bmi", direction="reduce", scope="feature_specific",
    ),
    "age_overweighted": CanonicalLearningSignal(
        target_feature="age", direction="reduce", scope="feature_specific",
    ),
    "waist_overweighted": CanonicalLearningSignal(
        target_feature="waist", direction="reduce", scope="feature_specific",
    ),
    "hypertension_overweighted": CanonicalLearningSignal(
        target_feature="hypertension", direction="reduce", scope="feature_specific",
    ),
    "smoking_overweighted": CanonicalLearningSignal(
        target_feature="smoking", direction="reduce", scope="feature_specific",
    ),
    "sedentary_overweighted": CanonicalLearningSignal(
        target_feature="sedentary", direction="reduce", scope="feature_specific",
    ),
    "multiple_factors_overweighted": CanonicalLearningSignal(
        target_feature="multiple", direction="adjust", scope="multiple_features",
    ),
    "other": CanonicalLearningSignal(
        target_feature="other", direction="contextual", scope="contextual",
    ),
    "no_learning_signal": NULL_SIGNAL,

    # v1.0 supplementary categories
    "bmi_underweighted": CanonicalLearningSignal(
        target_feature="bmi", direction="increase", scope="feature_specific",
    ),
    "age_underweighted": CanonicalLearningSignal(
        target_feature="age", direction="increase", scope="feature_specific",
    ),
    "waist_underweighted": CanonicalLearningSignal(
        target_feature="waist", direction="increase", scope="feature_specific",
    ),
    "sedentary_underweighted": CanonicalLearningSignal(
        target_feature="sedentary", direction="increase", scope="feature_specific",
    ),
    "hypertension_context": CanonicalLearningSignal(
        target_feature="hypertension", direction="contextual", scope="contextual",
    ),
    "smoking_context": CanonicalLearningSignal(
        target_feature="smoking", direction="contextual", scope="contextual",
    ),
    "sex_context": CanonicalLearningSignal(
        target_feature="other", direction="contextual", scope="contextual",
    ),
    "general_risk_too_high": CanonicalLearningSignal(
        target_feature="multiple", direction="reduce", scope="multiple_features",
    ),
    "general_risk_too_low": CanonicalLearningSignal(
        target_feature="multiple", direction="increase", scope="multiple_features",
    ),
    "unmapped": NULL_SIGNAL,
}


def parse_canonical_signal(
    category_id: Optional[str] = None,
    target_feature: Optional[str] = None,
    direction: Optional[str] = None,
    scope: Optional[str] = None,
) -> CanonicalLearningSignal:
    """
    Parse a canonical learning signal from either:
    A. Legacy category_id (backward compatibility): maps to structured signal.
    B. Explicit target_feature + direction + scope (v2.0 structured signal).

    If explicit fields are provided, they take precedence over category_id mapping.

    Returns CanonicalLearningSignal (NULL_SIGNAL if inputs are invalid/missing).
    """
    # Path B: explicit structured fields (v2.0)
    if target_feature and direction and scope:
        if (
            target_feature in VALID_TARGET_FEATURES
            and direction in VALID_SIGNAL_DIRECTIONS
            and scope in VALID_SCOPES
        ):
            # Mutual consistency: target "none" cannot combine with directional adjustments
            if target_feature == "none" and (direction != "none" or scope != "none"):
                return NULL_SIGNAL
            if direction == "none" and (target_feature != "none" or scope != "none"):
                return NULL_SIGNAL
            return CanonicalLearningSignal(
                target_feature=target_feature,
                direction=direction,
                scope=scope,
            )

    # Path A: legacy category_id mapping
    if category_id:
        mapped = LEGACY_CATEGORY_TO_CANONICAL.get(category_id)
        if mapped is not None:
            return mapped

    return NULL_SIGNAL


# ---------------------------------------------------------------------------
# Master Feedback Taxonomy — v2.0 (preserves all v1.0 category_ids)
# ---------------------------------------------------------------------------
FEEDBACK_CATEGORIES: Dict[str, FeedbackCategory] = {}

_RAW_CATEGORIES: List[FeedbackCategory] = [
    # --- Canonical Override Factors / Learning Signals ---
    FeedbackCategory(
        category_id="bmi_overweighted",
        category_name="BMI appears over-weighted",
        description="The reviewer believes BMI had too much influence on the screening result for this case.",
        relevant_features=["bmi"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="age_overweighted",
        category_name="Age appears over-weighted",
        description="The reviewer believes age had too much influence on the screening result for this case.",
        relevant_features=["age"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="waist_overweighted",
        category_name="Waist circumference appears over-weighted",
        description="The reviewer believes waist circumference had too much influence on the screening result.",
        relevant_features=["waist_cm"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="hypertension_overweighted",
        category_name="Hypertension history appears over-weighted",
        description="The reviewer believes hypertension had too much influence on the screening result.",
        relevant_features=["hypertension_history"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="smoking_overweighted",
        category_name="Smoking history appears over-weighted",
        description="The reviewer believes smoking history had too much influence on the screening result.",
        relevant_features=["smoking_history"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="sedentary_overweighted",
        category_name="Sedentary time appears over-weighted",
        description="The reviewer believes sedentary time had too much influence on the screening result.",
        relevant_features=["sedentary_minutes_day"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="multiple_factors_overweighted",
        category_name="Multiple factors appear over-weighted",
        description="The reviewer believes multiple factors were collectively over-weighted, pushing probability too high.",
        relevant_features=[],
        learning_direction=DIR_REDUCE_GLOBAL,
    ),
    FeedbackCategory(
        category_id="other",
        category_name="Other",
        description="Contextual or idiosyncratic reason not mapped to a specific feature. Does not create automatic adaptation.",
        relevant_features=[],
        learning_direction=DIR_NO_LEARNING,
    ),
    FeedbackCategory(
        category_id="no_learning_signal",
        category_name="No learning signal",
        description="Decision does not convey a directional correction signal.",
        relevant_features=[],
        learning_direction=DIR_NO_LEARNING,
    ),

    # --- Supplementary / Compatibility Categories ---
    FeedbackCategory(
        category_id="bmi_underweighted",
        category_name="BMI weighted too weakly",
        description="The reviewer believes BMI should have had more influence on the screening result.",
        relevant_features=["bmi"],
        learning_direction=DIR_INCREASE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="age_underweighted",
        category_name="Age weighted too weakly",
        description="The reviewer believes age should have had more influence on the screening result.",
        relevant_features=["age"],
        learning_direction=DIR_INCREASE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="waist_underweighted",
        category_name="Waist circumference weighted too weakly",
        description="The reviewer believes waist circumference should have had more influence.",
        relevant_features=["waist_cm"],
        learning_direction=DIR_INCREASE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="sedentary_underweighted",
        category_name="Sedentary time weighted too weakly",
        description="The reviewer believes sedentary time should have had more influence.",
        relevant_features=["sedentary_minutes_day"],
        learning_direction=DIR_INCREASE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="hypertension_context",
        category_name="Hypertension context differs from model assumption",
        description="The reviewer has additional context about hypertension that the model cannot capture.",
        relevant_features=["hypertension_history"],
        learning_direction=DIR_CONTEXTUAL,
    ),
    FeedbackCategory(
        category_id="smoking_context",
        category_name="Smoking context differs from model assumption",
        description="The reviewer has additional context about smoking history that the model cannot capture.",
        relevant_features=["smoking_history"],
        learning_direction=DIR_CONTEXTUAL,
    ),
    FeedbackCategory(
        category_id="sex_context",
        category_name="Sex-related clinical context",
        description="The reviewer has sex-related clinical context that the model does not account for.",
        relevant_features=["sex"],
        learning_direction=DIR_CONTEXTUAL,
    ),
    FeedbackCategory(
        category_id="general_risk_too_high",
        category_name="Overall risk assessment too high",
        description="The reviewer believes the model's overall screening probability is too high for this case profile.",
        relevant_features=[],
        learning_direction=DIR_REDUCE_GLOBAL,
    ),
    FeedbackCategory(
        category_id="general_risk_too_low",
        category_name="Overall risk assessment too low",
        description="The reviewer believes the model's overall screening probability is too low for this case profile.",
        relevant_features=[],
        learning_direction=DIR_INCREASE_GLOBAL,
    ),
    FeedbackCategory(
        category_id="unmapped",
        category_name="Could not map to a specific feedback category",
        description="The feedback could not be reliably mapped to any structured category. No learning signal is generated.",
        relevant_features=[],
        learning_direction=DIR_NO_LEARNING,
        active=True,
    ),
]

# Build the lookup dictionary
for _cat in _RAW_CATEGORIES:
    FEEDBACK_CATEGORIES[_cat.category_id] = _cat


# ===========================================================================
# EVALUATION DASHBOARD: Human Override Rationale Choices
# Participant-facing. Descriptive/audit only. Must NOT trigger adaptation.
# Uses "appears over-weighted" phrasing (non-clinical).
# ===========================================================================
EVALUATION_OVERRIDE_RATIONALE_CHOICES: List[Tuple[str, str]] = [
    ("bmi_overweighted", "BMI appears over-weighted"),
    ("age_overweighted", "Age appears over-weighted"),
    ("waist_overweighted", "Waist circumference appears over-weighted"),
    ("hypertension_overweighted", "Hypertension history appears over-weighted"),
    ("smoking_overweighted", "Smoking history appears over-weighted"),
    ("sedentary_overweighted", "Sedentary time appears over-weighted"),
    ("multiple_factors_overweighted", "Multiple factors appear over-weighted"),
    ("other", "Other"),
    ("no_learning_signal", "No learning signal"),
]


# ===========================================================================
# FEEDBACK LAB: Structured Learning Signal UI Choices
# Researcher-facing. Two-step: Step A (target feature) + Step B (direction).
# ===========================================================================

# Step A: "Which factor is involved?"
FEEDBACK_LAB_TARGET_FEATURE_CHOICES: List[Tuple[str, str]] = [
    ("bmi", "BMI"),
    ("age", "Age"),
    ("waist", "Waist circumference"),
    ("hypertension", "Hypertension history"),
    ("smoking", "Smoking history"),
    ("sedentary", "Sedentary time"),
    ("multiple", "Multiple factors"),
    ("other", "Other"),
    ("none", "No learning signal"),
]

# Step B: "What direction of adjustment is intended?"
# Keyed by target_feature → list of (direction, scope, display_label)
FEEDBACK_LAB_DIRECTION_CHOICES: Dict[str, List[Tuple[str, str, str]]] = {
    # Feature-specific targets: reduce or increase
    "bmi": [
        ("reduce", "feature_specific", "Reduce influence"),
        ("increase", "feature_specific", "Increase influence"),
    ],
    "age": [
        ("reduce", "feature_specific", "Reduce influence"),
        ("increase", "feature_specific", "Increase influence"),
    ],
    "waist": [
        ("reduce", "feature_specific", "Reduce influence"),
        ("increase", "feature_specific", "Increase influence"),
    ],
    "hypertension": [
        ("reduce", "feature_specific", "Reduce influence"),
        ("increase", "feature_specific", "Increase influence"),
    ],
    "smoking": [
        ("reduce", "feature_specific", "Reduce influence"),
        ("increase", "feature_specific", "Increase influence"),
    ],
    "sedentary": [
        ("reduce", "feature_specific", "Reduce influence"),
        ("increase", "feature_specific", "Increase influence"),
    ],
    # Multiple factors: adjust
    "multiple": [
        ("adjust", "multiple_features", "Adjust multiple features"),
    ],
    # Other: contextual
    "other": [
        ("contextual", "contextual", "Contextual / manual interpretation required"),
    ],
    # No learning signal
    "none": [
        ("none", "none", "No learning signal"),
    ],
}


# ===========================================================================
# BACKWARD COMPATIBILITY: OVERRIDE_FACTOR_CHOICES (used by UnifiedHumanReviewForm)
# Preserved for backward compatibility with existing forms and views.
# Evaluation Dashboard uses EVALUATION_OVERRIDE_RATIONALE_CHOICES (same IDs, updated labels).
# ===========================================================================
OVERRIDE_FACTOR_CHOICES: List[Tuple[str, str]] = EVALUATION_OVERRIDE_RATIONALE_CHOICES


CORRECTIVE_LEARNING_FACTORS: Tuple[str, ...] = (
    "bmi_overweighted",
    "age_overweighted",
    "waist_overweighted",
    "hypertension_overweighted",
    "smoking_overweighted",
    "sedentary_overweighted",
    "multiple_factors_overweighted",
)


def is_corrective_learning_factor(factor_code: str) -> bool:
    """Return True if the factor represents an actionable model adaptation signal."""
    return factor_code in CORRECTIVE_LEARNING_FACTORS


def is_direction_aware_signal(
    target_feature: Optional[str],
    direction: Optional[str],
    scope: Optional[str],
) -> bool:
    """
    Return True if the given structured fields represent a valid v2.0 direction-aware
    signal (as opposed to a legacy category_id-only record).
    """
    return (
        target_feature is not None
        and direction is not None
        and scope is not None
        and target_feature in VALID_TARGET_FEATURES
        and direction in VALID_SIGNAL_DIRECTIONS
        and scope in VALID_SCOPES
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_category(category_id: str) -> Optional[FeedbackCategory]:
    """Return a FeedbackCategory by ID, or None if not found."""
    return FEEDBACK_CATEGORIES.get(category_id)


def get_active_categories() -> List[FeedbackCategory]:
    """Return all active feedback categories (excluding inactive)."""
    return [c for c in FEEDBACK_CATEGORIES.values() if c.active]


def get_learnable_categories() -> List[FeedbackCategory]:
    """Return active categories that produce a learning signal (excludes 'unmapped')."""
    return [
        c for c in FEEDBACK_CATEGORIES.values()
        if c.active and c.learning_direction != DIR_NO_LEARNING
    ]


def get_category_choices() -> List[tuple]:
    """Return (category_id, category_name) tuples for form ChoiceField."""
    return [
        (c.category_id, c.category_name)
        for c in FEEDBACK_CATEGORIES.values()
        if c.active
    ]


def get_feature_specific_categories(feature_name: str) -> List[FeedbackCategory]:
    """Return all active categories relevant to a specific feature."""
    if feature_name not in STAGE1_FEATURES:
        return []
    return [
        c for c in FEEDBACK_CATEGORIES.values()
        if c.active and feature_name in c.relevant_features
    ]


def validate_category_id(category_id: str) -> bool:
    """Check if a category_id exists in the taxonomy (active or inactive)."""
    return category_id in FEEDBACK_CATEGORIES


def get_taxonomy_version() -> str:
    """Return the current taxonomy version string."""
    return TAXONOMY_VERSION


def get_taxonomy_summary() -> Dict[str, any]:
    """Return a summary of the taxonomy for auditing."""
    return {
        "version": TAXONOMY_VERSION,
        "total_categories": len(FEEDBACK_CATEGORIES),
        "active_categories": len(get_active_categories()),
        "learnable_categories": len(get_learnable_categories()),
        "categories": {
            cat_id: {
                "name": cat.category_name,
                "direction": cat.learning_direction,
                "features": cat.relevant_features,
                "active": cat.active,
            }
            for cat_id, cat in FEEDBACK_CATEGORIES.items()
        },
    }
