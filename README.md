# PLASU Smart Attendance System

A smart attendance system for **Plateau State University**

## Features

- **Role-based access**: Admin, Lecturer, Student dashboards
- **QR Code sessions**: Lecturers generate session QR codes; students scan to attend
- **Fingerprint simulation**: Biometric verification flow (simulated; WebAuthn-ready)
- **Live attendance**: Real-time student count polling via REST API
- **Full admin panel**: Manage faculties, departments, courses, lecturers, students
- **CSV export**: Download attendance records
- **Mobile-ready**: Responsive design for student QR scanning

---

## Quick Start

### 1. Prerequisites
```bash
Python 3.10+ required
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up the database
```bash
python manage.py migrate
```

### 4. Seed mock data (PLASU faculties, departments, lecturers, courses, students)
```bash
python manage.py seed_data
```

### 5. Run the development server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Login Credentials (after seeding for testing)

| Role     | Email                                | Password      |
|----------|--------------------------------------|---------------|
| Admin    | admin@plasu.edu.ng                   | admin1234     |
| Lecturer | heman.mangu@plasu.edu.ng             | lecturer1234  |
| Student  | john.doe@student.plasu.edu.ng        | student1234   |


---

## Attendance Flow

1. **Lecturer** logs in → clicks **Start Session** → selects course → QR code generated
2. **Student** opens browser on phone → navigates to `/attend/<token>/` (or scans QR)
3. Student is identified by Django session/login
4. Fingerprint verification screen appears → student taps **Verify Fingerprint**
5. Attendance marked as **Present + Fingerprint Verified**

### Security Rules Enforced
- One record per student per session (`unique_together`)
- Session must be `active` and not expired
- Student must be enrolled in the course
- Fingerprint template must exist



## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/session/<id>/status/` | Get session active/expired status |
| GET | `/api/session/<id>/count/` | Get live attendance count + student list |
| POST | `/api/verify-fingerprint/` | Verify fingerprint and mark attendance |
| POST | `/api/mark-attendance/` | Mark attendance via token |

---

## Tech Stack

- **Backend**: Python 3.10+, Django 4.2, Django REST Framework
- **Frontend**: Tailwind CSS (CDN), Vanilla JavaScript
- **Database**: SQLite (dev) — settings.py is structured for easy PostgreSQL migration
- **QR**: Generated client-side via `qrcode-generator` JS library (no server dependency)
- **Fonts**: Outfit (Google Fonts)

---

## Production Deployment Notes

1. Change `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Switch to PostgreSQL: update `DATABASES` in settings
5. Run `python manage.py collectstatic`
6. Use gunicorn + nginx

---

*PLASU Smart Attendance System — Built for Plateau State University*
