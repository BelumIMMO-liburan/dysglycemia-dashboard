from django.urls import path
from . import views

app_name = 'predictor'

urlpatterns = [
    # Primary Application Shell Routes (Phase D2.1 Foundation)
    path('', views.overview_view, name='overview'),
    path('screening/new/', views.new_screening_view, name='new_screening'),
    path('screening/run/', views.run_screening_view, name='run_screening'),
    path('screening/<uuid:screening_id>/result/', views.screening_result_view, name='screening_result'),
    path('screening/<uuid:screening_id>/review/accept/', views.accept_review_view, name='accept_review'),
    path('screening/<uuid:screening_id>/review/override/', views.override_review_view, name='override_review'),
    path('screening/<uuid:screening_id>/review/unified/', views.unified_review_view, name='unified_review'),
    path('screening/<uuid:screening_id>/stage2/', views.stage2_view, name='stage2'),
    path('screening/<uuid:screening_id>/stage2/confirm/', views.stage2_confirm_view, name='stage2_confirm'),
    path('review/', views.review_queue_view, name='review_queue'),
    path('history/', views.history_view, name='history'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('about/', views.about_model_view, name='about'),
    path('components/', views.components_demo_view, name='components_demo'),

    # Human Feedback Learning Loop Routes
    path('screening/<uuid:screening_id>/feedback/', views.submit_feedback_view, name='submit_feedback'),
    path('screening/<uuid:screening_id>/compare/', views.run_comparison_view, name='run_comparison'),
    path('feedback-experiment/', views.feedback_experiment_view, name='feedback_experiment'),
    path('feedback-experiment/start-controlled/', views.start_controlled_experiment_view, name='start_controlled_experiment'),
    path('feedback-experiment/run-controlled-learning/', views.run_controlled_learning_view, name='run_controlled_learning'),
    path('feedback-experiment/activate-controlled/', views.activate_controlled_adaptation_view, name='activate_controlled_adaptation'),
    path('feedback-experiment/evaluate-case-b/', views.evaluate_controlled_case_b_view, name='evaluate_controlled_case_b'),
    path('feedback-experiment/reset-controlled/', views.reset_controlled_experiment_view, name='reset_controlled_experiment'),
    path('feedback-experiment/trigger-learning/', views.trigger_learning_view, name='trigger_learning'),
    path('feedback-experiment/activate-candidate/', views.activate_candidate_view, name='activate_candidate'),
    path('feedback-experiment/rollback/', views.rollback_version_view, name='rollback_version'),

    # Participant Evaluation Mode Routes (Protocol E1 v1.0.3 / E2)
    path('evaluation/consent/', views.evaluation_consent_view, name='evaluation_consent'),
    path('evaluation/practice/', views.evaluation_practice_view, name='evaluation_practice'),
    path('evaluation/questionnaire/', views.evaluation_questionnaire_view, name='evaluation_questionnaire'),
    path('evaluation/complete/', views.evaluation_complete_view, name='evaluation_complete'),

    # Researcher-Only Evaluation Infrastructure Routes
    path('evaluation/analytics/', views.evaluation_analytics_view, name='evaluation_analytics'),
    path('evaluation/export/', views.evaluation_export_view, name='evaluation_export'),
    path('evaluation/session/<uuid:session_id>/exclude/', views.evaluation_exclude_session_view, name='evaluation_exclude_session'),

    # Backward-compatible routes for ongoing legacy/audit endpoints
    path('index/', views.index, name='index'),
    path('predict/', views.predict_view, name='predict'),
    path('prediction/<int:pk>/', views.prediction_detail_view, name='prediction_detail'),
    path('override/', views.override_view, name='override'),
    path('evaluation/', views.evaluation_view, name='evaluation'),
]

