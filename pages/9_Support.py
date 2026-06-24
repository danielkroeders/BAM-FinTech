from urllib.parse import quote
from datetime import datetime

import streamlit as st

from src.core.runtime import bootstrap_state
from src.ui.components import get_profile, is_sme_profile, render_sidebar

st.set_page_config(page_title="Support", layout="wide")
bootstrap_state()
render_sidebar()
profile = get_profile()
sme_mode = is_sme_profile(profile)

LENDER_SUPPORT_REPS = [
    {
        "name": "Mila Verhoeven",
        "role": "Risk Platform Lead",
        "email": "mila.verhoeven@yourbank.com",
        "focus": "Workspace setup, lender workflow questions, and analyst onboarding.",
    },
    {
        "name": "Daan Peters",
        "role": "Risk Support Specialist",
        "email": "daan.peters@yourbank.com",
        "focus": "Scoring, DSCR, risk flags, document verification, and model explanation questions.",
    },
    {
        "name": "Sofia de Vries",
        "role": "Operations Enablement",
        "email": "sofia.devries@yourbank.com",
        "focus": "Account access, support routing, and training material.",
    },
]

SME_CONSULTANTS = [
    {
        "name": "Emma de Vries",
        "role": "SME Finance Consultant",
        "email": "emma.devries@yourbank.com",
        "focus": "Application readiness, lender questions, and next-step planning.",
    },
    {
        "name": "Noah Bakker",
        "role": "Business Lending Consultant",
        "email": "noah.bakker@yourbank.com",
        "focus": "Loan-purpose discussion, affordability questions, and document expectations.",
    },
    {
        "name": "Sofia de Vries",
        "role": "Applicant Support Consultant",
        "email": "sme.support@yourbank.com",
        "focus": "Portal access, upload issues, and scheduling a consultant conversation.",
    },
]

