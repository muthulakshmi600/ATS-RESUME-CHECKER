"""
Applicant Tracking System (ATS) Web Application
Built with Flask, SQLite, Pandas, Scikit-learn, PyPDF2, and python-docx.

This application provides:
1. Job description management
2. PDF & DOCX resume upload and automatic text extraction
3. Transparent resume matching using TF-IDF and Cosine Similarity
4. Skill matching (matched skills vs missing skills)
5. Recruiter candidate dashboard with status management (Reviewing, Shortlisted, Rejected)
6. Search and filter capabilities
"""

import os
import re
import json
import sqlite3
from datetime import datetime
import csv
import io
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, send_from_directory, abort, Response
)

# Text processing & Machine Learning libraries
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Resume text extraction libraries
import PyPDF2
import docx

# Initialize Flask application
app = Flask(__name__)
app.secret_key = "ats_secret_key_beginner_friendly_recruiter_app"

# Configuration paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE = os.path.join(BASE_DIR, "ats.db")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# Ensure the uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================================
# Database Helpers & Initialization
# =====================================================================

def get_db():
    """Establish and return a connection to the SQLite database with concurrency support."""
    conn = sqlite3.connect(DATABASE, timeout=30.0)
    conn.row_factory = sqlite3.Row  # Access columns by name: row['column_name']
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    """Create the SQLite database tables if they do not exist and apply schema migrations."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Table 1: Jobs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                experience_level TEXT DEFAULT 'Junior / Mid Level',
                job_type TEXT DEFAULT 'Full-time',
                salary_range TEXT DEFAULT 'Competitive',
                min_score_threshold INTEGER DEFAULT 40,
                status TEXT DEFAULT 'Active',
                required_skills TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Schema migration check for existing jobs table
        cursor.execute("PRAGMA table_info(jobs)")
        existing_cols = [row["name"] for row in cursor.fetchall()]
        
        migrations = [
            ("experience_level", "TEXT DEFAULT 'Junior / Mid Level'"),
            ("job_type", "TEXT DEFAULT 'Full-time'"),
            ("salary_range", "TEXT DEFAULT 'Competitive'"),
            ("min_score_threshold", "INTEGER DEFAULT 40"),
            ("status", "TEXT DEFAULT 'Active'"),
            ("required_skills", "TEXT DEFAULT '[]'")
        ]
        for col_name, col_type in migrations:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}")
                
        # Table 2: Candidates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                filename TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                job_id INTEGER NOT NULL,
                match_percentage REAL NOT NULL,
                matched_skills TEXT,   -- stored as JSON list string
                missing_skills TEXT,   -- stored as JSON list string
                status TEXT DEFAULT 'Reviewing', -- 'Reviewing', 'Shortlisted', 'Rejected'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
            )
        """)
        conn.commit()


# =====================================================================
# File Validation & Text Extraction
# =====================================================================

