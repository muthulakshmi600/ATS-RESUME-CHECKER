# 💼 ResumeAI — ATS Resume Score Checker

> **"Build a Resume That Gets Noticed."**

A complete, production-ready, SaaS-style Applicant Tracking System (ATS) resume diagnostic platform. Engineered with a **React 18 & Tailwind CSS** frontend, a **Python Flask & SQLite** backend, and a transparent, deterministic **6-factor ATS scoring engine** that extracts and audits PDF and DOCX resumes in seconds.

---

## 🌟 Overview & Key Highlights

ResumeAI is designed as a portfolio-grade web application to demonstrate modern full-stack engineering, practical natural language document analysis, and SaaS design patterns.

- **Objective 0–100 ATS Score**: Deterministic evaluation instead of arbitrary numbers.
- **PDF & Word (.docx) Extraction**: Extracts clean text from modern multi-column resumes.
- **Job Description Semantic Matching**: Employs TF-IDF vectorization and cosine similarity from `scikit-learn` to measure precision candidate-to-job alignment.
- **Actionable Gap Recommendations**: Highlights exact missing keywords, unrepresented technical tools, and formatting pitfalls.
- **Zero-Friction Demo Mode**: Works with permissive demo credentials (e.g. `test@gmail.com` / `12345`) so tutors, interviewers, and evaluators can inspect every page immediately.
- **Zero-Config React Architecture**: No `node_modules` or `npm install` headaches. The React SPA is bundled with modular ES components and rendered directly.

---

## 📐 ATS Scoring Engine (0 – 100 Points)

Unlike opaque "black box" resume analyzers, ResumeAI calculates ATS compatibility using an explainable mathematical formula:

| Category | Max Weight | Evaluation Factors |
| :--- | :---: | :--- |
| **ATS Formatting** | **20 pts** | Validates email address, phone number, LinkedIn/GitHub links, clean character encoding, and optimal document length (250–1,300 words). |
| **Role Keywords** | **25 pts** | Evaluates role-specific terminology, strong past-tense action verbs (e.g. *Architected*, *Optimized*, *Engineered*), and balanced keyword density. |
| **Skills Match** | **15 pts** | Compares extracted competencies against a curated dictionary of 150+ hard technologies and soft engineering methodologies. |
| **Job Match** | **20 pts** | Calculates TF-IDF vector cosine similarity against the employer's Job Description (or standardized role benchmark if JD is omitted). |
| **Resume Structure** | **10 pts** | Detects 5 core standard sections: *Contact Info*, *Professional Summary*, *Work Experience*, *Education*, and *Technical Skills*. |
| **Readability** | **10 pts** | Audits bullet point usage (8+ points recommended), sentence brevity, and action verb initiation. |
| **Total** | **100 pts** | **Final ATS Readiness Score** |

### Compatibility Tiers
- **90 – 100**: 🟢 **Excellent** (High ATS Compatibility)
- **75 – 89**: 🔵 **Good** (Competitive Candidate)
- **60 – 74**: 🟡 **Fair** (Moderate ATS Risk — Needs Keyword Polish)
- **Below 60**: 🔴 **Needs Improvement** (Missing Core Sections or Unparsable Format)

---

## 🏗️ Project Structure

