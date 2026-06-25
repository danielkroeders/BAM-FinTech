# Lender home launchpad for submitted SME intake and operations context.
from datetime import datetime

import streamlit as st

from src.utils.formatting import format_integer
from src.core.runtime import bootstrap_state
from src.ui.components import get_profile, is_sme_profile, open_application_in_workspace, render_sidebar, safe_page_link
from src.features.workbench_features import build_application_queue
from src.utils.workflow_transfer import SME_SUBMISSION_SOURCE, find_submitted_application, submitted_intake_rows


st.set_page_config(page_title="CredRisk.AI Home", layout="wide")
bootstrap_state()
render_sidebar()
profile = get_profile()

# Home is intentionally a lender landing page. It reads session-level state that
# other pages write: the synthetic workboard comes from seed data/model scoring,
# while SME submissions come from the applicant-owned portal snapshot history.
# Keeping those two sources distinct prevents the demo from mixing "open queue"
# work with the SME -> analyst -> SME journey.
if is_sme_profile(profile):
    # Home is lender-facing; SME users are redirected to the intake portal to keep ownership of edits there.
    st.title(f"Welcome, {profile['name']}")
    st.caption("SME company account | Company data, connections, credit health, and lender submission")
    st.info(
        "Your company account uses the SME Portal. Continue there to manage the application and its evidence connections."
    )
    safe_page_link("pages/6_SME_Credit_Health.py", "Open Company Portal", ":material/domain:")
    st.stop()

applications = st.session_state.seed_data["applications"]
selected_model_key = st.session_state.model_bundle.default_model_key
workboard = build_application_queue(st.session_state.model_bundle, applications, model_key=selected_model_key)

analyst_name = profile["display_name"]
welcome_name = profile["name"]
my_tasks = workboard[workboard["assigned_analyst"].eq(analyst_name)].copy()
if my_tasks.empty:
    # Demo seed data may not always assign rows to the active profile, so keep Home populated.
    my_tasks = workboard.head(12).copy()
submitted_rows = submitted_intake_rows(
    st.session_state.sme_submission_history,
    st.session_state.application_lifecycle,
    active_application=st.session_state.get("active_queue_application"),
    sme_application=st.session_state.get("sme_company_application"),
)

# These headline numbers are operational indicators, not model metrics. They
# help a lender analyst decide whether to continue an SME-submitted case first
# or move into generic queue triage in Operations Desk.
high_priority = int(my_tasks["grade"].isin(["E", "F"]).sum())
due_this_week = int((my_tasks["sla"] == "This week").sum())
evidence_follow_up = int((my_tasks["missing_documents"] > 0).sum())
now_label = datetime.now().strftime("%A %H:%M")

st.title(f"Welcome, {welcome_name}")
st.caption(f"{profile['role']} at {profile['bank']} | Operations console | {now_label}")

metric_cols = st.columns(5)
metric_cols[0].metric("SME Intake", format_integer(len(submitted_rows)))
metric_cols[1].metric("High Priority Queue", format_integer(high_priority))
metric_cols[2].metric("Due This Week", format_integer(due_this_week))
metric_cols[3].metric("Evidence Follow-Up", format_integer(evidence_follow_up))
metric_cols[4].metric("Operations Queue", format_integer(len(my_tasks)))

