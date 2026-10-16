"""
Advanced Rule-Based ATS Resume Analyzer Engine for ResumeAI ATS.
Provides transparent, deterministic, and explainable scoring:
- Target Job Role dependency has been completely removed.
- Calculates an objective Resume Quality Score (0-100) across 6 meaningful factors:
  1. Resume Structure & Section Completeness (20 pts)
  2. Contact Information & Professional Links (15 pts)
  3. Measurable Achievements & Action Verbs (20 pts)
  4. ATS Formatting, Layout & Length (15 pts)
  5. Readability, Tone & Style (15 pts)
  6. Technical Skills Breadth & Depth (15 pts)
- When a Job Description is provided:
  Calculates a separate Job Match Score (0-100) based on extracted skills,
  domain keywords, and TF-IDF semantic similarity.
- When no Job Description is provided:
  Displays the Resume Quality Score with a clear explanation of what it measures.
- Deterministic, consistent, and produces actionable recommendations.
"""

import re
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------------------------------------------------
# TAXONOMIES AND DICTIONARIES
# -----------------------------------------------------------------------------

# High-impact Action Verbs favored by ATS parsers and hiring managers
ACTION_VERBS = {
    "accelerated", "accomplished", "achieved", "acquired", "adapted", "administered",
    "analyzed", "architected", "automated", "built", "centralized", "championed",
    "collaborated", "configured", "constructed", "converted", "coordinated", "created",
    "debugged", "decreased", "delivered", "deployed", "designed", "developed",
    "devised", "diagnosed", "directed", "documented", "doubled", "engineered",
    "enhanced", "established", "evaluated", "executed", "expanded", "expedited",
    "formulated", "generated", "guided", "implemented", "improved", "increased",
    "initiated", "inspected", "integrated", "invented", "launched", "led",
    "leveraged", "managed", "maximized", "mentored", "migrated", "minimized",
    "modernized", "monitored", "negotiated", "optimized", "orchestrated", "organized",
    "overhauled", "pioneered", "planned", "programmed", "reduced", "refactored",
    "resolved", "restructured", "revamped", "scaled", "secured", "simplified",
    "spearheaded", "standardized", "streamlined", "strengthened", "supervised",
    "trained", "transformed", "upgraded", "validated", "yielded"
}

# Clichés and passive filler phrases that weaken ATS ranking
BUZZWORD_CLICHES = [
    "team player", "go-getter", "hard worker", "results-driven", "detail-oriented",
    "self-starter", "think outside the box", "synergy", "proven track record",
    "dynamic individual", "strong work ethic", "fast learner", "people person",
    "guru", "ninja", "rockstar"
]

# Section headers detection
SECTION_PATTERNS = {
    "contact": r"(contact|phone|email|linkedin|github|address|location)",
    "summary": r"(professional summary|summary|about me|profile|executive summary|career objective|objective)",
    "experience": r"(work experience|experience|employment history|professional experience|work history|career history|internships|internship)",
    "education": r"(education|academic background|qualifications|academic history|degrees|university|college)",
    "skills": r"(technical skills|skills|technologies|competencies|core competencies|tools & technologies|expertise|tech stack)",
    "projects": r"(projects|personal projects|academic projects|key projects|featured projects|portfolio)",
    "certifications": r"(certifications|certificates|licenses|accreditations|courses|training)"
}

