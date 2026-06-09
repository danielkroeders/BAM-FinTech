import os

import streamlit as st


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
    drivers = "; ".join(flags) if flags else "no deterministic risk flags were triggered"
    amount = float(application.get("requested_amount", 0))
    context = (
        f"{application.get('company_type', 'The applicant')} in {application.get('industry', 'unknown industry')} "
        f"requested ${amount:,.0f}."
    )
    return (
        f"Recommended action is {prediction['decision']} with grade {prediction['grade']} and fraud probability "
        f"{probability:.1%}. {context} Main risk drivers: {drivers}. This is decision support for analyst review; "
        "high-risk cases require human compliance review and this output does not establish legal certainty."
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
            "instruction": "Explain the result concisely for a lending fraud analyst. Do not invent facts or claim legal certainty.",
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
