"""
Comprehensive ATS Compatibility Scoring & Analysis Engine.
Calculates the exact 100-point ATS Compatibility Score, separate Job Match %,
Fresher Resume Checklist, and actionable grounded improvement suggestions.
"""

import re
from utils.keyword_matcher import calculate_keyword_match
from utils.skills_analyzer import calculate_skills_match
from utils.formatting_checker import (
    detect_sections,
    calculate_section_score,
    analyze_contact_information,
    analyze_formatting
)


def extract_section_text(text: str, section_name: str) -> str:
    """
    Attempt to isolate text belonging to a specific resume section
    (e.g., Projects, Internship, Summary) for relevance scoring.
    """
    text_lower = text.lower()
    headers = [
        "professional summary", "summary", "career objective", "objective",
        "technical skills", "skills", "education", "projects", "academic projects",
        "internship", "internships", "training", "certifications", "contact"
    ]

    target_keywords = {
        "project": ["project", "projects", "academic projects", "key projects"],
        "internship": ["internship", "internships", "training", "experience"],
        "summary": ["summary", "career objective", "objective", "profile"]
    }

    words = target_keywords.get(section_name, [section_name])
    start_pos = -1
    for w in words:
        match = re.search(r"\b" + re.escape(w) + r"\b", text_lower)
        if match:
            start_pos = match.end()
            break

    if start_pos == -1:
        return ""

    # End position is the start of the next header
    end_pos = len(text)
    remaining_text = text_lower[start_pos:]
    for h in headers:
        if h not in words:
            m = re.search(r"\b" + re.escape(h) + r"\b", remaining_text)
            if m and (start_pos + m.start()) < end_pos:
                end_pos = start_pos + m.start()

    return text[start_pos:end_pos].strip()


def calculate_job_relevance(resume_text: str, job_description: str, matching_keywords: list):
    """
    Calculate the exact 10-point Job Relevance Score as specified in Section 19:
    - Project Relevance      = 4
    - Internship Relevance   = 3
    - Summary Relevance      = 3
    TOTAL = 10 points
    Evaluates whether the student's projects, internship/training, and summary
    reflect the target role's key concepts.
    """
    project_text = extract_section_text(resume_text, "project")
    internship_text = extract_section_text(resume_text, "internship")
    summary_text = extract_section_text(resume_text, "summary")

    # If section boundaries could not be cleanly isolated, search within the full resume text
    if not project_text and "project" in resume_text.lower():
        project_text = resume_text

    # Compute keyword overlaps in each section
    project_matches = sum(1 for kw in matching_keywords if kw.lower() in project_text.lower())
    internship_matches = sum(1 for kw in matching_keywords if kw.lower() in internship_text.lower())
    summary_matches = sum(1 for kw in matching_keywords if kw.lower() in summary_text.lower())

    # Project Relevance (max 4 pts)
    if len(matching_keywords) > 0 and project_matches >= 3:
        project_score = 4.0
    elif project_matches >= 1:
        project_score = 2.5
    elif project_text:
        project_score = 1.5
    else:
        project_score = 0.5

    # Internship / Training Relevance (max 3 pts)
    if internship_matches >= 2:
        internship_score = 3.0
    elif internship_matches >= 1:
        internship_score = 2.0
    elif internship_text:
        internship_score = 1.0
    else:
        internship_score = 0.5

    # Summary / Objective Relevance (max 3 pts)
    if summary_matches >= 2:
        summary_score = 3.0
    elif summary_matches >= 1:
        summary_score = 2.0
    elif summary_text:
        summary_score = 1.0
    else:
        summary_score = 0.5

    total = round(project_score + internship_score + summary_score, 1)
    return {
        "job_relevance_score": min(total, 10.0),
        "project_relevance": project_score,
        "internship_relevance": internship_score,
        "summary_relevance": summary_score,
        "max_score": 10.0
    }