# Comprehensive Universal Skills Taxonomy across tech & modern industry
UNIVERSAL_SKILLS = {
    # Programming Languages
    "python": "Python", "java": "Java", "javascript": "JavaScript", "typescript": "TypeScript",
    "c++": "C++", "c#": "C#", "golang": "Go", "go": "Go", "rust": "Rust", "ruby": "Ruby",
    "php": "PHP", "swift": "Swift", "kotlin": "Kotlin", "scala": "Scala", "r": "R",
    "sql": "SQL", "html": "HTML5", "html5": "HTML5", "css": "CSS3", "css3": "CSS3",
    "bash": "Bash", "shell": "Shell Scripting", "powershell": "PowerShell",

    # Frameworks & Libraries
    "react": "React", "react.js": "React", "next.js": "Next.js", "nextjs": "Next.js",
    "vue": "Vue.js", "vue.js": "Vue.js", "angular": "Angular", "node": "Node.js",
    "node.js": "Node.js", "express": "Express.js", "express.js": "Express.js",
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI", "spring": "Spring Boot",
    "spring boot": "Spring Boot", "asp.net": "ASP.NET", ".net": ".NET",
    "tailwind": "Tailwind CSS", "tailwind css": "Tailwind CSS", "bootstrap": "Bootstrap",
    "redux": "Redux", "graphql": "GraphQL", "rest api": "REST APIs", "restful": "REST APIs",
    "pytorch": "PyTorch", "tensorflow": "TensorFlow", "keras": "Keras",
    "scikit-learn": "Scikit-Learn", "pandas": "Pandas", "numpy": "NumPy",
    "scipy": "SciPy", "matplotlib": "Matplotlib", "seaborn": "Seaborn",

    # Databases & Storage
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL",
    "mongodb": "MongoDB", "redis": "Redis", "sqlite": "SQLite", "oracle": "Oracle DB",
    "cassandra": "Cassandra", "dynamodb": "DynamoDB", "elasticsearch": "Elasticsearch",
    "firebase": "Firebase", "snowflake": "Snowflake", "bigquery": "BigQuery",

    # Cloud & DevOps & Infrastructure
    "aws": "AWS", "amazon web services": "AWS", "azure": "Microsoft Azure",
    "gcp": "Google Cloud", "google cloud": "Google Cloud", "docker": "Docker",
    "kubernetes": "Kubernetes", "ci/cd": "CI/CD", "github actions": "GitHub Actions",
    "jenkins": "Jenkins", "terraform": "Terraform", "ansible": "Ansible",
    "linux": "Linux", "nginx": "Nginx", "git": "Git", "github": "GitHub", "gitlab": "GitLab",

    # AI / Data / ML concepts
    "machine learning": "Machine Learning", "deep learning": "Deep Learning",
    "natural language processing": "NLP", "nlp": "NLP", "computer vision": "Computer Vision",
    "large language models": "LLMs", "llm": "LLMs", "genai": "Generative AI",
    "data science": "Data Science", "data analysis": "Data Analysis",
    "data analytics": "Data Analytics", "business intelligence": "Business Intelligence",
    "power bi": "Power BI", "tableau": "Tableau", "excel": "Advanced Excel",
    "etl": "ETL Pipelines",

    # Methodologies & Engineering Practices
    "agile": "Agile", "scrum": "Scrum", "unit testing": "Unit Testing",
    "test driven development": "TDD", "tdd": "TDD", "code review": "Code Review",
    "microservices": "Microservices", "system design": "System Design",
    "object oriented programming": "OOP", "oop": "OOP", "debugging": "Debugging",
    "problem solving": "Problem Solving"
}

# -----------------------------------------------------------------------------
# MAIN ANALYSIS ENTRY POINT
# -----------------------------------------------------------------------------

def _extract_education(resume_text, lower_text):
    """
    Extracts degrees, majors, institutions, and graduation years.
    """
    degrees = []
    degree_patterns = [
        (r'\b(b\.?tech|bachelor of technology)\b', "B.Tech"),
        (r'\b(b\.?e\.?|bachelor of engineering)\b', "B.E."),
        (r'\b(b\.?s\.?|b\.?sc\.?|bachelor of science)\b', "B.S. / B.Sc"),
        (r'\b(bca|bachelor of computer applications)\b', "BCA"),
        (r'\b(m\.?tech|master of technology)\b', "M.Tech"),
        (r'\b(m\.?s\.?|m\.?sc\.?|master of science)\b', "M.S. / M.Sc"),
        (r'\b(mca|master of computer applications)\b', "MCA"),
        (r'\b(mba|master of business administration)\b', "MBA"),
        (r'\b(ph\.?d\.?|doctor of philosophy)\b', "Ph.D.")
    ]
    for pattern, name in degree_patterns:
        if re.search(pattern, lower_text):
            degrees.append(name)

    years = re.findall(r'\b(20[12]\d)\b', resume_text)
    grad_year = max(years) if years else None

    gpa_match = re.search(r'\b(?:cgpa|gpa)[\s:]*([0-9]+\.?[0-9]*)\s*(?:/\s*(?:10|4))?', lower_text)
    gpa_val = gpa_match.group(1) if gpa_match else None

    return {
        "detected_degrees": degrees,
        "graduation_year": grad_year,
        "cgpa_or_percentage": gpa_val,
        "has_education_section": bool(re.search(SECTION_PATTERNS["education"], lower_text))
    }

