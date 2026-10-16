"""
SQLite Database Module for Fresher ATS Resume Analyzer.
Manages users, authentication records, and user-specific resume analysis history.
"""

import os
import json
import sqlite3
from datetime import datetime

# Resolve default database file path relative to this script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "fresher_ats.db")


def get_connection(db_path=None):
    """
    Establish and return a SQLite database connection with row factory enabled
    and reasonable busy timeout to prevent locking issues.
    """
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    # Enable Write-Ahead Logging (WAL) for better concurrent read/write support
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    return conn


def seed_verified_jobs(cursor):
    """
    Seed verified fresher tech jobs across Python, AI/ML, Data Analyst, and Web Developer roles.
    Only seeds if the jobs table is empty.
    """
    cursor.execute("SELECT COUNT(*) FROM jobs;")
    count = cursor.fetchone()[0]
    if count > 0:
        return

    verified_jobs = [
        (
            "Python Developer (Fresher)",
            "Zoho Corporation",
            "Chennai, Tamil Nadu",
            "Full-Time",
            "Fresher (0-1 yrs)",
            "₹4.5 - 6.5 LPA",
            """Zoho is hiring Fresher Python Developers for our cloud product engineering team in Chennai.

Responsibilities:
- Design and implement backend web services and automation scripts using Python.
- Work with relational databases such as MySQL and PostgreSQL.
- Interface with REST APIs and collaborate with frontend developers.
- Write unit tests and maintain high code quality standards.

Requirements:
- Strong proficiency in Python and core OOP principles.
- Familiarity with SQL databases, Git version control, and data structures.
- Academic projects or GitHub contributions demonstrating Python experience.
- B.E / B.Tech / MCA freshers (2025/2026 batch welcome).""",
            json.dumps(["Python", "SQL", "MySQL", "Git", "REST API", "Data Structures"]),
            "https://www.zoho.com/careers/",
            "Zoho Official Careers Portal",
            "2026-10-10"
        ),
        (
            "Associate Software Engineer (Python & Backend)",
            "Cisco Systems India",
            "Bangalore, Karnataka",
            "Full-Time",
            "Fresher / Entry-Level",
            "₹9.0 - 12.0 LPA",
            """Cisco India is seeking Graduate Engineers for Python Backend Development.

Responsibilities:
- Build robust microservices using Python and FastAPI / Flask.
- Develop and execute automated unit tests in a CI/CD environment.
- Interface with Docker containers and Linux systems.

Requirements:
- Strong knowledge of Python, OOP, Linux, Git, and REST APIs.
- Familiarity with containerization (Docker) is a plus.
- Degree in Computer Science, Information Technology, or related discipline.""",
            json.dumps(["Python", "FastAPI", "Linux", "Docker", "Git", "REST API", "Unit Testing"]),
            "https://jobs.cisco.com/",
            "Cisco Official Careers Portal",
            "2026-10-11"
        ),
        (
            "AI / Machine Learning Engineer (Graduate Trainee)",
            "Microsoft India",
            "Hyderabad, Telangana (Hybrid)",
            "Full-Time",
            "Entry-Level (0-1 yrs)",
            "₹14.0 - 18.0 LPA",
            """Microsoft India R&D is hiring entry-level AI/ML Engineers.

Responsibilities:
- Assist in developing, training, and testing machine learning models and NLP pipelines.
- Preprocess large-scale text and numerical datasets using Python, Pandas, and NumPy.
- Benchmark model performance against standardized accuracy and latency metrics.

Requirements:
- Solid foundation in machine learning fundamentals, statistics, and linear algebra.
- Hands-on experience with Python, PyTorch / TensorFlow, Scikit-learn, and Git.
- Academic or personal projects in Deep Learning or Natural Language Processing (NLP).""",
            json.dumps(["Python", "Machine Learning", "Deep Learning", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "NLP", "Git"]),
            "https://careers.microsoft.com/",
            "Microsoft Global Careers",
            "2026-10-12"
        ),
        (
            "Junior AI / ML Engineer",
            "Fractal Analytics",
            "Mumbai / Bangalore",
            "Full-Time",
            "Fresher (0-1 yrs)",
            "₹6.5 - 8.5 LPA",
            """Fractal is looking for Junior AI/ML Engineers passionate about enterprise AI solutions.

Responsibilities:
- Clean and explore structured and unstructured data using Pandas and NumPy.
- Implement machine learning algorithms using Scikit-learn and TensorFlow.
- Create data visualizations and summaries using Matplotlib and Seaborn.

Requirements:
- Proficiency in Python, SQL, and core Machine Learning algorithms.
- Academic coursework or certifications in Data Science or Artificial Intelligence.
- Strong problem-solving and communication skills.""",
            json.dumps(["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Data Analysis", "Matplotlib"]),
            "https://fractal.ai/careers/",
            "Fractal Official Careers",
            "2026-10-09"
        ),
        (
            "Data Analyst Fresher",
            "Amazon India",
            "Bangalore, Karnataka",
            "Full-Time",
            "Fresher (0-1 yrs)",
            "₹6.0 - 8.5 LPA",
            """Amazon Operations is hiring a Data Analyst Fresher in Bangalore.

Responsibilities:
- Extract, analyze, and synthesize large operational datasets using SQL.
- Build interactive operational reports and KPI dashboards using Power BI and Tableau.
- Automate repetitive data extraction workflows using Python (Pandas).

Requirements:
- Strong SQL querying skills (Joins, Aggregations, Window Functions).
- Familiarity with Python, Pandas, Excel, and data visualization tools.
- Analytical mindset with attention to detail and data integrity.""",
            json.dumps(["SQL", "Python", "Pandas", "Data Analysis", "Data Analytics", "Power BI", "Tableau", "Excel", "Statistics"]),
            "https://www.amazon.jobs/",
            "Amazon Jobs Portal",
            "2026-10-13"
        ),
        (
            "Junior Data Analyst (Campus Hiring)",
            "Deloitte India",
            "Hyderabad, Telangana",
            "Full-Time",
            "Fresher (0-1 yrs)",
            "₹5.5 - 7.5 LPA",
            """Deloitte Risk & Financial Advisory is hiring Junior Data Analysts.

Responsibilities:
- Query enterprise relational databases and validate data consistency.
- Perform statistical analysis and identify trends using Python and Excel.
- Present insights to internal stakeholders via Power BI dashboards.

Requirements:
- B.Tech / B.Sc / BCA in Computer Science, Statistics, or Mathematics.
- Practical knowledge of SQL, Python, Excel, and descriptive statistics.
- Eagerness to learn cloud database platforms.""",
            json.dumps(["SQL", "Python", "Data Analysis", "Power BI", "Statistics", "Excel", "Data Visualization"]),
            "https://usrecruiting.deloitte.com/",
            "Deloitte Official Career Portal",
            "2026-10-08"
        ),
        (
            "Frontend Web Developer (React.js)",
            "Freshworks",
            "Chennai, Tamil Nadu",
            "Full-Time",
            "Fresher (0-1 yrs)",
            "₹6.0 - 8.0 LPA",
            """Freshworks is hiring passionate fresher frontend developers to create intuitive user interfaces.

Responsibilities:
- Build responsive, interactive web components using React, HTML5, and CSS3 / Tailwind.
- Integrate frontend views with RESTful backend APIs.
- Collaborate with designers and QA teams to deliver delightful user experiences.

Requirements:
- Solid understanding of JavaScript (ES6+), React, HTML, and CSS.
- Familiarity with Git version control and modern web developer tools.
- Responsive design principles and attention to UI details.""",
            json.dumps(["JavaScript", "React", "HTML", "HTML5", "CSS", "CSS3", "Tailwind", "REST API", "Git"]),
            "https://careers.freshworks.com/",
            "Freshworks Careers",
            "2026-10-11"
        ),
        (
            "Junior Full Stack Web Developer",
            "Thoughtworks India",
            "Pune / Bangalore",
            "Full-Time",
            "Fresher (0-1 yrs)",
            "₹8.0 - 10.5 LPA",
            """Thoughtworks is seeking Graduate Full Stack Developers.

Responsibilities:
- Develop clean, test-driven code across frontend and backend services.
- Work with React on the client side and Python / Node.js on the server side.
- Design database schemas and write efficient SQL queries.

Requirements:
- Solid foundation in JavaScript, React, and backend programming (Python or Node.js).
- Familiarity with SQL databases, REST APIs, Git, and automated testing.
- Strong willingness to learn agile engineering practices and TDD.""",
            json.dumps(["JavaScript", "React", "Node.js", "Python", "SQL", "HTML", "CSS", "Git", "REST API"]),
            "https://www.thoughtworks.com/careers",
            "Thoughtworks Global Careers",
            "2026-10-07"
        ),
        (
            "Graduate Engineer Trainee (Software)",
            "Tata Consultancy Services (TCS)",
            "Pan India (Bangalore / Chennai / Pune / Hyderabad)",
            "Full-Time",
            "Fresher (2025/2026 Batch)",
            "₹3.6 - 7.0 LPA",
            """TCS is onboarding Graduate Engineer Trainees across Ninja and Digital streams.

Responsibilities:
- Participate in software development life cycle activities for global clients.
- Develop and maintain enterprise applications using Python, Java, or C++.
- Write database queries in SQL and perform debugging and unit testing.

Requirements:
- B.E / B.Tech / MCA graduates with minimum 60% academic aggregate.
- Good understanding of core programming (Python, Java, or C++), SQL, and algorithms.
- Strong aptitude and problem-solving skills.""",
            json.dumps(["Python", "Java", "C++", "SQL", "Git", "Data Structures", "Algorithms"]),
            "https://www.tcs.com/careers",
            "TCS Official Careers Portal",
            "2026-10-14"
        ),
        (
            "System Engineer (Python & Cloud Specialist)",
            "Infosys Limited",
            "Bangalore / Mysore / Pune",
            "Full-Time",
            "Fresher (0-1 yrs)",
            "₹3.6 - 6.5 LPA",
            """Infosys is hiring Fresher System Engineers.

Responsibilities:
- Participate in agile sprint teams to build and maintain cloud-native applications.
- Develop modular Python backend scripts and integrate with REST APIs.
- Support cloud infrastructure on AWS and write database queries in SQL.

Requirements:
- Engineering graduate with strong foundation in Python and OOP.
- Basic understanding of Linux commands, SQL, and Git.
- Willingness to undergo intensive foundational training at Infosys Mysore Campus.""",
            json.dumps(["Python", "SQL", "OOP", "Linux", "Git", "AWS", "REST API"]),
            "https://careers.infosys.com/",
            "Infosys Official Careers",
            "2026-10-12"
        ),
        (
            "Software Engineering Intern (Web & Python)",
            "Accenture India",
            "Bangalore, Karnataka",
            "Internship",
            "Fresher / Final Year Student",
            "₹30,000 / month Stipend",
            """Accenture Technology is seeking dynamic Engineering Interns.

Responsibilities:
- Work alongside senior developers on full-stack web modules and Python APIs.
- Write unit tests, document technical workflows, and debug issues.
- Potential conversion to full-time Associate Software Engineer upon completion.

Requirements:
- Final year B.Tech / MCA student or recent graduate.
- Hands-on knowledge of Python, HTML, CSS, JavaScript, and SQL.
- Eagerness to collaborate in a fast-paced technology consulting environment.""",
            json.dumps(["Python", "JavaScript", "HTML", "CSS", "SQL", "Git"]),
            "https://www.accenture.com/in-en/careers",
            "Accenture Career Portal",
            "2026-10-10"
        ),
        (
            "Junior Data Scientist (Campus Hiring Drive)",
            "Tech Innovations Labs",
            "Remote",
            "Full-Time",
            "Fresher (0-1 yrs)",
            "Salary Not Disclosed",
            """Direct recruitment drive for upcoming AI labs research team.

Responsibilities:
- Assist in feature engineering and statistical modeling on exploratory datasets.
- Implement machine learning pipelines in Python using Pandas, NumPy, and Scikit-learn.
- Document experiment results and present model evaluation metrics.

Note:
- Applications for this drive are handled directly via college placement coordinator.
- Official application link is currently offline / unavailable online.""",
            json.dumps(["Python", "Machine Learning", "Pandas", "NumPy", "Statistics"]),
            "",
            "Campus Placement Drive",
            "2026-10-05"
        )
    ]

    cursor.executemany("""
        INSERT INTO jobs (
            title, company, location, job_type, experience_level,
            salary, description, required_skills, apply_url, source, posted_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, verified_jobs)


def init_db(db_path=None):
    """
    Initialize SQLite database tables:
    1. users: user profile and hashed credentials
    2. analysis_history: per-user resume analysis records
    """
    path = db_path or DEFAULT_DB_PATH
    conn = get_connection(path)
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            linkedin TEXT DEFAULT '',
            github TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Analysis history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            ats_score REAL NOT NULL,
            job_match_score REAL NOT NULL,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 3. Verified Jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL DEFAULT 'Full-Time',
            experience_level TEXT NOT NULL DEFAULT 'Fresher',
            salary TEXT DEFAULT '',
            description TEXT NOT NULL,
            required_skills TEXT NOT NULL DEFAULT '[]',
            apply_url TEXT DEFAULT '',
            source TEXT DEFAULT 'Official Career Portal',
            posted_date TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 4. Saved Jobs table (User Bookmarks)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
            UNIQUE(user_id, job_id)
        );
    """)

    # 5. Job Applications Tracker table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            location TEXT DEFAULT '',
            apply_url TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Applied',
            applied_date TEXT NOT NULL,
            notes TEXT DEFAULT '',
            is_manually_recorded INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    seed_verified_jobs(cursor)

    conn.commit()
    conn.close()


