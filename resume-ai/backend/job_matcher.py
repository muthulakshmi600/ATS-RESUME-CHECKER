"""
Intelligent Job Matcher Module for ResumeAI ATS.
Compares candidate resume text and extracted skills against verified jobs catalog.
Calculates transparent Job Match Percentage, matched vs missing skills,
human-readable match explanations, and filters by relevance threshold.
"""

import re
import json
import os
import urllib.parse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import get_all_jobs, get_job_by_id
from analyzer import _check_skills, UNIVERSAL_SKILLS

DEFAULT_MATCH_THRESHOLD = 75

def generate_job_platform_urls(job):
    """
    Generates official verified URLs for:
    1. LinkedIn Jobs search or direct listing
    2. Naukri.com search or direct listing
    3. Company official career portal
    """
    title = (job.get('title') or '').strip()
    company = (job.get('company') or '').strip()
    location = (job.get('location') or '').strip()

    # 1. LinkedIn URL: Direct listing if verified, otherwise official LinkedIn Jobs query
    if job.get('linkedin_url') and str(job['linkedin_url']).startswith('http'):
        linkedin_url = job['linkedin_url']
        linkedin_is_direct = True
    else:
        # e.g. keywords: "Python Developer Zoho Corporation" or "Python Developer"
        query_parts = [title]
        if company and len(company) <= 30:
            query_parts.append(company)
        keywords = ' '.join(query_parts)

        # Primary location (e.g. Bangalore, Chennai)
        primary_loc = location.split('/')[0].split('(')[0].strip() if location else ""
        params = {'keywords': keywords}
        if primary_loc:
            params['location'] = primary_loc

        linkedin_url = f"https://www.linkedin.com/jobs/search/?{urllib.parse.urlencode(params)}"
        linkedin_is_direct = False

    # 2. Naukri URL: Direct listing if verified, otherwise official Naukri Jobs query
    if job.get('naukri_url') and str(job['naukri_url']).startswith('http'):
        naukri_url = job['naukri_url']
        naukri_is_direct = True
    else:
        clean_title_slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
        primary_loc = location.split('/')[0].split('(')[0].strip() if location else ""
        naukri_params = {'k': title}
        if primary_loc:
            naukri_params['l'] = primary_loc

        if clean_title_slug:
            naukri_url = f"https://www.naukri.com/{clean_title_slug}-jobs?{urllib.parse.urlencode(naukri_params)}"
        else:
            naukri_url = f"https://www.naukri.com/jobs?{urllib.parse.urlencode(naukri_params)}"
        naukri_is_direct = False

    # 3. Company Application URL
    app_url = job.get('application_url') or ''
    has_company_url = bool(app_url and str(app_url).startswith('http'))

    return {
        'linkedin_search_url': linkedin_url,
        'linkedin_is_direct': linkedin_is_direct,
        'naukri_search_url': naukri_url,
        'naukri_is_direct': naukri_is_direct,
        'has_company_url': has_company_url,
        'has_application_url': has_company_url,
        'company_application_url': app_url if has_company_url else None
    }


