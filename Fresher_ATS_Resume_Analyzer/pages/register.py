"""
Registration Page for Fresher ATS Resume Analyzer.
Collects Full Name, Email / Username, Password, Confirm Password with strict client/server validations
and bcrypt password hashing.
"""

import streamlit as st
from auth.authentication import register_user


def render_register_page():
    """Render the user registration form and handle validation."""
    col1, col2, col3 = st.columns([1, 1.8, 1])

    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="color: #0f172a; margin-bottom: 0.25rem;">Create Your Account</h2>
                <p style="color: #64748b; font-size: 0.95rem;">Join Fresher ATS Resume Analyzer to benchmark and improve your resume</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            full_name = st.text_input(
                "Full Name *",
                placeholder="e.g., Alex Johnson",
                key="register_full_name_input"
            )
            email = st.text_input(
                "Email / Username *",
                placeholder="e.g., student@example.com or username",
                key="register_email_input"
            )
            password = st.text_input(
                "Password (min 8 characters) *",
                type="password",
                placeholder="••••••••",
                key="register_password_input"
            )
            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="••••••••",
                key="register_confirm_password_input"
            )

            st.caption("🔒 Passwords are securely hashed with bcrypt. We never store plaintext passwords.")
            submit = st.form_submit_button(
                "Create Account",
                use_container_width=True,
                type="primary",
                key="register_submit_btn"
            )

            if submit:
                success, msg = register_user(full_name, email, password, confirm_password)
                if success:
                    st.session_state["registration_success_msg"] = "Account created successfully. Please login."
                    st.session_state["page"] = "login"
                    st.session_state["current_page"] = "login"
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("<br>", unsafe_allow_html=True)
        sub_col1, sub_col2 = st.columns([1.5, 1])
        with sub_col1:
            st.markdown("Already have an account?")
        with sub_col2:
            if st.button("Sign In Here", use_container_width=True, key="register_to_login_btn"):
                st.session_state["page"] = "login"
                st.session_state["current_page"] = "login"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Landing Page", use_container_width=True, key="register_to_landing_btn"):
            st.session_state["page"] = "landing"
            st.session_state["current_page"] = "landing"
            st.rerun()
