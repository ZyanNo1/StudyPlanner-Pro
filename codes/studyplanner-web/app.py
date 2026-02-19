from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime, date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # For session management

# Data file paths
DATA_DIR = "data"
COURSES_FILE = os.path.join(DATA_DIR, "courses.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
GRADES_FILE = os.path.join(DATA_DIR, "grades.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# Initialize data folder and files
def init_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Initialize courses file
    if not os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    # Initialize tasks file
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    # Initialize grades file
    if not os.path.exists(GRADES_FILE):
        with open(GRADES_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    # Initialize users file
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    migrate_data()


# Load data
def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # Return correct type based on filename
        if "grades.json" in file_path:
            return {}
        return [] if "json" in file_path else {}


# Save data
def save_data(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Save failed: {e}")
        return False


def get_default_owner(users):
    if not users:
        return None
    return sorted(users.keys())[0]


def migrate_data():
    """Migrate legacy data to owner-based isolation and per-user grades."""
    users = load_data(USERS_FILE)
    default_owner = get_default_owner(users)
    if not default_owner:
        return

    courses = load_data(COURSES_FILE)
    tasks = load_data(TASKS_FILE)
    grades = load_data(GRADES_FILE)

    updated = False

    for course in courses:
        if 'owner' not in course:
            course['owner'] = default_owner
            updated = True

    for task in tasks:
        if 'owner' not in task:
            task['owner'] = default_owner
            updated = True

    if grades and all(isinstance(v, str) for v in grades.values()):
        grades = {default_owner: grades}
        updated = True

    if updated:
        save_data(COURSES_FILE, courses)
        save_data(TASKS_FILE, tasks)
        save_data(GRADES_FILE, grades)


def current_user():
    return session.get('username')


def filter_by_owner(items, username):
    return [item for item in items if item.get('owner') == username]


def get_user_grades(grades, username):
    if not isinstance(grades, dict):
        return {}
    return grades.get(username, {})


def get_next_id(items):
    max_id = 0
    for item in items:
        try:
            max_id = max(max_id, int(item.get('id', 0)))
        except (TypeError, ValueError):
            continue
    return max_id + 1


# Generate daily study luck
ZODIAC_ALIASES = {
    "白羊座": "Aries",
    "金牛座": "Taurus",
    "双子座": "Gemini",
    "巨蟹座": "Cancer",
    "狮子座": "Leo",
    "处女座": "Virgo",
    "天秤座": "Libra",
    "天蝎座": "Scorpio",
    "射手座": "Sagittarius",
    "摩羯座": "Capricorn",
    "水瓶座": "Aquarius",
    "双鱼座": "Pisces"
}


def generate_daily_luck(zodiac_sign):
    # Generate luck based on zodiac sign
    zodiac_sign = ZODIAC_ALIASES.get(zodiac_sign, zodiac_sign)
    luck_data = {
        "Aries": {
            "summary": "Excellent study luck today - quick thinking, great for challenging material.",
            "details": "Your mind is sharp today with strong memory retention. Ideal for math, physics, and logical subjects. Don't overexert yourself - take breaks when needed.",
            "color": "Red",
            "number": "9",
            "advice": "Morning study sessions work best. Maintain a positive attitude!"
        },
        "Taurus": {
            "summary": "Steady study energy - perfect for methodical learning.",
            "details": "Your learning pace is consistent today. Great for reviewing and strengthening foundations. Your patience is your strength - detailed tasks suit you well.",
            "color": "Green",
            "number": "6",
            "advice": "Create a detailed study plan and work through it step by step."
        },
        "Gemini": {
            "summary": "Good study energy - curious mind ready for new knowledge.",
            "details": "Your curiosity is high and you're eager to learn. Languages, literature, and creative subjects appeal to you. Watch out for distraction - focus on one topic at a time.",
            "color": "Yellow",
            "number": "5",
            "advice": "Discuss with classmates and share insights for new perspectives."
        },
        "Cancer": {
            "summary": "Moderate study energy - emotions may affect efficiency.",
            "details": "Your mood might fluctuate today, affecting focus. Study topics you genuinely enjoy and keep your spirits high.",
            "color": "White",
            "number": "2",
            "advice": "Study in a quiet, comfortable environment free from distractions."
        },
        "Leo": {
            "summary": "Great study energy - confidence high, perfect for showcasing knowledge.",
            "details": "Your confidence is soaring and motivation is strong. Participate in presentations, debates, and activities that let you demonstrate your learning.",
            "color": "Gold",
            "number": "1",
            "advice": "Set challenging goals and unleash your potential."
        },
        "Virgo": {
            "summary": "Excellent study focus - attention to detail shines.",
            "details": "Your observation is sharp and you catch details others miss. Quality work is guaranteed. Perfect for precision tasks like coding and lab work.",
            "color": "Gray",
            "number": "8",
            "advice": "Maintain rigorous standards but remember to rest and avoid burnout."
        },
        "Libra": {
            "summary": "Balanced study energy - good for coordinating multiple subjects.",
            "details": "Your sense of balance helps you allocate time wisely across subjects. Maintain equilibrium between study and rest.",
            "color": "Blue",
            "number": "4",
            "advice": "Create a balanced schedule and avoid neglecting any subject."
        },
        "Scorpio": {
            "summary": "Strong study intensity - deep focus for immersive learning.",
            "details": "Your concentration is powerful today. Dive deep into topics that fascinate you. Learning efficiency is high - you'll grasp new concepts quickly.",
            "color": "Purple",
            "number": "7",
            "advice": "Choose one key topic and study it thoroughly - you'll make great progress."
        },
        "Sagittarius": {
            "summary": "Good study energy - intellectual curiosity for broad learning.",
            "details": "Your thirst for knowledge is unquenchable. Explore widely and expand your horizons across disciplines.",
            "color": "Orange",
            "number": "3",
            "advice": "Stay curious and experiment with new study methods."
        },
        "Capricorn": {
            "summary": "Stable study endurance - perfect for long-term tasks.",
            "details": "Your stamina is impressive today. Extended study sessions suit you. Your serious, persistent approach pays dividends.",
            "color": "Brown",
            "number": "10",
            "advice": "Set long-term goals and work toward them consistently."
        },
        "Aquarius": {
            "summary": "Good study energy - innovative thinking for creative learning.",
            "details": "Your innovative approach is active today. Try creative study activities. Your unique methods help you discover what works best for you.",
            "color": "Light Blue",
            "number": "11",
            "advice": "Try new techniques and let your creativity flow."
        },
        "Pisces": {
            "summary": "Moderate study energy - rich imagination for artistic subjects.",
            "details": "Your imagination flourishes today. Art, literature, and creative subjects appeal to you. Focus might waver - gentle adjustment helps.",
            "color": "Pink",
            "number": "12",
            "advice": "Study in a relaxed, joyful atmosphere and let your imagination soar."
        }
    }

    return luck_data.get(zodiac_sign, {
        "summary": "Steady study energy - follow your plan.",
        "details": "Your learning state is stable today. Stick to your schedule and maintain good habits for solid progress.",
        "color": "Gray",
        "number": "5",
        "advice": "Maintain regular study hours and focus on efficiency."
    })


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped


# Home page route
@app.route('/')
@login_required
def index():
    username = current_user()
    courses = filter_by_owner(load_data(COURSES_FILE), username)
    tasks = filter_by_owner(load_data(TASKS_FILE), username)
    grades = get_user_grades(load_data(GRADES_FILE), username)

    # Process today's recommended tasks
    today = date.today()
    recommended_tasks = get_recommended_tasks(tasks)

    # Statistics for today overview
    upcoming_tasks = [t for t in tasks if not t.get('completed') and
                     (datetime.strptime(t['due_date'], "%Y-%m-%d").date() - today).days <= 3]

    # Calculate average study time
    completed_tasks = [t for t in tasks if t.get('completed') and t.get('actual_time')]
    avg_study_time = sum([int(t['actual_time']) for t in completed_tasks]) / len(completed_tasks) if completed_tasks else 0

    # Calculate overall progress
    total_tasks = len(tasks)
    completed_count = len([t for t in tasks if t.get('completed')])
    overall_progress = (completed_count / total_tasks * 100) if total_tasks > 0 else 0

    # Generate daily luck
    daily_luck = {"summary": "Login to see your personalized study luck"}
    users = load_data(USERS_FILE)
    user = users.get(username)
    if user and user.get('zodiac_sign'):
        daily_luck = generate_daily_luck(user['zodiac_sign'])

    return render_template('index.html',
                          courses=courses,
                          tasks=tasks,
                          recommended_tasks=recommended_tasks,
                          upcoming_tasks=upcoming_tasks,
                          avg_study_time=round(avg_study_time, 1),
                          overall_progress=round(overall_progress, 1),
                          datetime=datetime,
                          session=session,
                          daily_luck=daily_luck)


# Get recommended tasks algorithm
def get_recommended_tasks(tasks):
    today = date.today()
    # Filter incomplete tasks
    incomplete_tasks = [t for t in tasks if not t.get('completed')]

    # Calculate recommendation score for each task (urgency*0.6 + priority*0.4)
    for task in incomplete_tasks:
        due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
        days_left = (due_date - today).days

        # Calculate urgency score (higher for closer deadlines)
        if days_left <= 0:
            urgency_score = 10
        elif days_left <= 3:
            urgency_score = 8
        elif days_left <= 7:
            urgency_score = 5
        else:
            urgency_score = 2

        # Priority score (1=highest=5 points, 5=lowest=1 point)
        priority_score = 6 - int(task['priority'])

        # Total recommendation score
        task['recommendation_score'] = (urgency_score * 0.6) + (priority_score * 0.4)

    # Sort by recommendation score
    sorted_tasks = sorted(incomplete_tasks, key=lambda x: x['recommendation_score'], reverse=True)

    # Return top 3 recommended tasks
    return sorted_tasks[:3]


# Courses management route
@app.route('/courses')
@login_required
def courses():
    username = current_user()
    courses = filter_by_owner(load_data(COURSES_FILE), username)
    tasks = filter_by_owner(load_data(TASKS_FILE), username)
    for course in courses:
        course_tasks = [t for t in tasks if t.get('course_id') == course['id']]
        if course_tasks:
            completed = len([t for t in course_tasks if t.get('completed')])
            course['progress'] = (completed / len(course_tasks)) * 100
            course['completed_tasks'] = completed
            course['total_tasks'] = len(course_tasks)
            course['tasks'] = course_tasks
        else:
            course['progress'] = 0
            course['completed_tasks'] = 0
            course['total_tasks'] = 0
            course['tasks'] = []
    return render_template('courses.html', courses=courses, tasks=tasks)


# Add course
@app.route('/add_course', methods=['POST'])
@login_required
def add_course():
    username = current_user()
    data = request.form
    courses = load_data(COURSES_FILE)

    new_course = {
        "id": get_next_id(courses),
        "owner": username,
        "name": data.get('course_name'),
        "professor": data.get('professor', ''),
        "credits": int(data.get('credits', 0))
    }

    courses.append(new_course)
    save_data(COURSES_FILE, courses)

    return redirect(url_for('courses'))


# Delete course
@app.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    username = current_user()
    # Delete course
    courses = load_data(COURSES_FILE)
    target_course = next((c for c in courses if c.get('id') == course_id), None)
    if not target_course or target_course.get('owner') != username:
        return redirect(url_for('courses'))

    courses = [c for c in courses if c['id'] != course_id]
    save_data(COURSES_FILE, courses)

    # Also delete associated tasks
    tasks = load_data(TASKS_FILE)
    tasks = [t for t in tasks if not (t.get('owner') == username and t.get('course_id') == course_id)]
    save_data(TASKS_FILE, tasks)

    return redirect(url_for('courses'))


# Tasks management route
@app.route('/tasks')
@login_required
def tasks():
    username = current_user()
    courses = filter_by_owner(load_data(COURSES_FILE), username)
    tasks = filter_by_owner(load_data(TASKS_FILE), username)

    # Sort by due date
    tasks_sorted = sorted(tasks, key=lambda x: (x['due_date'], -int(x['priority'])))

    # Categorize tasks
    today = date.today()
    upcoming = []
    later = []
    completed = []

    for task in tasks_sorted:
        if task.get('completed'):
            completed.append(task)
            continue

        due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
        days_left = (due_date - today).days

        if days_left <= 3:
            upcoming.append(task)
        else:
            later.append(task)

    return render_template('tasks.html',
                          courses=courses,
                          upcoming_tasks=upcoming,
                          later_tasks=later,
                          completed_tasks=completed)


# Add task
@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    username = current_user()
    data = request.form
    tasks = load_data(TASKS_FILE)
    today = date.today()

    course_id = int(data.get('course_id'))
    course = None
    course_name = 'Others'
    if course_id != 0:
        course = next(
            (c for c in load_data(COURSES_FILE) if c.get('id') == course_id and c.get('owner') == username),
            None
        )
        if not course:
            return redirect(url_for('tasks'))
        course_name = course.get('name', '')

    new_task = {
        "id": get_next_id(tasks),
        "owner": username,
        "name": data.get('task_name'),
        "course_id": course_id,
        "course_name": course_name,
        "task_type": data.get('task_type'),
        "due_date": data.get('due_date'),
        "estimated_time": data.get('estimated_time'),
        "priority": data.get('priority'),
        "description": data.get('description', ''),
        "completed": False,
        "actual_time": '',
        "created_at": str(today)
    }

    tasks.append(new_task)
    save_data(TASKS_FILE, tasks)

    return redirect(url_for('tasks'))


# Mark task complete
@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    username = current_user()
    data = request.form
    tasks = load_data(TASKS_FILE)

    for task in tasks:
        if task.get('id') == task_id and task.get('owner') == username:
            task['completed'] = True
            task['actual_time'] = data.get('actual_time', '')
            break

    save_data(TASKS_FILE, tasks)
    return redirect(url_for('tasks'))


# Delete task
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    username = current_user()
    tasks = load_data(TASKS_FILE)
    tasks = [t for t in tasks if not (t.get('id') == task_id and t.get('owner') == username)]
    save_data(TASKS_FILE, tasks)
    return redirect(url_for('tasks'))


# Zodiac sign calculation function
def get_zodiac_sign(month, day):
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Pisces"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    else:
        return "Capricorn"


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        birthday = request.form.get('birthday')

        # Load user data
        users = load_data(USERS_FILE)

        # Check if username exists
        if username in users:
            return render_template('register.html', error='Username already exists')

        # Calculate zodiac sign
        if birthday:
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
            zodiac_sign = get_zodiac_sign(birth_date.month, birth_date.day)
        else:
            zodiac_sign = "Unknown"

        # Add new user
        users[username] = {
            'password': generate_password_hash(password),
            'email': email,
            'birthday': birthday,
            'zodiac_sign': zodiac_sign
        }

        # Save user data
        save_data(USERS_FILE, users)

        # Auto login
        session['username'] = username
        return redirect(url_for('index'))

    return render_template('register.html')


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Load user data
        users = load_data(USERS_FILE)

        # Verify user
        if username in users:
            stored = users[username].get('password', '')
            if stored == password:
                users[username]['password'] = generate_password_hash(password)
                save_data(USERS_FILE, users)
                session['username'] = username
                return redirect(url_for('index'))
            if check_password_hash(stored, password):
                session['username'] = username
                return redirect(url_for('index'))
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    # Clear session
    session.pop('username', None)
    return redirect(url_for('index'))


# Daily luck detail page
@app.route('/luck')
@login_required
def luck():
    # Load user data
    username = current_user()
    users = load_data(USERS_FILE)
    user = users.get(username)

    if not user or not user.get('zodiac_sign'):
        return redirect(url_for('index'))

    # Generate daily luck
    daily_luck = generate_daily_luck(user['zodiac_sign'])

    return render_template('luck.html',
                          session=session,
                          user=user,
                          daily_luck=daily_luck,
                          datetime=datetime)


# Update grades
@app.route('/update_grade', methods=['POST'])
@login_required
def update_grade():
    username = current_user()
    data = request.form
    grades = load_data(GRADES_FILE)

    course_id = data.get('course_id')
    grade = data.get('grade')

    if course_id and grade:
        user_grades = grades.get(username, {}) if isinstance(grades, dict) else {}
        user_grades[course_id] = grade
        grades = grades if isinstance(grades, dict) else {}
        grades[username] = user_grades
        save_data(GRADES_FILE, grades)

    return redirect(url_for('stats'))


# Statistics page
@app.route('/stats')
@login_required
def stats():
    username = current_user()
    courses = filter_by_owner(load_data(COURSES_FILE), username)
    tasks = filter_by_owner(load_data(TASKS_FILE), username)
    grades = get_user_grades(load_data(GRADES_FILE), username)

    # Calculate GPA
    gpa_data = calculate_gpa(grades, courses)

    # Study time statistics
    time_stats = get_time_statistics(tasks)

    # Task completion rate
    completion_stats = get_completion_stats(tasks, courses)

    return render_template('stats.html',
                          courses=courses,
                          tasks=tasks,
                          grades=grades,
                          gpa_data=gpa_data,
                          time_stats=time_stats,
                          completion_stats=completion_stats)


# GPA calculation function
def calculate_gpa(grades, courses):
    total_credits = 0
    total_grade_points = 0

    for course_id, grade in grades.items():
        course = next((c for c in courses if str(c['id']) == course_id), None)
        if course and grade:
            credits = course['credits']
            # Convert grade to grade points (A=4, B=3, C=2, D=1, F=0)
            grade_point = {'A':4, 'B':3, 'C':2, 'D':1, 'F':0}.get(grade, 0)
            total_credits += credits
            total_grade_points += credits * grade_point

    current_gpa = total_grade_points / total_credits if total_credits > 0 else 0

    # Calculate predicted GPA
    remaining_credits = sum([c['credits'] for c in courses if str(c['id']) not in grades])
    predicted_gpa = current_gpa

    return {
        "current_gpa": round(current_gpa, 2),
        "predicted_gpa": round(predicted_gpa, 2),
        "total_credits": total_credits,
        "remaining_credits": remaining_credits
    }


# Time statistics function
def get_time_statistics(tasks):
    completed_tasks = [t for t in tasks if t.get('completed')]

    # Calculate by course
    course_time = {}
    for task in completed_tasks:
        if not task.get('actual_time'):
            continue
        course_name = task.get('course_name', 'Unknown')
        time = int(task['actual_time'])
        if course_name in course_time:
            course_time[course_name] += time
        else:
            course_time[course_name] = time

    # Calculate by week day
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    week_time = {day:0 for day in week_days}

    # Simple simulation
    for i, task in enumerate(completed_tasks):
        day = week_days[i % 7]
        week_time[day] += int(task['actual_time']) if task.get('actual_time') else 0

    return {
        "course_time": course_time,
        "week_time": week_time,
        "total_time": sum(course_time.values())
    }


# Task completion rate statistics
def get_completion_stats(tasks, courses):
    stats = []
    for course in courses:
        course_tasks = [t for t in tasks if t.get('course_id') == course['id']]
        if course_tasks:
            completed = len([t for t in course_tasks if t.get('completed')])
            total = len(course_tasks)
            stats.append({
                "course_name": course['name'],
                "completed": completed,
                "total": total,
                "rate": (completed / total) * 100
            })
    return stats


# Main function
if __name__ == '__main__':
    init_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
