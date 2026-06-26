import sqlite3

def get_db():
    conn = sqlite3.connect('skillsdev.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn   = get_db()
    cursor = conn.cursor()

    cursor.executescript('''

        CREATE TABLE IF NOT EXISTS users (
            UserID      INTEGER PRIMARY KEY AUTOINCREMENT,
            Username    TEXT NOT NULL UNIQUE,
            Email       TEXT NOT NULL UNIQUE,
            Password    TEXT NOT NULL,
            PhoneNumber TEXT,
            Role        TEXT DEFAULT "Student"
        );

        CREATE TABLE IF NOT EXISTS courses (
            CourseID     INTEGER PRIMARY KEY AUTOINCREMENT,
            CourseName   TEXT NOT NULL,
            Duration     INTEGER,
            Description  TEXT,
            SkillCredits INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS skills (
            SkillID          INTEGER PRIMARY KEY AUTOINCREMENT,
            SkillName        TEXT NOT NULL,
            SkillCategory    TEXT,
            SkillDescription TEXT,
            SkillLevel       TEXT,
            CourseID         INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            EnrollmentID   INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID         INTEGER NOT NULL,
            CourseID       INTEGER NOT NULL,
            EnrollmentDate TEXT,
            Status         TEXT,
            Progress       INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS assessments (
            AssessmentID   INTEGER PRIMARY KEY AUTOINCREMENT,
            CourseID       INTEGER NOT NULL,
            AssessmentName TEXT NOT NULL,
            TotalMarks     INTEGER NOT NULL,
            PassMark       INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS questions (
            QuestionID    INTEGER PRIMARY KEY AUTOINCREMENT,
            AssessmentID  INTEGER NOT NULL,
            QuestionText  TEXT NOT NULL,
            OptionA       TEXT NOT NULL,
            OptionB       TEXT NOT NULL,
            OptionC       TEXT NOT NULL,
            OptionD       TEXT NOT NULL,
            CorrectAnswer TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS learning_materials (
            MaterialID      INTEGER PRIMARY KEY AUTOINCREMENT,
            CourseID        INTEGER NOT NULL,
            SkillID         INTEGER,
            MaterialTitle   TEXT NOT NULL,
            MaterialType    TEXT,
            SourcePlatform  TEXT,
            MaterialURL     TEXT,
            Description     TEXT,
            DifficultyLevel TEXT
        );

        CREATE TABLE IF NOT EXISTS results (
            ResultID      INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID        INTEGER NOT NULL,
            AssessmentID  INTEGER NOT NULL,
            Score         INTEGER,
            PassStatus    TEXT,
            DateCompleted TEXT
        );

        CREATE TABLE IF NOT EXISTS certificates (
            CertificateID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID        INTEGER NOT NULL,
            CourseID      INTEGER NOT NULL,
            IssueDate     TEXT
        );

        CREATE TABLE IF NOT EXISTS user_skills (
            UserSkillID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID      INTEGER NOT NULL,
            SkillID     INTEGER NOT NULL,
            TotalPoints INTEGER NOT NULL DEFAULT 0,
            UNIQUE (UserID, SkillID)
        );

        CREATE TABLE IF NOT EXISTS subscriptions (
            SubscriptionID INTEGER PRIMARY KEY AUTOINCREMENT,
            CompanyID      INTEGER NOT NULL,
            StartDate      TEXT NOT NULL,
            EndDate        TEXT NOT NULL,
            Status         TEXT NOT NULL DEFAULT "Active"
        );

    ''')

    # Only insert data if courses table is empty
    cursor.execute('SELECT COUNT(*) FROM courses')
    if cursor.fetchone()[0] == 0:

        cursor.executescript('''

            INSERT INTO courses (CourseID, CourseName, Duration, Description, SkillCredits) VALUES
            (1, "Java Programming",    60, "Learn Java programming fundamentals including OOP concepts.",      20),
            (2, "Python Programming",  60, "Learn Python basics including variables, loops and functions.",    20),
            (3, "Excel Fundamentals",  45, "Learn the basics of Excel including formulas, charts and data.",   10),
            (4, "Project Management",  45, "Learn the fundamentals of planning and managing projects.",        20),
            (5, "Communication Skills",30, "Build professional communication skills for the modern workplace.",10),
            (6, "Business Management", 45, "Understand key business management principles and strategies.",    30);

            INSERT INTO skills (SkillID, SkillName, SkillCategory, SkillDescription, SkillLevel, CourseID) VALUES
            (1, "Java Programming",   "Programming",     "Object oriented programming using Java",         "Intermediate", 1),
            (2, "Python Programming", "Programming",     "General purpose programming using Python",        "Beginner",     2),
            (3, "Microsoft Excel",    "Microsoft Excel", "Spreadsheet skills and data management",          "Beginner",     3),
            (4, "Project Management", "Business",        "Planning, executing and closing projects",         "Intermediate", 4),
            (5, "Communication",      "Soft Skills",     "Professional and workplace communication",         "Beginner",     5),
            (6, "Business Management","Business",        "Core business principles and management skills",  "Intermediate", 6);

            INSERT INTO assessments (AssessmentID, CourseID, AssessmentName, TotalMarks, PassMark) VALUES
            (1, 1, "Java Programming Assessment",    100, 50),
            (2, 2, "Python Programming Assessment",  100, 50),
            (3, 3, "Excel Fundamentals Assessment",  100, 50),
            (4, 4, "Project Management Assessment",  100, 50),
            (5, 5, "Communication Skills Assessment",100, 50),
            (6, 6, "Business Management Assessment", 100, 50);

            INSERT INTO learning_materials (CourseID, SkillID, MaterialTitle, MaterialType, SourcePlatform, MaterialURL, Description, DifficultyLevel) VALUES
            (1, 1, "A Gentle Introduction to Java",  "Lecture Notes", "MIT OpenCourseWare", "https://ocw.mit.edu/courses/6-092-introduction-to-programming-in-java-january-iap-2010/", "MIT intro to Java programming course", "Beginner"),
            (1, 1, "Java OOP Concepts",              "Video",         "YouTube",            "https://www.youtube.com/watch?v=pTB0EiLXUC8",                                            "Full Java OOP tutorial for beginners", "Intermediate"),
            (2, 2, "MIT Python Introduction",        "Lecture Notes", "MIT OpenCourseWare", "https://ocw.mit.edu/courses/6-189-a-gentle-introduction-to-programming-using-python-january-iap-2008/pages/lecture-notes/", "MIT gentle introduction to Python", "Beginner"),
            (2, 2, "Python for Beginners",           "Video",         "YouTube",            "https://www.youtube.com/watch?v=rfscVS0vtbw",                                            "Full Python tutorial for beginners",  "Beginner"),
            (2, 2, "Python on freeCodeCamp",         "Course",        "freeCodeCamp",       "https://www.freecodecamp.org/learn/scientific-computing-with-python/",                    "Free structured Python learning path","Intermediate"),
            (3, 3, "Excel for Beginners",            "Video",         "YouTube",            "https://www.youtube.com/watch?v=rwbho0CgEAI",                                            "Full Excel tutorial for beginners",   "Beginner"),
            (4, 4, "Project Management Basics",      "Course",        "Google Digital Garage","https://learndigital.withgoogle.com/digitalgarage",                                    "Free project management course",      "Beginner"),
            (5, 5, "Communication Skills",           "Course",        "Khan Academy",        "https://www.khanacademy.org",                                                            "Free communication skills course",    "Beginner"),
            (6, 6, "Business Management Intro",      "Course",        "Google Digital Garage","https://learndigital.withgoogle.com/digitalgarage",                                    "Free business management course",     "Beginner");

        ''')

        # Java questions
        java_questions = [
            (1, "What is Java?", "A type of coffee", "A programming language", "A database", "An operating system", "B"),
            (1, "What does OOP stand for?", "Object Oriented Programming", "Open Office Platform", "Ordered Output Processing", "Object Output Platform", "A"),
            (1, "What is a class in Java?", "A group of students", "A blueprint for creating objects", "A type of variable", "A loop structure", "B"),
            (1, "What is inheritance in Java?", "Copying code", "A class receiving properties from another class", "A type of loop", "A data type", "B"),
            (1, "What is a method in Java?", "A variable", "A class", "A block of code that performs a task", "A data type", "C"),
            (1, "What keyword creates an object in Java?", "create", "build", "new", "make", "C"),
            (1, "What is polymorphism?", "Many forms of an object or method", "A type of database", "A loop structure", "An error type", "A"),
            (1, "What is encapsulation?", "Hiding data and restricting access", "Creating new classes", "Importing libraries", "Running a loop", "A"),
            (1, "What does void mean in Java?", "The method returns a value", "The method returns nothing", "The method is private", "The method is static", "B"),
            (1, "What is an interface in Java?", "A screen display", "A contract that a class must follow", "A type of loop", "A variable type", "B"),
        ]
        cursor.executemany(
            'INSERT INTO questions (AssessmentID, QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer) VALUES (?,?,?,?,?,?,?)',
            java_questions
        )

        # Python questions
        python_questions = [
            (2, "What is Python?", "A snake", "A programming language", "A database", "An operating system", "B"),
            (2, "How do you print in Python?", "console.log()", "System.out.println()", "print()", "echo()", "C"),
            (2, "What is a variable?", "A fixed value", "A container for storing data", "A type of loop", "A function", "B"),
            (2, "Which symbol is used for comments in Python?", "//", "#", "--", "**", "B"),
            (2, "What does a loop do?", "Stops the program", "Repeats a block of code", "Creates a variable", "Connects to a database", "B"),
            (2, "What is a list in Python?", "A single value", "An ordered collection of items", "A type of loop", "A function", "B"),
            (2, "What is a function in Python?", "A variable", "A loop", "A reusable block of code", "A data type", "C"),
            (2, "What does len() do in Python?", "Loops through a list", "Returns the length of an object", "Prints a value", "Creates a list", "B"),
            (2, "What is an if statement used for?", "Repeating code", "Making decisions based on conditions", "Storing data", "Defining a function", "B"),
            (2, "What does import do in Python?", "Creates a new file", "Brings in an external module", "Saves data", "Starts the program", "B"),
        ]
        cursor.executemany(
            'INSERT INTO questions (AssessmentID, QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer) VALUES (?,?,?,?,?,?,?)',
            python_questions
        )

        # Excel questions
        excel_questions = [
            (3, "What does the SUM function do in Excel?", "Adds all numbers in a range", "Multiplies numbers together", "Counts cells with text", "Divides numbers", "A"),
            (3, "Which symbol starts a formula in Excel?", "#", "@", "=", "$", "C"),
            (3, "What is a cell reference in Excel?", "A colour code", "A column and row identifier like A1", "A formula name", "A chart type", "B"),
            (3, "What does the AVERAGE function do?", "Finds the highest value", "Adds numbers together", "Calculates the mean of a range", "Counts numbers in a range", "C"),
            (3, "What is a pivot table used for?", "Drawing charts", "Summarising and analysing large data", "Formatting cells", "Adding formulas", "B"),
            (3, "What does the VLOOKUP function do?", "Searches for a value in a column", "Counts blank cells", "Sorts data alphabetically", "Merges two cells", "A"),
            (3, "What is conditional formatting?", "A way to print spreadsheets", "Locking cells from editing", "Changing cell appearance based on rules", "Removing duplicate values", "C"),
            (3, "What does the COUNT function do?", "Counts cells that contain numbers", "Adds all values in a range", "Finds the maximum value", "Rounds numbers up", "A"),
            (3, "What is a spreadsheet?", "A type of database", "A grid of rows and columns for data", "A presentation tool", "A word processor", "B"),
            (3, "What is a chart in Excel used for?", "Storing passwords", "Writing formulas", "Sorting data", "Visualising data graphically", "D"),
        ]
        cursor.executemany(
            'INSERT INTO questions (AssessmentID, QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer) VALUES (?,?,?,?,?,?,?)',
            excel_questions
        )

        # Project Management questions
        pm_questions = [
            (4, "What is a project?", "An ongoing business operation", "A temporary endeavour with a specific goal", "A daily work routine", "A company department", "B"),
            (4, "What does a Gantt chart show?", "Project budget breakdown", "Team member profiles", "Project timeline and tasks", "Risk assessment results", "C"),
            (4, "What is a stakeholder?", "A project tool", "A type of budget", "Anyone affected by or interested in the project", "The project manager only", "C"),
            (4, "What is scope creep?", "Finishing a project early", "Uncontrolled changes to project scope", "A project planning tool", "Reducing the project budget", "B"),
            (4, "What does PERT stand for?", "Project Evaluation and Review Tool", "Program Evaluation and Review Technique", "Project Estimation and Resource Tracking", "Process Evaluation and Risk Testing", "B"),
            (4, "What is risk management in a project?", "Hiring the right team", "Identifying and reducing project risks", "Setting the project deadline", "Writing the project report", "B"),
            (4, "What is a project milestone?", "The project budget", "A team meeting", "A significant point or achievement in a project", "The project manager", "C"),
            (4, "What is the purpose of a project charter?", "To formally authorise a project", "To assign tasks to team members", "To track project expenses", "To close a completed project", "A"),
            (4, "What is Agile methodology?", "A fixed step-by-step project approach", "A budgeting technique", "An iterative and flexible project approach", "A risk assessment tool", "C"),
            (4, "What is a project deadline?", "The start date of a project", "The date a project must be completed", "The project budget limit", "The number of team members needed", "B"),
        ]
        cursor.executemany(
            'INSERT INTO questions (AssessmentID, QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer) VALUES (?,?,?,?,?,?,?)',
            pm_questions
        )

        # Communication questions
        comm_questions = [
            (5, "What is effective communication?", "Talking as much as possible", "Clearly conveying a message so it is understood", "Using technical language", "Sending emails only", "B"),
            (5, "What is active listening?", "Fully concentrating on what the speaker is saying", "Waiting for your turn to speak", "Taking notes during a meeting", "Asking many questions", "A"),
            (5, "What is non-verbal communication?", "Written messages", "Phone calls", "Body language, facial expressions and gestures", "Emails and reports", "C"),
            (5, "What is feedback in communication?", "A type of barrier", "A response or reaction to a message", "A formal report", "A presentation style", "B"),
            (5, "What is a barrier to communication?", "A strong vocabulary", "Clear body language", "Anything that prevents clear understanding", "A well structured message", "C"),
            (5, "What is empathy in communication?", "Agreeing with everything someone says", "Speaking loudly and clearly", "Understanding and sharing the feelings of others", "Using formal language only", "C"),
            (5, "What is professional communication?", "Casual conversation with friends", "Formal and respectful interaction in the workplace", "Using slang and abbreviations", "Avoiding all eye contact", "B"),
            (5, "What is the purpose of a meeting agenda?", "To record meeting minutes", "To invite people to a meeting", "To outline topics to be discussed in a meeting", "To summarise the meeting after it ends", "C"),
            (5, "What is tone in communication?", "The volume of your voice", "The attitude and feeling conveyed in a message", "The length of a message", "The language used in writing", "B"),
            (5, "Which of the following improves workplace communication?", "Interrupting others frequently", "Avoiding feedback", "Being clear, respectful and listening actively", "Using only written communication", "C"),
        ]
        cursor.executemany(
            'INSERT INTO questions (AssessmentID, QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer) VALUES (?,?,?,?,?,?,?)',
            comm_questions
        )

        # Business Management questions
        bm_questions = [
            (6, "What is management?", "Owning a business", "Planning, organising and controlling resources to achieve goals", "Hiring employees", "Setting prices for products", "B"),
            (6, "What is a business objective?", "A product a business sells", "A goal or target a business aims to achieve", "A type of business expense", "A marketing strategy", "B"),
            (6, "What does SWOT stand for?", "Sales, Workforce, Operations, Targets", "Strategy, Work, Outcomes, Tactics", "Strengths, Weaknesses, Opportunities, Threats", "Systems, Workflow, Output, Testing", "C"),
            (6, "What is leadership?", "Managing a company budget", "Guiding, inspiring and motivating a team towards a goal", "Hiring new employees", "Writing business reports", "B"),
            (6, "What is delegation?", "Taking on all tasks yourself", "Reducing the number of employees", "Assigning tasks to other team members", "Cancelling a project", "C"),
            (6, "What is a business strategy?", "A daily work schedule", "A product description", "A long term plan to achieve business goals", "A financial report", "C"),
            (6, "What is cash flow?", "The profit a business makes", "The movement of money in and out of a business", "The total value of a business", "The number of customers a business has", "B"),
            (6, "What is the role of human resources?", "Managing company finances", "Marketing products and services", "Managing and supporting people in an organisation", "Developing company software", "C"),
            (6, "What is marketing?", "Hiring new staff", "Managing company operations", "Promoting and selling products or services", "Recording financial transactions", "C"),
            (6, "What is an organisational structure?", "A company budget plan", "How a business is arranged and roles are defined", "A list of company products", "A marketing campaign", "B"),
        ]
        cursor.executemany(
            'INSERT INTO questions (AssessmentID, QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer) VALUES (?,?,?,?,?,?,?)',
            bm_questions
        )

    conn.commit()
    conn.close()
    print("Database ready!")

if __name__ == '__main__':
    init_db()
