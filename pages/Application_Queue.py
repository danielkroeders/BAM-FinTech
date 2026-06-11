import pandas as pd
import streamlit as st

from src.formatting import format_currency, format_percent, format_score
from src.runtime import bootstrap_state
from src.ui import render_sidebar
from src.workbench_features import build_application_queue


st.set_page_config(page_title="Application Queue", layout="wide")
bootstrap_state()
render_sidebar()

applications = st.session_state.seed_data["applications"]
queue = build_application_queue(st.session_state.model_bundle, applications)

st.title("Application Queue")
st.caption("Incoming SME credit applications prioritized for banker review.")

if st.session_state.investor_demo_mode:
    st.info("Demo path: filter to A2M Logistics or high-priority cases, then open Loan Intake to run the full scoring and review flow.")

status_counts = queue["queue_status"].value_counts()
metric_cols = st.columns(4)
metric_cols[0].metric("Open Applications", len(queue))
metric_cols[1].metric("Manual / Compliance", int(queue["queue_status"].isin(["Manual review", "Compliance review"]).sum()))
metric_cols[2].metric("Missing Docs", int((queue["missing_documents"] > 0).sum()))
metric_cols[3].metric("High Priority", int(queue["grade"].isin(["E", "F"]).sum()))

filter_cols = st.columns([1, 1, 1])
status_filter = filter_cols[0].multiselect("Status", sorted(queue["queue_status"].unique()), default=sorted(queue["queue_status"].unique()))
grade_filter = filter_cols[1].multiselect("Grade", list("ABCDEF"), default=list("ABCDEF"))
analyst_filter = filter_cols[2].multiselect("Analyst", sorted(queue["assigned_analyst"].unique()), default=sorted(queue["assigned_analyst"].unique()))

filtered = queue[
    queue["queue_status"].isin(status_filter)
    & queue["grade"].isin(grade_filter)
    & queue["assigned_analyst"].isin(analyst_filter)
].copy()

display = filtered[
    [
        "application_id",
        "company_name",
        "industry",
        "requested_amount",
        "fraud_probability",
        "grade",
        "decision",
        "queue_status",
        "missing_documents",
        "assigned_analyst",
        "sla",
    ]
].copy()
display["requested_amount"] = display["requested_amount"].apply(format_currency)
display["fraud_probability"] = display["fraud_probability"].apply(format_percent)
display = display.rename(
    columns={
        "application_id": "Application ID",
        "company_name": "Company",
        "industry": "Industry",
        "requested_amount": "Requested amount",
        "fraud_probability": "Application risk score",
        "grade": "Grade",
        "decision": "Model recommendation",
        "queue_status": "Queue status",
        "missing_documents": "Missing docs",
        "assigned_analyst": "Assigned analyst",
        "sla": "SLA",
    }
)

st.dataframe(display, use_container_width=True, hide_index=True)

if not filtered.empty:
    selected_label = st.selectbox(
        "Review application",
        [f"{row.application_id} - {row.company_name}" for row in filtered.itertuples()],
    )
    selected_id = selected_label.split(" - ", 1)[0]
    selected = filtered[filtered["application_id"] == selected_id].iloc[0]

    st.subheader("Selected Application")
    detail_cols = st.columns(5)
    detail_cols[0].metric("Risk score", format_percent(selected["fraud_probability"]))
    detail_cols[1].metric("Grade", selected["grade"])
    detail_cols[2].metric("Decision", selected["decision"])
    detail_cols[3].metric("Doc readiness", format_score(selected["document_completeness_score"]))
    detail_cols[4].metric("SLA", selected["sla"])

    selected_details = pd.DataFrame(
        [
            {"Field": "Company", "Value": selected["company_name"]},
            {"Field": "Industry", "Value": selected["industry"]},
            {"Field": "Region", "Value": selected["region"]},
            {"Field": "Requested amount", "Value": format_currency(selected["requested_amount"])},
            {"Field": "Interest rate", "Value": format_percent(selected["interest_rate"])},
            {"Field": "Free cash flow", "Value": format_currency(selected["free_cash_flow"])},
            {"Field": "Expected runway", "Value": f"{format_score(selected['expected_runway_months'], 0)} mo"},
            {"Field": "Queue status", "Value": selected["queue_status"]},
            {"Field": "Assigned analyst", "Value": selected["assigned_analyst"]},
        ]
    )
    st.dataframe(selected_details, use_container_width=True, hide_index=True)

    page_link = getattr(st, "page_link", None)
    if page_link:
        st.page_link("pages/Loan_Intake.py", label="Open Loan Intake")
else:
    st.info("No applications match the selected filters.")
