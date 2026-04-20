"""
PLASU Smart Attendance System — Custom Template Tags & Filters
Load in templates with: {% load attendance_tags %}
"""
from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def percentage(value, total):
    """Return integer percentage: {{ attended|percentage:total_sessions }}"""
    try:
        if int(total) == 0:
            return 0
        return round(int(value) / int(total) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def attendance_color(pct):
    """Return Tailwind color class based on attendance percentage."""
    try:
        pct = int(pct)
    except (ValueError, TypeError):
        return 'text-slate-400'
    if pct >= 75:
        return 'text-green-600'
    elif pct >= 50:
        return 'text-yellow-600'
    return 'text-red-500'


@register.filter
def bar_color(pct):
    """Return Tailwind bg color class for progress bars."""
    try:
        pct = int(pct)
    except (ValueError, TypeError):
        return 'bg-slate-300'
    if pct >= 75:
        return 'bg-green-500'
    elif pct >= 50:
        return 'bg-yellow-400'
    return 'bg-red-400'


@register.filter
def initials(user):
    """Return initials from a user object: JD for John Doe."""
    try:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    except (AttributeError, IndexError):
        return '?'


@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter: {{ "a,b,c"|split:"," }}"""
    return value.split(delimiter)


@register.simple_tag
def now_iso():
    """Return current datetime as ISO string for JS."""
    return timezone.now().isoformat()


@register.filter
def mul(value, arg):
    """Multiply filter: {{ value|mul:100 }}"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def sub(value, arg):
    """Subtract filter: {{ total|sub:attended }}"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.inclusion_tag('attendance/partials/stat_card.html')
def stat_card(title, value, subtitle='', icon='', color='green', badge='', badge_color='green'):
    """Reusable stat card inclusion tag."""
    return {
        'title': title,
        'value': value,
        'subtitle': subtitle,
        'icon': icon,
        'color': color,
        'badge': badge,
        'badge_color': badge_color,
    }
