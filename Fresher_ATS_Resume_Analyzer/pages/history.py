"""
Analysis History Page for Fresher ATS Resume Analyzer.
Allows the logged-in user to review their past resume benchmarks, search records,
and view historical ATS Compatibility scores.
"""

import streamlit as st
import pandas as pd
from database.database import get_user_history
from auth.authentication import get_current_user


def render_history_page():
    """Render user-specific analysis history table with search and filters."""
    user = get_current_user()
    if not user:
        st.warning("Please sign in to view your history.")
        st.session_state["page"] = "login"
        st.session_state["current_page"] = "login"
        st.rerun()
        return

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem;">
                Analysis History
            </h1>
            <p style="color: #64748b; font-size: 1rem; margin: 0;">
                All past resume benchmarks performed by your account. Only your personal records are visible.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Fetch user history strictly by user["id"]
    history_records = get_user_history(user["id"])

    if not history_records:
        st.info("You haven't run any resume analyses yet.")
        if st.button("🚀 Analyze Your First Resume Now", type="primary", key="history_btn_analyze_first"):
            st.session_state["page"] = "resume_checker"
            st.session_state["current_page"] = "resume_checker"
            st.rerun()
        return

    # Search / Filter Bar
    s_col1, s_col2 = st.columns([2, 1])
    with s_col1:
        search_query = st.text_input("🔍 Search by Resume Name or Target Role", placeholder="e.g. Python, Alex_Resume, etc.")
    with s_col2:
        sort_order = st.selectbox("Sort by", ["Newest First", "Highest ATS Score", "Highest Job Match"])

    filtered = history_records
    if search_query:
        q = search_query.lower()
        filtered = [
            r for r in filtered
            if q in r["resume_name"].lower() or q in r["job_title"].lower()
        ]

    # Sort
    if sort_order == "Highest ATS Score":
        filtered.sort(key=lambda x: x["ats_score"], reverse=True)
    elif sort_order == "Highest Job Match":
        filtered.sort(key=lambda x: x["job_match_score"], reverse=True)
    else:
        filtered.sort(key=lambda x: x["id"], reverse=True)

    st.markdown(f"Showing **{len(filtered)}** record{'s' if len(filtered)!=1 else ''}:")

    # Format table for display
    display_rows = []
    for r in filtered:
        display_rows.append({
            "ID": r["id"],
            "Resume Name": r["resume_name"],
            "Target Job Title": r["job_title"],
            "ATS Compatibility Score": f"{r['ats_score']} / 100",
            "Job Match Similarity": f"{r['job_match_score']}%",
            "Analysis Date": str(r["analysis_date"])[:19]
        })

    df = pd.DataFrame(display_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b_col1, b_col2 = st.columns([1, 3])
    with b_col1:
        if st.button("← Back to Dashboard", use_container_width=True, key="history_btn_back_dash"):
            st.session_state["page"] = "dashboard"
            st.session_state["current_page"] = "dashboard"
            st.rerun()
    with b_col2:
        # CSV Export of History
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export History as CSV",
            data=csv_bytes,
            file_name=f"ATS_History_{user['full_name'].replace(' ', '_')}.csv",
            mime="text/csv"
        )
