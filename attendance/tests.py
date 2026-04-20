"""
PLASU Smart Attendance System — Test Suite
Run with: python manage.py test attendance
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Faculty, Department, Course, LecturerProfile,
    StudentProfile, AttendanceSession, AttendanceRecord, FingerprintTemplate,
)
from .utils import attendance_percentage, fingerprint_hash, fingerprint_reference

User = get_user_model()


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_admin():
    return User.objects.create_superuser(
        email="admin_test@plasu.edu.ng",
        password="testpass123",
        first_name="Test", last_name="Admin",
    )


def make_faculty():
    return Faculty.objects.create(name="Test Faculty", code="TF01")


def make_department(faculty):
    return Department.objects.create(name="Test Dept", code="TD01", faculty=faculty)


def make_lecturer(department):
    user = User.objects.create_user(
        email="lect_test@plasu.edu.ng",
        password="testpass123",
        first_name="Test", last_name="Lecturer",
        role="lecturer",
    )
    profile = LecturerProfile.objects.create(
        user=user, staff_id="TST001", department=department
    )
    FingerprintTemplate.objects.create(
        user=user,
        template_reference=fingerprint_reference(user.id, "lecturer"),
        template_hash=fingerprint_hash(user.id, "lecturer"),
    )
    return profile


def make_student(department):
    user = User.objects.create_user(
        email="stu_test@plasu.edu.ng",
        password="testpass123",
        first_name="Test", last_name="Student",
        role="student",
    )
    profile = StudentProfile.objects.create(
        user=user, matric_number="TST/2024/001",
        department=department, level=100,
    )
    FingerprintTemplate.objects.create(
        user=user,
        template_reference=fingerprint_reference(user.id, "student"),
        template_hash=fingerprint_hash(user.id, "student"),
    )
    return profile


def make_course(department, lecturer):
    return Course.objects.create(
        code="TST101", title="Test Course",
        department=department, lecturer=lecturer,
    )


def make_session(course, lecturer):
    import secrets as _secrets
    token = _secrets.token_urlsafe(32)
    return AttendanceSession.objects.create(
        course=course, lecturer=lecturer,
        session_token=token, qr_data="{}",
        expires_at=timezone.now() + timedelta(hours=1),
    )


# ── Model Tests ───────────────────────────────────────────────────────────────

class FacultyModelTest(TestCase):
    def test_str(self):
        f = Faculty.objects.create(name="Faculty of Science", code="SCI")
        self.assertEqual(str(f), "Faculty of Science")


class DepartmentModelTest(TestCase):
    def setUp(self):
        self.faculty = make_faculty()

    def test_str(self):
        d = Department.objects.create(name="Computer Science", code="CSC", faculty=self.faculty)
        self.assertIn("Computer Science", str(d))

    def test_unique_code(self):
        Department.objects.create(name="Dept A", code="DA01", faculty=self.faculty)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Department.objects.create(name="Dept B", code="DA01", faculty=self.faculty)


class AttendanceSessionModelTest(TestCase):
    def setUp(self):
        fac = make_faculty()
        dept = make_department(fac)
        self.lecturer = make_lecturer(dept)
        self.course = make_course(dept, self.lecturer)

    def test_is_active_true(self):
        session = make_session(self.course, self.lecturer)
        self.assertTrue(session.is_active)

    def test_is_active_false_when_ended(self):
        session = make_session(self.course, self.lecturer)
        session.status = "ended"
        session.save()
        self.assertFalse(session.is_active)

    def test_is_active_false_when_expired(self):
        import secrets as _secrets
        token = _secrets.token_urlsafe(32)
        session = AttendanceSession.objects.create(
            course=self.course, lecturer=self.lecturer,
            session_token=token, qr_data="{}",
            expires_at=timezone.now() - timedelta(minutes=5),
        )
        self.assertFalse(session.is_active)


class AttendanceRecordUniqueTest(TestCase):
    def setUp(self):
        fac = make_faculty()
        dept = make_department(fac)
        self.lecturer = make_lecturer(dept)
        self.course = make_course(dept, self.lecturer)
        self.student = make_student(dept)
        self.course.students.add(self.student)
        self.session = make_session(self.course, self.lecturer)

    def test_duplicate_attendance_raises(self):
        AttendanceRecord.objects.create(
            session=self.session, student=self.student, status="present"
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            AttendanceRecord.objects.create(
                session=self.session, student=self.student, status="present"
            )


# ── Utility Tests ─────────────────────────────────────────────────────────────

class UtilsTest(TestCase):
    def test_attendance_percentage_normal(self):
        self.assertEqual(attendance_percentage(7, 10), 70)

    def test_attendance_percentage_zero_total(self):
        self.assertEqual(attendance_percentage(0, 0), 0)

    def test_attendance_percentage_full(self):
        self.assertEqual(attendance_percentage(10, 10), 100)

    def test_fingerprint_hash_consistent(self):
        h1 = fingerprint_hash("abc", "student")
        h2 = fingerprint_hash("abc", "student")
        self.assertEqual(h1, h2)

    def test_fingerprint_reference_prefix(self):
        ref = fingerprint_reference("some-uuid-here", "student")
        self.assertTrue(ref.startswith("FP-STU-"))


# ── View / Auth Tests ─────────────────────────────────────────────────────────

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_admin()

    def test_login_page_loads(self):
        resp = self.client.get(reverse("attendance:login"))
        self.assertEqual(resp.status_code, 200)

    def test_valid_login_redirects(self):
        resp = self.client.post(reverse("attendance:login"), {
            "email": "admin_test@plasu.edu.ng",
            "password": "testpass123",
        })
        self.assertRedirects(resp, reverse("attendance:dashboard"), fetch_redirect_response=False)

    def test_invalid_login_stays(self):
        resp = self.client.post(reverse("attendance:login"), {
            "email": "admin_test@plasu.edu.ng",
            "password": "wrongpassword",
        })
        self.assertEqual(resp.status_code, 200)

    def test_unauthenticated_dashboard_redirects(self):
        resp = self.client.get(reverse("attendance:dashboard"))
        self.assertEqual(resp.status_code, 302)


class RoleBasedAccessTest(TestCase):
    def setUp(self):
        fac = make_faculty()
        dept = make_department(fac)
        self.admin_user = make_admin()
        self.lecturer_profile = make_lecturer(dept)
        self.student_profile = make_student(dept)
        self.client = Client()

    def test_student_cannot_access_admin_dashboard(self):
        self.client.force_login(self.student_profile.user)
        resp = self.client.get(reverse("attendance:admin_dashboard"))
        self.assertRedirects(resp, reverse("attendance:dashboard"), fetch_redirect_response=False)

    def test_lecturer_cannot_access_admin_dashboard(self):
        self.client.force_login(self.lecturer_profile.user)
        resp = self.client.get(reverse("attendance:admin_dashboard"))
        self.assertRedirects(resp, reverse("attendance:dashboard"), fetch_redirect_response=False)

    def test_admin_can_access_admin_dashboard(self):
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse("attendance:admin_dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_lecturer_accesses_lecturer_dashboard(self):
        self.client.force_login(self.lecturer_profile.user)
        resp = self.client.get(reverse("attendance:lecturer_dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_student_accesses_student_dashboard(self):
        self.client.force_login(self.student_profile.user)
        resp = self.client.get(reverse("attendance:student_dashboard"))
        self.assertEqual(resp.status_code, 200)


class AttendanceAPITest(TestCase):
    def setUp(self):
        fac = make_faculty()
        dept = make_department(fac)
        self.lecturer = make_lecturer(dept)
        self.student = make_student(dept)
        self.course = make_course(dept, self.lecturer)
        self.course.students.add(self.student)
        self.session = make_session(self.course, self.lecturer)
        self.client = Client()

    def test_session_status_api(self):
        self.client.force_login(self.lecturer.user)
        resp = self.client.get(
            reverse("attendance:api_session_status", args=[self.session.id])
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("status", data)
        self.assertTrue(data["is_active"])

    def test_attendance_count_api(self):
        self.client.force_login(self.lecturer.user)
        resp = self.client.get(
            reverse("attendance:api_attendance_count", args=[self.session.id])
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 0)

    def test_attend_session_page_loads(self):
        self.client.force_login(self.student.user)
        resp = self.client.get(
            reverse("attendance:attend_session", args=[self.session.session_token])
        )
        self.assertEqual(resp.status_code, 200)
