from flask import Flask, render_template, session, request, redirect, url_for, flash
from init_db import get_db, init_db
from datetime import date

app = Flask(__name__)
app.secret_key = 'skillsdev_secret_key'



# ── HELPER FUNCTION ───────────────────────────────────────────────────────────

def get_skill_level(pts):
    if pts >= 90:   return "Expert"
    elif pts >= 70: return "Advanced"
    elif pts >= 40: return "Intermediate"
    elif pts > 0:   return "Beginner"
    else:           return "Not started"

app.jinja_env.globals['get_skill_level'] = get_skill_level



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
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE Username = ? AND Password = ?',
                (username, password)
            )
            user = cursor.fetchone()
            conn.close()

            if user:
                session['user_id']  = user['UserID']
                session['username'] = user['Username']
                session['role']     = user['Role']
                session['user']     = dict(user)
                if user['Role'] == 'Company':
                    return redirect(url_for('talent'))
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
        role     = request.form.get('role', 'Student')

        try:
            conn   = get_db()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT UserID FROM users WHERE Username = ? OR Email = ?',
                (username, email)
            )
            if cursor.fetchone():
                flash('Username or email already registered.', 'error')
                conn.close()
            else:
                cursor.execute(
                    '''INSERT INTO users (Username, Email, Password, PhoneNumber, Role)
                       VALUES (?, ?, ?, ?, ?)''',
                    (username, email, password, phone, role)
                )
                conn.commit()
                conn.close()
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('login'))

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

    user_id         = session['user_id']
    courses         = []
    recent          = []
    skill_scores    = []
    total_pts       = 0
    courses_done    = 0
    skills_unlocked = 0

    try:
        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.CourseID, c.CourseName, c.Duration, c.Description,
                   c.SkillCredits, s.SkillName,
                   COUNT(e.EnrollmentID) AS attempts
            FROM courses c
            LEFT JOIN skills      s ON s.CourseID = c.CourseID
            LEFT JOIN enrollments e ON e.CourseID = c.CourseID
                                    AND e.UserID  = ?
            GROUP BY c.CourseID
        ''', (user_id,))
        courses = [dict(row) for row in cursor.fetchall()]

        cursor.execute('''
            SELECT c.CourseID, c.CourseName, e.Status
            FROM enrollments e
            JOIN courses c ON e.CourseID = c.CourseID
            WHERE e.UserID = ?
            ORDER BY e.EnrollmentDate DESC
            LIMIT 5
        ''', (user_id,))
        recent = [dict(row) for row in cursor.fetchall()]

        cursor.execute('''
            SELECT s.SkillCategory AS SkillName,
                   SUM(us.TotalPoints) AS TotalPoints
            FROM user_skills us
            JOIN skills s ON us.SkillID = s.SkillID
            WHERE us.UserID = ?
            GROUP BY s.SkillCategory
            ORDER BY TotalPoints DESC
        ''', (user_id,))
        skill_scores = [dict(row) for row in cursor.fetchall()]

        cursor.execute(
            'SELECT COALESCE(SUM(TotalPoints), 0) AS total FROM user_skills WHERE UserID = ?',
            (user_id,)
        )
        total_pts = cursor.fetchone()['total']

        cursor.execute(
            'SELECT COUNT(*) AS total FROM enrollments WHERE UserID = ? AND Status = "Pass"',
            (user_id,)
        )
        courses_done = cursor.fetchone()['total']

        cursor.execute('''
            SELECT COUNT(DISTINCT s.SkillCategory) AS total
            FROM user_skills us
            JOIN skills s ON us.SkillID = s.SkillID
            WHERE us.UserID = ? AND us.TotalPoints > 0
        ''', (user_id,))
        skills_unlocked = cursor.fetchone()['total']

        conn.close()

    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')

    return render_template('dashboard.html',
        users           = session['user'],
        recent          = recent,
        courses         = courses,
        skill_scores    = skill_scores,
        total_pts       = total_pts,
        courses_done    = courses_done,
        skills_unlocked = skills_unlocked,
        get_skill_level = get_skill_level)

# ── COURSE LIBRARY ────────────────────────────────────────────────────────────
@app.route('/courses')
def courses():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    courses = []
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.CourseID, c.CourseName, c.Duration, c.Description,
                   c.SkillCredits, s.SkillName,
                   COUNT(e.EnrollmentID) AS attempts
            FROM courses c
            LEFT JOIN skills      s ON s.CourseID = c.CourseID
            LEFT JOIN enrollments e ON e.CourseID = c.CourseID
                                    AND e.UserID  = ?
            GROUP BY c.CourseID
        ''', (session['user_id'],))
        courses = [dict(row) for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')

    return render_template('course_library.html', courses=courses)

# ── COURSE DETAIL ─────────────────────────────────────────────────────────────
@app.route('/course_detail/<int:course_Id>')
def course_detail(course_Id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    course   = None
    attempts = 0
    try:
        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.CourseID, c.CourseName, c.Duration,
                   c.Description, c.SkillCredits, s.SkillName
            FROM courses c
            LEFT JOIN skills s ON s.CourseID = c.CourseID
            WHERE c.CourseID = ?
        ''', (course_Id,))
        row = cursor.fetchone()
        if row:
            course = dict(row)

        cursor.execute(
            'SELECT COUNT(*) AS attempts FROM enrollments WHERE UserID = ? AND CourseID = ?',
            (session['user_id'], course_Id)
        )
        attempts = cursor.fetchone()['attempts']
        conn.close()

    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('courses'))

    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('courses'))

    return render_template('course_detail.html',
        course   = course,
        attempts = attempts)

# ── START COURSE ──────────────────────────────────────────────────────────────
@app.route('/start_course/<int:course_id>')
def start_course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    course    = None
    materials = []
    try:
        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.CourseID, c.CourseName, c.Duration,
                   c.Description, c.SkillCredits, s.SkillName
            FROM courses c
            LEFT JOIN skills s ON s.CourseID = c.CourseID
            WHERE c.CourseID = ?
        ''', (course_id,))
        row = cursor.fetchone()
        if row:
            course = dict(row)

        cursor.execute('''
            SELECT MaterialTitle, MaterialType, SourcePlatform,
                   MaterialURL, Description, DifficultyLevel
            FROM learning_materials
            WHERE CourseID = ?
        ''', (course_id,))
        materials = [dict(row) for row in cursor.fetchall()]
        conn.close()

    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('courses'))

    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('courses'))

    return render_template('course_content.html',
        course    = course,
        materials = materials)