def allowed_file(filename):
    """Check if the uploaded file has a supported extension (.pdf or .docx)."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):
    """
    Extract text content from a PDF file using PyPDF2.
    Loops through every page and appends clean text.
    """
    text_content = []
    try:
        with open(filepath, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_index, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        return "\n".join(text_content).strip()
    except Exception as e:
        print(f"Error reading PDF file {filepath}: {e}")
        return ""


def extract_text_from_docx(filepath):
    """
    Extract text content from a Microsoft Word (.docx) file using python-docx.
    Reads both paragraph text and text inside tables.
    """
    text_content = []
    try:
        doc = docx.Document(filepath)
        # Extract from paragraphs
        for p in doc.paragraphs:
            if p.text.strip():
                text_content.append(p.text.strip())
        # Extract from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_content.append(cell.text.strip())
        return "\n".join(text_content).strip()
    except Exception as e:
        print(f"Error reading DOCX file {filepath}: {e}")
        return ""


def extract_resume_text(filepath, filename):
    """Detect file type and extract text safely."""
    extension = filename.rsplit(".", 1)[1].lower()
    if extension == "pdf":
        return extract_text_from_pdf(filepath)
    elif extension == "docx":
        return extract_text_from_docx(filepath)
    return ""


def clean_text(text):
    """
    Normalize text for keyword search and display.
    Replaces extra whitespace and standardizes line breaks.
    """
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =====================================================================
# Skills & TF-IDF Matching Engine (Transparent NLP, No Fake AI)
# =====================================================================

# Comprehensive common skills library for technical and general recruitment
KNOWN_SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "c", "ruby", "php", "go", "rust", "r", "swift", "kotlin",
    # Web Frameworks & Libraries
    "flask", "django", "fastapi", "react", "angular", "vue", "node.js", "express", "html", "html5", "css", "css3",
    "bootstrap", "tailwind", "jquery", "rest api", "graphql", "jinja",
    # Databases & Storage
    "sql", "sqlite", "mysql", "postgresql", "mongodb", "redis", "oracle", "nosql",
    # Data Science & Machine Learning
    "pandas", "numpy", "scikit-learn", "scipy", "matplotlib", "seaborn", "tensorflow", "keras", "pytorch",
    "data analysis", "machine learning", "deep learning", "nlp", "computer vision", "statistics",
    # Cloud & DevOps
    "git", "github", "gitlab", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "ci/cd", "jenkins", "terraform",
    # Core Engineering & Soft Skills
    "object-oriented programming", "oop", "data structures", "algorithms", "unit testing", "debugging",
    "problem solving", "agile", "scrum", "communication", "leadership", "teamwork"
]


def extract_skills_from_text(text):
    """
    Extract skills present in given text by searching for known skills.
    Uses regex word boundaries so 'c' doesn't match every single word containing 'c'.
    """
    found_skills = set()
    text_lower = text.lower()
    
    for skill in KNOWN_SKILLS:
        # Match multi-word or special symbols carefully
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text_lower):
            # Display cleanly capitalized
            found_skills.add(skill.title() if len(skill) > 3 else skill.upper())
            
    return found_skills


def match_resume_with_job(resume_text, job_description):
    """
    Transparently compares a candidate's resume with the job description.
    
    Methodology:
    1. TF-IDF (Term Frequency - Inverse Document Frequency) converts texts into vectors of word weights.
       - Common English stop words are filtered out.
       - 1-gram and 2-gram (phrases like 'rest api', 'machine learning') are weighted.
    2. Cosine Similarity calculates the angle between the two vectors:
       - Returns a score between 0.0 (no overlap) and 1.0 (identical terms).
       - Multiplied by 100 to get a transparent match percentage (0% to 100%).
    3. Keyword and Skill Overlap:
       - Detects skills required in the job description.
       - Categorizes them into 'Matched Skills' and 'Missing Skills'.
    """
    if not resume_text.strip() or not job_description.strip():
        return 0.0, [], []
    
    # 1. TF-IDF Vectorization and Cosine Similarity
    corpus = [job_description, resume_text]
    
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        lowercase=True
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        # Cosine similarity between job description (index 0) and resume (index 1)
        sim_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        match_percentage = round(float(sim_score) * 100, 1)
    except Exception as e:
        print(f"Error calculating TF-IDF similarity: {e}")
        match_percentage = 0.0

    # 2. Skill Comparison
    job_skills = extract_skills_from_text(job_description)
    resume_skills = extract_skills_from_text(resume_text)
    
    # Matched = Skills in Job Description that ARE present in Resume
    matched_skills = sorted(list(job_skills.intersection(resume_skills)))
    
    # Missing = Skills in Job Description that ARE NOT present in Resume
    missing_skills = sorted(list(job_skills.difference(resume_skills)))
    
    # 3. Transparent Combined Match Score:
    # 50% weighting on TF-IDF Cosine Similarity (document vocabulary overlap)
    # 50% weighting on Skill Coverage (percentage of required job skills present in resume)
    tfidf_score = match_percentage
    if job_skills:
        skill_score = round((len(matched_skills) / len(job_skills)) * 100, 1)
        final_score = round((0.5 * tfidf_score) + (0.5 * skill_score), 1)
    else:
        final_score = tfidf_score
        
    return final_score, matched_skills, missing_skills


# =====================================================================
# Colorful Target Job Roles Engine
# =====================================================================

def get_job_role_style(job_title):
    """
    Returns vibrant, distinct visual theme, badge class, color, and category
    for any job title to make target job roles visually rich and colorful.
    """
    title_lower = (job_title or "").lower()
    
    if any(k in title_lower for k in ["python", "django", "flask", "backend"]):
        return {
            "class_name": "role-badge-python",
            "category": "Python / Backend",
            "color": "#1d4ed8",
            "bg": "#eff6ff",
            "border": "#93c5fd",
            "gradient": "linear-gradient(135deg, #1e40af, #3b82f6)",
            "icon": "code"
        }
    elif any(k in title_lower for k in ["data", "machine learning", "ai", "scientist", "analyst"]):
        return {
            "class_name": "role-badge-data",
            "category": "AI & Data Science",
            "color": "#6d28d9",
            "bg": "#f5f3ff",
            "border": "#c4b5fd",
            "gradient": "linear-gradient(135deg, #6d28d9, #8b5cf6)",
            "icon": "chart"
        }
    elif any(k in title_lower for k in ["front", "react", "vue", "angular", "web", "javascript", "fullstack", "full stack"]):
        return {
            "class_name": "role-badge-frontend",
            "category": "Web & Fullstack",
            "color": "#047857",
            "bg": "#ecfdf5",
            "border": "#a7f3d0",
            "gradient": "linear-gradient(135deg, #047857, #10b981)",
            "icon": "layout"
        }
    elif any(k in title_lower for k in ["devops", "cloud", "aws", "docker", "kubernetes", "infra", "sre"]):
        return {
            "class_name": "role-badge-devops",
            "category": "Cloud & DevOps",
            "color": "#0e7490",
            "bg": "#ecfeff",
            "border": "#a5f3fc",
            "gradient": "linear-gradient(135deg, #0e7490, #06b6d4)",
            "icon": "cloud"
        }
    elif any(k in title_lower for k in ["qa", "test", "quality", "automation"]):
        return {
            "class_name": "role-badge-qa",
            "category": "QA & Automation",
            "color": "#b45309",
            "bg": "#fffbeb",
            "border": "#fde68a",
            "gradient": "linear-gradient(135deg, #b45309, #f59e0b)",
            "icon": "check"
        }
    elif any(k in title_lower for k in ["mobile", "android", "ios", "flutter"]):
        return {
            "class_name": "role-badge-mobile",
            "category": "Mobile Engineering",
            "color": "#be123c",
            "bg": "#fff1f2",
            "border": "#fecdd3",
            "gradient": "linear-gradient(135deg, #be123c, #f43f5e)",
            "icon": "device"
        }
    elif any(k in title_lower for k in ["marketing", "seo", "sales", "brand", "content"]):
        return {
            "class_name": "role-badge-marketing",
            "category": "Marketing & Growth",
            "color": "#c2410c",
            "bg": "#fff7ed",
            "border": "#fed7aa",
            "gradient": "linear-gradient(135deg, #c2410c, #ea580c)",
            "icon": "spark"
        }
    else:
        return {
            "class_name": "role-badge-general",
            "category": "Software Engineering",
            "color": "#334155",
            "bg": "#f8fafc",
            "border": "#cbd5e1",
            "gradient": "linear-gradient(135deg, #334155, #64748b)",
            "icon": "terminal"
        }


# =====================================================================
# Missing Skills Intelligence & Learning Roadmaps Knowledge Base
# =====================================================================

SKILL_KNOWLEDGE_BASE = {
    "Docker": {
        "priority": "Important",
        "topics": "Containers, Dockerfile, image layering, docker-compose, and volume mounts.",
        "est_time": "4-6 hours",
        "interview_question": "Have you worked with containerized microservices or Dockerfile creation? How would you containerize a web application?"
    },
    "Kubernetes": {
        "priority": "Important",
        "topics": "Pods, Deployments, Services, ConfigMaps, and cluster orchestration.",
        "est_time": "8-10 hours",
        "interview_question": "Can you explain how a Kubernetes Deployment manages replicas and handles rolling updates?"
    },
    "AWS": {
        "priority": "Important",
        "topics": "EC2 virtual instances, S3 object storage, IAM security roles, and RDS databases.",
        "est_time": "6-8 hours",
        "interview_question": "Which AWS cloud services have you interacted with, and how do you handle secret credentials securely in the cloud?"
    },
    "Azure": {
        "priority": "Important",
        "topics": "Azure App Services, Blob Storage, Azure SQL, and Entra ID authentication.",
        "est_time": "6-8 hours",
        "interview_question": "What experience do you have deploying web services to Microsoft Azure?"
    },
    "Gcp": {
        "priority": "Important",
        "topics": "Google Cloud Run, Compute Engine, Cloud Storage, and BigQuery.",
        "est_time": "6-8 hours",
        "interview_question": "How have you deployed serverless container apps using Google Cloud Run or GCF?"
    },
    "Linux": {
        "priority": "Important",
        "topics": "Shell scripting (Bash), file permissions (chmod/chown), process management, and SSH.",
        "est_time": "4-5 hours",
        "interview_question": "How comfortable are you managing servers, inspecting logs, and configuring systemd services over SSH?"
    },
    "Ci/Cd": {
        "priority": "Important",
        "topics": "GitHub Actions, automated testing pipelines, build stages, and release tags.",
        "est_time": "3-5 hours",
        "interview_question": "How do you set up an automated CI workflow that runs unit tests before code merges to main?"
    },
    "Python": {
        "priority": "Critical",
        "topics": "Core data structures (lists, dicts, sets), OOP, decorators, generators, and exception handling.",
        "est_time": "12-15 hours",
        "interview_question": "Explain how Python manages memory, difference between deep and shallow copies, or generator functions."
    },
    "Flask": {
        "priority": "Critical",
        "topics": "Application factories, Blueprint routing, request/response cycle, Jinja2 templating, and SQLAlchemy/SQLite.",
        "est_time": "6-8 hours",
        "interview_question": "How do you structure larger Flask apps using Blueprints, and how do you manage database connections?"
    },
    "Django": {
        "priority": "Critical",
        "topics": "MVT architecture, Django ORM querysets, migration management, and built-in Admin panel.",
        "est_time": "10-12 hours",
        "interview_question": "How does Django ORM prevent N+1 queries, and how do you customize Django admin models?"
    },
    "Fastapi": {
        "priority": "Critical",
        "topics": "Async def routes, Pydantic data schemas, dependency injection, and automatic OpenAPI docs.",
        "est_time": "5-7 hours",
        "interview_question": "What are the performance benefits of FastAPI's async endpoints and Pydantic validation?"
    },
    "Sql": {
        "priority": "Critical",
        "topics": "INNER/LEFT JOINs, GROUP BY aggregations, indexes, subqueries, and transaction ACID properties.",
        "est_time": "6-8 hours",
        "interview_question": "How would you optimize a slow SQL query with multiple JOINs on large tables?"
    },
    "Sqlite": {
        "priority": "Important",
        "topics": "Single-file relational database engine, connection locking, and embedded persistence.",
        "est_time": "2-3 hours",
        "interview_question": "What are the advantages and concurrency limitations of SQLite compared to client-server RDBMS?"
    },
    "Postgresql": {
        "priority": "Critical",
        "topics": "ACID compliance, JSONB columns, connection pooling, and execution EXPLAIN plans.",
        "est_time": "6-8 hours",
        "interview_question": "When would you choose PostgreSQL over MySQL or MongoDB, and how do you use EXPLAIN ANALYZE?"
    },
    "Javascript": {
        "priority": "Critical",
        "topics": "ES6+ syntax, Promises, async/await, DOM manipulation, and Event Loop.",
        "est_time": "8-10 hours",
        "interview_question": "Explain the JavaScript event loop and the difference between microtasks and macrotasks."
    },
    "React": {
        "priority": "Critical",
        "topics": "Functional components, Hooks (useState, useEffect, useMemo), state management, and Virtual DOM.",
        "est_time": "10-12 hours",
        "interview_question": "What causes unnecessary component re-renders in React, and how does useMemo/useCallback mitigate them?"
    },
    "Html": {
        "priority": "Core",
        "topics": "Semantic HTML5 tags, accessibility (ARIA), form validation, and SEO best practices.",
        "est_time": "2-3 hours",
        "interview_question": "Why is semantic HTML important for accessibility and SEO compared to generic div tags?"
    },
    "Html5": {
        "priority": "Core",
        "topics": "Semantic HTML5 tags, accessibility (ARIA), form validation, and modern web storage.",
        "est_time": "2-3 hours",
        "interview_question": "What HTML5 semantic elements do you prioritize for screen-reader and SEO optimization?"
    },
    "Css": {
        "priority": "Core",
        "topics": "Flexbox, CSS Grid, media queries, CSS variables, and modern responsive layouts.",
        "est_time": "4-5 hours",
        "interview_question": "When do you reach for CSS Grid versus Flexbox, and how do you handle responsive breakpoints?"
    },
    "Css3": {
        "priority": "Core",
        "topics": "Flexbox, Grid, transitions, CSS custom properties (variables), and responsive design.",
        "est_time": "4-5 hours",
        "interview_question": "How do you leverage CSS custom variables to implement theme switching and clean layouts?"
    },
    "Git": {
        "priority": "Critical",
        "topics": "Branching, merge vs rebase, resolving merge conflicts, git stash, and commit conventions.",
        "est_time": "3-4 hours",
        "interview_question": "How do you resolve a complex merge conflict, and what is the difference between git merge and git rebase?"
    },
    "Github": {
        "priority": "Important",
        "topics": "Pull request workflows, GitHub Actions, issues, code reviews, and release management.",
        "est_time": "2-3 hours",
        "interview_question": "What branch protection rules and code review practices do you recommend on GitHub?"
    },
    "Pandas": {
        "priority": "Critical",
        "topics": "DataFrames, groupby aggregations, merge/join, handling missing values, and vectorized operations.",
        "est_time": "6-8 hours",
        "interview_question": "Why should you avoid iterating over Pandas DataFrame rows with for-loops in production code?"
    },
    "Numpy": {
        "priority": "Important",
        "topics": "Ndarray broadcasting, matrix math, boolean masking, and fast numerical computing.",
        "est_time": "4-5 hours",
        "interview_question": "Explain NumPy array broadcasting rules with an example."
    },
    "Scikit-Learn": {
        "priority": "Critical",
        "topics": "Pipelines, TF-IDF vectorizers, train_test_split, cross-validation, and metrics (F1, Precision, Recall).",
        "est_time": "8-10 hours",
        "interview_question": "How do you prevent data leakage when scaling features or calculating TF-IDF in cross-validation?"
    },
    "Machine Learning": {
        "priority": "Critical",
        "topics": "Supervised vs unsupervised learning, bias-variance tradeoff, overfitting prevention, and hyperparameter tuning.",
        "est_time": "15-20 hours",
        "interview_question": "How do you detect overfitting in a machine learning model, and what techniques do you use to resolve it?"
    },
    "Rest Api": {
        "priority": "Critical",
        "topics": "HTTP methods (GET, POST, PUT, DELETE), status codes (200, 201, 400, 404, 500), idempotency, and JSON payloads.",
        "est_time": "4-5 hours",
        "interview_question": "What is the difference between PUT and PATCH in RESTful API design?"
    },
    "Unit Testing": {
        "priority": "Important",
        "topics": "pytest / unittest, mocking dependencies, test coverage, and edge-case testing.",
        "est_time": "4-6 hours",
        "interview_question": "How do you write unit tests for code that talks to an external third-party API or database?"
    },
    "Object-Oriented Programming": {
        "priority": "Core",
        "topics": "Inheritance, encapsulation, polymorphism, abstraction, and SOLID design principles.",
        "est_time": "5-6 hours",
        "interview_question": "Explain the Single Responsibility Principle and Open-Closed Principle with practical examples."
    },
    "Oop": {
        "priority": "Core",
        "topics": "Classes, methods, inheritance, composition vs inheritance, and design patterns.",
        "est_time": "4-5 hours",
        "interview_question": "When would you favor object composition over class inheritance?"
    },
    "Debugging": {
        "priority": "Core",
        "topics": "Interactive debuggers (pdb), breakpoint inspection, reading stack traces, and logging best practices.",
        "est_time": "2-3 hours",
        "interview_question": "Walk me through your thought process when diagnosing an intermittent production 500 error."
    },
    "Agile": {
        "priority": "Secondary",
        "topics": "Scrum sprints, daily standups, backlog grooming, retrospective meetings, and user stories.",
        "est_time": "2 hours",
        "interview_question": "How do you estimate user story points and handle scope creep during a 2-week sprint?"
    },
    "Communication": {
        "priority": "Core",
        "topics": "Technical documentation, asynchronous team messaging, stakeholder demos, and constructive code reviews.",
        "est_time": "Continuous",
        "interview_question": "Describe a time you had to explain a complex technical trade-off to a non-technical stakeholder."
    }
}


def get_skill_details(skill_name, job_title=""):
    """
    Returns comprehensive metadata for a skill, including priority classification,
    learning roadmap topics, estimated study time, and suggested screening questions.
    """
    cleaned_name = skill_name.strip()
    # Direct match or case-insensitive match
    entry = SKILL_KNOWLEDGE_BASE.get(cleaned_name)
    if not entry:
        for k, v in SKILL_KNOWLEDGE_BASE.items():
            if k.lower() == cleaned_name.lower():
                entry = v
                break
                
    if entry:
        priority = entry["priority"]
        topics = entry["topics"]
        est_time = entry["est_time"]
        question = entry["interview_question"]
    else:
        # Smart dynamic fallback for custom keywords
        is_core = any(word in (job_title or "").lower() for word in cleaned_name.lower().split())
        priority = "Critical" if is_core else "Important"
        topics = f"Foundational concepts, syntax patterns, practical architecture, and hands-on projects in {cleaned_name}."
        est_time = "4-6 hours"
        question = f"Could you describe your exposure to {cleaned_name} and how quickly you could ramp up on it?"
        
    return {
        "name": cleaned_name,
        "priority": priority,
        "priority_class": "badge-critical" if priority in ["Critical", "Core"] else "badge-important",
        "topics": topics,
        "est_time": est_time,
        "interview_question": question
    }


def generate_candidate_feedback(candidate_name, job_title, matched_skills, missing_skills):
    """
    Generates a constructive, professional candidate feedback email
    that highlights matched strengths and provides concrete upskilling advice.
    """
    matched_str = ", ".join(matched_skills[:8]) if matched_skills else "general experience"
    
    advice_lines = []
    for skill in missing_skills[:4]:
        info = get_skill_details(skill, job_title)
        advice_lines.append(f"- {skill} ({info['priority']}): Focus on {info['topics']} (~{info['est_time']})")
        
    advice_str = "\n".join(advice_lines) if advice_lines else "- Continue building projects aligning with our tech stack."
    
    feedback = f"""Subject: Update on your application for {job_title} at Our Team

