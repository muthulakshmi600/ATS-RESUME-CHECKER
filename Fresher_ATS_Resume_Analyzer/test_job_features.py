"""
Unit & Integration Tests for Job Search, Resume Job Matching,
Official Apply URL Handling, Saved Jobs, and Application Tracker.
"""

import os
import sys
import tempfile
import sqlite3

# Set path to import from Fresher_ATS_Resume_Analyzer
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database.database import (
    init_db, get_jobs, get_job_by_id,
    save_job_for_user, unsave_job_for_user, is_job_saved,
    get_saved_jobs_for_user, create_job_application,
    update_job_application_status, delete_job_application,
    get_user_applications, get_user_job_stats, get_user_stats,
    seed_verified_jobs
)
from utils.job_matcher import match_resume_to_job


def test_job_search_and_seed():
    print("Test 1: Verified jobs seeded & search filtering...")
    # Fetch all jobs
    all_jobs = get_jobs()
    assert len(all_jobs) >= 12, f"Expected at least 12 seeded jobs, got {len(all_jobs)}"

    # Check required fields
    for j in all_jobs:
        assert "title" in j and j["title"]
        assert "company" in j and j["company"]
        assert "location" in j and j["location"]
        assert "eligibility" in j and j["eligibility"]
        assert "description" in j and j["description"]
        assert "apply_url" in j

    # Filter by keyword "Python"
    py_jobs = get_jobs(search_query="Python")
    assert len(py_jobs) > 0, "Expected at least 1 Python job"
    for j in py_jobs:
        assert "python" in (j["title"] + " " + j["description"] + " " + j["company"]).lower()

    # Filter by Location "Bangalore"
    blr_jobs = get_jobs(location="Bangalore")
    assert len(blr_jobs) > 0, "Expected Bangalore jobs"

    # Filter by Job Type "Full-Time"
    ft_jobs = get_jobs(job_type="Full-Time")
    assert len(ft_jobs) > 0, "Expected Full-Time jobs"

    print(f"  [PASS] Found {len(all_jobs)} verified jobs. Search filters working properly.")


def test_missing_apply_url():
    print("Test 2: Missing application URL behavior...")
    # We seeded a specific job with empty apply_url (e.g. National Fresher Campus Placement Drive)
    all_jobs = get_jobs()
    no_url_jobs = [j for j in all_jobs if not j.get("apply_url")]
    assert len(no_url_jobs) >= 1, "Expected at least 1 job with empty apply_url to test disabled state"
    assert no_url_jobs[0]["apply_url"] == "", "Apply URL should be empty string"
    print(f"  [PASS] Verified listing with unavailable URL: '{no_url_jobs[0]['title']}' - apply_url is empty.")


def test_resume_job_matching():
    print("Test 3: Resume to Job matching logic...")
    sample_resume = """
    Rohan Sharma
    Email: rohan.sharma@example.com | Phone: 9876543210 | Bangalore
    B.E. Computer Science and Engineering, 2024 (CGPA 8.6)

    Technical Skills:
    Languages: Python, Java, SQL, C++
    Frameworks: Django, Flask, Pandas, NumPy, Scikit-learn
    Tools & DB: Git, GitHub, MySQL, PostgreSQL, Docker

    Projects:
    1. Automated ATS Analyzer: Built a full-stack Python application with NLP keyword extraction and SQLite.
    2. Predictive Healthcare Model: Built an ML classifier with Scikit-learn, Pandas, and evaluated ROC-AUC.
    """

    job = get_jobs(search_query="Python")[0]
    match_result = match_resume_to_job(sample_resume, job["description"])

    assert "match_percentage" in match_result
    assert 0 <= match_result["match_percentage"] <= 100
    assert "matching_skills" in match_result
    assert "missing_skills" in match_result
    assert "python" in [s.lower() for s in match_result["matching_skills"]]
    assert len(match_result["matching_skills"]) > 0

    print(f"  [PASS] Job: '{job['title']}' at '{job['company']}' -> Match: {match_result['match_percentage']}%")
    print(f"    Matched Skills: {match_result['matching_skills']}")
    print(f"    Missing Skills: {match_result['missing_skills']}")


def test_saved_jobs_lifecycle():
    print("Test 4: Saved Jobs bookmarking & user isolation...")
    test_user_1 = 9991
    test_user_2 = 9992

    all_jobs = get_jobs()
    job_1 = all_jobs[0]
    job_2 = all_jobs[1]

    # Clean any prior saved
    unsave_job_for_user(test_user_1, job_1["id"])
    unsave_job_for_user(test_user_1, job_2["id"])
    unsave_job_for_user(test_user_2, job_1["id"])

    # User 1 saves job 1
    assert not is_job_saved(test_user_1, job_1["id"])
    save_job_for_user(test_user_1, job_1["id"])
    assert is_job_saved(test_user_1, job_1["id"])

    # User 2 should NOT have job 1 saved
    assert not is_job_saved(test_user_2, job_1["id"])

    # User 1 saved list
    saved_1 = get_saved_jobs_for_user(test_user_1)
    assert len(saved_1) == 1
    assert saved_1[0]["id"] == job_1["id"]

    # Unsave
    unsave_job_for_user(test_user_1, job_1["id"])
    assert not is_job_saved(test_user_1, job_1["id"])
    assert len(get_saved_jobs_for_user(test_user_1)) == 0

    print("  [PASS] Saved Jobs bookmarking, isolation, and un-saving verified.")


def test_application_tracker_crud():
    print("Test 5: Application Tracker CRUD & status transitions...")
    test_user = 9993

    # Clean existing
    existing = get_user_applications(test_user)
    for app in existing:
        delete_job_application(test_user, app["id"])

    # 1. Create Application
    app_id = create_job_application(
        user_id=test_user,
        company="Zoho Corporation",
        role="Software Development Engineer - Fresher",
        apply_url="https://www.zoho.com/careers/freshers",
        status="Applied",
        applied_date="2026-10-14",
        notes="Applied via official portal after ATS 88% match."
    )
    assert app_id > 0

    # 2. Retrieve applications
    apps = get_user_applications(test_user)
    assert len(apps) == 1
    app = apps[0]
    assert app["company"] == "Zoho Corporation"
    assert app["status"] == "Applied"
    assert app["notes"] == "Applied via official portal after ATS 88% match."

    # 3. Update status to Interview
    ok = update_job_application_status(test_user, app_id, "Interview", "Technical round scheduled for next Monday.")
    assert ok

    updated_apps = get_user_applications(test_user)
    assert updated_apps[0]["status"] == "Interview"
    assert "Technical round" in updated_apps[0]["notes"]

    # 4. Check user stats
    stats = get_user_job_stats(test_user)
    assert stats["total"] == 1
    assert stats["interview"] == 1
    assert stats["applied"] == 0

    # 5. Delete application
    del_ok = delete_job_application(test_user, app_id)
    assert del_ok
    assert len(get_user_applications(test_user)) == 0

    print("  [PASS] Application Tracker CRUD, status updates, and stats verified.")


def run_all_tests():
    print("=" * 60)
    print("RUNNING FRESHER ATS JOB SEARCH & APPLY FEATURE TEST SUITE")
    print("=" * 60)
    init_db()
    test_job_search_and_seed()
    test_missing_apply_url()
    test_resume_job_matching()
    test_saved_jobs_lifecycle()
    test_application_tracker_crud()
    print("=" * 60)
    print("ALL JOB SEARCH & APPLY TESTS PASSED (5/5)!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
