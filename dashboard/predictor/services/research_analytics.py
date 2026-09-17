"""
Research Analytics Service (Phase D2.10).

Centralized, deterministic aggregate research analytics derived strictly from
authoritative persisted screening records (ScreeningRecord, ScreeningExplanation,
HumanReview, Stage2Assessment).

RESEARCH GOVERNANCE & EPISTEMIC PRINCIPLES:
1. Pure read-only aggregation: 0 database writes, 0 timestamp changes.
2. Zero ML/XAI execution: 0 GAM calls, 0 preprocessing calls, 0 XAI calls, 0 HbA1c reclassifications.
3. Every metric has an explicit numerator, denominator, and inclusion criteria.
4. Human-AI agreement is concordance between machine recommendation and clinician disposition,
   NOT predictive accuracy or clinical ground truth.
5. Human override reflects clinician decision behavior and structured rationale,
   NOT machine error or clinical mistake.
6. Stage-2 HbA1c is selectively observed only for cases that reached a final human REFER decision.
   Therefore, operational Stage-2 data MUST NOT be used to compute predictive performance metrics,
   discriminative curves, or classification correctness (verification bias safeguard).
7. Division-by-zero protection: rates with zero denominator return None, displayed as "Not available" / "—".
8. Legacy entities (Prediction, Override) and development datasets are strictly excluded.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
import logging

from django.db.models import Count, Q, QuerySet
from ..models import (
    ScreeningRecord,
    HumanReview,
    Stage2Assessment,
    OVERRIDE_REASONS_REFER_TO_NO_REFER,
    OVERRIDE_REASONS_NO_REFER_TO_REFER,
    ALL_OVERRIDE_REASONS_DICT,
)

logger = logging.getLogger(__name__)


# Structured reason display dictionary with clean human-readable labels
HUMAN_READABLE_REASON_LABELS: Dict[str, str] = {
    'additional_context_reduces_concern': 'Additional context reduces concern',
    'additional_context_increases_concern': 'Additional context increases concern',
    'input_quality_concern': 'Input quality or measurement concern',
    'repeat_assessment_preferred': 'Repeat assessment preferred',
    'precautionary_referral': 'Precautionary referral',
    'other': 'Other clinical rationale',
}


def get_reason_label(code: str) -> str:
    """Return human-readable label for a structured override reason code."""
    return HUMAN_READABLE_REASON_LABELS.get(code, ALL_OVERRIDE_REASONS_DICT.get(code, code))


@dataclass(frozen=True)
class DecisionTransitionMatrix:
    """
    2x2 Human-AI Decision Transition Matrix.
    Rows: AI Recommendation (Refer, Do not refer)
    Columns: Final Human Decision (Refer, Do not refer)
    Scoped exclusively to REVIEWED cases (N_reviewed).
    """
    ai_refer_human_refer: int       # Accepted referral (Agreement)
    ai_refer_human_no_refer: int    # Override away from referral (Override)
    ai_no_refer_human_no_refer: int # Accepted non-referral (Agreement)
    ai_no_refer_human_refer: int    # Override toward referral (Override)

    @property
    def total_cells(self) -> int:
        return (
            self.ai_refer_human_refer
            + self.ai_refer_human_no_refer
            + self.ai_no_refer_human_no_refer
            + self.ai_no_refer_human_refer
        )

    @property
    def diagonal_sum(self) -> int:
        """Total agreement count."""
        return self.ai_refer_human_refer + self.ai_no_refer_human_no_refer

    @property
    def off_diagonal_sum(self) -> int:
        """Total override count."""
        return self.ai_refer_human_no_refer + self.ai_no_refer_human_refer


@dataclass(frozen=True)
class OverrideReasonSummary:
    """Distribution of a single structured override reason category."""
    code: str
    label: str
    count: int
    rate: Optional[float]  # None if denominator is zero


@dataclass(frozen=True)
class ResearchAnalyticsSnapshot:
    """
    Deterministic, immutable contract for aggregate research analytics.
    Calculated strictly from persisted records.
    """
    # Population & Intake Volume
    total_screenings: int
    ai_refer_count: int
    ai_no_refer_count: int
    ai_refer_rate: Optional[float]

    # Review Eligibility & Protocol Completion
    review_eligible_count: int
    explanation_unavailable_count: int
    explanation_generated_count: int
    explanation_availability_rate: Optional[float]
    reviewed_count: int
    review_completion_rate: Optional[float]

    # Human-AI Agreement & Override Disposition
    accepted_count: int
    overridden_count: int
    agreement_rate: Optional[float]
    override_rate: Optional[float]

    # Final Human Referral Decisions
    final_refer_count: int
    final_no_refer_count: int
    final_referral_rate: Optional[float]

    # Stage-2 Cascade Completion
    stage2_eligible_count: int
    stage2_completed_count: int
    stage2_completion_rate: Optional[float]

    # 2x2 Decision Transition Summary
    transition_matrix: DecisionTransitionMatrix

    # Override Direction
    override_away_count: int      # AI Refer -> Human No Refer
    override_toward_count: int    # AI No Refer -> Human Refer
    override_away_rate: Optional[float]
    override_toward_rate: Optional[float]

    # Structured Override Reason Distributions
    reasons_refer_to_no_refer: List[OverrideReasonSummary]
    reasons_no_refer_to_refer: List[OverrideReasonSummary]
    all_override_reasons: List[OverrideReasonSummary]

    # Observed Stage-2 HbA1c Range Distribution
    stage2_normal_count: int
    stage2_prediabetes_count: int
    stage2_diabetes_count: int
    stage2_normal_rate: Optional[float]
    stage2_prediabetes_rate: Optional[float]
    stage2_diabetes_rate: Optional[float]

    # Date Filter Metadata
    date_from: Optional[date]
    date_to: Optional[date]

    # Data Integrity Audit
    data_integrity_passed: bool
    data_integrity_warnings: List[str] = field(default_factory=list)


def safe_rate(numerator: int, denominator: int) -> Optional[float]:
    """
    Compute percentage rate (0.0 to 100.0) safely.
    Strictly returns None when denominator is 0.
    Never substitutes 0.0 for an undefined division.
    """
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100.0, 1)


def compute_research_analytics(
    queryset: Optional[QuerySet] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> ResearchAnalyticsSnapshot:
    """
    Compute all research-safe aggregate analytics from authoritative ScreeningRecord rows.

    Parameters:
        queryset: Optional base ScreeningRecord queryset (defaults to ScreeningRecord.objects.all()).
        date_from: Optional inclusive start date for ScreeningRecord.created_at.
        date_to: Optional inclusive end date for ScreeningRecord.created_at.

    Returns:
        Immutable ResearchAnalyticsSnapshot containing all verified metrics.
    """
    if queryset is None:
        queryset = ScreeningRecord.objects.all()

    # Apply date filters consistently to primary ScreeningRecord intake date
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)

    # 1. Primary Aggregate Query (1 bounded SQL query across the joined cascade)
    agg = queryset.aggregate(
        total_screenings=Count('id'),
        ai_refer_count=Count('id', filter=Q(ai_referral_recommended=True)),
        ai_no_refer_count=Count('id', filter=Q(ai_referral_recommended=False)),
        review_eligible_count=Count('id', filter=Q(explanation__status='generated')),
        explanation_unavailable_count=Count(
            'id', filter=~Q(explanation__status='generated') | Q(explanation__isnull=True)
        ),
        reviewed_count=Count('id', filter=Q(human_review__isnull=False)),
        accepted_count=Count('id', filter=Q(human_review__review_action='accepted')),
        overridden_count=Count('id', filter=Q(human_review__review_action='overridden')),
        final_refer_count=Count('id', filter=Q(human_review__final_referral_recommended=True)),
        final_no_refer_count=Count('id', filter=Q(human_review__final_referral_recommended=False)),
        # 2x2 Decision Transition Cells (reviewed cases only)
        trans_refer_refer=Count(
            'id',
            filter=Q(
                human_review__isnull=False,
                ai_referral_recommended=True,
                human_review__final_referral_recommended=True,
            ),
        ),
        trans_refer_no_refer=Count(
            'id',
            filter=Q(
                human_review__isnull=False,
                ai_referral_recommended=True,
                human_review__final_referral_recommended=False,
            ),
        ),
        trans_no_refer_no_refer=Count(
            'id',
            filter=Q(
                human_review__isnull=False,
                ai_referral_recommended=False,
                human_review__final_referral_recommended=False,
            ),
        ),
        trans_no_refer_refer=Count(
            'id',
            filter=Q(
                human_review__isnull=False,
                ai_referral_recommended=False,
                human_review__final_referral_recommended=True,
            ),
        ),
        # Stage 2 completion & ranges
        stage2_completed_count=Count('id', filter=Q(human_review__stage2_assessment__isnull=False)),
        stage2_normal_count=Count(
            'id', filter=Q(human_review__stage2_assessment__laboratory_range='normal_range')
        ),
        stage2_prediabetes_count=Count(
            'id', filter=Q(human_review__stage2_assessment__laboratory_range='prediabetes_range')
        ),
        stage2_diabetes_count=Count(
            'id', filter=Q(human_review__stage2_assessment__laboratory_range='diabetes_range')
        ),
    )

    total_screenings = agg['total_screenings'] or 0
    ai_refer_count = agg['ai_refer_count'] or 0
    ai_no_refer_count = agg['ai_no_refer_count'] or 0
    review_eligible_count = agg['review_eligible_count'] or 0
    explanation_unavailable_count = agg['explanation_unavailable_count'] or 0
    explanation_generated_count = review_eligible_count
    reviewed_count = agg['reviewed_count'] or 0
    accepted_count = agg['accepted_count'] or 0
    overridden_count = agg['overridden_count'] or 0
    final_refer_count = agg['final_refer_count'] or 0
    final_no_refer_count = agg['final_no_refer_count'] or 0

    trans_refer_refer = agg['trans_refer_refer'] or 0
    trans_refer_no_refer = agg['trans_refer_no_refer'] or 0
    trans_no_refer_no_refer = agg['trans_no_refer_no_refer'] or 0
    trans_no_refer_refer = agg['trans_no_refer_refer'] or 0

    stage2_completed_count = agg['stage2_completed_count'] or 0
    stage2_normal_count = agg['stage2_normal_count'] or 0
    stage2_prediabetes_count = agg['stage2_prediabetes_count'] or 0
    stage2_diabetes_count = agg['stage2_diabetes_count'] or 0

    # Denominators per Specification
    # 1. AI Referral Rate Denominator: N_screenings
    ai_refer_rate = safe_rate(ai_refer_count, total_screenings)

    # 2. Explanation Availability Rate Denominator: N_screenings
    explanation_availability_rate = safe_rate(explanation_generated_count, total_screenings)

    # 3. Review Completion Rate Denominator: N_review_eligible
    review_completion_rate = safe_rate(reviewed_count, review_eligible_count)

    # 4. Human-AI Agreement Rate Denominator: N_reviewed
    agreement_rate = safe_rate(accepted_count, reviewed_count)

    # 5. Override Rate Denominator: N_reviewed
    override_rate = safe_rate(overridden_count, reviewed_count)

    # 6. Final Human Referral Rate Denominator: N_reviewed
    final_referral_rate = safe_rate(final_refer_count, reviewed_count)

    # 7. Stage-2 Completion Rate Denominator: N_stage2_eligible = N_final_refer
    stage2_eligible_count = final_refer_count
    stage2_completion_rate = safe_rate(stage2_completed_count, stage2_eligible_count)

    # 8. Observed Stage-2 Laboratory Range Denominator: N_stage2_completed
    stage2_normal_rate = safe_rate(stage2_normal_count, stage2_completed_count)
    stage2_prediabetes_rate = safe_rate(stage2_prediabetes_count, stage2_completed_count)
    stage2_diabetes_rate = safe_rate(stage2_diabetes_count, stage2_completed_count)

    # Decision Transition Matrix
    transition_matrix = DecisionTransitionMatrix(
        ai_refer_human_refer=trans_refer_refer,
        ai_refer_human_no_refer=trans_refer_no_refer,
        ai_no_refer_human_no_refer=trans_no_refer_no_refer,
        ai_no_refer_human_refer=trans_no_refer_refer,
    )

    # Override Direction: Denominator is N_overridden
    override_away_count = trans_refer_no_refer
    override_toward_count = trans_no_refer_refer
    override_away_rate = safe_rate(override_away_count, overridden_count)
    override_toward_rate = safe_rate(override_toward_count, overridden_count)

    # 2. Query 2: Structured Override Reasons Distribution (1 bounded query)
    reason_rows = (
        HumanReview.objects.filter(
            screening_record__in=queryset,
            review_action='overridden',
        )
        .values('override_reason_code', 'screening_record__ai_referral_recommended')
        .annotate(count=Count('id'))
    )

    # Aggregate counts by branch and overall
    refer_to_no_refer_counts: Dict[str, int] = {}
    no_refer_to_refer_counts: Dict[str, int] = {}
    all_reasons_dict: Dict[str, int] = {}

    for row in reason_rows:
        code = row['override_reason_code'] or 'unknown'
        cnt = row['count']
        ai_rec = row['screening_record__ai_referral_recommended']
        all_reasons_dict[code] = all_reasons_dict.get(code, 0) + cnt
        if ai_rec:
            refer_to_no_refer_counts[code] = refer_to_no_refer_counts.get(code, 0) + cnt
        else:
            no_refer_to_refer_counts[code] = no_refer_to_refer_counts.get(code, 0) + cnt

    # Build branch summaries preserving documented order
    reasons_refer_to_no_refer = []
    for code, _ in OVERRIDE_REASONS_REFER_TO_NO_REFER:
        c = refer_to_no_refer_counts.get(code, 0)
        r = safe_rate(c, override_away_count)
        reasons_refer_to_no_refer.append(
            OverrideReasonSummary(
                code=code,
                label=get_reason_label(code),
                count=c,
                rate=r,
            )
        )

    reasons_no_refer_to_refer = []
    for code, _ in OVERRIDE_REASONS_NO_REFER_TO_REFER:
        c = no_refer_to_refer_counts.get(code, 0)
        r = safe_rate(c, override_toward_count)
        reasons_no_refer_to_refer.append(
            OverrideReasonSummary(
                code=code,
                label=get_reason_label(code),
                count=c,
                rate=r,
            )
        )

    all_override_reasons = []
    # Combine all unique codes from taxonomy
    seen_codes = set()
    for code, _ in OVERRIDE_REASONS_REFER_TO_NO_REFER + OVERRIDE_REASONS_NO_REFER_TO_REFER:
        if code in seen_codes:
            continue
        seen_codes.add(code)
        c = all_reasons_dict.get(code, 0)
        r = safe_rate(c, overridden_count)
        all_override_reasons.append(
            OverrideReasonSummary(
                code=code,
                label=get_reason_label(code),
                count=c,
                rate=r,
            )
        )

    # 3. Data Integrity & Invariant Audit
    warnings = []
    if reviewed_count > review_eligible_count:
        warnings.append(
            f"Integrity alert: Reviewed cases ({reviewed_count}) exceed review-eligible cases ({review_eligible_count})."
        )

    if (accepted_count + overridden_count) != reviewed_count:
        warnings.append(
            f"Invariant violation: Accepted ({accepted_count}) + Overridden ({overridden_count}) != Reviewed ({reviewed_count})."
        )

    if transition_matrix.total_cells != reviewed_count:
        warnings.append(
            f"Invariant violation: Transition matrix sum ({transition_matrix.total_cells}) != Reviewed ({reviewed_count})."
        )

    if transition_matrix.diagonal_sum != accepted_count:
        warnings.append(
            f"Invariant violation: Transition diagonal ({transition_matrix.diagonal_sum}) != Accepted ({accepted_count})."
        )

    if transition_matrix.off_diagonal_sum != overridden_count:
        warnings.append(
            f"Invariant violation: Transition off-diagonal ({transition_matrix.off_diagonal_sum}) != Overridden ({overridden_count})."
        )

    if stage2_completed_count > stage2_eligible_count:
        warnings.append(
            f"Invariant violation: Completed Stage-2 ({stage2_completed_count}) exceeds eligible referrals ({stage2_eligible_count})."
        )

    range_sum = stage2_normal_count + stage2_prediabetes_count + stage2_diabetes_count
    if range_sum != stage2_completed_count:
        warnings.append(
            f"Invariant violation: Stage-2 range categories sum ({range_sum}) != Completed Stage-2 ({stage2_completed_count})."
        )

    total_reason_count = sum(all_reasons_dict.values())
    if total_reason_count != overridden_count:
        warnings.append(
            f"Invariant violation: Sum of override reasons ({total_reason_count}) != Overridden count ({overridden_count})."
        )

    for w in warnings:
        logger.warning("ResearchAnalyticsService data integrity warning: %s", w)

    return ResearchAnalyticsSnapshot(
        total_screenings=total_screenings,
        ai_refer_count=ai_refer_count,
        ai_no_refer_count=ai_no_refer_count,
        ai_refer_rate=ai_refer_rate,
        review_eligible_count=review_eligible_count,
        explanation_unavailable_count=explanation_unavailable_count,
        explanation_generated_count=explanation_generated_count,
        explanation_availability_rate=explanation_availability_rate,
        reviewed_count=reviewed_count,
        review_completion_rate=review_completion_rate,
        accepted_count=accepted_count,
        overridden_count=overridden_count,
        agreement_rate=agreement_rate,
        override_rate=override_rate,
        final_refer_count=final_refer_count,
        final_no_refer_count=final_no_refer_count,
        final_referral_rate=final_referral_rate,
        stage2_eligible_count=stage2_eligible_count,
        stage2_completed_count=stage2_completed_count,
        stage2_completion_rate=stage2_completion_rate,
        transition_matrix=transition_matrix,
        override_away_count=override_away_count,
        override_toward_count=override_toward_count,
        override_away_rate=override_away_rate,
        override_toward_rate=override_toward_rate,
        reasons_refer_to_no_refer=reasons_refer_to_no_refer,
        reasons_no_refer_to_refer=reasons_no_refer_to_refer,
        all_override_reasons=all_override_reasons,
        stage2_normal_count=stage2_normal_count,
        stage2_prediabetes_count=stage2_prediabetes_count,
        stage2_diabetes_count=stage2_diabetes_count,
        stage2_normal_rate=stage2_normal_rate,
        stage2_prediabetes_rate=stage2_prediabetes_rate,
        stage2_diabetes_rate=stage2_diabetes_rate,
        date_from=date_from,
        date_to=date_to,
        data_integrity_passed=(len(warnings) == 0),
        data_integrity_warnings=warnings,
    )
