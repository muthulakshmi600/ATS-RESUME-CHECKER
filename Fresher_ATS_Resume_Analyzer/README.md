# 🎓 Fresher ATS Resume Analyzer

> **"Check your resume. Match it with the job. Improve your ATS compatibility."**

A modern, transparent, and comprehensive web application built with **Python, Streamlit, SQLite, PyMuPDF, python-docx, ReportLab, and bcrypt**, specifically engineered for **freshers, recent college graduates, and entry-level IT job seekers** (B.Tech/BE, BCA, B.Sc Computer Science, Junior Python/Web/AI/Data Developers).

Unlike conventional corporate ATS checkers that penalize candidates for a lack of multi-year corporate experience, this analyzer prioritizes **Academic Projects, College Internships, Industrial Training, Technical Skill Categorization, and Code Repositories (GitHub/LinkedIn)**.

---

## 🌟 Key Features

1. **Exact 100-Point Rule-Based ATS Compatibility Score**:
   - **Keyword Match (30 pts)**: Scans job description keywords, ignores non-informative stopwords, and calculates exact keyword overlap.
   - **Skills Match (20 pts)**: Compares required tech stack against resume skills across 5 core categories (Programming, AI/ML, Web, Database, Tools).
   - **Resume Sections (15 pts)**: Contact (2), Summary (2), Technical Skills (3), Education (3), Projects (3), Internship/Training (1), Certifications (1).
   - **Formatting & Readability (15 pts)**: Verifies text extractability (PyMuPDF), standard headers, single-column parsing flow, table safety, image count, and spacing.
   - **Job Relevance (10 pts)**: Assesses project relevance (4), internship/training relevance (3), and career summary relevance (3).
   - **Contact Information (10 pts)**: Name (2), Email (2), Phone (2), Location (1), LinkedIn (1.5), GitHub (1.5).
   - **Total ATS Score**: `30 + 20 + 15 + 15 + 10 + 10 = 100 points`.

2. **Separate Application-Generated Job Match (%)**:
   - Distinct similarity metric broken down by Technical Skills %, Keywords %, Projects %, and Education %.
   - Clearly labeled to prevent deceptive claims of "hiring probability".

3. **Keyword & Skills Intelligence**:
   - **Matched Keywords** (✅) and **Missing Keywords** (⚠️).
   - Freshers guidance notice: *"Consider adding these only if you genuinely have knowledge or experience with them."*
   - Categorized skills inventory (Programming, AI/ML, Web Development, Databases, Tools).

4. **Fresher Resume Checklist**:
   - Instant verification of Education, Technical Skills, Academic Projects, Internship/Training, Certifications, LinkedIn, and GitHub.

5. **Grounded Improvement Suggestions**:
   - Actionable recommendations generated strictly from detected gaps. Never hallucinates false experience or claims.

6. **Downloadable Single-Column PDF ATS Report**:
   - Generated on-the-fly using **ReportLab** into an A4 PDF document containing full score breakdowns, checklist, and roadmap.

7. **Multi-User Security & Isolated History**:
   - **bcrypt** password hashing (no plaintext passwords).
   - User-isolated SQLite database storage (`fresher_ats.db`).
   - Session-guarded routes (Dashboard, Resume Checker, History, Profile).

---

## 📁 Project Structure

```text
Fresher_ATS_Resume_Analyzer/
│
├── app.py                      # Main Streamlit router & lifecycle controller
├── requirements.txt            # Package dependencies
├── README.md                   # Full documentation & run instructions
│
├── database/
│   └── database.py             # SQLite models, user records & history isolation
│
├── auth/
│   └── authentication.py       # bcrypt hashing, validations & session guards
│
├── pages/
│   ├── landing.py              # Hero landing page & feature highlights
│   ├── login.py                # bcrypt sign-in & session creation
│   ├── register.py             # User signup & email uniqueness verification
│   ├── dashboard.py            # Welcome greeting, KPI stat cards & recent checks
│   ├── resume_checker.py       # PDF/DOCX uploader, analysis runner & results UI
│   ├── history.py              # Historical analyses table, search & CSV export
│   └── profile.py              # Profile management, links & fresher advice
│
├── utils/
│   ├── resume_parser.py        # PyMuPDF & python-docx extraction & metadata
│   ├── ats_checker.py          # 100-pt ATS formula, Job Match & Suggestions
│   ├── keyword_matcher.py      # Stopword filtering & 30-pt keyword scoring
│   ├── skills_analyzer.py      # 5-category skills ontology & 20-pt skills scoring
│   ├── formatting_checker.py   # Section detection, layout inspection & contact
│   └── report_generator.py     # ReportLab A4 PDF generation engine
│
└── assets/
    └── style.css               # Executive clean recruiter UI styles
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Install Dependencies
Open your terminal in the project directory:

```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Streamlit application:

```bash
streamlit run app.py
```

If the `streamlit` command is not recognized in your Windows terminal, run:

```bash
py -m streamlit run app.py
```

The web application will open automatically at `http://localhost:8501`.

---

## 🔄 Complete User Journey

1. **Landing Page**: View overview, target freshers audience, and key ATS audit pillars. Click **Create Account** or **Sign In**.
2. **Register**: Sign up with Full Name, valid Email, and Password (min 8 chars, hashed with bcrypt).
3. **Login**: Authenticate securely into your private session.
4. **Dashboard**: View summary KPI cards (Total Resumes Checked, Average ATS Score, Latest ATS Score, Latest Job Match) and recent checks.
5. **Check Resume**:
   - Upload your resume (`.pdf` or `.docx`).
   - Enter your target Job Title (e.g., *Junior Python Developer*).
   - Paste the Job Description requirements.
   - Click **Analyze Resume Compatibility**.
6. **Detailed Analysis Results**:
   - View your ATS Compatibility Score out of 100 with full breakdown.
   - Review Job Match similarity percentage.
   - Check Matched and Missing Keywords.
   - Review technical skills categorized into Programming, AI/ML, Web, Databases, and Tools.
   - Check off your Fresher Resume Checklist (Projects, Training, GitHub, LinkedIn).
   - Read grounded improvement suggestions.
7. **Download ATS Report**: Click **Download Full ATS Report (PDF)** for an A4 ReportLab summary document.
8. **Analysis History**: Access all past benchmarks, search by role, or export to CSV.
9. **Candidate Profile**: Keep your GitHub and LinkedIn links up-to-date.
10. **Sign Out**: Safely clear session state and return to login.

---

## 🔒 Security & Privacy

- **Password Hashing**: Uses `bcrypt` with automatic salting.
- **Tenant Isolation**: Every database query filters strictly by the authenticated `user_id`.
- **In-Memory Parsing**: Resumes are parsed directly from memory without permanent retention of unneeded file uploads.
- **No External Paid APIs**: All NLP keyword and skill matching is executed locally using transparent, rule-based algorithms.