def _extract_experience(resume_text, lower_text):
    """
    Extracts work experience duration, internships, and role indicators.
    """
    has_internship = bool(re.search(r'\b(intern|internship|trainee|apprentice)\b', lower_text))
    has_experience_section = bool(re.search(SECTION_PATTERNS["experience"], lower_text))

    exp_year_match = re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience', lower_text)
    years_exp = float(exp_year_match.group(1)) if exp_year_match else (0.5 if has_internship else 0.0)

    if years_exp == 0.0 and not has_internship:
        exp_tier = "Fresher (0 yrs)"
    elif years_exp <= 1.0 or has_internship:
        exp_tier = "Fresher / Entry-Level (0-1 yrs)"
    elif years_exp <= 3.0:
        exp_tier = "Junior (1-3 yrs)"
    else:
        exp_tier = f"Experienced ({years_exp} yrs)"

    return {
        "experience_level": exp_tier,
        "years_estimated": years_exp,
        "has_internships": has_internship,
        "has_experience_section": has_experience_section
    }

def _extract_keywords(resume_text, lower_text, detected_skills):
    """
    Extracts high-value domain keywords, tools, and technical terms.
    """
    keywords = list(detected_skills)
    domain_terms = [
        "rest apis", "microservices", "ci/cd", "unit testing", "agile", "scrum",
        "oop", "data structures", "algorithms", "version control", "cloud computing",
        "machine learning", "deep learning", "nlp", "data visualization", "database design"
    ]
    for term in domain_terms:
        if term in lower_text and term.title() not in keywords:
            keywords.append(term.title())
    return keywords[:30]


def analyze_resume(resume_text, job_description="", job_role=None):
    """
    Main evaluation entry point.
    - Evaluates Resume Quality Score (0-100) across 6 objective dimensions.
    - If job_description is provided, calculates a separate Job Match Score (0-100).
    - job_role is completely optional and ignored in scoring.
    """
    if not resume_text or len(resume_text.strip()) < 40:
        return _empty_or_failed_analysis("Resume document is empty or text could not be extracted.")

    lower_text = resume_text.lower()
    has_jd = bool(job_description and len(job_description.strip()) >= 30)

    # 1. Structure & Sections (Max 20 pts)
    structure_score, section_status = _check_structure(lower_text)

    # 2. Contact Information & Links (Max 15 pts)
    contact_score, contact_details = _check_contact(resume_text, lower_text)

    # 3. Measurable Achievements & Action Verbs (Max 20 pts)
    achievements_score, achievements_details = _check_achievements(resume_text, lower_text)

    # 4. ATS Formatting, Layout & Length (Max 15 pts)
    formatting_score, formatting_details = _check_formatting(resume_text, lower_text)

    # 5. Readability, Tone & Style (Max 15 pts)
    readability_score, readability_details = _check_readability(resume_text, lower_text)

    # 6. Skills Breadth & Technical Depth (Max 15 pts)
    skills_score, detected_skills, categorized_skills = _check_skills(lower_text)

    # 7. Extract Candidate Profile Attributes (Education, Experience, Keywords)
    extracted_education = _extract_education(resume_text, lower_text)
    extracted_experience = _extract_experience(resume_text, lower_text)
    extracted_keywords = _extract_keywords(resume_text, lower_text, detected_skills)

    # Calculate Resume Quality Score (0 - 100)
    resume_quality_score = (
        structure_score + contact_score + achievements_score +
        formatting_score + readability_score + skills_score
    )
    resume_quality_score = min(100, max(0, int(round(resume_quality_score))))

    # Job Match Evaluation (when Job Description is provided)
    job_match_score = None
    job_match_details = None
    matched_jd_skills = []
    missing_jd_skills = []

    if has_jd:

        job_match_score, job_match_details = _calculate_job_match(
            resume_text, lower_text, job_description, detected_skills
        )
        matched_jd_skills = job_match_details.get("matched_skills", [])
        missing_jd_skills = job_match_details.get("missing_skills", [])
        # Overall score when JD provided: 50% Quality + 50% Job Match
        overall_score = int(round(0.5 * resume_quality_score + 0.5 * job_match_score))
    else:
        overall_score = resume_quality_score

    overall_score = min(100, max(0, overall_score))

    # Actionable Improvement Suggestions
    suggestions = _generate_suggestions(
        section_status=section_status,
        contact_details=contact_details,
        achievements_details=achievements_details,
        formatting_details=formatting_details,
        readability_details=readability_details,
        skills_count=len(detected_skills),
        has_jd=has_jd,
        missing_jd_skills=missing_jd_skills
    )

    # Concise Executive Summary
    summary = _generate_executive_summary(
        quality_score=resume_quality_score,
        has_jd=has_jd,
        job_match_score=job_match_score,
        detected_skills=detected_skills,
        metrics_count=achievements_details.get("metrics_count", 0)
    )

    # Ensure formatting_details mirrors key contact & achievement flags for frontend compatibility
    formatting_details["has_email"] = contact_details.get("has_email", False)
    formatting_details["has_phone"] = contact_details.get("has_phone", False)
    formatting_details["has_links"] = contact_details.get("has_links", False)

    return {
        "overall_score": overall_score,
        "resume_quality_score": resume_quality_score,
        "job_match_score": job_match_score,
        "has_job_description": has_jd,
        "grade": _get_grade(overall_score),
        "breakdown": {
            "structure": structure_score,         # max 20
            "contact": contact_score,             # max 15
            "achievements": achievements_score,   # max 20
            "metrics": achievements_score,        # max 20 (alias for achievements)
            "formatting": formatting_score,       # max 15
            "readability": readability_score,     # max 15
            "skills": skills_score                # max 15
        },
        "max_breakdown": {
            "structure": 20,
            "contact": 15,
            "achievements": 20,
            "metrics": 20,
            "formatting": 15,
            "readability": 15,
            "skills": 15
        },
        "section_status": section_status,
        "contact_details": contact_details,
        "achievements_details": achievements_details,
        "formatting_details": formatting_details,
        "readability_details": readability_details,
        "detected_skills": detected_skills,
        "categorized_skills": categorized_skills,
        "extracted_education": extracted_education,
        "extracted_experience": extracted_experience,
        "extracted_keywords": extracted_keywords,
        "matched_skills": matched_jd_skills if has_jd else detected_skills[:15],
        "missing_skills": missing_jd_skills if has_jd else [],
        "job_match_details": job_match_details,
        "action_verbs_found": achievements_details.get("action_verbs_count", 0),
        "quantified_metrics_found": achievements_details.get("metrics_count", 0),
        "metrics_count": achievements_details.get("metrics_count", 0),
        "suggestions": suggestions,
        "summary": summary
    }


