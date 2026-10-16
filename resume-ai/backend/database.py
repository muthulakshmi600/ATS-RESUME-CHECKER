"""
Database module for ResumeAI.
Provides SQLite persistence for user sessions, resume analyses, and settings.
"""

import sqlite3
import json
import os
import re
import urllib.parse
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resume_ai.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            target_role TEXT DEFAULT 'Software Developer',
            bio TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            resume_name TEXT NOT NULL,
            job_role TEXT NOT NULL,
            has_job_description INTEGER DEFAULT 0,
            overall_score INTEGER NOT NULL,
            score_formatting INTEGER NOT NULL,
            score_keywords INTEGER NOT NULL,
            score_skills INTEGER NOT NULL,
            score_job_match INTEGER NOT NULL,
            score_structure INTEGER NOT NULL,
            score_readability INTEGER NOT NULL,
            summary TEXT,
            matched_keywords TEXT,
            missing_keywords TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            section_status TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure details_json column exists
    cursor.execute("PRAGMA table_info(analyses)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'details_json' not in columns:
        try:
            cursor.execute("ALTER TABLE analyses ADD COLUMN details_json TEXT")
        except Exception:
            pass

    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            user_email TEXT PRIMARY KEY,
            scoring_sensitivity TEXT DEFAULT 'Standard',
            theme TEXT DEFAULT 'light',
            email_alerts INTEGER DEFAULT 0,
            auto_save INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Verified Jobs Catalog table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT DEFAULT 'Full-Time',
            experience_level TEXT DEFAULT 'Fresher (0-1 yrs)',
            salary TEXT,
            description TEXT NOT NULL,
            required_skills TEXT NOT NULL,
            application_url TEXT NOT NULL,
            portal_name TEXT DEFAULT 'Official Company Careers',
            is_remote INTEGER DEFAULT 0,
            posted_date TEXT,
            is_verified INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure jobs table has linkedin_url and naukri_url columns
    cursor.execute("PRAGMA table_info(jobs)")
    job_columns = [row[1] for row in cursor.fetchall()]
    if 'linkedin_url' not in job_columns:
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN linkedin_url TEXT")
        except Exception:
            pass
    if 'naukri_url' not in job_columns:
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN naukri_url TEXT")
        except Exception:
            pass

    # Saved Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            job_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_email, job_id)
        )
    ''')

    # Job Applications Tracker table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            job_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            application_url TEXT,
            status TEXT DEFAULT 'Applied',
            applied_date TEXT,
            notes TEXT,
            is_verified_application INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed verified jobs
    seed_verified_jobs(cursor)

    # Insert default demo user if not exists
    cursor.execute('SELECT id FROM users WHERE email = ?', ('test@gmail.com',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (email, name, password, target_role, bio)
            VALUES (?, ?, ?, ?, ?)
        ''', ('test@gmail.com', 'Alex Morgan', '12345', 'Full Stack Developer', 'Passionate software engineer building web and cloud applications.'))

    conn.commit()
    conn.close()

