"""
Job Search & Application Page for Fresher ATS Resume Analyzer.
Allows searching verified entry-level and fresher tech jobs, comparing
the candidate's resume against job requirements, saving jobs, reviewing
job details, and applying via verified official career portal URLs.
"""

import streamlit as st
from database.database import (
    get_jobs,
    save_job_for_user,
    unsave_job_for_user,
    is_job_saved,
    create_job_application
)
from auth.authentication import get_current_user
from utils.job_matcher import match_resume_to_job
from utils.resume_parser import parse_resume


def render_job_search_page():
    """Render the Job Search and Match view."""
    user = get_current_user()
    if not user:
        st.warning("Please sign in to access Job Search.")
        st.session_state["page"] = "login"
        st.session_state["current_page"] = "login"
        st.rerun()
        return

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">
                🔍 Fresher Job Search &amp; Match
            </h1>
            <p style="color: #64748b; font-size: 1rem; margin: 0;">
                Discover verified entry-level IT positions and benchmark your resume compatibility against official job postings.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Resume Context Banner (Active Resume or Inline Uploader)
    active_resume_text = st.session_state.get("active_resume_text")
    active_resume_name = st.session_state.get("active_resume_name")

    with st.expander("📄 Resume Matching Context", expanded=not bool(active_resume_text)):
        if active_resume_text:
            st.success(f"✅ Active resume loaded: **{active_resume_name}** (Automated job match scoring enabled)")
            col_r1, col_r2 = st.columns([3, 1])
            with col_r2:
                if st.button("Change Resume", key="change_resume_btn"):
                    st.session_state["active_resume_text"] = None
                    st.session_state["active_resume_name"] = None
                    st.rerun()
        else:
            st.info("Upload your resume (PDF/DOCX) to see real-time Job Match scores and skills gap analysis for every job.")
            new_file = st.file_uploader("Upload Resume for Job Matching", type=["pdf", "docx"], key="job_search_resume_uploader")
            if new_file is not None:
                success, text, meta, err = parse_resume(new_file.getvalue(), new_file.name)
                if success:
                    st.session_state["active_resume_text"] = text
                    st.session_state["active_resume_name"] = new_file.name
                    st.success(f"Resume '{new_file.name}' loaded successfully!")
                    st.rerun()
                else:
                    st.error(err)

    # 2. Search & Filters Bar
    st.markdown("### 🎯 Search & Filter Verified Jobs")

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1.2, 1.2, 1])

    with filter_col1:
        search_query = st.text_input(
            "Keywords or Company",
            placeholder="e.g. Python, Machine Learning, Zoho, Amazon, React",
            key="job_search_query"
        )

    with filter_col2:
        role_options = ["All", "Python Developer", "AI / Machine Learning", "Data Analyst", "Web Development"]
        selected_role = st.selectbox("Role Category", role_options, key="job_search_role")

    with filter_col3:
        location_options = ["All", "Bangalore", "Chennai", "Hyderabad", "Pune", "Mumbai", "Remote"]
        selected_location = st.selectbox("Location", location_options, key="job_search_location")

    with filter_col4:
        job_type_options = ["All", "Full-Time", "Internship", "Remote"]
        selected_type = st.selectbox("Job Type", job_type_options, key="job_search_type")

    # Map role selection to search keyword
    role_filter_map = {
        "All": None,
        "Python Developer": "python",
        "AI / Machine Learning": "machine learning",
        "Data Analyst": "data analyst",
        "Web Development": "web"
    }

    jobs = get_jobs(
        query=search_query,
        location=selected_location if selected_location != "All" else None,
        job_type=selected_type if selected_type != "All" else None,
        role=role_filter_map.get(selected_role),
        limit=50
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Disclaimer Note
    st.markdown("""
        <div style="background: #f8fafc; border-left: 4px solid #3b82f6; padding: 0.6rem 1rem; border-radius: 4px; margin-bottom: 1.25rem;">
            <span style="font-size: 0.85rem; color: #475569;">
                <strong>ℹ️ Transparency Notice:</strong> Job match scores are automated ATS compatibility indicators.
                A high score does not guarantee interview shortlisting or hiring selection. All listings reference verified official corporate career portals.
            </span>
        </div>
    """, unsafe_allow_html=True)

    # 3. Job Listings Display
    if not jobs:
        st.markdown("""
            <div style="text-align: center; padding: 3rem 1rem; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; margin: 1rem 0;">
                <span style="font-size: 2.5rem;">🔍</span>
                <h3 style="color: #0f172a; margin-top: 0.5rem; margin-bottom: 0.25rem;">No verified jobs match your criteria</h3>
                <p style="color: #64748b; font-size: 0.95rem; margin: 0;">
                    Try adjusting your search terms, role category, or location filter.
                </p>
            </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"**Showing {len(jobs)} verified fresher job opportunity{'ies' if len(jobs) > 1 else 'y'}:**")

    for job in jobs:
        job_id = job["id"]
        is_saved = is_job_saved(user["id"], job_id)

        # Calculate resume match if resume is active
        match_info = None
        if active_resume_text:
            match_info = match_resume_to_job(active_resume_text, job["description"])

        with st.container():
            st.markdown("""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            """, unsafe_allow_html=True)

            # Header row: Title, Company, Badges
            card_col1, card_col2 = st.columns([3, 1.2])

            with card_col1:
                st.markdown(f"""
                    <h3 style="color: #0f172a; margin: 0 0 0.25rem 0; font-size: 1.25rem; font-weight: 700;">
                        {job['title']}
                    </h3>
                    <p style="color: #2563eb; font-weight: 600; font-size: 0.95rem; margin: 0 0 0.5rem 0;">
                        🏢 {job['company']} &nbsp;&bull;&nbsp; 📍 {job['location']}
                    </p>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem;">
                        <span style="background: #eff6ff; color: #1e40af; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; border: 1px solid #bfdbfe;">
                            {job['job_type']}
                        </span>
                        <span style="background: #f1f5f9; color: #475569; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;">
                            🎓 {job['experience_level']}
                        </span>
                        {f'<span style="background: #ecfdf5; color: #047857; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; border: 1px solid #a7f3d0;">💰 {job["salary"]}</span>' if job.get('salary') else '<span style="background: #f8fafc; color: #64748b; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px;">Salary not disclosed</span>'}
                        <span style="color: #94a3b8; font-size: 0.75rem; padding: 2px 0;">Posted: {job.get('posted_date') or 'Recent'}</span>
                    </div>
                """, unsafe_allow_html=True)

            with card_col2:
                # Display Match Gauge / Badge if resume is active
                if match_info:
                    score = match_info["job_match_percentage"]
                    if score >= 75:
                        badge_color = "#059669"
                        badge_bg = "#ecfdf5"
                        badge_border = "#a7f3d0"
                        badge_text = "Strong Match"
                    elif score >= 50:
                        badge_color = "#d97706"
                        badge_bg = "#fffbeb"
                        badge_border = "#fde68a"
                        badge_text = "Moderate Match"
                    else:
                        badge_color = "#dc2626"
                        badge_bg = "#fef2f2"
                        badge_border = "#fecaca"
                        badge_text = "Low Match"

                    st.markdown(f"""
                        <div style="background: {badge_bg}; border: 1px solid {badge_border}; border-radius: 8px; padding: 0.5rem 0.75rem; text-align: center;">
                            <span style="color: {badge_color}; font-size: 1.4rem; font-weight: 800;">{score}%</span><br>
                            <span style="color: {badge_color}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">{badge_text}</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("Upload resume to view Job Match")

            # Skills badges row
            req_skills = job.get("required_skills_list", [])
            if req_skills:
                skills_html = "".join([
                    f"<span style='background: #e2e8f0; color: #1e293b; font-size: 0.75rem; font-weight: 500; padding: 2px 6px; border-radius: 4px; margin-right: 4px; margin-bottom: 4px; display: inline-block;'>{s}</span>"
                    for s in req_skills
                ])
                st.markdown(f"<div style='margin: 0.5rem 0;'><strong style='font-size: 0.8rem; color: #475569;'>Required Skills:</strong><br>{skills_html}</div>", unsafe_allow_html=True)

            # Match Breakdown Expander (if resume active)
            if match_info:
                with st.expander(f"📊 View Match Breakdown for {job['title']}"):
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.markdown("**✅ Matched Skills in Your Resume:**")
                        if match_info["matched_skills"]:
                            for s in match_info["matched_skills"]:
                                st.markdown(f"- 🟢 **{s}**")
                        else:
                            st.caption("None of the required technical skills were detected in your resume.")
                    with col_m2:
                        st.markdown("**⚠️ Missing Skills from Job Requirement:**")
                        if match_info["missing_skills"]:
                            for s in match_info["missing_skills"]:
                                st.markdown(f"- 🔴 {s}")
                        else:
                            st.caption("Great job! You have all primary technical skills required.")

            # Job Details Expander
            with st.expander(f"📄 Full Job Description & Requirements"):
                st.markdown(f"**Source:** {job.get('source', 'Official Portal')}")
                st.text(job["description"])

            # Action Buttons Row
            b_col1, b_col2, b_col3, b_col4 = st.columns([1.5, 1.2, 1.5, 1])

            # Apply Button
            with b_col1:
                apply_url = job.get("apply_url", "").strip()
                if apply_url and apply_url.startswith(("http://", "https://")):
                    st.link_button(
                        "🚀 Apply Now ↗",
                        url=apply_url,
                        help=f"Opens verified official career portal: {apply_url}",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.button(
                        "🔒 Application Link Unavailable",
                        disabled=True,
                        help="No official online application link is currently available for this position.",
                        use_container_width=True,
                        key=f"disabled_apply_{job_id}"
                    )

            # Save / Unsave Button
            with b_col2:
                if is_saved:
                    if st.button("⭐ Saved", key=f"unsave_btn_{job_id}", use_container_width=True):
                        unsave_job_for_user(user["id"], job_id)
                        st.success("Job removed from saved list.")
                        st.rerun()
                else:
                    if st.button("☆ Save Job", key=f"save_btn_{job_id}", use_container_width=True):
                        save_job_for_user(user["id"], job_id)
                        st.success("Job saved successfully!")
                        st.rerun()

            # Record in Application Tracker button
            with b_col3:
                track_modal_key = f"show_track_modal_{job_id}"
                if st.button("📝 Log in Tracker", key=f"track_btn_{job_id}", use_container_width=True, help="Record that you applied to this job in your Application Tracker"):
                    st.session_state[track_modal_key] = not st.session_state.get(track_modal_key, False)

            # Check this job in Resume Checker
            with b_col4:
                if st.button("⚡ Test in Checker", key=f"test_checker_btn_{job_id}", use_container_width=True, help="Load this Job Title and Description directly into the Resume Checker"):
                    st.session_state["active_job_title"] = job["title"]
                    st.session_state["active_jd_text"] = job["description"]
                    st.session_state["page"] = "resume_checker"
                    st.session_state["current_page"] = "resume_checker"
                    st.rerun()

            # Optional inline tracker drawer
            if st.session_state.get(f"show_track_modal_{job_id}", False):
                st.markdown("""
                    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 1rem; margin-top: 0.75rem;">
                        <strong style="color: #0f172a;">Record Application in Application Tracker</strong>
                        <p style="color: #64748b; font-size: 0.8rem; margin: 0 0 0.5rem 0;">
                            Logged status will be marked with a <em>[Manually Logged by Candidate]</em> indicator.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                with st.form(key=f"record_app_form_{job_id}"):
                    c_app1, c_app2 = st.columns(2)
                    with c_app1:
                        app_status = st.selectbox("Application Status", ["Applied", "Interview", "Offer", "Rejected", "Saved"], key=f"app_status_{job_id}")
                    with c_app2:
                        app_notes = st.text_input("Notes (Optional)", placeholder="e.g. Applied via official portal, assessment pending", key=f"app_notes_{job_id}")

                    if st.form_submit_button("Confirm & Save to Tracker", type="primary"):
                        create_job_application(
                            user_id=user["id"],
                            job_title=job["title"],
                            company_name=job["company"],
                            location=job["location"],
                            apply_url=job.get("apply_url", ""),
                            status=app_status,
                            notes=app_notes,
                            job_id=job_id
                        )
                        st.session_state[f"show_track_modal_{job_id}"] = False
                        st.success(f"Recorded application to {job['company']} in your tracker!")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
