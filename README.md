# 💼 Applicant Tracking System (ATS) Web Application

A clean, modern, and beginner-friendly Applicant Tracking System (ATS) web application built with **Python**, **Flask**, **SQLite**, **Pandas**, **Scikit-learn**, **PyPDF2**, and **python-docx**.

Designed specifically for recruiters to streamline candidate screening and for beginner Python developers to easily understand, learn from, and expand.

---

## 🌟 Features Overview

1. **Dashboard Overview**
   - KPI metrics: Total Candidates, Shortlisted, In Review, Rejected, and Active Job Openings.
   - Quick shortcuts to post jobs and upload resumes.
   - Recent applicants summary table with match score badges.

2. **Job Description Management**
   - Create and store job titles and complete job descriptions.
   - Automatically track how many candidates have applied to each job.
   - Delete outdated job postings.

3. **Resume Upload & Text Extraction**
   - Supports both **PDF (`.pdf`)** and **Microsoft Word (`.docx`)** files.
   - Automated text extraction using **PyPDF2** and **python-docx**.
   - Validates file extensions and prevents duplicate file overwriting.

4. **Transparent Resume Matching (No "Fake AI")**
   - **TF-IDF Vectorization** (Term Frequency - Inverse Document Frequency) converts resumes and job descriptions into statistical word-weight vectors.
   - **Cosine Similarity** from `scikit-learn` calculates the exact mathematical alignment between the documents (0% to 100%).
   - **Skill & Keyword Extraction**: Detects technical skills required in the job description and compares them against the resume.
   - **Matched Skills**: Highlights skills present in the resume with green badges.
   - **Missing Skills**: Highlights required skills absent from the resume with red badges.

5. **Candidate Pipeline & Dashboard**
   - Displays candidate name, contact info, applied job, match score, skills badges, and application stage.
   - Allows recruiter to change candidate status on the fly: **Shortlisted**, **Reviewing**, or **Rejected**.
   - Live search by candidate name or specific skill (e.g., *Python*, *SQL*, *Flask*).
   - Filter candidates by Application Status or Job Position.
   - View full extracted resume text and download the original uploaded document.

---

## 📁 Project Structure

```text
ats resume/
│
├── app.py                      # Main Flask application, routes, and NLP matching engine
├── requirements.txt            # Python dependencies
├── ats.db                      # SQLite database (auto-created on startup)
├── sample_job.txt              # Ready-to-use sample job description for quick testing
├── create_sample_resumes.py    # Script to regenerate sample PDF and DOCX resumes
├── test_backend.py             # Automated unit & integration tests
│
├── templates/                  # HTML templates using Jinja2
│   ├── base.html               # Semantic base layout, navbar, flash messages, footer
│   ├── index.html              # Main recruiter dashboard
│   ├── job.html                # Job description creator & job list
│   ├── upload.html             # Resume upload form & match result preview
│   ├── candidates.html         # Candidate pipeline table with search & filters
│   └── candidate_detail.html   # Full candidate profile & extracted text preview
│
├── static/                     # Static styling and frontend scripts
│   ├── css/
│   │   └── style.css           # Clean, professional recruiter UI design
│   └── js/
│       └── script.js           # Drag-and-drop upload & instant search filtering
│
├── uploads/                    # Folder where uploaded resumes are securely stored
└── sample_resumes/             # Ready-to-test sample resumes
    ├── alex_python_developer.docx         (High match - Junior Python Developer)
    ├── sarah_data_scientist.pdf          (Medium/High match - Data & Python)
    └── david_marketing_specialist.pdf    (Low match - Marketing Specialist)
```

---

## 🚀 Step-by-Step Beginner Setup Guide

### Step 1: Open the Project Folder in VS Code
1. Open **Visual Studio Code**.
2. Click **File** &rarr; **Open Folder...**
3. Select this project folder: `c:\Users\acer\Desktop\ats resume`.
4. Open the integrated terminal in VS Code:
   - Press <kbd>Ctrl</kbd> + <kbd>`</kbd> (backtick) OR click **Terminal** &rarr; **New Terminal**.

---

### Step 2: Create a Virtual Environment
A virtual environment keeps your project dependencies isolated from the rest of your computer.

In your VS Code terminal (PowerShell or Command Prompt), run:

```powershell
py -m venv venv
```

*(If `py` is not recognized, use `python -m venv venv`)*

---

### Step 3: Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

> **Note for PowerShell execution policy error:**
> If PowerShell says *script execution is disabled*, run this once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then run `.\venv\Scripts\Activate.ps1` again.

**On Windows (Command Prompt `cmd`):**
```cmd
venv\Scripts\activate.bat
```

Once activated, you will see `(venv)` at the beginning of your terminal prompt.

---

### Step 4: Install the Required Packages

With `(venv)` active, run:

```powershell
pip install -r requirements.txt
```

This installs:
- **Flask**: Web framework to handle routes, forms, and render HTML pages.
- **scikit-learn**: Machine learning library for TF-IDF vectorization & Cosine Similarity.
- **pandas**: Data manipulation library.
- **PyPDF2**: Extracts readable text from PDF documents.
- **python-docx**: Extracts paragraphs and table text from `.docx` files.
- **Werkzeug**: Provides security utilities like `secure_filename`.

---

### Step 5: Run the Flask Application

Run the application with:

```powershell
python app.py
```
*(or `py app.py`)*

You will see output in the terminal:
```text
==================================================
 Applicant Tracking System (ATS) Server Started 
 Local URL: http://127.0.0.1:5000/ 
