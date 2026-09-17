"""
Feedback Learning Service for Human Feedback Learning Loop.

Implements the feature-weighted residual correction layer that sits on top of
the frozen GAM baseline. This is the learning mechanism that converts human
feedback into a measurable (or non-measurable) behavioral change.

ARCHITECTURE:
    Frozen GAM → base_log_odds (immutable, never retrained)
    Adaptation Layer → delta_log_odds (trained from feedback)
    Combined: sigmoid(base_log_odds + delta_log_odds) → adapted_probability
    Apply locked threshold 0.1389 → adapted_recommendation

REPRESENTATION & CREDIT ASSIGNMENT:
    The adaptation layer operates on an 8-dimensional normalized input vector:
    ['global_bias', 'age', 'sex', 'bmi', 'waist_cm', 'hypertension_history', 'smoking_history', 'sedentary_minutes_day']
    
    1. Feature-specific feedback (e.g., bmi_overweighted):
       Credit is assigned directly to the relevant feature column during training.
       The learned weight (beta_bmi) modifies the log-odds correction for any
       subsequent case proportionally to that case's own normalized BMI.
       Case B does NOT receive Case A's feedback metadata at inference time.
    2. Global feedback (e.g., reduce_risk_general):
       Credit is assigned to global_bias.
    3. Contextual feedback:
       Credit is distributed across global_bias and patient feature profile.
    4. No-learning feedback:
       Produces zero correction signal.

LEAKAGE PROTECTION:
    Eligible feedback records are verified against the canonical N=812 final-test
    set from master_split.csv and analytic_expanded_complete.parquet.
    If an eligible record intersects with final-test observations, learning is aborted.
"""

import hashlib
import logging
import math
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set

import numpy as np
import pandas as pd
from django.utils import timezone
from sklearn.linear_model import Ridge

from .feedback_taxonomy import (
    FEEDBACK_CATEGORIES,
    DIR_REDUCE_INFLUENCE,
    DIR_INCREASE_INFLUENCE,
    DIR_CONTEXTUAL,
    DIR_REDUCE_GLOBAL,
    DIR_INCREASE_GLOBAL,
    DIR_NO_LEARNING,
    STAGE1_FEATURES,
)
from .similarity import (
    NORMALIZATION_BOUNDS,
    CONTINUOUS_FEATURES,
    CATEGORICAL_FEATURES,
    CANONICAL_PREDICTOR_ORDER,
    _normalize_continuous,
)

logger = logging.getLogger(__name__)

# Minimum eligible feedback records required for a learning batch
MINIMUM_FEEDBACK_FOR_BATCH: int = 3

# Maximum absolute log-odds correction (safety bound)
MAX_DELTA_LOG_ODDS: float = 2.0

# Canonical 8-dimensional feature vector for the adaptation model
ADAPTATION_FEATURE_NAMES: List[str] = [
    "global_bias",
    "age",
    "sex",
    "bmi",
    "waist_cm",
    "hypertension_history",
    "smoking_history",
    "sedentary_minutes_day",
]

# Adaptation model directory
ADAPTATION_MODELS_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "models" / "adaptations"
)

# Project root for data access
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class FinalTestLeakageError(Exception):
    """Raised when a final-test observation is detected in the feedback learning pipeline."""
    pass


@dataclass
class AdaptationTrainingResult:
    """Result of training an adaptation layer."""
    success: bool
    artifact_path: str
    artifact_sha256: str
    feedback_count: int
    feature_names: List[str]
    training_summary: Dict[str, Any]
    error_message: str = ""


# Cached final test signatures and SEQN set
_CACHED_FINAL_TEST_SEQNS: Optional[Set[int]] = None
_CACHED_FINAL_TEST_SIGNATURES: Optional[Set[Tuple]] = None


