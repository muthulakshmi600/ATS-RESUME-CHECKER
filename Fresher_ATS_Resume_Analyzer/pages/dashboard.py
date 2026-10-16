"""
Dashboard Page for Fresher ATS Resume Analyzer.
Displays greeting, personal ATS analytics, summary KPI cards, quick actions,
and recent analysis history table for the authenticated user.
"""

import streamlit as st
import pandas as pd
from database.database import get_user_stats, get_user_history, get_user_applications
from auth.authentication import get_current_user, logout


def render_dashboard_page():
    """Render user dashboard with personal metrics and recent analysis records."""
    user = get_current_user()
    if not user:
        st.warning("Session expired. Please sign in.")
        st.session_state["page"] = "login"
        st.session_state["current_page"] = "login"
        st.rerun()
        return

    # Header Greeting
    user_name = user.get("full_name", "Student")
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">
                    Welcome, {user_name} 👋
                </h1>
                <p style="color: #64748b; font-size: 1rem; margin: 0;">
                    Fresher Candidate Dashboard &bull; Track ATS benchmarks, discover verified roles, and track applications
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Fetch User-Specific Stats strictly for logged-in user_id
    stats = get_user_stats(user["id"])

    # Row 1: 4 Resume Analytics KPI Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
            <div class="metric-card metric-card-blue">
                <span class="metric-label">Resumes Analyzed</span>
                <span class="metric-value">{stats['total_resumes']}</span>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="metric-card metric-card-green">
                <span class="metric-label">Average ATS Score</span>
                <span class="metric-value">{stats['avg_ats']}<span style="font-size: 1rem; font-weight: 500; color: #64748b;"> / 100</span></span>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="metric-card metric-card-amber">
                <span class="metric-label">Latest ATS Score</span>
                <span class="metric-value">{stats['latest_ats']}<span style="font-size: 1rem; font-weight: 500; color: #64748b;"> / 100</span></span>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="metric-card metric-card-purple">
                <span class="metric-label">Latest Job Match</span>
                <span class="metric-value">{stats['latest_job_match']}%</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: 2 Job Search & Tracker KPI Cards
    jc1, jc2 = st.columns(2)
    with jc1:
        st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #2563eb; border-radius: 10px; padding: 1.15rem 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Saved Jobs</span>
                    <h2 style="margin: 0.25rem 0 0 0; color: #0f172a; font-size: 1.8rem; font-weight: 800;">{stats.get('total_saved_jobs', 0)}</h2>
                    <span style="font-size: 0.8rem; color: #94a3b8;">Bookmarked for review</span>
                </div>
                <div style="font-size: 2.2rem; opacity: 0.8;">⭐</div>
            </div>
        """, unsafe_allow_html=True)

    with jc2:
        st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #059669; border-radius: 10px; padding: 1.15rem 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Active Applications</span>
                    <h2 style="margin: 0.25rem 0 0 0; color: #0f172a; font-size: 1.8rem; font-weight: 800;">{stats.get('total_applications', 0)}</h2>
                    <span style="font-size: 0.8rem; color: #94a3b8;">Logged in candidate tracker</span>
                </div>
                <div style="font-size: 2.2rem; opacity: 0.8;">💼</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action Buttons Row
    act1, act2, act3, act4, act5, act6 = st.columns(6)
    with act1:
        if st.button("📄 Check Resume", use_container_width=True, type="primary", key="dash_btn_check_resume"):
            st.session_state["page"] = "resume_checker"
            st.session_state["current_page"] = "resume_checker"
            st.rerun()
    with act2:
        if st.button("🔍 Search Jobs", use_container_width=True, key="dash_btn_search_jobs"):
            st.session_state["page"] = "job_search"
            st.session_state["current_page"] = "job_search"
            st.rerun()
    with act3:
        if st.button("⭐ Saved Jobs", use_container_width=True, key="dash_btn_saved_jobs"):
            st.session_state["page"] = "saved_jobs"
            st.session_state["current_page"] = "saved_jobs"
            st.rerun()
    with act4:
        if st.button("💼 My Tracker", use_container_width=True, key="dash_btn_applications"):
            st.session_state["page"] = "applications"
            st.session_state["current_page"] = "applications"
            st.rerun()
    with act5:
        if st.button("📊 History", use_container_width=True, key="dash_btn_history"):
            st.session_state["page"] = "history"
            st.session_state["current_page"] = "history"
            st.rerun()
    with act6:
        if st.button("👤 Profile", use_container_width=True, key="dash_btn_profile"):
            st.session_state["page"] = "profile"
            st.session_state["current_page"] = "profile"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Two columns: Recent Analyses & Recent Applications
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📋 Recent Analyses")
        recent_history = get_user_history(user["id"], limit=5)
        if recent_history:
            table_data = []
            for row in recent_history:
                table_data.append({
                    "Resume": row["resume_name"],
                    "Target Role": row["job_title"],
                    "ATS Score": f"{row['ats_score']} / 100",
                    "Match": f"{row['job_match_score']}%"
                })
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No resumes analyzed yet. Click **Check Resume** to start!")

    with col_right:
        st.markdown("### 💼 Recent Applications")
        user_apps = get_user_applications(user["id"])
        if user_apps:
            app_table = []
            for app in user_apps[:5]:
                app_table.append({
                    "Company": app["company"],
                    "Role": app["role"],
                    "Status": app["status"],
                    "Applied": str(app["applied_date"])
                })
            df_app = pd.DataFrame(app_table)
            st.dataframe(df_app, use_container_width=True, hide_index=True)
        else:
            st.info("No applications logged yet. Search jobs and apply, then record them in your tracker!")