# -----------------------------------------------------------------------------
# FACTOR 1: RESUME STRUCTURE & SECTIONS (MAX 20 PTS)
# -----------------------------------------------------------------------------

def _check_structure(lower_text):
    """
    Evaluates presence of standard sections expected by ATS parsers.
    Contact: 3 pts, Summary: 3 pts, Experience: 5 pts, Education: 3 pts,
    Skills: 3 pts, Projects/Certifications: 3 pts.
    Total: 20 pts.
    """
    status = {}
    score = 0

    has_contact = bool(re.search(SECTION_PATTERNS["contact"], lower_text)) or '@' in lower_text
    status["Contact Information"] = has_contact
    if has_contact:
        score += 3

    has_summary = bool(re.search(SECTION_PATTERNS["summary"], lower_text))
    status["Professional Summary"] = has_summary
    if has_summary:
        score += 3

    has_exp = bool(re.search(SECTION_PATTERNS["experience"], lower_text))
    status["Experience"] = has_exp
    if has_exp:
        score += 5

    has_edu = bool(re.search(SECTION_PATTERNS["education"], lower_text))
    status["Education"] = has_edu
    if has_edu:
        score += 3

    has_skills = bool(re.search(SECTION_PATTERNS["skills"], lower_text))
    status["Skills"] = has_skills
    if has_skills:
        score += 3

    has_proj = bool(re.search(SECTION_PATTERNS["projects"], lower_text))
    has_cert = bool(re.search(SECTION_PATTERNS["certifications"], lower_text))
    status["Projects"] = has_proj
    status["Certifications"] = has_cert
    if has_proj or has_cert:
        score += 3

    return min(20, score), status


# -----------------------------------------------------------------------------
# FACTOR 2: CONTACT INFORMATION & LINKS (MAX 15 PTS)
# -----------------------------------------------------------------------------

def _check_contact(resume_text, lower_text):
    """
    Email: 4 pts, Phone: 4 pts, Professional Links (LinkedIn/GitHub/Portfolio): 4 pts,
    Location: 3 pts. Total: 15 pts.
    """
    score = 0
    details = {}

    # Email
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', resume_text)
    has_email = bool(email_match)
    details["has_email"] = has_email
    details["email"] = email_match.group(0) if email_match else None
    if has_email:
        score += 4

    # Phone
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    has_phone = bool(re.search(phone_pattern, resume_text))
    details["has_phone"] = has_phone
    if has_phone:
        score += 4

    # Professional Links
    links_pattern = r'(linkedin\.com/in/|github\.com/|gitlab\.com/|portfolio|behance\.net|dribbble\.com|https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    has_links = bool(re.search(links_pattern, lower_text))
    details["has_links"] = has_links
    if has_links:
        score += 4

    # Location (City, State, Country indicators)
    location_pattern = r'(\b[A-Z][a-zA-Z]+,\s*[A-Z]{2}\b|\b[A-Za-z\s]+,\s*(india|usa|united states|uk|canada|australia|germany|singapore)\b|\b(bangalore|bengaluru|chennai|hyderabad|mumbai|pune|delhi|san francisco|new york|seattle|austin|chicago|london)\b)'
    has_location = bool(re.search(location_pattern, lower_text))
    details["has_location"] = has_location
    if has_location:
        score += 3

    return min(15, score), details


