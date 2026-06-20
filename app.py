from flask import Flask, render_template, session, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'skillsdev_secret_key'

# ── DATABASE CONNECTION ────────────────────────────────────────────────────────
IS_LOCAL = True

if IS_LOCAL:
    DB_CONFIG = {
        'host'    : 'localhost',
        'user'    : 'root',
        'password': '',
        'database': 'skillsdevelopmentdb'
    }
else:
    DB_CONFIG = {
        'host'    : 'yourusername.mysql.pythonanywhere-services.com',
        'user'    : 'yourusername',
        'password': 'pythonanywhere_db_password',
        'database': 'yourusername$skillsdevelopmentdb'
    }

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ── HELPER FUNCTION ────────────────────────────────────────────────────────────
def get_skill_level(pts):
    if pts >= 90:   return "Expert"
    elif pts >= 70: return "Advanced"
    elif pts >= 40: return "Intermediate"
    elif pts > 0:   return "Beginner"
    else:           return "Not started"

# ── SAMPLE DATA ────────────────────────────────────────────────────────────────
SAMPLE_SKILLS = [
    {'SkillName': 'Microsoft Excel',     'TotalPoints': 82},
    {'SkillName': 'Python Programming',  'TotalPoints': 95},
    {'SkillName': 'Communication',       'TotalPoints': 45},
    {'SkillName': 'Business Management', 'TotalPoints': 30},
]

SAMPLE_COURSES = [
    {
        'CourseID':     1,
        'CourseName':   'Excel Fundamentals',
        'SkillName':    'Microsoft Excel',
        'Duration':     45,
        'Description':  'Learn the basics of Excel including formulas, charts and data management.',
        'SkillCredits': 10,
        'attempts':     0
    },
    {
        'CourseID':     2,
        'CourseName':   'Advanced Excel Formulas',
        'SkillName':    'Microsoft Excel',
        'Duration':     60,
        'Description':  'Master VLOOKUP, INDEX MATCH, pivot tables and data analysis.',
        'SkillCredits': 15,
        'attempts':     1
    },
    {
        'CourseID':     3,
        'CourseName':   'Python for Beginners',
        'SkillName':    'Python Programming',
        'Duration':     60,
        'Description':  'Learn Python basics including variables, loops and functions.',
        'SkillCredits': 12,
        'attempts':     0
    },
    {
        'CourseID':     4,
        'CourseName':   'Python for Data Analysis',
        'SkillName':    'Python Programming',
        'Duration':     90,
        'Description':  'Use Python and Pandas to analyse and visualise real world data.',
        'SkillCredits': 20,
        'attempts':     2
    },
    {
        'CourseID':     5,
        'CourseName':   'Workplace Communication',
        'SkillName':    'Communication',
        'Duration':     30,
        'Description':  'Build professional communication skills for the modern workplace.',
        'SkillCredits': 10,
        'attempts':     3
    },
    {
        'CourseID':     6,
        'CourseName':   'Business Management Basics',
        'SkillName':    'Business Management',
        'Duration':     45,
        'Description':  'Understand key business management principles and strategies.',
        'SkillCredits': 12,
        'attempts':     0
    },
]

SAMPLE_RECENT = [
    {'CourseID': 1, 'CourseName': 'Excel Fundamentals',       'Status': 'Pass'},
    {'CourseID': 3, 'CourseName': 'Python for Beginners',     'Status': 'Pass'},
    {'CourseID': 4, 'CourseName': 'Python for Data Analysis', 'Status': 'Fail'},
]

SAMPLE_CERTS = [
    {'CourseName': 'Excel Fundamentals',   'IssueDate': '2026-03-15'},
    {'CourseName': 'Python for Beginners', 'IssueDate': '2026-04-02'},
]

SAMPLE_LEARNERS = [
    {'Username': 'Dominique Minaar', 'skills': 'Python: 95 pts | Excel: 82 pts',               'total': 177},
    {'Username': 'Khanyi Mahlangu',  'skills': 'Excel: 90 pts | Communication: 88 pts',        'total': 178},
    {'Username': 'Nkulueko Masina',  'skills': 'Python: 88 pts | Business Management: 75 pts', 'total': 163},
    {'Username': 'Flavi Munganga',   'skills': 'Python: 70 pts | Communication: 60 pts',       'total': 130},
]

