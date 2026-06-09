import pandas as pd
import streamlit as st

from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="Model Insights", layout="wide")
bootstrap_state()
render_sidebar()

bundle = st.session_state.model_bundle
metrics = bundle.metrics

st.title("Model Insights")
st.caption("Supervised fraud model performance and grading policy.")

cols = st.columns(5)
for col, key in zip(cols, ["accuracy", "precision", "recall", "f1", "roc_auc"]):
    col.metric(key.replace("_", " ").title(), f"{metrics[key]:.3f}")

left, right = st.columns(2)
with left:
    st.subheader("Confusion Matrix")
    matrix = pd.DataFrame(
        [[metrics["tn"], metrics["fp"]], [metrics["fn"], metrics["tp"]]],
        index=["Actual legitimate", "Actual fraud"],
        columns=["Predicted legitimate", "Predicted fraud"],
    )
    st.dataframe(matrix, use_container_width=True)
with right:
    st.subheader("A-F Grading Thresholds")
    thresholds = pd.DataFrame(
        [
            {"Grade": "A", "Fraud probability": "< 0.15", "Decision": "Approve"},
            {"Grade": "B", "Fraud probability": "0.15 to < 0.28", "Decision": "Approve"},
            {"Grade": "C", "Fraud probability": "0.28 to < 0.42", "Decision": "Manual Review"},
            {"Grade": "D", "Fraud probability": "0.42 to < 0.58", "Decision": "Manual Review"},
            {"Grade": "E", "Fraud probability": "0.58 to < 0.74", "Decision": "Reject"},
            {"Grade": "F", "Fraud probability": ">= 0.74", "Decision": "Reject"},
        ]
    )
    st.dataframe(thresholds, use_container_width=True, hide_index=True)

st.subheader("Top Feature Importances")
st.dataframe(bundle.feature_importance.head(20), use_container_width=True, hide_index=True)
st.bar_chart(bundle.feature_importance.head(12).set_index("feature")["importance"])