# ── ASSESSMENT ────────────────────────────────────────────────────────────────
@app.route('/assessment/<int:course_id>')
def assessment(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    course    = None
    questions = []
    try:
        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.CourseID, c.CourseName, c.Duration, c.Description,
                   c.SkillCredits, s.SkillName, s.SkillID,
                   a.AssessmentID, a.AssessmentName, a.PassMark
            FROM courses c
            LEFT JOIN skills      s ON s.CourseID = c.CourseID
            LEFT JOIN assessments a ON a.CourseID = c.CourseID
            WHERE c.CourseID = ?
        ''', (course_id,))
        row = cursor.fetchone()
        if row:
            course = dict(row)

        if course and course['AssessmentID']:
            cursor.execute('''
                SELECT QuestionID, QuestionText,
                       OptionA, OptionB, OptionC, OptionD
                FROM questions
                WHERE AssessmentID = ?
                ORDER BY QuestionID
            ''', (course['AssessmentID'],))
            questions = [dict(row) for row in cursor.fetchall()]

        conn.close()

    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('courses'))

    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('courses'))

    if not questions:
        flash('No questions available for this course yet.', 'error')
        return redirect(url_for('course_detail', course_Id=course_id))

    return render_template('assessment.html',
        course    = course,
        questions = questions)

# ── SUBMIT ASSESSMENT ─────────────────────────────────────────────────────────
@app.route('/submit_assessment/<int:course_id>', methods=['POST'])
def submit_assessment(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    course  = None
    score   = 0
    credits = 0

    try:
        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.CourseID, c.CourseName, c.Duration, c.Description,
                   c.SkillCredits, s.SkillName, s.SkillID,
                   a.AssessmentID, a.PassMark
            FROM courses c
            LEFT JOIN skills      s ON s.CourseID = c.CourseID
            LEFT JOIN assessments a ON a.CourseID = c.CourseID
            WHERE c.CourseID = ?
        ''', (course_id,))
        row = cursor.fetchone()
        if row:
            course = dict(row)

        if course and course['AssessmentID']:
            cursor.execute(
                'SELECT QuestionID, CorrectAnswer FROM questions WHERE AssessmentID = ?',
                (course['AssessmentID'],)
            )
            questions = cursor.fetchall()

            correct = sum(
                1 for q in questions
                if request.form.get(f"q{q['QuestionID']}") == q['CorrectAnswer']
            )
            total = len(questions)
            score = round((correct / total) * 100) if total else 0

            if score >= 90:
                credits = course['SkillCredits']
            elif score >= 70:
                credits = int(course['SkillCredits'] * 0.75)
            elif score >= 50:
                credits = int(course['SkillCredits'] * 0.50)
            else:
                credits = 0

            pass_status = 'Pass' if score >= 50 else 'Fail'

            # Save result
            cursor.execute('''
                INSERT INTO results (UserID, AssessmentID, Score, PassStatus, DateCompleted)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, course['AssessmentID'], score, pass_status, str(date.today())))

            # Save enrollment
            cursor.execute('''
                INSERT INTO enrollments (UserID, CourseID, EnrollmentDate, Status, Progress)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, course_id, str(date.today()), pass_status, score))

            # Update skill points
            if credits > 0 and course['SkillID']:
                cursor.execute(
                    'SELECT UserSkillID FROM user_skills WHERE UserID = ? AND SkillID = ?',
                    (user_id, course['SkillID'])
                )
                if cursor.fetchone():
                    cursor.execute(
                        'UPDATE user_skills SET TotalPoints = TotalPoints + ? WHERE UserID = ? AND SkillID = ?',
                        (credits, user_id, course['SkillID'])
                    )
                else:
                    cursor.execute(
                        'INSERT INTO user_skills (UserID, SkillID, TotalPoints) VALUES (?, ?, ?)',
                        (user_id, course['SkillID'], credits)
                    )

            # Award certificate if 70%+
            if score >= 70:
                cursor.execute(
                    'SELECT CertificateID FROM certificates WHERE UserID = ? AND CourseID = ?',
                    (user_id, course_id)
                )
                if not cursor.fetchone():
                    cursor.execute(
                        'INSERT INTO certificates (UserID, CourseID, IssueDate) VALUES (?, ?, ?)',
                        (user_id, course_id, str(date.today()))
                    )

            conn.commit()

        conn.close()

    except Exception as e:
        flash(f'Could not save result: {str(e)}', 'error')

    if not course:
        return redirect(url_for('courses'))

    return render_template('result.html',
        course  = course,
        score   = score,
        credits = credits)

