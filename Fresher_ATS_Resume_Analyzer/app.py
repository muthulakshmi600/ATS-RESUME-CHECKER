"""
Fresher ATS Resume Analyzer - Main Application Entrypoint.
Orchestrates page routing, session state management, database initialization,
and sidebar navigation with strict authentication guards.
"""

import os
import sys
import streamlit as st

# Ensure the root directory of this app is in the Python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Initialize SQLite database schema
from database.database import init_db
init_db()

from auth.authentication import is_authenticated, get_current_user, logout
from pages.landing import render_landing_page
from pages.login import render_login_page
from pages.register import render_register_page
from pages.dashboard import render_dashboard_page
from pages.resume_checker import render_resume_checker_page
from pages.history import render_history_page
from pages.profile import render_profile_page
from pages.job_search import render_job_search_page
from pages.saved_jobs import render_saved_jobs_page
from pages.applications import render_applications_page

# Configure Streamlit page settings
st.set_page_config(
    page_title="Fresher ATS Resume Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    """Inject custom styling from assets/style.css."""
    css_path = os.path.join(CURRENT_DIR, "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_session_state():
    """Initialize necessary session state keys."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None

    # Harmonize page and current_page keys
    if "page" in st.session_state and "current_page" not in st.session_state:
        st.session_state["current_page"] = st.session_state["page"]
    elif "current_page" in st.session_state and "page" not in st.session_state:
        st.session_state["page"] = st.session_state["current_page"]
    elif "page" not in st.session_state and "current_page" not in st.session_state:
        st.session_state["page"] = "landing"
        st.session_state["current_page"] = "landing"

    if "analysis_results" not in st.session_state:
        st.session_state["analysis_results"] = None


def render_sidebar():
    """Render the sidebar navigation for authenticated and unauthenticated users."""
    user = get_current_user()

    with st.sidebar:
        # App branding in sidebar
        st.markdown("""
            <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🎓</span>
                <strong style="font-size: 1.1rem; color: #0f172a; margin-left: 0.5rem;">Fresher ATS Pro</strong>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0.25rem 0 0 0;">
                    Resume Optimizer for College Grads
                </p>
            </div>
        """, unsafe_allow_html=True)

        if is_authenticated() and user:
            # User profile card
            user_name = st.session_state.get("user_name") or user.get("full_name", "Student")
            user_email = st.session_state.get("user_email") or user.get("email", "")
            st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1.25rem;">
                    <span style="font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Candidate</span><br>
                    <strong style="color: #0f172a; font-size: 0.95rem;">{user_name}</strong><br>
                    <span style="color: #64748b; font-size: 0.8rem;">{user_email}</span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("### Navigation")

            current = st.session_state.get("page") or st.session_state.get("current_page", "dashboard")

            # Nav items with active state styling
            if st.button("📊 Dashboard", use_container_width=True, type="primary" if current == "dashboard" else "secondary", key="sidebar_nav_dashboard"):
                st.session_state["page"] = "dashboard"
                st.session_state["current_page"] = "dashboard"
                st.rerun()

            if st.button("📄 Check Resume", use_container_width=True, type="primary" if current in ["resume_checker", "check_resume"] else "secondary", key="sidebar_nav_check_resume"):
                st.session_state["page"] = "resume_checker"
                st.session_state["current_page"] = "resume_checker"
                st.rerun()

            if st.button("🔍 Search Jobs", use_container_width=True, type="primary" if current == "job_search" else "secondary", key="sidebar_nav_job_search"):
                st.session_state["page"] = "job_search"
                st.session_state["current_page"] = "job_search"
                st.rerun()

            if st.button("⭐ Saved Jobs", use_container_width=True, type="primary" if current == "saved_jobs" else "secondary", key="sidebar_nav_saved_jobs"):
                st.session_state["page"] = "saved_jobs"
                st.session_state["current_page"] = "saved_jobs"
                st.rerun()

            if st.button("💼 My Applications", use_container_width=True, type="primary" if current == "applications" else "secondary", key="sidebar_nav_applications"):
                st.session_state["page"] = "applications"
                st.session_state["current_page"] = "applications"
                st.rerun()

            if st.button("🕒 Analysis History", use_container_width=True, type="primary" if current in ["history", "analysis_history"] else "secondary", key="sidebar_nav_history"):
                st.session_state["page"] = "history"
                st.session_state["current_page"] = "history"
                st.rerun()

            if st.button("👤 My Profile", use_container_width=True, type="primary" if current == "profile" else "secondary", key="sidebar_nav_profile"):
                st.session_state["page"] = "profile"
                st.session_state["current_page"] = "profile"
                st.rerun()

            st.markdown("<br><hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

            if st.button("🚪 Sign Out", use_container_width=True, key="sidebar_signout_btn"):
                logout()

        else:
            # Unauthenticated navigation
            st.markdown("### Welcome")
            st.caption("Sign in or create an account to start analyzing your resume against target roles.")
            if st.button("Home Page", use_container_width=True, key="sidebar_unauth_home"):
                st.session_state["page"] = "landing"
                st.session_state["current_page"] = "landing"
                st.rerun()
            if st.button("Sign In", use_container_width=True, key="sidebar_unauth_login"):
                st.session_state["page"] = "login"
                st.session_state["current_page"] = "login"
                st.rerun()
            if st.button("Create Account", use_container_width=True, type="primary", key="sidebar_unauth_register"):
                st.session_state["page"] = "register"
                st.session_state["current_page"] = "register"
                st.rerun()


def main():
    """Main routing controller."""
    load_custom_css()
    init_session_state()

    # Synchronize page keys
    page = st.session_state.get("page") or st.session_state.get("current_page", "landing")
    # Normalize aliases
    if page == "check_resume":
        page = "resume_checker"
    elif page == "analysis_history":
        page = "history"

    authenticated = is_authenticated()

    # Protected routes: Dashboard, Check Resume, Analysis Result, Job Search, Saved Jobs, Applications, History, Profile
    protected_pages = ["dashboard", "resume_checker", "analysis_result", "job_search", "saved_jobs", "applications", "history", "profile"]
    if page in protected_pages and not authenticated:
        st.warning("Please sign in to access this page.")
        st.session_state["page"] = "login"
        st.session_state["current_page"] = "login"
        st.rerun()
        return

    # Render sidebar
    render_sidebar()

    # Route to active view
    if page == "landing":
        render_landing_page()
    elif page == "login":
        render_login_page()
    elif page == "register":
        render_register_page()
    elif page == "dashboard":
        render_dashboard_page()
    elif page in ["resume_checker", "analysis_result"]:
        render_resume_checker_page()
    elif page == "job_search":
        render_job_search_page()
    elif page == "saved_jobs":
        render_saved_jobs_page()
    elif page == "applications":
        render_applications_page()
    elif page == "history":
        render_history_page()
    elif page == "profile":
        render_profile_page()
    else:
        render_landing_page()


if __name__ == "__main__":
    main()