==================================================
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Testing the Application with Sample Resumes

We have included pre-built sample resumes in the `sample_resumes/` folder so you can test all features immediately!

### Test Walkthrough:
1. **Create a Job Description:**
   - Go to the **Job Description** tab (`/job`).
   - Open the included `sample_job.txt` file.
   - Copy the title: `Junior Python Developer`.
   - Copy the job description text and click **Save Job Description**.

2. **Upload a Strong Match Resume (DOCX):**
   - Go to **Upload Resume** (`/upload`).
   - Candidate Name: `Alex Johnson`
   - Select Target Job: `Junior Python Developer`
   - Drag & drop or browse for: `sample_resumes/alex_python_developer.docx`
   - Click **Upload, Extract & Match**.
   - **Result:** You will see a high match score (~49%), 18 matched skills (`Python`, `Flask`, `SQLite`, `Git`, `HTML5`, `CSS3`, `JavaScript`, etc.), and the full extracted text!

3. **Upload a Strong Match Resume (PDF):**
   - Upload `sample_resumes/sarah_data_scientist.pdf` for `Sarah Chen`.
   - **Result:** You will see a strong score (~41%) with matched data science and Python skills.

4. **Upload a Low Match Resume (PDF):**
   - Upload `sample_resumes/david_marketing_specialist.pdf` for `David Miller`.
   - **Result:** You will see a low match score (~3%), only 1 soft skill matched (`Communication`), and 24 missing technical skills!

5. **Test the Candidate Dashboard:**
   - Go to the **Candidates** tab (`/candidates`).
   - Try the **Search** box: type `Python` or `Alex` — notice the list filters in real time!
   - Try the **Status** filter: select `Shortlisted`, `Reviewing`, or `Rejected`.
   - Change a candidate's status using the dropdown or click **Review** to open the candidate's full profile.

---

## 🧠 How the Matching Engine Works (Honest NLP Explanation)

Unlike marketing gimmicks that claim "black-box AI understands human potential", this ATS uses **grounded, transparent Natural Language Processing (NLP)**:

### 1. TF-IDF Vectorization (`scikit-learn`)
- **TF (Term Frequency)** measures how often a word appears in a document.
- **IDF (Inverse Document Frequency)** reduces the weight of common English filler words (e.g., *"the"*, *"and"*, *"with"*).
- We use **unigrams and bigrams** (`ngram_range=(1, 2)`). This ensures technical terms like `"rest api"` and `"machine learning"` are treated as single meaningful phrases rather than isolated words.

### 2. Cosine Similarity
- The job description and resume are transformed into high-dimensional numerical vectors.
- Cosine similarity calculates the cosine of the angle between these two vectors:
  $$\text{Cosine Similarity} = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|}$$
- If the resume shares identical vocabulary and phrase frequencies with the job description, the score approaches 1.0 (100%). If there is no overlap, it is 0.0 (0%).

### 3. Skill & Keyword Coverage
- The system checks for known technical and domain skills required in the job description.
- **Matched Skills**: $\text{Job Skills} \cap \text{Resume Skills}$ (present in both).
- **Missing Skills**: $\text{Job Skills} - \text{Resume Skills}$ (required by the employer but missing from the resume).

### 4. Combined Transparent Score
- The ATS calculates a balanced score:
  $$\text{Match Percentage} = 50\% \times \text{TF-IDF Cosine Score} + 50\% \times \text{Skill Coverage Score}$$
- This ensures candidates with the exact required tools score significantly higher than candidates with general prose.

---

## 🗄️ SQLite Database Schema

The database `ats.db` is stored locally and managed with Python's built-in `sqlite3`:

### `jobs` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER PRIMARY KEY | Unique job ID (Auto-increment) |
| `title` | TEXT | Job title (e.g. Junior Python Developer) |
| `description` | TEXT | Complete text of job description |
| `created_at` | TIMESTAMP | Date and time the job was created |

### `candidates` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER PRIMARY KEY | Unique candidate ID (Auto-increment) |
| `name` | TEXT | Candidate full name |
| `email` | TEXT | Optional candidate email |
| `phone` | TEXT | Optional candidate phone |
| `filename` | TEXT | Saved resume file name in `uploads/` |
| `extracted_text`| TEXT | Full extracted text from PDF/DOCX |
| `job_id` | INTEGER | Foreign key referencing `jobs(id)` |
| `match_percentage` | REAL | Calculated similarity percentage (0-100%) |
| `matched_skills` | TEXT (JSON) | List of matched skills stored as JSON |
| `missing_skills` | TEXT (JSON) | List of missing skills stored as JSON |
| `status` | TEXT | 'Reviewing', 'Shortlisted', or 'Rejected' |
| `created_at` | TIMESTAMP | Application submission timestamp |

---

## 💻 Running Automated Tests

To run the automated verification test suite at any time:

```powershell
python test_backend.py
```

This verifies:
- Database table creation.
- Text extraction from both PDF and DOCX documents.
- Mathematical calculation of TF-IDF Cosine Similarity and skill overlap.
- Flask endpoints (`/`, `/job`, `/upload`, `/candidates`, `/update_status`).
