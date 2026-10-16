"""
Integration test suite for ResumeAI ATS Resume Checker.
Tests:
1. Health check endpoint
2. Sample resumes endpoint
3. Valid PDF parsing and 6-factor score calculation
4. Valid DOCX parsing and job description matching
5. Empty (0-byte) file upload validation
6. Scanned PDF (image-only, no selectable text) OCR rejection
7. Unsupported file format validation
8. Short text (<40 chars) document validation
9. Persistence in SQLite database and history unpacking
"""

import os
import io
import requests
import pymupdf

BASE_URL = "http://127.0.0.1:5050"
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(PROJECT_DIR, "sample_resumes", "sample_ai_ml_engineer.pdf")
DOCX_PATH = os.path.join(PROJECT_DIR, "sample_resumes", "sample_python_developer.docx")

def run_all_tests():
    print("==================================================")
    print("STARTING ATS RESUME ANALYZER WORKFLOW TESTS")
    print("==================================================")
    passed = 0
    total = 0

    # 1. Health check
    total += 1
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200 and r.json().get("status") == "ok", f"Health check failed: {r.text}"
    print("[PASS] TEST 1: Health Check Passed")
    passed += 1

    # 2. Sample Resumes Endpoint
    total += 1
    r_pdf = requests.get(f"{BASE_URL}/api/sample-resume?type=pdf")
    r_docx = requests.get(f"{BASE_URL}/api/sample-resume?type=docx")
    assert r_pdf.status_code == 200 and len(r_pdf.content) > 1000, "Sample PDF endpoint failed"
    assert r_docx.status_code == 200 and len(r_docx.content) > 1000, "Sample DOCX endpoint failed"
    print(f"[PASS] TEST 2: /api/sample-resume endpoint returned valid files (PDF: {len(r_pdf.content)}B, DOCX: {len(r_docx.content)}B)")
    passed += 1

    # 3. Valid PDF Resume Upload & ATS Scoring
    total += 1
    with open(PDF_PATH, "rb") as f:
        r = requests.post(
            f"{BASE_URL}/api/analyze",
            files={"resume": ("sample_ai_ml_engineer.pdf", f, "application/pdf")},
            data={"user_email": "test@gmail.com", "auto_save": "true"}
        )
    assert r.status_code == 200, f"Valid PDF upload failed with status {r.status_code}: {r.text}"
    res = r.json()
    assert res.get("success") is True, f"Success was not True: {res}"
    data = res["data"]
    score = data["overall_score"]
    assert 0 <= score <= 100, f"Overall score {score} out of range"
    assert "breakdown" in data, "breakdown missing"
    assert data["breakdown"]["structure"] > 0, "structure score is 0"
    assert data["contact_details"]["has_email"] is True, "has_email should be True"
    assert data["contact_details"]["has_phone"] is True, "has_phone should be True"
    assert data["contact_details"]["has_links"] is True, "has_links should be True"
    assert data["formatting_details"]["has_email"] is True, "formatting_details.has_email should be True"
    assert data["quantified_metrics_found"] > 0, "quantified_metrics_found should be > 0"
    print(f"[PASS] TEST 3: Valid PDF Resume Analysis Passed! Quality Score: {score}/100, Breakdown: {data['breakdown']}")
    passed += 1

    # 4. Valid DOCX Resume Upload & ATS Scoring + Job Description Match
    total += 1
    jd = "Seeking a Python Developer with expertise in Flask, Django, PostgreSQL, Docker, Redis, and RESTful APIs."
    with open(DOCX_PATH, "rb") as f:
        r = requests.post(
            f"{BASE_URL}/api/analyze",
            files={"resume": ("sample_python_developer.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"job_description": jd, "user_email": "test@gmail.com", "auto_save": "true"}
        )
    assert r.status_code == 200, f"Valid DOCX upload failed: {r.text}"
    res = r.json()
    assert res.get("success") is True
    data = res["data"]
    assert data["has_job_description"] is True
    assert data["job_match_score"] is not None and 0 <= data["job_match_score"] <= 100
    assert len(data["matched_skills"]) > 0
    print(f"[PASS] TEST 4: Valid DOCX Resume + JD Match Passed! Quality Score: {data['resume_quality_score']}, Job Match: {data['job_match_score']}%, Matched Skills: {data['matched_skills']}")
    passed += 1

    # 5. Empty / 0-byte File Upload
    total += 1
    empty_bytes = io.BytesIO(b"")
    r = requests.post(
        f"{BASE_URL}/api/analyze",
        files={"resume": ("empty_resume.pdf", empty_bytes, "application/pdf")}
    )
    assert r.status_code == 400, f"Expected 400 for empty file, got {r.status_code}"
    res = r.json()
    assert res.get("success") is False
    assert "empty (0 bytes)" in res.get("message", "").lower()
    print(f"[PASS] TEST 5: Empty (0-byte) Upload Properly Rejected: '{res.get('message')}'")
    passed += 1

    # 6. Scanned PDF (Image-Only, Zero Selectable Text)
    total += 1
    # Create an image-only PDF using pymupdf
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    import base64
    dummy_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    page.insert_image(pymupdf.Rect(50, 50, 300, 400), stream=dummy_png)
    pdf_bytes = doc.tobytes()
    doc.close()

    r = requests.post(
        f"{BASE_URL}/api/analyze",
        files={"resume": ("scanned_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    assert r.status_code == 400, f"Expected 400 for scanned PDF, got {r.status_code}: {r.text}"
    res = r.json()
    assert res.get("success") is False
    assert "scanned image" in res.get("message", "").lower() or "ocr" in res.get("message", "").lower()
    print(f"[PASS] TEST 6: Scanned PDF (Image-only) Properly Rejected: '{res.get('message')}'")
    passed += 1

    # 7. Unsupported File Format (.txt or .png)
    total += 1
    r = requests.post(
        f"{BASE_URL}/api/analyze",
        files={"resume": ("my_resume.txt", io.BytesIO(b"This is a plain text file."), "text/plain")}
    )
    assert r.status_code == 400, f"Expected 400 for unsupported format, got {r.status_code}"
    res = r.json()
    assert res.get("success") is False
    assert "only pdf and docx" in res.get("message", "").lower()
    print(f"[PASS] TEST 7: Unsupported File Format Properly Rejected: '{res.get('message')}'")
    passed += 1

    # 8. Document with Very Little Text (< 40 chars)
    total += 1
    short_doc = pymupdf.open()
    short_page = short_doc.new_page(width=595, height=842)
    short_page.insert_text((50, 50), "Hello world")  # 11 chars
    short_bytes = short_doc.tobytes()
    short_doc.close()

    r = requests.post(
        f"{BASE_URL}/api/analyze",
        files={"resume": ("short_resume.pdf", io.BytesIO(short_bytes), "application/pdf")}
    )
    assert r.status_code == 400, f"Expected 400 for short text, got {r.status_code}"
    res = r.json()
    assert res.get("success") is False
    assert "insufficient text" in res.get("message", "").lower() or "40 characters" in res.get("message", "").lower()
    print(f"[PASS] TEST 8: Short Text Document (<40 chars) Properly Rejected: '{res.get('message')}'")
    passed += 1

    # 9. Verify History and Detail Persistence
    total += 1
    r_hist = requests.get(f"{BASE_URL}/api/history?email=test@gmail.com")
    assert r_hist.status_code == 200
    hist_items = r_hist.json().get("data", [])
    assert len(hist_items) > 0, "Expected at least 1 history item"
    first_item = hist_items[0]
    assert "resume_quality_score" in first_item, "resume_quality_score missing in history item"
    assert "contact_details" in first_item, "contact_details missing in history item"
    assert first_item["contact_details"]["has_email"] is True, "contact_details.has_email missing"
    assert first_item["formatting_details"]["has_email"] is True, "formatting_details.has_email missing"
    print(f"[PASS] TEST 9: History Unpacking Verified! Latest item ID: {first_item['id']}, Resume: {first_item['resume_name']}, Quality: {first_item['resume_quality_score']}")
    passed += 1

    print("==================================================")
    print(f"ALL {passed}/{total} WORKFLOW INTEGRATION TESTS PASSED PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    run_all_tests()
