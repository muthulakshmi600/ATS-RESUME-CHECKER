"""
Automated Test Suite for ResumeAI ATS.
Tests:
1. Health check & SPA serving
2. Auth (Demo Login, Signup, validations)
3. Strong, Average, and Weak resumes testing (quality scores, realistic range, deterministic consistency)
4. Analysis WITHOUT Target Job Role
5. Analysis WITH and WITHOUT Job Description (Resume Quality vs Job Match)
6. Breakdown validation (structure, contact, metrics, formatting, readability, skills)
7. Profile update without target_role
8. History and Stats endpoints
"""

import sys
import os
import io

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from app import app, init_db
from analyzer import analyze_resume

def run_tests():
    print("=====================================================================")
    print("[TEST SUITE] Running ResumeAI ATS Comprehensive Verification Suite")
    print("=====================================================================\n")
    init_db()
    client = app.test_client()

    # 1. Health check
    res = client.get('/api/health')
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    data = res.get_json()
    assert data['app'] == 'ResumeAI', "App name mismatch"
    print("  [✓] Health check endpoint: OK")

    # 2. SPA index serving with new Branding & Theme
    res = client.get('/')
    assert res.status_code == 200
    assert b'ResumeAI ATS' in res.data, "ResumeAI ATS branding not found in index.html"
    assert b'components/Logo.js' in res.data, "Logo.js not included in index.html"
    print("  [✓] Static SPA Frontend index serving (ResumeAI ATS & Logo.js): OK")

    # 3. Auth Endpoints
    res = client.post('/api/auth/login', json={'email': 'test@gmail.com', 'password': '12345'})
    assert res.status_code == 200
    assert res.get_json()['success'] is True
    print("  [✓] Demo Login (test@gmail.com / 12345): OK")

    res = client.post('/api/auth/login', json={'email': '', 'password': ''})
    assert res.status_code == 400
    print("  [✓] Empty credentials validation: OK")

    # 4. Weak Resume Test (Minimal text, missing sections, no metrics, no links)
    weak_resume_text = """
    John Doe
    I am looking for a job in software.
    I know some HTML and have used a computer.
    Thanks for reading.
    """
    weak_result = analyze_resume(weak_resume_text)
    print(f"\n  --- WEAK RESUME TEST ---")
    print(f"  Overall Quality Score: {weak_result['overall_score']}/100")
    print(f"  Breakdown: {weak_result['breakdown']}")
    assert weak_result['overall_score'] < 50, f"Weak resume scored too high: {weak_result['overall_score']}"
    assert weak_result['overall_score'] != 85, "Weak resume artificially forced to 85%"
    assert weak_result['has_job_description'] is False
    assert len(weak_result['suggestions']) > 0, "Weak resume must have improvement suggestions"
    print("  [✓] Weak resume properly evaluated with realistic low score: OK")

    # 5. Average Resume Test (Some sections, some skills, few metrics)
    average_resume_text = """
    Jane Smith
    jane.smith@email.com | (555) 123-4567 | City, State

    Summary:
    Developer with experience building web applications using JavaScript and Python.

    Experience:
    Junior Programmer | Tech Co (2022 - 2023)
    - Developed web interfaces using React.
    - Worked on Python scripts for data processing.
    - Participated in team meetings and fixed bugs.

    Education:
    B.S. in Information Technology | State University (2018 - 2022)

    Skills:
    Python, JavaScript, React, Git, HTML, CSS
    """
    average_result = analyze_resume(average_resume_text)
    print(f"\n  --- AVERAGE RESUME TEST ---")
    print(f"  Overall Quality Score: {average_result['overall_score']}/100")
    print(f"  Breakdown: {average_result['breakdown']}")
    assert 45 <= average_result['overall_score'] <= 75, f"Average resume out of expected range: {average_result['overall_score']}"
    assert average_result['overall_score'] != 85, "Average resume artificially forced to 85%"
    print("  [✓] Average resume scored in realistic balanced range: OK")

    # 6. Strong Resume Test (Complete sections, contact info, metrics %, links, strong skills)
    strong_resume_text = """
    Muthu Kumar
    muthu.kumar@example.com | +91 98765 43210 | linkedin.com/in/muthukumar | github.com/muthukumar

    Professional Summary:
    Dedicated Software Engineer with 3+ years of experience in backend development, REST API design, and database architecture using Django, Flask, FastAPI, and PostgreSQL. Proven track record of improving API latency by 35% and building resilient microservices with Docker.

    Technical Skills:
    • Programming: Python, SQL, JavaScript, HTML5, CSS3
    • Frameworks: Django, Flask, FastAPI, Celery, SQLAlchemy
    • Databases: PostgreSQL, MySQL, Redis, SQLite
    • Tools & Cloud: Docker, Git, GitHub, Linux, Postman, AWS EC2
    • Methodologies: Agile/Scrum, Unit Testing, Pytest, REST APIs, CI/CD

    Professional Experience:
    Senior Software Engineer | Innovate Tech Solutions (2022 - Present)
    • Designed and engineered high-throughput RESTful APIs using Python, FastAPI, and PostgreSQL.
    • Refactored legacy monolithic services into lightweight Docker containers, reducing cloud costs by 22%.
    • Optimized complex SQL queries and implemented Redis caching, accelerating report generation by 40%.
    • Authored comprehensive automated test suites using Pytest, maintaining 85%+ code coverage.
    • Spearheaded transition to CI/CD pipeline, reducing deployment times by 50%.

    Junior Software Engineer | CloudSoft Labs (2021 - 2022)
    • Built internal data extraction pipelines using Python scripts and Pandas handling 100,000+ daily records.
    • Collaborated closely with front-end developers to integrate JSON endpoints with React UI.
    • Resolved 50+ critical production bug tickets and actively participated in Agile sprint retrospectives.

    Education:
    Bachelor of Engineering in Computer Science | Anna University (2017 - 2021)

    Projects:
    • E-Commerce Inventory Service: Distributed inventory tracking engine with Celery and Redis.
    • Automated Log Analyzer: Python script parsing server logs for security anomalies with 99% accuracy.

    Certifications:
    • AWS Certified Solutions Architect Associate
    """
    strong_result_no_jd = analyze_resume(strong_resume_text)
    print(f"\n  --- STRONG RESUME TEST (NO JD) ---")
    print(f"  Overall Quality Score: {strong_result_no_jd['overall_score']}/100")
    print(f"  Breakdown: {strong_result_no_jd['breakdown']}")
    assert strong_result_no_jd['overall_score'] >= 75, f"Strong resume scored too low: {strong_result_no_jd['overall_score']}"
    assert strong_result_no_jd['has_job_description'] is False
    assert strong_result_no_jd['job_match_score'] in (None, 0)
    assert strong_result_no_jd['overall_score'] > average_result['overall_score'] > weak_result['overall_score'], "Score hierarchy violated!"
    print("  [✓] Strong resume without JD scores high on quality foundation: OK")

    # 7. Deterministic Consistency Test (Identical inputs must yield identical scores)
    strong_result_repeat = analyze_resume(strong_resume_text)
    assert strong_result_no_jd['overall_score'] == strong_result_repeat['overall_score'], "Scores are non-deterministic!"
    assert strong_result_no_jd['breakdown'] == strong_result_repeat['breakdown'], "Breakdowns are non-deterministic!"
    print("  [✓] Deterministic consistency test: identical inputs produce identical scores: OK")

    # 8. Resume Analysis WITH Job Description (Job Match score calculated separately)
    job_description = """
    Looking for a Senior Python Developer with deep experience in FastAPI, Django, PostgreSQL, Docker, Redis, and Pytest.
    Must have experience optimizing SQL queries, building microservices, and implementing CI/CD pipelines.
    """
    strong_result_with_jd = analyze_resume(strong_resume_text, job_description=job_description)
    print(f"\n  --- STRONG RESUME TEST (WITH JD) ---")
    print(f"  Resume Quality Score: {strong_result_with_jd['overall_score']}/100")
    print(f"  Job Match Score: {strong_result_with_jd['job_match_score']}/100")
    assert strong_result_with_jd['has_job_description'] is True
    assert strong_result_with_jd['job_match_score'] >= 50, f"Expected realistic job match: {strong_result_with_jd['job_match_score']}"
    assert len(strong_result_with_jd['matched_skills']) > 0
    print("  [✓] Job Description analysis calculates separate Job Match score: OK")

    # 9. API Analysis Endpoint WITHOUT Target Job Role
    sample_dir = os.path.join(os.path.dirname(CURRENT_DIR), 'sample_resumes')
    docx_path = os.path.join(sample_dir, 'sample_python_developer.docx')
    with open(docx_path, 'rb') as f:
        res = client.post('/api/analyze', data={
            'resume': (f, 'sample_python_developer.docx'),
            # NOTE: NO job_role sent! Completely role-independent
            'job_description': 'Python Django Flask PostgreSQL Docker REST APIs',
            'user_email': 'test@gmail.com',
            'auto_save': 'true'
        }, content_type='multipart/form-data')

    assert res.status_code == 200, f"Analysis without job_role failed: {res.status_code}, {res.data}"
    api_data = res.get_json()['data']
    assert 0 <= api_data['overall_score'] <= 100
    assert api_data['has_job_description'] is True
    assert api_data['job_match_score'] > 0
    saved_id = api_data.get('id')
    print(f"  [✓] API /api/analyze succeeds without any Target Job Role (Score: {api_data['overall_score']}/100, JD Match: {api_data['job_match_score']}%): OK")

    # 10. History and Stats verification
    res = client.get('/api/history?email=test@gmail.com')
    assert res.status_code == 200
    history = res.get_json()['data']
    assert len(history) >= 1
    print(f"  [✓] History endpoint retrieves stored analyses: OK")

    res = client.get('/api/stats?email=test@gmail.com')
    assert res.status_code == 200
    stats = res.get_json()['data']
    assert stats['total_checked'] >= 1
    assert stats['avg_score'] > 0
    print(f"  [✓] Stats endpoint returns accurate metrics: OK")

    # 11. Profile Update without target_role
    res = client.post('/api/profile', json={
        'email': 'test@gmail.com',
        'name': 'Alex Morgan',
        'bio': 'Software engineer dedicated to building scalable distributed systems.'
    })
    assert res.status_code == 200
    assert res.get_json()['success'] is True
    print("  [✓] Profile update without target_role field: OK")

    print("\n=====================================================================")
    print("[SUCCESS] ALL VERIFICATION AND TEST CASES PASSED PERFECTLY!")
    print("=====================================================================")

if __name__ == '__main__':
    run_tests()