SAMPLE_QUESTIONS = [
    {
        'QuestionID':    1,
        'QuestionText':  'What does the SUM function do in Excel?',
        'OptionA':       'Adds all numbers in a range',
        'OptionB':       'Multiplies numbers together',
        'OptionC':       'Counts cells with text',
        'OptionD':       'Divides numbers',
        'CorrectAnswer': 'A'
    },
    {
        'QuestionID':    2,
        'QuestionText':  'Which symbol starts a formula in Excel?',
        'OptionA':       '#',
        'OptionB':       '@',
        'OptionC':       '=',
        'OptionD':       '$',
        'CorrectAnswer': 'C'
    },
    {
        'QuestionID':    3,
        'QuestionText':  'What is a cell reference?',
        'OptionA':       'A colour code',
        'OptionB':       'A column and row identifier like A1',
        'OptionC':       'A formula name',
        'OptionD':       'A chart type',
        'CorrectAnswer': 'B'
    },
    {
        'QuestionID':    4,
        'QuestionText':  'What does the AVERAGE function do?',
        'OptionA':       'Finds the highest value',
        'OptionB':       'Adds numbers together',
        'OptionC':       'Calculates the mean of a range',
        'OptionD':       'Counts numbers in a range',
        'CorrectAnswer': 'C'
    },
    {
        'QuestionID':    5,
        'QuestionText':  'What is a pivot table used for?',
        'OptionA':       'Drawing charts',
        'OptionB':       'Summarising and analysing large sets of data',
        'OptionC':       'Formatting cells',
        'OptionD':       'Adding formulas to a spreadsheet',
        'CorrectAnswer': 'B'
    },
]

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

# ── LOGIN ─────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn   = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                'SELECT * FROM users WHERE Username = %s AND Password = %s',
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['user']    = user
                session['user_id'] = user['UserID']
                session['role']    = user['Role']
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect username or password.', 'error')

        except Exception as e:
            flash(f'Database error: {str(e)}', 'error')

    return render_template('login.html')

# ── REGISTER ──────────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']
        phone    = request.form.get('phone', '')

        try:
            conn   = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                'SELECT * FROM users WHERE Username = %s OR Email = %s',
                (username, email)
            )
            if cursor.fetchone():
                flash('Username or email already registered.', 'error')
            else:
                cursor.execute(
                    '''INSERT INTO users (Username, Email, Password, PhoneNumber, Role)
                       VALUES (%s, %s, %s, %s, %s)''',
                    (username, email, password, phone, 'Student')
                )
                conn.commit()
                flash('Account created successfully! Please log in.', 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('login'))
            cursor.close()
            conn.close()

        except Exception as e:
            flash(f'Database error: {str(e)}', 'error')

    return render_template('register.html')

# ── LOGOUT ────────────────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = session.get('user', {'Username': session.get('username', 'User')})
    return render_template('dashboard.html',
        skill_scores    = SAMPLE_SKILLS,
        recent          = SAMPLE_RECENT,
        courses         = SAMPLE_COURSES,
        total_pts       = 252,
        courses_done    = 4,
        skills_unlocked = 3,
        get_skill_level = get_skill_level,
        users           = user)

# ── COURSE LIBRARY ────────────────────────────────────────────────────────────
@app.route('/courses')
def courses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('course_library.html',
        courses = SAMPLE_COURSES)

# ── COURSE DETAIL ─────────────────────────────────────────────────────────────
@app.route('/course_detail/<int:course_Id>')
def course_detail(course_Id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    course   = next((c for c in SAMPLE_COURSES if c['CourseID'] == course_Id), SAMPLE_COURSES[0])
    attempts = course.get('attempts', 0)
    return render_template('course_detail.html',
        course   = course,
        attempts = attempts)

# ── START COURSE ──────────────────────────────────────────────────────────────
@app.route('/start_course/<int:course_id>')
def start_course(course_id=1):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    course = next((c for c in SAMPLE_COURSES if c['CourseID'] == course_id), SAMPLE_COURSES[0])
    return render_template('assessment.html',
        course    = course,
        questions = SAMPLE_QUESTIONS)

# ── ASSESSMENT ────────────────────────────────────────────────────────────────
@app.route('/assessment/<int:course_id>')
def assessment(course_id=1):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    course = next((c for c in SAMPLE_COURSES if c['CourseID'] == course_id), SAMPLE_COURSES[0])
    return render_template('assessment.html',
        course    = course,
        questions = SAMPLE_QUESTIONS)

# ── SUBMIT ASSESSMENT ─────────────────────────────────────────────────────────
@app.route('/submit_assessment/<int:course_id>', methods=['POST'])
def submit_assessment(course_id=1):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    course  = next((c for c in SAMPLE_COURSES if c['CourseID'] == course_id), SAMPLE_COURSES[0])
    score   = 85
    credits = 8
    return render_template('result.html',
        course  = course,
        score   = score,
        credits = credits)

# ── RESULT ────────────────────────────────────────────────────────────────────
@app.route('/result')
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    course = {'CourseName': 'Excel Fundamentals', 'SkillName': 'Microsoft Excel'}
    return render_template('result.html',
        course  = course,
        score   = 85,
        credits = 8)

# ── PROFILE ───────────────────────────────────────────────────────────────────
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = session.get('user', {'Username': session.get('username', 'User')})
    return render_template('profile.html',
        user            = user,
        skills          = SAMPLE_SKILLS,
        certs           = SAMPLE_CERTS,
        total_pts       = 252,
        get_skill_level = get_skill_level)

# ── TALENT HUB ────────────────────────────────────────────────────────────────
@app.route('/talent')
def talent():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('talent.html',
        learners = SAMPLE_LEARNERS)

# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
