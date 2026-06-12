import os
import json

import pandas as pd
import streamlit as st

from src.data_pipeline import add_derived_features
from src.formatting import format_currency, format_percent


def _api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def _local_base_url():
    return os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1")


def _local_model():
    return os.getenv("LOCAL_LLM_MODEL", "local-model")


def _local_api_key():
    return os.getenv("LOCAL_LLM_API_KEY", "local")


def _normalize_local_base_url(base_url):
    normalized = (base_url or _local_base_url()).strip().rstrip("/")
    if normalized.endswith("/v1/chat/completions"):
        return normalized[: -len("/chat/completions")]
    if normalized.endswith("/chat/completions"):
        normalized = normalized[: -len("/chat/completions")]
    if not normalized.endswith("/v1"):
        normalized = f"{normalized}/v1"
    return normalized


def _set_explanation_error(message):
    st.session_state.last_explanation_error = message


def deterministic_explanation(application, prediction):
    probability = prediction["fraud_probability"]
    derived = add_derived_features(pd.DataFrame([application])).iloc[0]
    flags = prediction.get("flags", [])
    amount = float(application.get("requested_amount", 0))
    drivers = "\n".join(f"- {flag}" for flag in flags) if flags else "- No elevated deterministic risk flags were triggered."
    mitigants = []
    if float(application.get("collateral_ratio", 0)) >= 0.8:
        mitigants.append("Collateral coverage is relatively strong.")
    if float(application.get("years_in_business", 0)) >= 5:
        mitigants.append("Operating history is established.")
    if float(application.get("late_payment_ratio", 0)) < 0.1:
        mitigants.append("Late payment behavior is limited.")
    if float(application.get("free_cash_flow", 0)) > 0:
        mitigants.append("Free cash flow is positive.")
    if float(application.get("expected_runway_months", 0)) >= 12:
        mitigants.append("Expected runway is at least 12 months.")
    if float(application.get("forecast_plan_confidence_score", 0)) >= 0.7:
        mitigants.append("Five-year plan confidence is relatively strong.")
    if float(derived.get("debt_service_coverage_ratio", 0)) >= 1.25:
        mitigants.append("Free cash flow covers estimated annual debt service.")
    if float(derived.get("stressed_debt_service_coverage_ratio", 0)) >= 1.0:
        mitigants.append("Debt-service coverage remains above 1.0 under a +2% rate stress.")
    if float(derived.get("document_completeness_score", 0)) >= 0.95:
        mitigants.append("Expected application documents are complete.")
    if float(application.get("current_ratio", 0)) >= 1.5 and float(application.get("quick_ratio", 0)) >= 1.0:
        mitigants.append("Working-capital ratios are relatively healthy.")
    if float(derived.get("identity_verification_risk_score", 1)) < 0.20:
        mitigants.append("Digital identity and KYB verification signals are low risk.")
    mitigant_text = "\n".join(f"- {item}" for item in mitigants) if mitigants else "- No major mitigating factor was identified in the deterministic checks."
    next_step = {
        "Approve": "Proceed with standard analyst sign-off and retain the case summary.",
        "Manual Review": "Route to an analyst for document verification and risk-factor review.",
        "Reject": "Route to compliance review before any final adverse action is communicated.",
    }[prediction["decision"]]
    return (
        f"Decision: {prediction['decision']} | Grade {prediction['grade']} | Application risk score {format_percent(probability)}\n\n"
        f"Applicant context: {application.get('company_type', 'The applicant')} in "
        f"{application.get('industry', 'unknown industry')} requested {format_currency(amount)}.\n\n"
        f"Top risk drivers:\n{drivers}\n\n"
        f"Mitigating factors:\n{mitigant_text}\n\n"
        f"Recommended analyst action: {next_step}\n\n"
        "Compliance note: This is decision support for analyst review; high-risk cases require human compliance review "
        "and this output does not establish legal certainty."
    )