def calculate_job_match(skills_match_pct: float, keyword_match_pct: float, has_projects: bool, has_education: bool):
    """
    Calculate the separate Job Match percentage and breakdown as specified in Section 22:
    Breakdown:
      - Technical Skills = XX%
      - Keywords         = XX%
      - Projects         = XX%
      - Education        = XX%
    Note: Job Match is an application-generated similarity metric, NOT a hiring probability.
    """
    tech_skills_pct = round(skills_match_pct, 1)
    keywords_pct = round(keyword_match_pct, 1)
    projects_pct = 90.0 if has_projects else 40.0
    education_pct = 95.0 if has_education else 50.0

    # Weighted composite similarity:
    # Skills 35%, Keywords 35%, Projects 20%, Education 10%
    overall_match = round(
        (tech_skills_pct * 0.35) +
        (keywords_pct * 0.35) +
        (projects_pct * 0.20) +
        (education_pct * 0.10),
        1
    )

    return {
        "overall_match_percentage": overall_match,
        "breakdown": {
            "Technical Skills": tech_skills_pct,
            "Keywords": keywords_pct,
            "Projects": projects_pct,
            "Education": education_pct
        }
    }


def generate_fresher_checklist(detected_sections: dict, contact_info: dict):
    """
    Build the Fresher Resume Checklist as specified in Section 26:
    - Education
    - Technical Skills
    - Academic Projects
    - Internship / Training
    - Certifications
    - LinkedIn
    - GitHub
    """
    items = [
        {
            "label": "Education",
            "status": detected_sections.get("Education", False),
            "tip": "Include degree, college name, branch, and CGPA/percentage."
        },
        {
            "label": "Technical Skills",
            "status": detected_sections.get("Technical Skills", False),
            "tip": "Categorize skills into Programming, Web, Databases, and Tools."
        },
        {
            "label": "Academic Projects",
            "status": detected_sections.get("Projects", False),
            "tip": "Highlight 2-3 academic or personal projects detailing the stack used and your role."
        },
        {
            "label": "Internship / Training",
            "status": detected_sections.get("Internship / Training", False),
            "tip": "Add any industrial training, virtual internships, or college workshops."
        },
        {
            "label": "Certifications",
            "status": detected_sections.get("Certifications", False),
            "tip": "List verified certifications from Coursera, Udemy, NPTEL, HackerRank, etc."
        },
        {
            "label": "LinkedIn Profile",
            "status": contact_info.get("linkedin_found", False),
            "tip": "Add a link to your updated LinkedIn profile to build professional credibility."
        },
        {
            "label": "GitHub Profile",
            "status": contact_info.get("github_found", False),
            "tip": "Add your GitHub profile if you have relevant code repositories or projects."
        }
    ]
    return items


def generate_improvement_suggestions(
    missing_keywords: list,
    missing_skills: list,
    detected_sections: dict,
    contact_info: dict,
    formatting_details: list
):
    """
    Synthesize actionable improvement suggestions grounded strictly in detected issues
    as specified in Section 28. Never invent fake data or skills.
    """
    suggestions = []

    # 1. Missing Technical Skills
    if missing_skills:
        top_missing = missing_skills[:4]
        skills_str = ", ".join(top_missing)
        suggestions.append(
            f"Target Skills Alignment: The job description emphasizes {skills_str}. "
            "Consider adding these to your Technical Skills section ONLY if you genuinely have knowledge or experience with them."
        )

    # 2. Missing Key Terminology / Frameworks
    other_missing_kw = [k for k in missing_keywords if k not in missing_skills][:3]
    if other_missing_kw:
        kw_str = ", ".join(other_missing_kw)
        suggestions.append(
            f"Role-Specific Terminology: Consider integrating terms like {kw_str} into your project descriptions if you used them in your coursework or projects."
        )

    # 3. Missing Sections for Freshers
    if not detected_sections.get("Projects", False):
        suggestions.append(
            "Add an 'Academic Projects' section: As a fresher, personal and college projects are the primary proof of your hands-on coding abilities."
        )
    if not detected_sections.get("Internship / Training", False):
        suggestions.append(
            "Add Internship or Training Details: If you completed industrial training, an internship, or a boot camp, create a dedicated section for it."
        )
    if not detected_sections.get("Certifications", False):
        suggestions.append(
            "Highlight Certifications & Courses: Add any relevant certifications (e.g., Python, SQL, Cloud) to demonstrate self-directed learning."
        )

    # 4. Contact & Online Presence
    if not contact_info.get("github_found", False):
        suggestions.append(
            "Add GitHub Link: Including your GitHub profile allows recruiters to view your project source code and commit history."
        )
    if not contact_info.get("linkedin_found", False):
        suggestions.append(
            "Add LinkedIn URL: Providing a clean LinkedIn profile link makes it easy for hiring managers to verify your background."
        )

    # 5. Formatting Feedback
    for rule in formatting_details:
        if not rule["passed"]:
            if "paragraph" in rule["rule"].lower():
                suggestions.append(
                    "Format with Bullet Points: Break long paragraphs into concise 1-2 line bullet points starting with strong action verbs."
                )
            elif "special" in rule["rule"].lower():
                suggestions.append(
                    "Simplify Typography: Remove decorative graphics or unusual symbols that may confuse standard applicant tracking parsers."
                )
            elif "heading" in rule["rule"].lower():
                suggestions.append(
                    "Use Standard Headings: Use clear section headers like 'Education', 'Technical Skills', and 'Projects' for seamless parsing."
                )

    if not suggestions:
        suggestions.append(
            "Your resume is strongly structured! Continue tailoring your project descriptions to match the specific tools mentioned in target job descriptions."
        )

    return suggestions