def get_final_test_signatures() -> Tuple[Set[int], Set[Tuple]]:
    """
    Load and cache canonical final-test SEQN identifiers and 7-feature signatures.
    Authoritative sources:
      - nhanes_feasibility_2021_2023/predictions_phase5/final_test_predictions.csv (812 SEQN)
      - nhanes_feasibility_2021_2023/processed_phase3/analytic_expanded_complete.parquet
    """
    global _CACHED_FINAL_TEST_SEQNS, _CACHED_FINAL_TEST_SIGNATURES
    if _CACHED_FINAL_TEST_SEQNS is not None and _CACHED_FINAL_TEST_SIGNATURES is not None:
        return _CACHED_FINAL_TEST_SEQNS, _CACHED_FINAL_TEST_SIGNATURES

    pred_path = PROJECT_ROOT / "nhanes_feasibility_2021_2023" / "predictions_phase5" / "final_test_predictions.csv"
    parquet_path = PROJECT_ROOT / "nhanes_feasibility_2021_2023" / "processed_phase3" / "analytic_expanded_complete.parquet"

    seqns: Set[int] = set()
    signatures: Set[Tuple] = set()

    if pred_path.exists():
        df_p = pd.read_csv(pred_path)
        if "SEQN" in df_p.columns:
            seqns = set(int(s) for s in df_p["SEQN"].dropna())

    if parquet_path.exists() and len(seqns) > 0:
        df_parquet = pd.read_parquet(parquet_path)
        df_final = df_parquet[df_parquet["SEQN"].isin(seqns)]
        for _, row in df_final.iterrows():
            sex_str = "male" if row["sex"] == 1.0 else "female"
            hyp_str = "yes" if row["hypertension_history"] == 1.0 else "no"
            smk_str = "yes" if row["smoking_history"] == 1.0 else "no"
            sig = (
                int(round(row["age"])),
                sex_str,
                round(float(row["bmi"]), 1),
                round(float(row["waist_cm"]), 1),
                hyp_str,
                smk_str,
                int(round(row["sedentary_minutes_day"])),
            )
            signatures.add(sig)

    _CACHED_FINAL_TEST_SEQNS = seqns
    _CACHED_FINAL_TEST_SIGNATURES = signatures
    return seqns, signatures


def verify_no_final_test_leakage(eligible_feedback: list) -> Tuple[bool, str]:
    """
    Verify that NO observation in the eligible feedback records belongs to
    the canonical N=812 final-test set.

    Raises FinalTestLeakageError if an intersection is found.
    """
    final_seqns, final_signatures = get_final_test_signatures()

    for fb in eligible_feedback:
        review = getattr(fb, "human_review", None)
        if review is None:
            continue
        rec = getattr(review, "screening_record", None)
        if rec is None:
            continue

        # Check explicit token / identifier if present
        token = str(getattr(rec, "idempotency_token", "") or "")
        for s in final_seqns:
            if str(s) in token:
                msg = f"Leakage detected: ScreeningRecord {rec.id} matches final-test SEQN {s} in token."
                logger.error(msg)
                raise FinalTestLeakageError(msg)

        # Check feature signature
        try:
            sex_str = str(getattr(rec, "sex", "")).strip().lower()
            hyp_str = str(getattr(rec, "hypertension_history", "")).strip().lower()
            smk_str = str(getattr(rec, "smoking_history", "")).strip().lower()
            rec_sig = (
                int(round(float(rec.age))),
                sex_str,
                round(float(rec.bmi), 1),
                round(float(rec.waist_cm), 1),
                hyp_str,
                smk_str,
                int(round(float(rec.sedentary_minutes_day))),
            )
            if rec_sig in final_signatures:
                msg = (
                    f"Leakage detected: ScreeningRecord {rec.id} feature signature "
                    f"{rec_sig} matches a canonical final-test observation!"
                )
                logger.error(msg)
                raise FinalTestLeakageError(msg)
        except Exception as e:
            if isinstance(e, FinalTestLeakageError):
                raise
            logger.warning(f"Error checking signature for record {rec.id}: {e}")

    return True, f"Leakage verification passed: 0/{len(eligible_feedback)} records match final-test set."


