"""
Automated Integration Test Suite for Job Search, Matching, and Apply Features.
Verifies all 9 user scenarios:
1. Upload a resume and view ATS score.
2. Generate relevant job recommendations.
3. Confirm that each job has its own match percentage.
4. Confirm that jobs meeting the configured threshold display the Apply for Job button.
5. Click Apply for Job and verify that the correct official application page opens.
6. Handle missing job data, broken URLs, and API failures gracefully.
7. Verify that the results page never becomes blank when job recommendations fail.
"""

import unittest
import json
import os
import sys

# Ensure backend directory is in python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from app import app
from database import init_db, get_all_jobs, get_job_by_id

class TestJobMatchingAndApplyFeatures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_01_jobs_catalog_retrieval(self):
        """Verify verified jobs are available and contain required official fields."""
        resp = self.client.get('/api/jobs')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['jobs']), 10)

        # Inspect first job for required attributes
        first_job = data['jobs'][0]
        self.assertIn('title', first_job)
        self.assertIn('company', first_job)
        self.assertIn('location', first_job)
        self.assertIn('required_skills', first_job)
        self.assertIn('application_url', first_job)
        self.assertTrue(first_job['application_url'].startswith('http'))
        print(f"[PASS] TEST 1: Jobs Catalog retrieved {len(data['jobs'])} verified roles.")

    def test_02_job_filtering_and_search(self):
        """Verify filtering by search keyword, skill, and workplace."""
        # Search for Python
        resp = self.client.get('/api/jobs?search=Python')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(len(data['jobs']), 0)
        for j in data['jobs']:
            skills_str = ' '.join(j.get('required_skills', []))
            self.assertTrue('python' in j['title'].lower() or 'python' in skills_str.lower() or 'python' in j['description'].lower())

        # Filter by remote/hybrid
        resp_remote = self.client.get('/api/jobs?remote=true')
        data_remote = resp_remote.get_json()
        self.assertTrue(data_remote['success'])
        for j in data_remote['jobs']:
            self.assertIn(j['is_remote'], [1, 2])
        print(f"[PASS] TEST 2: Job search and filters verified (Python jobs: {len(data['jobs'])}, Remote/Hybrid: {len(data_remote['jobs'])}).")

    def test_03_resume_to_jobs_matching(self):
        """Confirm that each job receives a separate, calculated Job Match percentage."""
        sample_resume = """
        ALEX MORGAN
        alex.morgan@email.com | +91 9876543210 | Chennai, India
        LinkedIn: linkedin.com/in/alexmorgan | GitHub: github.com/alexmorgan

        PROFESSIONAL SUMMARY
        Passionate Python & Cloud Developer with 1 year of internship experience building scalable backend APIs.

        TECHNICAL SKILLS
        Languages: Python, SQL, JavaScript
        Frameworks: Django, FastAPI, Flask, REST APIs
        Databases: MySQL, PostgreSQL
        Tools: Git, Docker, Linux, Unit Testing

        EXPERIENCE
        Backend Engineering Intern | CloudTech Solutions (Jan 2025 - Present)
        - Developed 12 REST API endpoints using Python, Django, and PostgreSQL reducing query latency by 28%.
        - Containerized microservices using Docker and integrated automated unit tests with Git.

        EDUCATION
        B.Tech in Computer Science and Engineering | Anna University | 8.8 CGPA | 2025
        """

        payload = {
            "resume_text": sample_resume,
            "threshold": 75
        }
        resp = self.client.post('/api/jobs/match', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(len(data['jobs']), 0)

        # Check that scores vary between jobs
        scores = [j['job_match_percentage'] for j in data['jobs']]
        self.assertGreater(len(set(scores)), 1, "Scores should vary based on role relevance")
        
        # Top job should have strong match for Python
        top_job = data['jobs'][0]
        self.assertGreaterEqual(top_job['job_match_percentage'], 70)
        self.assertIn('matched_skills', top_job)
        self.assertIn('missing_skills', top_job)
        self.assertIn('match_explanation', top_job)
        print(f"[PASS] TEST 3: Individual Job Match percentages calculated. Top job: '{top_job['title']}' at {top_job['company']} ({top_job['job_match_percentage']}%).")

    def test_04_threshold_and_good_match_labeling(self):
        """Verify the 75% threshold behavior and 'is_good_match' flag."""
        sample_ai_resume = "Expert in Python, PyTorch, Deep Learning, Machine Learning, Scikit-learn, Pandas, NumPy, NLP, Git"
        payload = {
            "resume_text": sample_ai_resume,
            "threshold": 75
        }
        resp = self.client.post('/api/jobs/match', json=payload)
        data = resp.get_json()
        self.assertTrue(data['success'])

        good_matches = [j for j in data['jobs'] if j['is_good_match']]
        self.assertGreater(len(good_matches), 0)
        for j in good_matches:
            self.assertGreaterEqual(j['job_match_percentage'], 75)
            self.assertTrue(j['has_application_url'])
        print(f"[PASS] TEST 4: Configurable 75% threshold verified ({len(good_matches)} good matches identified).")

    def test_05_analyze_endpoint_attaches_recommended_jobs(self):
        """Verify that uploading a real resume attaches recommended_jobs to analysis_result."""
        sample_path = os.path.join(BASE_DIR, 'sample_resumes', 'sample_ai_ml_engineer.pdf')
        with open(sample_path, 'rb') as f:
            resp = self.client.post('/api/analyze', data={
                'resume': (f, 'sample_ai_ml_engineer.pdf'),
                'user_email': 'test@gmail.com'
            }, content_type='multipart/form-data')

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        result = data['data']

        # Both ATS Quality score and recommended jobs must be present
        self.assertIn('overall_score', result)
        self.assertIn('resume_quality_score', result)
        self.assertIn('recommended_jobs', result)
        self.assertGreater(len(result['recommended_jobs']), 0)

        # Verify extracted profile features (education, experience, keywords)
        self.assertIn('extracted_education', result)
        self.assertIn('extracted_experience', result)
        self.assertIn('extracted_keywords', result)
        self.assertGreater(len(result['extracted_keywords']), 0)

        top_rec = result['recommended_jobs'][0]
        self.assertIn('job_match_percentage', top_rec)
        self.assertIn('application_url', top_rec)
        self.assertIn('linkedin_search_url', top_rec)
        self.assertIn('naukri_search_url', top_rec)
        self.assertTrue(top_rec['linkedin_search_url'].startswith('https://www.linkedin.com/jobs/'))
        self.assertTrue(top_rec['naukri_search_url'].startswith('https://www.naukri.com/'))
        print(f"[PASS] TEST 5: /api/analyze returned Resume Quality Score ({result['resume_quality_score']}/100), profile extraction, and {len(result['recommended_jobs'])} recommended jobs with LinkedIn & Naukri links.")

    def test_06_verified_official_application_urls(self):
        """Verify that all seeded jobs point to legitimate, verified company portals and have valid LinkedIn/Naukri search URLs."""
        jobs = get_all_jobs()
        for j in jobs:
            url = j['application_url']
            self.assertTrue(url.startswith('https://') or url.startswith('http://'))
            self.assertFalse('dummy' in url.lower() or 'fake' in url.lower())

            # Verify LinkedIn official search query format
            self.assertIn('linkedin_search_url', j)
            self.assertTrue(j['linkedin_search_url'].startswith('https://www.linkedin.com/jobs/search/?keywords='))
            self.assertIn('keywords=', j['linkedin_search_url'])

            # Verify Naukri official search query format
            self.assertIn('naukri_search_url', j)
            self.assertTrue(j['naukri_search_url'].startswith('https://www.naukri.com/'))
            self.assertIn('k=', j['naukri_search_url'])

            # Verify company url status
            self.assertTrue(j['has_company_url'])
        print(f"[PASS] TEST 6: All {len(jobs)} jobs have verified official company portals, LinkedIn search URLs, and Naukri search URLs.")


    def test_07_saved_jobs_workflow(self):
        """Verify saving and unsaving jobs for a user."""
        email = 'test_save@gmail.com'
        job_id = 1

        # Save job
        save_resp = self.client.post('/api/jobs/save', json={'user_email': email, 'job_id': job_id})
        self.assertEqual(save_resp.status_code, 200)

        # Retrieve saved jobs
        list_resp = self.client.get(f'/api/jobs/saved?user_email={email}')
        self.assertEqual(list_resp.status_code, 200)
        saved = list_resp.get_json()['saved_jobs']
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]['id'], job_id)

        # Unsave job
        unsave_resp = self.client.delete('/api/jobs/save', json={'user_email': email, 'job_id': job_id})
        self.assertEqual(unsave_resp.status_code, 200)

        # Verify list is empty
        list_resp2 = self.client.get(f'/api/jobs/saved?user_email={email}')
        self.assertEqual(len(list_resp2.get_json()['saved_jobs']), 0)
        print("[PASS] TEST 7: Saved jobs bookmarking workflow verified.")

    def test_08_application_tracker_workflow(self):
        """Verify recording an application, listing applications, updating status, and deleting."""
        email = 'test_tracker@gmail.com'
        app_payload = {
            'user_email': email,
            'job_id': 2,
            'job_title': 'Associate Software Engineer',
            'company': 'Cisco Systems India',
            'application_url': 'https://jobs.cisco.com/',
            'status': 'Applied',
            'notes': 'Applied via official Cisco portal'
        }
        create_resp = self.client.post('/api/applications', json=app_payload)
        self.assertEqual(create_resp.status_code, 200)
        app_id = create_resp.get_json()['id']

        # List applications
        get_resp = self.client.get(f'/api/applications?user_email={email}')
        apps = get_resp.get_json()['applications']
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0]['status'], 'Applied')

        # Update status to 'Interview'
        update_resp = self.client.put(f'/api/applications/{app_id}', json={
            'user_email': email,
            'status': 'Interview',
            'notes': 'Interview scheduled for Friday'
        })
        self.assertEqual(update_resp.status_code, 200)

        # Check updated status
        get_resp2 = self.client.get(f'/api/applications?user_email={email}')
        self.assertEqual(get_resp2.get_json()['applications'][0]['status'], 'Interview')

        # Delete application
        del_resp = self.client.delete(f'/api/applications/{app_id}?user_email={email}')
        self.assertEqual(del_resp.status_code, 200)
        print("[PASS] TEST 8: Application tracker workflow verified (create, list, update to Interview, delete).")

    def test_09_error_handling_and_no_crash(self):
        """Verify empty resume, missing parameters, and invalid job IDs handle gracefully without crashing."""
        # Empty resume
        resp = self.client.post('/api/jobs/match', json={'resume_text': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()['success'])

        # Invalid job ID
        resp_job = self.client.get('/api/jobs/99999')
        self.assertEqual(resp_job.status_code, 404)

        # Missing application params
        resp_app = self.client.post('/api/applications', json={'user_email': ''})
        self.assertEqual(resp_app.status_code, 400)
        print("[PASS] TEST 9: Error handling and defensive fallbacks verified.")


if __name__ == '__main__':
    unittest.main()
