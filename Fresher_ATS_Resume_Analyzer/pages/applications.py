"""
Application Tracker Page for Fresher ATS Resume Analyzer.
Allows candidates to record and track applications submitted to corporate websites.
Supports stages: Saved, Applied, Interview, Rejected, and Offer.
Clearly distinguishes manually logged records with transparent candidate ownership badges.
"""

import streamlit as st
from datetime import datetime
from database.database import (
    get_user_applications,
    create_job_application,
    update_job_application_status,
    delete_job_application,
    get_user_job_stats
)
from auth.authentication import get_current_user


def render_applications_page():
    """Render the Application Tracker dashboard & management interface."""
    user = get_current_user()
    if not user:
        st.warning("Please sign in to access your Application Tracker.")
        st.session_state["page"] = "login"
        st.session_state["current_page"] = "login"
        st.rerun()
        return

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">
                💼 My Application Tracker
            </h1>
            <p style="color: #64748b; font-size: 1rem; margin: 0;">
                Keep track of your job submissions, interview stages, follow-ups, and offers in one organized dashboard.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Pipeline Summary KPI Cards
    job_stats = get_user_job_stats(user["id"])
    sc = job_stats["status_counts"]

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; text-align: center;">
                <span style="font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 700;">Total Logged</span>
                <div style="font-size: 1.5rem; font-weight: 800; color: #0f172a;">{job_stats['total_applications']}</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 0.75rem; text-align: center;">
                <span style="font-size: 0.8rem; color: #1d4ed8; text-transform: uppercase; font-weight: 700;">Applied</span>
                <div style="font-size: 1.5rem; font-weight: 800; color: #1e40af;">{sc.get('Applied', 0)}</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
            <div style="background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 8px; padding: 0.75rem; text-align: center;">
                <span style="font-size: 0.8rem; color: #6d28d9; text-transform: uppercase; font-weight: 700;">Interview</span>
                <div style="font-size: 1.5rem; font-weight: 800; color: #5b21b6;">{sc.get('Interview', 0)}</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 0.75rem; text-align: center;">
                <span style="font-size: 0.8rem; color: #047857; text-transform: uppercase; font-weight: 700;">Offer</span>
                <div style="font-size: 1.5rem; font-weight: 800; color: #065f46;">{sc.get('Offer', 0)}</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi5:
        st.markdown(f"""
            <div style="background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 0.75rem; text-align: center;">
                <span style="font-size: 0.8rem; color: #be123c; text-transform: uppercase; font-weight: 700;">Rejected</span>
                <div style="font-size: 1.5rem; font-weight: 800; color: #9f1239;">{sc.get('Rejected', 0)}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Add New Application Form (Collapsible)
    with st.expander("➕ Log a New Job Application"):
        with st.form("manual_add_application_form"):
            fa1, fa2 = st.columns(2)
            with fa1:
                company_name = st.text_input("Company Name *", placeholder="e.g. Infosys, TCS, Amazon")
                job_title = st.text_input("Job Title *", placeholder="e.g. Junior Python Developer")
                location = st.text_input("Location", placeholder="e.g. Bangalore, Hybrid, Remote")
            with fa2:
                apply_url = st.text_input("Application / Careers Portal URL", placeholder="https://careers.company.com/job/1234")
                status = st.selectbox("Current Status", ["Applied", "Interview", "Offer", "Rejected", "Saved"], index=0)
                applied_date = st.date_input("Date Applied", value=datetime.today())

            notes = st.text_area("Notes & Next Steps", placeholder="e.g. Completed initial online test; waiting for technical round schedule.")

            if st.form_submit_button("Save Application", type="primary"):
                if not company_name.strip() or not job_title.strip():
                    st.error("Company Name and Job Title are required.")
                else:
                    create_job_application(
                        user_id=user["id"],
                        job_title=job_title,
                        company_name=company_name,
                        location=location,
                        apply_url=apply_url,
                        status=status,
                        applied_date=applied_date.strftime("%Y-%m-%d"),
                        notes=notes
                    )
                    st.success(f"Recorded application to {company_name}!")
                    st.rerun()

    # 3. Filter applications by status
    status_filter_col1, status_filter_col2 = st.columns([1.5, 3])
    with status_filter_col1:
        selected_status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Applied", "Interview", "Offer", "Rejected", "Saved"],
            key="apps_status_filter"
        )

    applications = get_user_applications(
        user_id=user["id"],
        status_filter=selected_status_filter if selected_status_filter != "All" else None
    )

    # Transparency Notice regarding manually recorded status
    st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 0.6rem 1rem; margin: 0.75rem 0 1rem 0;">
            <span style="font-size: 0.8rem; color: #475569;">
                <strong>📌 Candidate Tracking Notice:</strong> All records below carry a
                <span style="background: #f1f5f9; color: #334155; font-weight: 600; padding: 1px 6px; border-radius: 3px; border: 1px solid #cbd5e1;">[Manually Logged by Candidate]</span>
                designation to differentiate candidate-maintained records from external company verification.
            </span>
        </div>
    """, unsafe_allow_html=True)

    if not applications:
        st.info("No applications match the selected status filter.")
        return

    # 4. Applications List / Cards
    status_color_map = {
        "Applied": ("#1d4ed8", "#eff6ff", "#bfdbfe"),
        "Interview": ("#6d28d9", "#f5f3ff", "#ddd6fe"),
        "Offer": ("#047857", "#ecfdf5", "#a7f3d0"),
        "Rejected": ("#9f1239", "#fff1f2", "#fecdd3"),
        "Saved": ("#b45309", "#fffbeb", "#fde68a"),
    }

    for app in applications:
        app_id = app["id"]
        current_status = app["status"]
        c_text, c_bg, c_border = status_color_map.get(current_status, ("#0f172a", "#f8fafc", "#e2e8f0"))

        with st.container():
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; margin-bottom: 0.75rem; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div>
                            <h3 style="color: #0f172a; margin: 0; font-size: 1.2rem; font-weight: 700;">
                                {app['job_title']}
                            </h3>
                            <strong style="color: #2563eb; font-size: 1rem;">🏢 {app['company_name']}</strong>
                            {f"<span style='color: #64748b; font-size: 0.9rem;'> &bull; 📍 {app['location']}</span>" if app.get('location') else ""}
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem;">
                            <span style="background: {c_bg}; color: {c_text}; border: 1px solid {c_border}; font-weight: 700; font-size: 0.85rem; padding: 4px 12px; border-radius: 6px;">
                                {current_status.upper()}
                            </span>
                            <span style="background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; font-size: 0.7rem; font-weight: 600; padding: 2px 6px; border-radius: 4px;">
                                👤 Manually Logged by Candidate
                            </span>
                        </div>
                    </div>
                    <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 0.5rem;">
                        📅 <strong>Applied Date:</strong> {app.get('applied_date', 'Not specified')}
                        &nbsp;&bull;&nbsp;
                        ⏱️ <strong>Last Updated:</strong> {app.get('updated_at', app.get('created_at', ''))[:16]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if app.get("notes"):
                st.markdown(f"**📝 Notes:** {app['notes']}")

            if app.get("apply_url") and app["apply_url"].startswith(("http://", "https://")):
                st.markdown(f"🔗 [Company Application Link ↗]({app['apply_url']})")

            # Inline update controls
            with st.expander(f"⚙️ Update Status & Notes for {app['company_name']}"):
                with st.form(key=f"update_app_form_{app_id}"):
                    u_col1, u_col2 = st.columns(2)
                    with u_col1:
                        new_status = st.selectbox(
                            "Update Status",
                            ["Applied", "Interview", "Offer", "Rejected", "Saved"],
                            index=["Applied", "Interview", "Offer", "Rejected", "Saved"].index(current_status) if current_status in ["Applied", "Interview", "Offer", "Rejected", "Saved"] else 0,
                            key=f"upd_status_{app_id}"
                        )
                    with u_col2:
                        new_notes = st.text_input("Update Notes", value=app.get("notes", ""), key=f"upd_notes_{app_id}")

                    sub_col1, sub_col2 = st.columns([1, 1])
                    with sub_col1:
                        if st.form_submit_button("Save Changes", type="primary"):
                            update_job_application_status(
                                application_id=app_id,
                                user_id=user["id"],
                                status=new_status,
                                notes=new_notes
                            )
                            st.success("Application updated!")
                            st.rerun()

                # Separate delete button outside form
                if st.button("🗑️ Delete Application Record", key=f"del_app_{app_id}"):
                    delete_job_application(app_id, user["id"])
                    st.success("Application record removed.")
                    st.rerun()

            st.markdown("<hr style='margin: 0.75rem 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