# -----------------------------------------------------------------------------
# FACTOR 3: MEASURABLE ACHIEVEMENTS & ACTION VERBS (MAX 20 PTS)
# -----------------------------------------------------------------------------

def _check_achievements(resume_text, lower_text):
    """
    Quantified Metrics: up to 10 pts.
    Strong Action Verbs: up to 10 pts.
    Total: 20 pts.
    """
    details = {}

    # 1. Quantified Metrics (percentages, numbers, multipliers, currency)
    metric_regex = r'(?:\b\d+(?:\.\d+)?%|\b\d+x\b|\$\d+[\d,]*(?:\.\d+)?|\b₹\d+[\d,]*(?:\.\d+)?|\b\d+[\d,]*\+?\s*(?:[a-z-]+\s+)?(?:users|clients|customers|projects|downloads|requests|tickets|students|team members|engineers|microservices|apis|records|stars|samples|queries|tests)\b|\b(?:reduced|increased|improved|saved|boosted|accelerated|scaled)\s+[a-z\s]{0,25}\b\d+)'
    found_metrics = re.findall(metric_regex, lower_text)
    metrics_count = len(found_metrics)
    details["metrics_count"] = metrics_count

    if metrics_count >= 6:
        metric_pts = 10
    elif metrics_count >= 4:
        metric_pts = 8
    elif metrics_count >= 2:
        metric_pts = 5
    elif metrics_count >= 1:
        metric_pts = 3
    else:
        metric_pts = 0

    # 2. Action Verbs
    words = set(re.findall(r'\b[a-z]+\b', lower_text))
    found_verbs = [v for v in ACTION_VERBS if v in words]
    verb_count = len(found_verbs)
    details["action_verbs_count"] = verb_count
    details["sample_verbs"] = found_verbs[:8]

    if verb_count >= 10:
        verb_pts = 10
    elif verb_count >= 7:
        verb_pts = 8
    elif verb_count >= 4:
        verb_pts = 5
    elif verb_count >= 2:
        verb_pts = 3
    else:
        verb_pts = 0

    score = metric_pts + verb_pts
    details["metrics_score"] = metric_pts
    details["verbs_score"] = verb_pts
    return min(20, score), details


# -----------------------------------------------------------------------------
# FACTOR 4: ATS FORMATTING, LAYOUT & LENGTH (MAX 15 PTS)
# -----------------------------------------------------------------------------

def _check_formatting(resume_text, lower_text):
    """
    Word Count / Document Length: 5 pts
    Bullet Points Structure: 5 pts
    Text Encoding & Cleanliness: 5 pts
    Total: 15 pts.
    """
    details = {}
    score = 0

    words = resume_text.split()
    word_count = len(words)
    details["word_count"] = word_count

    # Length (ideal 300 - 1100 words for standard 1-2 page resume)
    if 300 <= word_count <= 1100:
        score += 5
        details["length_status"] = "Optimal (1-2 pages)"
    elif 200 <= word_count < 300 or 1101 <= word_count <= 1500:
        score += 3
        details["length_status"] = "Acceptable but could be tighter"
    elif word_count < 200:
        score += 1
        details["length_status"] = "Too short (under 200 words)"
    else:
        score += 1
        details["length_status"] = "Too lengthy (over 1500 words)"

    # Bullet points count
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    bullet_lines = [
        l for l in lines
        if l.startswith(('•', '-', '*', '–', '—', '1.', '2.', '3.')) or re.match(r'^\d+\.', l)
    ]
    bullet_count = len(bullet_lines)
    details["bullet_count"] = bullet_count

    if bullet_count >= 8:
        score += 5
    elif bullet_count >= 4:
        score += 3
    elif bullet_count >= 1:
        score += 2
    else:
        score += 0

    # Encoding hygiene
    non_ascii = len([c for c in resume_text if ord(c) > 127])
    ratio = non_ascii / max(1, len(resume_text))
    if ratio < 0.04:
        score += 5
        details["encoding_clean"] = True
    else:
        score += 2
        details["encoding_clean"] = False

    return min(15, score), details


# -----------------------------------------------------------------------------
# FACTOR 5: READABILITY, TONE & WRITING STYLE (MAX 15 PTS)
# -----------------------------------------------------------------------------

