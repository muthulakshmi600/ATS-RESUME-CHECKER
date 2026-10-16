"""
Skills Analysis and Categorization Engine for Fresher ATS Resume Analyzer.
Detects technical skills across 5 primary categories (Programming, AI/ML, Web, Database, Tools),
extracts requirements from Job Descriptions, and calculates the exact 20-point Skills Score.
"""

import re

# Standardized categorization of technical skills for freshers & entry-level IT roles
SKILL_CATEGORIES = {
    "Programming": [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript",
        "PHP", "Ruby", "Go", "Rust", "R", "Swift", "Kotlin", "Dart"
    ],
    "AI / Machine Learning": [
        "Artificial Intelligence", "Machine Learning", "Deep Learning",
        "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "Keras", "PyTorch",
        "NLP", "Computer Vision", "Data Analysis", "Data Analytics", "Statistics",
        "Matplotlib", "Seaborn", "Power BI", "Tableau"
    ],
    "Web Development": [
        "HTML", "HTML5", "CSS", "CSS3", "JavaScript", "React", "Angular",
        "Vue", "Node.js", "Express", "Flask", "Django", "FastAPI",
        "REST API", "Tailwind", "Bootstrap", "GraphQL", "Jinja"
    ],
    "Databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite",
        "Redis", "Oracle", "NoSQL", "Firebase"
    ],
    "Tools & Platforms": [
        "Git", "GitHub", "GitLab", "VS Code", "Docker", "Kubernetes",
        "Linux", "Unix", "Postman", "CI/CD", "Jira", "AWS", "Azure", "GCP"
    ]
}

# Flat list of all recognized technical skills for lookup
ALL_SKILLS = []
for cat, skills in SKILL_CATEGORIES.items():
    ALL_SKILLS.extend(skills)
# Deduplicate
ALL_SKILLS = list(dict.fromkeys(ALL_SKILLS))


def match_skill_in_text(skill_name: str, text: str) -> bool:
    """Accurate word-boundary detection for skill names in text."""
    s_lower = skill_name.lower().strip()
    text_lower = text.lower()

    if s_lower in ["c++", "c#", "node.js"]:
        pattern = r"(?<!\w)" + re.escape(s_lower) + r"(?!\w)"
    elif s_lower == "c":
        # Special case for single-letter language 'C'
        pattern = r"(?<!\w)c(?!\w)"
    else:
        pattern = r"\b" + re.escape(s_lower) + r"\b"

    return bool(re.search(pattern, text_lower))


def extract_skills_from_text(text: str):
    """
    Scans text against the skill repository and returns:
    - flat list of found skills
    - dictionary of found skills grouped by category
    """
    found_skills = []
    categorized_found = {cat: [] for cat in SKILL_CATEGORIES}

    for cat, skills in SKILL_CATEGORIES.items():
        for s in skills:
            if match_skill_in_text(s, text):
                if s not in found_skills:
                    found_skills.append(s)
                if s not in categorized_found[cat]:
                    categorized_found[cat].append(s)

    return found_skills, categorized_found


def calculate_skills_match(resume_text: str, job_description: str):
    """
    Calculate the exact Skills Match metrics as specified in Section 16 & 25:
    - Formula:
        Skills Match % = Matched Required Skills / Total Required Skills * 100
        Skills Score = Skills Match % * 20 / 100
    Returns:
      dict containing:
        - required_skills: list[str] (Skills detected in the Job Description)
        - resume_skills: list[str] (Skills detected in the Resume)
        - matching_skills: list[str] (Overlap between required & resume)
        - missing_skills: list[str] (Required skills absent from resume)
        - categorized_resume_skills: dict[category -> list[str]]
        - match_percentage: float (0.0 to 100.0)
        - skills_score: float (0.0 to 20.0)
    """
    required_skills, _ = extract_skills_from_text(job_description)
    resume_skills, categorized_resume = extract_skills_from_text(resume_text)

    # If the Job Description mentions no recognized technical skills, fallback to resume skills as baseline
    if not required_skills:
        required_skills = ["Python", "SQL", "Git", "Problem Solving"]

    matching_skills = [s for s in required_skills if s in resume_skills]
    missing_skills = [s for s in required_skills if s not in resume_skills]

    total_req = len(required_skills)
    matched_cnt = len(matching_skills)

    if total_req > 0:
        match_pct = round((matched_cnt / total_req) * 100.0, 1)
        score = round((match_pct * 20.0) / 100.0, 1)
    else:
        match_pct = 0.0
        score = 0.0

    return {
        "required_skills": required_skills,
        "resume_skills": resume_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "categorized_resume_skills": categorized_resume,
        "match_percentage": match_pct,
        "skills_score": score
    }