Dear {candidate_name},

Thank you for your interest in the {job_title} position and for taking the time to share your resume with us.

We were very impressed by your demonstrated strengths in:
{matched_str}

To help you grow and make your profile even more competitive for roles like this in the future, our technical screening team identified a few skill areas worth strengthening:
{advice_str}

We strongly believe in continuous learning and encourage you to explore these topics and keep in touch for future opportunities that match your growing skill set.

Best regards,
Hiring & Talent Acquisition Team"""
    return feedback


# Register Jinja context helpers and filters
@app.template_filter("job_style")
def filter_job_style(title):
    return get_job_role_style(title)


@app.template_filter("skill_info")
def filter_skill_info(skill, job_title=""):
    return get_skill_details(skill, job_title)


# =====================================================================
# Routes & Controllers
# =====================================================================

@app.route("/")
def index():
    """Home / Dashboard view displaying key ATS statistics and recent candidates."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Summary KPI statistics
        cursor.execute("SELECT COUNT(*) FROM candidates")
        total_candidates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM candidates WHERE status = 'Shortlisted'")
        shortlisted_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM candidates WHERE status = 'Reviewing'")
        reviewing_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM candidates WHERE status = 'Rejected'")
        rejected_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        
        # Recent 5 candidates
        cursor.execute("""
            SELECT c.*, j.title AS job_title
            FROM candidates c
            JOIN jobs j ON c.job_id = j.id
            ORDER BY c.id DESC
            LIMIT 5
        """)
        recent_candidates = cursor.fetchall()
        
        # Process JSON skills strings and add colorful role styles
        processed_candidates = []
        for c in recent_candidates:
            c_dict = dict(c)
            c_dict["matched_skills"] = json.loads(c_dict["matched_skills"] or "[]")
            c_dict["missing_skills"] = json.loads(c_dict["missing_skills"] or "[]")
            c_dict["role_style"] = get_job_role_style(c_dict["job_title"])
            c_dict["missing_skills_detailed"] = [get_skill_details(s, c_dict["job_title"]) for s in c_dict["missing_skills"]]
            processed_candidates.append(c_dict)
            
        # Recent jobs list with role styles
        cursor.execute("""
            SELECT j.*, COUNT(c.id) AS candidate_count
            FROM jobs j
            LEFT JOIN candidates c ON j.id = c.job_id
            GROUP BY j.id
            ORDER BY j.id DESC
            LIMIT 4
        """)
        raw_jobs = cursor.fetchall()
        recent_jobs = []
        for r in raw_jobs:
            jd = dict(r)
            jd["role_style"] = get_job_role_style(jd["title"])
            recent_jobs.append(jd)

    return render_template(
        "index.html",
        total_candidates=total_candidates,
        shortlisted_count=shortlisted_count,
        reviewing_count=reviewing_count,
        rejected_count=rejected_count,
        total_jobs=total_jobs,
        recent_candidates=processed_candidates,
        recent_jobs=recent_jobs
    )


