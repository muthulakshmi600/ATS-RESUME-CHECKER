"""
Automated Verification Script for ATS Backend Functions
Tests:
1. SQLite Database initialization & schema
2. Resume text extraction from PDF and DOCX
3. TF-IDF Cosine Similarity calculation
4. Skill matching (matched vs missing skills)
5. Flask test client endpoints (GET /, GET /job, GET /upload, GET /candidates)
"""

import os
import json
import sqlite3
import app

def test_system():
    print("--- 1. Testing Database Initialization ---")
    app.init_db()
    with app.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Active tables in ats.db: {tables}")
        assert "jobs" in tables, "Table 'jobs' is missing"
        assert "candidates" in tables, "Table 'candidates' is missing"
    print("[PASS] Database tables verified.")

    print("\n--- 2. Testing Text Extraction ---")
    # Test DOCX extraction
    alex_docx = os.path.join("sample_resumes", "alex_python_developer.docx")
    alex_text = app.extract_resume_text(alex_docx, "alex_python_developer.docx")
    print(f"Alex DOCX extracted length: {len(alex_text)} characters")
    assert "Python" in alex_text and "Flask" in alex_text, "Failed to extract skills from DOCX"
    print("[PASS] DOCX text extraction verified.")

    # Test PDF extraction
    sarah_pdf = os.path.join("sample_resumes", "sarah_data_scientist.pdf")
    sarah_text = app.extract_resume_text(sarah_pdf, "sarah_data_scientist.pdf")
    print(f"Sarah PDF extracted length: {len(sarah_text)} characters")
    assert "Sarah" in sarah_text and "Python" in sarah_text, "Failed to extract skills from PDF"
    print("[PASS] PDF text extraction verified.")

    # Test Marketing PDF (low match test)
    david_pdf = os.path.join("sample_resumes", "david_marketing_specialist.pdf")
    david_text = app.extract_resume_text(david_pdf, "david_marketing_specialist.pdf")
    print(f"David PDF extracted length: {len(david_text)} characters")
    assert "Marketing" in david_text, "Failed to extract text from David's PDF"
    print("[PASS] Secondary PDF text extraction verified.")

    print("\n--- 3. Testing Job Posting & Matching Logic ---")
    with open("sample_job.txt", "r", encoding="utf-8") as f:
        job_content = f.read()

    # Calculate match for Alex (Python Dev - should be high match)
    alex_score, alex_matched, alex_missing = app.match_resume_with_job(alex_text, job_content)
    print(f"Alex Match Score: {alex_score}%")
    print(f"Alex Matched Skills: {alex_matched}")
    print(f"Alex Missing Skills: {alex_missing}")
    assert alex_score > 30.0, "Expected Alex to have a significant match score"
    assert "Python" in alex_matched and "Flask" in alex_matched, "Expected Python and Flask to be matched for Alex"
    print("[PASS] High match candidate calculation verified.")

    # Calculate match for David (Marketing - should be low match)
    david_score, david_matched, david_missing = app.match_resume_with_job(david_text, job_content)
    print(f"David Match Score: {david_score}%")
    print(f"David Matched Skills: {david_matched}")
    print(f"David Missing Skills: {david_missing}")
    assert david_score < alex_score, "Marketing candidate should score lower than Python candidate"
    print("[PASS] Low match candidate distinction verified.")

    print("\n--- 4. Testing Flask Endpoints with Test Client ---")
    client = app.app.test_client()

    # 4.1 Test GET /
    res = client.get("/")
    assert res.status_code == 200, f"Dashboard returned {res.status_code}"
    print("[PASS] GET / (Dashboard) -> 200 OK")

    # 4.2 Test POST /job
    res = client.post("/job", data={
        "title": "Junior Python Developer",
        "description": job_content
    }, follow_redirects=True)
    assert res.status_code == 200, f"Job creation returned {res.status_code}"
    print("[PASS] POST /job (Job creation) -> 200 OK")

    # Fetch inserted job ID
    with app.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM jobs WHERE title = 'Junior Python Developer'")
        job_id = cursor.fetchone()[0]

    # 4.3 Test POST /upload with DOCX resume
    with open(alex_docx, "rb") as f:
        res = client.post("/upload", data={
            "name": "Alex Johnson",
            "email": "alex.johnson@example.com",
            "phone": "+1 555-014-2391",
            "job_id": job_id,
            "resume_file": (f, "alex_python_developer.docx")
        }, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200, f"Upload returned {res.status_code}"
    assert b"Analysis Complete" in res.data or b"Match Report" in res.data, "Upload result preview not found in response"
    print("[PASS] POST /upload (DOCX resume upload & match preview) -> 200 OK")

    # 4.4 Test POST /upload with PDF resume
    with open(sarah_pdf, "rb") as f:
        res = client.post("/upload", data={
            "name": "Sarah Chen",
            "email": "sarah.chen@example.com",
            "phone": "+1 555-234-8890",
            "job_id": job_id,
            "resume_file": (f, "sarah_data_scientist.pdf")
        }, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200, f"Upload returned {res.status_code}"
    print("[PASS] POST /upload (PDF resume upload & match preview) -> 200 OK")

    # 4.5 Test GET /candidates
    res = client.get("/candidates")
    assert res.status_code == 200
    assert b"Alex Johnson" in res.data and b"Sarah Chen" in res.data
    print("[PASS] GET /candidates -> 200 OK (Contains uploaded candidates)")

    # 4.6 Test search filtering
    res = client.get("/candidates?search=Alex")
    assert res.status_code == 200
    assert b"Alex Johnson" in res.data
    print("[PASS] GET /candidates?search=Alex -> 200 OK (Search verified)")

    # 4.7 Test Status update
    with app.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM candidates WHERE name = 'Alex Johnson'")
        alex_cand_id = cursor.fetchone()[0]

    res = client.post(f"/update_status/{alex_cand_id}", data={"status": "Shortlisted"}, follow_redirects=True)
    assert res.status_code == 200
    with app.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM candidates WHERE id = ?", (alex_cand_id,))
        new_status = cursor.fetchone()[0]
        assert new_status == "Shortlisted", f"Expected 'Shortlisted', got {new_status}"
    print("[PASS] POST /update_status -> Status updated to 'Shortlisted'")

    # 4.8 Test GET /job/<job_id> (Target Job Details & Talent Pool Heatmap)
    res = client.get(f"/job/{job_id}")
    assert res.status_code == 200
    assert b"Talent Pool Skill Gap" in res.data
    assert b"Ranked Candidates" in res.data or b"Ranked Applicants" in res.data or b"Pipeline" in res.data
    print(f"[PASS] GET /job/{job_id} -> 200 OK (Target Job Details & Heatmap verified)")

    # 4.9 Test GET /job/<job_id>/export (CSV Export)
    res = client.get(f"/job/{job_id}/export")
    assert res.status_code == 200
    assert res.headers["Content-Type"].startswith("text/csv")
    assert b"Candidate Name" in res.data and b"Alex Johnson" in res.data
    print(f"[PASS] GET /job/{job_id}/export -> 200 OK (CSV Export generated & verified)")

    # 4.10 Test POST /job/status/<job_id> (Status toggle)
    res = client.post(f"/job/status/{job_id}", data={"status": "Paused"}, follow_redirects=True)
    assert res.status_code == 200
    with app.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM jobs WHERE id = ?", (job_id,))
        job_status = cursor.fetchone()[0]
        assert job_status == "Paused", f"Expected job status 'Paused', got {job_status}"
    print("[PASS] POST /job/status -> Status updated to 'Paused'")

    # 4.11 Test GET /job?status=Paused (Status filtering)
    res = client.get("/job?status=Paused")
    assert res.status_code == 200
    assert b"Junior Python Developer" in res.data
    print("[PASS] GET /job?status=Paused -> 200 OK (Job status filter verified)")

    print("\n=======================================================")
    print(" ALL BACKEND AND INTEGRATION TESTS PASSED SUCCESSFULLY! ")
    print("=======================================================")

if __name__ == "__main__":
    test_system()
