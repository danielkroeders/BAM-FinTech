from datetime import datetime

import streamlit as st

from src.formatting import format_currency, format_integer, format_percent
from src.runtime import bootstrap_state
from src.ui import PROFILE, render_sidebar
from src.workbench_features import build_application_queue


st.set_page_config(page_title="CredRisk.AI Home", layout="wide")
bootstrap_state()
render_sidebar()

applications = st.session_state.seed_data["applications"]
workboard = build_application_queue(st.session_state.model_bundle, applications)

analyst_name = PROFILE["display_name"]
my_tasks = workboard[workboard["assigned_analyst"].eq(analyst_name)].copy()
if my_tasks.empty:
    my_tasks = workboard.head(12).copy()

high_priority = int(my_tasks["grade"].isin(["E", "F"]).sum())
evidence_follow_up = int((my_tasks["missing_documents"] > 0).sum())
reviews_saved = len(st.session_state.review_history)
now_label = datetime.now().strftime("%A %H:%M")

st.title(f"Welcome, {analyst_name}")
st.caption(f"{PROFILE['role']} at {PROFILE['bank']} | Operations console | {now_label}")

metric_cols = st.columns(4)
metric_cols[0].metric("My Open Tasks", format_integer(len(my_tasks)))
metric_cols[1].metric("High Priority", format_integer(high_priority))
metric_cols[2].metric("Evidence Follow-Up", format_integer(evidence_follow_up))
metric_cols[3].metric("Reviews Saved", format_integer(reviews_saved))

st.subheader("Current Tasks")
task_display = my_tasks[
    [
        "application_id",
        "company_name",
        "requested_amount",
        "fraud_probability",
        "grade",
        "queue_status",
        "missing_documents",
        "sla",
    ]
].head(10).copy()
task_display["requested_amount"] = task_display["requested_amount"].apply(format_currency)
task_display["fraud_probability"] = task_display["fraud_probability"].apply(format_percent)
task_display = task_display.rename(
    columns={
        "application_id": "Task ID",
        "company_name": "Applicant",
        "requested_amount": "Requested amount",
        "fraud_probability": "Application risk score",
        "grade": "Grade",
        "queue_status": "Task status",
        "missing_documents": "Evidence gaps",
        "sla": "SLA",
    }
)
st.dataframe(task_display, width="stretch", hide_index=True)

page_link = getattr(st, "page_link", None)
if page_link:
    link_cols = st.columns([1, 1, 3])
    with link_cols[0]:
        st.page_link("pages/Personal_Workspace.py", label="Open Personal Workspace")
    with link_cols[1]:
        st.page_link("pages/Operations_Desk.py", label="Open Operations Desk")

ops_left, ops_right = st.columns(2)
with ops_left:
    st.subheader("Slack Updates")
    slack_rows = [
        {"Time": "09:08", "Channel": "#sme-credit-ops", "Update": "A2M Logistics file assigned to Ms. Cooper for credit review."},
        {"Time": "09:21", "Channel": "#evidence-follow-up", "Update": "Two bank-statement requests are waiting on applicant response."},
        {"Time": "09:34", "Channel": "#compliance-review", "Update": "High-risk E/F cases ready for human compliance review before action."},
        {"Time": "09:47", "Channel": "#portfolio-watch", "Update": "Manual review exposure is within the morning operating range."},
    ]
    st.dataframe(slack_rows, width="stretch", hide_index=True)

with ops_right:
    st.subheader("Calendar Today")
    calendar_rows = [
        {"Time": "10:00", "Event": "Morning credit-risk stand-up", "Owner": "Credit team"},
        {"Time": "11:30", "Event": "A2M Logistics case review", "Owner": analyst_name},
        {"Time": "14:00", "Event": "Compliance escalation check", "Owner": "Risk lead"},
        {"Time": "16:15", "Event": "Watchlist review", "Owner": "Portfolio risk"},
    ]
    st.dataframe(calendar_rows, width="stretch", hide_index=True)