def save_analysis(user_email, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    job_role = data.get('job_role') or ('Job Match Analysis' if data.get('has_job_description') else 'Resume Quality')
    breakdown = data.get('breakdown', {})
    achievements_score = breakdown.get('achievements', breakdown.get('metrics', 0))
    job_match_score = data.get('job_match_score')
    if job_match_score is None:
        job_match_score = breakdown.get('job_match', 0)
    
    details_json = json.dumps(data)
    
    cursor.execute('''
        INSERT INTO analyses (
            user_email, resume_name, job_role, has_job_description,
            overall_score, score_formatting, score_keywords, score_skills,
            score_job_match, score_structure, score_readability,
            summary, matched_keywords, missing_keywords,
            matched_skills, missing_skills, section_status, suggestions, details_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_email,
        data.get('resume_name', 'Resume.pdf'),
        job_role,
        1 if data.get('has_job_description') else 0,
        int(data.get('overall_score', 0)),
        int(breakdown.get('formatting', 0)),
        int(achievements_score),
        int(breakdown.get('skills', 0)),
        int(job_match_score or 0),
        int(breakdown.get('structure', 0)),
        int(breakdown.get('readability', 0)),
        data.get('summary', ''),
        json.dumps(data.get('matched_keywords', [])),
        json.dumps(data.get('missing_keywords', [])),
        json.dumps(data.get('matched_skills', [])),
        json.dumps(data.get('missing_skills', [])),
        json.dumps(data.get('section_status', {})),
        json.dumps(data.get('suggestions', [])),
        details_json
    ))
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def _unpack_analysis_row(row):
    row_keys = row.keys()
    details = {}
    if 'details_json' in row_keys and row['details_json']:
        try:
            details = json.loads(row['details_json'])
        except Exception:
            details = {}

    quality_score = details.get('resume_quality_score', row['overall_score'])
    job_match = details.get('job_match_score', row['score_job_match'] if row['has_job_description'] else None)
    
    achievements_score = details.get('breakdown', {}).get('achievements', row['score_keywords'])
    contact_score = details.get('breakdown', {}).get('contact', 15)

    return {
        'id': row['id'],
        'user_email': row['user_email'],
        'resume_name': row['resume_name'],
        'job_role': row['job_role'],
        'has_job_description': bool(row['has_job_description']),
        'overall_score': row['overall_score'],
        'resume_quality_score': quality_score,
        'job_match_score': job_match,
        'grade': details.get('grade'),
        'breakdown': {
            'structure': row['score_structure'],
            'contact': contact_score,
            'achievements': achievements_score,
            'metrics': achievements_score,
            'formatting': row['score_formatting'],
            'readability': row['score_readability'],
            'skills': row['score_skills'],
            'job_match': row['score_job_match'],
            'keywords': row['score_keywords']
        },
        'max_breakdown': details.get('max_breakdown', {
            'structure': 20,
            'contact': 15,
            'achievements': 20,
            'metrics': 20,
            'formatting': 15,
            'readability': 15,
            'skills': 15
        }),
        'summary': row['summary'],
        'matched_keywords': json.loads(row['matched_keywords'] or '[]'),
        'missing_keywords': json.loads(row['missing_keywords'] or '[]'),
        'matched_skills': json.loads(row['matched_skills'] or '[]'),
        'missing_skills': json.loads(row['missing_skills'] or '[]'),
        'section_status': json.loads(row['section_status'] or '{}'),
        'contact_details': details.get('contact_details', {}),
        'formatting_details': details.get('formatting_details', {}),
        'achievements_details': details.get('achievements_details', {}),
        'readability_details': details.get('readability_details', {}),
        'action_verbs_found': details.get('action_verbs_found', 0),
        'quantified_metrics_found': details.get('quantified_metrics_found', 0),
        'suggestions': json.loads(row['suggestions'] or '[]'),
        'created_at': row['created_at']
    }

def get_user_analyses(user_email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM analyses WHERE user_email = ? ORDER BY created_at DESC
    ''', (user_email,))
    rows = cursor.fetchall()
    results = [_unpack_analysis_row(row) for row in rows]
    conn.close()
    return results

def get_analysis_by_id(analysis_id, user_email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM analyses WHERE id = ? AND user_email = ?
    ''', (analysis_id, user_email))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    res = _unpack_analysis_row(row)
    conn.close()
    return res

def delete_analysis(analysis_id, user_email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM analyses WHERE id = ? AND user_email = ?', (analysis_id, user_email))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def delete_all_analyses(user_email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM analyses WHERE user_email = ?', (user_email,))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def get_user_stats(user_email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            COUNT(*) as total_checked,
            AVG(overall_score) as avg_score,
            MAX(overall_score) as best_score,
            MAX(created_at) as last_analysis
        FROM analyses
        WHERE user_email = ?
    ''', (user_email,))
    row = cursor.fetchone()
    conn.close()
    
    total = row['total_checked'] if row and row['total_checked'] else 0
    avg = round(row['avg_score'], 1) if row and row['avg_score'] is not None else 0
    best = row['best_score'] if row and row['best_score'] is not None else 0
    last = row['last_analysis'] if row and row['last_analysis'] else None

    return {
        'total_checked': total,
        'avg_score': avg,
        'best_score': best,
        'last_analysis': last
    }

def get_or_create_user(email, name=None, password=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    if not user:
        name_val = name if name else email.split('@')[0].replace('.', ' ').title()
        pass_val = password if password else 'demo123'
        cursor.execute('''
            INSERT INTO users (email, name, password) VALUES (?, ?, ?)
        ''', (email, name_val, pass_val))
        conn.commit()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
    conn.close()
    return dict(user)

def update_user_profile(email, name, bio, target_role=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET name = ?, target_role = ?, bio = ? WHERE email = ?
    ''', (name, target_role or '', bio, email))
    conn.commit()
    conn.close()
    return True

def get_user_settings(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings WHERE user_email = ?', (email,))
    row = cursor.fetchone()
    if not row:
        cursor.execute('''
            INSERT INTO settings (user_email) VALUES (?)
        ''', (email,))
        conn.commit()
        cursor.execute('SELECT * FROM settings WHERE user_email = ?', (email,))
        row = cursor.fetchone()
    conn.close()
    return dict(row)

def update_user_settings(email, scoring_sensitivity, theme, email_alerts, auto_save):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO settings (user_email, scoring_sensitivity, theme, email_alerts, auto_save, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_email) DO UPDATE SET
            scoring_sensitivity=excluded.scoring_sensitivity,
            theme=excluded.theme,
            email_alerts=excluded.email_alerts,
            auto_save=excluded.auto_save,
            updated_at=CURRENT_TIMESTAMP
    ''', (email, scoring_sensitivity, theme, email_alerts, auto_save))
    conn.commit()
    conn.close()
    return True

# -----------------------------------------------------------------------------
# VERIFIED JOBS CATALOG & SEEDING
# -----------------------------------------------------------------------------

def seed_verified_jobs(cursor):
    """
    Seeds verified fresher tech jobs across Python, AI/ML, Data Analyst, and Web Developer roles.
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
- Design and implement backend web services and automation scripts using Python and Django.
- Work with relational databases such as MySQL and PostgreSQL.
- Interface with REST APIs and collaborate with frontend developers.
- Write unit tests and maintain high code quality standards.

Requirements:
- Strong proficiency in Python and core OOP principles.
- Familiarity with SQL databases, Git version control, and data structures.
- Academic projects or GitHub contributions demonstrating Python experience.
- B.E / B.Tech / MCA freshers (2025/2026 batch welcome).""",
            json.dumps(["Python", "SQL", "MySQL", "Git", "REST API", "Data Structures", "Django"]),
            "https://www.zoho.com/careers/",
            "Zoho Official Careers Portal",
            0,
            "2026-10-10"
        ),
        (
            "Associate Software Engineer (Python & Cloud)",
            "Cisco Systems India",
            "Bangalore, Karnataka",
            "Full-Time",
            "Fresher / Entry-Level",
            "₹9.0 - 12.0 LPA",
            """Cisco India is seeking Graduate Engineers for Python Backend & Cloud Development.

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
            2,
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
            2,
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
            0,
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
            json.dumps(["SQL", "Python", "Pandas", "Data Analysis", "Power BI", "Tableau", "Excel", "Statistics"]),
            "https://www.amazon.jobs/",
            "Amazon Jobs Portal",
            0,
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
            0,
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
            json.dumps(["JavaScript", "React", "HTML5", "CSS3", "Tailwind", "REST API", "Git", "TypeScript"]),
            "https://careers.freshworks.com/",
            "Freshworks Careers",
            0,
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
            json.dumps(["JavaScript", "React", "Node.js", "Python", "SQL", "HTML5", "CSS3", "Git", "REST API"]),
            "https://www.thoughtworks.com/careers",
            "Thoughtworks Global Careers",
            2,
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
            0,
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
- Deploy, maintain, and automate cloud backend services.
- Write Python scripts to automate routine operations and testing.
- Work with relational database systems and container technologies.

Requirements:
- B.E / B.Tech in CS/IT/ECE or related branches.
- Solid programming proficiency in Python, Linux fundamentals, and SQL.
- Basic understanding of cloud infrastructure (AWS/Azure/GCP).""",
            json.dumps(["Python", "Linux", "SQL", "Git", "AWS", "Cloud Computing", "Docker"]),
            "https://www.infosys.com/careers.html",
            "Infosys Careers",
            0,
            "2026-10-10"
        ),
        (
            "Software Engineering Intern (Summer 2026)",
            "Google India",
            "Bangalore / Hyderabad",
            "Internship",
            "Student / Fresher",
            "₹75,000 - 1,00,000 / month",
            """Google India is looking for Software Engineering Interns for our engineering teams.

Responsibilities:
- Build and optimize large-scale distributed systems and customer-facing products.
- Write readable, robust, and well-tested code in Python, C++, or Java.
- Collaborate with software engineers, designers, and product teams on challenging computer science problems.

Requirements:
- Currently pursuing a Bachelor's, Master's, or Dual Degree in Computer Science or related technical field.
- Experience with one or more general-purpose programming languages including Python, C++, or Java.
- Solid knowledge of Data Structures and Algorithms.""",
            json.dumps(["Python", "C++", "Java", "Data Structures", "Algorithms", "Git", "Problem Solving"]),
            "https://careers.google.com/",
            "Google Careers",
            2,
            "2026-10-15"
        ),
        (
            "Associate Cloud Developer",
            "IBM India",
            "Kochi / Bangalore",
            "Full-Time",
            "Entry-Level (0-1 yrs)",
            "₹5.0 - 7.2 LPA",
            """IBM Client Engineering is hiring Associate Cloud Developers.

Responsibilities:
- Build cloud-native microservices and deploy them into containerized environments.
- Develop RESTful APIs using Python and Node.js.
- Work with Docker, Kubernetes, and Linux environments.

Requirements:
- Degree in Computer Science, Software Engineering, or equivalent.
- Experience with Python or JavaScript, Git, and Linux.
- Hands-on interest in Docker and Cloud platforms.""",
            json.dumps(["Python", "Docker", "Kubernetes", "Linux", "Git", "REST API", "Cloud Computing"]),
            "https://www.ibm.com/careers/",
            "IBM Careers Portal",
            1,
            "2026-10-12"
        )
    ]

    cursor.executemany("""
        INSERT INTO jobs (
            title, company, location, job_type, experience_level,
            salary, description, required_skills, application_url, portal_name, is_remote, posted_date, is_verified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, verified_jobs)


# -----------------------------------------------------------------------------
# JOBS CATALOG & APPLICATIONS API FUNCTIONS
# -----------------------------------------------------------------------------

def get_all_jobs(search=None, skill=None, location=None, job_type=None, is_remote=None):
    """
    Retrieves jobs matching optional search and filter criteria.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if search:
        search_like = f"%{search.strip().lower()}%"
        query += " AND (LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(description) LIKE ? OR LOWER(required_skills) LIKE ?)"
        params.extend([search_like, search_like, search_like, search_like])

    if skill:
        skill_like = f"%{skill.strip().lower()}%"
        query += " AND LOWER(required_skills) LIKE ?"
        params.append(skill_like)

    if location:
        loc_like = f"%{location.strip().lower()}%"
        query += " AND LOWER(location) LIKE ?"
        params.append(loc_like)

    if job_type:
        query += " AND LOWER(job_type) = LOWER(?)"
        params.append(job_type.strip())

    if is_remote is not None:
        if str(is_remote).lower() in ('1', 'true', 'yes', 'remote'):
            query += " AND is_remote IN (1, 2)"  # remote or hybrid
        elif str(is_remote).lower() in ('0', 'false', 'onsite'):
            query += " AND is_remote = 0"

    query += " ORDER BY id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        item = _attach_job_meta(dict(row))
        result.append(item)
    return result


def _attach_job_meta(item):
    """
    Normalizes required_skills and attaches verified URLs for LinkedIn, Naukri, and Company Website.
    """
    if not item:
        return item

    try:
        if isinstance(item.get('required_skills'), str):
            item['required_skills'] = json.loads(item.get('required_skills') or '[]')
    except Exception:
        item['required_skills'] = []

    title = (item.get('title') or '').strip()
    company = (item.get('company') or '').strip()
    location = (item.get('location') or '').strip()
    primary_loc = location.split('/')[0].split('(')[0].strip() if location else ""

    # 1. LinkedIn Search / Direct URL
    if item.get('linkedin_url') and str(item['linkedin_url']).startswith('http'):
        item['linkedin_search_url'] = item['linkedin_url']
        item['linkedin_is_direct'] = True
    else:
        query_parts = [title]
        if company and len(company) <= 30:
            query_parts.append(company)
        params = {'keywords': ' '.join(query_parts)}
        if primary_loc:
            params['location'] = primary_loc
        item['linkedin_search_url'] = f"https://www.linkedin.com/jobs/search/?{urllib.parse.urlencode(params)}"
        item['linkedin_is_direct'] = False

    # 2. Naukri Search / Direct URL
    if item.get('naukri_url') and str(item['naukri_url']).startswith('http'):
        item['naukri_search_url'] = item['naukri_url']
        item['naukri_is_direct'] = True
    else:
        clean_slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
        n_params = {'k': title}
        if primary_loc:
            n_params['l'] = primary_loc
        if clean_slug:
            item['naukri_search_url'] = f"https://www.naukri.com/{clean_slug}-jobs?{urllib.parse.urlencode(n_params)}"
        else:
            item['naukri_search_url'] = f"https://www.naukri.com/jobs?{urllib.parse.urlencode(n_params)}"
        item['naukri_is_direct'] = False

    # 3. Company Application URL
    app_url = item.get('application_url') or ''
    has_company = bool(app_url and str(app_url).startswith('http'))
    item['has_company_url'] = has_company
    item['has_application_url'] = has_company
    item['company_application_url'] = app_url if has_company else None

    return item


def get_job_by_id(job_id):
    """
    Retrieves a single job by primary key.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return _attach_job_meta(dict(row))


def save_job_for_user(user_email, job_id):
    """
    Bookmark a job for a user in SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO saved_jobs (user_email, job_id) VALUES (?, ?)", (user_email, job_id))
        conn.commit()
        success = True
    except Exception:
        success = False
    finally:
        conn.close()
    return success


def unsave_job_for_user(user_email, job_id):
    """
    Remove a bookmarked job for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_jobs WHERE user_email = ? AND job_id = ?", (user_email, job_id))
    conn.commit()
    conn.close()
    return True


def get_saved_jobs_for_user(user_email):
    """
    Retrieve all bookmarked jobs for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.* FROM jobs j
        JOIN saved_jobs s ON j.id = s.job_id
        WHERE s.user_email = ?
        ORDER BY s.created_at DESC
    """, (user_email,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append(_attach_job_meta(dict(row)))
    return result



def record_job_application(user_email, job_id, job_title, company, application_url, status='Applied', applied_date=None, notes=''):
    """
    Records an application in the application tracker.
    Distinguishes user-recorded application from automated verification.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    date_val = applied_date if applied_date else datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
        INSERT INTO job_applications (
            user_email, job_id, job_title, company, application_url, status, applied_date, notes, is_verified_application
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (user_email, job_id, job_title, company, application_url, status, date_val, notes))
    app_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return app_id


def get_user_job_applications(user_email):
    """
    Gets all tracked applications for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM job_applications
        WHERE user_email = ?
        ORDER BY created_at DESC
    """, (user_email,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_application_status(app_id, user_email, status, notes=None):
    """
    Updates application status (Saved, Applied, Interview, Rejected, Offer) or notes.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    if notes is not None:
        cursor.execute("""
            UPDATE job_applications
            SET status = ?, notes = ?
            WHERE id = ? AND user_email = ?
        """, (status, notes, app_id, user_email))
    else:
        cursor.execute("""
            UPDATE job_applications
            SET status = ?
            WHERE id = ? AND user_email = ?
        """, (status, app_id, user_email))
    conn.commit()
    conn.close()
    return True


def delete_job_application(app_id, user_email):
    """
    Deletes an application record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_applications WHERE id = ? AND user_email = ?", (app_id, user_email))
    conn.commit()
    conn.close()
    return True

