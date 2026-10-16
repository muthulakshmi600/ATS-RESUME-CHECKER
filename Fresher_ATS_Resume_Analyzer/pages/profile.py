"""
User Profile Page for Fresher ATS Resume Analyzer.
Allows the logged-in candidate to view account details, update their name,
and link their LinkedIn and GitHub profiles.
"""

import streamlit as st
from database.database import get_user_by_id, update_user_profile
from auth.authentication import get_current_user


def render_profile_page():
    """Render profile info, update form, and profile optimization tips."""
    current_user = get_current_user()
    if not current_user:
        st.warning("Please sign in to view your profile.")
        st.session_state["page"] = "login"
        st.session_state["current_page"] = "login"
        st.rerun()
        return

    # Refresh user data from database
    user = get_user_by_id(current_user["id"])
    if not user:
        user = current_user

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">
                Candidate Profile
            </h1>
            <p style="color: #64748b; font-size: 1rem; margin: 0;">
                Manage your personal details and professional links.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("### Profile Information")

        # Static Account Info
        st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.25rem;">
                <div style="margin-bottom: 0.5rem;"><span style="color: #64748b; font-size: 0.85rem;">Registered Email:</span><br><strong>{user['email']}</strong></div>
                <div><span style="color: #64748b; font-size: 0.85rem;">Account Created:</span><br><strong>{str(user.get('created_at', 'N/A'))[:19]}</strong></div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("profile_update_form"):
            new_name = st.text_input("Full Name", value=user["full_name"])
            new_linkedin = st.text_input("LinkedIn Profile URL", value=user.get("linkedin", ""), placeholder="https://linkedin.com/in/username")
            new_github = st.text_input("GitHub Profile URL", value=user.get("github", ""), placeholder="https://github.com/username")

            st.caption("ℹ️ Password changes require email verification and must be requested separately.")
            submit = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

            if submit:
                if not new_name.strip():
                    st.error("Full Name cannot be empty.")
                else:
                    update_user_profile(
                        user_id=user["id"],
                        full_name=new_name.strip(),
                        linkedin=new_linkedin.strip(),
                        github=new_github.strip()
                    )
                    # Update session state user
                    st.session_state["user"]["full_name"] = new_name.strip()
                    st.session_state["user"]["linkedin"] = new_linkedin.strip()
                    st.session_state["user"]["github"] = new_github.strip()
                    st.success("Profile updated successfully!")
                    st.rerun()

    with col2:
        st.markdown("### 🌟 Profile Completeness Tips")
        st.markdown("""
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 1.25rem;">
                <h4 style="color: #1e40af; margin-top: 0;">Why add LinkedIn & GitHub?</h4>
                <ul style="color: #1e3a8a; font-size: 0.9rem; line-height: 1.6; padding-left: 1.25rem;">
                    <li><strong>GitHub (1.5 pts in ATS):</strong> Freshers with active repositories, well-written READMEs, and clean code examples get significantly higher interview callbacks.</li>
                    <li><strong>LinkedIn (1.5 pts in ATS):</strong> Helps recruiters verify your college degree, certificates, and endorsements with 1 click.</li>
                    <li><strong>Consistent Branding:</strong> Keep your name and email consistent across your resume, GitHub, and LinkedIn accounts.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Return to Dashboard", use_container_width=True, key="profile_btn_return_dash"):
            st.session_state["page"] = "dashboard"
            st.session_state["current_page"] = "dashboard"
            st.rerun()
