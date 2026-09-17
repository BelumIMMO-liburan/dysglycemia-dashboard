"""
Master Feedback Taxonomy for Human Feedback Learning Loop.

Provides a versioned, explicit vocabulary of structured feedback categories
that serve as the canonical learning signal for the feedback-driven adaptation layer.

DESIGN PRINCIPLES:
1. Extends (does NOT replace) existing override reason codes in models.py.
2. Override reason = WHY the human overrode the recommendation.
   Feedback category = WHAT aspect of the model behavior the human wants to influence.
3. Each category maps to specific feature(s) and a learning direction.
4. The taxonomy is versioned; categories can be deactivated but never deleted.
5. The human-selected structured category is the canonical learning signal.
   NLP interpretation of free-text is supplementary.

GOVERNANCE:
- Categories must not be created at runtime from free text.
- New categories require a taxonomy version bump.
- 'unmapped' category produces no learning signal.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Current taxonomy version — bump when categories are added/modified
TAXONOMY_VERSION: str = "1.0"


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


# ---------------------------------------------------------------------------
# Master Feedback Taxonomy — v1.0
# ---------------------------------------------------------------------------
FEEDBACK_CATEGORIES: Dict[str, FeedbackCategory] = {}

_RAW_CATEGORIES: List[FeedbackCategory] = [
    # --- Canonical Override Factors / Learning Signals (Section 2 Specification) ---
    FeedbackCategory(
        category_id="bmi_overweighted",
        category_name="BMI was over-weighted",
        description="The reviewer believes BMI had too much influence on the screening result for this case.",
        relevant_features=["bmi"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="age_overweighted",
        category_name="Age was over-weighted",
        description="The reviewer believes age had too much influence on the screening result for this case.",
        relevant_features=["age"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="waist_overweighted",
        category_name="Waist circumference was over-weighted",
        description="The reviewer believes waist circumference had too much influence on the screening result.",
        relevant_features=["waist_cm"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="hypertension_overweighted",
        category_name="Hypertension was over-weighted",
        description="The reviewer believes hypertension had too much influence on the screening result.",
        relevant_features=["hypertension_history"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="smoking_overweighted",
        category_name="Smoking history was over-weighted",
        description="The reviewer believes smoking history had too much influence on the screening result.",
        relevant_features=["smoking_history"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="sedentary_overweighted",
        category_name="Sedentary time was over-weighted",
        description="The reviewer believes sedentary time had too much influence on the screening result.",
        relevant_features=["sedentary_minutes_day"],
        learning_direction=DIR_REDUCE_INFLUENCE,
    ),
    FeedbackCategory(
        category_id="multiple_factors_overweighted",
        category_name="Multiple factors were over-weighted",
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

# ---------------------------------------------------------------------------
# Canonical Override Factor Categories for Unified Human Review UI
# ---------------------------------------------------------------------------
OVERRIDE_FACTOR_CHOICES: List[Tuple[str, str]] = [
    ("bmi_overweighted", "BMI was over-weighted"),
    ("age_overweighted", "Age was over-weighted"),
    ("waist_overweighted", "Waist circumference was over-weighted"),
    ("hypertension_overweighted", "Hypertension was over-weighted"),
    ("smoking_overweighted", "Smoking history was over-weighted"),
    ("sedentary_overweighted", "Sedentary time was over-weighted"),
    ("multiple_factors_overweighted", "Multiple factors were over-weighted"),
    ("other", "Other"),
    ("no_learning_signal", "No learning signal"),
]

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
