"""
PLASU Smart Attendance System — Context Processors
Inject global variables into every template context.
"""
from django.utils import timezone
from .models import AttendanceSession


def site_context(request):
    """Inject site-wide variables available in all templates."""
    context = {
        'site_name': 'PLASU Smart Attendance',
        'university_name': 'Plateau State University',
        'current_year': timezone.now().year,
        'now': timezone.now(),
    }
    if request.user.is_authenticated:
        if request.user.role == 'lecturer':
            try:
                active_count = AttendanceSession.objects.filter(
                    lecturer__user=request.user,
                    status='active',
                ).count()
                context['lecturer_active_sessions'] = active_count
            except Exception:
                context['lecturer_active_sessions'] = 0
    return context
