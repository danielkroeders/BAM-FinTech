import re

import streamlit as st

from src.utils.demo_persistence import persist_demo_state
from src.features.explanations import deterministic_explanation, explain_prediction
from src.utils.formatting import format_percent, format_score
from src.core.runtime import bootstrap_state
from src.features.shap_explanations import shap_driver_table
from src.ui.components import render_sidebar, safe_page_link


st.set_page_config(page_title="LLM Integration", layout="wide")
bootstrap_state()
render_sidebar()

st.title("LLM Integration")
st.caption("Connect deterministic, hosted, or local-model second-review explanations to the latest scored loan request.")

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


def _grade_comparison(ai_grade, model_grade, model_label):
    if not ai_grade or not model_grade:
        return None
    grade_rank = {grade: index for index, grade in enumerate("ABCDEF")}
    ai_rank = grade_rank.get(ai_grade)
    model_rank = grade_rank.get(model_grade)
    if ai_rank is None or model_rank is None:
        return None
    if ai_rank > model_rank:
        return f"More severe than {model_label} grade {model_grade}"
    if ai_rank < model_rank:
        return f"Less severe than {model_label} grade {model_grade}"
    return f"Aligned with {model_label} grade {model_grade}"


def _record_llm_run(signature, application, prediction, provider, source, error, explanation):
    ai_review_score = _extract_ai_review_score(explanation)
    ai_text_grade = _extract_ai_grade(explanation)
    ai_grade = _grade_from_review_score(ai_review_score) or ai_text_grade
    st.session_state.llm_review_history.append(
        {
            "Run ID": f"LLM-{len(st.session_state.llm_review_history) + 1:03d}",
            "Timestamp": st.session_state.llm_chat_last_run,
            "Application ID": application.get("application_id", "Session"),
            "Provider": provider,
            "Source": source,
            "Status": "Fallback" if error else "Completed",
            "Model": prediction.get("model_label", "ML model"),
            "Model grade": prediction.get("grade"),
            "AI review score": f"{ai_review_score}/100" if ai_review_score is not None else "N/A",
            "AI grade": ai_grade or "N/A",
        }
    )


if not application or not prediction:
    st.info("No application has been scored yet. Use Personal Workspace to create the first decision.")
    safe_page_link("pages/1_Personal_Workspace.py", "Open Personal Workspace", ":material/person_search:")
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

    model_key = prediction.get("model_key", st.session_state.get("selected_ml_model", "random_forest"))
    model_label = prediction.get("model_label", st.session_state.model_bundle.label_for(model_key))
    metrics = st.session_state.model_bundle.metrics_for(model_key)
    st.subheader(f"{model_label} Model Baseline")
    rf_cols = st.columns(4)
    rf_cols[0].metric("Application risk score", format_percent(prediction["fraud_probability"]))
    rf_cols[1].metric("Model grade", prediction["grade"])
    rf_cols[2].metric("Model recommendation", prediction["decision"])
    rf_cols[3].metric("Model ROC-AUC", format_score(metrics.get("roc_auc", 0), 3))
    metric_cols = st.columns(4)
    metric_cols[0].metric("Model recall", format_score(metrics.get("recall", 0), 3))
    metric_cols[1].metric("Model precision", format_score(metrics.get("precision", 0), 3))
    metric_cols[2].metric("Balanced accuracy", format_score(metrics.get("balanced_accuracy", 0), 3))
    metric_cols[3].metric("Precision top 10%", format_score(metrics.get("precision_at_10pct", 0), 3))

    default_explanation = deterministic_explanation(application, prediction)

    st.subheader("Run LLM Review")
    st.caption(
        f"The {model_label} model provides the baseline score. A hosted or local LLM can then act as a second reviewer, "
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

        run_explanation = st.form_submit_button("Run LLM Review", width="stretch")

    if run_explanation:
        from datetime import datetime

        st.session_state.llm_chat_provider = provider
        st.session_state.llm_chat_last_run = datetime.now().strftime("%Y-%m-%d %H:%M")
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
        _record_llm_run(
            signature,
            application,
            prediction,
            provider,
            st.session_state.llm_chat_source,
            st.session_state.llm_chat_error,
            st.session_state.llm_chat_explanation,
        )
        persist_demo_state()

    explanation = st.session_state.get("llm_chat_explanation") or default_explanation
    source = st.session_state.get("llm_chat_source") or "Deterministic"
    error = st.session_state.get("llm_chat_error")

    status_cols = st.columns(4)
    status_cols[0].metric("Selected provider", st.session_state.get("llm_chat_provider", "Deterministic"))
    status_cols[1].metric("Last source", source)
    status_cols[2].metric("Last run", st.session_state.get("llm_chat_last_run", "Not run yet"))
    status_cols[3].metric("Status", "Fallback" if error else "Ready")

    st.subheader("LLM Review Output")
    st.caption(f"Explanation source: {source}")
    if source == "Local server":
        st.caption(f"Local endpoint used: {st.session_state.last_local_llm_base_url}")
    if error:
        st.warning(error)
    ai_review_score = _extract_ai_review_score(explanation)
    ai_text_grade = _extract_ai_grade(explanation)
    ai_implied_grade = _grade_from_review_score(ai_review_score)
    ai_grade = ai_implied_grade or ai_text_grade
    comparison = _grade_comparison(ai_grade, prediction["grade"], model_label)
    if ai_review_score is not None:
        ai_cols = st.columns(3)
        ai_cols[0].metric("AI review score", f"{ai_review_score}/100")
        ai_cols[1].metric("AI implied grade", ai_grade or "N/A")
        ai_cols[2].metric("AI vs model grade", comparison or "N/A")
        if ai_text_grade and ai_implied_grade and ai_text_grade != ai_implied_grade:
            st.warning(
                f"The LLM wrote grade {ai_text_grade}, but {ai_review_score}/100 maps to grade {ai_implied_grade} "
                "under the configured thresholds. Treat the implied grade as the normalized comparison."
            )
        st.caption("AI grade uses the same A-F thresholds as the selected ML score. This is a qualitative second-review score, not a calibrated probability.")
    st.info(explanation)

    current_history = [
        row
        for row in st.session_state.llm_review_history
        if row.get("Application ID") == application.get("application_id", "Session")
    ]
    if current_history:
        st.subheader("Saved LLM Review Runs")
        st.dataframe(current_history[-8:], width="stretch", hide_index=True)

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
            "Tree SHAP is shown for the Random Forest baseline. Positive contributions push the application risk score higher; negative contributions push it lower. "
            "Categorical one-hot features are grouped back to their original fields for readability."
        )
    except ImportError:
        st.warning("Install the `shap` dependency from requirements.txt to view SHAP driver analysis.")

persist_demo_state()
