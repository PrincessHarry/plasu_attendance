"""
PLASU Smart Attendance System — DRF Serializers
Used by REST API endpoints.
"""
from rest_framework import serializers
from .models import (
    User, Faculty, Department, Course,
    LecturerProfile, StudentProfile,
    AttendanceSession, AttendanceRecord, FingerprintTemplate,
)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role', 'is_active']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name()


class FacultySerializer(serializers.ModelSerializer):
    department_count = serializers.IntegerField(source='departments.count', read_only=True)

    class Meta:
        model = Faculty
        fields = ['id', 'name', 'code', 'description', 'department_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    student_count = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'faculty', 'faculty_name', 'student_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    lecturer_name   = serializers.SerializerMethodField()
    student_count   = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'title', 'department', 'department_name',
                  'lecturer', 'lecturer_name', 'credit_units', 'semester',
                  'level', 'student_count']
        read_only_fields = ['id']

    def get_lecturer_name(self, obj):
        return obj.lecturer.user.get_full_name() if obj.lecturer else None


class LecturerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    course_count    = serializers.IntegerField(source='courses.count', read_only=True)

    class Meta:
        model = LecturerProfile
        fields = ['id', 'user', 'staff_id', 'department', 'department_name',
                  'phone', 'qualification', 'course_count']
        read_only_fields = ['id']


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'matric_number', 'department', 'department_name',
                  'level', 'phone']
        read_only_fields = ['id']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name   = serializers.CharField(source='student.user.get_full_name', read_only=True)
    matric_number  = serializers.CharField(source='student.matric_number', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student', 'student_name', 'matric_number',
                  'status', 'fingerprint_verified', 'marked_at']
        read_only_fields = ['id', 'marked_at']


class AttendanceSessionSerializer(serializers.ModelSerializer):
    course_code    = serializers.CharField(source='course.code', read_only=True)
    course_title   = serializers.CharField(source='course.title', read_only=True)
    lecturer_name  = serializers.CharField(source='lecturer.user.get_full_name', read_only=True)
    attendance_count = serializers.IntegerField(read_only=True)
    is_active      = serializers.BooleanField(read_only=True)
    records        = AttendanceRecordSerializer(many=True, read_only=True)

    class Meta:
        model = AttendanceSession
        fields = ['id', 'course', 'course_code', 'course_title',
                  'lecturer', 'lecturer_name', 'session_token',
                  'status', 'is_active', 'started_at', 'ended_at',
                  'expires_at', 'venue', 'attendance_count', 'records']
        read_only_fields = ['id', 'session_token', 'started_at', 'qr_data']


class FingerprintTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FingerprintTemplate
        fields = ['id', 'user', 'template_reference', 'enrolled_at', 'is_active']
        read_only_fields = ['id', 'enrolled_at', 'template_hash']
