"""
PLASU Smart Attendance System — Signals
"""
import hashlib
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import User, AttendanceSession, FingerprintTemplate


@receiver(post_save, sender=User)
def auto_create_fingerprint(sender, instance, created, **kwargs):
    """
    Create a fingerprint template stub when a new lecturer or student is created.
    Uses get_or_create to be idempotent — safe to call multiple times (e.g. from
    seed_data and signal both firing for the same user).
    """
    if created and instance.role in ('lecturer', 'student'):
        fp_hash = hashlib.sha256(
            f"{instance.id}{instance.role}{instance.email}".encode()
        ).hexdigest()
        prefix = 'LECT' if instance.role == 'lecturer' else 'STU'
        FingerprintTemplate.objects.get_or_create(
            user=instance,
            defaults={
                'template_reference': f"FP-{prefix}-{str(instance.id)[:8].upper()}",
                'template_hash': fp_hash,
                'is_active': True,
            }
        )


@receiver(pre_save, sender=AttendanceSession)
def auto_expire_session(sender, instance, **kwargs):
    """Mark session as expired if its expiry time has passed."""
    if instance.status == 'active' and instance.expires_at:
        if timezone.now() > instance.expires_at:
            instance.status = 'expired'
