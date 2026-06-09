import os

import streamlit as st


def _has_api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return True
    except Exception:
        pass
    return bool(os.getenv("OPENAI_API_KEY"))


def render_sidebar():
    with st.sidebar:
        st.header("Controls")
        st.toggle("Use LLM explanations", key="use_llm_explanations")
        st.selectbox("Explanation model", ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"], key="explanation_model")
        if _has_api_key():
            st.success("OpenAI API key detected")
        else:
            st.info("No OpenAI API key detected")
