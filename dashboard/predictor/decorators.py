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