# ── PROFILE ───────────────────────────────────────────────────────────────────
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id   = session['user_id']
    skills    = []
    certs     = []
    total_pts = 0

    try:
        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.SkillCategory AS SkillName,
                   SUM(us.TotalPoints) AS TotalPoints
            FROM user_skills us
            JOIN skills s ON us.SkillID = s.SkillID
            WHERE us.UserID = ?
            GROUP BY s.SkillCategory
            ORDER BY TotalPoints DESC
        ''', (user_id,))
        skills = [dict(row) for row in cursor.fetchall()]

        cursor.execute(
            'SELECT COALESCE(SUM(TotalPoints), 0) AS total FROM user_skills WHERE UserID = ?',
            (user_id,)
        )
        total_pts = cursor.fetchone()['total']

        cursor.execute('''
            SELECT c.CourseName, cert.IssueDate
            FROM certificates cert
            JOIN courses c ON cert.CourseID = c.CourseID
            WHERE cert.UserID = ?
            ORDER BY cert.IssueDate DESC
        ''', (user_id,))
        certs = [dict(row) for row in cursor.fetchall()]

        conn.close()

    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')

    return render_template('profile.html',
        user            = session['user'],
        skills          = skills,
        certs           = certs,
        total_pts       = total_pts,
        get_skill_level = get_skill_level)

# ── TALENT HUB ────────────────────────────────────────────────────────────────
@app.route('/talent')
def talent():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    learners   = []
    subscribed = False
    company_id = session['user_id']
    today      = str(date.today())

    try:
        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SubscriptionID FROM subscriptions
            WHERE CompanyID = ? AND Status = "Active" AND EndDate >= ?
        ''', (company_id, today))
        subscribed = cursor.fetchone() is not None

        cursor.execute('''
            SELECT u.UserID, u.Username, u.Email, u.PhoneNumber,
                   COALESCE(SUM(us.TotalPoints), 0) AS total
            FROM users u
            LEFT JOIN user_skills us ON us.UserID = u.UserID
            WHERE u.Role = "Student"
            GROUP BY u.UserID
            ORDER BY total DESC
        ''')
        learners = [dict(row) for row in cursor.fetchall()]

        for learner in learners:
            cursor.execute('''
                SELECT s.SkillCategory AS SkillName,
                       SUM(us.TotalPoints) AS TotalPoints
                FROM user_skills us
                JOIN skills s ON us.SkillID = s.SkillID
                WHERE us.UserID = ? AND us.TotalPoints > 0
                GROUP BY s.SkillCategory
                ORDER BY TotalPoints DESC
            ''', (learner['UserID'],))
            rows = cursor.fetchall()
            learner['skills'] = ' | '.join(
                f"{r['SkillName']}: {r['TotalPoints']} pts" for r in rows
            )

        conn.close()

    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')

    return render_template('talent.html',
        learners   = learners,
        subscribed = subscribed)

# ── SUBSCRIBE ─────────────────────────────────────────────────────────────────
@app.route('/subscribe', methods=['POST'])
def subscribe():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    company_id = session['user_id']
    today      = str(date.today())

    try:
        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SubscriptionID FROM subscriptions
            WHERE CompanyID = ? AND Status = "Active" AND EndDate >= ?
        ''', (company_id, today))

        if cursor.fetchone():
            flash('You already have an active subscription.', 'success')
        else:
            from datetime import timedelta
            end_date = str(date.today() + timedelta(days=30))
            cursor.execute('''
                INSERT INTO subscriptions (CompanyID, StartDate, EndDate, Status)
                VALUES (?, ?, ?, "Active")
            ''', (company_id, today, end_date))
            conn.commit()
            flash('Subscription activated! You can now contact learners.', 'success')

        conn.close()

    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')

    return redirect(url_for('talent'))

# ── ABOUT ─────────────────────────────────────────────────────────────────────
@app.route('/about')
def about():
    return render_template('about.html')

# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