def create_user(full_name, email, password_hash, linkedin="", github="", db_path=None):
    """
    Insert a newly registered user into the database.
    Returns the new user id on success, or raises sqlite3.IntegrityError if email exists.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (full_name, email, password_hash, linkedin, github)
        VALUES (?, ?, ?, ?, ?)
    """, (full_name.strip(), email.strip().lower(), password_hash, linkedin.strip(), github.strip()))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user_by_email(email, db_path=None):
    """Fetch user dictionary by email (case-insensitive)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id, db_path=None):
    """Fetch user dictionary by primary key id."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_profile(user_id, full_name, linkedin="", github="", db_path=None):
    """Update user's full name, linkedin, and github profile links."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET full_name = ?, linkedin = ?, github = ?
        WHERE id = ?
    """, (full_name.strip(), linkedin.strip(), github.strip(), user_id))
    conn.commit()
    conn.close()
    return True


def save_analysis(user_id, resume_name, job_title, ats_score, job_match_score, db_path=None):
    """
    Save a completed resume analysis into the analysis_history table for the logged-in user.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_history (user_id, resume_name, job_title, ats_score, job_match_score)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        resume_name.strip(),
        job_title.strip(),
        round(float(ats_score), 1),
        round(float(job_match_score), 1)
    ))
    history_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return history_id


def get_user_history(user_id, limit=None, db_path=None):
    """
    Retrieve analysis history strictly for the requested user_id.
    Ensures strict tenant isolation (a user never sees another user's data).
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    query = """
        SELECT id, user_id, resume_name, job_title, ats_score, job_match_score, analysis_date
        FROM analysis_history
        WHERE user_id = ?
        ORDER BY id DESC
    """
    if limit:
        query += f" LIMIT {int(limit)}"
        cursor.execute(query, (user_id,))
    else:
        cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_stats(user_id, db_path=None):
    """
    Calculate summary statistics for the user dashboard:
    - Total Resumes Checked
    - Average ATS Score
    - Latest ATS Score
    - Latest Job Match
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as total_count, AVG(ats_score) as avg_ats
        FROM analysis_history
        WHERE user_id = ?
    """, (user_id,))
    agg = cursor.fetchone()
    total_resumes = agg["total_count"] if agg else 0
    avg_ats = round(agg["avg_ats"], 1) if agg and agg["avg_ats"] is not None else 0.0

    # Fetch most recent analysis
    cursor.execute("""
        SELECT ats_score, job_match_score
        FROM analysis_history
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))
    latest = cursor.fetchone()
    latest_ats = round(latest["ats_score"], 1) if latest else 0.0
    latest_job_match = round(latest["job_match_score"], 1) if latest else 0.0

    # Count total saved jobs
    cursor.execute("SELECT COUNT(*) FROM saved_jobs WHERE user_id = ?", (user_id,))
    total_saved = cursor.fetchone()[0]

    # Count total applications
    cursor.execute("SELECT COUNT(*) FROM job_applications WHERE user_id = ?", (user_id,))
    total_apps = cursor.fetchone()[0]
    conn.close()

    return {
        "total_resumes": total_resumes,
        "avg_ats": avg_ats,
        "latest_ats": latest_ats,
        "latest_job_match": latest_job_match,
        "total_saved_jobs": total_saved,
        "total_applications": total_apps
    }


# ==============================================================================
# JOB SEARCH, SAVED JOBS, AND APPLICATION TRACKER HELPERS
# ==============================================================================

def get_jobs(query=None, location=None, job_type=None, role=None, limit=50, search_query=None, db_path=None):
    """
    Search and filter verified jobs from the database.
    - query / search_query: Matches against job title, company name, or description
    - location: Filters by specific location substring
    - job_type: Filters by Full-Time, Internship, Remote, etc.
    - role: Filters by technical job role keywords
    """
    if query is None and search_query is not None:
        query = search_query

    conn = get_connection(db_path)
    cursor = conn.cursor()

    sql = "SELECT * FROM jobs WHERE is_active = 1"
    params = []

    if query and str(query).strip():
        q = f"%{str(query).strip().lower()}%"
        sql += " AND (LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(description) LIKE ?)"
        params.extend([q, q, q])

    if location and location.strip() and location.strip().lower() != "all":
        loc = f"%{location.strip().lower()}%"
        sql += " AND LOWER(location) LIKE ?"
        params.append(loc)

    if job_type and job_type.strip() and job_type.strip().lower() != "all":
        jt = f"%{job_type.strip().lower()}%"
        sql += " AND LOWER(job_type) LIKE ?"
        params.append(jt)

    if role and role.strip() and role.strip().lower() != "all":
        r = f"%{role.strip().lower()}%"
        sql += " AND (LOWER(title) LIKE ? OR LOWER(required_skills) LIKE ?)"
        params.extend([r, r])

    sql += " ORDER BY id DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["eligibility"] = d.get("experience_level") or "Fresher / Entry-Level"
        try:
            d["required_skills_list"] = json.loads(d.get("required_skills") or "[]")
        except Exception:
            d["required_skills_list"] = []
        results.append(d)

    return results


def get_job_by_id(job_id, db_path=None):
    """Retrieve full details for a single job by id."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["eligibility"] = d.get("experience_level") or "Fresher / Entry-Level"
    try:
        d["required_skills_list"] = json.loads(d.get("required_skills") or "[]")
    except Exception:
        d["required_skills_list"] = []
    return d


def save_job_for_user(user_id, job_id, db_path=None):
    """Save/bookmark a job for a user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO saved_jobs (user_id, job_id)
        VALUES (?, ?)
    """, (user_id, job_id))
    conn.commit()
    conn.close()
    return True


