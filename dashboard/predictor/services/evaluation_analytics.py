"""
Evaluation Analytics Service (Protocol E1 v1.0.3 / E2).

Centralized, deterministic aggregate analytics for the participant evaluation study.
Derived strictly from db_evaluation.sqlite3 models:
- EvaluationRespondent
- EvaluationSession
- EvaluationEvent
- QuestionnaireResponse
- ScreeningRecord (evaluation-linked cases)

RESEARCH GOVERNANCE & EPISTEMIC PRINCIPLES:
1. 0 ML/GAM/XAI executions, 0 model evaluations, 0 database mutations during computation.
2. Distinct respondent counts are strictly decoupled from session counts (one respondent may have multiple sessions).
3. Valid Respondent follows E1 Protocol §6.1 (complete instrument) and §6.2 (pre-specified exclusion criteria).
4. Division-by-zero protection: rates return None or 0.0 with explicit display guards.
5. Practice case P0 is explicitly segregated and excluded from real evaluation intake counts.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import math

from django.db.models import Count, Q, Avg, Min, Max, StdDev
from django.utils import timezone

from ..models import (
    EvaluationRespondent,
    EvaluationSession,
    EvaluationEvent,
    QuestionnaireResponse,
    ScreeningRecord,
    HumanReview,
    Stage2Assessment,
)


OPERATIONAL_RECRUITMENT_TARGET = 40  # Protocol target cohort size (NOT a statistical power threshold)


@dataclass(frozen=True)
class MetricRate:
    numerator: int
    denominator: int
    percentage: Optional[float]

    @classmethod
    def compute(cls, num: int, den: int) -> 'MetricRate':
        pct = round((num / den) * 100.0, 1) if den > 0 else None
        return cls(numerator=num, denominator=den, percentage=pct)


@dataclass(frozen=True)
class EvaluationOverviewSnapshot:
    total_respondents: int
    total_sessions: int
    sessions_in_progress: int
    sessions_completed: int
    sessions_abandoned: int
    sessions_excluded: int
    
    questionnaires_started: int
    questionnaires_submitted: int
    questionnaires_completed: int
    questionnaires_incomplete: int

    full_evaluation_completed_sessions: int
    full_evaluation_completed_respondents: int

    valid_research_respondents: int
    target_respondents: int
    target_progress_pct: Optional[float]

    session_completion_rate: MetricRate
    respondent_completion_rate: MetricRate
    questionnaire_submission_rate: MetricRate

    # Component Completion
    comprehension_completed_count: int
    sus_completed_count: int
    clarity_completed_count: int
    open_ended_completed_count: int

    # Psychometric Summaries
    mean_sus_score: Optional[float]
    median_sus_score: Optional[float]
    min_sus_score: Optional[float]
    max_sus_score: Optional[float]
    std_sus_score: Optional[float]

    mean_comprehension_score: Optional[float]
    median_comprehension_score: Optional[float]
    min_comprehension_score: Optional[int]
    max_comprehension_score: Optional[int]

    # Timeline
    earliest_submission: Optional[datetime]
    latest_submission: Optional[datetime]
    daily_submissions: List[Dict[str, Any]]

    # Excluded sessions audit log
    excluded_sessions: List[Dict[str, Any]]


def compute_median(numbers: List[float]) -> Optional[float]:
    """Compute median from a list of numbers."""
    if not numbers:
        return None
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    mid = n // 2
    if n % 2 == 1:
        return float(sorted_nums[mid])
    return float((sorted_nums[mid - 1] + sorted_nums[mid]) / 2.0)


def compute_valid_respondent_status(session: EvaluationSession) -> Dict[str, Any]:
    """
    Evaluates valid respondent criteria according to E1_ANALYSIS_PLAN.md §6.1 & §6.2:
    1. Consent given (§6.1)
    2. Completed questionnaire submitted (§6.1)
    3. Session completed (§6.1)
    4. Not marked as excluded under pre-specified §6.2 criteria (technical failure, procedural error, etc.)
    """
    if not session.respondent.consent_given:
        return {
            'is_valid': False,
            'status_code': 'CONSENT_NOT_GIVEN',
            'status_display': 'Consent was not provided',
        }

    if session.is_excluded:
        return {
            'is_valid': False,
            'status_code': 'PROTOCOL_EXCLUDED',
            'status_display': f"Excluded per protocol §6.2 ({session.get_exclusion_reason_display()})",
            'exclusion_reason': session.exclusion_reason,
            'exclusion_notes': session.exclusion_notes,
        }

    if session.status != 'completed' or not session.questionnaire_completed:
        return {
            'is_valid': False,
            'status_code': 'INCOMPLETE_QUESTIONNAIRE',
            'status_display': 'Questionnaire or session incomplete',
        }

    return {
        'is_valid': True,
        'status_code': 'VALID',
        'status_display': 'Valid Research Respondent',
    }


def compute_evaluation_analytics(include_excluded: bool = False) -> EvaluationOverviewSnapshot:
    """
    Computes all research evaluation metrics strictly from evaluation database tables.
    Read-only: 0 writes, 0 ML, 0 external calls.
    """
    # 1. Respondent Counts
    total_respondents = EvaluationRespondent.objects.count()

    # 2. Session Aggregates
    session_agg = EvaluationSession.objects.aggregate(
        total=Count('id'),
        in_progress=Count('id', filter=Q(status='in_progress')),
        completed=Count('id', filter=Q(status='completed')),
        abandoned=Count('id', filter=Q(status='abandoned')),
        excluded=Count('id', filter=Q(is_excluded=True)),
        q_completed=Count('id', filter=Q(questionnaire_completed=True)),
        q_incomplete=Count('id', filter=Q(questionnaire_completed=False)),
    )
    total_sessions = session_agg['total'] or 0
    sessions_in_progress = session_agg['in_progress'] or 0
    sessions_completed = session_agg['completed'] or 0
    sessions_abandoned = session_agg['abandoned'] or 0
    sessions_excluded = session_agg['excluded'] or 0
    questionnaires_completed = session_agg['q_completed'] or 0
    questionnaires_incomplete = session_agg['q_incomplete'] or 0

    # 3. Questionnaire Progress (Event-backed + Record-backed)
    questionnaires_started = (
        EvaluationEvent.objects.filter(event_name='questionnaire_started')
        .values('session_id')
        .distinct()
        .count()
    )
    questionnaires_submitted = QuestionnaireResponse.objects.count()

    # 4. Full Evaluation Completion
    # Criteria: Session status='completed', practice_completed=True, questionnaire_completed=True, is_excluded=False
    full_eval_sessions_qs = EvaluationSession.objects.filter(
        status='completed',
        practice_completed=True,
        questionnaire_completed=True,
        is_excluded=False,
    )
    full_evaluation_completed_sessions = full_eval_sessions_qs.count()
    full_evaluation_completed_respondents = (
        full_eval_sessions_qs.values('respondent_id').distinct().count()
    )

    # 5. Valid Research Respondents (E1 Protocol §6.1 & §6.2)
    # A respondent is VALID if they consented, completed at least one session with complete questionnaire,
    # and their completed session is NOT marked as excluded under §6.2 criteria.
    valid_respondents_qs = EvaluationRespondent.objects.filter(
        consent_given=True,
        sessions__status='completed',
        sessions__questionnaire_completed=True,
        sessions__is_excluded=False,
    ).distinct()
    valid_research_respondents = valid_respondents_qs.count()

    target_respondents = OPERATIONAL_RECRUITMENT_TARGET
    target_progress_pct = (
        round((valid_research_respondents / target_respondents) * 100.0, 1)
        if target_respondents > 0
        else None
    )

    # 6. Completion Rates
    # A. Session Completion Rate: completed sessions / total started sessions
    session_completion_rate = MetricRate.compute(sessions_completed, total_sessions)
    # B. Respondent Completion Rate: respondents with >=1 completed session / total registered respondents
    completed_resp_count = (
        EvaluationSession.objects.filter(status='completed')
        .values('respondent_id')
        .distinct()
        .count()
    )
    respondent_completion_rate = MetricRate.compute(completed_resp_count, total_respondents)
    # C. Questionnaire Submission Rate: questionnaires submitted / questionnaires started
    questionnaire_submission_rate = MetricRate.compute(
        questionnaires_submitted, questionnaires_started
    )

    # 7. Questionnaire Component Counts & Psychometric Stats
    # When include_excluded is False, exclude responses from protocol-excluded sessions
    q_qs = QuestionnaireResponse.objects.all()
    if not include_excluded:
        q_qs = q_qs.filter(session__is_excluded=False)

    q_responses = list(q_qs)

    comp_completed_count = sum(1 for q in q_responses if q.comprehension_score is not None)
    sus_completed_count = sum(1 for q in q_responses if q.sus_score is not None)
    clarity_completed_count = sum(1 for q in q_responses if q.clarity_1 is not None)
    open_ended_completed_count = sum(
        1 for q in q_responses if bool((q.open_1 or "").strip() or (q.open_2 or "").strip() or (q.open_3 or "").strip())
    )

    # SUS Statistics
    sus_scores = [q.sus_score for q in q_responses if q.sus_score is not None]
    if sus_scores:
        mean_sus = round(sum(sus_scores) / len(sus_scores), 2)
        med_sus = round(compute_median(sus_scores), 2)
        min_sus = round(min(sus_scores), 1)
        max_sus = round(max(sus_scores), 1)
        if len(sus_scores) > 1:
            variance = sum((x - mean_sus) ** 2 for x in sus_scores) / (len(sus_scores) - 1)
            std_sus = round(math.sqrt(variance), 2)
        else:
            std_sus = 0.0
    else:
        mean_sus = None
        med_sus = None
        min_sus = None
        max_sus = None
        std_sus = None

    # Comprehension Statistics
    comp_scores = [q.comprehension_score for q in q_responses if q.comprehension_score is not None]
    if comp_scores:
        mean_comp = round(sum(comp_scores) / len(comp_scores), 2)
        med_comp = round(compute_median([float(x) for x in comp_scores]), 1)
        min_comp = min(comp_scores)
        max_comp = max(comp_scores)
    else:
        mean_comp = None
        med_comp = None
        min_comp = None
        max_comp = None

    # 8. Timeline Breakdown
    submission_dates = [q.submitted_at for q in q_responses if q.submitted_at]
    earliest_sub = min(submission_dates) if submission_dates else None
    latest_sub = max(submission_dates) if submission_dates else None

    # Daily aggregation
    daily_map: Dict[str, int] = {}
    for dt in submission_dates:
        d_str = dt.strftime('%Y-%m-%d')
        daily_map[d_str] = daily_map.get(d_str, 0) + 1

    daily_submissions = [
        {'date': k, 'count': daily_map[k]}
        for k in sorted(daily_map.keys())
    ]

    # 9. Excluded Sessions Audit List
    excluded_qs = EvaluationSession.objects.filter(is_excluded=True).select_related('respondent')
    excluded_sessions = [
        {
            'session_id': str(s.id),
            'respondent_code': s.respondent.respondent_code,
            'reason_code': s.exclusion_reason,
            'reason_display': s.get_exclusion_reason_display() if s.exclusion_reason else "Unspecified",
            'notes': s.exclusion_notes,
            'excluded_at': s.excluded_at,
        }
        for s in excluded_qs
    ]

    return EvaluationOverviewSnapshot(
        total_respondents=total_respondents,
        total_sessions=total_sessions,
        sessions_in_progress=sessions_in_progress,
        sessions_completed=sessions_completed,
        sessions_abandoned=sessions_abandoned,
        sessions_excluded=sessions_excluded,
        questionnaires_started=questionnaires_started,
        questionnaires_submitted=questionnaires_submitted,
        questionnaires_completed=questionnaires_completed,
        questionnaires_incomplete=questionnaires_incomplete,
        full_evaluation_completed_sessions=full_evaluation_completed_sessions,
        full_evaluation_completed_respondents=full_evaluation_completed_respondents,
        valid_research_respondents=valid_research_respondents,
        target_respondents=target_respondents,
        target_progress_pct=target_progress_pct,
        session_completion_rate=session_completion_rate,
        respondent_completion_rate=respondent_completion_rate,
        questionnaire_submission_rate=questionnaire_submission_rate,
        comprehension_completed_count=comp_completed_count,
        sus_completed_count=sus_completed_count,
        clarity_completed_count=clarity_completed_count,
        open_ended_completed_count=open_ended_completed_count,
        mean_sus_score=mean_sus,
        median_sus_score=med_sus,
        min_sus_score=min_sus,
        max_sus_score=max_sus,
        std_sus_score=std_sus,
        mean_comprehension_score=mean_comp,
        median_comprehension_score=med_comp,
        min_comprehension_score=min_comp,
        max_comprehension_score=max_comp,
        earliest_submission=earliest_sub,
        latest_submission=latest_sub,
        daily_submissions=daily_submissions,
        excluded_sessions=excluded_sessions,
    )
