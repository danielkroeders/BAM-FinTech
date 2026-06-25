import os

import streamlit as st

from src.core.data_pipeline import BASE_NUMERIC_COLUMNS, ensure_seed_data
from src.utils.demo_persistence import restore_demo_state
from src.utils.llm_profiles import load_local_llm_profile
from src.core.modeling import train_model

MODEL_CACHE_VERSION = "rf-only-v1"


@st.cache_data(show_spinner="Loading portfolio")
def get_seed_data():
    return ensure_seed_data()


@st.cache_resource(show_spinner="Training application risk model")
def get_model_bundle(cache_version=MODEL_CACHE_VERSION):
    seed_data = ensure_seed_data()
    return train_model(seed_data["applications"])


def _seed_data_has_current_schema(seed_data):
    applications = (
        seed_data.get("applications") if isinstance(seed_data, dict) else None
    )
    if applications is None:
        return False
    return all(column in applications.columns for column in BASE_NUMERIC_COLUMNS)


def _seed_data_has_named_companies(seed_data):
    applications = (
        seed_data.get("applications") if isinstance(seed_data, dict) else None
    )
    if applications is None or "company_name" not in applications:
        return False
    return (
        not applications["company_name"].astype(str).str.match(r"^Company\s+\d+$").any()
    )


def _model_bundle_has_current_metrics(model_bundle):
    models = getattr(model_bundle, "models", None)
    if not isinstance(models, dict) or set(models) != {"random_forest"}:
        return False
    required_metrics = {
        "precision_at_5pct",
        "precision_at_10pct",
        "precision_at_20pct",
        "estimated_total_error_cost",
    }
    return all(key in models["random_forest"].metrics for key in required_metrics)


def bootstrap_state():
    restore_demo_state()
    if (
        "seed_data" not in st.session_state
        or not _seed_data_has_current_schema(st.session_state.seed_data)
        or not _seed_data_has_named_companies(st.session_state.seed_data)
    ):
        st.session_state.seed_data = get_seed_data()
    if "model_bundle" not in st.session_state or not _model_bundle_has_current_metrics(
        st.session_state.model_bundle
    ):
        # Reuse the RF-only bundle across reruns and pages; model selection is no longer exposed.
        st.session_state.model_bundle = get_model_bundle(MODEL_CACHE_VERSION)
    if "portfolio_history" not in st.session_state:
        st.session_state.portfolio_history = []
    if "score_history" not in st.session_state:
        st.session_state.score_history = []
    if "review_history" not in st.session_state:
        st.session_state.review_history = []
    if "last_application" not in st.session_state:
        st.session_state.last_application = None
    if "last_prediction" not in st.session_state:
        st.session_state.last_prediction = None
    if "last_explanation" not in st.session_state:
        st.session_state.last_explanation = None
    if "last_explanation_source" not in st.session_state:
        st.session_state.last_explanation_source = "Deterministic"
    if "last_explanation_error" not in st.session_state:
        st.session_state.last_explanation_error = None
    if "last_review" not in st.session_state:
        st.session_state.last_review = None
    if "last_email_link" not in st.session_state:
        st.session_state.last_email_link = None
    if "show_review_dialog" not in st.session_state:
        st.session_state.show_review_dialog = False
    if "use_llm_explanations" not in st.session_state:
        st.session_state.use_llm_explanations = False
    if "llm_chat_provider" not in st.session_state:
        st.session_state.llm_chat_provider = "Deterministic"
    if "llm_chat_explanation" not in st.session_state:
        st.session_state.llm_chat_explanation = None
    if "llm_chat_source" not in st.session_state:
        st.session_state.llm_chat_source = None
    if "llm_chat_error" not in st.session_state:
        st.session_state.llm_chat_error = None
    if "llm_chat_signature" not in st.session_state:
        st.session_state.llm_chat_signature = None
    if "llm_review_history" not in st.session_state:
        st.session_state.llm_review_history = []
    if "llm_evaluation_packages" not in st.session_state:
        st.session_state.llm_evaluation_packages = {}
    if "document_validation_results" not in st.session_state:
        st.session_state.document_validation_results = {}
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "OpenAI API"
    if "explanation_model" not in st.session_state:
        st.session_state.explanation_model = "gpt-4.1-mini"
    saved_local_profile = load_local_llm_profile()
    env_local_base_url = os.getenv("LOCAL_LLM_BASE_URL", "")
    env_local_model = os.getenv("LOCAL_LLM_MODEL", "")
    env_local_api_key = os.getenv("LOCAL_LLM_API_KEY", "")
    if "local_llm_base_url" not in st.session_state:
        st.session_state.local_llm_base_url = (
            env_local_base_url or saved_local_profile.get("ip", "")
        )
    if "local_llm_model" not in st.session_state:
        st.session_state.local_llm_model = env_local_model or saved_local_profile.get(
            "model_name", ""
        )
    if "local_llm_api_key" not in st.session_state:
        st.session_state.local_llm_api_key = env_local_api_key
    if "local_llm_base_url_draft" not in st.session_state:
        st.session_state.local_llm_base_url_draft = (
            st.session_state.local_llm_base_url or "http://localhost:1234/v1"
        )
    if "local_llm_model_draft" not in st.session_state:
        st.session_state.local_llm_model_draft = st.session_state.local_llm_model
    if "local_llm_api_key_draft" not in st.session_state:
        st.session_state.local_llm_api_key_draft = st.session_state.local_llm_api_key
    if "local_llm_settings_saved" not in st.session_state:
        st.session_state.local_llm_settings_saved = bool(
            st.session_state.local_llm_base_url and st.session_state.local_llm_model
        )
    if "last_local_llm_base_url" not in st.session_state:
        st.session_state.last_local_llm_base_url = (
            st.session_state.local_llm_base_url
            or st.session_state.local_llm_base_url_draft
        )
    if "bulk_final_decisions" not in st.session_state:
        st.session_state.bulk_final_decisions = {}
    if "bulk_action_history" not in st.session_state:
        st.session_state.bulk_action_history = []
    if "support_ticket_history" not in st.session_state:
        st.session_state.support_ticket_history = []
    if "active_queue_application" not in st.session_state:
        st.session_state.active_queue_application = None
    if "active_intake_source" not in st.session_state:
        st.session_state.active_intake_source = "Manual entry"
    if "sme_company_application" not in st.session_state:
        st.session_state.sme_company_application = None
    if "sme_connection_status" not in st.session_state:
        st.session_state.sme_connection_status = {}
    if "sme_submission_history" not in st.session_state:
        st.session_state.sme_submission_history = []
    if "application_lifecycle" not in st.session_state:
        st.session_state.application_lifecycle = {}
    if "rating_publication_history" not in st.session_state:
        st.session_state.rating_publication_history = []
