"""
Model Versioning Service for Human Feedback Learning Loop.

Manages the lifecycle of model versions:
  baseline (GAM-v1) → candidate (adaptation trained) → validated → active → rolled_back

DESIGN PRINCIPLES:
1. The frozen GAM artifact is NEVER modified. Only the adaptation layer changes.
2. Exactly ONE version may have is_active=True at any time.
3. The baseline (GAM-v1) is always recoverable.
4. Historical predictions are NEVER recalculated when versions change.
5. Every prediction records the version label used.

VERSION LIFECYCLE:
  baseline     — The original frozen GAM with no adaptation layer.
  candidate    — A new adaptation layer has been trained but not yet validated.
  active       — Passed validation and is used for new predictions.
  rejected     — Failed validation; preserved for audit.
  rolled_back  — Was active but was rolled back to a previous version.
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

# Baseline version label constant
BASELINE_VERSION_LABEL = "GAM-v1"

# Synthetic test cases for technical validation (strictly non-final-test cases)
SYNTHETIC_VALIDATION_CASES: List[Dict[str, Any]] = [
    {
        "age": 45,
        "sex": "male",
        "bmi": 28.5,
        "waist_cm": 92.0,
        "hypertension_history": "no",
        "smoking_history": "no",
        "sedentary_minutes_day": 360,
    },
    {
        "age": 62,
        "sex": "female",
        "bmi": 34.2,
        "waist_cm": 102.0,
        "hypertension_history": "yes",
        "smoking_history": "yes",
        "sedentary_minutes_day": 600,
    },
    {
        "age": 35,
        "sex": "female",
        "bmi": 22.0,
        "waist_cm": 74.0,
        "hypertension_history": "no",
        "smoking_history": "no",
        "sedentary_minutes_day": 240,
    },
    {
        "age": 55,
        "sex": "male",
        "bmi": 32.1,
        "waist_cm": 105.0,
        "hypertension_history": "yes",
        "smoking_history": "yes",
        "sedentary_minutes_day": 580,
    },
]


def _compute_file_sha256(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def ensure_baseline_version():
    """
    Ensure the baseline GAM-v1 ModelVersion record exists.
    Creates it if absent. Idempotent.
    """
    from ..models import ModelVersion

    existing = ModelVersion.objects.filter(version_label=BASELINE_VERSION_LABEL).first()
    if existing:
        return existing

    with transaction.atomic():
        existing = ModelVersion.objects.filter(version_label=BASELINE_VERSION_LABEL).first()
        if existing:
            return existing

        baseline = ModelVersion.objects.create(
            version_label=BASELINE_VERSION_LABEL,
            version_type="baseline",
            description=(
                "Original frozen Phase-5 GAM (λ=10.0, Splines=10). "
                "No adaptation layer. Threshold 0.1389. "
                "This is the immutable research baseline."
            ),
            base_model_sha256="204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d",
            adaptation_artifact_path="",
            adaptation_sha256="",
            feedback_count_used=0,
            training_data_description="No adaptation training data (pure frozen GAM baseline).",
            validation_status="not_applicable",
            is_active=True,
            activated_at=timezone.now(),
        )
        logger.info(f"Created baseline ModelVersion: {baseline.version_label}")
        return baseline


def get_active_version():
    """
    Return the currently active ModelVersion.
    If none exists, ensures and returns the baseline.
    """
    from ..models import ModelVersion

    active = ModelVersion.objects.filter(is_active=True).first()
    if active:
        return active
    return ensure_baseline_version()


def get_baseline_version():
    """Return the baseline GAM-v1 version (always exists)."""
    return ensure_baseline_version()


def get_version_by_label(label: str):
    """Return a ModelVersion by its label, or None."""
    from ..models import ModelVersion
    return ModelVersion.objects.filter(version_label=label).first()


def create_candidate_version(
    parent_label: str,
    candidate_label: str,
    adaptation_path: str,
    feedback_count: int,
    description: str = "",
) -> "ModelVersion":
    """
    Create a new candidate ModelVersion.

    The candidate is NOT active until validated and explicitly activated.
    """
    from ..models import ModelVersion

    parent = get_version_by_label(parent_label)
    if parent is None and parent_label == BASELINE_VERSION_LABEL:
        parent = ensure_baseline_version()
    if parent is None:
        raise ValueError(f"Parent version '{parent_label}' not found.")

    if ModelVersion.objects.filter(version_label=candidate_label).exists():
        raise ValueError(f"Version label '{candidate_label}' already exists.")

    adaptation_sha = ""
    if adaptation_path and Path(adaptation_path).exists():
        adaptation_sha = _compute_file_sha256(adaptation_path)

    with transaction.atomic():
        candidate = ModelVersion.objects.create(
            version_label=candidate_label,
            version_type="candidate",
            parent_version=parent,
            description=description or f"Candidate derived from {parent_label}",
            base_model_sha256=parent.base_model_sha256,
            adaptation_artifact_path=adaptation_path,
            adaptation_sha256=adaptation_sha,
            feedback_count_used=feedback_count,
            training_data_description=f"Trained on {feedback_count} eligible feedback records.",
            validation_status="pending",
            is_active=False,
        )
        logger.info(f"Created candidate ModelVersion: {candidate.version_label}")
        return candidate


def validate_candidate(
    version_label: str,
    metrics: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Run 13 rigorous executable technical validation checks on a candidate version.
    Uses actual synthetic test cases and checks actual inference behavior.
    
    13 Executable Checks:
    1. Artifact exists on disk.
    2. Artifact loads successfully as a valid dictionary.
    3. Artifact SHA-256 matches stored SHA-256.
    4. Model input dimensions match the 8 adaptation features.
    5. Expected Stage-1 feature names are present.
    6. Same input produces identical output repeatedly (deterministic inference).
    7. Output probabilities on test cases are within [0.0, 1.0].
    8. Actual adaptation deltas are within ±2.0 log-odds bound.
    9. Frozen GAM hash is unchanged (204a94ff...).
    10. Decision threshold remains locked at exactly 0.1389.
    11. Both baseline and adapted outputs can be produced for each case.
    12. Candidate inference does not mutate historical prediction records.
    13. Candidate inference does not modify the frozen GAM artifact file.

    Returns True if ALL 13 checks pass, False otherwise.
    """
    from ..models import ModelVersion, ScreeningRecord
    from .screening_inference import (
        EXPECTED_GAM_SHA256,
        FROZEN_DECISION_THRESHOLD,
        get_artifact_paths,
    )
    from .feedback_learning import (
        load_adaptation_model,
        compute_adaptation_delta,
        ADAPTATION_FEATURE_NAMES,
        MAX_DELTA_LOG_ODDS,
    )
    from .adapted_inference import predict_adapted

    version = get_version_by_label(version_label)
    if version is None:
        raise ValueError(f"Version '{version_label}' not found.")

    if version.version_type != "candidate":
        raise ValueError(f"Version '{version_label}' is not a candidate (type={version.version_type}).")

    checks_passed = True
    validation_details: Dict[str, Any] = {"checks": []}

    def _record_check(name: str, passed: bool, details: Dict[str, Any]):
        nonlocal checks_passed
        if not passed:
            checks_passed = False
        validation_details["checks"].append({
            "check": name,
            "passed": passed,
            **details,
        })

    # Baseline paths
    gam_path = get_artifact_paths()["gam"]

    # Pre-inference state capture for immutability assertions (Checks 12 & 13)
    record_count_before = ScreeningRecord.objects.count()
    first_record_before = None
    if record_count_before > 0:
        r0 = ScreeningRecord.objects.first()
        first_record_before = (r0.id, float(r0.screening_probability), bool(r0.ai_referral_recommended))

    gam_sha_before = _compute_file_sha256(str(gam_path))
    gam_size_before = gam_path.stat().st_size

    # --- Check 1: Artifact exists ---
    artifact_path = Path(version.adaptation_artifact_path)
    exists = artifact_path.exists()
    _record_check("artifact_exists", exists, {"path": str(artifact_path)})

    # --- Check 2: Artifact loads successfully ---
    adaptation = None
    loads_success = False
    if exists:
        adaptation = load_adaptation_model(str(artifact_path))
        loads_success = adaptation is not None and "model" in adaptation
    _record_check("artifact_loads_successfully", loads_success, {"loaded": loads_success})

    # --- Check 3: Artifact SHA-256 matches stored SHA-256 ---
    sha_match = False
    actual_sha = ""
    if exists:
        actual_sha = _compute_file_sha256(str(artifact_path))
        sha_match = (actual_sha == version.adaptation_sha256)
    _record_check("artifact_sha256_matches", sha_match, {
        "expected": version.adaptation_sha256,
        "actual": actual_sha,
    })

    # --- Check 4: Model input dimensions are correct (8 features) ---
    dim_correct = False
    if adaptation and "model" in adaptation:
        model_obj = adaptation["model"]
        if hasattr(model_obj, "coef_"):
            dim_correct = (len(model_obj.coef_) == len(ADAPTATION_FEATURE_NAMES))
    _record_check("model_input_dimensions_correct", dim_correct, {
        "expected_dim": len(ADAPTATION_FEATURE_NAMES),
        "actual_dim": len(adaptation["model"].coef_) if dim_correct else None,
    })

    # --- Check 5: Expected Stage-1 feature names are present ---
    feat_names_match = False
    if adaptation and "feature_names" in adaptation:
        feat_names_match = (adaptation["feature_names"] == ADAPTATION_FEATURE_NAMES)
    _record_check("expected_feature_names_present", feat_names_match, {
        "expected": ADAPTATION_FEATURE_NAMES,
        "actual": adaptation.get("feature_names") if adaptation else None,
    })

    # --- Run inference checks on synthetic cases ---
    all_deterministic = True
    all_prob_valid = True
    all_delta_bounded = True
    all_dual_produced = True

    if loads_success:
        # --- Check 6: Deterministic inference (repeatable identical output) ---
        sample_case = SYNTHETIC_VALIDATION_CASES[0]
        res1 = predict_adapted(sample_case, version_label=version_label)
        res2 = predict_adapted(sample_case, version_label=version_label)
        all_deterministic = (
            abs(res1.adapted_probability - res2.adapted_probability) < 1e-12
            and abs(res1.delta_log_odds - res2.delta_log_odds) < 1e-12
            and res1.adapted_recommendation == res2.adapted_recommendation
        )

        # --- Checks 7, 8, 11 across all synthetic cases ---
        for sc in SYNTHETIC_VALIDATION_CASES:
            res = predict_adapted(sc, version_label=version_label)
            # Check 7: Probability in [0, 1]
            if not (0.0 <= res.adapted_probability <= 1.0):
                all_prob_valid = False
            # Check 8: Delta bounded
            if abs(res.delta_log_odds) > MAX_DELTA_LOG_ODDS:
                all_delta_bounded = False
            # Check 11: Dual outputs produced
            if res.baseline_probability is None or res.adapted_probability is None:
                all_dual_produced = False
    else:
        all_deterministic = False
        all_prob_valid = False
        all_delta_bounded = False
        all_dual_produced = False

    _record_check("repeatable_deterministic_inference", all_deterministic, {})
    _record_check("output_probabilities_in_range", all_prob_valid, {"range": "[0.0, 1.0]"})
    _record_check("actual_adaptation_deltas_bounded", all_delta_bounded, {"max_bound": MAX_DELTA_LOG_ODDS})
    _record_check("dual_outputs_produced", all_dual_produced, {})

    # --- Check 9: Frozen GAM hash is unchanged ---
    current_gam_sha = _compute_file_sha256(str(gam_path))
    gam_hash_ok = (current_gam_sha == EXPECTED_GAM_SHA256)
    _record_check("frozen_gam_hash_unchanged", gam_hash_ok, {
        "expected": EXPECTED_GAM_SHA256,
        "actual": current_gam_sha,
    })

    # --- Check 10: Threshold remains exactly 0.1389 ---
    threshold_ok = (FROZEN_DECISION_THRESHOLD == 0.1389)
    _record_check("threshold_remains_exact", threshold_ok, {
        "expected": 0.1389,
        "actual": FROZEN_DECISION_THRESHOLD,
    })

    # --- Check 12: Candidate inference does not mutate historical prediction records ---
    record_count_after = ScreeningRecord.objects.count()
    records_unmutated = (record_count_after == record_count_before)
    if records_unmutated and first_record_before is not None:
        r0_after = ScreeningRecord.objects.get(id=first_record_before[0])
        records_unmutated = (
            float(r0_after.screening_probability) == first_record_before[1]
            and bool(r0_after.ai_referral_recommended) == first_record_before[2]
        )
    _record_check("historical_records_unmutated", records_unmutated, {
        "count_before": record_count_before,
        "count_after": record_count_after,
    })

    # --- Check 13: Candidate inference does not modify the frozen model artifact ---
    gam_sha_after = _compute_file_sha256(str(gam_path))
    gam_size_after = gam_path.stat().st_size
    gam_unmodified = (gam_sha_after == gam_sha_before and gam_size_after == gam_size_before)
    _record_check("frozen_gam_artifact_unmodified", gam_unmodified, {
        "size_before": gam_size_before,
        "size_after": gam_size_after,
    })

    # Save validation details to candidate
    if metrics:
        validation_details["supplied_metrics"] = metrics

    version.validation_status = "passed" if checks_passed else "failed"
    version.validation_metrics = validation_details
    if not checks_passed:
        version.version_type = "rejected"
    version.save()

    logger.info(
        f"Validation for {version_label}: {'PASSED (13/13)' if checks_passed else 'FAILED'}"
    )
    return checks_passed


