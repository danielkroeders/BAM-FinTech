import os
import json

import pandas as pd
import streamlit as st

from src.core.data_pipeline import add_derived_features
from src.utils.formatting import format_currency, format_percent


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
    if float(application.get("forecast_support_uploaded", 0)) >= 0.5:
        mitigants.append("Forecast support evidence is present.")
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


def evaluation_signature(application, prediction):
    return (
        f"{application.get('application_id', '')}:"
        f"{prediction.get('fraud_probability', 0):.6f}:"
        f"{prediction.get('grade', '')}:"
        f"{prediction.get('decision', '')}"
    )


def deterministic_sme_report(application, prediction):
    derived = add_derived_features(pd.DataFrame([application])).iloc[0]
    strengths = []
    improvements = []

    if float(application.get("free_cash_flow", 0)) > 0:
        strengths.append("The application shows positive free cash flow.")
    else:
        improvements.append("Explain the path to positive free cash flow and provide evidence for the assumptions.")
    if float(application.get("years_in_business", 0)) >= 5:
        strengths.append("The company has an established operating history.")
    else:
        improvements.append("Provide additional evidence of customer continuity, management experience, and trading history.")
    if float(derived.get("stressed_debt_service_coverage_ratio", 0)) >= 1.0:
        strengths.append("Projected cash flow remains sufficient to cover estimated debt service under the demo stress.")
    else:
        improvements.append("Show how debt service remains affordable if interest costs or operating expenses increase.")
    if float(derived.get("document_completeness_score", 0)) >= 0.95:
        strengths.append("The expected application document set is complete.")
    else:
        improvements.append("Complete the financial statements, bank statements, tax, ownership/KYB, and forecast-support package.")
    if float(application.get("forecast_support_uploaded", 0)) >= 0.5:
        strengths.append("Supporting evidence for the forecast is attached.")
    else:
        improvements.append("Attach contracts, orders, assumptions, or management evidence supporting the forecast.")
    if float(application.get("late_payment_ratio", 0)) >= 0.1:
        improvements.append("Explain recent late-payment patterns and the controls being used to improve payment performance.")
    if float(application.get("collateral_ratio", 0)) < 0.5:
        improvements.append("Clarify available security, guarantees, or other ways the requested exposure could be reduced.")

    strength_text = "\n".join(f"- {item}" for item in strengths) or "- No material strength was confirmed from the current data alone."
    improvement_text = "\n".join(f"- {item}" for item in improvements) or "- Keep the submitted evidence current and respond promptly to lender questions."
    return (
        f"# Credit application evaluation for {application.get('company_name', 'your company')}\n\n"
        "## What this report means\n"
        "This report explains the main factors considered in the application and practical steps that may strengthen the file. "
        "It should be read together with the lender's published rating and decision.\n\n"
        f"## Application reviewed\n"
        f"- Requested amount: {format_currency(float(application.get('requested_amount', 0)))}\n"
        f"- Industry: {application.get('industry', 'Not provided')}\n"
        f"- Region: {application.get('region', 'Not provided')}\n\n"
        f"## Factors supporting the application\n{strength_text}\n\n"
        f"## Areas that need attention\n{improvement_text}\n\n"
        "## Recommended next steps\n"
        "1. Review every item above and attach evidence for any statement or forecast that the lender could not independently verify.\n"
        "2. Explain unusual movements, one-off costs, late payments, or changes in counterparties in plain language.\n"
        "3. Update the cash-flow and debt-repayment plan using assumptions the company can support with records.\n"
        "4. Contact the lender if the published outcome appears to rely on incomplete or outdated information.\n\n"
        "## Important note\n"
        "This is an explanatory decision-support report, not legal or financial advice. Improving the file does not guarantee "
        "approval or a different rating; the lender remains responsible for the final reviewed outcome."
    )


