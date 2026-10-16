"""
Landing Page for Fresher ATS Resume Analyzer.
Introduces the application purpose, features, target freshers audience, and navigation to Register/Login.
"""

import streamlit as st


def render_landing_page():
    """Render professional hero banner, value propositions, feature cards, and CTA buttons."""
    # Top Header Hero Banner
    st.markdown("""
        <div class="app-header">
            <span class="fresher-badge">🎓 Built Exclusively for Freshers & Entry-Level Job Seekers</span>
            <h1>Fresher ATS Resume Analyzer</h1>
            <p class="tagline">"Check your resume. Match it with the job. Improve your ATS compatibility."</p>
            <p style="max-width: 700px; margin: 0 auto; color: #94a3b8; font-size: 0.95rem; line-height: 1.6;">
                Analyze your resume against any target job description. Uncover missing technical keywords,
                verify fresher-critical sections (Education, Projects, Training), and get an objective 100-point compatibility score.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Action Callouts (Sign In / Create Account)
    cta_col1, cta_col2, cta_col3, cta_col4 = st.columns([1, 1.2, 1.2, 1])
    with cta_col2:
        if st.button("🚀 Create Free Account", use_container_width=True, type="primary", key="landing_btn_create_acc"):
            st.session_state["page"] = "register"
            st.session_state["current_page"] = "register"
            st.rerun()
    with cta_col3:
        if st.button("🔑 Sign In to Portal", use_container_width=True, key="landing_btn_signin"):
            st.session_state["page"] = "login"
            st.session_state["current_page"] = "login"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Target Audience Notice
    st.info(
        "🎯 **Designed specifically for:** B.Tech / BE, BCA, B.Sc Computer Science & IT graduates, "
        "Python Developer freshers, Data Analyst freshers, AI/ML graduates, and Junior Software Engineers. "
        "Evaluates your academic projects and college training without penalizing for lack of years of full-time work experience."
    )

    st.markdown("### 🌟 What This Analyzer Checks")

    # Features Grid
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        st.markdown("""
            <div class="feature-card">
                <span class="feature-card-icon">📊</span>
                <h3>Exact 100-pt ATS Scoring</h3>
                <p>Transparent rule-based formula: Keywords (30), Skills (20), Sections (15), Formatting (15), Job Relevance (10), Contact Info (10).</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="feature-card" style="margin-top: 1rem;">
                <span class="feature-card-icon">🔍</span>
                <h3>Keyword & Tech Matching</h3>
                <p>Scans target Job Descriptions to identify critical libraries, languages, databases, and frameworks found or missing in your CV.</p>
            </div>
        """, unsafe_allow_html=True)

    with f_col2:
        st.markdown("""
            <div class="feature-card">
                <span class="feature-card-icon">🎓</span>
                <h3>Fresher Resume Checklist</h3>
                <p>Audits presence of Education, Academic Projects, Technical Skills, Training, Certifications, and code links (GitHub & LinkedIn).</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="feature-card" style="margin-top: 1rem;">
                <span class="feature-card-icon">📑</span>
                <h3>Formatting & Layout Check</h3>
                <p>Ensures standard section headers, single-column readability, table parsing safety, and text extractability with PyMuPDF.</p>
            </div>
        """, unsafe_allow_html=True)

    with f_col3:
        st.markdown("""
            <div class="feature-card">
                <span class="feature-card-icon">💡</span>
                <h3>Actionable Suggestions</h3>
                <p>Grounded advice generated strictly from detected gaps. Never encourages inventing false skills or misleading experience.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="feature-card" style="margin-top: 1rem;">
                <span class="feature-card-icon">📥</span>
                <h3>Instant PDF ATS Report</h3>
                <p>Download a single-column, recruiter-friendly A4 PDF summary detailing your scores, matched keywords, and roadmap.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # Bottom Registration Bar
    bot_col1, bot_col2 = st.columns([3, 1])
    with bot_col1:
        st.markdown("""
            **Ready to benchmark your fresher resume against real job requirements?**  
            Join hundreds of graduates improving their interview call rates.
        """)
    with bot_col2:
        if st.button("Get Started Now →", use_container_width=True, type="primary", key="landing_btn_get_started"):
            st.session_state["page"] = "register"
            st.session_state["current_page"] = "register"
            st.rerun()
