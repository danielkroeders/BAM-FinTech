from datetime import datetime

import pandas as pd
import streamlit as st

from src.formatting import format_currency, format_percent, format_score
from src.runtime import bootstrap_state
from src.ui import render_sidebar
from src.workbench_features import build_application_queue


st.set_page_config(page_title="Operations Desk", layout="wide")
bootstrap_state()
render_sidebar()

applications = st.session_state.seed_data["applications"]
queue = build_application_queue(st.session_state.model_bundle, applications)
final_decisions = st.session_state.bulk_final_decisions
queue["final_decision"] = queue["application_id"].apply(
    lambda application_id: final_decisions.get(application_id, {}).get("final_decision", "Pending")
)

st.title("Operations Desk")
st.caption("Team workboard for live SME lending tasks, evidence follow-up, and review routing.")

metric_cols = st.columns(4)
metric_cols[0].metric("Open Work Items", len(queue))
metric_cols[1].metric("Manual / Compliance", int(queue["queue_status"].isin(["Manual review", "Compliance review"]).sum()))
metric_cols[2].metric("Evidence Follow-Up", int((queue["missing_documents"] > 0).sum()))
metric_cols[3].metric("Rejected Today", int((queue["final_decision"] == "Reject").sum()))

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
        "final_decision",
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
        "queue_status": "Task status",
        "final_decision": "Final decision",
        "missing_documents": "Missing docs",
        "assigned_analyst": "Assigned analyst",
        "sla": "SLA",
    }
)

st.dataframe(display, width="stretch", hide_index=True)

with st.expander("Bulk Actions", expanded=False):
    st.caption("Select several visible work items and record one final decision for all of them.")
    bulk_options = [f"{row.application_id} - {row.company_name} | Grade {row.grade}" for row in filtered.itertuples()]
    with st.form("bulk_reject_form"):
        selected_bulk_labels = st.multiselect("Cases", bulk_options)
        bulk_note = st.text_area(
            "Decision note",
            value="Rejected from Operations Desk after reviewing task status, model recommendation, and available evidence.",
        )
        reject_selected = st.form_submit_button("Reject Selected Cases", width="stretch")

    if reject_selected:
        selected_ids = [label.split(" - ", 1)[0] for label in selected_bulk_labels]
        if not selected_ids:
            st.warning("Select at least one case before applying a bulk rejection.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            for application_id in selected_ids:
                row = filtered[filtered["application_id"] == application_id].iloc[0].to_dict()
                review = {
                    "review_id": f"REV-{len(st.session_state.review_history) + 1:03d}",
                    "application_id": application_id,
                    "timestamp": timestamp,
                    "action": "Bulk Reject",
                    "supervisor_email": "",
                    "send_email": False,
                    "analyst_note": bulk_note,
                    "manual_adjustment": False,
                    "final_probability": row["fraud_probability"],
                    "final_grade": row["grade"],
                    "model_recommendation": row["decision"],
                    "final_decision": "Reject",
                }
                st.session_state.bulk_final_decisions[application_id] = review
                st.session_state.bulk_action_history.append(review)
                st.session_state.review_history.append(review)
                st.session_state.portfolio_history.append(
                    {
                        **row,
                        "review_action": "Bulk Reject",
                        "final_decision": "Reject",
                        "manual_adjustment": False,
                    }
                )
            st.success(f"Rejected {len(selected_ids)} case(s) and added the decision to the audit trail.")
            rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
            if rerun:
                rerun()

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
            {"Field": "Task status", "Value": selected["queue_status"]},
            {"Field": "Final decision", "Value": selected["final_decision"]},
            {"Field": "Assigned analyst", "Value": selected["assigned_analyst"]},
        ]
    )
    st.dataframe(selected_details, width="stretch", hide_index=True)

    page_link = getattr(st, "page_link", None)
    if page_link:
        st.page_link("pages/Personal_Workspace.py", label="Open Personal Workspace")
else:
    st.info("No applications match the selected filters.")
