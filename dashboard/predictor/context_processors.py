"""
Context processors for the predictor dashboard.
Provides application mode and operational flags to templates.
"""
from django.conf import settings


def app_environment(request):
    """Exposes application operational mode and environment indicators."""
    mode = getattr(settings, 'APP_MODE', 'feedback_lab').lower()
    data_mode = getattr(settings, 'APP_DATA_MODE', None)
    if data_mode:
        data_mode = str(data_mode).lower()
        is_dev = data_mode == 'development'
        is_study = data_mode == 'study'
    else:
        is_dev = mode == 'feedback_lab'
        is_study = mode == 'evaluation'
        data_mode = 'development' if is_dev else 'study'

    return {
        'APP_MODE': mode,
        'IS_EVALUATION_MODE': mode == 'evaluation',
        'IS_FEEDBACK_LAB_MODE': mode == 'feedback_lab',
        'APP_VERSION': 'research-prototype-v1.0',
        'EVALUATION_PROTOCOL_VERSION': 'v1.0.3',
        # Backward-compatibility flags
        'APP_DATA_MODE': data_mode,
        'IS_DEVELOPMENT_MODE': is_dev,
        'IS_STUDY_MODE': is_study,
    }