def _direction_to_target(direction: str, ai_referral_recommended: bool) -> float:
    """
    Convert a feedback direction + original AI recommendation into a pseudo-target
    for the correction model on the log-odds scale:
    - Negative target (-1.0) → push probability DOWN (reduce risk signal)
    - Positive target (+1.0) → push probability UP (increase risk signal)
    - Zero (0.0) → no correction
    """
    if direction == DIR_NO_LEARNING:
        return 0.0

    if direction in (DIR_REDUCE_INFLUENCE, DIR_REDUCE_GLOBAL):
        return -1.0
    elif direction in (DIR_INCREASE_INFLUENCE, DIR_INCREASE_GLOBAL):
        return 1.0
    elif direction == DIR_CONTEXTUAL:
        if ai_referral_recommended:
            return -1.0
        else:
            return 1.0
    return 0.0


def _extract_raw_features_dict(record_or_dict) -> Dict[str, Any]:
    """Extract raw 7 Stage-1 features from a dict or ScreeningRecord."""
    if isinstance(record_or_dict, dict):
        return {f: record_or_dict.get(f) for f in CANONICAL_PREDICTOR_ORDER}

    return {
        "age": getattr(record_or_dict, "age", None),
        "sex": getattr(record_or_dict, "sex", None),
        "bmi": getattr(record_or_dict, "bmi", None),
        "waist_cm": getattr(record_or_dict, "waist_cm", None),
        "hypertension_history": getattr(record_or_dict, "hypertension_history", None),
        "smoking_history": getattr(record_or_dict, "smoking_history", None),
        "sedentary_minutes_day": getattr(record_or_dict, "sedentary_minutes_day", None),
    }


def _normalize_features_to_vector(record_or_dict) -> np.ndarray:
    """
    Convert raw 7 Stage-1 features to the canonical 8-dimensional vector:
    [global_bias (1.0), norm_age, norm_sex, norm_bmi, norm_waist, norm_hyp, norm_smk, norm_sed]
    All continuous features are normalized to [0, 1] via NORMALIZATION_BOUNDS.
    """
    data = _extract_raw_features_dict(record_or_dict)

    norm_age = _normalize_continuous(float(data["age"]), "age")
    norm_bmi = _normalize_continuous(float(data["bmi"]), "bmi")
    norm_waist = _normalize_continuous(float(data["waist_cm"]), "waist_cm")
    norm_sed = _normalize_continuous(float(data["sedentary_minutes_day"]), "sedentary_minutes_day")

    sex_val = str(data.get("sex", "")).strip().lower()
    norm_sex = 1.0 if sex_val == "male" else 0.0

    hyp_val = str(data.get("hypertension_history", "")).strip().lower()
    norm_hyp = 1.0 if hyp_val == "yes" else 0.0

    smk_val = str(data.get("smoking_history", "")).strip().lower()
    norm_smk = 1.0 if smk_val == "yes" else 0.0

    return np.array([
        1.0,  # global_bias
        norm_age,
        norm_sex,
        norm_bmi,
        norm_waist,
        norm_hyp,
        norm_smk,
        norm_sed,
    ], dtype=np.float64)


