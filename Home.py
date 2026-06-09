import streamlit as st

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
metric_cols[0].metric("Portfolio Size", f"{len(applications):,}")
metric_cols[1].metric("Known Fraud Count", f"{fraud_count:,}")
metric_cols[2].metric("Model ROC-AUC", f"{metrics['roc_auc']:.3f}")
metric_cols[3].metric("Model Recall", f"{metrics['recall']:.3f}")

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

st.dataframe(
    portfolio.sort_values("fraud_probability", ascending=False)[
        ["application_id", "company_name", "industry", "requested_amount", "fraud_probability", "grade", "decision"]
    ].head(10),
    use_container_width=True,
    hide_index=True,
)

st.warning(
    "This synthetic demo supports analyst review. High-risk results require human compliance review and are not legal determinations."
)
