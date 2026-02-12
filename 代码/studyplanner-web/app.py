from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime, date

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 用于session管理

# 数据文件路径
DATA_DIR = "data"
COURSES_FILE = os.path.join(DATA_DIR, "courses.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
GRADES_FILE = os.path.join(DATA_DIR, "grades.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# 初始化数据文件夹和文件
def init_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # 初始化课程文件
    if not os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # 初始化任务文件
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # 初始化成绩文件
    if not os.path.exists(GRADES_FILE):
        with open(GRADES_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    
    # 初始化用户文件
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

# 加载数据
def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 根据文件名返回正确的类型
        if "grades.json" in file_path:
            return {}
        return [] if "json" in file_path else {}

# 保存数据
def save_data(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False

# 生成每日学习运势
def generate_daily_luck(zodiac_sign):
    # 根据星座生成运势
    luck_data = {
        "白羊座": {
            "summary": "今日学习运势极佳，思维敏捷，适合挑战高难度内容。",
            "details": "今天你的学习状态非常好，大脑运转迅速，记忆力强。适合安排数学、物理等需要逻辑思维的课程。注意不要过度疲劳，适当休息。",
            "color": "红色",
            "number": "9",
            "advice": "建议早晨学习效果最佳，保持积极的学习态度。"
        },
        "金牛座": {
            "summary": "今日学习运势平稳，适合按部就班地学习。",
            "details": "今天你的学习状态稳定，适合复习旧知识，巩固基础。耐心是你的优势，适合进行需要细致的学习任务。",
            "color": "绿色",
            "number": "6",
            "advice": "建议制定详细的学习计划，一步一步完成目标。"
        },
        "双子座": {
            "summary": "今日学习运势不错，好奇心强，适合探索新知识。",
            "details": "今天你的好奇心旺盛，学习兴趣浓厚。适合学习语言、文学等需要创造力的课程。注意不要分散注意力，专注于一个主题。",
            "color": "黄色",
            "number": "5",
            "advice": "建议多与同学交流，分享学习心得，会有新的收获。"
        },
        "巨蟹座": {
            "summary": "今日学习运势一般，情绪可能会影响学习效率。",
            "details": "今天你的情绪可能会有些波动，影响学习状态。适合学习自己感兴趣的内容，保持心情愉悦。",
            "color": "白色",
            "number": "2",
            "advice": "建议在安静舒适的环境中学习，避免外界干扰。"
        },
        "狮子座": {
            "summary": "今日学习运势良好，自信心强，适合展示自己的知识。",
            "details": "今天你的自信心爆棚，学习积极性高。适合参加演讲、辩论等活动，展示自己的学习成果。",
            "color": "金色",
            "number": "1",
            "advice": "建议设定挑战性的学习目标，充分发挥自己的潜力。"
        },
        "处女座": {
            "summary": "今日学习运势优秀，注重细节，适合精细的学习任务。",
            "details": "今天你的观察力敏锐，注重细节，学习质量高。适合进行需要细心的学习任务，如编程、实验等。",
            "color": "灰色",
            "number": "8",
            "advice": "建议保持严谨的学习态度，注意休息，避免过度劳累。"
        },
        "天秤座": {
            "summary": "今日学习运势平稳，平衡感好，适合协调各科学习。",
            "details": "今天你的平衡感不错，适合合理安排各科学习时间。注重学习与休息的平衡，保持良好的学习状态。",
            "color": "蓝色",
            "number": "4",
            "advice": "建议制定均衡的学习计划，不要偏科。"
        },
        "天蝎座": {
            "summary": "今日学习运势较强，专注力高，适合深入学习。",
            "details": "今天你的专注力非常高，适合深入研究某个主题。学习效率高，能够快速掌握新知识。",
            "color": "紫色",
            "number": "7",
            "advice": "建议选择一个重点内容深入学习，会有很大收获。"
        },
        "射手座": {
            "summary": "今日学习运势不错，求知欲强，适合广泛学习。",
            "details": "今天你的求知欲旺盛，对各种知识都感兴趣。适合博览群书，拓宽知识面。",
            "color": "橙色",
            "number": "3",
            "advice": "建议保持好奇心，多尝试新的学习方法。"
        },
        "摩羯座": {
            "summary": "今日学习运势稳定，耐力强，适合长期学习任务。",
            "details": "今天你的耐力很好，适合进行需要长期坚持的学习任务。学习态度认真，能够持之以恒。",
            "color": "棕色",
            "number": "10",
            "advice": "建议设定长期学习目标，一步一步实现。"
        },
        "水瓶座": {
            "summary": "今日学习运势良好，创新思维活跃，适合创造性学习。",
            "details": "今天你的创新思维活跃，适合进行创造性的学习活动。学习方法独特，能够找到适合自己的学习方式。",
            "color": "浅蓝色",
            "number": "11",
            "advice": "建议尝试新的学习方法，发挥自己的创造力。"
        },
        "双鱼座": {
            "summary": "今日学习运势一般，想象力丰富，适合艺术相关学习。",
            "details": "今天你的想象力丰富，适合学习艺术、文学等需要创造力的课程。学习状态可能会有些波动，需要调整。",
            "color": "粉色",
            "number": "12",
            "advice": "建议在轻松愉快的环境中学习，发挥自己的想象力。"
        }
    }
    
    return luck_data.get(zodiac_sign, {
        "summary": "今日学习运势平稳，适合按计划学习。",
        "details": "今天你的学习状态稳定，适合按计划完成学习任务。保持良好的学习习惯，会有不错的收获。",
        "color": "灰色",
        "number": "5",
        "advice": "建议保持规律的学习时间，注重学习效率。"
    })

# 主页路由
@app.route('/')
def index():
    # 加载数据
    courses = load_data(COURSES_FILE)
    tasks = load_data(TASKS_FILE)
    grades = load_data(GRADES_FILE)
    
    # 处理今日推荐任务
    today = date.today()
    recommended_tasks = get_recommended_tasks(tasks)
    
    # 统计今日概览
    upcoming_tasks = [t for t in tasks if not t.get('completed') and 
                     (datetime.strptime(t['due_date'], "%Y-%m-%d").date() - today).days <= 3]
    
    # 计算平均学习时间
    completed_tasks = [t for t in tasks if t.get('completed') and t.get('actual_time')]
    avg_study_time = sum([int(t['actual_time']) for t in completed_tasks]) / len(completed_tasks) if completed_tasks else 0
    
    # 计算整体进度
    total_tasks = len(tasks)
    completed_count = len([t for t in tasks if t.get('completed')])
    overall_progress = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
    
    # 生成每日运势
    daily_luck = {"summary": "登录后查看你的专属学习运势"}
    if 'username' in session:
        users = load_data(USERS_FILE)
        user = users.get(session['username'])
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

# 获取推荐任务算法
def get_recommended_tasks(tasks):
    today = date.today()
    # 过滤未完成任务
    incomplete_tasks = [t for t in tasks if not t.get('completed')]
    
    # 计算每个任务的推荐分数 (截止日期紧迫性*0.6 + 优先级*0.4)
    for task in incomplete_tasks:
        due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
        days_left = (due_date - today).days
        
        # 计算紧迫性分数 (越近分数越高)
        if days_left <= 0:
            urgency_score = 10
        elif days_left <= 3:
            urgency_score = 8
        elif days_left <= 7:
            urgency_score = 5
        else:
            urgency_score = 2
        
        # 优先级分数 (1最高=5分，5最低=1分)
        priority_score = 6 - int(task['priority'])
        
        # 总推荐分数
        task['recommendation_score'] = (urgency_score * 0.6) + (priority_score * 0.4)
    
    # 按推荐分数排序
    sorted_tasks = sorted(incomplete_tasks, key=lambda x: x['recommendation_score'], reverse=True)
    
    # 返回前3个推荐任务
    return sorted_tasks[:3]

# 课程管理路由
@app.route('/courses')
def courses():
    courses = load_data(COURSES_FILE)
    tasks = load_data(TASKS_FILE)
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

# 添加课程
@app.route('/add_course', methods=['POST'])
def add_course():
    data = request.form
    courses = load_data(COURSES_FILE)
    
    new_course = {
        "id": len(courses) + 1,
        "name": data.get('course_name'),
        "professor": data.get('professor', ''),
        "credits": int(data.get('credits', 0))
    }
    
    courses.append(new_course)
    save_data(COURSES_FILE, courses)
    
    return redirect(url_for('courses'))

# 删除课程
@app.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    # 删除课程
    courses = load_data(COURSES_FILE)
    courses = [c for c in courses if c['id'] != course_id]
    save_data(COURSES_FILE, courses)
    
    # 同时删除关联的任务
    tasks = load_data(TASKS_FILE)
    tasks = [t for t in tasks if t.get('course_id') != course_id]
    save_data(TASKS_FILE, tasks)
    
    return redirect(url_for('courses'))

# 任务管理路由
@app.route('/tasks')
def tasks():
    courses = load_data(COURSES_FILE)
    tasks = load_data(TASKS_FILE)
    
    # 按截止日期排序
    tasks_sorted = sorted(tasks, key=lambda x: (x['due_date'], -int(x['priority'])))
    
    # 分类任务
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

# 添加任务
# 添加任务
@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.form
    tasks = load_data(TASKS_FILE)
    # 修复：定义today变量（关键！）
    today = date.today()
    
    new_task = {
        "id": len(tasks) + 1,
        "name": data.get('task_name'),
        "course_id": int(data.get('course_id')),
        "course_name": next((c['name'] for c in load_data(COURSES_FILE) if c['id'] == int(data.get('course_id'))), ''),
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

# 标记任务完成
@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    data = request.form
    tasks = load_data(TASKS_FILE)
    
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = True
            task['actual_time'] = data.get('actual_time', '')
            break
    
    save_data(TASKS_FILE, tasks)
    return redirect(url_for('tasks'))

# 删除任务
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    tasks = load_data(TASKS_FILE)
    tasks = [t for t in tasks if t['id'] != task_id]
    save_data(TASKS_FILE, tasks)
    return redirect(url_for('tasks'))

# 星座计算函数
def get_zodiac_sign(month, day):
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "水瓶座"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "双鱼座"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "白羊座"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "金牛座"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "双子座"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "巨蟹座"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "狮子座"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "处女座"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "天秤座"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "天蝎座"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "射手座"
    else:
        return "摩羯座"

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        birthday = request.form.get('birthday')
        
        # 加载用户数据
        users = load_data(USERS_FILE)
        
        # 检查用户名是否已存在
        if username in users:
            return render_template('register.html', error='用户名已存在')
        
        # 计算星座
        if birthday:
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
            zodiac_sign = get_zodiac_sign(birth_date.month, birth_date.day)
        else:
            zodiac_sign = "未知"
        
        # 添加新用户
        users[username] = {
            'password': password,  # 实际应用中应该加密密码
            'email': email,
            'birthday': birthday,
            'zodiac_sign': zodiac_sign
        }
        
        # 保存用户数据
        save_data(USERS_FILE, users)
        
        # 自动登录
        session['username'] = username
        return redirect(url_for('index'))
    
    return render_template('register.html')

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 加载用户数据
        users = load_data(USERS_FILE)
        
        # 验证用户
        if username in users and users[username]['password'] == password:
            # 登录成功，设置session
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    # 清除session
    session.pop('username', None)
    return redirect(url_for('index'))

# 今日运势详细页面
@app.route('/luck')
def luck():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # 加载用户数据
    users = load_data(USERS_FILE)
    user = users.get(session['username'])
    
    if not user or not user.get('zodiac_sign'):
        return redirect(url_for('index'))
    
    # 生成每日运势
    daily_luck = generate_daily_luck(user['zodiac_sign'])
    
    return render_template('luck.html',
                          session=session,
                          user=user,
                          daily_luck=daily_luck,
                          datetime=datetime)

# 更新成绩
@app.route('/update_grade', methods=['POST'])
def update_grade():
    data = request.form
    grades = load_data(GRADES_FILE)
    
    course_id = data.get('course_id')
    grade = data.get('grade')
    
    if course_id and grade:
        grades[course_id] = grade
        save_data(GRADES_FILE, grades)
    
    return redirect(url_for('stats'))

# 统计分析页面
@app.route('/stats')
def stats():
    courses = load_data(COURSES_FILE)
    tasks = load_data(TASKS_FILE)
    grades = load_data(GRADES_FILE)
    
    # 计算GPA
    gpa_data = calculate_gpa(grades, courses)
    
    # 学习时间统计
    time_stats = get_time_statistics(tasks)
    
    # 任务完成率
    completion_stats = get_completion_stats(tasks, courses)
    
    return render_template('stats.html',
                          courses=courses,
                          tasks=tasks,
                          grades=grades,
                          gpa_data=gpa_data,
                          time_stats=time_stats,
                          completion_stats=completion_stats)

# GPA计算函数
def calculate_gpa(grades, courses):
    total_credits = 0
    total_grade_points = 0
    
    for course_id, grade in grades.items():
        course = next((c for c in courses if str(c['id']) == course_id), None)
        if course and grade:
            credits = course['credits']
            # 转换成绩为绩点 (A=4, B=3, C=2, D=1, F=0)
            grade_point = {'A':4, 'B':3, 'C':2, 'D':1, 'F':0}.get(grade, 0)
            total_credits += credits
            total_grade_points += credits * grade_point
    
    current_gpa = total_grade_points / total_credits if total_credits > 0 else 0
    
    # 预测最终GPA (假设未完成任务都拿B)
    incomplete_courses = [c for c in courses if str(c['id']) not in grades]
    predicted_credits = total_credits + sum([c['credits'] for c in incomplete_courses])
    predicted_points = total_grade_points + sum([c['credits'] * 3 for c in incomplete_courses])
    predicted_gpa = predicted_points / predicted_credits if predicted_credits > 0 else 0
    
    return {
        "current": round(current_gpa, 2),
        "predicted": round(predicted_gpa, 2),
        "total_credits": total_credits
    }

# 学习时间统计
def get_time_statistics(tasks):
    # 按课程统计
    course_time = {}
    completed_tasks = [t for t in tasks if t.get('completed') and t.get('actual_time')]
    
    for task in completed_tasks:
        course_name = task['course_name']
        time = int(task['actual_time'])
        if course_name in course_time:
            course_time[course_name] += time
        else:
            course_time[course_name] = time
    
    # 按星期统计
    week_days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    week_time = {day:0 for day in week_days}
    
    # 简单模拟（实际可根据任务完成时间统计）
    for i, task in enumerate(completed_tasks):
        day = week_days[i % 7]
        week_time[day] += int(task['actual_time']) if task.get('actual_time') else 0
    
    return {
        "course_time": course_time,
        "week_time": week_time,
        "total_time": sum(course_time.values())
    }

# 任务完成率统计
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

# 主函数
if __name__ == '__main__':
    init_data()
    app.run(debug=True, host='0.0.0.0', port=5000)