def _llm_messages(application, prediction, detail_level="Detailed analyst memo", model_metrics=None):
    metrics = model_metrics or {}
    model_context = {
        "model_type": "RandomForestClassifier risk model",
        "rf_application_risk_score": prediction.get("fraud_probability"),
        "rf_grade": prediction.get("grade"),
        "rf_recommendation": prediction.get("decision"),
        "validation_metrics": {
            "roc_auc": metrics.get("roc_auc"),
            "recall": metrics.get("recall"),
            "precision": metrics.get("precision"),
            "balanced_accuracy": metrics.get("balanced_accuracy"),
            "average_precision": metrics.get("average_precision"),
            "precision_at_10pct": metrics.get("precision_at_10pct"),
        },
        "grade_policy": {
            "A": "risk score < 15/100",
            "B": "risk score 15/100 to < 28/100",
            "C": "risk score 28/100 to < 42/100",
            "D": "risk score 42/100 to < 58/100",
            "E": "risk score 58/100 to < 74/100",
            "F": "risk score >= 74/100",
        },
    }
    if detail_level == "Concise summary":
        instruction = (
            "Act as an independent AI credit reviewer. Use the Random Forest score and loan intake inputs as evidence. "
            "Provide sections for RF model baseline, AI independent assessment, Top risk drivers, Mitigating factors, "
            "Recommended analyst action, and Compliance note. Include one line exactly like 'AI review score: NN/100' "
            "where 0 is lower risk and 100 is higher risk. Include one line exactly like 'AI suggested grade: X' "
            "using the same A-F grade thresholds provided. If your AI grade differs from the RF grade, say whether the case "
            "looks more severe or less severe, for example 'more like grade E than RF grade C'. Keep it brief. "
            "Do not invent facts or claim legal certainty."
        )
    else:
        instruction = (
            "Act as an independent AI credit reviewer and write a detailed credit-risk analyst memo. "
            "Use the Random Forest score, RF model validation metrics, and loan intake inputs as evidence, but do not merely restate the RF result. "
            "Run your own qualitative assessment of the case and explain whether you agree, partially agree, or disagree with the RF recommendation. "
            "Include one line exactly like 'AI review score: NN/100' where 0 is lower risk and 100 is higher risk. "
            "Treat this AI review score as an independent qualitative review score, not as a calibrated probability. "
            "Convert that score into an A-F grade using the same grade thresholds provided and include one line exactly like "
            "'AI suggested grade: X'. If your AI grade is worse than the RF grade, explicitly say the case looks more severe, "
            "for example 'more like grade E than RF grade C', and explain why. If your AI grade is better than the RF grade, "
            "explicitly say the case looks less severe, for example 'more like grade B than RF grade C', and explain why. "
            "If the grades match, explain why the RF grade is directionally supported. "
            "Use these sections: RF model baseline, AI independent assessment, Agreement with RF model, AI suggested grade rationale, Key risk drivers, "
            "Mitigating factors, Evidence and data readiness, Recommended analyst action, Follow-up questions, "
            "and Compliance note. Explain what each important signal means in practical lending terms, "
            "connect the recommendation to the applicant facts, and be specific about what the analyst should verify next. "
            "Do not invent facts or claim legal certainty."
        )
    payload = {
        "application": application,
        "prediction": prediction,
        "model_context": model_context,
        "instruction": instruction,
    }
    return [
        {
            "role": "system",
            "content": "You write plain-language credit and anomaly risk explanations for SME lending decision support.",
        },
        {"role": "user", "content": json.dumps(payload, default=str)},
    ]


def _openai_explanation(application, prediction, model, detail_level="Detailed analyst memo", model_metrics=None):
    key = _api_key()
    if not key:
        _set_explanation_error("OpenAI API key is not configured.")
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key, timeout=30)
        response = client.responses.create(model=model, input=_llm_messages(application, prediction, detail_level, model_metrics))
        st.session_state.last_explanation_error = None
        return response.output_text
    except Exception as error:
        _set_explanation_error(f"OpenAI API explanation failed: {error}")
        return None


def _local_explanation(
    application,
    prediction,
    model,
    base_url=None,
    api_key=None,
    detail_level="Detailed analyst memo",
    model_metrics=None,
):
    if not st.session_state.get("local_llm_settings_saved", False):
        _set_explanation_error("Local server settings have not been saved yet.")
        return None
    if not (base_url or "").strip() or not (model or "").strip():
        _set_explanation_error("Local server URL and model name are required before calling the local model.")
        return None
    try:
        from openai import OpenAI

        normalized_base_url = _normalize_local_base_url(base_url)
        client = OpenAI(
            api_key=api_key or _local_api_key(),
            base_url=normalized_base_url,
            timeout=45,
        )
        response = client.chat.completions.create(
            model=model or _local_model(),
            messages=_llm_messages(application, prediction, detail_level, model_metrics),
            temperature=0.2,
        )
        st.session_state.last_explanation_error = None
        st.session_state.last_local_llm_base_url = normalized_base_url
        return response.choices[0].message.content
    except Exception as error:
        _set_explanation_error(f"Local server explanation failed: {error}")
        return None


def llm_explanation(
    application,
    prediction,
    model,
    provider="OpenAI API",
    local_base_url=None,
    local_api_key=None,
    detail_level="Detailed analyst memo",
    model_metrics=None,
):
    if provider == "Local server":
        return _local_explanation(application, prediction, model, local_base_url, local_api_key, detail_level, model_metrics)
    return _openai_explanation(application, prediction, model, detail_level, model_metrics)


def explain_prediction(
    application,
    prediction,
    use_llm=False,
    model="gpt-4.1-mini",
    provider="OpenAI API",
    local_base_url=None,
    local_api_key=None,
    detail_level="Detailed analyst memo",
    model_metrics=None,
):
    if use_llm:
        explanation = llm_explanation(
            application,
            prediction,
            model,
            provider,
            local_base_url,
            local_api_key,
            detail_level,
            model_metrics,
        )
        if explanation:
            st.session_state.last_explanation_source = provider
            return explanation
        st.session_state.last_explanation_source = "Deterministic fallback"
    else:
        st.session_state.last_explanation_source = "Deterministic"
        st.session_state.last_explanation_error = None
    return deterministic_explanation(application, prediction)