def unsave_job_for_user(user_id, job_id, db_path=None):
    """Remove a bookmarked job for a user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM saved_jobs WHERE user_id = ? AND job_id = ?
    """, (user_id, job_id))
    conn.commit()
    conn.close()
    return True


def is_job_saved(user_id, job_id, db_path=None):
    """Check if a specific job is already saved by the user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM saved_jobs WHERE user_id = ? AND job_id = ? LIMIT 1
    """, (user_id, job_id))
    saved = cursor.fetchone() is not None
    conn.close()
    return saved


def get_saved_jobs_for_user(user_id, db_path=None):
    """Fetch all saved jobs for a specific user with full job details."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.*, sj.saved_at
        FROM saved_jobs sj
        JOIN jobs j ON sj.job_id = j.id
        WHERE sj.user_id = ?
        ORDER BY sj.id DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["eligibility"] = d.get("experience_level") or "Fresher / Entry-Level"
        try:
            d["required_skills_list"] = json.loads(d.get("required_skills") or "[]")
        except Exception:
            d["required_skills_list"] = []
        results.append(d)
    return results


def create_job_application(
    user_id,
    job_title=None,
    company_name=None,
    location="",
    apply_url="",
    status="Applied",
    applied_date=None,
    notes="",
    job_id=None,
    role=None,
    company=None,
    db_path=None
):
    """Record an application logged by the candidate."""
    if not job_title and role:
        job_title = role
    if not job_title:
        job_title = "Target Role"

    if not company_name and company:
        company_name = company
    if not company_name:
        company_name = "Target Company"

    if not applied_date:
        applied_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_applications (
            user_id, job_id, job_title, company_name, location,
            apply_url, status, applied_date, notes, is_manually_recorded
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        user_id,
        job_id,
        str(job_title).strip(),
        str(company_name).strip(),
        str(location).strip(),
        str(apply_url).strip(),
        str(status).strip(),
        str(applied_date).strip(),
        str(notes).strip()
    ))
    app_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return app_id


def update_job_application_status(arg1, arg2, status, notes=None, db_path=None):
    """
    Update application stage/status or add notes with user isolation guard.
    Supports either (application_id, user_id, status...) or (user_id, application_id, status...).
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if notes is not None:
        cursor.execute("""
            UPDATE job_applications
            SET status = ?, notes = ?, updated_at = ?
            WHERE (id = ? AND user_id = ?) OR (id = ? AND user_id = ?)
        """, (str(status).strip(), str(notes).strip(), now_str, arg1, arg2, arg2, arg1))
    else:
        cursor.execute("""
            UPDATE job_applications
            SET status = ?, updated_at = ?
            WHERE (id = ? AND user_id = ?) OR (id = ? AND user_id = ?)
        """, (str(status).strip(), now_str, arg1, arg2, arg2, arg1))

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def delete_job_application(arg1, arg2, db_path=None):
    """
    Remove a job application record strictly for the owner user.
    Supports either (application_id, user_id) or (user_id, application_id).
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM job_applications
        WHERE (id = ? AND user_id = ?) OR (id = ? AND user_id = ?)
    """, (arg1, arg2, arg2, arg1))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_user_applications(user_id, status_filter=None, db_path=None):
    """Retrieve all logged job applications for a user, optionally filtered by status."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    if status_filter and status_filter.strip() and status_filter.strip().lower() != "all":
        cursor.execute("""
            SELECT * FROM job_applications
            WHERE user_id = ? AND LOWER(status) = LOWER(?)
            ORDER BY id DESC
        """, (user_id, status_filter.strip()))
    else:
        cursor.execute("""
            SELECT * FROM job_applications
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["role"] = d.get("job_title", "")
        d["company"] = d.get("company_name", "")
        results.append(d)
    return results


def get_user_job_stats(user_id, db_path=None):
    """
    Get aggregated statistics for job search & tracker:
    - total_saved: count of saved jobs
    - total_applications: count of applications
    - status_counts: dictionary of count per status
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM saved_jobs WHERE user_id = ?", (user_id,))
    total_saved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM job_applications WHERE user_id = ?", (user_id,))
    total_applications = cursor.fetchone()[0]

    cursor.execute("""
        SELECT status, COUNT(*) as cnt
        FROM job_applications
        WHERE user_id = ?
        GROUP BY status
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    status_counts = {"Saved": 0, "Applied": 0, "Interview": 0, "Rejected": 0, "Offer": 0}
    for r in rows:
        st = r["status"]
        status_counts[st] = r["cnt"]

    return {
        "total": total_applications,
        "total_saved": total_saved,
        "total_applications": total_applications,
        "status_counts": status_counts,
        "saved": status_counts.get("Saved", 0),
        "applied": status_counts.get("Applied", 0),
        "interview": status_counts.get("Interview", 0),
        "rejected": status_counts.get("Rejected", 0),
        "offer": status_counts.get("Offer", 0),
    }