def analyze_resume_ats(resume_text: str, job_description: str, resume_metadata: dict):
    """
    Main controller for ATS Analysis:
    Combines all 6 components to produce the exact 100-point ATS Compatibility Score:
      1. Keyword Match       = 30 pts
      2. Skills Match        = 20 pts
      3. Resume Sections     = 15 pts
      4. Formatting          = 15 pts
      5. Job Relevance       = 10 pts
      6. Contact Information = 10 pts
      TOTAL                  = 100 pts
    Also produces:
      - Separate Job Match Score (%)
      - Matched & Missing Keywords
      - Skills Analysis
      - Fresher Checklist
      - Grounded Suggestions
    """
    # 1. Keywords (30 pts)
    kw_result = calculate_keyword_match(resume_text, job_description)

    # 2. Skills (20 pts)
    skills_result = calculate_skills_match(resume_text, job_description)

    # 3. Sections (15 pts)
    detected_sections = detect_sections(resume_text)
    section_score, section_breakdown = calculate_section_score(detected_sections)

    # 4. Formatting (15 pts)
    format_result = analyze_formatting(resume_text, resume_metadata)

    # 5. Job Relevance (10 pts)
    relevance_result = calculate_job_relevance(
        resume_text,
        job_description,
        kw_result["matched_keywords"]
    )

    # 6. Contact Information (10 pts)
    contact_result = analyze_contact_information(resume_text)

    # Total ATS Compatibility Score (100 pts)
    final_ats_score = round(
        kw_result["keyword_score"] +
        skills_result["skills_score"] +
        section_score +
        format_result["formatting_score"] +
        relevance_result["job_relevance_score"] +
        contact_result["contact_score"],
        1
    )
    final_ats_score = min(max(final_ats_score, 0.0), 100.0)

    # Separate Job Match (%)
    job_match_result = calculate_job_match(
        skills_match_pct=skills_result["match_percentage"],
        keyword_match_pct=kw_result["match_percentage"],
        has_projects=detected_sections.get("Projects", False),
        has_education=detected_sections.get("Education", False)
    )

    # Fresher Checklist
    checklist = generate_fresher_checklist(detected_sections, contact_result)

    # Actionable Suggestions
    suggestions = generate_improvement_suggestions(
        missing_keywords=kw_result["missing_keywords"],
        missing_skills=skills_result["missing_skills"],
        detected_sections=detected_sections,
        contact_info=contact_result,
        formatting_details=format_result["details"]
    )

    return {
        "final_ats_score": final_ats_score,
        "score_breakdown": {
            "keyword_match": {"score": kw_result["keyword_score"], "max": 30.0, "pct": kw_result["match_percentage"]},
            "skills_match": {"score": skills_result["skills_score"], "max": 20.0, "pct": skills_result["match_percentage"]},
            "resume_sections": {"score": section_score, "max": 15.0, "details": section_breakdown},
            "formatting": {"score": format_result["formatting_score"], "max": 15.0, "details": format_result["details"]},
            "job_relevance": {"score": relevance_result["job_relevance_score"], "max": 10.0, "details": relevance_result},
            "contact_information": {"score": contact_result["contact_score"], "max": 10.0, "details": contact_result}
        },
        "job_match": job_match_result,
        "keywords": kw_result,
        "skills": skills_result,
        "detected_sections": detected_sections,
        "contact_info": contact_result,
        "formatting": format_result,
        "fresher_checklist": checklist,
        "improvement_suggestions": suggestions
    }
