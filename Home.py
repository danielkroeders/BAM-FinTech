from datetime import datetime

import streamlit as st

from src.utils.formatting import format_integer
from src.core.runtime import bootstrap_state
from src.utils.table_views import application_table
from src.ui.components import get_profile, open_application_in_workspace, render_sidebar, safe_page_link
from src.features.workbench_features import build_application_queue


st.set_page_config(page_title="CredRisk.AI Home", layout="wide")
bootstrap_state()
render_sidebar()
profile = get_profile()

applications = st.session_state.seed_data["applications"]
selected_model_key = st.session_state.get("selected_ml_model", st.session_state.model_bundle.default_model_key)
workboard = build_application_queue(st.session_state.model_bundle, applications, model_key=selected_model_key)

analyst_name = profile["display_name"]
welcome_name = profile["name"]
my_tasks = workboard[workboard["assigned_analyst"].eq(analyst_name)].copy()
if my_tasks.empty:
    my_tasks = workboard.head(12).copy()

high_priority = int(my_tasks["grade"].isin(["E", "F"]).sum())
due_this_week = int((my_tasks["sla"] == "This week").sum())
evidence_follow_up = int((my_tasks["missing_documents"] > 0).sum())
now_label = datetime.now().strftime("%A %H:%M")

st.title(f"Welcome, {welcome_name}")
st.caption(f"{profile['role']} at {profile['bank']} | Operations console | {now_label}")

metric_cols = st.columns(4)
metric_cols[0].metric("My Open Tasks", format_integer(len(my_tasks)))
metric_cols[1].metric("High Priority", format_integer(high_priority))
metric_cols[2].metric("Due This Week", format_integer(due_this_week))
metric_cols[3].metric("Evidence Follow-Up", format_integer(evidence_follow_up))

st.subheader("Quick Actions")
action_cols = st.columns([2, 1, 1], vertical_alignment="bottom")
task_options = [f"{row.application_id} - {row.company_name} | Grade {row.grade}" for row in my_tasks.head(20).itertuples()]
selected_task_label = action_cols[0].selectbox("Continue task", task_options)
selected_task_id = selected_task_label.split(" - ", 1)[0]
selected_task = my_tasks[my_tasks["application_id"] == selected_task_id].iloc[0].to_dict()
if action_cols[1].button("Continue Selected Task", width="stretch"):
    open_application_in_workspace(selected_task, "Home")


st.subheader("Current Tasks")
task_display = application_table(
    my_tasks.head(10),
    [
        "application_id",
        "company_name",
        "requested_amount",
        "fraud_probability",
        "grade",
        "queue_status",
        "missing_documents",
        "sla",
    ],
    aliases={
        "application_id": "Task ID",
        "company_name": "Applicant",
        "missing_documents": "Evidence gaps",
    },
)
st.dataframe(task_display, width="stretch", hide_index=True)

link_cols = st.columns([1, 1, 3])
with link_cols[0]:
    safe_page_link("pages/1_Personal_Workspace.py", "Open Personal Workspace", ":material/person_search:")
with link_cols[1]:
    safe_page_link("pages/5_LLM_Integration.py", "Open LLM Integration", ":material/psychology:")
with link_cols[2]:
    safe_page_link("pages/2_Operations_Desk.py", "Review Pending Work", ":material/view_list:")

ops_left, ops_right = st.columns(2)
with ops_left:
    if profile.get("slack_connected"):
        st.subheader("Slack Updates")
        update_rows = [
            {"Time": "09:08", "Channel": "#sme-credit-ops", "Update": "A2M Logistics file assigned to Ms. Cooper for credit review."},
            {"Time": "09:21", "Channel": "#evidence-follow-up", "Update": "Two bank-statement requests are waiting on applicant response."},
            {"Time": "09:34", "Channel": "#compliance-review", "Update": "High-risk E/F cases ready for human compliance review before action."},
            {"Time": "09:47", "Channel": "#portfolio-watch", "Update": "Manual review exposure is within the morning operating range."},
        ]
    else:
        st.subheader("Workspace Updates")
        update_rows = [
            {"Time": "09:08", "Channel": "Email", "Update": "A2M Logistics file assigned for credit review."},
            {"Time": "09:21", "Channel": "Teams", "Update": "Two evidence requests are waiting on applicant response."},
            {"Time": "09:34", "Channel": "Queue", "Update": "High-risk E/F cases ready for human compliance review."},
            {"Time": "09:47", "Channel": "Portfolio", "Update": "Manual review exposure is within the morning operating range."},
        ]
    st.dataframe(update_rows, width="stretch", hide_index=True)

with ops_right:
    st.subheader("Calendar Today")
    calendar_rows = [
        {"Time": "10:00", "Event": "Morning credit-risk stand-up", "Owner": "Credit team"},
        {"Time": "11:30", "Event": "A2M Logistics case review", "Owner": analyst_name},
        {"Time": "14:00", "Event": "Compliance escalation check", "Owner": "Risk lead"},
        {"Time": "16:15", "Event": "Watchlist review", "Owner": "Portfolio risk"},
    ]
    st.dataframe(calendar_rows, width="stretch", hide_index=True)