LENDER_FAQ_ITEMS = [
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

SME_FAQ_ITEMS = [
    (
        "Can I speak with someone about my application?",
        "Yes. Use the consultant cards or request form to connect with a YourBank SME consultant about your application, documents, or next steps.",
    ),
    (
        "Does submitting an application show me the lender's internal score?",
        "No. Internal model scores, verification notes, and lender review details stay private unless the lender publishes a reviewed result.",
    ),
    (
        "What happens if my documents are incomplete or inconsistent?",
        "The lender may request clarification, ask for updated evidence, or decline the application if submitted evidence cannot be verified.",
    ),
    (
        "Are PSD2, accounting, and registry connections live?",
        "In this MVP they are simulated. The portal demonstrates consent and source selection without connecting to real bank, accounting, or registry systems.",
    ),
    (
        "When will I see a rating or evaluation report?",
        "Only after the lender completes review and chooses to publish the outcome. Until then, the SME portal shows readiness guidance rather than an internal lender rating.",
    ),
]


def _active_reps():
    return SME_CONSULTANTS if sme_mode else LENDER_SUPPORT_REPS


def _active_faq():
    return SME_FAQ_ITEMS if sme_mode else LENDER_FAQ_ITEMS


def _support_response(message):
    text = message.lower()
    if sme_mode:
        if any(
            word in text
            for word in ["consultant", "call", "appointment", "speak", "contact"]
        ):
            return "Use the consultant cards above or submit the form to connect with a YourBank SME consultant."
        if any(
            word in text for word in ["document", "upload", "statement", "tax", "kyb"]
        ):
            return (
                "Upload the requested financial statements, bank statements, tax evidence, ownership/KYB files, and forecast support. "
                "The lender verifies submitted evidence after you send the application."
            )
        if any(word in text for word in ["rating", "decision", "report", "published"]):
            return "The rating and evaluation report become visible only after the lender publishes the reviewed outcome."
        if any(
            word in text
            for word in ["psd2", "bank", "accounting", "registry", "connection"]
        ):
            return "In this MVP, data connections are simulated. They show what consent and source selection would look like in production."
        return "Thanks. For applicant help, submit the consultant request above and include your application ID if you have one."

    if any(word in text for word in ["dscr", "interest", "rate", "pricing"]):
        return (
            "For pricing questions, check Personal Workspace's interest rate, annual debt service, DSCR, and stressed DSCR fields. "
            "If DSCR is below 1.0, the case should usually remain in manual review."
        )
    if any(
        word in text
        for word in ["document", "kyb", "upload", "checklist", "validation"]
    ):
        return (
            "Use the Evidence tab in Personal Workspace to download SME-uploaded files and run lender document verification. "
            "Likely category mismatches should be handled as review evidence."
        )
    if any(word in text for word in ["score", "grade", "risk", "flag"]):
        return (
            "The score combines financial pressure, cash flow, forecast realism, document quality, identity/KYB signals, "
            "transaction anomalies, and debt-service stress. Open Model Insights for the full signal list."
        )
    if any(word in text for word in ["email", "rep", "contact", "call"]):
        return "You can contact Mila, Daan, or Sofia using the email links at the top of this Support page."
    if any(word in text for word in ["api", "psd2", "accounting", "integration"]):
        return "Personal connected apps live on Profile & Settings. Model data sources, such as file evidence and financial signals, are separate from those personal app connections."
    return "Thanks. I logged that as a support question. For urgent case review, contact Daan Peters or use the request form above."


def _mailto(rep, category, case_id, message):
    prefix = (
        "YourBank consultant request"
        if sme_mode
        else "YourBank risk-platform support request"
    )
    subject = quote(f"{prefix}: {category}")
    body = quote(
        "\n".join(
            [
                f"Contact: {rep['name']}",
                f"Category: {category}",
                f"Application/Case ID: {case_id or 'Not provided'}",
                f"Requester: {profile.get('email', 'Not provided')}",
                "",
                message or "Please describe the request here.",
            ]
        )
    )
    return f"mailto:{rep['email']}?subject={subject}&body={body}"


reps = _active_reps()
faq_items = _active_faq()
if sme_mode:
    st.title("Connect with a YourBank Consultant")
    st.caption(
        "Ask for application help, document guidance, or a conversation about next steps."
    )
else:
    st.title("Support")
    st.caption(
        "Contact YourBank risk-platform support, submit a request, or use live chat."
    )

st.subheader("Consultants" if sme_mode else "Support Contacts")
rep_cols = st.columns(len(reps))
for column, rep in zip(rep_cols, reps):
    with column:
        st.markdown(f"**{rep['name']}**")
        st.caption(rep["role"])
        st.write(rep["focus"])
        st.markdown(f"[Email {rep['name'].split()[0]}](mailto:{rep['email']})")

st.subheader("Consultant Request" if sme_mode else "Support Request")
with st.form("support_request_form"):
    form_left, form_right = st.columns(2)
    with form_left:
        selected_name = st.selectbox(
            "Consultant" if sme_mode else "Contact", [rep["name"] for rep in reps]
        )
        category = st.selectbox(
            "Category",
            (
                [
                    "Application help",
                    "Documents and uploads",
                    "Data connections",
                    "Published rating or report",
                    "Consultant call",
                    "Account access",
                ]
                if sme_mode
                else [
                    "Personal workspace",
                    "Model score",
                    "Case review",
                    "Document verification",
                    "Account access",
                    "Technical issue",
                    "Workflow question",
                ]
            ),
        )
    with form_right:
        preferred_contact = st.radio(
            "Preferred contact",
            (
                ["Email", "Phone call", "Video call"]
                if sme_mode
                else ["Email", "Slack", "Teams"]
            ),
            horizontal=True,
        )
        case_id = st.text_input(
            "Application ID" if sme_mode else "Case or application ID",
            placeholder="SME-A2M-001" if sme_mode else "APP-00001 or SESSION-001",
        )
    message = st.text_area(
        "Message",
        placeholder=(
            "Tell the consultant what you need help with."
            if sme_mode
            else "Describe what you need help with."
        ),
        height=110,
    )
    submitted = st.form_submit_button(
        "Request Consultant Contact" if sme_mode else "Submit Support Request",
        width="stretch",
    )

if submitted:
    selected_rep = next(rep for rep in reps if rep["name"] == selected_name)
    ticket = {
        "Ticket ID": f"TICKET-{len(st.session_state.support_ticket_history) + 1:03d}",
        "Created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Contact": selected_rep["name"],
        "Category": category,
        "Preferred contact": preferred_contact,
        "Application/Case ID": case_id or "Not provided",
        "Requester": profile.get("email", "Not provided"),
        "Status": "Prepared",
    }
    st.session_state.support_ticket_history.append(ticket)
    st.success(
        f"Request prepared for {selected_rep['name']}. Preferred channel: {preferred_contact}."
    )
    st.markdown(
        f"[Open email draft]({_mailto(selected_rep, category, case_id, message)})"
    )

if st.session_state.support_ticket_history:
    st.subheader("Recent Requests")
    st.dataframe(
        st.session_state.support_ticket_history[-6:], width="stretch", hide_index=True
    )

chat_left, chat_right = st.columns([2, 1])
with chat_left:
    st.subheader("Live Chat")
    st.caption(
        "This chat uses scripted responses and does not contact a real support desk."
    )
    chat_key = "sme_support_chat_history" if sme_mode else "lender_support_chat_history"
    if chat_key not in st.session_state:
        first_name = (
            profile.get("name") or profile.get("display_name") or "there"
        ).split()[0]
        greeting = (
            f"Hi {first_name}, I can help route you to a YourBank consultant or explain the SME application steps."
            if sme_mode
            else f"Hi {first_name}, this is YourBank risk-platform support. Ask about scoring, documents, DSCR, integrations, or case review."
        )
        st.session_state[chat_key] = [{"role": "assistant", "content": greeting}]

    for entry in st.session_state[chat_key][-8:]:
        with st.chat_message(entry["role"]):
            st.write(entry["content"])

    with st.form("support_chat_form", clear_on_submit=True):
        prompt = st.text_input(
            "Message support",
            placeholder=(
                "Ask about documents, submission, consultant contact, or published reports."
                if sme_mode
                else "Ask about scoring, DSCR, documents, or integrations."
            ),
        )
        send_chat = st.form_submit_button("Send", width="stretch")
    if send_chat and prompt.strip():
        st.session_state[chat_key].append({"role": "user", "content": prompt.strip()})
        st.session_state[chat_key].append(
            {"role": "assistant", "content": _support_response(prompt.strip())}
        )
        rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
        if rerun:
            rerun()

with chat_right:
    st.subheader("FAQ")
    for question, answer in faq_items:
        with st.expander(question, expanded=False):
            st.write(answer)
