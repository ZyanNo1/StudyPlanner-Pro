# StudyPlanner Pro

A web-based student study planner built with Flask. Helps students manage courses, track tasks, monitor GPA, and get daily study fortune based on zodiac sign.

---

## Features

- **User Authentication** — Register, login, logout with encrypted passwords
- **Course Management** — Add/delete courses with progress tracking
- **Task Management** — Add/delete/complete tasks with priority, due date, and countdown timer
- **GPA Tracker** — Track grades using UT Austin's full +/- scale (A to F), with predicted GPA based on your expected grade for remaining courses
- **Study Statistics** — Study time breakdown by course, task completion rates
- **Daily Study Fortune** — Personalized daily study advice based on zodiac sign (supports Chinese and English zodiac names)
- **Data Isolation** — Each user only sees their own courses, tasks, and grades

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Frontend | HTML, Tailwind CSS, Font Awesome |
| Data Storage | JSON files (no database required) |
| Auth | Werkzeug password hashing (scrypt) |

---

## Project Structure

```
studyplanner-web/
├── app.py                  # Main Flask application
├── data/
│   ├── users.json          # User accounts (hashed passwords)
│   ├── courses.json        # Courses (per-user via owner field)
│   ├── tasks.json          # Tasks (per-user via owner field)
│   └── grades.json         # Grades (per-user dictionary)
├── static/
│   ├── css/style.css
│   └── js/script.js
├── templates/
│   ├── index.html          # Home / Dashboard
│   ├── courses.html        # Course management
│   ├── tasks.html          # Task management
│   ├── stats.html          # Statistics & GPA
│   ├── luck.html           # Daily study fortune
│   ├── login.html
│   └── register.html
└── README.md
```

---

## Getting Started

### 1. Install dependencies

```bash
pip install flask werkzeug
```

### 2. Run the app

```bash
cd codes/studyplanner-web
python app.py
```

### 3. Open in browser

```
http://localhost:5000
```

---

## GPA Scale (UT Austin)

| Grade | Points |
|-------|--------|
| A     | 4.00   |
| A-    | 3.67   |
| B+    | 3.33   |
| B     | 3.00   |
| B-    | 2.67   |
| C+    | 2.33   |
| C     | 2.00   |
| C-    | 1.67   |
| D+    | 1.33   |
| D     | 1.00   |
| D-    | 0.67   |
| F     | 0.00   |

Predicted GPA is calculated using your actual grades for completed courses plus your chosen **expected grade** (default: B+) for remaining courses.

---

## Data Isolation

Every course, task, and grade is tagged with an `owner` field matching the logged-in username.  
Users can only view and modify their own data. Legacy data without an `owner` field is automatically migrated on startup.

---

## Notes

- Data is stored in plain JSON files — suitable for personal/demo use

- No database setup required

- Passwords are hashed using `scrypt` via Werkzeug; legacy plaintext passwords are auto-upgraded on first login

---

## Team:

- Zyan Li @[ZyanNo1]([ZyanNo1 (Zyan Li)](https://github.com/ZyanNo1))
- Shijun Tian @[frozen66-ai](https://github.com/frozen66-ai)
- Qinyan Liu @[qinyanliu](https://github.com/qinyanliu)