```text
resume-ai/
│
├── backend/
│   ├── app.py              # Flask REST API, CORS middleware & static SPA hosting
│   ├── analyzer.py         # 6-Factor deterministic ATS scoring engine
│   ├── parser.py           # Text extraction from PDF (pymupdf/PyPDF2) and DOCX (python-docx)
│   ├── database.py         # SQLite persistence for users, scan history, and settings
│   ├── test_suite.py       # Automated end-to-end unit & integration tests
│   └── resume_ai.db        # SQLite database (auto-generated on startup)
│
├── frontend/
│   ├── index.html          # Single-Page Application (SPA) container
│   ├── components/
│   │   ├── Icons.js        # Crisp standalone SVG icon system (Lucide style)
│   │   ├── Navbar.js       # Public landing page navigation
│   │   ├── Sidebar.js      # Authenticated dashboard sidebar
│   │   ├── ScoreGauge.js   # Animated circular SVG score indicator (0-100)
│   │   ├── MetricCard.js   # KPI cards for dashboard statistics
│   │   ├── FileUploader.js # Drag-and-drop file uploader with size/format check
│   │   ├── CategoryBreakdown.js # Progress bars for the 6 scoring dimensions
│   │   ├── SkillTags.js    # Matched (green) vs Missing (rose) pills with filters
│   │   ├── SuggestionsList.js   # Prioritized recommendations with High/Med badges
│   │   └── Toast.js        # Snappy action notification toasts
│   ├── pages/
│   │   ├── LandingPage.js  # Hero with preview badge, 4 steps, and 8 features
│   │   ├── LoginPage.js    # Demo login (any non-empty email/password)
│   │   ├── SignUpPage.js   # Account registration with validation
│   │   ├── DashboardPage.js# Welcome banner, KPI metrics, recent scans
│   │   ├── CheckResumePage.js # 3-step file upload & animated scanner
│   │   ├── AnalysisResultPage.js # Complete ATS report & print summary
│   │   ├── HistoryPage.js  # Searchable scan history & deletion
│   │   └── ProfileSettingsPage.js # Profile editor & engine strictness tuning
│   ├── services/
│   │   ├── api.js          # Backend API client with localStorage fallback
│   │   └── clientEngine.js # Standalone client scoring engine for offline demo
│   └── assets/
│       └── css/styles.css  # Typography, keyframes, and print layout
│
├── sample_resumes/
│   ├── sample_python_developer.docx # Real Word resume for testing
│   └── sample_ai_ml_engineer.pdf    # Real PDF resume for testing
│
├── run.py                  # Single-command launcher (starts Flask & opens browser)
├── start.bat               # Windows double-click shortcut
├── requirements.txt        # Pinned Python dependencies
└── README.md               # Documentation & demonstration guide
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.9 or higher (Python 3.10+ recommended)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 1. Installation
Install the lightweight backend dependencies:
```bash
cd resume-ai
pip install -r requirements.txt
```

### 2. Run the Application
Run the unified launcher script:
```bash
python run.py
```
*(Or double-click `start.bat` on Windows)*

The application will automatically initialize the SQLite database, launch the Flask API on port `5050`, and open your default browser to:
👉 **`http://127.0.0.1:5050`**

---

## 🔑 Demo Login Instructions

ResumeAI includes **Demo Mode** enabled for seamless college grading and review:
- **Email**: `test@gmail.com` *(or `muthu@gmail.com`, or any non-empty email)*
- **Password**: `12345` *(or any non-empty password)*

> **Note**: You can also register a brand new custom account on the Sign Up page.

---

## 🧪 Testing & Verification

ResumeAI includes an automated 13-point test suite verifying every route, parser, and scoring calculation:
```bash
python backend/test_suite.py
```

### Verified Test Suite Output:
```text
[TEST] Running ResumeAI Comprehensive Test Suite...

  ✓ Health check endpoint: OK
  ✓ Demo Login (test@gmail.com / 12345): OK
  ✓ Demo Login (muthu@gmail.com / muthu123): OK
  ✓ Empty credentials validation: OK
  ✓ User Registration endpoint: OK
  ✓ DOCX Resume Analysis (Score: 74/100): OK
  ✓ PDF Resume Analysis (Score: 74/100): OK
  ✓ User History retrieval (2 items): OK
  ✓ User Stats (Total: 2, Avg: 74.0): OK
  ✓ Profile update: OK
  ✓ Preferences & Settings update: OK
  ✓ Delete History item (#1): OK
  ✓ Static SPA Frontend index serving: OK

[SUCCESS] ALL 13 TEST CASES PASSED SUCCESSFULLY!
```

---

## 🎓 College Presentation Walkthrough

When presenting this project to your tutor or evaluator:

1. **Landing Page**:
   - Point out the SaaS branding, hero preview widget (`ATS Score: 82/100`), the 4-step workflow, and the 8 feature cards.
2. **Demo Authentication**:
   - Show that entering `test@gmail.com` / `12345` logs in immediately.
   - Show validation when leaving fields empty.
3. **Dashboard & KPIs**:
   - Highlight the 4 stat cards (*Resumes Checked*, *Average ATS Score*, *Best Score*, *Last Scan*).
4. **Interactive Checker**:
   - Click **Check My Resume**.
   - Either drag & drop `sample_resumes/sample_python_developer.docx` or click **Load Sample Resume**.
   - Show the smooth multi-step animated loading overlay.
5. **Comprehensive Diagnostic Report**:
   - Explain the circular animated gauge.
   - Walk through the 6 category breakdown cards.
   - Show the Matched vs. Missing skill pills and how filtering works.
   - Review the prioritized suggestions list.
   - Click **Print Report** to demonstrate the formatted print view.
6. **History & Persistence**:
   - Navigate to **Resume History** to show the saved record with search and filtering.
7. **Profile & Strictness Settings**:
   - Demonstrate adjusting the ATS strictness (Lenient, Standard, Strict) and editing user profile info.

---

## 📄 License
MIT License. Created for portfolio and academic presentation.
