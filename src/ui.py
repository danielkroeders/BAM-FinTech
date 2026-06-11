import streamlit as st


PROFILE = {
    "bank": "Bank XYZ",
    "id": "01",
    "display_name": "Ms. Cooper",
    "role": "Credit Analyst",
}


def render_sidebar():
    st.markdown(
        """
        <style>
        .profile-sidebar-card {
            position: fixed;
            left: 0.75rem;
            bottom: 0.75rem;
            width: 14.5rem;
            max-width: calc(100vw - 1.5rem);
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 8px;
            padding: 0.7rem 0.8rem;
            background: rgba(15, 23, 42, 0.92);
            color: #f8fafc;
            z-index: 999;
            box-shadow: 0 12px 28px rgba(2, 6, 23, 0.18);
        }
        .profile-sidebar-card .profile-label {
            color: rgba(226, 232, 240, 0.72);
            font-size: 0.72rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
        }
        .profile-sidebar-card .profile-name {
            font-size: 1rem;
            font-weight: 750;
            line-height: 1.1;
            margin-bottom: 0.15rem;
        }
        .profile-sidebar-card .profile-meta {
            color: rgba(226, 232, 240, 0.82);
            font-size: 0.78rem;
            line-height: 1.35;
        }
        @media (max-width: 640px) {
            .profile-sidebar-card {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.header("Workspace")
        with st.expander("Advanced settings", expanded=False):
            st.toggle("Use LLM explanations", key="use_llm_explanations")
            st.selectbox("Explanation model", ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"], key="explanation_model")
        st.markdown(
            f"""
            <div class="profile-sidebar-card">
                <div class="profile-label">Signed in</div>
                <div class="profile-name">{PROFILE["display_name"]}</div>
                <div class="profile-meta">Bank: {PROFILE["bank"]}</div>
                <div class="profile-meta">ID: {PROFILE["id"]} | {PROFILE["role"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
