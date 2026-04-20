from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Faculty, Department, Course, LecturerProfile,
    StudentProfile, FingerprintTemplate, AttendanceSession, AttendanceRecord
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(LecturerProfile)
admin.site.register(StudentProfile)
admin.site.register(FingerprintTemplate)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
