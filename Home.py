import streamlit as st

from src.formatting import format_currency, format_integer, format_percent, format_score
from src.modeling import score_portfolio
from src.runtime import bootstrap_state
from src.ui import render_sidebar
from src.workbench_features import build_application_queue


st.set_page_config(page_title="CredRisk.AI Underwriter Workbench", layout="wide")
bootstrap_state()
render_sidebar()

seed_data = st.session_state.seed_data
model_bundle = st.session_state.model_bundle
applications = seed_data["applications"]
portfolio = score_portfolio(model_bundle, applications)

high_risk_count = int(portfolio["grade"].isin(["E", "F"]).sum())
metrics = model_bundle.metrics

st.title("CredRisk.AI Underwriter Workbench")
st.caption("AI-driven SME credit risk decision support for lenders, using synthetic real-time data signals.")

metric_cols = st.columns(4)
metric_cols[0].metric("Applications Assessed", format_integer(len(applications)))
metric_cols[1].metric("High-Risk Cases", format_integer(high_risk_count))
metric_cols[2].metric("Model ROC-AUC", format_score(metrics["roc_auc"], 3))
metric_cols[3].metric("Model Recall", format_score(metrics["recall"], 3))

st.subheader("Operational Workflow")
workflow_cols = st.columns(3)
workflow_cols[0].info("1. Intake an SME loan request with financial, document, KYB, pricing, and contextual signals.")
workflow_cols[1].info("2. Score application risk, assign an A-F risk grade, and recommend an action.")
workflow_cols[2].info("3. Route C-D cases to manual review and high-risk E-F cases to compliance review.")

st.subheader("Application Queue")
queue_preview = build_application_queue(model_bundle, applications, limit=8)
queue_display = queue_preview[
    [
        "application_id",
        "company_name",
        "requested_amount",
        "fraud_probability",
        "grade",
        "queue_status",
        "assigned_analyst",
        "sla",
    ]
].copy()
queue_display["requested_amount"] = queue_display["requested_amount"].apply(format_currency)
queue_display["fraud_probability"] = queue_display["fraud_probability"].apply(format_percent)
queue_display = queue_display.rename(
    columns={
        "application_id": "Application ID",
        "company_name": "Company",
        "requested_amount": "Requested amount",
        "fraud_probability": "Application risk score",
        "grade": "Grade",
        "queue_status": "Queue status",
        "assigned_analyst": "Assigned analyst",
        "sla": "SLA",
    }
)
st.dataframe(queue_display, use_container_width=True, hide_index=True)
page_link = getattr(st, "page_link", None)
if page_link:
    st.page_link("pages/Application_Queue.py", label="Open full application queue")

st.subheader("Simulated Data Sources")
data_sources = [
    {"Source": "PSD2 / Open Banking", "MVP status": "Simulated", "Signals": "Transactions, payment behavior, cash flow, runway"},
    {"Source": "Accounting integrations", "MVP status": "Simulated", "Signals": "Revenue, debt, working capital, financial ratios"},
    {"Source": "Document package", "MVP status": "Simulated", "Signals": "Financial statements, bank statements, tax, KYB, forecast support"},
    {"Source": "Registry / KvK", "MVP status": "Simulated", "Signals": "Entity type, operating history, ownership and identity markers"},
    {"Source": "Management context", "MVP status": "Simulated", "Signals": "CEO, CFO, COO notes and applicant narrative"},
    {"Source": "Market/contextual signals", "MVP status": "Simulated", "Signals": "Region, country risk, sector and anomaly indicators"},
]
st.dataframe(data_sources, use_container_width=True, hide_index=True)

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
top_applications = top_applications.rename(columns={"fraud_probability": "Application risk score"})
st.dataframe(top_applications, use_container_width=True, hide_index=True)

st.warning(
    "This synthetic MVP supports analyst review. High-risk results require human compliance review and are not legal determinations."
)
