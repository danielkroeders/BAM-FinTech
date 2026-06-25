# Local demo-session persistence for refresh-safe walkthrough state.
import json
import math
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

SESSION_QUERY_KEY = "demo_session"
SESSION_STATE_KEY = "demo_session_id"
SESSION_LOADED_KEY = "demo_session_loaded"
SESSION_DIR = Path(__file__).resolve().parents[2] / ".tmp" / "demo_sessions"

# Persistence is deliberately local and demo-scoped. It keeps the app smooth
# across Streamlit reruns/refreshes but is not a production database and does
# not write API tokens or model cache objects.
PERSISTED_KEYS = [
    # Only demo workflow state is persisted; model caches and secrets remain outside this file.
    "authenticated",
    "remember_me",
    "login_stage",
    "login_transition",
    "user_profile",
    "portfolio_history",
    "score_history",
    "review_history",
    "last_application",
    "last_prediction",
    "last_explanation",
    "last_explanation_source",
    "last_explanation_error",
    "last_review",
    "last_email_link",
    "show_review_dialog",
    "llm_chat_provider",
    "llm_chat_explanation",
    "llm_chat_source",
    "llm_chat_error",
    "llm_chat_signature",
    "llm_chat_last_run",
    "llm_review_history",
    "llm_evaluation_packages",
    "document_validation_results",
    "explanation_model",
    "bulk_final_decisions",
    "bulk_action_history",
    "support_ticket_history",
    "active_queue_application",
    "active_intake_source",
    "sme_company_application",
    "sme_connection_status",
    "sme_submission_history",
    "application_lifecycle",
    "rating_publication_history",
    "loan_example_scenario",
    "profile_settings_saved",
    "demo_prompt_remembered",
    "demo_prompt_choice",
]


def _query_session_id():
    # Query params let multiple browser tabs keep separate demo sessions without
    # a backend account system.
    try:
        value = st.query_params.get(SESSION_QUERY_KEY)
    except Exception:
        try:
            value = st.experimental_get_query_params().get(SESSION_QUERY_KEY)
        except Exception:
            return None
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _set_query_session_id(session_id):
    try:
        st.query_params[SESSION_QUERY_KEY] = session_id
        return
    except Exception:
        pass
    try:
        params = st.experimental_get_query_params()
        params[SESSION_QUERY_KEY] = session_id
        st.experimental_set_query_params(**params)
    except Exception:
        return


def _session_path(session_id):
    # Sanitize the query-provided session ID before using it as a filename.
    safe_id = "".join(
        character
        for character in str(session_id)
        if character.isalnum() or character in {"-", "_"}
    )
    return SESSION_DIR / f"{safe_id}.json"


def ensure_demo_session():
    session_id = st.session_state.get(SESSION_STATE_KEY) or _query_session_id()
    if not session_id:
        session_id = f"demo-{uuid4().hex[:12]}"
    st.session_state[SESSION_STATE_KEY] = session_id
    _set_query_session_id(session_id)
    return session_id


def restore_demo_state():
    # Restore once per Streamlit session. Re-reading on every rerun could
    # overwrite fresh widget changes before they are persisted.
    session_id = ensure_demo_session()
    if st.session_state.get(SESSION_LOADED_KEY):
        return

    path = _session_path(session_id)
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        saved_state = payload.get("state", {})
        for key in PERSISTED_KEYS:
            if key in saved_state:
                st.session_state[key] = saved_state[key]
        st.session_state.demo_state_restored_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
    st.session_state[SESSION_LOADED_KEY] = True


def _json_ready(value):
    # Streamlit state may contain numpy scalars, pandas values, sets, or NaN.
    # Convert everything into JSON-safe primitives before writing the session
    # file.
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(item) for item in value]
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return _json_ready(item())
        except (TypeError, ValueError):
            pass
    return str(value)


def persist_demo_state():
    # Persist only whitelisted keys. Large deterministic resources such as the
    # seed dataset/model bundle are rebuilt or cached by runtime.py, not stored
    # in the demo JSON file.
    session_id = ensure_demo_session()
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    state = {
        key: _json_ready(st.session_state.get(key))
        for key in PERSISTED_KEYS
        if key in st.session_state
    }
    payload = {
        "demo_session_id": session_id,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "state": state,
    }
    path = _session_path(session_id)
    temp_path = path.with_suffix(".tmp")
    # Atomic replace avoids corrupting the demo session if the app stops mid-write.
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)
    return path


def clear_demo_state():
    # Clear keeps the same demo_session_id so the browser URL remains valid, but
    # removes every other state key and all local uploaded evidence for a clean
    # new walkthrough.
    session_id = ensure_demo_session()
    from src.utils.document_storage import clear_session_documents

    # Clearing state also removes local SME uploads so the next demo starts clean.
    clear_session_documents(session_id)
    path = _session_path(session_id)
    if path.exists():
        path.unlink()
    for key in list(st.session_state.keys()):
        if key != SESSION_STATE_KEY:
            del st.session_state[key]
    st.session_state[SESSION_STATE_KEY] = session_id
    st.session_state[SESSION_LOADED_KEY] = True
    st.session_state.demo_state_cleared_at = datetime.now().strftime("%Y-%m-%d %H:%M")