@app.route("/job", methods=["GET", "POST"])
def job_page():
    """Manage job postings: enter job title, metadata, requirements, and list all active jobs with analytics."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        experience_level = request.form.get("experience_level", "Junior / Mid Level").strip()
        job_type = request.form.get("job_type", "Full-time").strip()
        salary_range = request.form.get("salary_range", "Competitive").strip()
        min_score_threshold = int(request.form.get("min_score_threshold", 40) or 40)
        
        if not title or not description:
            flash("Please provide both a job title and job description.", "danger")
            return redirect(url_for("job_page"))
            
        # Automatically detect required technical skills from the job description
        extracted_skills = sorted(list(extract_skills_from_text(description)))
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO jobs (title, description, experience_level, job_type, salary_range, min_score_threshold, status, required_skills)
                VALUES (?, ?, ?, ?, ?, ?, 'Active', ?)
            """, (title, description, experience_level, job_type, salary_range, min_score_threshold, json.dumps(extracted_skills)))
            conn.commit()
            
        flash(f"Job opening '{title}' created with {len(extracted_skills)} auto-detected skills!", "success")
        return redirect(url_for("job_page"))
    
    # GET: display job creation form and all current jobs with analytics & funnel metrics
    status_filter = request.args.get("status", "All")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT j.*, 
                   COUNT(c.id) AS candidate_count,
                   AVG(c.match_percentage) AS avg_match,
                   MAX(c.match_percentage) AS top_score,
                   SUM(CASE WHEN c.status = 'Shortlisted' THEN 1 ELSE 0 END) AS shortlisted_count,
                   SUM(CASE WHEN c.status = 'Reviewing' THEN 1 ELSE 0 END) AS reviewing_count,
                   SUM(CASE WHEN c.status = 'Rejected' THEN 1 ELSE 0 END) AS rejected_count
            FROM jobs j
            LEFT JOIN candidates c ON j.id = c.job_id
            GROUP BY j.id
            ORDER BY j.id DESC
        """)
        raw_jobs = cursor.fetchall()
        
        all_jobs = []
        active_count = 0
        paused_count = 0
        closed_count = 0
        
        for r in raw_jobs:
            jd = dict(r)
            jd["avg_match"] = round(jd["avg_match"] or 0.0, 1)
            jd["top_score"] = round(jd["top_score"] or 0.0, 1)
            jd["role_style"] = get_job_role_style(jd["title"])
            jd["required_skills"] = json.loads(jd.get("required_skills") or "[]")
            
            # Count statuses
            if jd["status"] == "Active":
                active_count += 1
            elif jd["status"] == "Paused":
                paused_count += 1
            elif jd["status"] == "Closed":
                closed_count += 1
            
            # Fetch top candidate name if any
            if jd["candidate_count"] > 0:
                cursor.execute("""
                    SELECT name, match_percentage FROM candidates 
                    WHERE job_id = ? ORDER BY match_percentage DESC LIMIT 1
                """, (jd["id"],))
                top_cand = cursor.fetchone()
                jd["top_candidate"] = dict(top_cand) if top_cand else None
            else:
                jd["top_candidate"] = None
                
            all_jobs.append(jd)
            
        # Filter if requested
        if status_filter != "All":
            filtered_jobs = [j for j in all_jobs if j["status"] == status_filter]
        else:
            filtered_jobs = all_jobs
            
        status_counts = {
            "All": len(all_jobs),
            "Active": active_count,
            "Paused": paused_count,
            "Closed": closed_count
        }
        
    return render_template("job.html", jobs=filtered_jobs, status_counts=status_counts, current_status=status_filter)


@app.route("/job/<int:job_id>")
def job_detail_page(job_id):
    """Dedicated Target Job page showing complete requirements, talent pool skill gap heatmap, top candidate spotlight, and ranked pipeline."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job_row = cursor.fetchone()
        
        if not job_row:
            flash("Target Job not found.", "danger")
            return redirect(url_for("job_page"))
            
        job = dict(job_row)
        job["role_style"] = get_job_role_style(job["title"])
        job["required_skills"] = json.loads(job.get("required_skills") or "[]")
        
        # Query candidates for this job ranked by match score
        cursor.execute("""
            SELECT * FROM candidates 
            WHERE job_id = ? 
            ORDER BY match_percentage DESC, id DESC
        """, (job_id,))
        cands_raw = cursor.fetchall()
        candidates = []
        shortlisted_cnt = 0
        reviewing_cnt = 0
        rejected_cnt = 0
        score_sum = 0
        
        for r in cands_raw:
            c = dict(r)
            c["matched_skills"] = json.loads(c["matched_skills"] or "[]")
            c["missing_skills"] = json.loads(c["missing_skills"] or "[]")
            c["role_style"] = job["role_style"]
            c["missing_skills_detailed"] = [get_skill_details(s, job["title"]) for s in c["missing_skills"]]
            if c["status"] == "Shortlisted": shortlisted_cnt += 1
            elif c["status"] == "Reviewing": reviewing_cnt += 1
            elif c["status"] == "Rejected": rejected_cnt += 1
            score_sum += c["match_percentage"]
            candidates.append(c)
            
        job["candidate_count"] = len(candidates)
        job["shortlisted_count"] = shortlisted_cnt
        job["reviewing_count"] = reviewing_cnt
        job["rejected_count"] = rejected_cnt
        job["avg_match"] = round(score_sum / len(candidates), 1) if candidates else 0.0
        
        # Talent Pool Skill Gap & Coverage Analysis
        talent_pool_skills = []
        num_candidates = len(candidates)
        for skill in job["required_skills"]:
            present_in = sum(1 for c in candidates if skill in c["matched_skills"])
            cov_pct = round((present_in / num_candidates * 100), 1) if num_candidates > 0 else 0.0
            is_gap = cov_pct < 50.0
            talent_pool_skills.append({
                "name": skill,
                "count": present_in,
                "total": num_candidates,
                "coverage_pct": cov_pct,
                "is_gap": is_gap
            })
            
        # Sort skills: skill gaps first so recruiters spot missing talent instantly
        talent_pool_skills.sort(key=lambda x: (not x["is_gap"], x["coverage_pct"]))
        
        # Top Candidate Spotlight
        top_candidate = None
        if candidates:
            top_candidate = candidates[0]
            top_candidate["is_qualified"] = top_candidate["match_percentage"] >= job["min_score_threshold"]
            top_candidate["diff_threshold"] = round(top_candidate["match_percentage"] - job["min_score_threshold"], 1)
            
        # Funnel Percentages for Visual Progress Bar
        funnel = {
            "shortlisted_pct": round(shortlisted_cnt / num_candidates * 100, 1) if num_candidates else 0.0,
            "reviewing_pct": round(reviewing_cnt / num_candidates * 100, 1) if num_candidates else 0.0,
            "rejected_pct": round(rejected_cnt / num_candidates * 100, 1) if num_candidates else 0.0
        }

    return render_template(
        "job_detail.html", 
        job=job, 
        candidates=candidates, 
        talent_pool_skills=talent_pool_skills, 
        top_candidate=top_candidate,
        funnel=funnel
    )


