from urllib.parse import quote

import streamlit as st

from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="Support", layout="wide")
bootstrap_state()
render_sidebar()

SUPPORT_REPS = [
    {
        "name": "Mila Verhoeven",
        "role": "Implementation Lead",
        "email": "mila.verhoeven@credrisk.ai",
        "phone": "+31 20 555 0101",
        "focus": "Onboarding, demo setup, and lender workflow questions.",
    },
    {
        "name": "Daan Peters",
        "role": "Risk Support Specialist",
        "email": "daan.peters@credrisk.ai",
        "phone": "+31 20 555 0102",
        "focus": "Scoring, DSCR, risk flags, and model explanation questions.",
    },
    {
        "name": "Sofia de Vries",
        "role": "Customer Success",
        "email": "sofia.devries@credrisk.ai",
        "phone": "+31 20 555 0103",
        "focus": "Account access, support routing, and training material.",
    },
]

FAQ_ITEMS = [
    (
        "Is this a production credit decision system?",
        "No. This MVP is a synthetic decision-support demo. It helps analysts review risk signals, explanations, and workflow controls, but it does not make legal, compliance, or final credit decisions.",
    ),
    (
        "Where does the data come from in this MVP?",
        "The current demo uses synthetic seed data. It simulates financial statements, cash flow, document status, KYB checks, transaction behavior, forecasts, and pricing inputs.",
    ),
    (
        "Does the model consider interest rates and repayment affordability?",
        "Yes. Loan Intake includes an offered interest rate, annual debt service, DSCR, and a +2 percentage point stressed DSCR.",
    ),
    (
        "Can analysts override the model result?",
        "Yes. The Case Review workflow stores the final decision separately from the model recommendation and records supervisor approval for manual score adjustment.",
    ),
    (
        "How should high-risk outcomes be handled?",
        "High-risk E/F outcomes should be routed to human compliance-style review before any external decision is communicated.",
    ),
    (
        "What integrations are planned after the MVP?",
        "The business plan points toward PSD2/Open Banking, accounting integrations, registry/KvK data, contextual data sources, and eventually an API and SME self-service portal.",
    ),
]


def _support_response(message):
    text = message.lower()
    if any(word in text for word in ["dscr", "interest", "rate", "pricing"]):
        return (
            "For pricing questions, check Loan Intake's interest rate, annual debt service, DSCR, and stressed DSCR fields. "
            "If DSCR is below 1.0, the case should usually remain in manual review."
        )
    if any(word in text for word in ["document", "kyb", "upload", "checklist"]):
        return (
            "The MVP does not upload real files. It uses document checklist statuses to simulate whether financial statements, "
            "bank statements, tax returns, KYB docs, and forecast support have already been reviewed."
        )
    if any(word in text for word in ["score", "grade", "risk", "flag"]):
        return (
            "The score combines financial pressure, cash flow, forecast realism, document quality, identity/KYB signals, "
            "transaction anomalies, and debt-service stress. Open Model Insights for the full signal list."
        )
    if any(word in text for word in ["email", "phone", "rep", "contact", "call"]):
        return "You can contact Mila, Daan, or Sofia using the email and phone links at the top of this Support page."
    if any(word in text for word in ["api", "psd2", "accounting", "integration"]):
        return (
            "Integrations are part of the post-MVP roadmap. The current version simulates PSD2, accounting, document, "
            "registry, and contextual signals with synthetic data."
        )
    return (
        "Thanks. I logged that as a demo support question. For urgent case review, contact Daan Peters or use the request form above."
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
st.caption("Contact a CredRisk.AI representative, submit a support request, or use the demo live chat.")

st.subheader("Contact A Representative")
rep_cols = st.columns(len(SUPPORT_REPS))
for column, rep in zip(rep_cols, SUPPORT_REPS):
    with column:
        st.markdown(f"**{rep['name']}**")
        st.caption(rep["role"])
        st.write(rep["focus"])
        st.markdown(f"[Email {rep['name'].split()[0]}](mailto:{rep['email']})")
        st.markdown(f"[Call {rep['phone']}](tel:{rep['phone'].replace(' ', '')})")

st.subheader("Support Request")
with st.form("support_request_form"):
    form_left, form_right = st.columns(2)
    with form_left:
        selected_name = st.selectbox("Representative", [rep["name"] for rep in SUPPORT_REPS])
        category = st.selectbox(
            "Category",
            [
                "Loan intake",
                "Model score",
                "Case review",
                "Document checks",
                "Account access",
                "Technical issue",
                "Demo question",
            ],
        )
    with form_right:
        preferred_contact = st.radio("Preferred contact", ["Email", "Phone"], horizontal=True)
        case_id = st.text_input("Case or application ID", placeholder="APP-00001 or SESSION-001")
    message = st.text_area("Message", placeholder="Describe what you need help with.", height=110)
    submitted = st.form_submit_button("Submit Support Request", use_container_width=True)

if submitted:
    selected_rep = next(rep for rep in SUPPORT_REPS if rep["name"] == selected_name)
    st.success(f"Support request prepared for {selected_rep['name']}. Preferred contact: {preferred_contact}.")
    st.markdown(f"[Open email draft]({_mailto(selected_rep, category, case_id, message)})")

chat_left, chat_right = st.columns([2, 1])
with chat_left:
    st.subheader("Live Chat")
    st.caption("Demo chat only. It uses scripted responses and does not contact a real support desk.")
    if "support_chat_history" not in st.session_state:
        st.session_state.support_chat_history = [
            {
                "role": "assistant",
                "content": "Hi Alice, this is CredRisk.AI support. Ask about scoring, documents, DSCR, integrations, or case review.",
            }
        ]

    for entry in st.session_state.support_chat_history[-8:]:
        with st.chat_message(entry["role"]):
            st.write(entry["content"])

    with st.form("support_chat_form", clear_on_submit=True):
        prompt = st.text_input("Message support", placeholder="Ask about scoring, DSCR, documents, or integrations.")
        send_chat = st.form_submit_button("Send", use_container_width=True)
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
