"""
ASGI config for PLASU Smart Attendance System.
Exposes the ASGI callable as module-level variable named ``application``.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plasu_attendance.settings')
application = get_asgi_application()
