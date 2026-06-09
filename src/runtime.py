import streamlit as st

from src.data_pipeline import ensure_seed_data
from src.modeling import train_model


@st.cache_data(show_spinner="Loading seed data")
def get_seed_data():
    return ensure_seed_data()


@st.cache_resource(show_spinner="Training fraud model")
def get_model_bundle():
    seed_data = ensure_seed_data()
    return train_model(seed_data["applications"])


def bootstrap_state():
    if "seed_data" not in st.session_state:
        st.session_state.seed_data = get_seed_data()
    if "model_bundle" not in st.session_state:
        st.session_state.model_bundle = get_model_bundle()
    if "portfolio_history" not in st.session_state:
        st.session_state.portfolio_history = []
    if "review_history" not in st.session_state:
        st.session_state.review_history = []
    if "last_application" not in st.session_state:
        st.session_state.last_application = None
    if "last_prediction" not in st.session_state:
        st.session_state.last_prediction = None
    if "last_explanation" not in st.session_state:
        st.session_state.last_explanation = None
    if "last_review" not in st.session_state:
        st.session_state.last_review = None
    if "last_email_link" not in st.session_state:
        st.session_state.last_email_link = None
    if "show_review_dialog" not in st.session_state:
        st.session_state.show_review_dialog = False
    if "use_llm_explanations" not in st.session_state:
        st.session_state.use_llm_explanations = False
    if "explanation_model" not in st.session_state:
        st.session_state.explanation_model = "gpt-4.1-mini"