st.subheader("Suggested Actions")
st.caption(
    "Use SME Portal Intake for the end-to-end demo flow. Generic task queues live in Operations Desk."
)
if submitted_rows:
    # Submitted SME snapshots are opened from the workflow-transfer helper, not rebuilt from the queue.
    st.markdown("**SME Portal Intake**")
    st.caption(
        "Company-submitted applications carried through demo-session state. Open one to continue the lender review."
    )
    st.dataframe(submitted_rows, width="stretch", hide_index=True)
    intake_options = [
        f"{row['Application ID']} - {row['Company']} | {row['Status']}"
        for row in submitted_rows
    ]
    intake_cols = st.columns([2, 1])
    selected_intake_label = intake_cols[0].selectbox("Submitted application", intake_options)
    selected_intake_id = selected_intake_label.split(" - ", 1)[0]
    if intake_cols[1].button("Open SME Submission", width="stretch"):
        application = find_submitted_application(
            st.session_state.sme_submission_history,
            selected_intake_id,
            active_application=st.session_state.get("active_queue_application"),
            sme_application=st.session_state.get("sme_company_application"),
        )
        if application:
            open_application_in_workspace(application, SME_SUBMISSION_SOURCE)
        else:
            st.error("The submitted application snapshot could not be found.")
else:
    st.info(
        "No SME-submitted intake is waiting yet. Start from the SME company account to create the demo case, "
        "or use Operations Desk if you want to inspect the synthetic work queue."
    )

# The quick links mirror the normal analyst sequence: review the locked intake,
# generate the AI evaluation package, then use help/training or queue pages only
# when they are useful side paths.
link_cols = st.columns([1, 1, 1, 2])
with link_cols[0]:
    safe_page_link("pages/1_Personal_Workspace.py", "Open Personal Workspace", ":material/person_search:")
with link_cols[1]:
    safe_page_link("pages/5_LLM_Integration.py", "Open LLM Integration", ":material/psychology:")
with link_cols[2]:
    safe_page_link("pages/10_Tutorials.py", "Open Tutorials", ":material/school:")
with link_cols[3]:
    safe_page_link("pages/2_Operations_Desk.py", "Review Pending Work", ":material/view_list:")

ops_left, ops_right = st.columns(2)
with ops_left:
    if profile.get("slack_connected"):
        # Integration cards remain simulated; Profile Settings controls which channel label is shown.
        # The content is static demo context; it changes channel labels based on
        # profile settings so users can see the effect of connecting Slack.
        st.subheader("Slack Updates")
        update_rows = [
            {"Time": "09:08", "Channel": "#sme-credit-ops", "Update": "A2M Logistics file assigned to Ms. Cooper for credit review."},
            {"Time": "09:21", "Channel": "#evidence-follow-up", "Update": "Two bank-statement requests are waiting on applicant response."},
            {"Time": "09:34", "Channel": "#compliance-review", "Update": "High-risk E/F cases ready for human compliance review before action."},
            {"Time": "09:47", "Channel": "#portfolio-watch", "Update": "Manual review exposure is within the morning operating range."},
        ]
    else:
        # When Slack is disabled, keep the same operational story available via
        # generic workspace/email labels instead of hiding the entire section.
        st.subheader("Workspace Updates")
        update_rows = [
            {"Time": "09:08", "Channel": "Email", "Update": "A2M Logistics file assigned for credit review."},
            {"Time": "09:21", "Channel": "Teams", "Update": "Two evidence requests are waiting on applicant response."},
            {"Time": "09:34", "Channel": "Queue", "Update": "High-risk E/F cases ready for human compliance review."},
            {"Time": "09:47", "Channel": "Portfolio", "Update": "Manual review exposure is within the morning operating range."},
        ]
    st.dataframe(update_rows, width="stretch", hide_index=True)

with ops_right:
    # The calendar is a lightweight narrative device. It gives presenters a
    # reason to open the A2M case without requiring a real calendar integration.
    st.subheader("Calendar Today")
    calendar_rows = [
        {"Time": "10:00", "Event": "Morning credit-risk stand-up", "Owner": "Credit team"},
        {"Time": "11:30", "Event": "A2M Logistics case review", "Owner": analyst_name},
        {"Time": "14:00", "Event": "Compliance escalation check", "Owner": "Risk lead"},
        {"Time": "16:15", "Event": "Watchlist review", "Owner": "Portfolio risk"},
    ]
    st.dataframe(calendar_rows, width="stretch", hide_index=True)