def _check_readability(resume_text, lower_text):
    """
    Bullet Length Balance: 5 pts
    Absence of Fluffy Clichés: 5 pts
    Active Voice & Sentence Quality: 5 pts
    Total: 15 pts.
    """
    details = {}
    score = 0

    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    bullet_lines = [
        l for l in lines
        if l.startswith(('•', '-', '*', '–', '—', '1.', '2.', '3.')) or re.match(r'^\d+\.', l)
    ]

    # Average bullet word length
    if bullet_lines:
        avg_len = sum(len(b.split()) for b in bullet_lines) / len(bullet_lines)
        details["avg_bullet_words"] = round(avg_len, 1)
        if 10 <= avg_len <= 26:
            score += 5
        elif 6 <= avg_len < 10 or 27 <= avg_len <= 35:
            score += 3
        else:
            score += 1
    else:
        score += 2
        details["avg_bullet_words"] = 0

    # Cliché / Buzzword Detection
    found_cliches = [c for c in BUZZWORD_CLICHES if c in lower_text]
    details["cliches_found"] = found_cliches
    cliche_penalty = min(4, len(found_cliches))
    score += max(1, 5 - cliche_penalty)

    # Passive voice check (avoids excessive "responsible for", "assisted with", "helped to")
    passive_phrases = ["responsible for", "assisted with", "helped to", "duties included", "worked on"]
    found_passives = [p for p in passive_phrases if p in lower_text]
    details["passive_phrases"] = found_passives
    if not found_passives:
        score += 5
    elif len(found_passives) == 1:
        score += 4
    elif len(found_passives) <= 2:
        score += 3
    else:
        score += 1

    return min(15, score), details


# -----------------------------------------------------------------------------
# FACTOR 6: SKILLS BREADTH & TECHNICAL DEPTH (MAX 15 PTS)
# -----------------------------------------------------------------------------

