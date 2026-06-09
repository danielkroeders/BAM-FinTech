import streamlit as st

from src.explanations import explain_prediction
from src.runtime import bootstrap_state
from src.shap_explanations import shap_driver_table
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

    st.subheader("SHAP Driver Analysis")
    try:
        shap_table, baseline_probability, predicted_probability = shap_driver_table(st.session_state.model_bundle, application)
        top_drivers = shap_table.head(8).copy()

        summary_cols = st.columns(3)
        summary_cols[0].metric("Baseline Fraud Risk", f"{baseline_probability:.1%}")
        summary_cols[1].metric("Application Fraud Risk", f"{predicted_probability:.1%}")
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
        st.dataframe(display_table, use_container_width=True, hide_index=True)
        st.caption(
            "Positive SHAP contributions push the fraud score higher for this application. Negative contributions push it lower. "
            "Categorical one-hot features are grouped back to their original fields for readability."
        )
    except ImportError:
        st.warning("Install the `shap` dependency from requirements.txt to view SHAP driver analysis.")
