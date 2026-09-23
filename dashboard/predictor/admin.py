from django.contrib import admin
from .models import (
    Prediction, Override,
    EvaluationRespondent, EvaluationSession, EvaluationEvent, QuestionnaireResponse,
    ScreeningRecord, HumanReview, Stage2Assessment
)


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'model_used', 'prediction', 'confidence', 'threshold', 'is_reviewed']
    list_filter = ['model_used', 'prediction', 'is_reviewed']
    search_fields = ['model_used']
    readonly_fields = ['timestamp', 'patient_data', 'model_used', 'prediction', 'confidence', 'threshold', 'shap_values']


@admin.register(Override)
class OverrideAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'prediction', 'doctor_name', 'decision', 'override_value']
    list_filter = ['decision', 'doctor_name']
    search_fields = ['doctor_name', 'reason']
    readonly_fields = ['timestamp']


@admin.register(EvaluationRespondent)
class EvaluationRespondentAdmin(admin.ModelAdmin):
    list_display = ['respondent_code', 'age_group', 'education_level', 'health_background', 'created_at']
    list_filter = ['age_group', 'education_level', 'health_background']
    search_fields = ['respondent_code']
    readonly_fields = ['created_at', 'consent_timestamp']


@admin.register(EvaluationSession)
class EvaluationSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'respondent', 'status', 'practice_completed', 'questionnaire_completed', 'is_excluded', 'exclusion_reason', 'started_at']
    list_filter = ['status', 'practice_completed', 'questionnaire_completed', 'is_excluded']
    search_fields = ['id', 'respondent__respondent_code']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'sus_score', 'submitted_at']
    search_fields = ['session__id', 'session__respondent__respondent_code']
    readonly_fields = ['submitted_at']


@admin.register(ScreeningRecord)
class ScreeningRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'screening_probability', 'ai_referral_recommended', 'is_practice', 'evaluation_session']
    list_filter = ['is_practice', 'ai_referral_recommended']
    search_fields = ['id', 'idempotency_token']
    readonly_fields = ['created_at']