def calculate_single_job_match(resume_text, job, detected_skills=None):
    """
    Calculates detailed match statistics for a single job against resume text.
    Returns:
    - job_match_percentage: int (0 to 100)
    - matched_skills: list of skill strings present in both resume and job
    - missing_skills: list of required skills absent in resume
    - skill_match_percentage: float
    - semantic_similarity_percentage: float
    - match_explanation: str
    - is_good_match: bool (relative to threshold)
    """
    resume_lower = resume_text.lower() if resume_text else ""
    
    # 1. Resolve detected resume skills
    if detected_skills is None:
        _, detected_skills, _ = _check_skills(resume_lower)
    
    resume_skills_lower = {s.lower() for s in detected_skills}

    # 2. Required skills from job
    required_skills = job.get('required_skills') or []
    if isinstance(required_skills, str):
        try:
            required_skills = json.loads(required_skills)
        except Exception:
            required_skills = [s.strip() for s in required_skills.split(',') if s.strip()]

    matched_skills = []
    missing_skills = []

    for req in required_skills:
        req_clean = req.strip()
        req_lower = req_clean.lower()
        # Direct skill match or word boundary regex match in resume text
        if req_lower in resume_skills_lower:
            matched_skills.append(req_clean)
        elif re.search(r'(?:^|\W)' + re.escape(req_lower) + r'(?:$|\W)', resume_lower):
            matched_skills.append(req_clean)
        else:
            missing_skills.append(req_clean)

    # Calculate skill match ratio
    total_req = max(1, len(required_skills))
    skill_match_pct = round((len(matched_skills) / total_req) * 100, 1)

    # 3. Semantic TF-IDF Similarity
    job_full_text = f"{job.get('title', '')} {job.get('company', '')} {job.get('description', '')} {' '.join(required_skills)}"
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=1200)
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_full_text])
        raw_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        # Rescale realistic resume-to-job text cosine similarity (typical range 0.12 - 0.55)
        semantic_pct = min(100.0, max(20.0, round(raw_sim * 165.0, 1)))
    except Exception:
        semantic_pct = skill_match_pct

    # 4. Composite Job Match Percentage (60% Skill Match + 40% Semantic Content Match)
    job_match_score = int(round(0.60 * skill_match_pct + 0.40 * semantic_pct))
    job_match_score = min(100, max(0, job_match_score))

    # 5. Human-readable Match Explanation
    if job_match_score >= 75:
        match_explanation = (
            f"Strong match ({job_match_score}%). Your resume directly satisfies {len(matched_skills)} of {len(required_skills)} "
            f"key competencies ({', '.join(matched_skills[:3]) if matched_skills else 'core tools'}). Highly aligned with role requirements."
        )
    elif job_match_score >= 50:
        missing_preview = f", but lacks {', '.join(missing_skills[:2])}" if missing_skills else ""
        match_explanation = (
            f"Moderate match ({job_match_score}%). Foundational qualifications detected in "
            f"{', '.join(matched_skills[:2]) if matched_skills else 'programming'}{missing_preview}."
        )
    else:
        missing_preview = f"like {', '.join(missing_skills[:3])} " if missing_skills else ""
        match_explanation = (
            f"Partial alignment ({job_match_score}%). Core technical qualifications {missing_preview}are currently not emphasized in your resume."
        )

    platform_urls = generate_job_platform_urls(job)

    return {
        "job_match_percentage": job_match_score,
        "skill_match_percentage": skill_match_pct,
        "semantic_similarity_percentage": semantic_pct,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_explanation": match_explanation,
        "has_application_url": platform_urls['has_application_url'],
        "has_company_url": platform_urls['has_company_url'],
        "company_application_url": platform_urls['company_application_url'],
        "linkedin_search_url": platform_urls['linkedin_search_url'],
        "linkedin_is_direct": platform_urls['linkedin_is_direct'],
        "naukri_search_url": platform_urls['naukri_search_url'],
        "naukri_is_direct": platform_urls['naukri_is_direct']
    }


def match_jobs_against_resume(
    resume_text,
    detected_skills=None,
    threshold=DEFAULT_MATCH_THRESHOLD,
    search=None,
    skill=None,
    location=None,
    job_type=None,
    is_remote=None
):
    """
    Ranks all catalog jobs according to match percentage against candidate's resume text.
    Filters by optional criteria and sorts by job_match_percentage descending.
    """
    all_jobs = get_all_jobs(
        search=search,
        skill=skill,
        location=location,
        job_type=job_type,
        is_remote=is_remote
    )

    if not resume_text:
        # If no resume provided, return jobs with 0 match
        for j in all_jobs:
            p_urls = generate_job_platform_urls(j)
            j['job_match_percentage'] = 0
            j['matched_skills'] = []
            j['missing_skills'] = j.get('required_skills', [])
            j['is_good_match'] = False
            j['match_explanation'] = "Upload your resume to calculate a personalized job match percentage."
            j.update(p_urls)
        return {
            "success": True,
            "jobs": all_jobs,
            "threshold": threshold,
            "total_jobs": len(all_jobs),
            "good_matches_count": 0
        }

    # Extract skills if not provided
    if detected_skills is None:
        _, detected_skills, _ = _check_skills(resume_text.lower())

    matched_job_list = []
    good_matches_count = 0

    for job in all_jobs:
        match_data = calculate_single_job_match(resume_text, job, detected_skills=detected_skills)
        job_entry = dict(job)
        job_entry['job_match_percentage'] = match_data['job_match_percentage']
        job_entry['skill_match_percentage'] = match_data['skill_match_percentage']
        job_entry['semantic_similarity_percentage'] = match_data['semantic_similarity_percentage']
        job_entry['matched_skills'] = match_data['matched_skills']
        job_entry['missing_skills'] = match_data['missing_skills']
        job_entry['match_explanation'] = match_data['match_explanation']
        job_entry['has_application_url'] = match_data['has_application_url']
        job_entry['has_company_url'] = match_data['has_company_url']
        job_entry['company_application_url'] = match_data['company_application_url']
        job_entry['linkedin_search_url'] = match_data['linkedin_search_url']
        job_entry['linkedin_is_direct'] = match_data['linkedin_is_direct']
        job_entry['naukri_search_url'] = match_data['naukri_search_url']
        job_entry['naukri_is_direct'] = match_data['naukri_is_direct']
        job_entry['is_good_match'] = match_data['job_match_percentage'] >= threshold

        if job_entry['is_good_match']:
            good_matches_count += 1

        matched_job_list.append(job_entry)

    # Sort by Job Match Percentage descending (strongest matches first)
    matched_job_list.sort(key=lambda x: (x['job_match_percentage'], len(x['matched_skills'])), reverse=True)

    return {
        "success": True,
        "jobs": matched_job_list,
        "threshold": threshold,
        "total_jobs": len(matched_job_list),
        "good_matches_count": good_matches_count,
        "candidate_skills_detected": detected_skills
    }

