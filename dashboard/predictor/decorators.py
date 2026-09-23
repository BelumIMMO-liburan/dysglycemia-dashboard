"""
Route and API mode protection decorators.

Enforces strict backend isolation between:
- 'evaluation': Participant-facing evaluation mode (Railway hosted).
- 'feedback_lab': Researcher-facing model adaptation and governance mode (Localhost).
"""
import functools
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render


def require_app_mode(required_mode: str):
    """
    Decorator that restricts view execution to a specific application mode.
    
    If the current APP_MODE does not match required_mode, returns HTTP 403 Forbidden.
    This prevents participants in Evaluation Mode from accessing researcher endpoints
    (learning batch trigger, candidate activation, rollback, comparison, etc.)
    by guessing URLs or crafting POST requests.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            current_mode = getattr(settings, 'APP_MODE', 'feedback_lab').lower()
            if current_mode != required_mode.lower():
                msg = (
                    f"Access Denied: This endpoint is restricted to '{required_mode}' mode. "
                    f"Current system mode is '{current_mode}'."
                )
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
                    return JsonResponse({'error': msg, 'status': 403}, status=403)
                
                return HttpResponseForbidden(
                    f"<h1>403 Forbidden</h1><p>{msg}</p><p><a href='/'>Return to Home</a></p>"
                )
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_researcher_access(view_func):
    """
    Restricts access to researcher-only administrative views (Analytics, Data Export).

    Access Governance:
    1. Feedback Lab Mode ('feedback_lab'):
       Directly permitted (this mode is exclusively researcher-facing on localhost).
    2. Evaluation Mode ('evaluation'):
       Requires authenticated staff/superuser (request.user.is_staff or is_superuser),
       OR a verified RESEARCHER_ACCESS_KEY provided via header X-Researcher-Key, parameter,
       or session.
       Ordinary participants and anonymous visitors are rejected with HTTP 403 Forbidden.
    """
    import os

    @functools.wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        current_mode = getattr(settings, 'APP_MODE', 'feedback_lab').lower()
        if current_mode == 'feedback_lab':
            return view_func(request, *args, **kwargs)

        # In evaluation mode: verify staff authentication or researcher secret key
        user = getattr(request, 'user', None)
        is_staff_auth = user and user.is_authenticated and (user.is_staff or user.is_superuser)
        if is_staff_auth:
            return view_func(request, *args, **kwargs)

        # Check configured researcher access key
        expected_key = getattr(settings, 'RESEARCHER_ACCESS_KEY', '') or os.environ.get('RESEARCHER_ACCESS_KEY', '').strip()
        if expected_key:
            header_key = request.headers.get('X-Researcher-Key', '').strip()
            param_key = (
                request.GET.get('key', '').strip()
                or request.GET.get('researcher_key', '').strip()
                or request.POST.get('key', '').strip()
                or request.POST.get('researcher_key', '').strip()
            )
            session_key = request.session.get('researcher_access_granted_key', '').strip()

            if header_key == expected_key or param_key == expected_key or session_key == expected_key:
                request.session['researcher_access_granted_key'] = expected_key
                return view_func(request, *args, **kwargs)

        # Rejection
        msg = (
            "Access Denied: This endpoint is restricted to authorized study researchers. "
            "Participant accounts are prohibited from accessing evaluation analytics or data exports."
        )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
            return JsonResponse({'error': msg, 'status': 403}, status=403)

        return HttpResponseForbidden(
            f"<h1>403 Forbidden</h1><p>{msg}</p><p><a href='/'>Return to Home</a></p>"
        )

    return _wrapped_view

