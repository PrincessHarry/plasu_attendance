"""
PLASU Smart Attendance System — Forms
Centralised form definitions used by views.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import (
    User, Faculty, Department, Course,
    LecturerProfile, StudentProfile, AttendanceSession,
)


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-input pl-11',
            'placeholder': 'you@plasu.edu.ng',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input pl-11 pr-11',
            'placeholder': '••••••••',
        })
    )


# ─── Faculty ──────────────────────────────────────────────────────────────────

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Faculty of Natural and Applied Sciences'}),
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. FNAS', 'style': 'text-transform:uppercase'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    def clean_code(self):
        return self.cleaned_data['code'].upper().strip()


# ─── Department ───────────────────────────────────────────────────────────────

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'faculty', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Computer Science'}),
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CSC', 'style': 'text-transform:uppercase'}),
            'faculty': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    def clean_code(self):
        return self.cleaned_data['code'].upper().strip()


# ─── Course ───────────────────────────────────────────────────────────────────

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'title', 'department', 'lecturer', 'credit_units', 'semester', 'level', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CSC401', 'style': 'text-transform:uppercase'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Artificial Intelligence'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'lecturer': forms.Select(attrs={'class': 'form-input'}),
            'credit_units': forms.Select(choices=[(i, i) for i in range(1, 7)], attrs={'class': 'form-input'}),
            'semester': forms.Select(attrs={'class': 'form-input'}),
            'level': forms.Select(choices=[(l, f'{l} Level') for l in [100,200,300,400,500]], attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    def clean_code(self):
        return self.cleaned_data['code'].upper().strip()


# ─── Lecturer ─────────────────────────────────────────────────────────────────

class LecturerUserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Leave blank to keep current'}),
        help_text='Leave blank when editing to keep existing password.'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'name@plasu.edu.ng'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A user with this email already exists.')
        return email


class LecturerProfileForm(forms.ModelForm):
    class Meta:
        model = LecturerProfile
        fields = ['staff_id', 'department', 'phone', 'qualification']
        widgets = {
            'staff_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. STAFF001'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+234...'}),
            'qualification': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. PhD Computer Science'}),
        }


# ─── Student ──────────────────────────────────────────────────────────────────

class StudentUserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Leave blank to keep current'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'student@student.plasu.edu.ng'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A user with this email already exists.')
        return email


class StudentProfileForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label='Enrolled Courses',
    )

    class Meta:
        model = StudentProfile
        fields = ['matric_number', 'department', 'level', 'phone', 'courses']
        widgets = {
            'matric_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CSC/2021/001'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'level': forms.Select(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+234...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['courses'].initial = self.instance.courses.all()


# ─── Attendance Session ───────────────────────────────────────────────────────

class StartSessionForm(forms.Form):
    DURATION_CHOICES = [
        (30, '30 minutes'),
        (60, '1 hour'),
        (90, '1.5 hours'),
        (120, '2 hours'),
        (180, '3 hours'),
    ]
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        empty_label='-- Choose a course --',
        widget=forms.Select(attrs={'class': 'form-input'}),
    )
    venue = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Lecture Hall A, Room 201'}),
    )
    duration = forms.ChoiceField(
        choices=DURATION_CHOICES,
        initial=60,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    def __init__(self, lecturer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=lecturer)
