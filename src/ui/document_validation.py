# Streamlit components for reviewing uploaded evidence and validation results.
import streamlit as st

from src.features.document_validation import (
    DOCUMENT_VALIDATION_PROVIDERS,
    run_document_validation,
    validation_results_table,
)
from src.utils.demo_persistence import persist_demo_state
from src.utils.document_storage import list_documents

# This module renders validation controls while src/features/document_validation.py
# performs classification. Keeping UI and validation logic separate lets both
# SME preview and lender verification reuse the same engine with different scopes.

def _validation_store():
    if "document_validation_results" not in st.session_state:
        # Store validation by application and scope so SME preview checks do not overwrite lender checks.
        st.session_state.document_validation_results = {}
    return st.session_state.document_validation_results


def latest_document_validation_run(application_id, scope):
    # Scope prevents an SME preview validation from overwriting the lender's
    # formal verification run for the same application.
    return _validation_store().get(str(application_id), {}).get(scope)


def _store_document_validation_run(application_id, scope, run):
    store = _validation_store()
    application_key = str(application_id)
    application_runs = store.setdefault(application_key, {})
    application_runs[scope] = run
    st.session_state.document_validation_results = store
    # Persist immediately because validation can be used later in the lender review lifecycle.
    persist_demo_state()


def _provider_inputs(scope, application_id):
    # Provider choice is namespaced by scope/application so repeated panels do not share widgets.
    # This is especially important when a page renders both preview and formal
    # validation panels during the same Streamlit session.
    provider = st.selectbox(
        "Validation mode",
        DOCUMENT_VALIDATION_PROVIDERS,
        key=f"doc_validation_provider_{scope}_{application_id}",
        help=(
            "Deterministic checks stay local. OpenAI or local server adds AI-assisted classification using "
            "metadata and a bounded text preview."
        ),
    )
    model = ""
    local_base_url = None
    local_api_key = None

    if provider == "OpenAI API":
        st.warning(
            "Hosted AI validation sends document metadata and a limited extracted text preview to the configured provider. "
            "Use deterministic or local validation for sensitive real files.",
            icon=":material/privacy_tip:",
        )
        model = st.text_input(
            "OpenAI validation model",
            value=st.session_state.get("explanation_model", "gpt-4.1-mini"),
            key=f"doc_validation_openai_model_{scope}_{application_id}",
        )
    elif provider == "Local server":
        st.info(
            "Local validation uses an OpenAI-compatible local endpoint. The token is session-only and is not persisted.",
            icon=":material/dns:",
        )
        local_base_url = st.text_input(
            "Local server URL or IP",
            value=st.session_state.get(
                "local_llm_base_url", "http://localhost:1234/v1"
            ),
            key=f"doc_validation_local_url_{scope}_{application_id}",
        )
        model = st.text_input(
            "Local validation model",
            value=st.session_state.get("local_llm_model", ""),
            key=f"doc_validation_local_model_{scope}_{application_id}",
        )
        local_api_key = st.text_input(
            "Local API token",
            value=st.session_state.get("local_llm_api_key", ""),
            type="password",
            key=f"doc_validation_local_key_{scope}_{application_id}",
        )

    return provider, model, local_base_url, local_api_key


def _render_validation_run(run):
    # Render both the summary and row-level findings from a stored validation
    # run. This function is display-only; it never revalidates files.
    if not run:
        return
    summary = run.get("summary", {})
    st.caption(
        f"Latest run: {run.get('validated_at', 'Unknown time')} · "
        f"{run.get('provider_requested', 'Deterministic')} · {run.get('run_id', 'DOCVAL')}"
    )
    metric_cols = st.columns(4)
    metric_cols[0].metric("Overall", summary.get("status", "Unknown"))
    metric_cols[1].metric("Verified", summary.get("verified", 0))
    metric_cols[2].metric("Needs review", summary.get("needs_review", 0))
    metric_cols[3].metric("Mismatches", summary.get("mismatches", 0))

    results = run.get("results", [])
    if results:
        st.dataframe(
            validation_results_table(results), width="stretch", hide_index=True
        )
        with st.expander("Validation details", expanded=False):
            for result in results:
                st.markdown(
                    f"**{result.get('expected_label', 'Document')}: {result.get('file', 'unknown file')}**"
                )
                st.write(result.get("rationale", "No rationale returned."))
                if result.get("evidence"):
                    st.caption("Evidence markers: " + ", ".join(result["evidence"]))
                if result.get("red_flags"):
                    st.warning(
                        "Red flags: " + ", ".join(result["red_flags"]),
                        icon=":material/report:",
                    )
                st.caption(
                    f"Follow-up: {result.get('follow_up', 'Ask for clearer evidence.')}"
                )
                if result.get("ai_error"):
                    st.warning(result["ai_error"], icon=":material/warning:")


def render_document_validation_panel(
    session_id,
    application_id,
    scope,
    title,
    description,
    button_label,
):
    # Render a provider selector plus a run button for one application/scope. The
    # caller decides whether this is an applicant preview or lender verification.
    documents = list_documents(session_id, application_id)
    st.markdown(f"**{title}**")
    st.caption(description)
    if not documents:
        st.info("Save or upload application files before running document validation.")
        return latest_document_validation_run(application_id, scope), None

    provider, model, local_base_url, local_api_key = _provider_inputs(
        scope, application_id
    )
    if provider != "Deterministic":
        st.caption(
            "This is document-type classification and consistency screening. It does not prove that a document is genuine, "
            "unaltered, or legally valid."
        )

    run_clicked = st.button(
        button_label,
        key=f"run_document_validation_{scope}_{application_id}",
        width="stretch",
    )
    new_run = None
    if run_clicked:
        if provider == "Local server":
            # Local validation uses session credentials only; saving profiles is handled on LLM Integration.
            st.session_state.local_llm_base_url = (local_base_url or "").strip()
            st.session_state.local_llm_model = (model or "").strip()
            st.session_state.local_llm_api_key = (local_api_key or "").strip()
            st.session_state.local_llm_settings_saved = bool(
                st.session_state.local_llm_base_url and st.session_state.local_llm_model
            )
        new_run = run_document_validation(
            session_id,
            application_id,
            provider=provider,
            model=model,
            local_base_url=local_base_url,
            local_api_key=local_api_key,
        )
        _store_document_validation_run(application_id, scope, new_run)
        summary = new_run.get("summary", {})
        if summary.get("mismatches", 0):
            st.error("Document validation found at least one likely category mismatch.")
            if scope == "lender_verification":
                st.info(
                    "Suggested company-facing position: the application cannot proceed because submitted evidence "
                    "could not be verified against the requested document categories.",
                    icon=":material/quick_phrases:",
                )
        elif summary.get("needs_review", 0):
            st.warning(
                "Document validation completed with items that still need human review."
            )
        else:
            st.success(
                "Document validation completed. All checked files match their expected categories."
            )

    latest_run = new_run or latest_document_validation_run(application_id, scope)
    _render_validation_run(latest_run)
    return latest_run, new_run
