"""
Initial migration for PLASU Smart Attendance System.
Generated manually — run: python manage.py migrate
"""
import uuid
import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # ── User ──────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('lecturer', 'Lecturer'), ('student', 'Student')], default='student', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
            managers=[('objects', django.contrib.auth.models.BaseUserManager())],
        ),
        # ── Faculty ───────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name_plural': 'Faculties', 'ordering': ['name']},
        ),
        # ── Department ────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='attendance.faculty')),
            ],
            options={'ordering': ['name'], 'unique_together': {('name', 'faculty')}},
        ),
        # ── LecturerProfile ───────────────────────────────────────────────────
        migrations.CreateModel(
            name='LecturerProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('staff_id', models.CharField(max_length=50, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('qualification', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lecturers', to='attendance.department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='lecturer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        # ── StudentProfile ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('matric_number', models.CharField(max_length=50, unique=True)),
                ('level', models.IntegerField(choices=[(100, '100'), (200, '200'), (300, '300'), (400, '400'), (500, '500')], default=100)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='attendance.department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        # ── FingerprintTemplate ───────────────────────────────────────────────
        migrations.CreateModel(
            name='FingerprintTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('template_reference', models.CharField(max_length=256)),
                ('template_hash', models.CharField(max_length=64)),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fingerprint', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        # ── Course ────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('credit_units', models.IntegerField(default=3)),
                ('semester', models.CharField(choices=[('first', 'First'), ('second', 'Second')], default='first', max_length=20)),
                ('level', models.IntegerField(default=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='attendance.department')),
                ('lecturer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to='attendance.lecturerprofile')),
                ('students', models.ManyToManyField(blank=True, related_name='courses', to='attendance.studentprofile')),
            ],
            options={'ordering': ['code']},
        ),
        # ── AttendanceSession ─────────────────────────────────────────────────
        migrations.CreateModel(
            name='AttendanceSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_token', models.CharField(max_length=64, unique=True)),
                ('qr_data', models.TextField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('ended', 'Ended'), ('expired', 'Expired')], default='active', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('venue', models.CharField(blank=True, max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='attendance.course')),
                ('lecturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='attendance.lecturerprofile')),
            ],
            options={'ordering': ['-started_at']},
        ),
        # ── AttendanceRecord ──────────────────────────────────────────────────
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late')], default='present', max_length=20)),
                ('marked_at', models.DateTimeField(auto_now_add=True)),
                ('fingerprint_verified', models.BooleanField(default=False)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('device_info', models.CharField(blank=True, max_length=500)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='attendance.attendancesession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='attendance.studentprofile')),
            ],
            options={'ordering': ['-marked_at'], 'unique_together': {('session', 'student')}},
        ),
    ]