@app.route("/job/<int:job_id>/export")
def export_job_candidates(job_id):
    """Export all candidates for a target job opening as a clean CSV file."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job_row = cursor.fetchone()
        if not job_row:
            flash("Target Job not found.", "danger")
            return redirect(url_for("job_page"))
            
        job = dict(job_row)
        cursor.execute("""
            SELECT * FROM candidates 
            WHERE job_id = ? 
            ORDER BY match_percentage DESC, id DESC
        """, (job_id,))
        candidates = cursor.fetchall()
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Candidate Name", "Email", "Phone", 
        "Match Score (%)", "Hiring Bar Threshold (%)", "Hiring Bar Status", 
        "Application Status", "Matched Skills", "Missing Skills", "Application Date"
    ])
    
    for idx, c_row in enumerate(candidates, 1):
        c = dict(c_row)
        matched = ", ".join(json.loads(c.get("matched_skills") or "[]"))
        missing = ", ".join(json.loads(c.get("missing_skills") or "[]"))
        bar_status = "Qualified" if c["match_percentage"] >= job["min_score_threshold"] else "Under Bar"
        writer.writerow([
            idx,
            c["name"],
            c["email"] or "N/A",
            c["phone"] or "N/A",
            c["match_percentage"],
            job["min_score_threshold"],
            bar_status,
            c["status"],
            matched,
            missing,
            c["created_at"]
        ])
        
    output.seek(0)
    clean_title = re.sub(r'[^a-zA-Z0-9_-]', '_', job['title']).lower()
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=target_job_{job_id}_{clean_title}_candidates.csv"}
    )


@app.route("/job/status/<int:job_id>", methods=["POST"])
def update_job_status(job_id):
    """Toggle target job opening status: Active, Paused, or Closed."""
    new_status = request.form.get("status", "Active")
    if new_status in ["Active", "Paused", "Closed"]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))
            conn.commit()
        flash(f"Job status updated to '{new_status}'.", "success")
    return redirect(request.referrer or url_for("job_page"))


@app.route("/job/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    """Delete a job posting and its associated candidates."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()
    flash("Job posting deleted.", "info")
    return redirect(url_for("job_page"))


