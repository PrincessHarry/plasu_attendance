"""
Management command: python manage.py seed_data
Seeds the database with initial PLASU mock data.
Names, emails, matric numbers aligned with live screenshot data.
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
        self.stdout.write(self.style.SUCCESS('Seeding PLASU Attendance Database...'))

        # Admin
        if not User.objects.filter(email='admin@plasu.edu.ng').exists():
            admin = User.objects.create_superuser(
                email='admin@plasu.edu.ng',
                password='PLASUAdmin@2024',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            self.stdout.write(f'  Admin: {admin.email}')

        # Faculties
        fnas, _ = Faculty.objects.get_or_create(code='FNAS', defaults={'name': 'Faculty of Natural and Applied Sciences'})
        farts, _ = Faculty.objects.get_or_create(code='ARTS', defaults={'name': 'Faculty of Arts'})
        self.stdout.write(f'  Faculties created')

        # Departments
        cs,  _ = Department.objects.get_or_create(code='CSC', defaults={'name': 'Computer Science', 'faculty': fnas})
        mth, _ = Department.objects.get_or_create(code='MTH', defaults={'name': 'Mathematics',      'faculty': fnas})
        eng, _ = Department.objects.get_or_create(code='ENG', defaults={'name': 'English',          'faculty': farts})
        his, _ = Department.objects.get_or_create(code='HIS', defaults={'name': 'History',          'faculty': farts})
        self.stdout.write('  Departments created')

        # Lecturers
        lecturers_data = [
            ('heman.mangut@plasu.edu.ng',       'Heman',   'Mangut',     'STAFF001', cs),
            ('kalamba.aristakus@plasu.edu.ng', 'Kalamba', 'Aristakus', 'STAFF002', cs),
            ('palang.mangut@plasu.edu.ng',     'Palang',  'Mangut',    'STAFF003', cs),
        ]
        lecturers = {}
        for email, first, last, staff_id, dept in lecturers_data:
            user, created_user = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'role': 'lecturer',
                    'is_active': True,
                }
            )
            if created_user:
                user.set_password('PLASULect@2024')
                user.save()
                self.stdout.write(f'  Lecturer: {first} {last}')

            profile = LecturerProfile.objects.filter(user=user).first()
            if not profile:
                profile = LecturerProfile.objects.filter(staff_id=staff_id).first()

            if not profile:
                profile = LecturerProfile.objects.create(
                    user=user,
                    department=dept,
                    staff_id=staff_id
                )
            else:
                if profile.user_id != user.id:
                    profile.user = user
                profile.department = dept
                profile.staff_id = staff_id
                profile.save()

            FingerprintTemplate.objects.get_or_create(
                user=user,
                defaults={
                    'template_reference': f"LECT-FP-{staff_id}",
                    'template_hash': '',  # Will be set during first enrollment
                }
            )
            lecturers[staff_id] = profile

        heman   = lecturers.get('STAFF001')
        kalamba = lecturers.get('STAFF002')
        palang  = lecturers.get('STAFF003')

        # Courses
        courses_data = [
            ('CSC401', 'Artificial Intelligence',     cs,  heman,   3, 'first',  400),
            ('CSC403', 'Software Engineering',        cs,  heman,   3, 'first',  400),
            ('CSC301', 'Data Structures',             cs,  kalamba, 3, 'first',  300),
            ('CSC305', 'Database Systems',            cs,  kalamba, 3, 'second', 300),
            ('CSC201', 'Introduction to Programming', cs,  palang,  3, 'first',  200),
            ('CSC203', 'Computer Architecture',       cs,  palang,  3, 'second', 200),
            ('MTH101', 'Calculus I',                  mth, None,    3, 'first',  100),
            ('MTH201', 'Linear Algebra',              mth, None,    3, 'first',  200),
            ('ENG101', 'Use of English',              eng, None,    2, 'first',  100),
            ('ENG201', 'Literature in English',       eng, None,    3, 'first',  200),
            ('HIS101', 'African History',             his, None,    3, 'first',  100),
            ('HIS201', 'Modern History',              his, None,    3, 'first',  200),
        ]
        course_objs = {}
        for code, title, dept, lecturer, cu, sem, level in courses_data:
            c, created = Course.objects.get_or_create(
                code=code,
                defaults={'title': title, 'department': dept, 'lecturer': lecturer,
                          'credit_units': cu, 'semester': sem, 'level': level}
            )
            course_objs[code] = c
            if created:
                self.stdout.write(f'  Course: {code}')

        # Students — names/emails/matric aligned with screenshot
        # email  = firstname.lastname@student.plasu.edu.ng
        # password = PLASUStu@<serial>
        students_data = [
            # first            last          matric                   dept  lvl
            ('Odelade Gideon', 'Oluwafemi',  'PLASU/2020/FNAS/0024', cs,  400),
            ('James',          'Daniel',     'PLASU/2020/FNAS/008',  eng, 400),
            ('Grace',          'Danjuma',    'PLASU/2020/FNAS/005',  his, 400),
            ('Mike',           'Johnson',    'PLASU/2021/FNAS/003',  cs,  300),
            ('David',          'Mahan',      'PLASU/2022/FNAS/006',  cs,  200),
            ('Mark',           'Methuselah', 'PLASU/2020/FNAS/002',  mth, 400),
            ('Sarah',          'Williams',   'PLASU/2021/FNAS/007',  cs,  300),
            ('Dimka',          'Yilrit',     'PLASU/2020/FNAS/004',  cs,  400),
        ]

        student_course_map = {
            'PLASU/2020/FNAS/0024': ['CSC401', 'CSC403'],
            'PLASU/2020/FNAS/008':  ['ENG101', 'ENG201'],
            'PLASU/2020/FNAS/005':  ['HIS101', 'HIS201'],
            'PLASU/2021/FNAS/003':  ['CSC301', 'CSC305'],
            'PLASU/2022/FNAS/006':  ['CSC201', 'CSC203'],
            'PLASU/2020/FNAS/002':  ['MTH101', 'MTH201'],
            'PLASU/2021/FNAS/007':  ['CSC301', 'CSC305'],
            'PLASU/2020/FNAS/004':  ['CSC401', 'CSC403'],
        }

        for first, last, matric, dept, level in students_data:
            first_slug = first.split()[0].lower()
            last_slug  = last.lower()
            email      = f"{first_slug}.{last_slug}@student.plasu.edu.ng"
            serial     = matric.split('/')[-1]
            password   = f"PLASUStu@{serial}"

            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email, password=password,
                    first_name=first, last_name=last, role='student'
                )
                student = StudentProfile.objects.create(
                    user=user, department=dept, matric_number=matric, level=level
                )
                for code in student_course_map.get(matric, []):
                    if code in course_objs:
                        student.courses.add(course_objs[code])
                FingerprintTemplate.objects.get_or_create(
                    user=user,
                    defaults={
                        'template_reference': f"STU-FP-{matric.replace('/', '-')}",
                        'template_hash': '',  # Will be set during first enrollment
                    }
                )
                self.stdout.write(f'  Student: {first} {last} ({matric})  ->  {email} / {password}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Login Credentials'))
        self.stdout.write('Admin    : admin@plasu.edu.ng                              / PLASUAdmin@2024')
        self.stdout.write('Lecturer : heman.mangut@plasu.edu.ng                        / PLASULect@2024')
        self.stdout.write('Student  : odelade.oluwafemi@student.plasu.edu.ng          / PLASUStu@0024')
        self.stdout.write('Student  : james.daniel@student.plasu.edu.ng               / PLASUStu@008')
        self.stdout.write('')