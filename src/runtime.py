import streamlit as st

from src.data_pipeline import BASE_NUMERIC_COLUMNS, ensure_seed_data
from src.modeling import train_model


@st.cache_data(show_spinner="Loading seed data")
def get_seed_data():
    return ensure_seed_data()


@st.cache_resource(show_spinner="Training application risk model")
def get_model_bundle():
    seed_data = ensure_seed_data()
    return train_model(seed_data["applications"])


def _seed_data_has_current_schema(seed_data):
    applications = seed_data.get("applications") if isinstance(seed_data, dict) else None
    if applications is None:
        return False
    return all(column in applications.columns for column in BASE_NUMERIC_COLUMNS)


def _seed_data_has_named_companies(seed_data):
    applications = seed_data.get("applications") if isinstance(seed_data, dict) else None
    if applications is None or "company_name" not in applications:
        return False
    return not applications["company_name"].astype(str).str.match(r"^Company\s+\d+$").any()


def _model_bundle_has_current_metrics(model_bundle):
    required_metrics = {
        "precision_at_5pct",
        "precision_at_10pct",
        "precision_at_20pct",
        "estimated_total_error_cost",
    }
    metrics = getattr(model_bundle, "metrics", {})
    return all(key in metrics for key in required_metrics)


def bootstrap_state():
    if (
        "seed_data" not in st.session_state
        or not _seed_data_has_current_schema(st.session_state.seed_data)
        or not _seed_data_has_named_companies(st.session_state.seed_data)
    ):
        st.session_state.seed_data = ensure_seed_data()
    if "model_bundle" not in st.session_state or not _model_bundle_has_current_metrics(st.session_state.model_bundle):
        st.session_state.model_bundle = train_model(st.session_state.seed_data["applications"])
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
    if "investor_demo_mode" not in st.session_state:
        st.session_state.investor_demo_mode = False
    if "active_queue_application" not in st.session_state:
        st.session_state.active_queue_application = None
    if "active_intake_source" not in st.session_state:
        st.session_state.active_intake_source = "Manual entry"
