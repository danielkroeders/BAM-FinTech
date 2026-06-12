import re

import streamlit as st

from src.explanations import deterministic_explanation, explain_prediction
from src.formatting import format_percent, format_score
from src.runtime import bootstrap_state
from src.shap_explanations import shap_driver_table
from src.ui import render_sidebar


st.set_page_config(page_title="AI Explainability", layout="wide")
bootstrap_state()
render_sidebar()

st.title("AI Explainability")
st.caption("Run deterministic, hosted, or local-model explanations for the latest scored loan request.")

application = st.session_state.last_application
prediction = st.session_state.last_prediction

PROVIDERS = ["Deterministic", "OpenAI API", "Local server"]


def _provider_index():
    saved = st.session_state.get("llm_chat_provider", "Deterministic")
    return PROVIDERS.index(saved) if saved in PROVIDERS else 0


def _extract_ai_review_score(text):
    match = re.search(r"AI review score\s*:\s*(\d{1,3})\s*/\s*100", text or "", re.IGNORECASE)
    if not match:
        return None
    score = int(match.group(1))
    return max(0, min(score, 100))


def _extract_ai_grade(text):
    match = re.search(r"AI suggested grade\s*:\s*([A-F])", text or "", re.IGNORECASE)
    return match.group(1).upper() if match else None


def _grade_from_review_score(score):
    if score is None:
        return None
    probability = score / 100
    if probability < 0.15:
        return "A"
    if probability < 0.28:
        return "B"
    if probability < 0.42:
        return "C"
    if probability < 0.58:
        return "D"
    if probability < 0.74:
        return "E"
    return "F"


def _grade_comparison(ai_grade, rf_grade):
    if not ai_grade or not rf_grade:
        return None
    grade_rank = {grade: index for index, grade in enumerate("ABCDEF")}
    ai_rank = grade_rank.get(ai_grade)
    rf_rank = grade_rank.get(rf_grade)
    if ai_rank is None or rf_rank is None:
        return None
    if ai_rank > rf_rank:
        return f"More severe than RF grade {rf_grade}"
    if ai_rank < rf_rank:
        return f"Less severe than RF grade {rf_grade}"
    return f"Aligned with RF grade {rf_grade}"


if not application or not prediction:
    st.info("No application has been scored yet. Use Personal Workspace to create the first decision.")
