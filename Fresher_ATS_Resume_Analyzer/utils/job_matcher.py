"""
Resume-to-Job Matching Utility for Fresher ATS Resume Analyzer.
Compares candidate resume text against job descriptions to calculate
standardized Job Match percentage and identify matched vs missing skills.
Reuses existing ATS scoring and skills extraction routines.
"""

from utils.skills_analyzer import calculate_skills_match
from utils.keyword_matcher import calculate_keyword_match
from utils.ats_checker import detect_sections, calculate_job_match


def match_resume_to_job(resume_text: str, job_description: str):
    """
    Compare resume text against a specific job description.
    Returns:
    - job_match_percentage: float (0.0 to 100.0)
    - matched_skills: list of matched skill names
    - missing_skills: list of missing skill names
    - matched_keywords: list of matched domain keywords
    - missing_keywords: list of missing domain keywords
    - breakdown: dictionary of score component weights
    """
    if not resume_text or not job_description:
        return {
            "job_match_percentage": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "matched_keywords": [],
            "missing_keywords": [],
            "breakdown": {
                "Technical Skills": 0.0,
                "Keywords": 0.0,
                "Projects": 0.0,
                "Education": 0.0
            }
        }

    # 1. Skills match
    skills_res = calculate_skills_match(resume_text, job_description)

    # 2. Keywords match
    kw_res = calculate_keyword_match(resume_text, job_description)

    # 3. Detect sections for project & education weight
    detected_sections = detect_sections(resume_text)

    # 4. Calculate overall job match percentage using standard formula:
    # (Tech Skills * 0.35) + (Keywords * 0.35) + (Projects * 0.20) + (Education * 0.10)
    match_result = calculate_job_match(
        skills_match_pct=skills_res["match_percentage"],
        keyword_match_pct=kw_res["match_percentage"],
        has_projects=detected_sections.get("Projects", False),
        has_education=detected_sections.get("Education", False)
    )

    matching_skills = skills_res.get("matching_skills") or skills_res.get("matched_skills", [])
    missing_skills = skills_res.get("missing_skills", [])
    overall_match = match_result["overall_match_percentage"]

    return {
        "job_match_percentage": overall_match,
        "match_percentage": overall_match,
        "matching_skills": matching_skills,
        "matched_skills": matching_skills,
        "missing_skills": missing_skills,
        "skills_match_percentage": skills_res["match_percentage"],
        "matched_keywords": kw_res["matched_keywords"],
        "missing_keywords": kw_res["missing_keywords"],
        "keyword_match_percentage": kw_res["match_percentage"],
        "breakdown": match_result["breakdown"]
    }
