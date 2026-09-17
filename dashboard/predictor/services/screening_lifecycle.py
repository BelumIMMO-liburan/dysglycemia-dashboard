"""
Screening Case Lifecycle Service (Phase D2.9).

Centralized, deterministic lifecycle-state derivation for the two-stage screening cascade:
Stage-1 Non-Lab Intake -> Frozen GAM -> GAM Additive XAI -> Human Review -> Stage-2 HbA1c

RESEARCH & EPISTEMIC GOVERNANCE RULES:
1. Zero ML execution: 0 GAM calls, 0 preprocessing calls, 0 XAI calculations.
2. Read-only derivation: 0 database writes. Lifecycle states are DERIVED from persisted entities.
3. No mutable status column in ScreeningRecord.
4. Deterministic precedence hierarchy.
5. Strict distinction between workflow state and clinical/laboratory state.
6. Clear separation between AI Recommendation and Final Human Decision.
7. Stage-2 distinction: "Not applicable" vs "Pending" vs "Completed".
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


# Standard lifecycle codes
STATE_EXPLANATION_UNAVAILABLE = "explanation_unavailable"
STATE_PENDING_REVIEW = "pending_review"
STATE_REVIEWED_NO_REFERRAL = "reviewed_no_referral"
STATE_PENDING_STAGE2 = "pending_stage2"
STATE_COMPLETED_STAGE2 = "completed_stage2"
STATE_INTEGRITY_ERROR = "integrity_error"

ALL_LIFECYCLE_STATES = [
    STATE_EXPLANATION_UNAVAILABLE,
    STATE_PENDING_REVIEW,
    STATE_REVIEWED_NO_REFERRAL,
    STATE_PENDING_STAGE2,
    STATE_COMPLETED_STAGE2,
    STATE_INTEGRITY_ERROR,
]

# Stage-2 status codes
STAGE2_NOT_APPLICABLE = "not_applicable"
STAGE2_PENDING = "pending"
STAGE2_COMPLETED = "completed"
STAGE2_UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ScreeningLifecycleState:
    """
    Immutable representation of the derived workflow state for a screening case.
    Describes application workflow, NOT patient biology or clinical disease state.
    """
    code: str
    label: str
    actionable: bool
    action_type: str  # 'review', 'stage2', 'none', 'system_attention', 'integrity_error'
    action_url_name: Optional[str]
    action_label: Optional[str]
    stage2_status_code: str  # 'not_applicable', 'pending', 'completed', 'unavailable'
    stage2_status_label: str
    badge_variant: str  # 'warning', 'primary', 'success', 'secondary', 'destructive', 'slate'
    summary_text: str
    integrity_issues: Tuple[str, ...] = ()

    @property
    def is_pending_review(self) -> bool:
        return self.code == STATE_PENDING_REVIEW

    @property
    def is_pending_stage2(self) -> bool:
        return self.code == STATE_PENDING_STAGE2

    @property
    def is_explanation_unavailable(self) -> bool:
        return self.code == STATE_EXPLANATION_UNAVAILABLE

    @property
    def is_completed(self) -> bool:
        return self.code == STATE_COMPLETED_STAGE2

    @property
    def is_reviewed_no_referral(self) -> bool:
        return self.code == STATE_REVIEWED_NO_REFERRAL


def audit_record_integrity(record) -> List[str]:
    """
    Audit a ScreeningRecord and its relations for logically impossible states.
    Returns a list of diagnostic issue strings, empty if consistent.
    """
    issues = []
    if record is None:
        issues.append("ScreeningRecord is null or does not exist.")
        return issues

    explanation = getattr(record, 'explanation', None)
    human_review = getattr(record, 'human_review', None)
    stage2 = getattr(human_review, 'stage2_assessment', None) if human_review else None

    # Audit Rule 1: HumanReview accepted but final decision differs from AI recommendation
    if human_review and human_review.review_action == 'accepted':
        if human_review.final_referral_recommended != record.ai_referral_recommended:
            issues.append(
                f"Accepted review has final_referral_recommended={human_review.final_referral_recommended} "
                f"which conflicts with ai_referral_recommended={record.ai_referral_recommended}."
            )

    # Audit Rule 2: HumanReview overridden but final decision equals AI recommendation
    if human_review and human_review.review_action == 'overridden':
        if human_review.final_referral_recommended == record.ai_referral_recommended:
            issues.append(
                f"Overridden review has final_referral_recommended={human_review.final_referral_recommended} "
                f"which matches ai_referral_recommended={record.ai_referral_recommended}."
            )

    # Audit Rule 3: Stage2Assessment exists but final referral decision is False (Do Not Refer)
    if stage2 and human_review and not human_review.final_referral_recommended:
        issues.append(
            f"Stage2Assessment exists (ID: {stage2.id}) but HumanReview final referral recommendation is False."
        )

    # Audit Rule 4: Stage2Assessment exists but HumanReview is missing
    # (Relational constraint protects this at DB level, but checked for completeness)
    if hasattr(record, '_stage2_orphaned') and record._stage2_orphaned:
        issues.append("Stage2Assessment found without parent HumanReview.")

    # Audit Rule 5: HumanReview exists when explanation was marked failed or absent
    if human_review and (not explanation or explanation.status != 'generated'):
        issues.append(
            "HumanReview exists despite missing or ungenerated ScreeningExplanation."
        )

    return issues


def derive_screening_lifecycle(record) -> ScreeningLifecycleState:
    """
    Centralized deterministic lifecycle-state derivation.

    PRECEDENCE HIERARCHY:
    0. Logical data integrity check -> 'integrity_error'
    1. Explanation missing or status != 'generated' -> 'explanation_unavailable'
    2. HumanReview absent -> 'pending_review'
    3. HumanReview.final_referral_recommended is False -> 'reviewed_no_referral'
    4. Stage2Assessment absent -> 'pending_stage2'
    5. Stage2Assessment present -> 'completed_stage2'
    """
    if record is None:
        return ScreeningLifecycleState(
            code=STATE_INTEGRITY_ERROR,
            label="Record Missing",
            actionable=False,
            action_type="integrity_error",
            action_url_name=None,
            action_label=None,
            stage2_status_code=STAGE2_UNAVAILABLE,
            stage2_status_label="—",
            badge_variant="destructive",
            summary_text="Screening record could not be found.",
            integrity_issues=("Record does not exist.",),
        )

    # Check for logical inconsistencies first
    integrity_issues = audit_record_integrity(record)
    if integrity_issues:
        logger.error(f"Integrity error on ScreeningRecord {record.id}: {integrity_issues}")
        return ScreeningLifecycleState(
            code=STATE_INTEGRITY_ERROR,
            label="Data Integrity Issue",
            actionable=False,
            action_type="integrity_error",
            action_url_name=None,
            action_label=None,
            stage2_status_code=STAGE2_UNAVAILABLE,
            stage2_status_label="—",
            badge_variant="destructive",
            summary_text="Data integrity check failed: conflicting relational entities detected.",
            integrity_issues=tuple(integrity_issues),
        )

    explanation = getattr(record, 'explanation', None)
    human_review = getattr(record, 'human_review', None)
    stage2 = getattr(human_review, 'stage2_assessment', None) if human_review else None

    # Precedence 1: Faithful Explanation Available?
    if not explanation or explanation.status != 'generated':
        return ScreeningLifecycleState(
            code=STATE_EXPLANATION_UNAVAILABLE,
            label="Needs System Attention",
            actionable=False,
            action_type="system_attention",
            action_url_name=None,
            action_label=None,
            stage2_status_code=STAGE2_UNAVAILABLE,
            stage2_status_label="—",
            badge_variant="warning",
            summary_text="Model explanation is unavailable. Human review is locked under evidence-first protocol.",
        )

    # Precedence 2: Human Review Completed?
    if not human_review:
        return ScreeningLifecycleState(
            code=STATE_PENDING_REVIEW,
            label="Pending Human Review",
            actionable=True,
            action_type="review",
            action_url_name="predictor:screening_result",
            action_label="Review",
            stage2_status_code=STAGE2_UNAVAILABLE,
            stage2_status_label="—",
            badge_variant="warning",
            summary_text="Stage-1 screening evaluated. Awaiting human review before referral.",
        )

    # Precedence 3: Final Human Referral Recommended?
    if not human_review.final_referral_recommended:
        return ScreeningLifecycleState(
            code=STATE_REVIEWED_NO_REFERRAL,
            label="Reviewed — No Stage 2",
            actionable=False,
            action_type="none",
            action_url_name="predictor:screening_result",
            action_label="View Case",
            stage2_status_code=STAGE2_NOT_APPLICABLE,
            stage2_status_label="Not applicable",
            badge_variant="secondary",
            summary_text="Human review finalized with 'Do not refer'. Stage 2 is not indicated.",
        )

    # Precedence 4: Stage-2 HbA1c Confirmed?
    if not stage2:
        return ScreeningLifecycleState(
            code=STATE_PENDING_STAGE2,
            label="Pending Stage 2",
            actionable=True,
            action_type="stage2",
            action_url_name="predictor:stage2",
            action_label="Enter HbA1c",
            stage2_status_code=STAGE2_PENDING,
            stage2_status_label="Pending",
            badge_variant="primary",
            summary_text="Final human decision recommended referral. Awaiting Stage-2 HbA1c laboratory entry.",
        )

    # Precedence 5: Completed Two-Stage Cascade
    return ScreeningLifecycleState(
        code=STATE_COMPLETED_STAGE2,
        label="Completed Two-Stage",
        actionable=False,
        action_type="none",
        action_url_name="predictor:screening_result",
        action_label="View Case",
        stage2_status_code=STAGE2_COMPLETED,
        stage2_status_label="Completed",
        badge_variant="success",
        summary_text="Two-stage cascade complete. Stage-2 laboratory range documented.",
    )