else:
    signature = (
        f"{application.get('application_id', '')}:"
        f"{prediction.get('fraud_probability', 0):.6f}:"
        f"{prediction.get('grade', '')}:"
        f"{prediction.get('decision', '')}"
    )
    if st.session_state.llm_chat_signature != signature:
        st.session_state.llm_chat_explanation = None
        st.session_state.llm_chat_source = None
        st.session_state.llm_chat_error = None
        st.session_state.llm_chat_signature = signature

    st.subheader("RF Model Baseline")
    metrics = st.session_state.model_bundle.metrics
    rf_cols = st.columns(4)
    rf_cols[0].metric("RF application risk score", format_percent(prediction["fraud_probability"]))
    rf_cols[1].metric("RF grade", prediction["grade"])
    rf_cols[2].metric("RF recommendation", prediction["decision"])
    rf_cols[3].metric("RF ROC-AUC", format_score(metrics.get("roc_auc", 0), 3))
    metric_cols = st.columns(4)
    metric_cols[0].metric("RF recall", format_score(metrics.get("recall", 0), 3))
    metric_cols[1].metric("RF precision", format_score(metrics.get("precision", 0), 3))
    metric_cols[2].metric("Balanced accuracy", format_score(metrics.get("balanced_accuracy", 0), 3))
    metric_cols[3].metric("Precision top 10%", format_score(metrics.get("precision_at_10pct", 0), 3))

    default_explanation = deterministic_explanation(application, prediction)

    st.subheader("Run Explanation")
    st.caption(
        "The RF model provides the baseline score. A hosted or local LLM can then act as a second reviewer, "
        "produce an AI review score, map it back to the A-F grade policy, and suggest follow-up actions."
    )
    with st.form("llm_explanation_form"):
        provider = st.radio("Explanation source", PROVIDERS, index=_provider_index(), horizontal=True)
        detail_level = st.radio(
            "Detail level",
            ["Detailed analyst memo", "Concise summary"],
            index=0,
            horizontal=True,
        )

        openai_model = st.session_state.explanation_model
        local_base_url = st.session_state.local_llm_base_url or "http://localhost:1234/v1"
        local_model = st.session_state.local_llm_model
        local_api_key = st.session_state.local_llm_api_key

        if provider == "OpenAI API":
            openai_model = st.selectbox(
                "OpenAI model",
                ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"],
                index=["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"].index(st.session_state.explanation_model)
                if st.session_state.explanation_model in ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"]
                else 0,
            )
        elif provider == "Local server":
            local_base_url = st.text_input("Local server URL", value=local_base_url)
            local_model = st.text_input("Local model", value=local_model)
            local_api_key = st.text_input("Local API key", value=local_api_key, type="password")
            st.caption("Enter the server root or `/v1` base URL. The app calls `/v1/chat/completions` when you click Run.")

        run_explanation = st.form_submit_button("Run Explanation", width="stretch")

    if run_explanation:
        st.session_state.llm_chat_provider = provider
        if provider == "Deterministic":
            st.session_state.llm_chat_explanation = default_explanation
            st.session_state.llm_chat_source = "Deterministic"
            st.session_state.llm_chat_error = None
            st.session_state.llm_chat_signature = signature
        elif provider == "OpenAI API":
            st.session_state.explanation_model = openai_model
            explanation = explain_prediction(
                application,
                prediction,
                use_llm=True,
                model=openai_model,
                provider="OpenAI API",
                detail_level=detail_level,
                model_metrics=metrics,
            )
            st.session_state.llm_chat_explanation = explanation
            st.session_state.llm_chat_source = st.session_state.last_explanation_source
            st.session_state.llm_chat_error = st.session_state.last_explanation_error
            st.session_state.llm_chat_signature = signature
        else:
            st.session_state.local_llm_base_url = local_base_url.strip()
            st.session_state.local_llm_model = local_model.strip()
            st.session_state.local_llm_api_key = local_api_key.strip()
            st.session_state.local_llm_settings_saved = bool(
                st.session_state.local_llm_base_url and st.session_state.local_llm_model
            )
            explanation = explain_prediction(
                application,
                prediction,
                use_llm=True,
                model=st.session_state.local_llm_model,
                provider="Local server",
                local_base_url=st.session_state.local_llm_base_url,
                local_api_key=st.session_state.local_llm_api_key,
                detail_level=detail_level,
                model_metrics=metrics,
            )
            st.session_state.llm_chat_explanation = explanation
            st.session_state.llm_chat_source = st.session_state.last_explanation_source
            st.session_state.llm_chat_error = st.session_state.last_explanation_error
            st.session_state.llm_chat_signature = signature

    explanation = st.session_state.get("llm_chat_explanation") or default_explanation
    source = st.session_state.get("llm_chat_source") or "Deterministic"
    error = st.session_state.get("llm_chat_error")

    st.subheader("Explanation Output")
    st.caption(f"Explanation source: {source}")
    if source == "Local server":
        st.caption(f"Local endpoint used: {st.session_state.last_local_llm_base_url}")
    if error:
        st.warning(error)
    ai_review_score = _extract_ai_review_score(explanation)
    ai_text_grade = _extract_ai_grade(explanation)
    ai_implied_grade = _grade_from_review_score(ai_review_score)
    ai_grade = ai_implied_grade or ai_text_grade
    comparison = _grade_comparison(ai_grade, prediction["grade"])
    if ai_review_score is not None:
        ai_cols = st.columns(3)
        ai_cols[0].metric("AI review score", f"{ai_review_score}/100")
        ai_cols[1].metric("AI implied grade", ai_grade or "N/A")
        ai_cols[2].metric("AI vs RF grade", comparison or "N/A")
        if ai_text_grade and ai_implied_grade and ai_text_grade != ai_implied_grade:
            st.warning(
                f"The LLM wrote grade {ai_text_grade}, but {ai_review_score}/100 maps to grade {ai_implied_grade} "
                "under the configured thresholds. Treat the implied grade as the normalized comparison."
            )
        st.caption("AI grade uses the same A-F thresholds as the RF score. This is a qualitative second-review score, not a calibrated probability.")
    st.info(explanation)

    st.subheader("SHAP Driver Analysis")
    try:
        shap_table, baseline_probability, predicted_probability = shap_driver_table(st.session_state.model_bundle, application)
        top_drivers = shap_table.head(8).copy()

        summary_cols = st.columns(3)
        summary_cols[0].metric("Baseline Risk", format_percent(baseline_probability))
        summary_cols[1].metric("Application Risk", format_percent(predicted_probability))
        summary_cols[2].metric("Largest Driver", top_drivers.iloc[0]["driver"].replace("_", " ").title())

        chart_data = top_drivers.set_index("driver")["contribution"].sort_values()
        st.bar_chart(chart_data)

        display_table = top_drivers.rename(
            columns={
                "driver": "Driver",
                "application_value": "Application value",
                "contribution": "SHAP contribution",
                "impact": "Impact",
            }
        )[["Driver", "Application value", "SHAP contribution", "Impact"]]
        display_table["SHAP contribution"] = display_table["SHAP contribution"].apply(lambda value: format_score(value, 4))
        st.dataframe(display_table, width="stretch", hide_index=True)
        st.caption(
            "Positive SHAP contributions push the application risk score higher. Negative contributions push it lower. "
            "Categorical one-hot features are grouped back to their original fields for readability."
        )
    except ImportError:
        st.warning("Install the `shap` dependency from requirements.txt to view SHAP driver analysis.")
