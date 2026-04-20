"""
Management command: python manage.py seed_data
Seeds the database with initial PLASU mock data.
"""
import hashlib
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from attendance.models import (
    Faculty, Department, Course, LecturerProfile,
    StudentProfile, FingerprintTemplate
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with initial PLASU mock data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Seeding PLASU Attendance Database...'))

        # ── Admin ────────────────────────────────────────────────────
        if not User.objects.filter(email='admin@plasu.edu.ng').exists():
            admin = User.objects.create_superuser(
                email='admin@plasu.edu.ng',
                password='admin1234',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            self.stdout.write(f'  ✓ Admin: {admin.email}')

        # ── Faculties ────────────────────────────────────────────────
        fnas, _ = Faculty.objects.get_or_create(
            code='FNAS',
            defaults={'name': 'Faculty of Natural and Applied Sciences'}
        )
        farts, _ = Faculty.objects.get_or_create(
            code='ARTS',
            defaults={'name': 'Faculty of Arts'}
        )
        self.stdout.write(f'  ✓ Faculties: {fnas.name}, {farts.name}')

        # ── Departments ──────────────────────────────────────────────
        cs, _ = Department.objects.get_or_create(code='CSC', defaults={'name': 'Computer Science', 'faculty': fnas})
        mth, _ = Department.objects.get_or_create(code='MTH', defaults={'name': 'Mathematics', 'faculty': fnas})
        eng, _ = Department.objects.get_or_create(code='ENG', defaults={'name': 'English', 'faculty': farts})
        his, _ = Department.objects.get_or_create(code='HIS', defaults={'name': 'History', 'faculty': farts})
        self.stdout.write(f'  ✓ Departments: CS, Mathematics, English, History')

        # ── Lecturers ────────────────────────────────────────────────
        lecturers_data = [
            ('heman.mangu@plasu.edu.ng', 'Heman', 'Mangu', 'STAFF001', cs),
            ('kalamba.aristakus@plasu.edu.ng', 'Kalamba', 'Aristakus', 'STAFF002', cs),
            ('palang.mangut@plasu.edu.ng', 'Palang', 'Mangut', 'STAFF003', cs),
        ]
        lecturers = {}
        for email, first, last, staff_id, dept in lecturers_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email, password='lecturer1234',
                    first_name=first, last_name=last, role='lecturer'
                )
                profile = LecturerProfile.objects.create(
                    user=user, department=dept, staff_id=staff_id
                )
                fp_hash = hashlib.sha256(f"{user.id}lecturer".encode()).hexdigest()
                FingerprintTemplate.objects.get_or_create(
                    user=user,
                    defaults={
                        'template_reference': f"LECT-FP-{staff_id}",
                        'template_hash': fp_hash,
                    }
                )
                lecturers[staff_id] = profile
                self.stdout.write(f'  ✓ Lecturer: {first} {last}')
            else:
                lecturers[staff_id] = LecturerProfile.objects.get(staff_id=staff_id)

        heman = lecturers.get('STAFF001')
        kalamba = lecturers.get('STAFF002')
        palang = lecturers.get('STAFF003')

        # ── Courses ──────────────────────────────────────────────────
        courses_data = [
            # CSC - Heman Mangu
            ('CSC401', 'Artificial Intelligence', cs, heman, 3, 'first', 400),
            ('CSC403', 'Software Engineering', cs, heman, 3, 'first', 400),
            # CSC - Kalamba
            ('CSC301', 'Data Structures', cs, kalamba, 3, 'first', 300),
            ('CSC305', 'Database Systems', cs, kalamba, 3, 'second', 300),
            # CSC - Palang
            ('CSC201', 'Introduction to Programming', cs, palang, 3, 'first', 200),
            ('CSC203', 'Computer Architecture', cs, palang, 3, 'second', 200),
            # Mathematics
            ('MTH101', 'Calculus I', mth, None, 3, 'first', 100),
            ('MTH201', 'Linear Algebra', mth, None, 3, 'first', 200),
            # English
            ('ENG101', 'Use of English', eng, None, 2, 'first', 100),
            ('ENG201', 'Literature in English', eng, None, 3, 'first', 200),
            # History
            ('HIS101', 'African History', his, None, 3, 'first', 100),
            ('HIS201', 'Modern History', his, None, 3, 'first', 200),
        ]
        course_objs = {}
        for code, title, dept, lecturer, cu, sem, level in courses_data:
            c, created = Course.objects.get_or_create(
                code=code,
                defaults={
                    'title': title, 'department': dept, 'lecturer': lecturer,
                    'credit_units': cu, 'semester': sem, 'level': level
                }
            )
            course_objs[code] = c
            if created:
                self.stdout.write(f'  ✓ Course: {code} - {title}')

        # ── Students ─────────────────────────────────────────────────
        students_data = [
            ('john.doe@student.plasu.edu.ng', 'John', 'Doe', 'CSC/2021/001', cs, 400),
            ('jane.smith@student.plasu.edu.ng', 'Jane', 'Smith', 'CSC/2021/002', cs, 400),
            ('mike.johnson@student.plasu.edu.ng', 'Mike', 'Johnson', 'CSC/2022/001', cs, 300),
            ('sarah.williams@student.plasu.edu.ng', 'Sarah', 'Williams', 'CSC/2022/002', cs, 300),
            ('david.brown@student.plasu.edu.ng', 'David', 'Brown', 'CSC/2023/001', cs, 200),
            ('emily.davis@student.plasu.edu.ng', 'Emily', 'Davis', 'MTH/2021/001', mth, 400),
            ('james.wilson@student.plasu.edu.ng', 'James', 'Wilson', 'ENG/2021/001', eng, 400),
            ('grace.taylor@student.plasu.edu.ng', 'Grace', 'Taylor', 'HIS/2021/001', his, 400),
        ]

        student_course_map = {
            'CSC/2021/001': ['CSC401', 'CSC403'],
            'CSC/2021/002': ['CSC401', 'CSC403'],
            'CSC/2022/001': ['CSC301', 'CSC305'],
            'CSC/2022/002': ['CSC301', 'CSC305'],
            'CSC/2023/001': ['CSC201', 'CSC203'],
            'MTH/2021/001': ['MTH101', 'MTH201'],
            'ENG/2021/001': ['ENG101', 'ENG201'],
            'HIS/2021/001': ['HIS101', 'HIS201'],
        }

        for email, first, last, matric, dept, level in students_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email, password='student1234',
                    first_name=first, last_name=last, role='student'
                )
                student = StudentProfile.objects.create(
                    user=user, department=dept,
                    matric_number=matric, level=level
                )
                # Enroll in courses
                course_codes = student_course_map.get(matric, [])
                for code in course_codes:
                    if code in course_objs:
                        student.courses.add(course_objs[code])
                # Fingerprint
                fp_hash = hashlib.sha256(f"{user.id}student".encode()).hexdigest()
                FingerprintTemplate.objects.get_or_create(
                    user=user,
                    defaults={
                        'template_reference': f"STU-FP-{matric.replace('/', '-')}",
                        'template_hash': fp_hash,
                    }
                )
                self.stdout.write(f'  ✓ Student: {first} {last} ({matric})')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Seeding complete!'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('━━━ Login Credentials ━━━'))
        self.stdout.write('Admin:    admin@plasu.edu.ng  / admin1234')
        self.stdout.write('Lecturer: heman.mangu@plasu.edu.ng  / lecturer1234')
        self.stdout.write('Lecturer: kalamba.aristakus@plasu.edu.ng  / lecturer1234')
        self.stdout.write('Lecturer: palang.mangut@plasu.edu.ng  / lecturer1234')
        self.stdout.write('Student:  john.doe@student.plasu.edu.ng  / student1234')
        self.stdout.write('')
