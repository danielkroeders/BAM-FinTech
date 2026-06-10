import streamlit as st

from src.formatting import format_currency, format_integer, format_percent, format_score
from src.modeling import score_portfolio
from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="B2B Loan Fraud Intelligence", layout="wide")
bootstrap_state()
render_sidebar()

seed_data = st.session_state.seed_data
model_bundle = st.session_state.model_bundle
applications = seed_data["applications"]
portfolio = score_portfolio(model_bundle, applications)

fraud_count = int(applications["is_fraud"].sum())
metrics = model_bundle.metrics

st.title("B2B Loan Fraud Intelligence")
st.caption("Decision support for business lenders reviewing B2B loan fraud risk.")

metric_cols = st.columns(4)
metric_cols[0].metric("Portfolio Size", format_integer(len(applications)))
metric_cols[1].metric("Known Fraud Count", format_integer(fraud_count))
metric_cols[2].metric("Model ROC-AUC", format_score(metrics["roc_auc"], 3))
metric_cols[3].metric("Model Recall", format_score(metrics["recall"], 3))

st.subheader("Operational Workflow")
workflow_cols = st.columns(3)
workflow_cols[0].info("1. Intake a B2B loan request with company, credit, and transaction-risk signals.")
workflow_cols[1].info("2. Score fraud probability, assign an A-F risk grade, and recommend an action.")
workflow_cols[2].info("3. Route C-D cases to manual review and high-risk E-F cases to compliance review.")

st.subheader("Current Portfolio Snapshot")
left, right = st.columns(2)
with left:
    grade_counts = portfolio["grade"].value_counts().reindex(list("ABCDEF"), fill_value=0)
    st.bar_chart(grade_counts)
with right:
    decision_counts = portfolio["decision"].value_counts()
    st.bar_chart(decision_counts)

top_applications = portfolio.sort_values("fraud_probability", ascending=False)[
    ["application_id", "company_name", "industry", "requested_amount", "fraud_probability", "grade", "decision"]
].head(10)
top_applications = top_applications.copy()
top_applications["requested_amount"] = top_applications["requested_amount"].apply(format_currency)
top_applications["fraud_probability"] = top_applications["fraud_probability"].apply(format_percent)
st.dataframe(top_applications, use_container_width=True, hide_index=True)

st.warning(
    "This synthetic demo supports analyst review. High-risk results require human compliance review and are not legal determinations."
)