def _llm_messages(application, prediction, detail_level="Detailed analyst memo", model_metrics=None):
    metrics = model_metrics or {}
    model_label = prediction.get("model_label", "ML model")
    model_context = {
        "model_type": model_label,
        "application_risk_score": prediction.get("fraud_probability"),
        "model_grade": prediction.get("grade"),
        "model_recommendation": prediction.get("decision"),
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
            f"Act as an independent AI credit reviewer. Use the {model_label} score and loan intake inputs as evidence. "
            "Provide sections for ML model baseline, AI independent assessment, Top risk drivers, Mitigating factors, "
            "Recommended analyst action, and Compliance note. Include one line exactly like 'AI review score: NN/100' "
            "where 0 is lower risk and 100 is higher risk. Include one line exactly like 'AI suggested grade: X' "
            "using the same A-F grade thresholds provided. If your AI grade differs from the model grade, say whether the case "
            "looks more severe or less severe, for example 'more like grade E than model grade C'. Keep it brief. "
            "Do not invent facts or claim legal certainty."
        )
    else:
        instruction = (
            "Act as an independent AI credit reviewer and write a detailed credit-risk analyst memo. "
            f"Use the {model_label} score, selected model validation metrics, and loan intake inputs as evidence, but do not merely restate the model result. "
            "Run your own qualitative assessment of the case and explain whether you agree, partially agree, or disagree with the selected model recommendation. "
            "Include one line exactly like 'AI review score: NN/100' where 0 is lower risk and 100 is higher risk. "
            "Treat this AI review score as an independent qualitative review score, not as a calibrated probability. "
            "Convert that score into an A-F grade using the same grade thresholds provided and include one line exactly like "
            "'AI suggested grade: X'. If your AI grade is worse than the model grade, explicitly say the case looks more severe, "
            "for example 'more like grade E than model grade C', and explain why. If your AI grade is better than the model grade, "
            "explicitly say the case looks less severe, for example 'more like grade B than model grade C', and explain why. "
            "If the grades match, explain why the model grade is directionally supported. "
            "Use these sections: ML model baseline, AI independent assessment, Agreement with ML model, AI suggested grade rationale, Key risk drivers, "
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


def _sme_report_messages(application, prediction, internal_report):
    payload = {
        "application": application,
        "prediction_context": {
            "model_recommendation": prediction.get("decision"),
            "model_grade": prediction.get("grade"),
        },
        "internal_evaluation": internal_report,
        "instruction": (
            "Write a detailed SME-facing evaluation report in Markdown. The audience is the applicant company, not a credit analyst. "
            "Use calm, respectful, plain language and explain what factors support the application, what concerns require clarification, "
            "what evidence may be missing, and concrete actions the company can take to improve or better explain its position. "
            "Use these headings: What this report means, Application summary, Factors supporting the application, Areas that need attention, "
            "How to strengthen the application, Questions to discuss with the lender, and Important note. "
            "Do not reveal the model risk score, AI review score, provisional model grade, model validation metrics, hidden system signals, "
            "internal compliance routing, or private analyst notes. Do not accuse the company of fraud or wrongdoing. Translate sensitive "
            "signals into neutral requests for evidence or clarification. Do not promise approval or a changed rating. State that the lender's "
            "published rating and decision are the authoritative reviewed outcome."
        ),
    }
    return [
        {
            "role": "system",
            "content": "You write fair, actionable, plain-language credit evaluation reports for SME applicants.",
        },
        {"role": "user", "content": json.dumps(payload, default=str)},
    ]


def _sanitize_sme_report(report):
    restricted_phrases = (
        "ai review score",
        "ai suggested grade",
        "model grade",
        "provisional grade",
        "model risk score",
        "application risk score",
        "fraud probability",
        "model recommendation",
        "roc-auc",
        "balanced accuracy",
        "average precision",
        "precision at",
        "shap",
        "internal compliance",
        "private analyst",
    )
    safe_lines = [
        line
        for line in str(report or "").splitlines()
        if not any(phrase in line.lower() for phrase in restricted_phrases)
    ]
    return "\n".join(safe_lines).strip()


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


def _openai_sme_report(application, prediction, internal_report, model):
    key = _api_key()
    if not key:
        _set_explanation_error("OpenAI API key is not configured.")
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key, timeout=30)
        response = client.responses.create(
            model=model,
            input=_sme_report_messages(application, prediction, internal_report),
        )
        st.session_state.last_explanation_error = None
        return response.output_text
    except Exception as error:
        _set_explanation_error(f"OpenAI API SME report failed: {error}")
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


def _local_sme_report(application, prediction, internal_report, model, base_url=None, api_key=None):
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
            messages=_sme_report_messages(application, prediction, internal_report),
            temperature=0.2,
        )
        st.session_state.last_explanation_error = None
        st.session_state.last_local_llm_base_url = normalized_base_url
        return response.choices[0].message.content
    except Exception as error:
        _set_explanation_error(f"Local server SME report failed: {error}")
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


def generate_evaluation_package(
    application,
    prediction,
    provider="Deterministic",
    model="gpt-4.1-mini",
    local_base_url=None,
    local_api_key=None,
    detail_level="Detailed analyst memo",
    model_metrics=None,
):
    errors = []
    if provider == "Deterministic":
        internal_report = deterministic_explanation(application, prediction)
        sme_report = deterministic_sme_report(application, prediction)
        return {
            "internal_report": internal_report,
            "sme_report": sme_report,
            "internal_source": "Deterministic",
            "sme_source": "Deterministic",
            "errors": errors,
        }

    internal_report = llm_explanation(
        application,
        prediction,
        model,
        provider,
        local_base_url,
        local_api_key,
        detail_level,
        model_metrics,
    )
    internal_error = st.session_state.get("last_explanation_error")
    if not internal_report:
        internal_report = deterministic_explanation(application, prediction)
        internal_source = "Deterministic fallback"
        if internal_error:
            errors.append(internal_error)
    else:
        internal_source = provider

    if provider == "Local server":
        sme_report = _local_sme_report(
            application,
            prediction,
            internal_report,
            model,
            local_base_url,
            local_api_key,
        )
    else:
        sme_report = _openai_sme_report(application, prediction, internal_report, model)
    sme_error = st.session_state.get("last_explanation_error")
    if not sme_report:
        sme_report = deterministic_sme_report(application, prediction)
        sme_source = "Deterministic fallback"
        if sme_error and sme_error not in errors:
            errors.append(sme_error)
    else:
        sme_report = _sanitize_sme_report(sme_report)
        sme_source = provider
        if not sme_report:
            sme_report = deterministic_sme_report(application, prediction)
            sme_source = "Deterministic fallback"
            errors.append("The generated SME report was removed by the applicant-safety filter.")

    st.session_state.last_explanation_source = internal_source
    st.session_state.last_explanation_error = " ".join(errors) if errors else None
    return {
        "internal_report": internal_report,
        "sme_report": sme_report,
        "internal_source": internal_source,
        "sme_source": sme_source,
        "errors": errors,
    }


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