def _check_skills(lower_text):
    """
    Detects universal technical and professional skills from standard dictionary.
    Scores depth: 15+ skills = 15 pts, 11-14 = 12 pts, 7-10 = 9 pts, 4-6 = 6 pts, 1-3 = 3 pts.
    Total: 15 pts.
    """
    detected_skills = []
    seen = set()

    # Sort keys by length descending to match multi-word skills first (e.g., 'spring boot' before 'spring')
    sorted_skills = sorted(UNIVERSAL_SKILLS.keys(), key=lambda x: len(x), reverse=True)

    for skill_key in sorted_skills:
        pattern = r'(?:^|\W)' + re.escape(skill_key) + r'(?:$|\W)'
        if re.search(pattern, lower_text):
            canonical = UNIVERSAL_SKILLS[skill_key]
            if canonical not in seen:
                seen.add(canonical)
                detected_skills.append(canonical)

    skill_count = len(detected_skills)
    if skill_count >= 15:
        score = 15
    elif skill_count >= 11:
        score = 12
    elif skill_count >= 7:
        score = 9
    elif skill_count >= 4:
        score = 6
    elif skill_count >= 1:
        score = 3
    else:
        score = 0

    # Categorize detected skills
    categorized = {
        "Languages": [],
        "Frameworks & Libraries": [],
        "Databases & Cloud": [],
        "Tools & Methodologies": []
    }

    for s in detected_skills:
        s_low = s.lower()
        if s_low in ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html5", "css3", "bash", "shell scripting", "powershell"]:
            categorized["Languages"].append(s)
        elif s_low in ["react", "next.js", "vue.js", "angular", "node.js", "express.js", "django", "flask", "fastapi", "spring boot", "asp.net", ".net", "tailwind css", "bootstrap", "redux", "graphql", "rest apis", "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "scipy", "matplotlib", "seaborn"]:
            categorized["Frameworks & Libraries"].append(s)
        elif s_low in ["postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle db", "cassandra", "dynamodb", "elasticsearch", "firebase", "snowflake", "bigquery", "aws", "microsoft azure", "google cloud", "docker", "kubernetes", "linux"]:
            categorized["Databases & Cloud"].append(s)
        else:
            categorized["Tools & Methodologies"].append(s)

    return score, detected_skills, categorized


# -----------------------------------------------------------------------------
# JOB MATCH CALCULATION (WHEN JOB DESCRIPTION IS PROVIDED)
# -----------------------------------------------------------------------------

def _calculate_job_match(resume_text, lower_text, job_description, resume_skills):
    """
    Calculates precision Job Match Score (0 - 100) comparing resume against JD:
    - JD Skills Match (50% weight)
    - TF-IDF Cosine Similarity & Domain Keyword Match (50% weight)
    """
    jd_lower = job_description.lower()

    # Extract required skills from JD using universal skills dictionary
    jd_required_skills = []
    seen = set()
    sorted_skills = sorted(UNIVERSAL_SKILLS.keys(), key=lambda x: len(x), reverse=True)
    for skill_key in sorted_skills:
        pattern = r'(?:^|\W)' + re.escape(skill_key) + r'(?:$|\W)'
        if re.search(pattern, jd_lower):
            canonical = UNIVERSAL_SKILLS[skill_key]
            if canonical not in seen:
                seen.add(canonical)
                jd_required_skills.append(canonical)

    if not jd_required_skills:
        # Fallback to key words from JD
        jd_required_skills = ["Communication", "Problem Solving", "Documentation", "Git"]

    resume_skills_set = set(resume_skills)
    matched_skills = [s for s in jd_required_skills if s in resume_skills_set]
    missing_skills = [s for s in jd_required_skills if s not in resume_skills_set]

    # 1. Skill Match Percentage
    skill_match_pct = round((len(matched_skills) / max(1, len(jd_required_skills))) * 100, 1)

    # 2. Semantic Text Cosine Similarity using TF-IDF
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1200, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        cosine_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        # Rescale realistic resume-to-JD cosine similarity (0.10 - 0.60 typical range)
        semantic_pct = min(100.0, max(15.0, round(cosine_sim * 165.0, 1)))
    except Exception:
        semantic_pct = skill_match_pct

    # Blended Job Match Score (0 - 100)
    job_match_score = int(round(0.55 * skill_match_pct + 0.45 * semantic_pct))
    job_match_score = min(100, max(0, job_match_score))

    details = {
        "job_match_score": job_match_score,
        "skill_match_pct": skill_match_pct,
        "semantic_similarity_pct": semantic_pct,
        "jd_required_skills_count": len(jd_required_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }

    return job_match_score, details


# -----------------------------------------------------------------------------
# DYNAMIC ACTIONABLE RECOMMENDATIONS
# -----------------------------------------------------------------------------

def _generate_suggestions(
    section_status, contact_details, achievements_details,
    formatting_details, readability_details, skills_count,
    has_jd, missing_jd_skills
):
    suggestions = []

    # 1. Missing Core Sections
    if not section_status.get("Professional Summary"):
        suggestions.append({
            "category": "Structure",
            "priority": "High",
            "text": "Add a crisp 3-4 sentence 'Professional Summary' at the top highlighting your core value, years of experience, and signature strengths."
        })

    if not section_status.get("Skills"):
        suggestions.append({
            "category": "Structure",
            "priority": "High",
            "text": "Add a dedicated 'Technical Skills' section categorizing your programming languages, frameworks, databases, and developer tools."
        })

    if not section_status.get("Projects") and not section_status.get("Certifications"):
        suggestions.append({
            "category": "Structure",
            "priority": "Medium",
            "text": "Include a 'Projects' or 'Certifications' section to showcase practical applied knowledge and verified credentials."
        })

    # 2. Contact Information
    if not contact_details.get("has_links"):
        suggestions.append({
            "category": "Contact Information",
            "priority": "High",
            "text": "Add your LinkedIn profile URL and GitHub or online portfolio link so recruiters can verify your code and professional footprint."
        })

    if not contact_details.get("has_location"):
        suggestions.append({
            "category": "Contact Information",
            "priority": "Medium",
            "text": "Include your City and State/Country (e.g., 'San Francisco, CA' or 'Bangalore, India') to ensure location-based ATS queries index your resume."
        })

    # 3. Measurable Achievements & Action Verbs
    metrics_count = achievements_details.get("metrics_count", 0)
    if metrics_count < 3:
        suggestions.append({
            "category": "Measurable Impact",
            "priority": "High",
            "text": "Quantify your achievements using specific numbers, percentages, or scale metrics (e.g., 'accelerated load times by 35%', 'managed 500+ daily queries')."
        })

    verb_count = achievements_details.get("action_verbs_count", 0)
    if verb_count < 7:
        suggestions.append({
            "category": "Action Verbs",
            "priority": "Medium",
            "text": "Start every experience bullet with an impactful action verb (e.g., 'Architected', 'Spearheaded', 'Optimized', 'Streamlined') instead of passive statements."
        })

    # 4. Readability & Clichés
    cliches = readability_details.get("cliches_found", [])
    if cliches:
        cliche_str = ", ".join(f"'{c}'" for c in cliches[:3])
        suggestions.append({
            "category": "Tone & Style",
            "priority": "Medium",
            "text": f"Replace generic buzzwords ({cliche_str}) with concrete achievements and tangible technical contributions."
        })

    # 5. Technical Skills Breadth
    if skills_count < 8:
        suggestions.append({
            "category": "Technical Depth",
            "priority": "High",
            "text": "Expand your technical stack inventory to include modern frameworks, cloud platforms (AWS/Azure/GCP), containerization (Docker), and developer tools."
        })

    # 6. Job Description Alignment
    if has_jd and missing_jd_skills:
        top_missing = ", ".join(missing_jd_skills[:4])
        suggestions.append({
            "category": "Job Match",
            "priority": "High",
            "text": f"Your target job specifically requires: {top_missing}. If you possess experience with these tools, explicitly add them to your resume."
        })
    elif not has_jd:
        suggestions.append({
            "category": "Job Matching",
            "priority": "Low",
            "text": "Paste an employer's Job Description in the analyzer to unlock custom skill gap matching and keyword alignment."
        })

    return suggestions


# -----------------------------------------------------------------------------
# EXECUTIVE SUMMARY
# -----------------------------------------------------------------------------

def _generate_executive_summary(quality_score, has_jd, job_match_score, detected_skills, metrics_count):
    skills_sample = ", ".join(detected_skills[:3]) if detected_skills else "core competencies"

    if has_jd:
        if job_match_score >= 80:
            return (
                f"Outstanding Job Alignment! Your resume achieves a {job_match_score}% match against the target job description "
                f"with a strong Resume Quality Score of {quality_score}/100. It demonstrates high keyword density and relevant skills in {skills_sample}."
            )
        elif job_match_score >= 60:
            return (
                f"Moderate Job Alignment ({job_match_score}% match) with a Resume Quality Score of {quality_score}/100. "
                f"Your resume showcases core capabilities in {skills_sample}, but has gaps in specific requirements requested in the Job Description."
            )
        else:
            return (
                f"Low Job Alignment ({job_match_score}% match). While your general Resume Quality Score is {quality_score}/100, "
                f"several crucial skills and keywords required by the employer are currently absent from your document."
            )

    # When NO JD is provided
    if quality_score >= 85:
        return (
            f"Exceptional Resume Quality ({quality_score}/100). Your document features clean section hierarchy, robust technical depth "
            f"in {skills_sample}, and {metrics_count} quantified accomplishments. It is fully primed for modern ATS parser indexing."
        )
    elif quality_score >= 65:
        return (
            f"Good Resume Quality ({quality_score}/100). The document has solid structural foundations and recognizes proficiencies in {skills_sample}. "
            f"Adding more quantified metrics and online portfolio links will push your score into the top percentile."
        )
    else:
        return (
            f"Resume Quality Needs Work ({quality_score}/100). Automated ATS scanners may struggle with missing standard sections, "
            f"sparse technical keywords, or lack of measurable achievements. Review the actionable checklist below to elevate your resume."
        )


def _get_grade(score):
    if score >= 90:
        return {"label": "Excellent", "color": "emerald", "badge": "High ATS Compatibility"}
    elif score >= 75:
        return {"label": "Good", "color": "blue", "badge": "Competitive Candidate"}
    elif score >= 60:
        return {"label": "Fair", "color": "amber", "badge": "Moderate ATS Risk"}
    else:
        return {"label": "Needs Improvement", "color": "rose", "badge": "High ATS Risk"}


def _empty_or_failed_analysis(error_msg):
    return {
        "overall_score": 0,
        "resume_quality_score": 0,
        "job_match_score": None,
        "has_job_description": False,
        "grade": {"label": "Unanalyzed", "color": "slate", "badge": "No Content"},
        "breakdown": {
            "structure": 0,
            "contact": 0,
            "achievements": 0,
            "formatting": 0,
            "readability": 0,
            "skills": 0
        },
        "max_breakdown": {
            "structure": 20,
            "contact": 15,
            "achievements": 20,
            "formatting": 15,
            "readability": 15,
            "skills": 15
        },
        "section_status": {},
        "contact_details": {},
        "achievements_details": {},
        "formatting_details": {},
        "readability_details": {},
        "detected_skills": [],
        "categorized_skills": {"Languages": [], "Frameworks & Libraries": [], "Databases & Cloud": [], "Tools & Methodologies": []},
        "matched_skills": [],
        "missing_skills": [],
        "job_match_details": None,
        "action_verbs_found": 0,
        "quantified_metrics_found": 0,
        "suggestions": [{
            "category": "Error",
            "priority": "High",
            "text": error_msg
        }],
        "summary": error_msg
    }