@app.route("/upload", methods=["GET", "POST"])
def upload_page():
    """
    Resume upload controller.
    Extracts text from PDF/DOCX, matches with selected job description,
    saves candidate record to SQLite, and displays enriched results preview.
    """
    selected_job_id = request.args.get("job_id", "")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, min_score_threshold FROM jobs WHERE status != 'Closed' ORDER BY id DESC")
        raw_jobs = cursor.fetchall()
        jobs = []
        for j in raw_jobs:
            jd = dict(j)
            jd["role_style"] = get_job_role_style(jd["title"])
            jobs.append(jd)
        
    if request.method == "POST":
        candidate_name = request.form.get("name", "").strip()
        candidate_email = request.form.get("email", "").strip()
        candidate_phone = request.form.get("phone", "").strip()
        job_id = request.form.get("job_id")
        
        # Validation 1: Check required fields
        if not candidate_name:
            flash("Candidate name is required.", "danger")
            return redirect(url_for("upload_page"))
            
        if not job_id:
            flash("Please select a target job position to match against.", "danger")
            return redirect(url_for("upload_page"))
            
        # Validation 2: Check file input
        if "resume_file" not in request.files:
            flash("No resume file uploaded.", "danger")
            return redirect(url_for("upload_page"))
            
        file = request.files["resume_file"]
        if file.filename == "":
            flash("No file selected for upload.", "danger")
            return redirect(url_for("upload_page"))
            
        if not allowed_file(file.filename):
            flash("Invalid file format. Please upload a PDF (.pdf) or Word document (.docx).", "danger")
            return redirect(url_for("upload_page"))
            
        # Secure and save the file with unique timestamp prefix to prevent collisions
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_filename = f"{timestamp}_{original_filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], saved_filename)
        file.save(filepath)
        
        # Extract text from the resume
        extracted_text = extract_resume_text(filepath, original_filename)
        if not extracted_text.strip():
            flash("Could not extract any readable text from this file. Please verify the document has readable text.", "warning")
            extracted_text = "No readable text extracted."
            
        # Fetch target job description
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, description FROM jobs WHERE id = ?", (job_id,))
            job_row = cursor.fetchone()
            
        if not job_row:
            flash("The selected job posting could not be found.", "danger")
            return redirect(url_for("upload_page"))
            
        job_title = job_row["title"]
        job_desc = job_row["description"]
        
        # Calculate TF-IDF Cosine Similarity and extract matching/missing skills
        match_pct, matched_skills, missing_skills = match_resume_with_job(extracted_text, job_desc)
        
        # Save to SQLite candidates table
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO candidates (
                    name, email, phone, filename, extracted_text,
                    job_id, match_percentage, matched_skills, missing_skills, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Reviewing')
            """, (
                candidate_name,
                candidate_email,
                candidate_phone,
                saved_filename,
                extracted_text,
                job_id,
                match_pct,
                json.dumps(matched_skills),
                json.dumps(missing_skills)
            ))
            candidate_id = cursor.lastrowid
            conn.commit()
            
        flash("Resume uploaded and processed successfully!", "success")
        
        # Detailed skill insights & learning roadmaps for missing skills
        missing_skills_detailed = [get_skill_details(s, job_title) for s in missing_skills]
        matched_skills_detailed = [get_skill_details(s, job_title) for s in matched_skills]
        feedback_text = generate_candidate_feedback(candidate_name, job_title, matched_skills, missing_skills)
        role_style = get_job_role_style(job_title)
        
        # Render page with matching result preview and extracted text
        result_preview = {
            "id": candidate_id,
            "name": candidate_name,
            "job_title": job_title,
            "filename": saved_filename,
            "match_percentage": match_pct,
            "matched_skills": matched_skills,
            "matched_skills_detailed": matched_skills_detailed,
            "missing_skills": missing_skills,
            "missing_skills_detailed": missing_skills_detailed,
            "role_style": role_style,
            "feedback_text": feedback_text,
            "extracted_text": extracted_text
        }
        
        return render_template("upload.html", jobs=jobs, result_preview=result_preview, selected_job_id=job_id)
        
    return render_template("upload.html", jobs=jobs, result_preview=None, selected_job_id=selected_job_id)


@app.route("/candidates")
def candidates_page():
    """
    Recruiter Candidate Dashboard.
    Lists all candidates with match percentages, skills, and application status.
    Supports filtering by status, role, and searching by candidate name or skill.
    """
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    job_filter = request.args.get("job_id", "").strip()
    missing_skill_filter = request.args.get("missing_skill", "").strip()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Fetch all jobs with applicant counts and colorful styling for role pills
        cursor.execute("""
            SELECT j.id, j.title, COUNT(c.id) AS count
            FROM jobs j
            LEFT JOIN candidates c ON j.id = c.job_id
            GROUP BY j.id
            ORDER BY count DESC, j.title ASC
        """)
        raw_job_stats = cursor.fetchall()
        job_stats = []
        for js in raw_job_stats:
            j_dict = dict(js)
            j_dict["role_style"] = get_job_role_style(j_dict["title"])
            job_stats.append(j_dict)
            
        jobs = cursor.execute("SELECT id, title FROM jobs ORDER BY title ASC").fetchall()
        
        # Build dynamic query
        query = """
            SELECT c.*, j.title AS job_title
            FROM candidates c
            JOIN jobs j ON c.job_id = j.id
            WHERE 1=1
        """
        params = []
        
        if search_query:
            query += " AND (c.name LIKE ? OR c.matched_skills LIKE ? OR c.missing_skills LIKE ? OR c.extracted_text LIKE ?)"
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])
            
        if status_filter and status_filter != "All":
            query += " AND c.status = ?"
            params.append(status_filter)
            
        if job_filter and job_filter != "All":
            query += " AND c.job_id = ?"
            params.append(job_filter)
            
        if missing_skill_filter and missing_skill_filter != "All":
            query += " AND c.missing_skills LIKE ?"
            params.append(f"%{missing_skill_filter}%")
            
        query += " ORDER BY c.match_percentage DESC, c.id DESC"
        cursor.execute(query, params)
        candidates_raw = cursor.fetchall()
        
        # Collect set of all unique missing skills across candidates for quick filter dropdown
        all_missing_skills = set()
        
        # Parse JSON skills and enrich with role styles & missing skill roadmaps
        candidates = []
        for row in candidates_raw:
            c = dict(row)
            c["matched_skills"] = json.loads(c["matched_skills"] or "[]")
            c["missing_skills"] = json.loads(c["missing_skills"] or "[]")
            c["role_style"] = get_job_role_style(c["job_title"])
            c["missing_skills_detailed"] = [get_skill_details(s, c["job_title"]) for s in c["missing_skills"]]
            for s in c["missing_skills"]:
                all_missing_skills.add(s)
            candidates.append(c)

    return render_template(
        "candidates.html",
        candidates=candidates,
        jobs=jobs,
        job_stats=job_stats,
        all_missing_skills=sorted(list(all_missing_skills)),
        search_query=search_query,
        status_filter=status_filter,
        job_filter=job_filter,
        missing_skill_filter=missing_skill_filter
    )


@app.route("/candidate/<int:candidate_id>")
def candidate_detail(candidate_id):
    """View complete candidate profile, matching details, full extracted resume text, and upskill roadmaps."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, j.title AS job_title, j.description AS job_description
            FROM candidates c
            JOIN jobs j ON c.job_id = j.id
            WHERE c.id = ?
        """, (candidate_id,))
        row = cursor.fetchone()
        
    if not row:
        flash("Candidate not found.", "danger")
        return redirect(url_for("candidates_page"))
        
    candidate = dict(row)
    candidate["matched_skills"] = json.loads(candidate["matched_skills"] or "[]")
    candidate["missing_skills"] = json.loads(candidate["missing_skills"] or "[]")
    candidate["role_style"] = get_job_role_style(candidate["job_title"])
    candidate["missing_skills_detailed"] = [get_skill_details(s, candidate["job_title"]) for s in candidate["missing_skills"]]
    candidate["matched_skills_detailed"] = [get_skill_details(s, candidate["job_title"]) for s in candidate["matched_skills"]]
    candidate["feedback_text"] = generate_candidate_feedback(
        candidate["name"], candidate["job_title"], candidate["matched_skills"], candidate["missing_skills"]
    )
    
    return render_template("candidate_detail.html", candidate=candidate)


@app.route("/api/candidate/<int:candidate_id>/feedback")
def candidate_feedback_api(candidate_id):
    """Generate and return pre-formatted constructive feedback email for the candidate."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, j.title AS job_title
            FROM candidates c
            JOIN jobs j ON c.job_id = j.id
            WHERE c.id = ?
        """, (candidate_id,))
        row = cursor.fetchone()
        
    if not row:
        return jsonify({"error": "Candidate not found"}), 404
        
    c = dict(row)
    matched = json.loads(c["matched_skills"] or "[]")
    missing = json.loads(c["missing_skills"] or "[]")
    feedback = generate_candidate_feedback(c["name"], c["job_title"], matched, missing)
    return jsonify({
        "success": True, 
        "feedback": feedback, 
        "candidate_name": c["name"], 
        "job_title": c["job_title"],
        "missing_count": len(missing)
    })


@app.route("/update_status/<int:candidate_id>", methods=["POST"])
def update_status(candidate_id):
    """
    Allow recruiter to mark candidates as 'Shortlisted', 'Reviewing', or 'Rejected'.
    Supports both regular form submissions and asynchronous AJAX requests.
    """
    new_status = request.form.get("status") or (request.json and request.json.get("status"))
    allowed_statuses = {"Shortlisted", "Reviewing", "Rejected"}
    
    if new_status not in allowed_statuses:
        if request.is_json:
            return jsonify({"success": False, "message": "Invalid status."}), 400
        flash("Invalid status specified.", "danger")
        return redirect(request.referrer or url_for("candidates_page"))
        
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE candidates SET status = ? WHERE id = ?", (new_status, candidate_id))
        conn.commit()
        
    if request.is_json:
        return jsonify({"success": True, "status": new_status})
        
    flash(f"Candidate status updated to '{new_status}'.", "success")
    return redirect(request.referrer or url_for("candidates_page"))


@app.route("/candidate/delete/<int:candidate_id>", methods=["POST"])
def delete_candidate(candidate_id):
    """Delete a candidate record and clean up their uploaded file."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT filename FROM candidates WHERE id = ?", (candidate_id,))
        row = cursor.fetchone()
        
        if row and row["filename"]:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], row["filename"])
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")
                    
        cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        conn.commit()
        
    flash("Candidate removed successfully.", "info")
    return redirect(url_for("candidates_page"))


@app.route("/uploads/<path:filename>")
def download_file(filename):
    """Safely serve uploaded resumes for recruiter inspection."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# =====================================================================
# Application Startup
# =====================================================================

# Initialize the database automatically when starting the application
init_db()

if __name__ == "__main__":
    print("==================================================")
    print(" Applicant Tracking System (ATS) Server Started ")
    print(" Local URL: http://127.0.0.1:5000/ ")
    print("==================================================")
    app.run(debug=True, port=5000)