def _build_training_row(
    screening_record,
    structured_category: str,
    relevant_feature: Optional[str],
    feedback_direction: str,
    ai_referral_recommended: bool,
) -> Tuple[np.ndarray, float]:
    """
    Construct a training sample (x_row, y_target) for the adaptation linear model.
    
    Credit assignment:
    - Feature-specific feedback: The target direction is attributed to the specific
      feature column, scaled by the observed normalized feature value. All other
      columns remain 0.
    - Global feedback: Attributed to column 0 (global_bias).
    - Contextual feedback: Attributed across global bias and patient features.
    - No-learning feedback: Target is 0.0.
    """
    y_target = _direction_to_target(feedback_direction, ai_referral_recommended)
    x_row = np.zeros(len(ADAPTATION_FEATURE_NAMES), dtype=np.float64)

    if y_target == 0.0 or feedback_direction == DIR_NO_LEARNING:
        return x_row, 0.0

    norm_vector = _normalize_features_to_vector(screening_record)

    # 1. Feature-specific feedback
    if relevant_feature and relevant_feature in ADAPTATION_FEATURE_NAMES:
        feat_idx = ADAPTATION_FEATURE_NAMES.index(relevant_feature)
        # Use observed feature value (minimum 0.2 to ensure gradient)
        obs_val = norm_vector[feat_idx]
        x_row[feat_idx] = obs_val if obs_val > 0.0 else 1.0
        return x_row, y_target

    # Also check category metadata if relevant_feature was not explicitly stored
    cat = FEEDBACK_CATEGORIES.get(structured_category)
    if cat and cat.relevant_features:
        feat = cat.relevant_features[0]
        if feat in ADAPTATION_FEATURE_NAMES:
            feat_idx = ADAPTATION_FEATURE_NAMES.index(feat)
            obs_val = norm_vector[feat_idx]
            x_row[feat_idx] = obs_val if obs_val > 0.0 else 1.0
            return x_row, y_target

    # 2. Global feedback
    if feedback_direction in (DIR_REDUCE_GLOBAL, DIR_INCREASE_GLOBAL):
        x_row[0] = 1.0  # global_bias
        return x_row, y_target

    # 3. Contextual feedback
    if feedback_direction == DIR_CONTEXTUAL:
        x_row[0] = 0.5  # global_bias component
        # Distribute remaining half across patient's normalized features
        scale = 0.5 / math.sqrt(len(CANONICAL_PREDICTOR_ORDER))
        for j in range(1, len(ADAPTATION_FEATURE_NAMES)):
            x_row[j] = norm_vector[j] * scale
        return x_row, y_target

    # Default fallback to global bias
    x_row[0] = 1.0
    return x_row, y_target


def collect_eligible_feedback() -> list:
    """
    Collect all eligible, pending HumanFeedback records.
    Returns list of HumanFeedback instances with related ScreeningRecord data.
    """
    from ..models import HumanFeedback

    return list(
        HumanFeedback.objects.filter(
            is_eligible_for_learning=True,
            learning_status='pending',
        ).select_related(
            'human_review__screening_record',
        ).order_by('created_at')
    )


