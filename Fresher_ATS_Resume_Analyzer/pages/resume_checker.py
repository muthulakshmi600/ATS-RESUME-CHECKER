"""
Check Resume Page for Fresher ATS Resume Analyzer.
Handles file upload (PDF/DOCX), metadata inspection, Job Description input,
triggers comprehensive ATS analysis, displays detailed results, generates PDF report,
and persists history to SQLite database.
"""

import streamlit as st
import pandas as pd
from datetime import date
from utils.resume_parser import parse_resume
from utils.ats_checker import analyze_resume_ats
from utils.report_generator import generate_ats_pdf_report
from database.database import save_analysis, create_job_application
from auth.authentication import get_current_user


def render_resume_checker_page():
    """Render resume upload form, job description inputs, and ATS analysis results."""
    user = get_current_user()
    if not user:
        st.warning("Please sign in to check your resume.")
        st.session_state["page"] = "login"
        st.session_state["current_page"] = "login"
        st.rerun()
        return

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">
                Check Your Resume
            </h1>
            <p style="color: #64748b; font-size: 1rem; margin: 0;">
                Upload your resume and paste your target job description to get a transparent ATS compatibility benchmark.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # If an analysis has already been performed in this session, show results view or allow reset
    if "analysis_results" in st.session_state and st.session_state["analysis_results"]:
        render_analysis_results()
        return

    # Upload Form Container
    st.markdown("### 1. Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file (Maximum 10 MB)",
        type=["pdf", "docx"],
        help="Upload a text-based resume in PDF or Word (.docx) format."
    )

    if uploaded_file is not None:
        file_size_kb = round(len(uploaded_file.getvalue()) / 1024.0, 1)
        file_type = "PDF Document" if uploaded_file.name.lower().endswith(".pdf") else "Microsoft Word DOCX"

        # Display File Details Card
        st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.85rem 1.25rem; margin-bottom: 1.5rem; display: flex; gap: 2rem; flex-wrap: wrap;">
                <div><span style="color: #64748b; font-size: 0.85rem;">File Name:</span><br><strong>{uploaded_file.name}</strong></div>
                <div><span style="color: #64748b; font-size: 0.85rem;">Format:</span><br><strong>{file_type}</strong></div>
                <div><span style="color: #64748b; font-size: 0.85rem;">File Size:</span><br><strong>{file_size_kb} KB</strong></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 2. Target Job Details")

    default_job_title = st.session_state.get("active_job_title", "")
    default_jd_text = st.session_state.get("active_jd_text", "")
    default_apply_url = st.session_state.get("active_apply_url", "")

    col_j1, col_j2 = st.columns([1, 1])
    with col_j1:
        job_title = st.text_input(
            "Job Title *",
            value=default_job_title,
            placeholder="e.g., Junior Python Developer / Data Analyst Fresher",
            help="Specify the target job title you are applying for."
        )

    with col_j2:
        official_apply_url = st.text_input(
            "Official Application URL (Optional)",
            value=default_apply_url,
            placeholder="https://careers.company.com/job/1234",
            help="Enter the direct official company application page to enable one-click Apply Now."
        )

    job_description = st.text_area(
        "Paste Job Description & Requirements *",
        value=default_jd_text,
        height=220,
        placeholder="""Example:
Python Developer required.

Skills:
Python, SQL, Pandas, NumPy, Machine Learning, Git.

Responsibilities:
Develop Python applications, work with data, build machine learning models, and collaborate with the development team.
Academic projects in Python are welcome.""",
        help="Paste the full job post, including responsibilities, required skills, tools, and qualifications."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Analyze Button
    if st.button("🔍 Analyze Resume Compatibility", type="primary", use_container_width=True):
        # Validation checks
        if uploaded_file is None:
            st.error("Please upload a PDF or DOCX resume.")
            return

        if not job_title or not job_title.strip():
            st.error("Please enter the target Job Title.")
            return

        if not job_description or not job_description.strip():
            st.error("Please paste the target Job Description.")
            return

        with st.spinner("Extracting resume text with PyMuPDF & calculating transparent ATS scores..."):
            file_bytes = uploaded_file.getvalue()
            success, text, metadata, err_msg = parse_resume(file_bytes, uploaded_file.name)

            if not success:
                st.error(err_msg)
                return

            # Run ATS Compatibility Engine
            results = analyze_resume_ats(
                resume_text=text,
                job_description=job_description,
                resume_metadata=metadata
            )

            # Persist to database history for this user
            try:
                save_analysis(
                    user_id=user["id"],
                    resume_name=uploaded_file.name,
                    job_title=job_title.strip(),
                    ats_score=results["final_ats_score"],
                    job_match_score=results["job_match"]["overall_match_percentage"]
                )
            except Exception as db_err:
                st.warning(f"Analysis complete, but history could not be saved: {db_err}")

            # Store in session state for display
            st.session_state["analysis_results"] = results
            st.session_state["active_resume_name"] = uploaded_file.name
            st.session_state["active_job_title"] = job_title.strip()
            st.session_state["active_resume_text"] = text
            st.session_state["active_jd_text"] = job_description
            st.session_state["active_apply_url"] = official_apply_url.strip() if official_apply_url else ""
            st.rerun()


def render_analysis_results():
    """Display the detailed analysis results as specified in Section 29."""
    results = st.session_state["analysis_results"]
    resume_name = st.session_state.get("active_resume_name", "Resume")
    job_title = st.session_state.get("active_job_title", "Target Role")
    user = get_current_user()
    candidate_name = results["contact_info"].get("candidate_name") or (user["full_name"] if user else "Candidate")

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <span style="background: #eff6ff; color: #1d4ed8; font-size: 0.85rem; font-weight: 700; padding: 4px 10px; border-radius: 4px; border: 1px solid #bfdbfe;">
                EVALUATION COMPLETED
            </span>
            <h2 style="color: #0f172a; margin-top: 0.5rem; margin-bottom: 0.25rem;">
                ATS Compatibility &amp; Match Report
            </h2>
            <p style="color: #64748b; font-size: 0.95rem;">
                Target Role: <strong>{}</strong> &bull; Resume: <strong>{}</strong>
            </p>
        </div>
    """.format(job_title, resume_name), unsafe_allow_html=True)

    # Top Banners: ATS Score (100 pts) & Job Match (%)
    final_score = results["final_ats_score"]
    job_match = results["job_match"]["overall_match_percentage"]

    st.markdown(f"""
        <div class="score-hero-container">
            <div class="score-box-main">
                <span class="score-subtitle">ATS COMPATIBILITY SCORE</span>
                <div class="score-number">{final_score} <span style="font-size: 1.8rem; font-weight: 600; opacity: 0.85;">/ 100</span></div>
                <span class="score-subtitle">Application-generated 100-point compatibility score</span>
            </div>
            <div class="score-box-match">
                <span class="score-subtitle">JOB MATCH SIMILARITY</span>
                <div class="score-number">{job_match}%</div>
                <span class="score-subtitle">Application-generated Job Match / Similarity Metric</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Score Breakdown Section
    st.markdown("### 📊 1. Exact ATS Compatibility Score Breakdown")
    sb = results["score_breakdown"]

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.markdown(f"""
            <div class="breakdown-row">
                <span class="breakdown-label">Keyword Match</span>
                <span class="breakdown-score">{sb['keyword_match']['score']} / 30 pts</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Skills Match</span>
                <span class="breakdown-score">{sb['skills_match']['score']} / 20 pts</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Resume Sections</span>
                <span class="breakdown-score">{sb['resume_sections']['score']} / 15 pts</span>
            </div>
        """, unsafe_allow_html=True)

    with b_col2:
        st.markdown(f"""
            <div class="breakdown-row">
                <span class="breakdown-label">Formatting &amp; Readability</span>
                <span class="breakdown-score">{sb['formatting']['score']} / 15 pts</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Job Relevance (Projects &amp; Summary)</span>
                <span class="breakdown-score">{sb['job_relevance']['score']} / 10 pts</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Contact Information</span>
                <span class="breakdown-score">{sb['contact_information']['score']} / 10 pts</span>
            </div>
        """, unsafe_allow_html=True)

    # Separate Job Match Breakdown
    st.markdown("#### 🎯 Job Match Breakdown")
    jmb = results["job_match"]["breakdown"]
    j_col1, j_col2, j_col3, j_col4 = st.columns(4)
    with j_col1:
        st.metric("Technical Skills", f"{jmb['Technical Skills']}%")
    with j_col2:
        st.metric("Keywords", f"{jmb['Keywords']}%")
    with j_col3:
        st.metric("Projects Presence", f"{jmb['Projects']}%")
    with j_col4:
        st.metric("Education Match", f"{jmb['Education']}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Matched & Missing Keywords
    st.markdown("### 🔑 2. Keyword Match Analysis")
    kw_col1, kw_col2 = st.columns(2)

    with kw_col1:
        st.markdown("#### ✅ Matched Keywords")
        matched_kws = results["keywords"]["matched_keywords"]
        if matched_kws:
            for kw in matched_kws:
                st.markdown(f"<span class='skill-badge skill-matched'>✅ {kw}</span>", unsafe_allow_html=True)
        else:
            st.info("No matching keywords detected from the job description.")

    with kw_col2:
        st.markdown("#### ⚠️ Missing Keywords")
        missing_kws = results["keywords"]["missing_keywords"]
        if missing_kws:
            for kw in missing_kws:
                st.markdown(f"<span class='skill-badge skill-missing'>⚠️ {kw}</span>", unsafe_allow_html=True)
            st.caption("💡 *Consider adding these only if you genuinely have knowledge or experience with them.*")
        else:
            st.success("All primary job description keywords were found in your resume!")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Skills Analysis
    st.markdown("### 🛠️ 3. Technical Skills Analysis")
    sk = results["skills"]
    sk_col1, sk_col2 = st.columns(2)

    with sk_col1:
        st.markdown("#### 📋 Skills Detected in Resume (Categorized)")
        cat_skills = sk["categorized_resume_skills"]
        has_any_skill = False
        for cat, s_list in cat_skills.items():
            if s_list:
                has_any_skill = True
                st.markdown(f"**{cat}:**")
                pills = " ".join([f"<span class='skill-badge skill-matched'>{s}</span>" for s in s_list])
                st.markdown(pills, unsafe_allow_html=True)
        if not has_any_skill:
            st.warning("No technical skills from standard categories detected.")

    with sk_col2:
        st.markdown("#### 🎯 Role Requirements Comparison")
        st.markdown(f"**Required Technical Skills ({len(sk['required_skills'])}):**")
        st.write(", ".join(sk["required_skills"]) if sk["required_skills"] else "None specified")

        st.markdown(f"**Matching Skills ({len(sk['matching_skills'])}):**")
        if sk["matching_skills"]:
            pills = " ".join([f"<span class='skill-badge skill-matched'>✓ {s}</span>" for s in sk["matching_skills"]])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.info("No overlapping skills found.")

        st.markdown(f"**Missing Required Skills ({len(sk['missing_skills'])}):**")
        if sk["missing_skills"]:
            pills = " ".join([f"<span class='skill-badge skill-missing'>! {s}</span>" for s in sk["missing_skills"]])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.success("All required technical skills matched!")

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Apply Now & Application Tracker
    st.markdown("### 🚀 4. Apply to Role & Track Application")
    apply_url = st.session_state.get("active_apply_url", "").strip()

    app_c1, app_c2 = st.columns([1.3, 1])

    with app_c1:
        st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <h4 style="margin: 0; color: #0f172a; font-size: 1.05rem;">🎯 {job_title}</h4>
                    <span style="background: #f1f5f9; color: #0f172a; font-weight: 700; padding: 3px 10px; border-radius: 12px; font-size: 0.82rem; border: 1px solid #cbd5e1;">
                        Match: {job_match}%
                    </span>
                </div>
                <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 0.75rem; line-height: 1.4;">
                    Review role details and matching requirements before applying. Submit your application directly through the employer's official career portal.
                </p>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 0.65rem 0.85rem; font-size: 0.82rem; color: #475569;">
                    <strong>Matched Skills:</strong> {", ".join(sk['matching_skills']) if sk['matching_skills'] else 'None'}<br>
                    <strong>Missing Skills:</strong> {", ".join(sk['missing_skills']) if sk['missing_skills'] else 'None'}
                </div>
            </div>
        """, unsafe_allow_html=True)

        if apply_url:
            st.markdown("""
                <div style="font-size: 0.85rem; color: #059669; font-weight: 600; margin-bottom: 0.25rem;">
                    ✓ Verified Application Link Available
                </div>
            """, unsafe_allow_html=True)
            st.link_button(
                "🚀 Apply Now on Official Company Portal ↗",
                url=apply_url,
                type="primary",
                use_container_width=True
            )
            st.caption("ℹ️ Opens the company career portal in a new tab. Applications are submitted directly to the employer.")
        else:
            st.markdown("""
                <div style="margin-top: 0.25rem; margin-bottom: 0.5rem;">
                    <button disabled style="opacity: 0.6; cursor: not-allowed; background: #94a3b8; color: #ffffff; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 600; width: 100%;">
                        Application link unavailable
                    </button>
                </div>
            """, unsafe_allow_html=True)
            st.info("ℹ️ No official application URL was provided for this job description. If you applied via campus drive or referral, you can record it in the tracker.")

        if st.button("🔍 Explore Verified Openings in Job Search", use_container_width=True):
            st.session_state["current_page"] = "job_search"
            st.rerun()

    with app_c2:
        with st.expander("📝 Log in Application Tracker", expanded=True):
            st.caption("Record and track your application status after applying:")
            with st.form("checker_track_form"):
                trk_company = st.text_input("Company Name *", value=st.session_state.get("active_company", "Target Company"))
                trk_date = st.date_input("Application Date", value=date.today())
                trk_status = st.selectbox("Status", ["Applied", "Saved", "Interview", "Offer", "Rejected"], index=0)
                trk_notes = st.text_area("Notes (optional)", value=f"Resume Match: {job_match}% | ATS Score: {final_score}/100", height=70)
                trk_submit = st.form_submit_button("💼 Save Application", use_container_width=True)

                if trk_submit:
                    if not trk_company.strip():
                        st.error("Please enter company name.")
                    else:
                        create_job_application(
                            user_id=user["id"],
                            company=trk_company.strip(),
                            role=job_title.strip(),
                            apply_url=apply_url,
                            status=trk_status,
                            applied_date=str(trk_date),
                            notes=trk_notes.strip()
                        )
                        st.success(f"Application recorded! Tracking as '{trk_status}'.")
                        st.caption("View and manage all your entries in 'My Applications'.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Fresher Resume Checklist
    st.markdown("### 🎓 5. Fresher Resume Checklist")
    chk_col1, chk_col2 = st.columns([1.5, 1])
    with chk_col1:
        for item in results["fresher_checklist"]:
            icon = "✅" if item["status"] else "⚠️"
            status_txt = "Present" if item["status"] else "Missing"
            status_color = "#059669" if item["status"] else "#d97706"
            st.markdown(f"""
                <div class="checklist-item">
                    <span>{icon}</span>
                    <strong style="width: 180px;">{item['label']}</strong>
                    <span style="color: {status_color}; font-weight: 600; width: 80px;">{status_txt}</span>
                    <span style="color: #64748b; font-size: 0.85rem;">{item['tip']}</span>
                </div>
            """, unsafe_allow_html=True)

    with chk_col2:
        st.markdown("""
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 1.25rem;">
                <h4 style="color: #1e40af; margin-top: 0; font-size: 1rem;">💡 Fresher Tip</h4>
                <p style="color: #1e3a8a; font-size: 0.88rem; line-height: 1.5; margin: 0;">
                    Recruiters hiring freshers look closely at your <strong>Academic Projects</strong> and <strong>GitHub repositories</strong>.
                    Make sure your project descriptions clearly list the frameworks and databases used, rather than just abstract summaries.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. Formatting Analysis
    st.markdown("### 📑 6. Formatting & Layout Analysis")
    fmt_details = results["formatting"]["details"]
    f_c1, f_c2 = st.columns(2)
    for idx, rule in enumerate(fmt_details):
        target_col = f_c1 if idx % 2 == 0 else f_c2
        with target_col:
            st.markdown(f"""
                <div class="breakdown-row">
                    <span>{rule['status']}</span>
                    <span style="color: #64748b; font-size: 0.85rem;">{rule['score']} / {rule['max']} pts</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 7. Actionable Suggestions
    st.markdown("### 💡 7. Actionable Improvement Suggestions")
    suggestions = results["improvement_suggestions"]
    for idx, s in enumerate(suggestions, 1):
        st.markdown(f"""
            <div class="suggestion-box">
                <strong>{idx}.</strong> {s}
            </div>
        """, unsafe_allow_html=True)

    # Notice Box
    st.markdown("""
        <div class="notice-box">
            <strong>ℹ️ Disclaimer:</strong> This evaluation is an application-generated compatibility and similarity score
            intended to help students identify resume gaps and optimize structure for standard ATS parsers.
            It is not an official score from any specific company's proprietary recruiting system and does not predict hiring or interview outcomes.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # Bottom Buttons: Download PDF & Check Another Resume
    btn_col1, btn_col2, btn_col3 = st.columns([1.5, 1.5, 1])

    with btn_col1:
        # Generate PDF bytes via ReportLab
        try:
            pdf_data = generate_ats_pdf_report(
                candidate_name=candidate_name,
                resume_name=resume_name,
                job_title=job_title,
                analysis_data=results
            )
            st.download_button(
                label="📥 Download Full ATS Report (PDF)",
                data=pdf_data,
                file_name=f"ATS_Report_{candidate_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        except Exception as pdf_err:
            st.error(f"Error generating PDF report: {pdf_err}")

    with btn_col2:
        if st.button("🔄 Check Another Resume", use_container_width=True):
            st.session_state["analysis_results"] = None
            st.session_state["active_resume_name"] = None
            st.session_state["active_job_title"] = None
            st.rerun()

    with btn_col3:
        if st.button("📊 Go to Dashboard", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
