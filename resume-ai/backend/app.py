"""
ResumeAI Flask Backend Application.
Provides REST APIs for:
- Demo & Custom Authentication
- Resume upload, PDF/DOCX parsing, and ATS Analysis
- Analysis history persistence & stats
- User profile & preferences
- Static SPA hosting
"""

import os
import re
import json
from flask import Flask, request, jsonify, send_from_directory, make_response
from werkzeug.utils import secure_filename

from database import (
    init_db, save_analysis, get_user_analyses, get_analysis_by_id,
    delete_analysis, delete_all_analyses, get_user_stats, get_or_create_user, update_user_profile,
    get_user_settings, update_user_settings,
    get_all_jobs, get_job_by_id, save_job_for_user, unsave_job_for_user,
    get_saved_jobs_for_user, record_job_application, get_user_job_applications,
    update_application_status, delete_job_application
)
from parser import extract_resume_text, allowed_file, MAX_FILE_SIZE_BYTES
from analyzer import analyze_resume
from job_matcher import match_jobs_against_resume, calculate_single_job_match, DEFAULT_MATCH_THRESHOLD

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database schema
init_db()

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_BYTES
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Enable CORS for all API routes
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-Email'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

# Handle preflight OPTIONS
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return ('', 204)

# ----------------- AUTH ROUTES ----------------- #

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """
    Demo Login endpoint:
    Any non-empty email and any non-empty password successfully logs in!
    Returns demo session user data.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()
    password = (data.get('password') or '').strip()

    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Please enter email and password.'
        }), 400

    # Retrieve or create user record
    user = get_or_create_user(email, password=password)

    return jsonify({
        'success': True,
        'message': f'Welcome back, {user["name"]}!',
        'user': {
            'email': user['email'],
            'name': user['name'],
            'bio': user['bio']
        }
    })

@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    """
    Sign Up endpoint:
    Validates name, email format, and password confirmation.
    Registers user and prompts redirect to login.
    """
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    password = (data.get('password') or '').strip()
    confirm_password = (data.get('confirm_password') or '').strip()

    if not name or not email or not password or not confirm_password:
        return jsonify({
            'success': False,
            'message': 'All fields are required.'
        }), 400

    # Basic email format validation
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return jsonify({
            'success': False,
            'message': 'Please enter a valid email address format (e.g., name@example.com).'
        }), 400

    if password != confirm_password:
        return jsonify({
            'success': False,
            'message': 'Passwords do not match. Please re-enter.'
        }), 400

    if len(password) < 4:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 4 characters long.'
        }), 400

    # Register user in database
    user = get_or_create_user(email, name=name, password=password)

    return jsonify({
        'success': True,
        'message': 'Account created successfully! Please log in to continue.',
        'user': {
            'email': user['email'],
            'name': user['name']
        }
    })

# ----------------- RESUME ANALYSIS ROUTES ----------------- #

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    Main ATS Resume Analyzer Endpoint.
    Accepts:
    - resume: PDF or DOCX file (up to 5MB)
    - job_role: Target job title
    - custom_role: Custom job title if job_role is 'Other'
    - job_description: Optional job description text
    - user_email: Optional email to attach record to
    - auto_save: Flag to automatically persist in DB
    """
    if 'resume' not in request.files:
        return jsonify({'success': False, 'message': 'No resume file uploaded.'}), 400

    file = request.files['resume']
    if not file or file.filename == '':
        return jsonify({'success': False, 'message': 'Please select a resume file to upload.'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'message': 'Invalid file format. Only PDF and DOCX documents are supported.'
        }), 400

    # File size validation
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size == 0:
        return jsonify({
            'success': False,
            'message': 'The uploaded file is empty (0 bytes). Please upload a valid resume file.'
        }), 400
    if size > MAX_FILE_SIZE_BYTES:
        return jsonify({
            'success': False,
            'message': f'File exceeds 5MB size limit. Your file is {round(size/(1024*1024), 2)} MB.'
        }), 400

    job_description = request.form.get('job_description', '').strip()
    user_email = request.form.get('user_email', '').strip()
    auto_save = request.form.get('auto_save', 'true').lower() in ('true', '1', 'yes')

    try:
        # Extract text using robust parser
        raw_text = extract_resume_text(file, file.filename)
        if not raw_text or len(raw_text.strip()) < 40:
            return jsonify({
                'success': False,
                'message': 'The resume contains insufficient text for ATS analysis (less than 40 characters). Please upload a complete resume.'
            }), 400

        # Execute rule-based analysis without role dependency
        analysis_result = analyze_resume(raw_text, job_description=job_description)
        analysis_result['resume_name'] = secure_filename(file.filename) or 'Resume.pdf'
        analysis_result['file_size_kb'] = round(size / 1024, 1)

        # Intelligent Job Matching for uploaded resume
        try:
            matched_data = match_jobs_against_resume(
                resume_text=raw_text,
                detected_skills=analysis_result.get('detected_skills'),
                threshold=DEFAULT_MATCH_THRESHOLD
            )
            analysis_result['recommended_jobs'] = matched_data.get('jobs', [])
            analysis_result['total_jobs_matched'] = matched_data.get('total_jobs', 0)
            analysis_result['good_matches_count'] = matched_data.get('good_matches_count', 0)
            analysis_result['match_threshold'] = DEFAULT_MATCH_THRESHOLD
        except Exception as job_err:
            print("Warning: Job matching encountered an error:", job_err)
            analysis_result['recommended_jobs'] = []
            analysis_result['total_jobs_matched'] = 0
            analysis_result['good_matches_count'] = 0
            analysis_result['match_threshold'] = DEFAULT_MATCH_THRESHOLD

        # Store resume text sample for interactive client-side filtering without re-upload
        analysis_result['resume_text_sample'] = raw_text[:4000]

        # Optionally persist
        saved_id = None
        if user_email and auto_save:
            saved_id = save_analysis(user_email, analysis_result)

        analysis_result['id'] = saved_id

        return jsonify({
            'success': True,
            'data': analysis_result
        })

    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Analysis error: {str(e)}'
        }), 500

