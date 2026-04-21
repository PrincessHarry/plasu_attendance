from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Auth
    path('', views.index_redirect, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),

    # Password reset
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/faculties/', views.manage_faculties, name='manage_faculties'),
    path('admin/faculties/add/', views.add_faculty, name='add_faculty'),
    path('admin/faculties/<uuid:pk>/edit/', views.edit_faculty, name='edit_faculty'),
    path('admin/faculties/<uuid:pk>/delete/', views.delete_faculty, name='delete_faculty'),
    path('admin/departments/', views.manage_departments, name='manage_departments'),
    path('admin/departments/add/', views.add_department, name='add_department'),
    path('admin/departments/<uuid:pk>/edit/', views.edit_department, name='edit_department'),
    path('admin/departments/<uuid:pk>/delete/', views.delete_department, name='delete_department'),
    path('admin/courses/', views.manage_courses, name='manage_courses'),
    path('admin/courses/add/', views.add_course, name='add_course'),
    path('admin/courses/<uuid:pk>/edit/', views.edit_course, name='edit_course'),
    path('admin/courses/<uuid:pk>/delete/', views.delete_course, name='delete_course'),
    path('admin/lecturers/', views.manage_lecturers, name='manage_lecturers'),
    path('admin/lecturers/add/', views.add_lecturer, name='add_lecturer'),
    path('admin/lecturers/<uuid:pk>/edit/', views.edit_lecturer, name='edit_lecturer'),
    path('admin/lecturers/<uuid:pk>/delete/', views.delete_lecturer, name='delete_lecturer'),
    path('admin/students/', views.manage_students, name='manage_students'),
    path('admin/students/add/', views.add_student, name='add_student'),
    path('admin/students/bulk-upload/', views.bulk_upload_students, name='bulk_upload_students'),
    path('admin/students/bulk-upload/template/', views.download_student_template, name='download_student_template'),
    path('admin/students/<uuid:pk>/edit/', views.edit_student, name='edit_student'),
    path('admin/students/<uuid:pk>/delete/', views.delete_student, name='delete_student'),
    path('admin/attendance/', views.admin_attendance_records, name='admin_attendance_records'),
    path('admin/attendance/export/', views.export_attendance_csv, name='export_attendance_csv'),

    # Lecturer
    path('lecturer-dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('lecturer/courses/', views.lecturer_courses, name='lecturer_courses'),
    path('lecturer/sessions/', views.lecturer_sessions, name='lecturer_sessions'),
    path('lecturer/sessions/start/', views.start_session, name='start_session'),
    path('lecturer/sessions/<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('lecturer/sessions/<uuid:session_id>/end/', views.end_session, name='end_session'),
    path('lecturer/sessions/<uuid:session_id>/qr/', views.session_qr, name='session_qr'),
    path('lecturer/attendance/<uuid:course_id>/', views.lecturer_attendance_history, name='lecturer_attendance_history'),

    # Student
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/attendance/', views.student_attendance_history, name='student_attendance_history'),
    path('student/scan/', views.scan_qr, name='scan_qr'),
    path('attend/<str:token>/', views.attend_session, name='attend_session'),
    path('verify-fingerprint/<uuid:session_id>/', views.verify_fingerprint, name='verify_fingerprint'),

    # API
    path('api/session/<uuid:session_id>/status/', views.api_session_status, name='api_session_status'),
    path('api/session/<uuid:session_id>/count/', views.api_attendance_count, name='api_attendance_count'),
    path('api/verify-fingerprint/', views.api_verify_fingerprint, name='api_verify_fingerprint'),
    path('api/mark-attendance/', views.api_mark_attendance, name='api_mark_attendance'),
]