import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.db import transaction
from django.utils import timezone
from .models import (
    Prediction, Override, ScreeningRecord, ScreeningExplanation, HumanReview,
    Stage2Assessment,
    ControlledFeedbackExperiment,
    OVERRIDE_REASONS_REFER_TO_NO_REFER, OVERRIDE_REASONS_NO_REFER_TO_REFER,
    ALL_OVERRIDE_REASONS_DICT,
    EvaluationRespondent, EvaluationSession, EvaluationEvent, QuestionnaireResponse,
)
import uuid
from decimal import Decimal
try:
    from . import model_loader
except Exception:
    model_loader = None

try:
    from . import shap_explainer
except Exception:
    shap_explainer = None

import json
import csv
import traceback
from pathlib import Path

logger = logging.getLogger(__name__)

from .decorators import require_app_mode, require_researcher_access
from .forms import (
    Stage1ScreeningForm, HumanReviewAcceptForm, HumanReviewOverrideForm,
    Stage2EntryForm, Stage2ConfirmForm,
    EvaluationConsentForm, DashboardQuestionnaireForm,
)
from .screening_schema import STAGE1_INPUT_SCHEMA
from .services.hba1c_range import classify_hba1c_range
from .services.screening_lifecycle import (
    derive_screening_lifecycle,
    audit_record_integrity,
    STATE_EXPLANATION_UNAVAILABLE,
    STATE_PENDING_REVIEW,
    STATE_REVIEWED_NO_REFERRAL,
    STATE_PENDING_STAGE2,
    STATE_COMPLETED_STAGE2,
    STATE_INTEGRITY_ERROR,
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from .services.research_analytics import compute_research_analytics


def _log_eval_event(request, event_name, event_data=None):
    """Helper to log evaluation events if an active EvaluationSession exists in request.session."""
    token = request.session.get('evaluation_session_token')
    if not token:
        return
    try:
        session = EvaluationSession.objects.filter(session_token=token, status='in_progress').first()
        if session:
            EvaluationEvent.objects.create(
                session=session,
                event_name=event_name,
                event_data=event_data or {}
            )
    except Exception as e:
        logger.warning(f"Could not log evaluation event {event_name}: {e}")


def check_evaluation_onboarding(request):
    """
    Enforces evaluation protocol prerequisite gates (Consent -> Practice P0).
    Returns an HttpResponse redirect if a prerequisite is unfulfilled, or None.
    """
    if getattr(settings, 'APP_MODE', 'feedback_lab').lower() != 'evaluation':
        return None
    token = request.session.get('evaluation_session_token')
    session = EvaluationSession.objects.filter(session_token=token).first() if token else None
    if not session:
        return redirect('predictor:evaluation_consent')
    if not session.practice_completed:
        return redirect('predictor:evaluation_practice')
    if session.questionnaire_completed:
        return redirect('predictor:evaluation_complete')
    return None


def overview_view(request):
    """
    Research screening overview — primary orientation page (Phase D2.9).
    Consumes persisted ScreeningRecord entities and derived lifecycle states.
    Zero ML/XAI execution, zero database writes.
    """
    gate_redirect = check_evaluation_onboarding(request)
    if gate_redirect:
        return gate_redirect

    records = list(
        ScreeningRecord.objects.select_related('explanation', 'human_review__stage2_assessment')
        .order_by('-created_at')
    )
    total_screenings = len(records)

    pending_reviews = 0
    pending_stage2 = 0
    completed_screenings = 0
    reviewed_no_stage2 = 0
    system_attention = 0

    records_with_lifecycle = []
    for r in records:
        lc = derive_screening_lifecycle(r)
        records_with_lifecycle.append({'record': r, 'lifecycle': lc})
        if lc.is_pending_review:
            pending_reviews += 1
        elif lc.is_pending_stage2:
            pending_stage2 += 1
        elif lc.is_completed:
            completed_screenings += 1
        elif lc.is_reviewed_no_referral:
            reviewed_no_stage2 += 1
        elif lc.is_explanation_unavailable:
            system_attention += 1

    reviewed_count = total_screenings - pending_reviews - system_attention

    context = {
        'total': total_screenings,
        'pending_reviews': pending_reviews,
        'pending_stage2': pending_stage2,
        'reviewed': reviewed_count,
        'completed': completed_screenings,
        'system_attention': system_attention,
        'total_actionable': pending_reviews + pending_stage2,
        'recent_cases': records_with_lifecycle[:5],
    }
    return render(request, 'predictor/overview.html', context)


import logging
logger = logging.getLogger(__name__)

from .services import screening_inference, screening_explanation


def new_screening_view(request):
    """
    Stage-1 Non-Laboratory Screening form.
    Validates the 7 locked predictors and presents an Input Review State.
    Does NOT execute model inference or persist prediction records in Phase D2.2.
    """
    gate_redirect = check_evaluation_onboarding(request)
    if gate_redirect:
        return gate_redirect

    is_validated = False
    sanitized_summary = None
    error_count = 0

    if request.GET.get('simulate_error') == '1':
        dummy_data = {
            'age': 52, 'sex': 'male', 'bmi': 28.4, 'waist_cm': 98.5,
            'hypertension_history': 'yes', 'smoking_history': 'no', 'sedentary_minutes_day': 480
        }
        form = Stage1ScreeningForm(initial=dummy_data)
        context = {
            'form': form,
            'is_validated': True,
            'sanitized_summary': [
                {'canonical_name': 'age', 'label': 'Age', 'display_value': '52 years'},
                {'canonical_name': 'sex', 'label': 'Biological Sex', 'display_value': 'Male'},
                {'canonical_name': 'bmi', 'label': 'Body Mass Index (BMI)', 'display_value': '28.4 kg/m²'},
                {'canonical_name': 'waist_cm', 'label': 'Waist Circumference', 'display_value': '98.5 cm'},
                {'canonical_name': 'hypertension_history', 'label': 'History of Hypertension', 'display_value': 'Yes'},
                {'canonical_name': 'smoking_history', 'label': 'Smoking History', 'display_value': 'No'},
                {'canonical_name': 'sedentary_minutes_day', 'label': 'Sedentary Time', 'display_value': '480 minutes/day'},
            ],
            'inference_error': "Screening inference execution error: Model artifact hash verification failed. Inference halted defensively.",
            'schema': STAGE1_INPUT_SCHEMA,
            'raw_post_data': None,
        }
        return render(request, 'predictor/new_screening.html', context)

    idempotency_token = None
    if request.method == 'POST':
        form = Stage1ScreeningForm(request.POST)
        if form.is_valid():
            is_validated = True
            sanitized_summary = form.get_sanitized_summary()
            idempotency_token = uuid.uuid4().hex
        else:
            error_count = len(form.errors)
    else:
        form = Stage1ScreeningForm()

    context = {
        'form': form,
        'is_validated': is_validated,
        'sanitized_summary': sanitized_summary,
        'error_count': error_count,
        'schema': STAGE1_INPUT_SCHEMA,
        'raw_post_data': request.POST if request.method == 'POST' else None,
        'idempotency_token': idempotency_token,
    }
    return render(request, 'predictor/new_screening.html', context)


def run_screening_view(request):
    """
    Execute Stage-1 screening inference using the frozen GAM adapter
    and atomically persist an immutable ScreeningRecord (Phase D2.4).
    Redirects via HTTP 302 to the stable screening_result view.
    """
    if request.method != 'POST':
        return redirect('predictor:new_screening')

    # Re-validate inputs rigorously from POST data (never trust hidden client inputs)
    form = Stage1ScreeningForm(request.POST)
    if not form.is_valid():
        context = {
            'form': form,
            'is_validated': False,
            'error_count': len(form.errors),
            'schema': STAGE1_INPUT_SCHEMA,
            'raw_post_data': request.POST,
        }
        return render(request, 'predictor/new_screening.html', context)

    sanitized_summary = form.get_sanitized_summary()
    idempotency_token = request.POST.get('idempotency_token', '').strip()

    # Double-submission protection: if token already exists, redirect to existing result
    if idempotency_token:
        existing_record = ScreeningRecord.objects.filter(idempotency_token=idempotency_token).first()
        if existing_record:
            return redirect('predictor:screening_result', screening_id=existing_record.id)

    # 1. Execute Inference (verified D2.3 service is the SOLE inference authority)
    try:
        if request.POST.get('_simulate_error') == '1':
            raise screening_inference.ScreeningInferenceError("Simulated model adapter integrity failure: Hash verification check failed.")
        inference_result = screening_inference.predict_screening(form.cleaned_data)
    except Exception as e:
        logger.error(f"Screening inference error: {e}", exc_info=True)
        context = {
            'form': form,
            'is_validated': True,
            'sanitized_summary': sanitized_summary,
            'inference_error': "Screening could not be completed. Please try again or contact the study administrator.",
            'schema': STAGE1_INPUT_SCHEMA,
            'raw_post_data': request.POST,
            'idempotency_token': idempotency_token,
        }
        return render(request, 'predictor/new_screening.html', context)

    # 2. Atomic Database Persistence for ScreeningRecord
    try:
        if request.POST.get('_simulate_db_error') == '1':
            raise RuntimeError("Simulated database write failure for verification.")

        # Resolve active evaluation session if operating in participant evaluation flow
        eval_session = None
        eval_token = request.session.get('evaluation_session_token')
        if eval_token:
            eval_session = EvaluationSession.objects.filter(session_token=eval_token, status='in_progress').first()

        with transaction.atomic():
            record = ScreeningRecord.objects.create(
                age=form.cleaned_data['age'],
                sex=form.cleaned_data['sex'],
                bmi=form.cleaned_data['bmi'],
                waist_cm=form.cleaned_data['waist_cm'],
                hypertension_history=form.cleaned_data['hypertension_history'],
                smoking_history=form.cleaned_data['smoking_history'],
                sedentary_minutes_day=form.cleaned_data['sedentary_minutes_day'],
                screening_probability=inference_result.screening_probability,
                ai_referral_recommended=inference_result.referral_recommended,
                decision_threshold=Decimal(str(inference_result.threshold)),
                model_name=inference_result.model_name,
                model_sha256=screening_inference.EXPECTED_GAM_SHA256,
                preprocessor_sha256=screening_inference.EXPECTED_PREPROCESSOR_SHA256,
                input_schema_version="1.0",
                idempotency_token=idempotency_token if idempotency_token else None,
                evaluation_session=eval_session,
            )
    except Exception as db_err:
        logger.error(f"Failed to persist ScreeningRecord: {db_err}", exc_info=True)
        context = {
            'form': form,
            'is_validated': True,
            'sanitized_summary': sanitized_summary,
            'inference_error': "The screening result could not be saved. Please try again.",
            'schema': STAGE1_INPUT_SCHEMA,
            'raw_post_data': request.POST,
            'idempotency_token': idempotency_token,
        }
        return render(request, 'predictor/new_screening.html', context)

    # 2b. Compute and Persist GAM-Native Additive Explanation (Phase D2.5)
    # Critical Architecture Invariant: ScreeningRecord is ALREADY committed.
    # An explanation generation/persistence failure MUST NOT rollback or delete ScreeningRecord.
    try:
        if request.POST.get('_simulate_explanation_error') == '1':
            raise screening_explanation.ExplanationFidelityError("Simulated explanation failure for verification.")
        exp_result = screening_explanation.explain_screening(form.cleaned_data)
        ScreeningExplanation.objects.create(
            screening_record=record,
            method=exp_result.method,
            method_version=exp_result.method_version,
            link_function=exp_result.link_function,
            intercept=exp_result.intercept,
            contributions_json=[c.to_dict() for c in exp_result.contributions],
            reconstructed_linear_predictor=exp_result.reconstructed_linear_predictor,
            reconstructed_probability=exp_result.reconstructed_probability,
            reconstruction_error=exp_result.reconstruction_error,
            model_sha256=exp_result.model_sha256,
            status='generated',
        )
    except Exception as exp_err:
        logger.error(f"Failed to generate ScreeningExplanation: {exp_err}", exc_info=True)
        try:
            ScreeningExplanation.objects.create(
                screening_record=record,
                method="gam_native_additive",
                method_version="1.0",
                link_function="logit",
                intercept=0.0,
                contributions_json=[],
                reconstructed_linear_predictor=0.0,
                reconstructed_probability=0.0,
                reconstruction_error=0.0,
                model_sha256=screening_inference.EXPECTED_GAM_SHA256,
                status='failed',
                failure_reason=str(exp_err),
            )
        except Exception as failed_save_err:
            logger.error(f"Could not persist failed explanation state: {failed_save_err}", exc_info=True)

    # 3. Post-Redirect-Get (302 Redirect to stable result detail route)
    if eval_session:
        _log_eval_event(request, 'stage1_completed', {
            'record_id': str(record.id),
            'probability': record.screening_probability,
            'ai_referral': record.ai_referral_recommended,
        })

    return redirect('predictor:screening_result', screening_id=record.id)


def screening_result_view(request, screening_id):
    """
    Stage-1 Screening Result Detail page (Phase D2.4 + D2.5).
    Retrieves the persisted ScreeningRecord by UUID and displays the authoritative result.
    NEVER re-executes machine learning inference or explanation computation.
    """
    record = get_object_or_404(ScreeningRecord, id=screening_id)

    input_summary = [
        {'label': 'Age', 'value': f"{record.age} years"},
        {'label': 'Biological Sex', 'value': record.get_sex_display()},
        {'label': 'Body Mass Index (BMI)', 'value': f"{record.bmi} kg/m²"},
        {'label': 'Waist Circumference', 'value': f"{record.waist_cm} cm"},
        {'label': 'History of Hypertension', 'value': record.get_hypertension_history_display()},
        {
            'label': 'Smoking History',
            'value': f"{record.get_smoking_history_display()} (≥100 cigarettes lifetime)" if record.smoking_history == 'yes' else record.get_smoking_history_display()
        },
        {'label': 'Sedentary Time', 'value': f"{record.sedentary_minutes_day} min/day ({record.sedentary_minutes_day / 60:.1f} hours/day)"},
    ]

    # Formatted GAM-native explanation factors (Phase D2.5)
    explanation = getattr(record, 'explanation', None)
    explanation_factors = []
    explanation_status = explanation.status if explanation else 'none'
    intercept = 0.0
    reconstruction_error = 0.0

    if explanation and explanation.status == 'generated':
        raw_contribs = explanation.contributions_json or []
        sorted_contribs = sorted(raw_contribs, key=lambda x: abs(x.get('contribution', 0.0)), reverse=True)
        max_abs = max([abs(x.get('contribution', 0.0)) for x in sorted_contribs], default=1.0)
        if max_abs == 0.0:
            max_abs = 1.0

        for item in sorted_contribs:
            val = item.get('contribution', 0.0)
            rel_pct = round((abs(val) / max_abs) * 100.0, 1)
            explanation_factors.append({
                'feature_name': item.get('feature_name'),
                'display_name': item.get('display_name'),
                'formatted_value': item.get('formatted_value'),
                'contribution': val,
                'abs_contribution': abs(val),
                'direction': item.get('direction', 'higher' if val >= 0 else 'lower'),
                'relative_width_percent': rel_pct,
            })
        intercept = explanation.intercept
        reconstruction_error = explanation.reconstruction_error

    human_review = getattr(record, 'human_review', None)
    stage2_assessment = getattr(human_review, 'stage2_assessment', None) if human_review else None
    explanation_faithful = bool(explanation and explanation.status == 'generated')
    review_error = request.session.pop('review_error', None)
    override_error = request.session.pop('override_error', None)
    stage2_error = request.session.pop('stage2_error', None)
    open_override_dialog = request.session.pop('open_override_dialog', False)
    review_form = HumanReviewAcceptForm()
    override_form = HumanReviewOverrideForm(ai_referral_recommended=record.ai_referral_recommended)
    from .forms import UnifiedHumanReviewForm
    unified_form = UnifiedHumanReviewForm()

    # Branch-specific reason taxonomy & opposite decision for UI presentation
    if record.ai_referral_recommended:
        branch_override_reasons = OVERRIDE_REASONS_REFER_TO_NO_REFER
        opposite_decision_text = "Do not refer at this time"
        opposite_decision_badge = "No Referral Recommended"
    else:
        branch_override_reasons = OVERRIDE_REASONS_NO_REFER_TO_REFER
        opposite_decision_text = "Refer for Stage-2 HbA1c assessment"
        opposite_decision_badge = "Refer for Stage-2 HbA1c"

    # Human Feedback & Similar Case Comparisons
    human_feedback = getattr(human_review, 'feedback', None) if human_review else None
    feedback_error = request.session.pop('feedback_error', None)
    experiment_message = request.session.pop('experiment_message', None)
    from .services.feedback_taxonomy import (
        get_active_categories,
        OVERRIDE_FACTOR_CHOICES,
        is_corrective_learning_factor,
    )
    feedback_categories = get_active_categories()
    feedback_form = None  # Standalone feedback form deprecated in favor of unified review

    override_factor_display = None
    is_corrective_signal = False
    if human_review and human_review.review_action == 'overridden':
        reason = human_review.override_reason_code
        override_factor_display = ALL_OVERRIDE_REASONS_DICT.get(reason, reason)
        is_corrective_signal = is_corrective_learning_factor(reason)

    is_feedback_lab = (getattr(settings, 'APP_MODE', 'feedback_lab').lower() == 'feedback_lab')

    from .models import SimilarCaseComparison
    similar_comparisons = list(
        SimilarCaseComparison.objects.filter(target_case=record)
        .select_related('source_case', 'baseline_version', 'updated_version')
        .order_by('-created_at')[:5]
    )

    context = {
        'record': record,
        'input_summary': input_summary,
        'explanation': explanation,
        'explanation_status': explanation_status,
        'explanation_factors': explanation_factors,
        'intercept': intercept,
        'reconstruction_error': reconstruction_error,
        'human_review': human_review,
        'stage2_assessment': stage2_assessment,
        'explanation_faithful': explanation_faithful,
        'review_error': review_error,
        'override_error': override_error,
        'stage2_error': stage2_error,
        'open_override_dialog': open_override_dialog,
        'review_form': review_form,
        'override_form': override_form,
        'unified_form': unified_form,
        'override_factor_choices': OVERRIDE_FACTOR_CHOICES,
        'override_factor_display': override_factor_display,
        'is_corrective_signal': is_corrective_signal,
        'is_feedback_lab': is_feedback_lab,
        'branch_override_reasons': branch_override_reasons,
        'opposite_decision_text': opposite_decision_text,
        'opposite_decision_badge': opposite_decision_badge,
        'human_feedback': human_feedback,
        'feedback_form': feedback_form,
        'feedback_categories': feedback_categories,
        'feedback_error': feedback_error,
        'experiment_message': experiment_message,
        'similar_comparisons': similar_comparisons,
        'active_exp': ControlledFeedbackExperiment.objects.filter(case_a=record).order_by('-created_at').first(),
    }
    return render(request, 'predictor/screening_result.html', context)


def unified_review_view(request, screening_id):
    """
    Finalize a human review in a single, unified action (Accept or Override).
    Captures the decision, reviewer code, override factor / learning signal,
    and optional rationale without a secondary feedback submission step.
    """
    if request.method != 'POST':
        return redirect('predictor:screening_result', screening_id=screening_id)

    screening_record = get_object_or_404(ScreeningRecord, id=screening_id)

    # 1. Duplicate Review Protection
    if hasattr(screening_record, 'human_review') and screening_record.human_review is not None:
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 2. Explanation Prerequisite Enforcement
    explanation = getattr(screening_record, 'explanation', None)
    if not explanation or explanation.status != 'generated':
        request.session['review_error'] = (
            "Human review is unavailable because the model explanation for this screening could not be generated."
        )
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 3. Validate Unified Form
    from .forms import UnifiedHumanReviewForm
    form = UnifiedHumanReviewForm(request.POST)
    if not form.is_valid():
        first_err = None
        for field, errs in form.errors.items():
            if errs:
                first_err = errs[0]
                break
        request.session['review_error'] = first_err or "Invalid review submission."
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    reviewer_code = form.cleaned_data['reviewer_code']
    human_decision = form.cleaned_data['human_decision']
    override_factor = form.cleaned_data.get('override_factor')
    rationale = form.cleaned_data.get('rationale', '')
    target_feature = form.cleaned_data.get('target_feature') or request.POST.get('target_feature')
    signal_direction = form.cleaned_data.get('signal_direction') or request.POST.get('signal_direction')
    signal_scope = form.cleaned_data.get('signal_scope') or request.POST.get('signal_scope')

    try:
        from .services.feedback_learning import record_review_with_learning_signal
        review, feedback = record_review_with_learning_signal(
            screening_record=screening_record,
            reviewer_code=reviewer_code,
            human_decision=human_decision,
            override_factor=override_factor,
            rationale=rationale,
            target_feature=target_feature,
            signal_direction=signal_direction,
            signal_scope=signal_scope,
        )
        _log_eval_event(request, 'unified_review_submitted', {
            'record_id': str(screening_record.id),
            'action': review.review_action,
            'factor': override_factor,
            'has_feedback': feedback is not None,
            'is_eligible': feedback.is_eligible_for_learning if feedback else False,
        })
        _log_eval_event(request, 'human_review_completed', {
            'record_id': str(screening_record.id),
            'action': review.review_action,
            'final_referral': review.final_referral_recommended,
        })
        if review.review_action == 'overridden':
            _log_eval_event(request, 'override_recorded', {
                'record_id': str(screening_record.id),
                'reason': review.override_reason_code,
            })
    except Exception as e:
        logger.error(f"Failed to record unified review for {screening_record.id}: {e}", exc_info=True)
        request.session['review_error'] = f"The review could not be saved: {e}"

    return redirect('predictor:screening_result', screening_id=screening_record.id)


def accept_review_view(request, screening_id):
    """
    Finalize a human review by accepting the AI referral recommendation (Phase D2.6).

    GOVERNANCE RULES:
    1. POST-only route.
    2. Reviewer code must be valid anonymous alphanumeric identifier (max 32 chars).
    3. Final decision is DERIVED SERVER-SIDE from screening_record.ai_referral_recommended.
       Never trust client-supplied decision values.
    4. One finalized review per screening (OneToOneField + duplicate defense).
    5. Requires faithful explanation prerequisite (ScreeningExplanation.status == 'generated').
    6. Submitting review does NOT recalculate GAM or XAI.
    """
    if request.method != 'POST':
        return redirect('predictor:screening_result', screening_id=screening_id)

    screening_record = get_object_or_404(ScreeningRecord, id=screening_id)

    # 1. Duplicate Review Protection (Idempotent: redirect if already reviewed)
    if hasattr(screening_record, 'human_review'):
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 2. Explanation Prerequisite Enforcement
    explanation = getattr(screening_record, 'explanation', None)
    if not explanation or explanation.status != 'generated':
        request.session['review_error'] = "Human review is unavailable because the model explanation for this screening could not be generated."
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 3. Validate Reviewer Code
    form = HumanReviewAcceptForm(request.POST)
    if not form.is_valid():
        err_msg = form.errors.get('reviewer_code', ['Invalid reviewer code.'])[0]
        request.session['review_error'] = err_msg
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    cleaned_reviewer_code = form.cleaned_data['reviewer_code']

    # 4. Delegate to unified service helper
    try:
        from .services.feedback_learning import record_review_with_learning_signal
        review, feedback = record_review_with_learning_signal(
            screening_record=screening_record,
            reviewer_code=cleaned_reviewer_code,
            human_decision='accept',
        )
        _log_eval_event(request, 'human_review_completed', {
            'record_id': str(screening_record.id),
            'action': review.review_action,
            'final_referral': review.final_referral_recommended,
        })
    except Exception as e:
        logger.error(f"Failed to persist HumanReview for {screening_record.id}: {e}", exc_info=True)
        request.session['review_error'] = "The review could not be saved. Please try again."

    return redirect('predictor:screening_result', screening_id=screening_record.id)


def override_review_view(request, screening_id):
    """
    Finalize a human review by overriding the AI referral recommendation (Phase D2.7).

    GOVERNANCE RULES:
    1. POST-only route.
    2. Reviewer code must be valid anonymous alphanumeric identifier (max 32 chars).
    3. Final decision is DERIVED SERVER-SIDE as strict opposite of screening_record.ai_referral_recommended:
       final_referral_recommended = not screening_record.ai_referral_recommended
       Never trust client-supplied decision values.
    4. One finalized review per screening (OneToOneField + duplicate defense).
    5. Requires faithful explanation prerequisite (ScreeningExplanation.status == 'generated').
    6. Structured override reason required matching branch-specific taxonomy.
    7. Reason 'other' strictly requires contextual explanation in override_note (max 500 chars).
    8. Submitting override does NOT recalculate GAM or XAI.
    """
    if request.method != 'POST':
        return redirect('predictor:screening_result', screening_id=screening_id)

    screening_record = get_object_or_404(ScreeningRecord, id=screening_id)

    # 1. Duplicate Review Protection (Idempotent: redirect if already reviewed)
    if hasattr(screening_record, 'human_review'):
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 2. Explanation Prerequisite Enforcement
    explanation = getattr(screening_record, 'explanation', None)
    if not explanation or explanation.status != 'generated':
        request.session['review_error'] = "Human review is unavailable because the model explanation for this screening could not be generated."
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 3. Validate Override Form
    form = HumanReviewOverrideForm(request.POST, ai_referral_recommended=screening_record.ai_referral_recommended)
    if not form.is_valid():
        first_err = None
        for field, errs in form.errors.items():
            if errs:
                first_err = errs[0]
                break
        request.session['override_error'] = first_err or "Invalid override submission."
        request.session['open_override_dialog'] = True
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    cleaned_reviewer_code = form.cleaned_data['reviewer_code']
    cleaned_reason_code = form.cleaned_data['override_reason_code']
    cleaned_note = form.cleaned_data.get('override_note', '')
    target_feature = request.POST.get('target_feature')
    signal_direction = request.POST.get('signal_direction')
    signal_scope = request.POST.get('signal_scope')

    # 4. Delegate to unified service helper
    try:
        from .services.feedback_learning import record_review_with_learning_signal
        review, feedback = record_review_with_learning_signal(
            screening_record=screening_record,
            reviewer_code=cleaned_reviewer_code,
            human_decision='override',
            override_factor=cleaned_reason_code,
            rationale=cleaned_note,
            target_feature=target_feature,
            signal_direction=signal_direction,
            signal_scope=signal_scope,
        )
        _log_eval_event(request, 'human_review_completed', {
            'record_id': str(screening_record.id),
            'action': review.review_action,
            'final_referral': review.final_referral_recommended,
        })
        _log_eval_event(request, 'override_recorded', {
            'record_id': str(screening_record.id),
            'reason': review.override_reason_code,
        })
    except Exception as e:
        logger.error(f"Failed to persist HumanReview override for {screening_record.id}: {e}", exc_info=True)
        request.session['override_error'] = "The override could not be saved. Please try again."
        request.session['open_override_dialog'] = True

    return redirect('predictor:screening_result', screening_id=screening_record.id)


def stage2_view(request, screening_id):
    """
    Stage-2 HbA1c Laboratory Assessment workflow view (Phase D2.8).

    GOVERNANCE RULES:
    1. Requires existing ScreeningRecord.
    2. Requires faithful model explanation (explanation.status == 'generated').
    3. Requires finalized HumanReview.
    4. Only accessible if human_review.final_referral_recommended == True.
       If final referral is False, Stage 2 is strictly blocked (redirect with notice).
    5. If Stage2Assessment already exists, renders read-only completed result.
    6. GET: renders initial numeric input form.
    7. POST: validates HbA1c input, derives preview range server-side, renders Input Review state.
    8. Executes 0 GAM calls, 0 XAI calls, and does not mutate ScreeningRecord or HumanReview.
    """
    screening_record = get_object_or_404(ScreeningRecord, id=screening_id)

    # 1. Explanation Prerequisite Enforcement
    explanation = getattr(screening_record, 'explanation', None)
    if not explanation or explanation.status != 'generated':
        request.session['stage2_error'] = (
            "Stage-2 assessment is unavailable because the model explanation for this screening could not be verified."
        )
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 2. Human Review Prerequisite Enforcement
    human_review = getattr(screening_record, 'human_review', None)
    if not human_review:
        request.session['stage2_error'] = (
            "Stage-2 assessment requires a finalized Human Review decision."
        )
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 3. Final Referral Eligibility Enforcement
    if not human_review.final_referral_recommended:
        request.session['stage2_error'] = (
            "Stage-2 assessment is unavailable because the final human review decision does not recommend referral."
        )
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 4. If Stage2Assessment already exists, render read-only completed result!
    stage2_assessment = getattr(human_review, 'stage2_assessment', None)
    if stage2_assessment:
        context = {
            'record': screening_record,
            'human_review': human_review,
            'stage2': stage2_assessment,
        }
        return render(request, 'predictor/stage2_result.html', context)

    # 5. Handle initial submission (Input Review Step) vs Initial Form GET
    if request.method == 'POST':
        form = Stage2EntryForm(request.POST)
        if form.is_valid():
            hba1c_val = form.cleaned_data['hba1c_percent']
            range_result = classify_hba1c_range(hba1c_val)
            confirm_form = Stage2ConfirmForm(initial={'hba1c_percent': hba1c_val})
            context = {
                'record': screening_record,
                'human_review': human_review,
                'hba1c_val': hba1c_val,
                'range_result': range_result,
                'confirm_form': confirm_form,
            }
            return render(request, 'predictor/stage2_review.html', context)
    else:
        initial_val = request.GET.get('hba1c', '')
        initial_data = {}
        if initial_val:
            try:
                initial_data['hba1c_percent'] = Decimal(initial_val)
            except Exception:
                pass
        form = Stage2EntryForm(initial=initial_data)

    context = {
        'record': screening_record,
        'human_review': human_review,
        'form': form,
    }
    return render(request, 'predictor/stage2_entry.html', context)


def stage2_confirm_view(request, screening_id):
    """
    Persist Stage-2 HbA1c Laboratory Assessment (Phase D2.8).

    GOVERNANCE RULES:
    1. POST-only route.
    2. Re-verifies all eligibility gates server-side.
    3. Revalidates HbA1c input server-side.
    4. Derives laboratory_range and range_rule_version server-side using classify_hba1c_range.
       Client-injected decision or range parameters are ignored.
    5. Persists Stage2Assessment exactly once inside atomic transaction with duplicate defense.
    6. Executes 0 GAM inference calls and 0 XAI generation calls.
    """
    if request.method != 'POST':
        return redirect('predictor:stage2', screening_id=screening_id)

    screening_record = get_object_or_404(ScreeningRecord, id=screening_id)

    # 1. Explanation Prerequisite Enforcement
    explanation = getattr(screening_record, 'explanation', None)
    if not explanation or explanation.status != 'generated':
        request.session['stage2_error'] = (
            "Stage-2 assessment is unavailable because the model explanation could not be verified."
        )
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 2. Human Review Prerequisite Enforcement
    human_review = getattr(screening_record, 'human_review', None)
    if not human_review:
        request.session['stage2_error'] = (
            "Stage-2 assessment requires a finalized Human Review decision."
        )
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 3. Final Referral Eligibility Enforcement
    if not human_review.final_referral_recommended:
        request.session['stage2_error'] = (
            "Stage-2 assessment is unavailable because the final human review decision does not recommend referral."
        )
        return redirect('predictor:screening_result', screening_id=screening_record.id)

    # 4. Duplicate / Idempotency Protection
    if hasattr(human_review, 'stage2_assessment'):
        return redirect('predictor:stage2', screening_id=screening_record.id)

    # 5. Validate Confirmation Payload
    form = Stage2ConfirmForm(request.POST)
    if not form.is_valid():
        request.session['stage2_error'] = "Validation failed on confirmation. Please re-enter the HbA1c value."
        return redirect('predictor:stage2', screening_id=screening_record.id)

    cleaned_hba1c = form.cleaned_data['hba1c_percent']

    # 6. Server Derivation of Range and Reference Version
    range_result = classify_hba1c_range(cleaned_hba1c)

    # 7. Atomic Transactional Persistence
    try:
        with transaction.atomic():
            if not Stage2Assessment.objects.filter(human_review=human_review).exists():
                assessment = Stage2Assessment(
                    human_review=human_review,
                    hba1c_percent=cleaned_hba1c,
                    laboratory_range=range_result.range_code,
                    range_rule_version=range_result.rule_version,
                    entry_method='manual',
                )
                assessment.full_clean()
                assessment.save()
    except Exception as e:
        logger.error(f"Failed to persist Stage2Assessment for {screening_record.id}: {e}", exc_info=True)
        request.session['stage2_error'] = "The laboratory assessment could not be saved. Please try again."
        return redirect('predictor:stage2', screening_id=screening_record.id)

    # Log evaluation event if session is active
    _log_eval_event(request, 'stage2_completed', {
        'record_id': str(screening_record.id),
        'hba1c': float(cleaned_hba1c),
        'range': range_result.range_code,
    })

    return redirect('predictor:stage2', screening_id=screening_record.id)


def review_queue_view(request):
    """
    Screening Review Queue for actionable workflow cases (Phase D2.9).
    Partitioned into:
    - Pending Human Review (faithful explanation, HumanReview absent)
    - Pending Stage 2 (HumanReview finalized with refer, Stage2Assessment absent)
    - Needs System Attention (explanation failed or absent)
    
    Excludes completed and no-referral cases.
    Read-only surface: 0 writes, 0 ML, 0 XAI.
    """
    records = list(
        ScreeningRecord.objects.select_related('explanation', 'human_review__stage2_assessment')
        .order_by('-created_at')
    )

    pending_review_cases = []
    pending_stage2_cases = []
    attention_cases = []

    for r in records:
        lc = derive_screening_lifecycle(r)
        if lc.is_pending_review:
            pending_review_cases.append({'record': r, 'lifecycle': lc})
        elif lc.is_pending_stage2:
            pending_stage2_cases.append({'record': r, 'lifecycle': lc})
        elif lc.is_explanation_unavailable or lc.code == STATE_INTEGRITY_ERROR:
            attention_cases.append({'record': r, 'lifecycle': lc})

    # Sort pending stage 2 by human review timestamp (newest first)
    pending_stage2_cases.sort(
        key=lambda x: x['record'].human_review.created_at if hasattr(x['record'], 'human_review') and x['record'].human_review else x['record'].created_at,
        reverse=True
    )

    # Active tab from query param ('review' or 'stage2')
    active_tab = request.GET.get('tab', 'review')
    if active_tab not in ('review', 'stage2'):
        active_tab = 'review'

    context = {
        'pending_review_cases': pending_review_cases,
        'pending_stage2_cases': pending_stage2_cases,
        'attention_cases': attention_cases,
        'pending_review_count': len(pending_review_cases),
        'pending_stage2_count': len(pending_stage2_cases),
        'attention_count': len(attention_cases),
        'total_actionable': len(pending_review_cases) + len(pending_stage2_cases),
        'active_tab': active_tab,
    }
    return render(request, 'predictor/review_queue.html', context)


def about_model_view(request):
    """About the Model — methodology, benchmarks, and research prototype disclaimers."""
    return render(request, 'predictor/about.html')


def components_demo_view(request):
    """Interactive design system component inventory for visual QA."""
    return render(request, 'predictor/components_demo.html')


def index(request):
    """Dashboard home — patient data input form."""
    available_models = model_loader.get_available_models() if model_loader else []
    
    # Get recent predictions for the sidebar
    recent_predictions = Prediction.objects.all()[:5]
    
    # Get basic stats
    total_predictions = Prediction.objects.count()
    total_overrides = Override.objects.filter(decision='reject').count()
    
    context = {
        'available_models': available_models,
        'recent_predictions': recent_predictions,
        'total_predictions': total_predictions,
        'total_overrides': total_overrides,
        'feature_names': getattr(model_loader, 'FEATURE_NAMES', []),
        'feature_display_names': getattr(shap_explainer, 'FEATURE_DISPLAY_NAMES', {}),
    }
    return render(request, 'predictor/index.html', context)


def predict_view(request):
    """Run prediction, generate SHAP explanation, show result page."""
    if request.method != 'POST':
        return redirect('predictor:index')
    
    try:
        # Extract patient features from form
        features = {
            'gender': float(request.POST.get('gender', 0)),
            'age': float(request.POST.get('age', 0)),
            'hypertension': float(request.POST.get('hypertension', 0)),
            'heart_disease': float(request.POST.get('heart_disease', 0)),
            'smoking': float(request.POST.get('smoking', 0)),
            'bmi': float(request.POST.get('bmi', 0)),
            'HbA1c': float(request.POST.get('HbA1c', 0)),
            'glucose': float(request.POST.get('glucose', 0)),
        }
        
        model_name = request.POST.get('model_name', 'DLNN Baseline')
        threshold = float(request.POST.get('threshold', 0.5))
        
        # Run prediction
        result = model_loader.predict(model_name, features, threshold)
        
        # Generate SHAP explanation
        try:
            explanation = shap_explainer.explain_prediction(model_name, features)
        except Exception as e:
            print(f"SHAP explanation error: {e}")
            traceback.print_exc()
            explanation = {
                'shap_values': {f: 0.0 for f in model_loader.FEATURE_NAMES},
                'base_value': 0.5,
                'feature_values': features,
            }
        
        # Save prediction to database
        prediction_obj = Prediction.objects.create(
            patient_data=features,
            model_used=model_name,
            prediction=result['prediction'],
            confidence=result['confidence'],
            threshold=threshold,
            shap_values=explanation['shap_values'],
        )
        
        # Redirect to the detail page
        return redirect('predictor:prediction_detail', pk=prediction_obj.id)
        
    except Exception as e:
        traceback.print_exc()
        context = {
            'error': str(e),
            'available_models': model_loader.get_available_models(),
            'feature_names': model_loader.FEATURE_NAMES,
            'feature_display_names': shap_explainer.FEATURE_DISPLAY_NAMES,
        }
        return render(request, 'predictor/index.html', context)


def prediction_detail_view(request, pk):
    """
    View a single prediction with SHAP explanation and override form.
    This allows pending predictions to be re-opened for review.
    """
    prediction_obj = get_object_or_404(Prediction, pk=pk)
    
    # Build SHAP data from stored values
    shap_values = prediction_obj.shap_values or {}
    features = prediction_obj.patient_data or {}
    
    shap_data = []
    for feature_name in model_loader.FEATURE_NAMES:
        shap_val = shap_values.get(feature_name, 0)
        display_name = shap_explainer.FEATURE_DISPLAY_NAMES.get(feature_name, feature_name)
        
        # Get human-readable feature value
        raw_value = features.get(feature_name, 0)
        if feature_name in shap_explainer.FEATURE_LABELS:
            display_value = shap_explainer.FEATURE_LABELS[feature_name].get(int(raw_value), str(raw_value))
        else:
            display_value = str(raw_value)
        
        shap_data.append({
            'feature': display_name,
            'feature_key': feature_name,
            'value': display_value,
            'raw_value': raw_value,
            'shap_value': round(float(shap_val), 4),
            'direction': 'risk' if float(shap_val) > 0 else 'protective',
        })
    
    # Sort by absolute SHAP value (most important first)
    shap_data.sort(key=lambda x: abs(x['shap_value']), reverse=True)
    
    # Compute probability from confidence
    probability = prediction_obj.confidence if prediction_obj.prediction == 1 else (1 - prediction_obj.confidence)
    
    result = {
        'prediction': prediction_obj.prediction,
        'confidence': prediction_obj.confidence,
        'probability': probability,
    }
    
    # Dynamic Multi-Model Consensus (selected model vs statistical GAM baseline)
    try:
        gam_result = model_loader.predict('GAM', features, 0.50)
        selected_pred = prediction_obj.prediction
        gam_pred = gam_result['prediction']
        
        if selected_pred == gam_pred:
            consensus_status = 'both_positive' if selected_pred == 1 else 'both_negative'
        else:
            consensus_status = 'disagreement'
    except Exception as e:
        print(f"Error computing dynamic GAM consensus: {e}")
        gam_result = {'prediction': 0, 'probability': 0.0, 'confidence': 0.5}
        consensus_status = 'unknown'
    
    context = {
        'prediction': prediction_obj,
        'result': result,
        'shap_data': shap_data,
        'shap_data_json': json.dumps(shap_data),
        'base_value': 0.5,
        'patient_display': prediction_obj.get_patient_data_display(),
        'feature_names': model_loader.FEATURE_NAMES,
        'has_override': prediction_obj.overrides.exists(),
        'existing_override': prediction_obj.overrides.first(),
        'gam_result': gam_result,
        'consensus_status': consensus_status,
    }
    return render(request, 'predictor/result.html', context)


def override_view(request):
    """Submit reviewer's override decision."""
    if request.method != 'POST':
        return redirect('predictor:index')
    
    prediction_id = request.POST.get('prediction_id')
    prediction = get_object_or_404(Prediction, id=prediction_id)
    
    decision = request.POST.get('decision', 'accept')
    doctor_name = request.POST.get('doctor_name', 'Anonymous')
    
    # Only save reason and flagged features for rejections
    override_value = None
    reason = ''
    flagged = None
    
    if decision == 'reject':
        reason = request.POST.get('reason', '')
        flagged = request.POST.getlist('flagged_features') or None
        # If rejecting, the override is the opposite of the AI prediction
        override_value = 0 if prediction.prediction == 1 else 1
    
    # Save override
    Override.objects.create(
        prediction=prediction,
        doctor_name=doctor_name,
        decision=decision,
        override_value=override_value,
        reason=reason,
        flagged_features=flagged,
    )
    
    # Mark prediction as reviewed
    prediction.is_reviewed = True
    prediction.save()
    
    return redirect('predictor:history')


def history_view(request):
    """
    Auditable Screening History Ledger (Phase D2.9).
    Exactly 1 row per ScreeningRecord.
    Server-side filtering, UUID search, and pagination.
    Read-only surface: 0 writes, 0 ML, 0 XAI.
    """
    qs = ScreeningRecord.objects.select_related('explanation', 'human_review__stage2_assessment')

    # Exclude practice cases (P0) by default to prevent research contamination
    include_practice = request.GET.get('include_practice', '0') == '1'
    if not include_practice:
        qs = qs.filter(is_practice=False)

    # In evaluation mode, restrict participants to their own evaluation session records
    app_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
    eval_token = request.session.get('evaluation_session_token')
    if app_mode == 'evaluation' and eval_token and not (request.user.is_authenticated and request.user.is_staff):
        qs = qs.filter(evaluation_session__session_token=eval_token)

    # 1. Search by Screening UUID (full or prefix/substring)
    search_query = request.GET.get('search', '').strip()
    if search_query:
        try:
            val_uuid = uuid.UUID(search_query)
            qs = qs.filter(id=val_uuid)
        except (ValueError, AttributeError):
            try:
                qs = qs.filter(id__icontains=search_query)
            except Exception:
                pass

    # 2. Non-PII Database-Level Filters
    ai_rec_filter = request.GET.get('ai_rec', 'all').strip()
    if ai_rec_filter == 'refer':
        qs = qs.filter(ai_referral_recommended=True)
    elif ai_rec_filter == 'no_refer':
        qs = qs.filter(ai_referral_recommended=False)

    review_action_filter = request.GET.get('review_action', 'all').strip()
    if review_action_filter == 'accepted':
        qs = qs.filter(human_review__review_action='accepted')
    elif review_action_filter == 'overridden':
        qs = qs.filter(human_review__review_action='overridden')
    elif review_action_filter == 'pending':
        qs = qs.filter(human_review__isnull=True)

    final_decision_filter = request.GET.get('final_decision', 'all').strip()
    if final_decision_filter == 'refer':
        qs = qs.filter(human_review__final_referral_recommended=True)
    elif final_decision_filter == 'no_refer':
        qs = qs.filter(human_review__final_referral_recommended=False)
    elif final_decision_filter == 'pending':
        qs = qs.filter(human_review__isnull=True)

    stage2_status_filter = request.GET.get('stage2_status', 'all').strip()
    if stage2_status_filter == 'not_applicable':
        qs = qs.filter(human_review__final_referral_recommended=False)
    elif stage2_status_filter == 'pending':
        qs = qs.filter(human_review__final_referral_recommended=True, human_review__stage2_assessment__isnull=True)
    elif stage2_status_filter == 'completed':
        qs = qs.filter(human_review__stage2_assessment__isnull=False)

    hba1c_range_filter = request.GET.get('hba1c_range', 'all').strip()
    if hba1c_range_filter in ('normal_range', 'prediabetes_range', 'diabetes_range'):
        qs = qs.filter(human_review__stage2_assessment__laboratory_range=hba1c_range_filter)

    # 3. Ordering
    order_filter = request.GET.get('order', 'newest').strip()
    if order_filter == 'oldest':
        qs = qs.order_by('created_at')
    else:
        qs = qs.order_by('-created_at')

    all_matched = list(qs)

    # Substring search safety fallback
    if search_query:
        sq_lower = search_query.lower()
        all_matched = [r for r in all_matched if sq_lower in str(r.id).lower()]

    # 4. Lifecycle status filter and state derivation
    status_filter = request.GET.get('status', 'all').strip()
    records_with_lifecycle = []
    for r in all_matched:
        lc = derive_screening_lifecycle(r)
        if status_filter != 'all':
            if lc.code != status_filter:
                continue
        records_with_lifecycle.append({
            'record': r,
            'lifecycle': lc,
        })

    # Summary metrics across active screening records
    all_total_count = ScreeningRecord.objects.count()

    # 5. Server-Side Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(records_with_lifecycle, 25)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    # Build querystring without page for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    extra_querystring = query_params.urlencode()

    context = {
        'page_obj': page_obj,
        'records': page_obj.object_list,
        'total_count': all_total_count,
        'filtered_count': len(records_with_lifecycle),
        'extra_querystring': extra_querystring,
        'filters': {
            'status': status_filter,
            'ai_rec': ai_rec_filter,
            'review_action': review_action_filter,
            'final_decision': final_decision_filter,
            'stage2_status': stage2_status_filter,
            'hba1c_range': hba1c_range_filter,
            'order': order_filter,
            'search': search_query,
        },
    }
    return render(request, 'predictor/history.html', context)


def evaluation_view(request):
    """Model evaluation page — displays all model metrics from results.csv."""
    results_path = Path(__file__).resolve().parent.parent.parent / 'models' / 'results.csv'
    
    models_data = []
    if results_path.exists():
        with open(str(results_path), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Model'):
                    models_data.append({
                        'name': row['Model'],
                        'accuracy': round(float(row.get('Accuracy', 0)) * 100, 2),
                        'precision': round(float(row.get('Precision', 0)) * 100, 2),
                        'recall': round(float(row.get('Recall', 0)) * 100, 2),
                        'f1': round(float(row.get('F1-score', 0)) * 100, 2),
                        'roc_auc': round(float(row.get('ROC-AUC', 0)) * 100, 2),
                    })
    
    # Find best model per metric
    best = {}
    if models_data:
        for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
            best_model = max(models_data, key=lambda x: x[metric])
            best[metric] = best_model['name']
    
    context = {
        'models_data': models_data,
        'models_data_json': json.dumps(models_data),
        'best': best,
    }
    return render(request, 'predictor/evaluation.html', context)


def analytics_view(request):
    """
    Research Analytics & Human-AI Decision Flow (Phase D2.10).
    Computes research-safe aggregate metrics from authoritative ScreeningRecord rows.
    Guarantees 0 GAM/XAI inferences, 0 model evaluations, and 0 database writes.
    """
    date_from_str = request.GET.get('date_from', '').strip()
    date_to_str = request.GET.get('date_to', '').strip()

    date_from = None
    date_to = None

    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            date_from = None
            date_from_str = ''

    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            date_to = None
            date_to_str = ''

    analytics = compute_research_analytics(
        date_from=date_from,
        date_to=date_to,
    )

    context = {
        'analytics': analytics,
        'date_from': date_from_str,
        'date_to': date_to_str,
        'has_active_filter': bool(date_from_str or date_to_str),
    }
    return render(request, 'predictor/analytics.html', context)


# ===========================================================================
# HUMAN FEEDBACK LEARNING LOOP VIEWS
# ===========================================================================

from .forms import HumanFeedbackForm
from .models import HumanFeedback, ModelVersion, FeedbackLearningBatch, SimilarCaseComparison


def submit_feedback_view(request, screening_id):
    """
    Submit structured human feedback for a screening case.

    PREREQUISITES:
    1. ScreeningRecord must exist.
    2. HumanReview must be finalized.
    3. No existing HumanFeedback for this review (one feedback per review).

    GOVERNANCE:
    - Does NOT modify the ScreeningRecord or its AI prediction.
    - The structured category is the canonical learning signal.
    - Optional free-text is processed by NLP but preserved raw.
    - NLP output is stored for auditability; low-confidence NLP does not generate learning signal.
    """
    if request.method != 'POST':
        return redirect('predictor:screening_result', screening_id=screening_id)

    screening_record = get_object_or_404(ScreeningRecord, id=screening_id)

    # 1. Human Review Prerequisite
    human_review = getattr(screening_record, 'human_review', None)
    if not human_review:
        request.session['review_error'] = "Feedback requires a finalized human review."
        return redirect('predictor:screening_result', screening_id=screening_id)

    # 2. Duplicate Feedback Prevention
    if hasattr(human_review, 'feedback'):
        return redirect('predictor:screening_result', screening_id=screening_id)

    # 3. Validate Form
    form = HumanFeedbackForm(request.POST)
    if not form.is_valid():
        first_err = None
        for field, errs in form.errors.items():
            if errs:
                first_err = errs[0]
                break
        request.session['feedback_error'] = first_err or "Invalid feedback submission."
        return redirect('predictor:screening_result', screening_id=screening_id)

    category_id = form.cleaned_data['structured_category']
    feedback_text = form.cleaned_data.get('feedback_text', '').strip()

    # 4. Look up taxonomy category
    from .services.feedback_taxonomy import get_category, get_taxonomy_version, DIR_NO_LEARNING
    category = get_category(category_id)
    if category is None:
        request.session['feedback_error'] = "Invalid feedback category."
        return redirect('predictor:screening_result', screening_id=screening_id)

    # 5. NLP Processing (only if free-text provided)
    nlp_confidence = None
    nlp_raw_output = None
    if feedback_text:
        try:
            from .services.feedback_nlp import interpret_feedback_text
            nlp_result = interpret_feedback_text(feedback_text)
            nlp_confidence = nlp_result.confidence
            nlp_raw_output = nlp_result.to_dict()
        except Exception as nlp_err:
            logger.warning(f"NLP interpretation failed: {nlp_err}")
            nlp_raw_output = {"error": str(nlp_err)}

    # 6. Determine learning eligibility
    from .services.model_versioning import get_active_version
    active_version = get_active_version()

    is_eligible = (
        category.learning_direction != DIR_NO_LEARNING
        and human_review.review_action == 'overridden'
        and category.active
    )
    # Mode guard: Never permit evaluation participants or practice records into learning loop
    current_mode = getattr(settings, 'APP_MODE', 'feedback_lab').lower()
    if current_mode == 'evaluation' or getattr(screening_record, 'is_practice', False):
        is_eligible = False

    # If NLP was used and confidence is below threshold, mark not eligible
    if feedback_text and nlp_confidence is not None and nlp_confidence < 0.5:
        # Still store the feedback, but don't auto-generate learning signal from NLP
        # The human-selected category remains the canonical signal
        pass  # Eligibility based on human category, not NLP confidence

    # 7. Persist HumanFeedback
    try:
        with transaction.atomic():
            if not HumanFeedback.objects.filter(human_review=human_review).exists():
                feedback = HumanFeedback(
                    human_review=human_review,
                    structured_category=category_id,
                    relevant_feature=(
                        category.relevant_features[0] if category.relevant_features else None
                    ),
                    feedback_direction=category.learning_direction,
                    feedback_text=feedback_text,
                    nlp_confidence=nlp_confidence,
                    nlp_raw_output=nlp_raw_output,
                    is_eligible_for_learning=is_eligible,
                    learning_status='pending' if is_eligible else 'excluded',
                    model_version_at_feedback=active_version.version_label,
                    taxonomy_version=get_taxonomy_version(),
                )
                feedback.save()
                _log_eval_event(request, 'feedback_submitted', {
                    'record_id': str(screening_record.id),
                    'category': category_id,
                    'direction': category.learning_direction,
                })
    except Exception as e:
        logger.error(f"Failed to persist HumanFeedback for {screening_id}: {e}", exc_info=True)
        request.session['feedback_error'] = "The feedback could not be saved. Please try again."

    return redirect('predictor:screening_result', screening_id=screening_id)


@require_app_mode('feedback_lab')
def feedback_experiment_view(request):
    """
    Feedback Learning Experiment Dashboard.
    Displays feedback accumulation, model versions, learning batches,
    controlled mechanism experiment, and before/after comparison results.

    Read-only surface: 0 writes, 0 ML execution.
    """
    from .services.model_versioning import get_model_status_summary
    from .services.feedback_learning import get_latest_controlled_experiment

    # Feedback summary
    total_feedback = HumanFeedback.objects.count()
    eligible_feedback = HumanFeedback.objects.filter(is_eligible_for_learning=True).count()
    pending_feedback = HumanFeedback.objects.filter(
        is_eligible_for_learning=True, learning_status='pending'
    ).count()
    included_feedback = HumanFeedback.objects.filter(learning_status='included').count()

    # Category breakdown
    from django.db.models import Count
    category_breakdown = list(
        HumanFeedback.objects.values('structured_category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Model versions and status
    versions = list(ModelVersion.objects.all().order_by('-created_at'))
    active_version = ModelVersion.objects.filter(is_active=True).first()
    model_status = get_model_status_summary()

    # Controlled Mechanism Experiment (Thesis Gap #2)
    controlled_exp = get_latest_controlled_experiment()

    # Learning batches
    batches = list(FeedbackLearningBatch.objects.all().order_by('-created_at')[:10])

    # Comparisons
    comparisons = list(
        SimilarCaseComparison.objects.select_related(
            'source_case', 'target_case', 'baseline_version', 'updated_version'
        ).order_by('-created_at')[:20]
    )

    # Flash messages
    experiment_message = request.session.pop('experiment_message', None)
    experiment_error = request.session.pop('experiment_error', None)

    context = {
        'total_feedback': total_feedback,
        'eligible_feedback': eligible_feedback,
        'pending_feedback': pending_feedback,
        'included_feedback': included_feedback,
        'category_breakdown': category_breakdown,
        'versions': versions,
        'active_version': active_version,
        'model_status': model_status,
        'controlled_exp': controlled_exp,
        'batches': batches,
        'comparisons': comparisons,
        'experiment_message': experiment_message,
        'experiment_error': experiment_error,
    }
    return render(request, 'predictor/feedback_experiment.html', context)


@require_app_mode('feedback_lab')
def start_controlled_experiment_view(request):
    """
    Step 1: Start or restart a Controlled Mechanism Demonstration Experiment.
    Creates Case A and redirects researcher directly to review Case A.
    """
    if request.method != 'POST':
        return redirect('predictor:feedback_experiment')

    from .services.feedback_learning import start_controlled_experiment
    try:
        exp, case_a = start_controlled_experiment()
        request.session['experiment_message'] = (
            "Controlled Mechanism Experiment initiated. Case A created. "
            "Please review the Native GAM explanation and record your human decision."
        )
        return redirect('predictor:screening_result', screening_id=case_a.id)
    except Exception as e:
        logger.error(f"Failed to start controlled experiment: {e}", exc_info=True)
        request.session['experiment_error'] = f"Failed to start controlled experiment: {e}"
        return redirect('predictor:feedback_experiment')


@require_app_mode('feedback_lab')
def run_controlled_learning_view(request):
    """
    Step 3: Execute controlled learning from the real Human Override signal.
    """
    if request.method != 'POST':
        return redirect('predictor:feedback_experiment')

    from .services.feedback_learning import run_controlled_learning
    res = run_controlled_learning()

    if res['success']:
        request.session['experiment_message'] = (
            f"Controlled Learning succeeded: Candidate Adaptation {res['candidate_label']} "
            f"trained and passed all 13 technical validation checks."
        )
    else:
        request.session['experiment_error'] = f"Controlled learning failed: {res.get('error')}"

    return redirect('predictor:feedback_experiment')


@require_app_mode('feedback_lab')
def activate_controlled_adaptation_view(request):
    """
    Step 4: Activate the validated candidate adaptation layer.
    """
    if request.method != 'POST':
        return redirect('predictor:feedback_experiment')

    from .services.feedback_learning import activate_controlled_adaptation
    res = activate_controlled_adaptation()

    if res['success']:
        request.session['experiment_message'] = (
            f"Residual Adaptation {res['active_label']} is now Validated & Active. "
            f"Ready to evaluate subsequent similar Case B."
        )
    else:
        request.session['experiment_error'] = f"Activation failed: {res.get('error')}"

    return redirect('predictor:feedback_experiment')


@require_app_mode('feedback_lab')
def evaluate_controlled_case_b_view(request):
    """
    Step 5: Evaluate subsequent similar Case B under frozen GAM vs active residual adaptation.
    """
    if request.method != 'POST':
        return redirect('predictor:feedback_experiment')

    from .services.feedback_learning import evaluate_controlled_case_b
    res = evaluate_controlled_case_b()

    if res['success']:
        request.session['experiment_message'] = (
            f"Case B evaluated! Baseline P={res['baseline_probability']:.4f} vs "
            f"Adapted P={res['adapted_probability']:.4f} (Δ={res['probability_delta']:+.4f}, "
            f"Similarity={res['similarity_score']:.4f}). Comparison complete."
        )
    else:
        request.session['experiment_error'] = f"Case B evaluation failed: {res.get('error')}"

    return redirect('predictor:feedback_experiment')


@require_app_mode('feedback_lab')
def reset_controlled_experiment_view(request):
    """
    Reset in-progress controlled experiment state back to READY.
    """
    if request.method != 'POST':
        return redirect('predictor:feedback_experiment')

    from .services.feedback_learning import reset_controlled_experiment
    reset_controlled_experiment()
    request.session['experiment_message'] = "Controlled experiment state reset."
    return redirect('predictor:feedback_experiment')


@require_app_mode('feedback_lab')
def trigger_learning_view(request):
    """
    Trigger a feedback learning batch.
    POST-only. Collects eligible feedback, trains adaptation layer,
    creates candidate version, and runs validation.

    Does NOT automatically activate the candidate. Activation is separate.
    """
    if request.method != 'POST':
        return redirect('predictor:feedback_experiment')

    from .services.feedback_learning import execute_learning_batch

    result = execute_learning_batch()

    if result['success']:
        request.session['experiment_message'] = (
            f"Learning batch completed successfully. "
            f"Candidate version: {result['candidate_label']}. "
            f"Feedback records used: {result['feedback_count']}. "
            f"Candidate is ready for activation."
        )
    else:
        request.session['experiment_error'] = (
            f"Learning batch failed: {result.get('error', 'Unknown error')}."
        )

    return redirect('predictor:feedback_experiment')


@require_app_mode('feedback_lab')
def activate_candidate_view(request):
    """
    Activate a validated candidate model version.
    POST-only. Requires batch_id in POST data.
    """
    if request.method != 'POST':
        return redirect('predictor:feedback_experiment')

    batch_id = request.POST.get('batch_id', '').strip()
    if not batch_id:
        request.session['experiment_error'] = "No batch specified for activation."
        return redirect('predictor:feedback_experiment')

    from .services.feedback_learning import activate_learning_batch
    result = activate_learning_batch(batch_id)

    if result['success']:
        request.session['experiment_message'] = "Candidate version activated successfully."
    else:
        request.session['experiment_error'] = f"Activation failed: {result.get('error', 'Unknown error')}."

    return redirect('predictor:feedback_experiment')


@require_app_mode('feedback_lab')
def rollback_version_view(request):
    """
    Rollback to the baseline GAM-v1 version.
    POST-only.
    """
    if request.method != 'POST':
        return redirect('predictor:feedback_experiment')

    from .services.model_versioning import rollback_to_version, BASELINE_VERSION_LABEL
    try:
        rollback_to_version(BASELINE_VERSION_LABEL)
        request.session['experiment_message'] = f"Rolled back to {BASELINE_VERSION_LABEL}."
    except Exception as e:
        request.session['experiment_error'] = f"Rollback failed: {str(e)}."

    return redirect('predictor:feedback_experiment')


@require_app_mode('feedback_lab')
def run_comparison_view(request, screening_id):
    """
    Run a before/after comparison for a specific screening case (Case B)
    against all source cases that have feedback.

    Finds similar source cases, computes baseline vs adapted predictions,
    and persists SimilarCaseComparison records.
    """
    if request.method != 'POST':
        return redirect('predictor:screening_result', screening_id=screening_id)

    target_record = get_object_or_404(ScreeningRecord, id=screening_id)

    from .services.similarity import compute_similarity
    from .services.adapted_inference import predict_adapted
    from .services.model_versioning import get_active_version, get_baseline_version
    from .services.screening_inference import predict_screening

    active_version = get_active_version()
    baseline_version = get_baseline_version()

    # Find source cases with feedback
    source_reviews = HumanReview.objects.filter(
        feedback__isnull=False,
        feedback__is_eligible_for_learning=True,
    ).select_related('screening_record', 'feedback')

    comparisons_created = 0

    for review in source_reviews:
        source_record = review.screening_record
        if source_record.id == target_record.id:
            continue  # Skip self-comparison

        try:
            sim = compute_similarity(source_record, target_record)
            if not sim.is_similar:
                continue

            # Check if comparison already exists
            existing = SimilarCaseComparison.objects.filter(
                source_case=source_record,
                target_case=target_record,
                updated_version=active_version,
            ).exists()
            if existing:
                continue

            # Compute baseline prediction for Case B
            target_data = {
                'age': target_record.age,
                'sex': target_record.sex,
                'bmi': float(target_record.bmi),
                'waist_cm': float(target_record.waist_cm),
                'hypertension_history': target_record.hypertension_history,
                'smoking_history': target_record.smoking_history,
                'sedentary_minutes_day': target_record.sedentary_minutes_day,
            }

            baseline_result = predict_screening(target_data)

            # Compute adapted prediction for Case B
            adapted_result = predict_adapted(target_data)

            # Persist comparison
            feedback = review.feedback
            SimilarCaseComparison.objects.create(
                source_case=source_record,
                target_case=target_record,
                similarity_score=sim.similarity_score,
                similarity_method=sim.method,
                similarity_features_used=sim.features_used,
                similarity_normalization_version=sim.normalization_bounds_version,
                baseline_version=baseline_version,
                baseline_probability=baseline_result.probability,
                baseline_recommendation=baseline_result.referral_recommended,
                updated_version=active_version,
                updated_probability=adapted_result.adapted_probability,
                updated_recommendation=adapted_result.adapted_recommendation,
                probability_delta=adapted_result.adapted_probability - baseline_result.probability,
                recommendation_changed=(
                    adapted_result.adapted_recommendation != baseline_result.referral_recommended
                ),
                feedback_category=feedback.structured_category,
            )
            comparisons_created += 1

        except Exception as e:
            logger.warning(f"Comparison failed for source={source_record.id}: {e}")
            continue

    if comparisons_created > 0:
        request.session['experiment_message'] = (
            f"Created {comparisons_created} similar-case comparison(s)."
        )
    else:
        request.session['experiment_message'] = (
            "No similar source cases with feedback were found for this screening."
        )

    return redirect('predictor:screening_result', screening_id=screening_id)


# ===========================================================================
# EVALUATION MODE VIEWS (PROTOCOL E1 v1.0.3 / E2)
# ===========================================================================

from .services.questionnaire import (
    PRACTICE_CASE_P0,
    COMPREHENSION_ITEMS,
    SUS_ITEMS,
    CLARITY_ITEMS,
    OPEN_ENDED_ITEMS,
    score_comprehension,
    score_sus,
)


def evaluation_consent_view(request):
    """
    Evaluation Participant Informed Consent & Demographic Intake (Protocol E1/E2).
    Anonymous intake: creates EvaluationRespondent and EvaluationSession.
    """
    token = request.session.get('evaluation_session_token')
    if token:
        existing_session = EvaluationSession.objects.filter(session_token=token).first()
        if existing_session:
            if existing_session.questionnaire_completed:
                return redirect('predictor:evaluation_complete')
            elif existing_session.practice_completed:
                return redirect('predictor:overview')
            else:
                return redirect('predictor:evaluation_practice')

    if request.method == 'POST':
        form = EvaluationConsentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                respondent = EvaluationRespondent.objects.create(
                    respondent_code=f"R-{uuid.uuid4().hex[:8].upper()}",
                    consent_given=True,
                    age_group=form.cleaned_data['age_group'],
                    education_level=form.cleaned_data['education_level'],
                    technical_background=form.cleaned_data['technical_background'],
                    health_background=form.cleaned_data['health_background'],
                )
                session = EvaluationSession.objects.create(
                    respondent=respondent,
                    session_token=uuid.uuid4().hex,
                    app_version=getattr(settings, 'APP_VERSION', 'v1.0.3'),
                    model_version='GAM-v1',
                    status='in_progress',
                )
                EvaluationEvent.objects.create(
                    session=session,
                    event_name='session_started',
                    event_data={
                        'age_group': respondent.age_group,
                        'technical_background': respondent.technical_background,
                        'health_background': respondent.health_background,
                    }
                )
            request.session['evaluation_session_token'] = session.session_token
            request.session['respondent_code'] = respondent.respondent_code
            return redirect('predictor:evaluation_practice')
    else:
        form = EvaluationConsentForm()

    return render(request, 'predictor/evaluation_consent.html', {
        'form': form,
        'protocol_version': getattr(settings, 'EVALUATION_PROTOCOL_VERSION', 'E1-v1.0.3'),
    })


def evaluation_practice_view(request):
    """
    Practice Case P0 Onboarding Walkthrough.
    Sets up the non-clinical orientation case P0 with is_practice=True.
    Excluded from learning, research analytics, and candidate model training.
    """
    token = request.session.get('evaluation_session_token')
    if not token:
        return redirect('predictor:evaluation_consent')

    session = get_object_or_404(EvaluationSession, session_token=token)

    # Log practice started if not already logged
    if not session.events.filter(event_name='practice_started').exists():
        EvaluationEvent.objects.create(session=session, event_name='practice_started')

    p0_spec = PRACTICE_CASE_P0
    p0_data = p0_spec['features']

    # Locate or create practice screening record
    practice_token = f"practice_{session.id}"
    practice_record = ScreeningRecord.objects.filter(
        idempotency_token=practice_token,
        is_practice=True
    ).first()

    if not practice_record:
        from .services import screening_inference, screening_explanation

        inf_res = screening_inference.predict_screening(p0_data)
        with transaction.atomic():
            practice_record = ScreeningRecord.objects.create(
                age=p0_data['age'],
                sex=p0_data['sex'],
                bmi=p0_data['bmi'],
                waist_cm=p0_data['waist_cm'],
                hypertension_history=p0_data['hypertension_history'],
                smoking_history=p0_data['smoking_history'],
                sedentary_minutes_day=p0_data['sedentary_minutes_day'],
                screening_probability=inf_res.screening_probability,
                ai_referral_recommended=inf_res.referral_recommended,
                decision_threshold=Decimal(str(inf_res.threshold)),
                model_name=inf_res.model_name,
                model_sha256=screening_inference.EXPECTED_GAM_SHA256,
                preprocessor_sha256=screening_inference.EXPECTED_PREPROCESSOR_SHA256,
                input_schema_version="1.0",
                idempotency_token=practice_token,
                is_practice=True,
                evaluation_session=session,
            )
            exp_res = screening_explanation.explain_screening(p0_data)
            ScreeningExplanation.objects.create(
                screening_record=practice_record,
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

    if request.method == 'POST' and request.POST.get('action') == 'finish_practice':
        session.practice_completed = True
        session.save(update_fields=['practice_completed'])
        EvaluationEvent.objects.create(session=session, event_name='practice_completed')
        return redirect('predictor:overview')

    context = {
        'session': session,
        'practice_record': practice_record,
        'p0_spec': p0_spec,
    }
    return render(request, 'predictor/evaluation_practice.html', context)


def evaluation_questionnaire_view(request):
    """
    Participant Post-Task Evaluation Questionnaire.
    Collects:
    - 8 Objective Comprehension Items (C1-C8, server scored 0-8, %)
    - 10 Indonesian SUS Items (Likert 1-5, Sharfina & Santoso 2016, scored 0-100)
    - 5 Dashboard Clarity Items (DQ1-DQ5, Likert 1-5)
    - 3 Open-ended Qualitative Items (OQ1-OQ3)
    """
    token = request.session.get('evaluation_session_token')
    if not token:
        return redirect('predictor:evaluation_consent')

    session = get_object_or_404(EvaluationSession, session_token=token)
    if session.questionnaire_completed:
        return redirect('predictor:evaluation_complete')

    if not session.events.filter(event_name='questionnaire_started').exists():
        EvaluationEvent.objects.create(session=session, event_name='questionnaire_started')

    if request.method == 'POST':
        form = DashboardQuestionnaireForm(request.POST)
        if form.is_valid():
            answers_c = {f"C{i}": form.cleaned_data[f"c{i}"] for i in range(1, 9)}
            comp_score, comp_pct = score_comprehension(answers_c)

            sus_answers = {i: int(form.cleaned_data[f"sus_{i}"]) for i in range(1, 11)}
            sus_total = score_sus(sus_answers)

            with transaction.atomic():
                QuestionnaireResponse.objects.create(
                    session=session,
                    respondent=session.respondent,
                    app_version=session.app_version,
                    model_version=session.model_version,
                    c1_answer=answers_c['C1'],
                    c2_answer=answers_c['C2'],
                    c3_answer=answers_c['C3'],
                    c4_answer=answers_c['C4'],
                    c5_answer=answers_c['C5'],
                    c6_answer=answers_c['C6'],
                    c7_answer=answers_c['C7'],
                    c8_answer=answers_c['C8'],
                    comprehension_score=comp_score,
                    comprehension_pct=comp_pct,
                    sus_1=sus_answers[1],
                    sus_2=sus_answers[2],
                    sus_3=sus_answers[3],
                    sus_4=sus_answers[4],
                    sus_5=sus_answers[5],
                    sus_6=sus_answers[6],
                    sus_7=sus_answers[7],
                    sus_8=sus_answers[8],
                    sus_9=sus_answers[9],
                    sus_10=sus_answers[10],
                    sus_score=sus_total,
                    clarity_1=int(form.cleaned_data['clarity_1']),
                    clarity_2=int(form.cleaned_data['clarity_2']),
                    clarity_3=int(form.cleaned_data['clarity_3']),
                    clarity_4=int(form.cleaned_data['clarity_4']),
                    clarity_5=int(form.cleaned_data['clarity_5']),
                    open_1=form.cleaned_data.get('open_1', '').strip(),
                    open_2=form.cleaned_data.get('open_2', '').strip(),
                    open_3=form.cleaned_data.get('open_3', '').strip(),
                )
                session.questionnaire_completed = True
                session.status = 'completed'
                session.completed_at = timezone.now()
                session.save(update_fields=['questionnaire_completed', 'status', 'completed_at'])

                EvaluationEvent.objects.create(session=session, event_name='questionnaire_submitted')
                EvaluationEvent.objects.create(session=session, event_name='session_completed')

            return redirect('predictor:evaluation_complete')
    else:
        form = DashboardQuestionnaireForm()

    context = {
        'session': session,
        'form': form,
        'comprehension_items': COMPREHENSION_ITEMS,
        'sus_items': SUS_ITEMS,
        'clarity_items': CLARITY_ITEMS,
        'open_ended_items': OPEN_ENDED_ITEMS,
    }
    return render(request, 'predictor/evaluation_questionnaire.html', context)


def evaluation_complete_view(request):
    """
    Participant Evaluation Completion View.
    Displays anonymous confirmation code.
    Strictly conceals answer keys and SUS scores from participant.
    """
    token = request.session.get('evaluation_session_token')
    resp_code = request.session.get('respondent_code')
    session = None
    if token:
        session = EvaluationSession.objects.filter(session_token=token).first()
        if session:
            resp_code = session.respondent.respondent_code

    return render(request, 'predictor/evaluation_complete.html', {
        'respondent_code': resp_code or "PARTICIPANT-ANON",
        'session': session,
    })


@require_researcher_access
def evaluation_analytics_view(request):
    """
    Researcher-only Evaluation Analytics View.
    Displays live recruitment stats, completion funnel, psychometrics,
    and protocol session exclusion management.
    """
    from .services.evaluation_analytics import compute_evaluation_analytics

    include_excluded = request.GET.get('include_excluded', '0') == '1'
    analytics = compute_evaluation_analytics(include_excluded=include_excluded)

    # Fetch recent sessions for audit/management
    sessions = (
        EvaluationSession.objects.select_related('respondent')
        .prefetch_related('questionnaire_responses', 'events')
        .order_by('-started_at')[:50]
    )

    context = {
        'stats': analytics,
        'analytics': analytics,
        'sessions': sessions,
        'include_excluded': include_excluded,
    }
    return render(request, 'predictor/evaluation_analytics.html', context)


@require_researcher_access
def evaluation_export_view(request):
    """
    Researcher-only Evaluation Data Export View.
    Generates and returns an atomic ZIP archive containing 7 de-identified CSVs,
    SHA-256 manifest.json, and documentation README.txt.
    """
    from .services.evaluation_export import generate_evaluation_export_zip

    zip_bytes, filename, _manifest = generate_evaluation_export_zip()

    response = HttpResponse(zip_bytes, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = len(zip_bytes)
    return response


@require_researcher_access
def evaluation_exclude_session_view(request, session_id):
    """
    Toggle protocol exclusion status on an EvaluationSession.
    Only allows pre-specified protocol reasons per E1_ANALYSIS_PLAN.md §6.2.
    """
    session_obj = get_object_or_404(EvaluationSession, id=session_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'exclude':
            reason = request.POST.get('exclusion_reason', 'other')
            notes = request.POST.get('exclusion_notes', '').strip()
            session_obj.is_excluded = True
            session_obj.exclusion_reason = reason
            session_obj.exclusion_notes = notes
            session_obj.excluded_at = timezone.now()
            session_obj.save(update_fields=['is_excluded', 'exclusion_reason', 'exclusion_notes', 'excluded_at'])
            messages.success(request, f"Session {session_obj.id} marked as excluded ({reason}).")
        elif action == 'reinstate':
            session_obj.is_excluded = False
            session_obj.exclusion_reason = ''
            session_obj.exclusion_notes = ''
            session_obj.excluded_at = None
            session_obj.save(update_fields=['is_excluded', 'exclusion_reason', 'exclusion_notes', 'excluded_at'])
            messages.success(request, f"Session {session_obj.id} reinstated.")

    return redirect('predictor:evaluation_analytics')


