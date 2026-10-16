"""
Login Page for Fresher ATS Resume Analyzer.
Validates email/username and password using bcrypt verification and establishes Streamlit session state.
"""

import streamlit as st
from auth.authentication import login_user


def render_login_page():
    """Render login form and authenticate user."""
    col1, col2, col3 = st.columns([1, 1.8, 1])

    with col2:
        # Check if there is a registration success message from previous step
        if st.session_state.get("registration_success_msg"):
            st.success(st.session_state.pop("registration_success_msg"))

        st.markdown("""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="color: #0f172a; margin-bottom: 0.25rem;">Sign In to Your Account</h2>
                <p style="color: #64748b; font-size: 0.95rem;">Enter your credentials to access your dashboard and resume reports</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "Email / Username",
                placeholder="e.g., student@example.com or username",
                key="login_email_input"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••",
                key="login_password_input"
            )

            submit = st.form_submit_button(
                "Login",
                use_container_width=True,
                type="primary",
                key="login_submit_btn"
            )

            if submit:
                success, result = login_user(email, password)
                if success:
                    user = result
                    # Set exact required session state keys
                    st.session_state["authenticated"] = True
                    st.session_state["user_id"] = user["id"]
                    st.session_state["user_name"] = user["full_name"]
                    st.session_state["user_email"] = user["email"]
                    st.session_state["page"] = "dashboard"
                    st.session_state["current_page"] = "dashboard"
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    # Do not redirect to Dashboard when login fails
                    st.error(result)

        st.markdown("<br>", unsafe_allow_html=True)
        sub_col1, sub_col2 = st.columns([1.5, 1])
        with sub_col1:
            st.markdown("Don't have an account yet?")
        with sub_col2:
            if st.button("Create Account", use_container_width=True, key="login_to_register_btn"):
                st.session_state["page"] = "register"
                st.session_state["current_page"] = "register"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Landing Page", use_container_width=True, key="login_to_landing_btn"):
            st.session_state["page"] = "landing"
            st.session_state["current_page"] = "landing"
            st.rerun()
