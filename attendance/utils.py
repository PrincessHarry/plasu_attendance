"""
PLASU Smart Attendance System — Utilities
Helper functions used across views and models.
"""
import hashlib
import json
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


# ── Session token ─────────────────────────────────────────────────────────────

def generate_session_token(length: int = 32) -> str:
    """Return a cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(length)


def build_qr_payload(session_token: str, course_code: str, expires_at) -> str:
    """
    Build the JSON string that gets encoded into the QR code.
    Keep it small — only what's needed to look up the session.
    """
    return json.dumps({
        "session_token": session_token,
        "course_code": course_code,
        "expires_at": expires_at.isoformat(),
    }, separators=(",", ":"))


def session_expires_at(duration_minutes: int = None) -> object:
    """Return a timezone-aware datetime for when a session expires."""
    timeout = duration_minutes or getattr(settings, "QR_SESSION_TIMEOUT", 3600) // 60
    return timezone.now() + timedelta(minutes=timeout)


# ── Fingerprint helpers ───────────────────────────────────────────────────────

def fingerprint_hash(user_id, role: str, extra: str = "") -> str:
    """
    Deterministic hash used as a fingerprint template stub.
    In production replace with real biometric template data.
    """
    raw = f"{user_id}{role}{extra}"
    return hashlib.sha256(raw.encode()).hexdigest()


def fingerprint_reference(user_id, role: str) -> str:
    """Return a human-readable template reference string."""
    prefix = {"lecturer": "LECT", "student": "STU", "admin": "ADMIN"}.get(role, "USR")
    short = str(user_id)[:8].upper()
    return f"FP-{prefix}-{short}"


def simulate_fingerprint_match(stored_hash: str, presented_hash: str) -> bool:
    """
    Simulate a biometric match.
    In production this would call the actual fingerprint SDK / hardware API.
    Returns True if hashes match (i.e., same enrolled user).
    """
    return secrets.compare_digest(stored_hash, presented_hash)


# ── Attendance helpers ────────────────────────────────────────────────────────

def attendance_percentage(attended: int, total: int) -> int:
    """Return integer attendance percentage, or 0 if total is 0."""
    if total <= 0:
        return 0
    return round(attended / total * 100)


def get_client_ip(request) -> str | None:
    """Extract the real client IP, respecting X-Forwarded-For."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_device_info(request) -> str:
    """Return a truncated user-agent string for audit logging."""
    ua = request.META.get("HTTP_USER_AGENT", "")
    return ua[:500]


# ── Export helpers ────────────────────────────────────────────────────────────

def attendance_csv_rows(records_qs):
    """
    Yield CSV rows (as lists) for an AttendanceRecord queryset.
    First row is the header.
    """
    yield [
        "Student Name", "Matric Number", "Course Code", "Course Title",
        "Lecturer", "Status", "Fingerprint Verified", "Marked At", "IP Address",
    ]
    for r in records_qs:
        yield [
            r.student.user.get_full_name(),
            r.student.matric_number,
            r.session.course.code,
            r.session.course.title,
            r.session.lecturer.user.get_full_name(),
            r.get_status_display(),
            "Yes" if r.fingerprint_verified else "No",
            r.marked_at.strftime("%Y-%m-%d %H:%M:%S"),
            r.ip_address or "",
        ]