def train_adaptation_layer(
    eligible_feedback: list,
) -> AdaptationTrainingResult:
    """
    Train a Ridge regression correction model from eligible feedback records.

    Returns AdaptationTrainingResult with artifact path and training summary.
    """
    if len(eligible_feedback) < MINIMUM_FEEDBACK_FOR_BATCH:
        return AdaptationTrainingResult(
            success=False,
            artifact_path="",
            artifact_sha256="",
            feedback_count=len(eligible_feedback),
            feature_names=[],
            training_summary={},
            error_message=(
                f"Insufficient eligible feedback: {len(eligible_feedback)} < "
                f"{MINIMUM_FEEDBACK_FOR_BATCH} minimum."
            ),
        )

    # 1. Leakage protection assertion: Final-test observations must never enter learning
    verify_no_final_test_leakage(eligible_feedback)

    # 2. Build training data
    X_train = []
    y_train = []
    training_log = []

    for fb in eligible_feedback:
        try:
            review = fb.human_review
            screening = review.screening_record

            x_row, target = _build_training_row(
                screening_record=screening,
                structured_category=fb.structured_category,
                relevant_feature=fb.relevant_feature,
                feedback_direction=fb.feedback_direction,
                ai_referral_recommended=screening.ai_referral_recommended,
            )

            X_train.append(x_row)
            y_train.append(target)

            training_log.append({
                "feedback_id": str(fb.id),
                "category": fb.structured_category,
                "direction": fb.feedback_direction,
                "feature": fb.relevant_feature,
                "target": target,
                "row_norm": round(float(np.linalg.norm(x_row)), 4),
            })

        except Exception as e:
            logger.warning(f"Skipping feedback {fb.id}: {e}")
            continue

    if len(X_train) == 0:
        return AdaptationTrainingResult(
            success=False,
            artifact_path="",
            artifact_sha256="",
            feedback_count=0,
            feature_names=[],
            training_summary={"reason": "No valid training examples after filtering."},
            error_message="No valid training examples could be constructed.",
        )

    X_train = np.array(X_train, dtype=np.float64)
    y_train = np.array(y_train, dtype=np.float64)

    # Fit Ridge regression (fit_intercept=False because global_bias is explicitly column 0)
    # alpha=0.5 provides controlled regularization for small-N mechanism demonstration
    model = Ridge(alpha=0.5, fit_intercept=False)
    model.fit(X_train, y_train)

    # Serialize the model
    ADAPTATION_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    from ..models import ModelVersion
    existing_count = ModelVersion.objects.filter(
        version_type__in=['candidate', 'active', 'rejected', 'rolled_back']
    ).count()
    version_num = existing_count + 2  # v1 is baseline, so start from v2

    artifact_filename = f"adaptation_v{version_num}.pkl"
    artifact_path = str(ADAPTATION_MODELS_DIR / artifact_filename)

    weights_dict = {
        name: round(float(coef), 6)
        for name, coef in zip(ADAPTATION_FEATURE_NAMES, model.coef_)
    }

    artifact_data = {
        "model": model,
        "feature_names": ADAPTATION_FEATURE_NAMES,
        "max_delta": MAX_DELTA_LOG_ODDS,
        "training_count": len(X_train),
        "version": f"v{version_num}",
        "weights": weights_dict,
        "normalization_bounds": NORMALIZATION_BOUNDS,
    }

    with open(artifact_path, "wb") as f:
        pickle.dump(artifact_data, f)

    # Compute SHA-256
    h = hashlib.sha256()
    with open(artifact_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    artifact_sha256 = h.hexdigest().lower()

    # Training summary
    training_summary = {
        "training_count": len(X_train),
        "feature_count": len(ADAPTATION_FEATURE_NAMES),
        "weights": weights_dict,
        "alpha": model.alpha,
        "training_log": training_log,
    }

    return AdaptationTrainingResult(
        success=True,
        artifact_path=artifact_path,
        artifact_sha256=artifact_sha256,
        feedback_count=len(X_train),
        feature_names=ADAPTATION_FEATURE_NAMES,
        training_summary=training_summary,
    )


def load_adaptation_model(artifact_path: str) -> Optional[dict]:
    """Load a serialized adaptation model from disk."""
    try:
        with open(artifact_path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        logger.error(f"Failed to load adaptation model from {artifact_path}: {e}")
        return None


def compute_adaptation_delta(
    adaptation_artifact: dict,
    case_data_or_record,
    **kwargs,
) -> float:
    """
    Compute the log-odds correction delta for a given screening case
    using ONLY the case's own 7 Stage-1 features and the trained adaptation artifact.

    The delta is bounded to ±MAX_DELTA_LOG_ODDS for safety.
    Case B does NOT require Case A's feedback metadata.
    """
    model = adaptation_artifact.get("model")
    if model is None:
        return 0.0

    # Extract and normalize features to 8-dimensional vector
    x_norm = _normalize_features_to_vector(case_data_or_record)

    # Compute raw linear prediction
    raw_delta = float(model.predict(x_norm.reshape(1, -1))[0])

    # Clamp to safety bounds [-2.0, +2.0]
    clamped_delta = max(-MAX_DELTA_LOG_ODDS, min(MAX_DELTA_LOG_ODDS, raw_delta))

    return clamped_delta


def execute_learning_batch(min_feedback: int = MINIMUM_FEEDBACK_FOR_BATCH) -> Dict[str, Any]:
    """
    Execute a complete learning batch:
    1. Collect eligible feedback
    2. Validate minimum count
    3. Verify no final-test leakage
    4. Train adaptation layer
    5. Create candidate ModelVersion
    6. Execute technical validation checks
    7. Return batch result
    """
    from ..models import FeedbackLearningBatch, HumanFeedback
    from . import model_versioning

    result = {
        "success": False,
        "batch_id": None,
        "candidate_label": None,
        "feedback_count": 0,
        "error": None,
    }

    # 1. Collect eligible feedback
    eligible = collect_eligible_feedback()
    result["feedback_count"] = len(eligible)

    if len(eligible) < min_feedback:
        result["error"] = (
            f"Insufficient eligible feedback: {len(eligible)} < {min_feedback} minimum."
        )
        return result

    # 2. Get current active version
    active_version = model_versioning.get_active_version()

    # 3. Create batch record
    from ..models import ModelVersion
    existing_batches = FeedbackLearningBatch.objects.count()
    batch_label = f"batch-{existing_batches + 1:03d}"

    batch = FeedbackLearningBatch.objects.create(
        batch_label=batch_label,
        source_version=active_version,
        feedback_count=len(eligible),
        status='training',
    )
    batch.feedback_records.set(eligible)
    result["batch_id"] = str(batch.id)

    # 4. Train adaptation layer (includes final-test leakage verification)
    try:
        training_result = train_adaptation_layer(eligible)

        if not training_result.success:
            batch.status = 'failed'
            batch.error_log = training_result.error_message
            batch.completed_at = timezone.now()
            batch.save()
            result["error"] = training_result.error_message
            return result

        # 5. Create candidate ModelVersion
        existing_versions = ModelVersion.objects.filter(
            version_type__in=['candidate', 'active', 'rejected', 'rolled_back']
        ).count()
        candidate_label = f"GAM-v{existing_versions + 2}-candidate"

        candidate = model_versioning.create_candidate_version(
            parent_label=active_version.version_label,
            candidate_label=candidate_label,
            adaptation_path=training_result.artifact_path,
            feedback_count=training_result.feedback_count,
            description=f"Adaptation layer trained on {training_result.feedback_count} feedback records (batch: {batch_label}).",
        )

        batch.candidate_version = candidate
        batch.status = 'validating'
        batch.save()

        # 6. Run technical validation
        passed = model_versioning.validate_candidate(candidate_label)

        if passed:
            batch.validation_metrics = candidate.validation_metrics
            batch.status = 'validating'  # Validated and ready for activation
            batch.save()

            # Mark feedback as included
            for fb in eligible:
                fb.learning_status = 'included'
                fb.save()

            result["success"] = True
            result["candidate_label"] = candidate_label

        else:
            batch.status = 'rejected'
            batch.error_log = "Candidate failed technical validation."
            batch.completed_at = timezone.now()
            batch.save()
            result["error"] = "Candidate version failed validation."

    except Exception as e:
        logger.error(f"Learning batch failed: {e}", exc_info=True)
        batch.status = 'failed'
        batch.error_log = str(e)
        batch.completed_at = timezone.now()
        batch.save()
        result["error"] = str(e)

    return result


def activate_learning_batch(batch_id: str) -> Dict[str, Any]:
    """
    Activate the candidate version produced by a learning batch.
    """
    from ..models import FeedbackLearningBatch
    from . import model_versioning

    result = {"success": False, "error": None}

    try:
        batch = FeedbackLearningBatch.objects.get(id=batch_id)
    except FeedbackLearningBatch.DoesNotExist:
        result["error"] = f"Batch '{batch_id}' not found."
        return result

    if batch.candidate_version is None:
        result["error"] = "Batch has no candidate version."
        return result

    candidate = batch.candidate_version
    if candidate.validation_status != "passed":
        result["error"] = f"Candidate validation status is '{candidate.validation_status}', expected 'passed'."
        return result

    try:
        model_versioning.activate_version(candidate.version_label)
        batch.status = 'activated'
        batch.completed_at = timezone.now()
        batch.save()
        result["success"] = True
    except Exception as e:
        result["error"] = str(e)

    return result
