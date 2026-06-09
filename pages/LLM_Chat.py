import streamlit as st

from src.explanations import explain_prediction
from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="AI Explainability", layout="wide")
bootstrap_state()
render_sidebar()

st.title("AI Explainability")
st.caption("Plain-language explanation for the latest scored loan request.")

application = st.session_state.last_application
prediction = st.session_state.last_prediction

if not application or not prediction:
    st.info("No application has been scored yet. Use the Loan Intake page to create the first decision.")
else:
    st.metric("Latest Fraud Probability", f"{prediction['fraud_probability']:.1%}")
    st.write(f"Grade: **{prediction['grade']}**")
    st.write(f"Recommended action: **{prediction['decision']}**")

    st.subheader("Explanation")
    explanation = explain_prediction(
        application,
        prediction,
        use_llm=st.session_state.use_llm_explanations,
        model=st.session_state.explanation_model,
    )
    st.info(explanation)

    with st.expander("Source signals"):
        st.json({"application": application, "prediction": prediction})
