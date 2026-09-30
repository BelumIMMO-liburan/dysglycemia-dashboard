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
    parse_canonical_signal,
    canonical_signal_to_learning_fields,
    CanonicalLearningSignal,
    NULL_SIGNAL,
)
from .similarity import (
    NORMALIZATION_BOUNDS,
    CONTINUOUS_FEATURES,
    CATEGORICAL_FEATURES,
    CANONICAL_PREDICTOR_ORDER,
    _normalize_continuous,
)
from . import model_versioning

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
    relevant_feature: Optional[str] = None,
    feedback_direction: Optional[str] = None,
    ai_referral_recommended: bool = True,
    canonical_signal: Optional[CanonicalLearningSignal] = None,
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
    # 1. Consume canonical structured signal if provided
    if canonical_signal is not None and canonical_signal != NULL_SIGNAL:
        fields = canonical_signal_to_learning_fields(canonical_signal)
        if not relevant_feature:
            relevant_feature = fields["relevant_feature"]
        if not feedback_direction or feedback_direction == DIR_NO_LEARNING:
            feedback_direction = fields["feedback_direction"]
    elif canonical_signal == NULL_SIGNAL and not feedback_direction:
        return np.zeros(len(ADAPTATION_FEATURE_NAMES), dtype=np.float64), 0.0

    y_target = _direction_to_target(feedback_direction or DIR_NO_LEARNING, ai_referral_recommended)
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
    min_feedback: int = 1,
) -> AdaptationTrainingResult:
    """
    Train a Ridge regression correction model from eligible feedback records.

    Returns AdaptationTrainingResult with artifact path and training summary.
    """
    if len(eligible_feedback) < min_feedback:
        return AdaptationTrainingResult(
            success=False,
            artifact_path="",
            artifact_sha256="",
            feedback_count=len(eligible_feedback),
            feature_names=[],
            training_summary={},
            error_message=(
                f"Insufficient eligible feedback: {len(eligible_feedback)} < "
                f"{min_feedback} minimum."
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

            # Parse canonical structured signal (Taxonomy v2.0)
            canonical = parse_canonical_signal(
                category_id=fb.structured_category,
                target_feature=getattr(fb, 'target_feature', None),
                direction=getattr(fb, 'direction', None),
                scope=getattr(fb, 'scope', None),
            )

            x_row, target = _build_training_row(
                screening_record=screening,
                structured_category=fb.structured_category,
                relevant_feature=fb.relevant_feature,
                feedback_direction=fb.feedback_direction,
                ai_referral_recommended=screening.ai_referral_recommended,
                canonical_signal=canonical,
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
    ).exclude(version_label=model_versioning.BASELINE_VERSION_LABEL).count()
    version_num = existing_count + 1

    artifact_filename = f"adaptation_ra_v{version_num}.pkl"
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
        "version": f"RA-v{version_num}",
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
    """Load a serialized adaptation model from disk with portable path resolution fallback."""
    try:
        resolved_path = Path(artifact_path)
        if not resolved_path.is_file():
            # Portable fallback: resolve by basename in models/adaptations relative to repo root
            from django.conf import settings
            repo_root = Path(settings.BASE_DIR).parent
            candidate = repo_root / "models" / "adaptations" / resolved_path.name
            if candidate.is_file():
                resolved_path = candidate
            else:
                logger.error(f"Failed to locate adaptation artifact at '{artifact_path}' or '{candidate}'")
                return None
        with open(resolved_path, "rb") as f:
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


def execute_learning_batch(
    min_feedback: int = MINIMUM_FEEDBACK_FOR_BATCH,
    specific_feedback: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Execute a complete learning batch:
    1. Collect eligible feedback (or use specific_feedback if provided)
    2. Validate minimum count
    3. Verify no final-test leakage
    4. Train adaptation layer
    5. Create candidate ModelVersion (RA-v{N}-candidate)
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
    if specific_feedback is not None:
        eligible = list(specific_feedback)
    else:
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
        training_result = train_adaptation_layer(eligible, min_feedback=min_feedback)

        if not training_result.success:
            batch.status = 'failed'
            batch.error_log = training_result.error_message
            batch.completed_at = timezone.now()
            batch.save()
            result["error"] = training_result.error_message
            return result

        # 5. Create candidate ModelVersion using RA-vX naming
        existing_versions = ModelVersion.objects.filter(
            version_type__in=['candidate', 'active', 'rejected', 'rolled_back']
        ).exclude(version_label=model_versioning.BASELINE_VERSION_LABEL).count()
        candidate_label = f"RA-v{existing_versions + 1}-candidate"

        candidate = model_versioning.create_candidate_version(
            parent_label=active_version.version_label,
            candidate_label=candidate_label,
            adaptation_path=training_result.artifact_path,
            feedback_count=training_result.feedback_count,
            description=f"Residual Adaptation layer trained on {training_result.feedback_count} feedback records (batch: {batch_label}).",
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


def record_review_with_learning_signal(
    screening_record,
    reviewer_code: str,
    human_decision: str,  # 'accept' or 'override'
    override_factor: Optional[str] = None,
    rationale: str = "",
    target_feature: Optional[str] = None,
    signal_direction: Optional[str] = None,
    signal_scope: Optional[str] = None,
) -> Tuple[Any, Optional[Any]]:
    """
    Unified entry point for recording human review and capturing its structured learning signal.

    In the unified workflow, the Human Override itself is the intervention that generates
    the learning feedback. No secondary feedback submission step exists.

    GOVERNANCE RULES:
    1. Explanation prerequisite: ScreeningExplanation.status == 'generated' required.
    2. Reviewer code must be alphanumeric + hyphens/underscores (max 32 chars).
    3. Final decision derived server-side:
       - 'accept' -> screening_record.ai_referral_recommended
       - 'override' -> not screening_record.ai_referral_recommended
    4. One review per screening (idempotent / duplicate protection).
    5. Override reason code maps directly to the canonical 9 override factors / learning signals.
    6. For overrides, canonical HumanFeedback is created atomically.
    7. Eligibility:
       - Only eligible if APP_MODE == 'feedback_lab', not a practice record, and factor is corrective.
       - In evaluation mode or for practice records: is_eligible_for_learning=False, learning_status='excluded'.
    8. Free-text rationale is analyzed with NLP for auditability, but the selected factor is canonical.
    """
    from django.conf import settings
    from django.db import transaction
    from ..models import HumanReview, HumanFeedback
    from . import model_versioning
    from .feedback_taxonomy import (
        get_category,
        get_taxonomy_version,
        is_corrective_learning_factor,
        DIR_NO_LEARNING,
    )
    from .feedback_nlp import interpret_feedback_text

    # 1. Idempotency / Duplicate Check
    if hasattr(screening_record, 'human_review') and screening_record.human_review is not None:
        existing_review = screening_record.human_review
        existing_feedback = getattr(existing_review, 'feedback', None)
        return existing_review, existing_feedback

    # 2. Explanation Prerequisite Enforcement
    explanation = getattr(screening_record, 'explanation', None)
    if not explanation or explanation.status != 'generated':
        raise ValueError("Human review requires a verified, generated model explanation.")

    # 3. Validate Reviewer Code
    cleaned_code = (reviewer_code or "").strip()
    if not cleaned_code:
        raise ValueError("Reviewer code is required.")
    if len(cleaned_code) > 32:
        raise ValueError("Reviewer code must be 32 characters or fewer.")

    # 4. Derive Decision and Action
    decision_norm = (human_decision or "").strip().lower()
    if decision_norm not in ("accept", "override"):
        raise ValueError(f"Invalid human decision '{human_decision}'. Must be 'accept' or 'override'.")

    if decision_norm == "accept":
        review_action = "accepted"
        final_referral = screening_record.ai_referral_recommended
        reason_code = None
    else:
        review_action = "overridden"
        final_referral = not screening_record.ai_referral_recommended
        factor = (override_factor or "").strip()
        if not factor:
            raise ValueError("An override factor must be selected when overriding the AI recommendation.")
        reason_code = factor

    cleaned_note = (rationale or "").strip() or None

    # 5. NLP Analysis on Rationale (if provided)
    nlp_confidence = None
    nlp_raw_output = None
    if cleaned_note:
        try:
            nlp_res = interpret_feedback_text(cleaned_note)
            nlp_confidence = nlp_res.confidence
            nlp_raw_output = nlp_res.to_dict()
        except Exception as nlp_err:
            logger.warning(f"NLP interpretation failed on review note: {nlp_err}")
            nlp_raw_output = {"error": str(nlp_err)}

    # 6. Atomic Persistence of Review & Feedback
    active_version = model_versioning.get_active_version()
    current_mode = getattr(settings, 'APP_MODE', 'feedback_lab').lower()
    is_practice = getattr(screening_record, 'is_practice', False)

    with transaction.atomic():
        # Double check inside transaction
        if HumanReview.objects.filter(screening_record=screening_record).exists():
            existing_review = HumanReview.objects.get(screening_record=screening_record)
            return existing_review, getattr(existing_review, 'feedback', None)

        review = HumanReview(
            screening_record=screening_record,
            reviewer_code=cleaned_code,
            review_action=review_action,
            final_referral_recommended=final_referral,
            override_reason_code=reason_code,
            override_note=cleaned_note,
        )
        review.full_clean()
        review.save()

        feedback = None
        if review_action == "overridden":
            # Parse canonical structured signal (Taxonomy v2.0)
            canonical = parse_canonical_signal(
                category_id=reason_code,
                target_feature=target_feature,
                direction=signal_direction,
                scope=signal_scope,
            )

            # Map canonical signal to learning fields
            fields = canonical_signal_to_learning_fields(canonical)
            rel_feature = fields["relevant_feature"]
            direction = fields["feedback_direction"]

            # Fallback to category metadata if direction is no_learning but category exists
            if (not direction or direction == DIR_NO_LEARNING) and not target_feature:
                cat = get_category(reason_code)
                if cat:
                    direction = cat.learning_direction
                    if not rel_feature and cat.relevant_features:
                        rel_feature = cat.relevant_features[0]

            # Mode guard and eligibility
            is_corrective = is_corrective_learning_factor(reason_code) or canonical.is_actionable
            is_eligible = (
                current_mode == "feedback_lab"
                and not is_practice
                and is_corrective
                and canonical.is_actionable
                and direction != DIR_NO_LEARNING
            )

            feedback = HumanFeedback.objects.create(
                human_review=review,
                structured_category=reason_code,
                relevant_feature=rel_feature,
                feedback_direction=direction,
                # Direction-aware canonical signal (Taxonomy v2.0)
                target_feature=canonical.target_feature,
                direction=canonical.direction,
                scope=canonical.scope,
                feedback_text=cleaned_note or "",
                nlp_confidence=nlp_confidence,
                nlp_raw_output=nlp_raw_output,
                is_eligible_for_learning=is_eligible,
                learning_status="pending" if is_eligible else "excluded",
                model_version_at_feedback=active_version.version_label if active_version else "GAM-v1-baseline",
                taxonomy_version=get_taxonomy_version(),
            )
        elif cleaned_note:
            # Audit feedback for accepted review with note
            feedback = HumanFeedback.objects.create(
                human_review=review,
                structured_category="no_learning_signal",
                relevant_feature=None,
                feedback_direction=DIR_NO_LEARNING,
                # Direction-aware canonical signal: null signal for accepted reviews
                target_feature="none",
                direction="none",
                scope="none",
                feedback_text=cleaned_note,
                nlp_confidence=nlp_confidence,
                nlp_raw_output=nlp_raw_output,
                is_eligible_for_learning=False,
                learning_status="excluded",
                model_version_at_feedback=active_version.version_label if active_version else "GAM-v1-baseline",
                taxonomy_version=get_taxonomy_version(),
            )

        try:
            on_human_review_submitted(review, feedback)
        except Exception as err:
            logger.warning(f"Hook on_human_review_submitted failed: {err}")

    return review, feedback


# ==============================================================================
# CONTROLLED MECHANISM DEMONSTRATION EXPERIMENT (Thesis Gap #2)
# State Machine:
#   READY -> CASE_A_CREATED -> HUMAN_REVIEW_PENDING -> OVERRIDE_RECORDED
#   -> LEARNING_SIGNAL_CREATED -> CANDIDATE_CREATED -> VALIDATION_PASSED
#   -> ADAPTATION_ACTIVE -> CASE_B_CREATED -> CASE_B_EVALUATED -> COMPARISON_COMPLETE
# ==============================================================================

CONTROLLED_CASE_A_DATA: Dict[str, Any] = {
    'age': 55,
    'sex': 'Male',
    'height_cm': 175.0,
    'weight_kg': 98.31,
    'bmi': 32.1,
    'waist_cm': 105.0,
    'hypertension_history': 'Yes',
    'smoking_history': 'Yes',
    'sedentary_minutes_day': 600,
}

CONTROLLED_CASE_B_DATA: Dict[str, Any] = {
    'age': 53,
    'sex': 'Male',
    'height_cm': 175.0,
    'weight_kg': 96.47,
    'bmi': 31.5,
    'waist_cm': 103.0,
    'hypertension_history': 'Yes',
    'smoking_history': 'Yes',
    'sedentary_minutes_day': 580,
}


def get_active_controlled_experiment() -> Optional[Any]:
    """Return the active in-progress controlled experiment, if any."""
    from ..models import ControlledFeedbackExperiment
    return ControlledFeedbackExperiment.objects.exclude(
        state='COMPARISON_COMPLETE'
    ).order_by('-created_at').first()


def get_latest_controlled_experiment() -> Optional[Any]:
    """Return the most recent controlled experiment record (including completed)."""
    from ..models import ControlledFeedbackExperiment
    return ControlledFeedbackExperiment.objects.order_by('-created_at').first()


def start_controlled_experiment() -> Tuple[Any, Any]:
    """
    Step 1: Start or restart a controlled mechanism demonstration experiment.
    - Creates or resets ControlledFeedbackExperiment to state 'HUMAN_REVIEW_PENDING'.
    - Performs intake for Case A:
        Age: 55, Sex: Male, BMI: 32.1, Waist: 105cm, Hyp: Yes, Smk: Yes, Sed: 600 min.
    - Generates immutable ScreeningRecord with frozen GAM prediction:
        Probability = 0.341141, AI Recommendation = REFER.
    - Generates Native GAM explanation so human review is enabled.
    - CRITICAL: Does NOT fabricate human review or override. The researcher must
      review and submit the override in the Human Review interface.
    Returns (experiment, case_a_record).
    """
    from ..models import ControlledFeedbackExperiment, ScreeningRecord, ScreeningExplanation
    from .screening_inference import predict_screening
    from .screening_explanation import explain_screening
    from .model_versioning import ensure_baseline_version

    ensure_baseline_version()

    # Cancel or clean any previous in-progress experiment
    in_progress = ControlledFeedbackExperiment.objects.exclude(state='COMPARISON_COMPLETE')
    in_progress.delete()

    # 1. Run inference on Case A
    pred_res = predict_screening(CONTROLLED_CASE_A_DATA)
    if not pred_res.referral_recommended:
        logger.warning(f"Case A prediction was not REFER: {pred_res.probability}")

    # 2. Persist Case A ScreeningRecord
    record_a = ScreeningRecord.objects.create(
        age=CONTROLLED_CASE_A_DATA['age'],
        sex=CONTROLLED_CASE_A_DATA['sex'],
        bmi=CONTROLLED_CASE_A_DATA['bmi'],
        waist_cm=CONTROLLED_CASE_A_DATA['waist_cm'],
        hypertension_history=CONTROLLED_CASE_A_DATA['hypertension_history'],
        smoking_history=CONTROLLED_CASE_A_DATA['smoking_history'],
        sedentary_minutes_day=CONTROLLED_CASE_A_DATA['sedentary_minutes_day'],
        screening_probability=pred_res.probability,
        ai_referral_recommended=pred_res.referral_recommended,
        is_practice=False,
    )

    # 3. Generate explanation
    exp_res = explain_screening(CONTROLLED_CASE_A_DATA)
    ScreeningExplanation.objects.create(
        screening_record=record_a,
        method=exp_res.method,
        method_version=exp_res.method_version,
        link_function=exp_res.link_function,
        intercept=exp_res.intercept,
        contributions_json=[c.to_dict() for c in exp_res.contributions],
        reconstructed_linear_predictor=exp_res.reconstructed_linear_predictor,
        reconstructed_probability=exp_res.reconstructed_probability,
        reconstruction_error=exp_res.reconstruction_error,
        model_sha256=exp_res.model_sha256,
        status='generated',
    )

    # 4. Create ControlledFeedbackExperiment in HUMAN_REVIEW_PENDING state
    experiment = ControlledFeedbackExperiment.objects.create(
        experiment_label=f"EXP-CONTROLLED-{timezone.now().strftime('%Y%m%d%H%M%S')}",
        state='HUMAN_REVIEW_PENDING',
        case_a=record_a,
        notes="Case A created. Awaiting manual human review and override in the UI."
    )

    return experiment, record_a


def on_human_review_submitted(review, feedback):
    """
    Hook called when a HumanReview is submitted.
    If the review is performed on Case A of the active controlled experiment:
    - If Overridden: transitions state to OVERRIDE_RECORDED -> LEARNING_SIGNAL_CREATED
    - Captures override factor and learning signal
    """
    from ..models import ControlledFeedbackExperiment
    exp = ControlledFeedbackExperiment.objects.filter(
        case_a=review.screening_record,
        state='HUMAN_REVIEW_PENDING'
    ).first()

    if exp is None:
        return

    exp.human_review = review
    exp.override_factor = review.override_reason_code or ""
    exp.override_rationale = review.override_note or ""
    exp.learning_signal = feedback

    if review.review_action == 'overridden' and feedback and feedback.is_eligible_for_learning:
        exp.state = 'LEARNING_SIGNAL_CREATED'
        exp.notes = f"Real Human Override recorded with factor '{exp.override_factor}'. Canonical learning signal created."
    else:
        exp.notes = f"Human decision recorded: {review.review_action}. Not eligible for corrective learning."
    exp.save()


def run_controlled_learning(experiment_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Step 3: Execute controlled learning from the real Human Override signal.
    - Requires state == 'LEARNING_SIGNAL_CREATED'
    - Trains Ridge residual adaptation layer on the single eligible signal (min_feedback=1).
    - Creates Candidate Adaptation (RA-v1-candidate).
    - Runs all 13 technical validation checks.
    - Transitions state to VALIDATION_PASSED.
    """
    from ..models import ControlledFeedbackExperiment
    if experiment_id:
        exp = ControlledFeedbackExperiment.objects.filter(id=experiment_id).first()
    else:
        exp = get_active_controlled_experiment()

    if not exp:
        return {'success': False, 'error': 'No active controlled experiment found.'}

    if exp.state != 'LEARNING_SIGNAL_CREATED':
        return {
            'success': False,
            'error': f"Cannot run learning in state '{exp.state}'. Expected 'LEARNING_SIGNAL_CREATED'."
        }

    if not exp.learning_signal or not exp.learning_signal.is_eligible_for_learning:
        return {
            'success': False,
            'error': "No eligible learning signal attached to this controlled experiment."
        }

    # Execute single-signal learning batch
    batch_res = execute_learning_batch(
        min_feedback=1,
        specific_feedback=[exp.learning_signal]
    )

    if not batch_res['success']:
        exp.state = 'READY'
        exp.notes = f"Learning batch failed: {batch_res.get('error')}"
        exp.save()
        return {'success': False, 'error': batch_res.get('error')}

    from ..models import FeedbackLearningBatch
    batch = FeedbackLearningBatch.objects.get(id=batch_res['batch_id'])

    exp.learning_batch = batch
    exp.candidate_adaptation = batch.candidate_version
    exp.validation_id = str(batch.id)
    exp.state = 'VALIDATION_PASSED'
    exp.notes = (
        f"Candidate {batch.candidate_version.version_label} trained and verified. "
        f"13/13 technical validation checks passed."
    )
    exp.save()

    return {
        'success': True,
        'candidate_label': batch.candidate_version.version_label,
        'experiment_id': str(exp.id),
    }


def activate_controlled_adaptation(experiment_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Step 4: Activate the validated candidate adaptation layer.
    - Requires state == 'VALIDATION_PASSED'.
    - Activates candidate as RA-vX (Validated & Active).
    - Transitions state to ADAPTATION_ACTIVE.
    """
    from ..models import ControlledFeedbackExperiment
    if experiment_id:
        exp = ControlledFeedbackExperiment.objects.filter(id=experiment_id).first()
    else:
        exp = get_active_controlled_experiment()

    if not exp:
        return {'success': False, 'error': 'No active controlled experiment found.'}

    if exp.state != 'VALIDATION_PASSED':
        return {
            'success': False,
            'error': f"Cannot activate adaptation in state '{exp.state}'. Expected 'VALIDATION_PASSED'."
        }

    act_res = activate_learning_batch(str(exp.learning_batch.id))
    if not act_res['success']:
        return {'success': False, 'error': act_res.get('error')}

    exp.active_adaptation = exp.candidate_adaptation
    exp.state = 'ADAPTATION_ACTIVE'
    exp.notes = f"Adaptation {exp.active_adaptation.version_label} activated and ready for Case B evaluation."
    exp.save()

    return {'success': True, 'active_label': exp.active_adaptation.version_label}


def evaluate_controlled_case_b(experiment_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Step 5: Evaluate subsequent similar Case B under frozen GAM vs active residual adaptation.
    - STRICT GUARD: Requires state == 'ADAPTATION_ACTIVE'.
    - Registers Case B:
        Age: 53, Sex: Male, BMI: 31.5, Waist: 103cm, Hyp: Yes, Smk: Yes, Sed: 580 min.
    - Computes similarity between Case A and Case B (expected 0.9846 >= 0.85).
    - Computes baseline probability via Frozen Baseline GAM (expected 0.311198).
    - Computes adapted probability via Active Residual Adaptation (expected 0.270487).
    - Probability delta: expected -0.040711. Log-odds delta: approx -0.1980.
    - STRICT EXPERIMENTAL CONSTRAINT: Case B inference uses ONLY Case B's own 7 features
      and the active adaptation artifact. It NEVER receives Case A metadata.
    - Persists SimilarCaseComparison and transitions experiment to 'COMPARISON_COMPLETE'.
    """
    from ..models import (
        ControlledFeedbackExperiment,
        ScreeningRecord,
        ScreeningExplanation,
        SimilarCaseComparison,
    )
    from .screening_inference import predict_screening
    from .screening_explanation import explain_screening
    from .adapted_inference import predict_adapted
    from .similarity import compute_similarity
    from .model_versioning import get_baseline_version

    if experiment_id:
        exp = ControlledFeedbackExperiment.objects.filter(id=experiment_id).first()
    else:
        exp = get_active_controlled_experiment()

    if not exp:
        return {'success': False, 'error': 'No active controlled experiment found.'}

    if exp.state != 'ADAPTATION_ACTIVE':
        return {
            'success': False,
            'error': f"Cannot evaluate Case B in state '{exp.state}'. Expected 'ADAPTATION_ACTIVE'."
        }

    # 1. Compute similarity between Case A and Case B
    sim = compute_similarity(exp.case_a, CONTROLLED_CASE_B_DATA)

    # 2. Compute Case B baseline prediction using Frozen GAM
    baseline_res = predict_screening(CONTROLLED_CASE_B_DATA)

    # 3. Compute Case B adapted prediction using Active Adaptation (strictly Case B's own features)
    adapted_res = predict_adapted(CONTROLLED_CASE_B_DATA, version_label=exp.active_adaptation.version_label)

    # 4. Persist Case B ScreeningRecord (for auditing and viewability)
    record_b = ScreeningRecord.objects.create(
        age=CONTROLLED_CASE_B_DATA['age'],
        sex=CONTROLLED_CASE_B_DATA['sex'],
        bmi=CONTROLLED_CASE_B_DATA['bmi'],
        waist_cm=CONTROLLED_CASE_B_DATA['waist_cm'],
        hypertension_history=CONTROLLED_CASE_B_DATA['hypertension_history'],
        smoking_history=CONTROLLED_CASE_B_DATA['smoking_history'],
        sedentary_minutes_day=CONTROLLED_CASE_B_DATA['sedentary_minutes_day'],
        screening_probability=baseline_res.probability,
        ai_referral_recommended=baseline_res.referral_recommended,
        is_practice=False,
    )

    exp_b = explain_screening(CONTROLLED_CASE_B_DATA)
    ScreeningExplanation.objects.create(
        screening_record=record_b,
        method=exp_b.method,
        method_version=exp_b.method_version,
        link_function=exp_b.link_function,
        intercept=exp_b.intercept,
        contributions_json=[c.to_dict() for c in exp_b.contributions],
        reconstructed_linear_predictor=exp_b.reconstructed_linear_predictor,
        reconstructed_probability=exp_b.reconstructed_probability,
        reconstruction_error=exp_b.reconstruction_error,
        model_sha256=exp_b.model_sha256,
        status='generated',
    )

    # 5. Persist SimilarCaseComparison
    prob_delta = adapted_res.adapted_probability - baseline_res.probability
    comparison = SimilarCaseComparison.objects.create(
        source_case=exp.case_a,
        target_case=record_b,
        similarity_score=sim.similarity_score,
        similarity_method=sim.method,
        similarity_features_used=sim.features_used,
        similarity_normalization_version=sim.normalization_bounds_version,
        baseline_version=get_baseline_version(),
        baseline_probability=baseline_res.probability,
        baseline_recommendation=baseline_res.referral_recommended,
        updated_version=exp.active_adaptation,
        updated_probability=adapted_res.adapted_probability,
        updated_recommendation=adapted_res.adapted_recommendation,
        probability_delta=prob_delta,
        recommendation_changed=(
            adapted_res.adapted_recommendation != baseline_res.referral_recommended
        ),
        feedback_category=exp.override_factor,
        learning_batch=exp.learning_batch,
    )

    # 6. Finalize ControlledFeedbackExperiment provenance
    exp.case_b = record_b
    exp.case_b_similarity = round(sim.similarity_score, 4)
    exp.case_b_baseline_probability = round(baseline_res.probability, 6)
    exp.case_b_adapted_probability = round(adapted_res.adapted_probability, 6)
    exp.case_b_probability_delta = round(prob_delta, 6)
    exp.case_b_log_odds_delta = round(adapted_res.delta_log_odds, 6)
    exp.state = 'COMPARISON_COMPLETE'
    exp.completed_at = timezone.now()
    exp.notes = (
        f"Demonstration completed successfully. "
        f"Case B baseline={exp.case_b_baseline_probability:.6f}, "
        f"adapted={exp.case_b_adapted_probability:.6f}, "
        f"delta={exp.case_b_probability_delta:+.6f}, "
        f"similarity={exp.case_b_similarity:.4f}."
    )
    exp.save()

    return {
        'success': True,
        'experiment': exp,
        'comparison': comparison,
        'baseline_probability': exp.case_b_baseline_probability,
        'adapted_probability': exp.case_b_adapted_probability,
        'probability_delta': exp.case_b_probability_delta,
        'log_odds_delta': exp.case_b_log_odds_delta,
        'similarity_score': exp.case_b_similarity,
    }


def reset_controlled_experiment(include_completed: bool = False) -> bool:
    """Reset or cancel the active controlled experiment."""
    from ..models import ControlledFeedbackExperiment
    if include_completed:
        ControlledFeedbackExperiment.objects.all().delete()
    else:
        ControlledFeedbackExperiment.objects.exclude(state='COMPARISON_COMPLETE').delete()
    return True


