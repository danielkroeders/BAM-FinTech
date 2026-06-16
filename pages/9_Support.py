from urllib.parse import quote
from datetime import datetime

import streamlit as st

from src.core.runtime import bootstrap_state
from src.ui.components import get_profile, render_sidebar


st.set_page_config(page_title="Support", layout="wide")
bootstrap_state()
render_sidebar()
profile = get_profile()

SUPPORT_REPS = [
    {
        "name": "Mila Verhoeven",
        "role": "Implementation Lead",
        "email": "mila.verhoeven@credrisk.ai",
        "focus": "Onboarding, workspace setup, and lender workflow questions.",
    },
    {
        "name": "Daan Peters",
        "role": "Risk Support Specialist",
        "email": "daan.peters@credrisk.ai",
        "focus": "Scoring, DSCR, risk flags, and model explanation questions.",
    },
    {
        "name": "Sofia de Vries",
        "role": "Customer Success",
        "email": "sofia.devries@credrisk.ai",
        "focus": "Account access, support routing, and training material.",
    },
]

FAQ_ITEMS = [
    (
        "Is this a production credit decision system?",
        "No. This is a decision-support workspace. It helps analysts review risk signals, explanations, and workflow controls, but it does not make legal, compliance, or final credit decisions.",
    ),
    (
        "Where does the data come from?",
        "The workspace uses application, accounting, document, KYB, transaction, forecast, and pricing inputs available to the review file.",
    ),
    (
        "Does the model consider interest rates and repayment affordability?",
        "Yes. Personal Workspace includes an offered interest rate, annual debt service, DSCR, and a +2 percentage point stressed DSCR.",
    ),
    (
        "Can analysts override the model result?",
        "Yes. The Case Review workflow stores the analyst's final action separately from the model recommendation and AI review output.",
    ),
    (
        "How should high-risk outcomes be handled?",
        "High-risk E/F outcomes should be routed to human compliance-style review before any external decision is communicated.",
    ),
    (
        "What integrations are supported?",
        "Personal connected apps include Slack, Teams, Gmail, Outlook, file storage, and meeting tools. Risk-model data sources are handled separately from personal app connections.",
    ),
]


def _support_response(message):
    text = message.lower()
    if any(word in text for word in ["dscr", "interest", "rate", "pricing"]):
        return (
            "For pricing questions, check Personal Workspace's interest rate, annual debt service, DSCR, and stressed DSCR fields. "
            "If DSCR is below 1.0, the case should usually remain in manual review."
        )
    if any(word in text for word in ["document", "kyb", "upload", "checklist"]):
        return (
            "The workspace uses document checklist statuses to track whether financial statements, "
            "bank statements, tax returns, KYB docs, and forecast support are present in the applicant file."
        )
    if any(word in text for word in ["score", "grade", "risk", "flag"]):
        return (
            "The score combines financial pressure, cash flow, forecast realism, document quality, identity/KYB signals, "
            "transaction anomalies, and debt-service stress. Open Model Insights for the full signal list."
        )
    if any(word in text for word in ["email", "rep", "contact", "call"]):
        return "You can contact Mila, Daan, or Sofia using the email links at the top of this Support page."
    if any(word in text for word in ["api", "psd2", "accounting", "integration"]):
        return (
            "Personal connected apps live on Profile & Settings. Model data sources, such as file evidence and financial signals, are separate from those personal app connections."
        )
    return (
        "Thanks. I logged that as a support question. For urgent case review, contact Daan Peters or use the request form above."
    )


def _mailto(rep, category, case_id, message):
    subject = quote(f"CredRisk.AI support request: {category}")
    body = quote(
        "\n".join(
            [
                f"Representative: {rep['name']}",
                f"Category: {category}",
                f"Case/Application ID: {case_id or 'Not provided'}",
                "",
                message or "Please describe the support request here.",
            ]
        )
    )
    return f"mailto:{rep['email']}?subject={subject}&body={body}"


st.title("Support")
st.caption("Contact a CredRisk.AI representative, submit a support request, or use live chat.")

st.subheader("Contact A Representative")
rep_cols = st.columns(len(SUPPORT_REPS))
for column, rep in zip(rep_cols, SUPPORT_REPS):
    with column:
        st.markdown(f"**{rep['name']}**")
        st.caption(rep["role"])
        st.write(rep["focus"])
        st.markdown(f"[Email {rep['name'].split()[0]}](mailto:{rep['email']})")

st.subheader("Support Request")
with st.form("support_request_form"):
    form_left, form_right = st.columns(2)
    with form_left:
        selected_name = st.selectbox("Representative", [rep["name"] for rep in SUPPORT_REPS])
        category = st.selectbox(
            "Category",
            [
                "Personal workspace",
                "Model score",
                "Case review",
                "Document checks",
                "Account access",
                "Technical issue",
                "Workflow question",
            ],
        )
    with form_right:
        preferred_contact = st.radio("Preferred contact", ["Email", "Slack", "Teams"], horizontal=True)
        case_id = st.text_input("Case or application ID", placeholder="APP-00001 or SESSION-001")
    message = st.text_area("Message", placeholder="Describe what you need help with.", height=110)
    submitted = st.form_submit_button("Submit Support Request", width="stretch")

if submitted:
    selected_rep = next(rep for rep in SUPPORT_REPS if rep["name"] == selected_name)
    ticket = {
        "Ticket ID": f"TICKET-{len(st.session_state.support_ticket_history) + 1:03d}",
        "Created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Representative": selected_rep["name"],
        "Category": category,
        "Preferred contact": preferred_contact,
        "Case/Application ID": case_id or "Not provided",
        "Status": "Prepared",
    }
    st.session_state.support_ticket_history.append(ticket)
    st.success(f"Support request prepared for {selected_rep['name']}. Preferred channel: {preferred_contact}.")
    st.markdown(f"[Open email draft]({_mailto(selected_rep, category, case_id, message)})")

if st.session_state.support_ticket_history:
    st.subheader("Recent Support Requests")
    st.dataframe(st.session_state.support_ticket_history[-6:], width="stretch", hide_index=True)

chat_left, chat_right = st.columns([2, 1])
with chat_left:
    st.subheader("Live Chat")
    st.caption("This chat uses scripted responses and does not contact a real support desk.")
    if "support_chat_history" not in st.session_state:
        first_name = (profile.get("name") or profile.get("display_name") or "there").split()[0]
        st.session_state.support_chat_history = [
            {
                "role": "assistant",
                "content": f"Hi {first_name}, this is CredRisk.AI support. Ask about scoring, documents, DSCR, integrations, or case review.",
            }
        ]

    for entry in st.session_state.support_chat_history[-8:]:
        with st.chat_message(entry["role"]):
            st.write(entry["content"])

    with st.form("support_chat_form", clear_on_submit=True):
        prompt = st.text_input("Message support", placeholder="Ask about scoring, DSCR, documents, or integrations.")
        send_chat = st.form_submit_button("Send", width="stretch")
    if send_chat and prompt.strip():
        st.session_state.support_chat_history.append({"role": "user", "content": prompt.strip()})
        st.session_state.support_chat_history.append({"role": "assistant", "content": _support_response(prompt.strip())})
        rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
        if rerun:
            rerun()

with chat_right:
    st.subheader("FAQ")
    for question, answer in FAQ_ITEMS:
        with st.expander(question, expanded=False):
            st.write(answer)
