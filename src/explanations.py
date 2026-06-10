import os

import streamlit as st

from src.formatting import format_currency, format_percent


def _api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def deterministic_explanation(application, prediction):
    probability = prediction["fraud_probability"]
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
    mitigant_text = "\n".join(f"- {item}" for item in mitigants) if mitigants else "- No major mitigating factor was identified in the deterministic checks."
    next_step = {
        "Approve": "Proceed with standard analyst sign-off and retain the case summary.",
        "Manual Review": "Route to an analyst for document verification and risk-factor review.",
        "Reject": "Route to compliance review before any final adverse action is communicated.",
    }[prediction["decision"]]
    return (
        f"Decision: {prediction['decision']} | Grade {prediction['grade']} | Fraud probability {format_percent(probability)}\n\n"
        f"Applicant context: {application.get('company_type', 'The applicant')} in "
        f"{application.get('industry', 'unknown industry')} requested {format_currency(amount)}.\n\n"
        f"Top risk drivers:\n{drivers}\n\n"
        f"Mitigating factors:\n{mitigant_text}\n\n"
        f"Recommended analyst action: {next_step}\n\n"
        "Compliance note: This is decision support for analyst review; high-risk cases require human compliance review "
        "and this output does not establish legal certainty."
    )


def llm_explanation(application, prediction, model):
    key = _api_key()
    if not key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key)
        prompt = {
            "application": application,
            "prediction": prediction,
            "instruction": (
                "Explain the result concisely for a lending fraud analyst using sections for Decision, Top risk drivers, "
                "Mitigating factors, Recommended analyst action, and Compliance note. Do not invent facts or claim legal certainty."
            ),
        }
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": "You write concise, plain-language fraud risk explanations for B2B lending decision support.",
                },
                {"role": "user", "content": str(prompt)},
            ],
        )
        return response.output_text
    except Exception:
        return None


def explain_prediction(application, prediction, use_llm=False, model="gpt-4.1-mini"):
    if use_llm:
        explanation = llm_explanation(application, prediction, model)
        if explanation:
            return explanation
    return deterministic_explanation(application, prediction)