def activate_version(version_label: str) -> bool:
    """
    Activate a validated candidate version.
    Deactivates the currently active version.

    Returns True if successful.
    """
    from ..models import ModelVersion

    version = get_version_by_label(version_label)
    if version is None:
        raise ValueError(f"Version '{version_label}' not found.")

    if version.validation_status != "passed":
        raise ValueError(
            f"Cannot activate version '{version_label}' — "
            f"validation_status is '{version.validation_status}', expected 'passed'."
        )

    now = timezone.now()

    with transaction.atomic():
        # Deactivate all currently active versions
        active_versions = ModelVersion.objects.filter(is_active=True)
        for av in active_versions:
            av.is_active = False
            av.deactivated_at = now
            if av.version_type == "active":
                av.version_type = "rolled_back"
            av.save()

        # Activate the new version
        if version.version_label.endswith("-candidate"):
            clean_label = version.version_label[:-10]
            if not ModelVersion.objects.filter(version_label=clean_label).exclude(id=version.id).exists():
                version.version_label = clean_label
        version.is_active = True
        version.version_type = "active"
        version.activated_at = now
        version.save()

    logger.info(f"Activated ModelVersion: {version_label}")
    return True


def rollback_to_version(target_label: str) -> bool:
    """
    Rollback to a specified version (typically the baseline GAM-v1).
    Deactivates the current active version and activates the target.
    """
    from ..models import ModelVersion

    target = get_version_by_label(target_label)
    if target is None:
        raise ValueError(f"Rollback target '{target_label}' not found.")

    now = timezone.now()

    with transaction.atomic():
        # Deactivate all currently active versions
        active_versions = ModelVersion.objects.filter(is_active=True)
        for av in active_versions:
            av.is_active = False
            av.deactivated_at = now
            if av.version_type == "active":
                av.version_type = "rolled_back"
            av.save()

        # Activate the target version
        target.is_active = True
        if target.version_type in ("baseline",):
            pass  # Keep baseline type
        else:
            target.version_type = "active"
        target.activated_at = now
        target.deactivated_at = None
        target.save()

    logger.info(f"Rolled back to ModelVersion: {target_label}")
    return True


