from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Decorator to restrict view access by user role."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('attendance:login')
            if request.user.role not in roles:
                messages.error(request, f'Access denied. This page requires {" or ".join(roles)} role.')
                return redirect('attendance:dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