@app.route('/api/sample-resume', methods=['GET'])
def api_sample_resume():
    """
    Returns a sample resume document (PDF or DOCX) for quick demo testing.
    """
    doc_type = request.args.get('type', 'pdf').lower()
    sample_dir = os.path.join(os.path.dirname(BASE_DIR), 'sample_resumes')
    if doc_type == 'docx':
        filename = 'sample_python_developer.docx'
        mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        filename = 'sample_ai_ml_engineer.pdf'
        mimetype = 'application/pdf'
    
    file_path = os.path.join(sample_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(sample_dir, filename, as_attachment=True, mimetype=mimetype)
    return jsonify({'success': False, 'message': 'Sample resume file not found.'}), 404

@app.route('/api/save-analysis', methods=['POST'])
def api_save_analysis():
    """
    Explicitly save an analysis result to history.
    """
    data = request.get_json(silent=True) or {}
    user_email = data.get('user_email', '').strip()
    analysis_data = data.get('analysis', {})

    if not user_email or not analysis_data:
        return jsonify({'success': False, 'message': 'Missing user email or analysis payload.'}), 400

    saved_id = save_analysis(user_email, analysis_data)
    return jsonify({
        'success': True,
        'message': 'Analysis successfully saved to history!',
        'id': saved_id
    })

# ----------------- HISTORY & STATS ROUTES ----------------- #

@app.route('/api/history', methods=['GET'])
def api_get_history():
    """
    Returns list of analyzed resumes for the user.
    """
    email = request.args.get('email', '').strip() or request.headers.get('X-User-Email', '').strip()
    if not email:
        return jsonify({'success': True, 'data': []})

    analyses = get_user_analyses(email)
    return jsonify({
        'success': True,
        'data': analyses
    })

@app.route('/api/history/<int:analysis_id>', methods=['GET'])
def api_get_analysis_detail(analysis_id):
    """
    Returns full details for a specific analysis.
    """
    email = request.args.get('email', '').strip() or request.headers.get('X-User-Email', '').strip()
    analysis = get_analysis_by_id(analysis_id, email)
    if not analysis:
        return jsonify({'success': False, 'message': 'Analysis record not found.'}), 404

    return jsonify({
        'success': True,
        'data': analysis
    })

@app.route('/api/history/all', methods=['DELETE', 'POST'])
def api_delete_all_analyses():
    """
    Deletes all analysis history records for the current user.
    """
    email = request.args.get('email', '').strip() or request.headers.get('X-User-Email', '').strip()
    if not email:
        data = request.get_json(silent=True) or {}
        email = data.get('email', '').strip()
    if not email:
        return jsonify({'success': False, 'message': 'User email is required to clear history.'}), 400

    deleted_count = delete_all_analyses(email)
    return jsonify({
        'success': True,
        'message': f'Successfully cleared {deleted_count} resume analysis records.',
        'deleted_count': deleted_count
    })

@app.route('/api/history/<int:analysis_id>', methods=['DELETE'])
def api_delete_analysis(analysis_id):
    """
    Deletes an analysis entry.
    """
    email = request.args.get('email', '').strip() or request.headers.get('X-User-Email', '').strip()
    deleted = delete_analysis(analysis_id, email)
    return jsonify({
        'success': deleted,
        'message': 'Analysis record removed.' if deleted else 'Record not found or not authorized.'
    })

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """
    Returns dashboard statistics cards for the user.
    """
    email = request.args.get('email', '').strip() or request.headers.get('X-User-Email', '').strip()
    if not email:
        return jsonify({
            'success': True,
            'data': {
                'total_checked': 0,
                'avg_score': 0,
                'best_score': 0,
                'last_analysis': None
            }
        })

    stats = get_user_stats(email)
    return jsonify({
        'success': True,
        'data': stats
    })

# ----------------- PROFILE & SETTINGS ROUTES ----------------- #

@app.route('/api/profile', methods=['GET', 'POST'])
def api_profile():
    if request.method == 'GET':
        email = request.args.get('email', '').strip()
        user = get_or_create_user(email)
        return jsonify({'success': True, 'data': user})

    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    name = data.get('name', '').strip()
    bio = data.get('bio', '').strip()

    if not email or not name:
        return jsonify({'success': False, 'message': 'Email and Name are required.'}), 400

    update_user_profile(email, name, bio)
    return jsonify({'success': True, 'message': 'Profile updated successfully!'})

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    if request.method == 'GET':
        email = request.args.get('email', '').strip()
        settings = get_user_settings(email)
        return jsonify({'success': True, 'data': settings})

    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    sensitivity = data.get('scoring_sensitivity', 'Standard')
    theme = data.get('theme', 'light')
    email_alerts = 1 if data.get('email_alerts') else 0
    auto_save = 1 if data.get('auto_save') else 0

    if not email:
        return jsonify({'success': False, 'message': 'Email is required.'}), 400

    update_user_settings(email, sensitivity, theme, email_alerts, auto_save)
    return jsonify({'success': True, 'message': 'Preferences saved successfully!'})

# ----------------- JOB SEARCH & MATCHING ROUTES ----------------- #

@app.route('/api/jobs', methods=['GET'])
def api_get_jobs():
    """
    Search and filter verified fresher tech jobs.
    """
    search = request.args.get('search') or request.args.get('q')
    skill = request.args.get('skill')
    location = request.args.get('location')
    job_type = request.args.get('job_type')
    is_remote = request.args.get('remote')

    jobs = get_all_jobs(
        search=search,
        skill=skill,
        location=location,
        job_type=job_type,
        is_remote=is_remote
    )
    return jsonify({
        'success': True,
        'jobs': jobs,
        'total': len(jobs)
    })

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def api_get_job(job_id):
    """
    Get a single verified job by ID.
    """
    job = get_job_by_id(job_id)
    if not job:
        return jsonify({'success': False, 'message': 'Job listing not found.'}), 404
    return jsonify({'success': True, 'job': job})

@app.route('/api/jobs/match', methods=['POST'])
def api_match_jobs():
    """
    Dynamically match candidate resume against verified jobs catalog.
    Calculates distinct Job Match Percentage for each job and sorts by relevance.
    """
    data = request.get_json(silent=True) or {}
    resume_text = data.get('resume_text', '').strip()
    detected_skills = data.get('skills')
    threshold = int(data.get('threshold', DEFAULT_MATCH_THRESHOLD))
    search = data.get('search')
    skill = data.get('skill')
    location = data.get('location')
    job_type = data.get('job_type')
    is_remote = data.get('remote')

    result = match_jobs_against_resume(
        resume_text=resume_text,
        detected_skills=detected_skills,
        threshold=threshold,
        search=search,
        skill=skill,
        location=location,
        job_type=job_type,
        is_remote=is_remote
    )
    return jsonify(result)

@app.route('/api/jobs/save', methods=['POST', 'DELETE'])
def api_save_job():
    """
    Save or unsave a job bookmark for a user.
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        email = (data.get('user_email') or '').strip()
        job_id = data.get('job_id')
        if not email or not job_id:
            return jsonify({'success': False, 'message': 'user_email and job_id are required.'}), 400
        save_job_for_user(email, int(job_id))
        return jsonify({'success': True, 'message': 'Job bookmarked successfully!'})
    else:
        data = request.get_json(silent=True) or {}
        email = (data.get('user_email') or request.args.get('user_email') or '').strip()
        job_id = data.get('job_id') or request.args.get('job_id')
        if not email or not job_id:
            return jsonify({'success': False, 'message': 'user_email and job_id are required.'}), 400
        unsave_job_for_user(email, int(job_id))
        return jsonify({'success': True, 'message': 'Job bookmark removed.'})

@app.route('/api/jobs/saved', methods=['GET'])
def api_get_saved_jobs():
    """
    Get all saved/bookmarked jobs for a user.
    """
    email = request.args.get('user_email', '').strip()
    if not email:
        return jsonify({'success': False, 'message': 'user_email query param is required.'}), 400
    saved = get_saved_jobs_for_user(email)
    return jsonify({
        'success': True,
        'saved_jobs': saved,
        'total': len(saved)
    })

@app.route('/api/applications', methods=['GET', 'POST'])
def api_applications():
    """
    Application tracker: view or record job applications.
    """
    if request.method == 'GET':
        email = request.args.get('user_email', '').strip()
        if not email:
            return jsonify({'success': False, 'message': 'user_email is required.'}), 400
        apps = get_user_job_applications(email)
        return jsonify({
            'success': True,
            'applications': apps,
            'total': len(apps)
        })

    data = request.get_json(silent=True) or {}
    email = data.get('user_email', '').strip()
    job_id = data.get('job_id', 0)
    job_title = data.get('job_title', '').strip()
    company = data.get('company', '').strip()
    app_url = data.get('application_url', '').strip()
    status = data.get('status', 'Applied').strip()
    applied_date = data.get('applied_date', '').strip()
    notes = data.get('notes', '').strip()

    if not email or not job_title or not company:
        return jsonify({'success': False, 'message': 'user_email, job_title, and company are required.'}), 400

    app_id = record_job_application(
        user_email=email,
        job_id=job_id,
        job_title=job_title,
        company=company,
        application_url=app_url,
        status=status,
        applied_date=applied_date,
        notes=notes
    )
    return jsonify({
        'success': True,
        'id': app_id,
        'message': 'Job application recorded in your tracker!'
    })

@app.route('/api/applications/<int:app_id>', methods=['PUT', 'DELETE'])
def api_single_application(app_id):
    """
    Update status or delete an application.
    """
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        email = data.get('user_email', '').strip()
        status = data.get('status', 'Applied').strip()
        notes = data.get('notes')
        if not email:
            return jsonify({'success': False, 'message': 'user_email is required.'}), 400
        update_application_status(app_id, email, status, notes)
        return jsonify({'success': True, 'message': 'Application status updated.'})
    else:
        email = (request.args.get('user_email') or '').strip()
        if not email:
            data = request.get_json(silent=True) or {}
            email = data.get('user_email', '').strip()
        delete_job_application(app_id, email)
        return jsonify({'success': True, 'message': 'Application record removed.'})

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'ok',
        'app': 'ResumeAI',
        'tagline': 'Build a Resume That Gets Noticed.',
        'version': '1.0.0'
    })

# ----------------- STATIC SPA SERVING ----------------- #

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    """
    Serves static files from frontend directory or falls back to index.html for SPA routing.
    """
    if path and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"🚀 ResumeAI Backend starting on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