def get_version_history() -> list:
    """Return all model versions ordered by creation time."""
    from ..models import ModelVersion
    return list(ModelVersion.objects.all().order_by('-created_at'))


def get_model_status_summary() -> Dict[str, Any]:
    """
    Return the standardized model and adaptation status display according to research terminology:
      - Baseline Model: GAM-v1 · Frozen
      - Active Adaptation: RA-vX · Validated & Active (or 'None')
      - Candidate Adaptation: RA-vY · Pending Validation (or 'None')
    """
    from ..models import ModelVersion

    active_adaptation = ModelVersion.objects.filter(
        is_active=True
    ).exclude(version_label=BASELINE_VERSION_LABEL).first()

    candidate_adaptation = ModelVersion.objects.filter(
        version_type='candidate'
    ).first()

    active_display = (
        f"{active_adaptation.version_label} · Validated & Active"
        if active_adaptation else "None"
    )
    candidate_display = (
        f"{candidate_adaptation.version_label} · Pending Validation"
        if candidate_adaptation else "None"
    )

    return {
        "baseline_model": "GAM-v1 · Frozen",
        "active_adaptation": active_display,
        "candidate_adaptation": candidate_display,
        "raw_active_adaptation": active_adaptation,
        "raw_candidate_adaptation": candidate_adaptation,
    }

