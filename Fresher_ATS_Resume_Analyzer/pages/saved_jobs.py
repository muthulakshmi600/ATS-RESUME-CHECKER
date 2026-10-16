"""
Saved Jobs Page for Fresher ATS Resume Analyzer.
Allows authenticated users to view, manage, and apply to their bookmarked jobs.
"""

import streamlit as st
from database.database import (
    get_saved_jobs_for_user,
    unsave_job_for_user,
    create_job_application
)
from auth.authentication import get_current_user
from utils.job_matcher import match_resume_to_job


def render_saved_jobs_page():
    """Render the candidate's bookmarked jobs."""
    user = get_current_user()
    if not user:
        st.warning("Please sign in to view your saved jobs.")
        st.session_state["page"] = "login"
        st.session_state["current_page"] = "login"
        st.rerun()
        return

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">
                ⭐ Saved Jobs
            </h1>
            <p style="color: #64748b; font-size: 1rem; margin: 0;">
                Review your bookmarked opportunities, compare compatibility, and apply when ready.
            </p>
        </div>
    """, unsafe_allow_html=True)

    saved_jobs = get_saved_jobs_for_user(user["id"])
    active_resume_text = st.session_state.get("active_resume_text")

    if not saved_jobs:
        st.markdown("""
            <div style="text-align: center; padding: 3rem 1rem; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; margin: 1rem 0;">
                <span style="font-size: 2.5rem;">⭐</span>
                <h3 style="color: #0f172a; margin-top: 0.5rem; margin-bottom: 0.25rem;">No saved jobs yet</h3>
                <p style="color: #64748b; font-size: 0.95rem; margin: 0 0 1rem 0;">
                    Bookmark jobs from the Job Search page to review them here later.
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔍 Explore Verified Fresher Jobs", type="primary", use_container_width=False):
            st.session_state["page"] = "job_search"
            st.session_state["current_page"] = "job_search"
            st.rerun()
        return

    st.markdown(f"**You have {len(saved_jobs)} saved job opportunity{'ies' if len(saved_jobs) > 1 else 'y'}:**")

    for job in saved_jobs:
        job_id = job["id"]

        match_info = None
        if active_resume_text:
            match_info = match_resume_to_job(active_resume_text, job["description"])

        with st.container():
            col1, col2 = st.columns([3, 1.2])

            with col1:
                st.markdown(f"""
                    <h3 style="color: #0f172a; margin: 0 0 0.25rem 0; font-size: 1.2rem; font-weight: 700;">
                        {job['title']}
                    </h3>
                    <p style="color: #2563eb; font-weight: 600; font-size: 0.95rem; margin: 0 0 0.5rem 0;">
                        🏢 {job['company']} &nbsp;&bull;&nbsp; 📍 {job['location']}
                    </p>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem;">
                        <span style="background: #eff6ff; color: #1e40af; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;">
                            {job['job_type']}
                        </span>
                        <span style="background: #f1f5f9; color: #475569; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;">
                            🎓 {job['experience_level']}
                        </span>
                        {f'<span style="background: #ecfdf5; color: #047857; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;">💰 {job["salary"]}</span>' if job.get('salary') else ''}
                        <span style="color: #94a3b8; font-size: 0.75rem;">Saved on: {job.get('saved_at', '')[:10]}</span>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                if match_info:
                    score = match_info["job_match_percentage"]
                    badge_color = "#059669" if score >= 75 else ("#d97706" if score >= 50 else "#dc2626")
                    badge_bg = "#ecfdf5" if score >= 75 else ("#fffbeb" if score >= 50 else "#fef2f2")
                    st.markdown(f"""
                        <div style="background: {badge_bg}; border: 1px solid {badge_color}33; border-radius: 8px; padding: 0.5rem 0.75rem; text-align: center;">
                            <span style="color: {badge_color}; font-size: 1.3rem; font-weight: 800;">{score}%</span><br>
                            <span style="color: {badge_color}; font-size: 0.75rem; font-weight: 700;">JOB MATCH</span>
                        </div>
                    """, unsafe_allow_html=True)

            with st.expander(f"📄 View Job Description & Requirements"):
                st.text(job["description"])

            act_col1, act_col2, act_col3 = st.columns([1.5, 1.5, 1])

            with act_col1:
                apply_url = job.get("apply_url", "").strip()
                if apply_url and apply_url.startswith(("http://", "https://")):
                    st.link_button(
                        "🚀 Apply Now ↗",
                        url=apply_url,
                        help=f"Opens official application portal: {apply_url}",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.button("🔒 Application Link Unavailable", disabled=True, use_container_width=True, key=f"saved_disabled_apply_{job_id}")

            with act_col2:
                if st.button("📝 Log in Application Tracker", key=f"saved_track_btn_{job_id}", use_container_width=True):
                    st.session_state[f"show_saved_track_{job_id}"] = not st.session_state.get(f"show_saved_track_{job_id}", False)

            with act_col3:
                if st.button("🗑️ Remove", key=f"remove_saved_{job_id}", use_container_width=True):
                    unsave_job_for_user(user["id"], job_id)
                    st.success("Removed from saved jobs.")
                    st.rerun()

            if st.session_state.get(f"show_saved_track_{job_id}", False):
                with st.form(key=f"saved_record_app_form_{job_id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        status = st.selectbox("Application Status", ["Applied", "Interview", "Offer", "Rejected", "Saved"], key=f"saved_status_{job_id}")
                    with c2:
                        notes = st.text_input("Notes (Optional)", placeholder="e.g. Applied via official portal", key=f"saved_notes_{job_id}")

                    if st.form_submit_button("Record in Tracker", type="primary"):
                        create_job_application(
                            user_id=user["id"],
                            job_title=job["title"],
                            company_name=job["company"],
                            location=job["location"],
                            apply_url=job.get("apply_url", ""),
                            status=status,
                            notes=notes,
                            job_id=job_id
                        )
                        st.session_state[f"show_saved_track_{job_id}"] = False
                        st.success("Application logged successfully!")
                        st.rerun()

            st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
