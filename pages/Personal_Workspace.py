from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st

from src.case_workflow import (
    DEMO_SCENARIOS,
    REVIEW_ACTIONS,
    adjusted_prediction,
    case_summary,
    mailto_link,
    similar_applications,
)
from src.data_pipeline import add_derived_features, build_forecast_table
from src.explanations import explain_prediction
from src.formatting import (
    format_currency,
    format_currency_input,
    format_integer,
    format_months,
    format_percent,
    format_score,
    parse_eu_number,
)
from src.runtime import bootstrap_state
from src.ui import render_sidebar
from src.workbench_features import (
    build_application_queue,
    credit_memo,
    data_source_badges,
    decision_timeline,
    grouped_risk_drivers,
    model_confidence_rows,
    portfolio_monitoring_preview,
    recommended_loan_terms,
)


st.set_page_config(page_title="Personal Workspace", layout="wide")
bootstrap_state()
render_sidebar()

st.markdown(
    """
    <style>
    .score-panel {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 8px;
        padding: 0;
        margin: 0.35rem 0 0.8rem;
        background: rgba(15, 23, 42, 0.26);
        overflow: hidden;
    }
    .score-panel.low { border-top: 4px solid #22c55e; }
    .score-panel.medium { border-top: 4px solid #eab308; }
    .score-panel.high { border-top: 4px solid #ef4444; }
    .score-panel-header {
        align-items: center;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.8rem 1rem 0.7rem;
    }
    .score-headline {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.05;
    }
    .score-subtitle {
        color: rgba(226, 232, 240, 0.76);
        font-size: 0.82rem;
        line-height: 1.35;
        margin-top: 0.25rem;
    }
    .score-strip {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 0;
    }
    .score-item {
        border-right: 1px solid rgba(148, 163, 184, 0.14);
        min-width: 0;
        padding: 0.75rem 1rem;
    }
    .score-item:last-child {
        border-right: none;
    }
    .score-label {
        color: rgba(226, 232, 240, 0.72);
        font-size: 0.72rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
    }
    .score-value {
        color: #f8fafc;
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.2;
        overflow-wrap: anywhere;
    }
    .decision-badge {
        border-radius: 999px;
        color: #0f172a;
        display: inline-flex;
        font-size: 0.86rem;
        font-weight: 800;
        line-height: 1;
        padding: 0.45rem 0.72rem;
        white-space: nowrap;
    }
    .decision-badge.approve { background: #86efac; }
    .decision-badge.review { background: #fde68a; }
    .decision-badge.reject { background: #fca5a5; }
    .decision-badge.pending { background: #cbd5e1; }
    .decision-panel {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 8px;
        margin: 0.25rem 0 0.9rem;
        padding: 0.9rem 1rem;
        background: rgba(15, 23, 42, 0.18);
    }
    .decision-panel.approve { border-left: 5px solid #22c55e; }
    .decision-panel.review,
    .decision-panel.pending { border-left: 5px solid #eab308; }
    .decision-panel.reject { border-left: 5px solid #ef4444; }
    .decision-title {
        color: #f8fafc;
        font-size: 1.1rem;
        font-weight: 800;
        line-height: 1.25;
        margin-bottom: 0.25rem;
    }
    .decision-copy {
        color: rgba(226, 232, 240, 0.82);
        font-size: 0.88rem;
        line-height: 1.45;
        margin-bottom: 0.55rem;
    }
    .decision-list {
        color: rgba(226, 232, 240, 0.86);
        font-size: 0.85rem;
        line-height: 1.45;
        margin: 0;
        padding-left: 1.1rem;
    }
    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.25rem 0 0.75rem;
    }
    .source-badge {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 999px;
        color: #f8fafc;
        display: inline-flex;
        font-size: 0.78rem;
        font-weight: 750;
        gap: 0.35rem;
        line-height: 1;
        padding: 0.48rem 0.68rem;
    }
    .source-badge.ready { background: rgba(34, 197, 94, 0.22); }
    .source-badge.partial { background: rgba(234, 179, 8, 0.24); }
    .source-badge.review { background: rgba(239, 68, 68, 0.22); }
    .queue-panel {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 8px;
        margin: 0.35rem 0 1rem;
        padding: 0.9rem 1rem;
        background: rgba(15, 23, 42, 0.16);
    }
    .queue-panel-title {
        color: #f8fafc;
        font-size: 1rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }
    .queue-panel-copy {
        color: rgba(226, 232, 240, 0.78);
        font-size: 0.86rem;
        line-height: 1.45;
        margin-bottom: 0.7rem;
    }
    .active-case-card {
        border: 1px solid rgba(34, 197, 94, 0.28);
        border-left: 5px solid #22c55e;
        border-radius: 8px;
        margin: 0.35rem 0 1rem;
        padding: 0.8rem 1rem;
        background: rgba(22, 101, 52, 0.14);
    }
    .active-case-title {
        color: #f8fafc;
        font-size: 0.98rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .active-case-copy {
        color: rgba(226, 232, 240, 0.84);
        font-size: 0.84rem;
        line-height: 1.4;
    }
    @media (max-width: 900px) {
        .score-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .score-panel-header {
            align-items: flex-start;
            flex-direction: column;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

applications = st.session_state.seed_data["applications"]
industries = sorted(applications["industry"].unique())
regions = sorted(applications["region"].unique())
company_types = sorted(applications["company_type"].unique())

FIELD_HELP = {
    "company_name": "Applicant company name used for the session case record and downloadable summary.",
    "industry": "Primary business sector. Sector patterns can affect fraud exposure and cash-flow volatility.",
    "region": "Applicant operating region. Regional context contributes to the risk profile.",
    "company_type": "Legal or operating structure, such as LLC, corporation, partnership, or sole proprietorship.",
    "years_in_business": "How long the company has operated. Short histories can reduce verification depth.",
    "employees": "Reported employee count, used to compare company scale with revenue and requested exposure.",
    "requested_amount": "Loan principal requested by the applicant.",
    "term_months": "Requested duration of the loan in months.",
    "interest_rate": "Offered annual interest rate used to estimate debt service, interest expense, and DSCR stress.",
    "collateral_ratio": "Estimated collateral value divided by requested loan amount.",
    "existing_debt": "Reported outstanding business debt at application date.",
    "num_recent_loans": "Number of recent loans in the last 12 months. High values can indicate credit stacking.",
    "annual_revenue": "Reported yearly business revenue.",
    "free_cash_flow": "Annual cash generated after operating and investment needs.",
    "monthly_burn_rate": "Estimated monthly cash consumption at application date.",
    "expected_runway_months": "Estimated months the applicant can sustain current burn with available cash.",
    "cash_flow_to_revenue_ratio": "Free cash flow divided by annual revenue, calculated automatically.",
    "late_payment_ratio": "Share of observed payments that were late in the transaction profile.",
    "suspicious_transfer_ratio": "Share of transfers flagged as unusual in the transaction profile.",
    "country_risk_score": "Jurisdictional risk score from 0 to 1.",
    "forecast_revenue_cagr": "Expected average annual revenue growth over the next five years.",
    "forecast_employee_cagr": "Expected average annual employee growth over the next five years.",
    "forecast_fcf_margin_year5": "Target free-cash-flow margin by year five.",
    "planned_debt_reduction_pct": "Planned reduction in existing debt over the five-year forecast horizon.",
    "forecast_plan_confidence_score": "Banker-assessed confidence in the applicant's five-year plan from 0 to 1.",
    "current_ratio": "Current assets divided by current liabilities; lower values can signal liquidity pressure.",
    "quick_ratio": "Liquid assets divided by current liabilities; excludes inventory-heavy support.",
    "receivables_days": "Estimated days sales remain outstanding before collection.",
    "payables_days": "Estimated days the applicant takes to pay suppliers.",
    "inventory_days": "Estimated days inventory remains before sale or use.",
    "financial_statements_uploaded": "Whether financial statements are already present in the application package.",
    "bank_statements_uploaded": "Whether bank statements are already present in the application package.",
    "tax_return_uploaded": "Whether recent tax documentation is already present in the application package.",
    "ownership_docs_uploaded": "Whether ownership and KYB documentation is already present in the application package.",
    "forecast_support_uploaded": "Whether supporting material for the five-year plan is already present.",
    "document_edit_count": "Number of observed edits or resubmissions after initial intake.",
    "late_stage_change_count": "Number of changes made late in the review process.",
    "process_deviation_score": "Score for unusual workflow or process deviations from 0 to 1.",
    "email_domain_age_months": "Estimated age of the applicant email domain in months.",
    "website_age_months": "Estimated age of the applicant website in months.",
    "bank_account_age_months": "Estimated age of the primary business bank account in months.",
    "location_mismatch_score": "Score for mismatch between stated location, bank, website, or application metadata.",
    "duplicate_contact_score": "Score for shared or duplicate contact details across applications.",
    "related_party_exposure_score": "Score for related-party or ownership complexity.",
    "counterparty_concentration_score": "Score for revenue or payment concentration in a small counterparty set.",
    "shared_identifier_score": "Score for shared bank, address, phone, or owner identifiers.",
    "narrative_contradiction_score": "Score for detected contradictions between applicant text and observed evidence.",
    "loan_purpose_context": "Applicant-provided reason for the loan and intended use of funds.",
    "current_business_context": "Applicant-provided context for current operating conditions, recent performance, and key constraints.",
    "future_business_context": "Applicant-provided context for expected changes after funding, outside the formal five-year forecast table.",
    "ceo_context": "CEO narrative context for strategy, market demand, and growth plan.",
    "cfo_context": "CFO narrative context for liquidity, debt, cash flow, and funding need.",
    "coo_context": "COO narrative context for operations, capacity, staffing, and execution risk.",
}


def _scenario_value(scenario, key, default):
    active_values = st.session_state.get("active_queue_application") or {}
    if key in active_values and pd.notna(active_values.get(key)):
        return active_values.get(key)
    values = DEMO_SCENARIOS.get(scenario) or {}
    return values.get(key, default)


def _clear_scored_case():
    st.session_state.last_application = None
    st.session_state.last_prediction = None
    st.session_state.last_explanation = None
    st.session_state.last_review = None
    st.session_state.last_email_link = None
    st.session_state.show_review_dialog = False


def _activate_intake_case(application, source):
    st.session_state.active_queue_application = dict(application)
    st.session_state.active_intake_source = source
    st.session_state.loan_example_scenario = "Custom application"
    _clear_scored_case()
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun:
        rerun()


def _clear_active_intake_case():
    st.session_state.active_queue_application = None
    st.session_state.active_intake_source = "Manual entry"
    _clear_scored_case()
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun:
        rerun()


def _example_application(scenario_name):
    values = dict(DEMO_SCENARIOS.get(scenario_name) or {})
    values["application_id"] = "DEMO-A2M-001" if scenario_name == "A2M Logistics Loan" else f"DEMO-{scenario_name[:8].upper()}"
    values["company_name"] = "A2M Logistics" if scenario_name == "A2M Logistics Loan" else scenario_name
    return values


def _money(value):
    return format_currency(value)


def _ratio(value):
    return format_percent(value)


def _score(value):
    return format_score(value)


def _days(value):
    return f"{format_integer(value)} d"


def _yes_no(value):
    return "Yes" if float(value or 0) >= 0.5 else "No"


def _risk_tone(probability):
    if probability >= 0.58:
        return "high"
    if probability >= 0.28:
        return "medium"
    return "low"


def _risk_label(probability):
    if probability >= 0.58:
        return "High risk"
    if probability >= 0.28:
        return "Moderate risk"
    return "Lower risk"


def _decision_tone(decision):
    normalized = str(decision or "").lower()
    if "approve" in normalized:
        return "approve"
    if "reject" in normalized:
        return "reject"
    if "pending" in normalized:
        return "pending"
    return "review"


def _missing_documents(application):
    document_fields = [
        ("financial_statements_uploaded", "financial statements"),
        ("bank_statements_uploaded", "bank statements"),
        ("tax_return_uploaded", "tax return"),
        ("ownership_docs_uploaded", "ownership/KYB"),
        ("forecast_support_uploaded", "forecast support"),
    ]
    return [label for key, label in document_fields if float(application.get(key, 0) or 0) < 0.5]


def _readiness_status(score):
    if score >= 0.8:
        return "Ready"
    if score >= 0.5:
        return "Partial"
    return "Needs review"


def _data_readiness_rows(application, signals):
    missing_documents = _missing_documents(application)
    document_score = float(signals.get("document_completeness_score", 0) or 0)
    context_status = _context_completeness(application)
    context_score = {"Complete": 1.0, "Partial": 0.6, "Missing": 0.0}.get(context_status, 0.0)
    management_notes = [
        label
        for key, label in [
            ("loan_purpose_context", "loan purpose"),
            ("current_business_context", "current business context"),
            ("future_business_context", "future business context"),
            ("ceo_context", "CEO note"),
            ("cfo_context", "CFO note"),
            ("coo_context", "COO note"),
        ]
        if str(application.get(key, "")).strip()
    ]
    management_coverage = ", ".join(management_notes) if management_notes else "No applicant or management narrative provided"
    forecast_score = (
        0.45 * float(application.get("forecast_support_uploaded", 0) or 0)
        + 0.35 * float(application.get("forecast_plan_confidence_score", 0) or 0)
        + 0.20
    )
    accounting_score = (
        0.45 * float(application.get("financial_statements_uploaded", 0) or 0)
        + 0.35 * float(application.get("tax_return_uploaded", 0) or 0)
        + 0.20 * min(max(float(application.get("current_ratio", 0) or 0) / 2, 0), 1)
    )
    registry_score = (
        0.45 * float(application.get("ownership_docs_uploaded", 0) or 0)
        + 0.25 * min(float(application.get("email_domain_age_months", 0) or 0) / 24, 1)
        + 0.20 * min(float(application.get("website_age_months", 0) or 0) / 24, 1)
        + 0.10 * (1 - float(application.get("location_mismatch_score", 0) or 0))
    )
    banking_score = (
        0.65 * float(application.get("bank_statements_uploaded", 0) or 0)
        + 0.25 * min(float(application.get("bank_account_age_months", 0) or 0) / 24, 1)
        + 0.10 * (1 - float(application.get("process_deviation_score", 0) or 0))
    )

    return [
        {
            "Source": "PSD2 / Open Banking",
            "Readiness": _readiness_status(banking_score),
            "Evidence coverage": (
                f"Connected bank-account history: {format_months(application.get('bank_account_age_months', 0))}. "
                f"Bank statements received: {_yes_no(application.get('bank_statements_uploaded', 0))}."
            ),
            "Decision use": "Confirms cash inflows/outflows and flags payment or transfer anomalies.",
        },
        {
            "Source": "Accounting data",
            "Readiness": _readiness_status(accounting_score),
            "Evidence coverage": (
                f"Financial statements received: {_yes_no(application.get('financial_statements_uploaded', 0))}. "
                f"Tax return received: {_yes_no(application.get('tax_return_uploaded', 0))}. "
                f"Current ratio: {_score(application.get('current_ratio', 0))}; quick ratio: {_score(application.get('quick_ratio', 0))}."
            ),
            "Decision use": "Checks liquidity and whether free cash flow can cover estimated debt service.",
        },
        {
            "Source": "Document package",
            "Readiness": _readiness_status(document_score),
            "Evidence coverage": "All expected documents received." if not missing_documents else f"Missing required evidence: {', '.join(missing_documents)}.",
            "Decision use": "Determines whether the file is complete enough to support a credit decision.",
        },
        {
            "Source": "Registry / KYB",
            "Readiness": _readiness_status(registry_score),
            "Evidence coverage": (
                f"Ownership/KYB documents received: {_yes_no(application.get('ownership_docs_uploaded', 0))}. "
                f"Email domain age: {format_months(application.get('email_domain_age_months', 0))}; "
                f"website age: {format_months(application.get('website_age_months', 0))}. "
                f"Location mismatch risk score: {_score(application.get('location_mismatch_score', 0))} / {_score(1)}."
            ),
            "Decision use": "Supports identity, ownership, related-party, and location consistency checks.",
        },
        {
            "Source": "Management narrative",
            "Readiness": _readiness_status(context_score),
            "Evidence coverage": f"Narrative completeness: {context_status}. Provided context: {management_coverage}.",
            "Decision use": "Compares the applicant story with financial evidence and flags contradictions.",
        },
        {
            "Source": "Five-year plan",
            "Readiness": _readiness_status(forecast_score),
            "Evidence coverage": (
                f"Forecast support document received: {_yes_no(application.get('forecast_support_uploaded', 0))}. "
                f"Banker confidence score: {_score(application.get('forecast_plan_confidence_score', 0))} / {_score(1)}."
            ),
            "Decision use": "Assesses growth realism, free-cash-flow margin, debt reduction, and execution risk.",
        },
    ]


def _decision_conditions(application, prediction, signals):
    conditions = []
    missing_documents = _missing_documents(application)
    if missing_documents:
        conditions.append(f"Collect or validate missing items: {', '.join(missing_documents)}.")
    if float(signals.get("stressed_debt_service_coverage_ratio", 0) or 0) < 1.1:
        conditions.append("Review debt-service coverage under the +2% interest-rate stress case.")
    if float(signals.get("document_quality_risk_score", 0) or 0) >= 0.35:
        conditions.append("Confirm document edits and late-stage changes before release.")
    if float(signals.get("narrative_consistency_risk_score", 0) or 0) >= 0.4:
        conditions.append("Resolve narrative contradictions against financial and document evidence.")
    for flag in prediction.get("flags", [])[:2]:
        if flag not in conditions:
            conditions.append(flag)
    if not conditions:
        conditions.append("No extra conditions flagged beyond standard credit covenants.")
    return conditions[:4]


def _decision_copy(application, prediction, review, signals):
    decision = review["final_decision"] if review else "Pending Review"
    if review:
        base = (
            f"{review['action']} saved by the analyst at {review['timestamp']}. "
            f"The final grade is {prediction['grade']} with an application risk score of {_ratio(prediction['fraud_probability'])}."
        )
        if prediction.get("manual_adjustment"):
            base += f" Manual score adjustment is logged for supervisor review via {review.get('supervisor_email', 'the review mailbox')}."
        return base
    return (
        f"Model recommends {prediction['decision']} at grade {prediction['grade']} "
        f"with a {_risk_label(prediction['fraud_probability']).lower()} profile. Analyst decision is still pending."
    )


def _summary_table(rows):
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def _parse_money(label, raw_value, errors, min_value=None, max_value=None):
    try:
        value = parse_eu_number(raw_value)
    except ValueError:
        errors.append(f"{label} must be a valid amount, for example €1.000.000,00.")
        return 0
    if min_value is not None and value < min_value:
        errors.append(f"{label} must be at least {format_currency_input(min_value)}.")
    if max_value is not None and value > max_value:
        errors.append(f"{label} must be no more than {format_currency_input(max_value)}.")
    return value


def _preview_money(raw_value, default):
    try:
        return parse_eu_number(raw_value)
    except ValueError:
        return float(default)


def _context_completeness(application):
    fields = ["loan_purpose_context", "current_business_context", "future_business_context"]
    completed = sum(bool(str(application.get(field, "")).strip()) for field in fields)
    if completed == len(fields):
        return "Complete"
    if completed:
        return "Partial"
    return "Missing"


def _rerun_after_review():
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun:
        rerun()
    st.success("Review saved to the case audit trail.")


def _store_prediction(application, prediction, explanation):
    st.session_state.last_application = application
    st.session_state.last_prediction = prediction
    st.session_state.last_explanation = explanation
    st.session_state.last_review = None
    st.session_state.last_email_link = None
    st.session_state.portfolio_history.append({**application, **prediction, "review_action": "Pending", "final_decision": "Pending Review"})


def _update_latest_history(prediction, review):
    application_id = st.session_state.last_application.get("application_id")
    for row in reversed(st.session_state.portfolio_history):
        if row.get("application_id") == application_id:
            row.update(
                {
                    "fraud_probability": prediction["fraud_probability"],
                    "grade": prediction["grade"],
                    "decision": prediction["decision"],
                    "manual_adjustment": prediction.get("manual_adjustment", False),
                    "review_action": review["action"],
                    "final_decision": review["final_decision"],
                    "supervisor_email": review["supervisor_email"],
                }
            )
            break


def _review_form_body():
    application = st.session_state.last_application
    prediction = st.session_state.last_prediction
    explanation = st.session_state.last_explanation
    current_probability = float(prediction["fraud_probability"])

    with st.form("case_review_form"):
        action = st.selectbox("Analyst action", REVIEW_ACTIONS)
        supervisor_email = st.text_input("Supervisor or review mailbox", value="supervisor@example.com")
        send_email = st.checkbox("Prepare email with case analysis", value=True)
        analyst_note = st.text_area(
            "Analyst note",
            value="Reviewed model score, deterministic flags, and explanation. Pending supervisor sign-off where required.",
        )

        manual_allowed = action in {"Approve", "Reject"}
        manual_approved = False
        manual_probability = current_probability
        if manual_allowed:
            manual_approved = st.checkbox("Supervisor approved manual score adjustment")
            if manual_approved:
                manual_probability = st.slider(
                    "Manual-adjust application risk score",
                    min_value=0.0,
                    max_value=1.0,
                    value=current_probability,
                    step=0.01,
                )
        else:
            st.caption("Manual score adjustment is only available for approve/reject review outcomes.")

        submitted = st.form_submit_button("Save Review", width="stretch")

    if submitted:
        final_prediction = prediction
        if manual_allowed and manual_approved:
            if not supervisor_email:
                st.error("Supervisor email is required for manual score adjustments.")
                return
            final_prediction = adjusted_prediction(prediction, manual_probability)
            explanation = explain_prediction(
                application,
                final_prediction,
                use_llm=False,
            )
            st.session_state.last_prediction = final_prediction
            st.session_state.last_explanation = explanation

        review = {
            "review_id": f"REV-{len(st.session_state.review_history) + 1:03d}",
            "application_id": application["application_id"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "supervisor_email": supervisor_email,
            "send_email": send_email,
            "analyst_note": analyst_note,
            "manual_adjustment": bool(final_prediction.get("manual_adjustment", False)),
            "final_probability": final_prediction["fraud_probability"],
            "final_grade": final_prediction["grade"],
            "model_recommendation": final_prediction["decision"],
            "final_decision": action,
        }
        st.session_state.last_review = review
        st.session_state.review_history.append(review)
        _update_latest_history(final_prediction, review)

        st.session_state.last_email_link = None
        if send_email:
            summary = case_summary(application, final_prediction, explanation, review)
            link = mailto_link(
                supervisor_email,
                f"Review required: {application['application_id']} grade {final_prediction['grade']}",
                summary,
            )
            st.session_state.last_email_link = link
        _rerun_after_review()


if hasattr(st, "dialog"):

    @st.dialog("Case Review")
    def _review_dialog():
        _review_form_body()


header_left, header_right = st.columns([3, 1])
with header_left:
    st.title("Personal Workspace")
    st.caption("Live analyst workspace for Ms. Cooper's current SME lending tasks.")
with header_right:
    st.metric("Active analyst", "Ms. Cooper")

st.subheader("Current Tasks")
queue = build_application_queue(st.session_state.model_bundle, applications)
queue_mine = queue[queue["assigned_analyst"].eq("Ms. Cooper")].copy()
if queue_mine.empty:
    queue_mine = queue.head(12).copy()

queue_metrics = st.columns(4)
queue_metrics[0].metric("Assigned to Ms. Cooper", format_integer(len(queue_mine)))
queue_metrics[1].metric("Same-day SLA", format_integer((queue_mine["sla"] == "Same day").sum()))
queue_metrics[2].metric("Manual / Compliance", format_integer(queue_mine["queue_status"].isin(["Manual review", "Compliance review"]).sum()))
queue_metrics[3].metric("Missing Docs", format_integer((queue_mine["missing_documents"] > 0).sum()))

queue_display = queue_mine[
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
].head(8).copy()
queue_display["requested_amount"] = queue_display["requested_amount"].apply(_money)
queue_display["fraud_probability"] = queue_display["fraud_probability"].apply(_ratio)
queue_display = queue_display.rename(
    columns={
        "application_id": "Application ID",
        "company_name": "Company",
        "requested_amount": "Requested amount",
        "fraud_probability": "Application risk score",
        "grade": "Grade",
        "queue_status": "Task status",
        "missing_documents": "Missing docs",
        "sla": "SLA",
    }
)

with st.container():
    st.markdown(
        """
            <div class="queue-panel">
            <div class="queue-panel-title">Start Work From Current Tasks</div>
            <div class="queue-panel-copy">Select an assigned case, start the review, and the working file below loads with the applicant data already present.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(queue_display, width="stretch", hide_index=True)
    queue_labels = [
        f"{row.application_id} - {row.company_name} | Grade {row.grade} | {row.queue_status}"
        for row in queue_mine.head(20).itertuples()
    ]
    queue_pick = st.selectbox("Next application", queue_labels)
    selected_application_id = queue_pick.split(" - ", 1)[0]
    selected_queue_row = queue_mine[queue_mine["application_id"] == selected_application_id].iloc[0].to_dict()
    queue_actions = st.columns([1, 1, 1, 2])
    if queue_actions[0].button("Start Selected Case", width="stretch"):
        _activate_intake_case(selected_queue_row, "Current tasks")
    if queue_actions[1].button("Start A2M Example Case", width="stretch"):
        _activate_intake_case(_example_application("A2M Logistics Loan"), "Example case")
    if queue_actions[2].button("Manual Entry", width="stretch"):
        _clear_active_intake_case()

active_case = st.session_state.get("active_queue_application")
if active_case:
    st.markdown(
        f"""
        <div class="active-case-card">
            <div class="active-case-title">Active intake: {escape(str(active_case.get("application_id", "Session")))} - {escape(str(active_case.get("company_name", "Applicant")))}</div>
            <div class="active-case-copy">Source: {escape(st.session_state.get("active_intake_source", "Manual entry"))}. Applicant data is loaded into the working file below; Ms. Cooper can adjust fields before scoring.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("No active workspace case yet. Start a task above or use Manual Entry to build a custom applicant.")

with st.expander("Example Cases", expanded=False):
    scenario = st.selectbox("Case example", list(DEMO_SCENARIOS.keys()), key="loan_example_scenario")
    if st.button("Load selected example", width="stretch"):
        if scenario == "Custom application":
            _clear_active_intake_case()
        else:
            _activate_intake_case(_example_application(scenario), "Example case")

scenario_values = DEMO_SCENARIOS.get(scenario) or {}
company_name_default = _scenario_value(
    scenario,
    "company_name",
    "Session Applicant" if scenario == "Custom application" else scenario,
)

with st.form("loan_intake_form"):
    st.subheader("Company Profile")
    profile_left, profile_right = st.columns(2)
    with profile_left:
        company_name = st.text_input(
            "Company name",
            value=company_name_default,
            help=FIELD_HELP["company_name"],
        )
        industry_default = _scenario_value(scenario, "industry", "Construction")
        region_default = _scenario_value(scenario, "region", regions[0])
        type_default = _scenario_value(scenario, "company_type", company_types[0])
        industry = st.selectbox(
            "Industry",
            industries,
            index=industries.index(industry_default) if industry_default in industries else 0,
            help=FIELD_HELP["industry"],
        )
        region = st.selectbox(
            "Region",
            regions,
            index=regions.index(region_default) if region_default in regions else 0,
            help=FIELD_HELP["region"],
        )
    with profile_right:
        company_type = st.selectbox(
            "Company type",
            company_types,
            index=company_types.index(type_default) if type_default in company_types else 0,
            help=FIELD_HELP["company_type"],
        )
        years_in_business = st.number_input(
            "Years in business",
            min_value=0.0,
            max_value=75.0,
            value=float(_scenario_value(scenario, "years_in_business", 4.0)),
            step=0.5,
            help=FIELD_HELP["years_in_business"],
        )
        employees = st.number_input(
            "Employees",
            min_value=1,
            max_value=10000,
            value=int(_scenario_value(scenario, "employees", 42)),
            step=1,
            help=FIELD_HELP["employees"],
        )

    st.subheader("Loan Request")
    loan_left, loan_right = st.columns(2)
    with loan_left:
        requested_amount_default = int(_scenario_value(scenario, "requested_amount", 350000))
        requested_amount_text = st.text_input(
            "Requested amount",
            value=format_currency_input(requested_amount_default),
            help=FIELD_HELP["requested_amount"],
        )
        term_months = st.slider(
            "Term months",
            min_value=6,
            max_value=84,
            value=int(_scenario_value(scenario, "term_months", 36)),
            step=6,
            help=FIELD_HELP["term_months"],
        )
        interest_rate_pct = st.slider(
            "Interest rate",
            min_value=0.0,
            max_value=30.0,
            value=float(_scenario_value(scenario, "interest_rate", 0.085)) * 100,
            step=0.25,
            format="%.2f%%",
            help=FIELD_HELP["interest_rate"],
        )
        collateral_ratio = st.slider(
            "Collateral coverage",
            min_value=0.0,
            max_value=2.0,
            value=float(_scenario_value(scenario, "collateral_ratio", 0.65)),
            step=0.05,
            help=FIELD_HELP["collateral_ratio"],
        )
    with loan_right:
        existing_debt_default = int(_scenario_value(scenario, "existing_debt", 550000))
        existing_debt_text = st.text_input(
            "Existing debt",
            value=format_currency_input(existing_debt_default),
            help=FIELD_HELP["existing_debt"],
        )
        num_recent_loans = st.slider(
            "Recent loans in the last 12 months",
            min_value=0,
            max_value=12,
            value=int(_scenario_value(scenario, "num_recent_loans", 2)),
            help=FIELD_HELP["num_recent_loans"],
        )

    st.subheader("Financial Snapshot")
    financial_left, financial_right = st.columns(2)
    with financial_left:
        annual_revenue_default = int(_scenario_value(scenario, "annual_revenue", 1800000))
        annual_revenue_text = st.text_input(
            "Annual revenue",
            value=format_currency_input(annual_revenue_default),
            help=FIELD_HELP["annual_revenue"],
        )
        free_cash_flow_default = int(_scenario_value(scenario, "free_cash_flow", 120000))
        free_cash_flow_text = st.text_input(
            "Free cash flow",
            value=format_currency_input(free_cash_flow_default),
            help=FIELD_HELP["free_cash_flow"],
        )
    with financial_right:
        monthly_burn_rate_default = int(_scenario_value(scenario, "monthly_burn_rate", 25000))
        monthly_burn_rate_text = st.text_input(
            "Monthly burn rate",
            value=format_currency_input(monthly_burn_rate_default),
            help=FIELD_HELP["monthly_burn_rate"],
        )
        expected_runway_months = st.slider(
            "Expected runway months",
            min_value=0,
            max_value=60,
            value=int(_scenario_value(scenario, "expected_runway_months", 18)),
            step=1,
            help=FIELD_HELP["expected_runway_months"],
        )
        annual_revenue_preview = _preview_money(annual_revenue_text, annual_revenue_default)
        free_cash_flow_preview = _preview_money(free_cash_flow_text, free_cash_flow_default)
        cash_flow_to_revenue_ratio = free_cash_flow_preview / max(float(annual_revenue_preview), 1)
        st.metric("Cash flow / revenue", _ratio(cash_flow_to_revenue_ratio), help=FIELD_HELP["cash_flow_to_revenue_ratio"])

    with st.expander("Working Capital Ratios", expanded=False):
        wc_first, wc_second, wc_third, wc_fourth, wc_fifth = st.columns(5)
        with wc_first:
            current_ratio = st.slider(
                "Current ratio",
                min_value=0.0,
                max_value=5.0,
                value=float(_scenario_value(scenario, "current_ratio", 1.45)),
                step=0.05,
                format="%.2f",
                help=FIELD_HELP["current_ratio"],
            )
        with wc_second:
            quick_ratio = st.slider(
                "Quick ratio",
                min_value=0.0,
                max_value=4.0,
                value=float(_scenario_value(scenario, "quick_ratio", 1.05)),
                step=0.05,
                format="%.2f",
                help=FIELD_HELP["quick_ratio"],
            )
        with wc_third:
            receivables_days = st.slider(
                "Receivables days",
                min_value=0,
                max_value=180,
                value=int(_scenario_value(scenario, "receivables_days", 48)),
                help=FIELD_HELP["receivables_days"],
            )
        with wc_fourth:
            payables_days = st.slider(
                "Payables days",
                min_value=0,
                max_value=180,
                value=int(_scenario_value(scenario, "payables_days", 44)),
                help=FIELD_HELP["payables_days"],
            )
        with wc_fifth:
            inventory_days = st.slider(
                "Inventory days",
                min_value=0,
                max_value=220,
                value=int(_scenario_value(scenario, "inventory_days", 35)),
                help=FIELD_HELP["inventory_days"],
            )

    st.subheader("Five-Year Plan")
    plan_left, plan_right = st.columns(2)
    with plan_left:
        forecast_revenue_cagr = st.slider(
            "Expected annual revenue growth",
            min_value=-0.20,
            max_value=0.60,
            value=float(_scenario_value(scenario, "forecast_revenue_cagr", 0.08)),
            step=0.01,
            format="%.2f",
            help=FIELD_HELP["forecast_revenue_cagr"],
        )
        forecast_employee_cagr = st.slider(
            "Expected annual employee growth",
            min_value=-0.10,
            max_value=0.50,
            value=float(_scenario_value(scenario, "forecast_employee_cagr", 0.04)),
            step=0.01,
            format="%.2f",
            help=FIELD_HELP["forecast_employee_cagr"],
        )
        forecast_fcf_margin_year5 = st.slider(
            "Year 5 FCF margin target",
            min_value=-0.25,
            max_value=0.35,
            value=float(_scenario_value(scenario, "forecast_fcf_margin_year5", 0.08)),
            step=0.01,
            format="%.2f",
            help=FIELD_HELP["forecast_fcf_margin_year5"],
        )
    with plan_right:
        planned_debt_reduction_pct = st.slider(
            "Planned debt reduction",
            min_value=0.0,
            max_value=1.0,
            value=float(_scenario_value(scenario, "planned_debt_reduction_pct", 0.20)),
            step=0.05,
            format="%.2f",
            help=FIELD_HELP["planned_debt_reduction_pct"],
        )
        forecast_plan_confidence_score = st.slider(
            "Plan confidence score",
            min_value=0.0,
            max_value=1.0,
            value=float(_scenario_value(scenario, "forecast_plan_confidence_score", 0.55)),
            step=0.05,
            format="%.2f",
            help=FIELD_HELP["forecast_plan_confidence_score"],
        )

    st.subheader("Applicant Narrative")
    narrative_left, narrative_middle, narrative_right = st.columns(3)
    with narrative_left:
        loan_purpose_context = st.text_area(
            "Loan purpose",
            value=_scenario_value(scenario, "loan_purpose_context", ""),
            height=120,
            help=FIELD_HELP["loan_purpose_context"],
        )
    with narrative_middle:
        current_business_context = st.text_area(
            "Current business context",
            value=_scenario_value(scenario, "current_business_context", ""),
            height=120,
            help=FIELD_HELP["current_business_context"],
        )
    with narrative_right:
        future_business_context = st.text_area(
            "Future business context",
            value=_scenario_value(scenario, "future_business_context", ""),
            height=120,
            help=FIELD_HELP["future_business_context"],
        )

    st.subheader("Executive Context")
    context_left, context_middle, context_right = st.columns(3)
    with context_left:
        ceo_context = st.text_area(
            "CEO context",
            value=_scenario_value(scenario, "ceo_context", ""),
            height=110,
            help=FIELD_HELP["ceo_context"],
        )
    with context_middle:
        cfo_context = st.text_area(
            "CFO context",
            value=_scenario_value(scenario, "cfo_context", ""),
            height=110,
            help=FIELD_HELP["cfo_context"],
        )
    with context_right:
        coo_context = st.text_area(
            "COO context",
            value=_scenario_value(scenario, "coo_context", ""),
            height=110,
            help=FIELD_HELP["coo_context"],
        )

    st.subheader("Document & Process Checks")
    doc_cols = st.columns(5)
    with doc_cols[0]:
        financial_statements_uploaded = st.checkbox(
            "Financial statements",
            value=bool(_scenario_value(scenario, "financial_statements_uploaded", 1)),
            help=FIELD_HELP["financial_statements_uploaded"],
        )
    with doc_cols[1]:
        bank_statements_uploaded = st.checkbox(
            "Bank statements",
            value=bool(_scenario_value(scenario, "bank_statements_uploaded", 1)),
            help=FIELD_HELP["bank_statements_uploaded"],
        )
    with doc_cols[2]:
        tax_return_uploaded = st.checkbox(
            "Tax return",
            value=bool(_scenario_value(scenario, "tax_return_uploaded", 1)),
            help=FIELD_HELP["tax_return_uploaded"],
        )
    with doc_cols[3]:
        ownership_docs_uploaded = st.checkbox(
            "Ownership/KYB",
            value=bool(_scenario_value(scenario, "ownership_docs_uploaded", 1)),
            help=FIELD_HELP["ownership_docs_uploaded"],
        )
    with doc_cols[4]:
        forecast_support_uploaded = st.checkbox(
            "Forecast support",
            value=bool(_scenario_value(scenario, "forecast_support_uploaded", 1)),
            help=FIELD_HELP["forecast_support_uploaded"],
        )

    with st.expander("Verification Metadata", expanded=False):
        verification_left, verification_middle, verification_right = st.columns(3)
        with verification_left:
            document_edit_count = st.slider(
                "Document edits",
                min_value=0,
                max_value=20,
                value=int(_scenario_value(scenario, "document_edit_count", 1)),
                help=FIELD_HELP["document_edit_count"],
            )
            late_stage_change_count = st.slider(
                "Late-stage changes",
                min_value=0,
                max_value=12,
                value=int(_scenario_value(scenario, "late_stage_change_count", 0)),
                help=FIELD_HELP["late_stage_change_count"],
            )
            process_deviation_score = st.slider(
                "Process deviation",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "process_deviation_score", 0.05)),
                step=0.01,
                format="%.2f",
                help=FIELD_HELP["process_deviation_score"],
            )
        with verification_middle:
            email_domain_age_months = st.slider(
                "Email domain age",
                min_value=0,
                max_value=240,
                value=int(_scenario_value(scenario, "email_domain_age_months", 36)),
                help=FIELD_HELP["email_domain_age_months"],
            )
            website_age_months = st.slider(
                "Website age",
                min_value=0,
                max_value=240,
                value=int(_scenario_value(scenario, "website_age_months", 36)),
                help=FIELD_HELP["website_age_months"],
            )
            bank_account_age_months = st.slider(
                "Bank account age",
                min_value=0,
                max_value=180,
                value=int(_scenario_value(scenario, "bank_account_age_months", 24)),
                help=FIELD_HELP["bank_account_age_months"],
            )
        with verification_right:
            location_mismatch_score = st.slider(
                "Location mismatch",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "location_mismatch_score", 0.05)),
                step=0.01,
                format="%.2f",
                help=FIELD_HELP["location_mismatch_score"],
            )
            duplicate_contact_score = st.slider(
                "Duplicate contact",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "duplicate_contact_score", 0.02)),
                step=0.01,
                format="%.2f",
                help=FIELD_HELP["duplicate_contact_score"],
            )
            related_party_exposure_score = st.slider(
                "Related-party exposure",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "related_party_exposure_score", 0.05)),
                step=0.01,
                format="%.2f",
                help=FIELD_HELP["related_party_exposure_score"],
            )
            counterparty_concentration_score = st.slider(
                "Counterparty concentration",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "counterparty_concentration_score", 0.20)),
                step=0.01,
                format="%.2f",
                help=FIELD_HELP["counterparty_concentration_score"],
            )
            shared_identifier_score = st.slider(
                "Shared identifier",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "shared_identifier_score", 0.02)),
                step=0.01,
                format="%.2f",
                help=FIELD_HELP["shared_identifier_score"],
            )
            narrative_contradiction_score = st.slider(
                "Narrative contradiction",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "narrative_contradiction_score", 0.05)),
                step=0.01,
                format="%.2f",
                help=FIELD_HELP["narrative_contradiction_score"],
            )

    with st.expander("Advanced Signals", expanded=False):
        signal_left, signal_right, signal_third = st.columns(3)
        with signal_left:
            late_payment_ratio = st.slider(
                "Late payment ratio",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "late_payment_ratio", 0.12)),
                step=0.01,
                help=FIELD_HELP["late_payment_ratio"],
            )
        with signal_right:
            suspicious_transfer_ratio = st.slider(
                "Suspicious transfer ratio",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "suspicious_transfer_ratio", 0.08)),
                step=0.01,
                help=FIELD_HELP["suspicious_transfer_ratio"],
            )
        with signal_third:
            country_risk_score = st.slider(
                "Country risk score",
                min_value=0.0,
                max_value=1.0,
                value=float(_scenario_value(scenario, "country_risk_score", 0.25)),
                step=0.01,
                help=FIELD_HELP["country_risk_score"],
            )

    submitted = st.form_submit_button("Score Application", width="stretch")

if submitted:
    errors = []
    active_application_id = None
    if st.session_state.get("active_queue_application"):
        active_application_id = st.session_state.active_queue_application.get("application_id")
    requested_amount = _parse_money("Requested amount", requested_amount_text, errors, 10000, 5000000)
    annual_revenue = _parse_money("Annual revenue", annual_revenue_text, errors, 50000, 50000000)
    existing_debt = _parse_money("Existing debt", existing_debt_text, errors, 0, 20000000)
    free_cash_flow = _parse_money("Free cash flow", free_cash_flow_text, errors, -20000000, 50000000)
    monthly_burn_rate = _parse_money("Monthly burn rate", monthly_burn_rate_text, errors, 0, 5000000)
    interest_rate = interest_rate_pct / 100
    cash_flow_to_revenue_ratio = free_cash_flow / max(float(annual_revenue), 1)

    if errors:
        st.error(" ".join(errors))
    else:
        application = {
            "application_id": active_application_id or f"SESSION-{len(st.session_state.portfolio_history) + 1:03d}",
            "company_name": company_name or "Session Applicant",
            "industry": industry,
            "region": region,
            "company_type": company_type,
            "requested_amount": requested_amount,
            "term_months": term_months,
            "interest_rate": interest_rate,
            "annual_revenue": annual_revenue,
            "years_in_business": years_in_business,
            "existing_debt": existing_debt,
            "num_recent_loans": num_recent_loans,
            "late_payment_ratio": late_payment_ratio,
            "suspicious_transfer_ratio": suspicious_transfer_ratio,
            "collateral_ratio": collateral_ratio,
            "employees": employees,
            "country_risk_score": country_risk_score,
            "free_cash_flow": free_cash_flow,
            "monthly_burn_rate": monthly_burn_rate,
            "cash_flow_to_revenue_ratio": cash_flow_to_revenue_ratio,
            "expected_runway_months": expected_runway_months,
            "forecast_revenue_cagr": forecast_revenue_cagr,
            "forecast_employee_cagr": forecast_employee_cagr,
            "forecast_fcf_margin_year5": forecast_fcf_margin_year5,
            "planned_debt_reduction_pct": planned_debt_reduction_pct,
            "forecast_plan_confidence_score": forecast_plan_confidence_score,
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "receivables_days": receivables_days,
            "payables_days": payables_days,
            "inventory_days": inventory_days,
            "financial_statements_uploaded": int(financial_statements_uploaded),
            "bank_statements_uploaded": int(bank_statements_uploaded),
            "tax_return_uploaded": int(tax_return_uploaded),
            "ownership_docs_uploaded": int(ownership_docs_uploaded),
            "forecast_support_uploaded": int(forecast_support_uploaded),
            "document_edit_count": document_edit_count,
            "late_stage_change_count": late_stage_change_count,
            "process_deviation_score": process_deviation_score,
            "email_domain_age_months": email_domain_age_months,
            "website_age_months": website_age_months,
            "bank_account_age_months": bank_account_age_months,
            "location_mismatch_score": location_mismatch_score,
            "duplicate_contact_score": duplicate_contact_score,
            "related_party_exposure_score": related_party_exposure_score,
            "counterparty_concentration_score": counterparty_concentration_score,
            "shared_identifier_score": shared_identifier_score,
            "narrative_contradiction_score": narrative_contradiction_score,
            "loan_purpose_context": loan_purpose_context,
            "current_business_context": current_business_context,
            "future_business_context": future_business_context,
            "ceo_context": ceo_context,
            "cfo_context": cfo_context,
            "coo_context": coo_context,
        }
        prediction = st.session_state.model_bundle.score_one(application)
        explanation = explain_prediction(
            application,
            prediction,
            use_llm=False,
        )
        _store_prediction(application, prediction, explanation)

if st.session_state.last_prediction:
    application = st.session_state.last_application
    prediction = st.session_state.last_prediction
    explanation = st.session_state.last_explanation
    current_review = st.session_state.last_review
    if current_review and current_review.get("application_id") != application["application_id"]:
        current_review = None
    final_decision = current_review["final_decision"] if current_review else "Pending Review"
    calculated = add_derived_features(pd.DataFrame([application]))
    signals = calculated.iloc[0]
    risk_tone = _risk_tone(prediction["fraud_probability"])
    risk_label = _risk_label(prediction["fraud_probability"])
    decision_tone = _decision_tone(final_decision)
    review_status = current_review["timestamp"] if current_review else "Awaiting analyst"
    manual_status = "Manual score" if prediction.get("manual_adjustment") else "Model score"
    flag_count = len(prediction.get("flags", []))
    flag_label = f"{flag_count} elevated flag" if flag_count == 1 else f"{flag_count} elevated flags"
    decision_conditions = _decision_conditions(application, prediction, signals)
    condition_html = "".join(f"<li>{escape(condition)}</li>" for condition in decision_conditions)
    loan_terms = recommended_loan_terms(application, prediction, signals)
    monitoring_rows = portfolio_monitoring_preview(application, prediction, signals)
    timeline_rows = decision_timeline(application, prediction, current_review)
    driver_rows = grouped_risk_drivers(application, signals)
    confidence_rows = model_confidence_rows(st.session_state.model_bundle.metrics, prediction, signals)

    st.subheader("Score Output")
    st.markdown(
        f"""
        <div class="score-panel {risk_tone}">
            <div class="score-panel-header">
                <div>
                    <div class="score-label">Application risk score</div>
                    <div class="score-headline">{escape(_ratio(prediction["fraud_probability"]))}</div>
                    <div class="score-subtitle">{escape(risk_label)} profile with {escape(flag_label)}.</div>
                </div>
                <div class="decision-badge {decision_tone}">{escape(final_decision)}</div>
            </div>
            <div class="score-strip">
                <div class="score-item">
                    <div class="score-label">Risk grade</div>
                    <div class="score-value">{escape(prediction["grade"])}</div>
                </div>
                <div class="score-item">
                    <div class="score-label">Model recommendation</div>
                    <div class="score-value">{escape(prediction["decision"])}</div>
                </div>
                <div class="score-item">
                    <div class="score-label">Score source</div>
                    <div class="score-value">{escape(manual_status)}</div>
                </div>
                <div class="score-item">
                    <div class="score-label">Review status</div>
                    <div class="score-value">{escape(review_status)}</div>
                </div>
                <div class="score-item">
                    <div class="score-label">Stressed DSCR</div>
                    <div class="score-value">{escape(_score(signals["stressed_debt_service_coverage_ratio"]))}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="decision-panel {decision_tone}">
            <div class="decision-title">Final Decision: {escape(final_decision)}</div>
            <div class="decision-copy">{escape(_decision_copy(application, prediction, current_review, signals))}</div>
            <ul class="decision-list">{condition_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Decision Rationale")
    st.caption("Explanation source: deterministic analyst explanation. Open AI Explainability to run a local or hosted model.")
    st.info(explanation)

    terms_col, monitoring_col = st.columns(2)
    with terms_col:
        st.subheader("Recommended Loan Terms")
        st.dataframe(pd.DataFrame(loan_terms), width="stretch", hide_index=True)
    with monitoring_col:
        st.subheader("Portfolio Monitoring Preview")
        st.dataframe(pd.DataFrame(monitoring_rows), width="stretch", hide_index=True)

    st.subheader("Model Confidence and Governance")
    st.dataframe(pd.DataFrame(confidence_rows), width="stretch", hide_index=True)
    st.caption("Output is banker decision support. Manual adjustments, C-F grades, and exception cases remain subject to human review.")

    st.subheader("Data Readiness")
    source_badges = data_source_badges(application, signals)
    badge_html = "".join(
        f'<span class="source-badge {escape(badge["Tone"])}">{escape(badge["Source"])}: {escape(badge["Status"])}</span>'
        for badge in source_badges
    )
    st.markdown(f'<div class="badge-row">{badge_html}</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(_data_readiness_rows(application, signals)), width="stretch", hide_index=True)

    st.subheader("Risk Driver View")
    st.dataframe(pd.DataFrame(driver_rows), width="stretch", hide_index=True)

    snapshot_left, snapshot_middle, snapshot_right = st.columns(3)
    with snapshot_left:
        st.dataframe(
            _summary_table(
                [
                    ("Interest rate", _ratio(application.get("interest_rate", 0))),
                    ("Annual interest", _money(signals["annual_interest_expense"])),
                    ("Annual debt service", _money(signals["annual_debt_service"])),
                    ("DSCR", _score(signals["debt_service_coverage_ratio"])),
                    ("Stress DSCR (+2%)", _score(signals["stressed_debt_service_coverage_ratio"])),
                    ("Free cash flow", _money(application.get("free_cash_flow", 0))),
                    ("Monthly burn", _money(application.get("monthly_burn_rate", 0))),
                    ("Cash flow / revenue", _ratio(application.get("cash_flow_to_revenue_ratio", 0))),
                    ("Expected runway", format_months(application.get("expected_runway_months", 0))),
                    ("Current ratio", _score(application.get("current_ratio", 0))),
                    ("Quick ratio", _score(application.get("quick_ratio", 0))),
                    ("Cash conversion cycle", _days(signals["cash_conversion_cycle_days"])),
                ]
            ),
            width="stretch",
            hide_index=True,
        )
    with snapshot_middle:
        st.dataframe(
            _summary_table(
                [
                    ("Revenue CAGR", _ratio(application.get("forecast_revenue_cagr", 0))),
                    ("Employee CAGR", _ratio(application.get("forecast_employee_cagr", 0))),
                    ("Y5 FCF margin", _ratio(application.get("forecast_fcf_margin_year5", 0))),
                    ("Debt reduction", _ratio(application.get("planned_debt_reduction_pct", 0))),
                    ("Plan confidence", _score(application.get("forecast_plan_confidence_score", 0))),
                    ("Applicant narrative", _context_completeness(application)),
                    ("Statement anomaly", _score(signals["financial_statement_anomaly_score"])),
                ]
            ),
            width="stretch",
            hide_index=True,
        )
    with snapshot_right:
        st.dataframe(
            _summary_table(
                [
                    ("Document complete", _score(signals["document_completeness_score"])),
                    ("Document risk", _score(signals["document_quality_risk_score"])),
                    ("Process risk", _score(signals["process_integrity_risk_score"])),
                    ("Identity risk", _score(signals["identity_verification_risk_score"])),
                    ("Working capital risk", _score(signals["working_capital_pressure_score"])),
                    ("Network risk", _score(signals["related_party_network_risk_score"])),
                    ("Narrative risk", _score(signals["narrative_consistency_risk_score"])),
                ]
            ),
            width="stretch",
            hide_index=True,
        )

    forecast = build_forecast_table(pd.DataFrame([application]))
    display_forecast = forecast.rename(
        columns={
            "forecast_year": "Year",
            "projected_revenue": "Projected revenue",
            "projected_employees": "Projected employees",
            "projected_free_cash_flow": "Projected FCF",
            "projected_debt": "Projected debt",
        }
    )[["Year", "Projected revenue", "Projected employees", "Projected FCF", "Projected debt"]].copy()
    for column in ["Projected revenue", "Projected FCF", "Projected debt"]:
        display_forecast[column] = display_forecast[column].apply(_money)
    display_forecast["Projected employees"] = display_forecast["Projected employees"].apply(format_integer)
    with st.expander("Generated Five-Year Forecast", expanded=True):
        st.dataframe(display_forecast, width="stretch", hide_index=True)

    executive_rows = [
        {"Executive": "CEO", "Context": application.get("ceo_context", "")},
        {"Executive": "CFO", "Context": application.get("cfo_context", "")},
        {"Executive": "COO", "Context": application.get("coo_context", "")},
    ]
    executive_rows = [row for row in executive_rows if row["Context"]]
    if executive_rows:
        with st.expander("Executive Context", expanded=False):
            st.dataframe(executive_rows, width="stretch", hide_index=True)

    applicant_rows = [
        {"Context": "Loan purpose", "Applicant input": application.get("loan_purpose_context", "")},
        {"Context": "Current business", "Applicant input": application.get("current_business_context", "")},
        {"Context": "Future business", "Applicant input": application.get("future_business_context", "")},
    ]
    applicant_rows = [row for row in applicant_rows if row["Applicant input"]]
    if applicant_rows:
        with st.expander("Applicant Narrative", expanded=False):
            st.dataframe(applicant_rows, width="stretch", hide_index=True)

    document_rows = [
        {"Document": "Financial statements", "Present": _yes_no(application.get("financial_statements_uploaded", 0))},
        {"Document": "Bank statements", "Present": _yes_no(application.get("bank_statements_uploaded", 0))},
        {"Document": "Tax return", "Present": _yes_no(application.get("tax_return_uploaded", 0))},
        {"Document": "Ownership/KYB", "Present": _yes_no(application.get("ownership_docs_uploaded", 0))},
        {"Document": "Forecast support", "Present": _yes_no(application.get("forecast_support_uploaded", 0))},
    ]
    verification_rows = [
        {"Check": "Document edits", "Value": format_integer(application.get("document_edit_count", 0))},
        {"Check": "Late-stage changes", "Value": format_integer(application.get("late_stage_change_count", 0))},
        {"Check": "Process deviation", "Value": _score(application.get("process_deviation_score", 0))},
        {"Check": "Email domain age", "Value": format_months(application.get("email_domain_age_months", 0))},
        {"Check": "Website age", "Value": format_months(application.get("website_age_months", 0))},
        {"Check": "Bank account age", "Value": format_months(application.get("bank_account_age_months", 0))},
        {"Check": "Location mismatch", "Value": _score(application.get("location_mismatch_score", 0))},
        {"Check": "Duplicate contact", "Value": _score(application.get("duplicate_contact_score", 0))},
        {"Check": "Related-party exposure", "Value": _score(application.get("related_party_exposure_score", 0))},
        {"Check": "Counterparty concentration", "Value": _score(application.get("counterparty_concentration_score", 0))},
        {"Check": "Shared identifier", "Value": _score(application.get("shared_identifier_score", 0))},
        {"Check": "Narrative contradiction", "Value": _score(application.get("narrative_contradiction_score", 0))},
    ]
    with st.expander("Document & Verification Review", expanded=True):
        review_left, review_right = st.columns(2)
        with review_left:
            st.dataframe(pd.DataFrame(document_rows), width="stretch", hide_index=True)
        with review_right:
            st.dataframe(pd.DataFrame(verification_rows), width="stretch", hide_index=True)

    signal_rows = [
        {"Signal": "Debt / revenue", "Value": _ratio(signals["debt_to_revenue_ratio"]), "What it tells the banker": "Debt pressure relative to business size."},
        {"Signal": "Request / revenue", "Value": _ratio(signals["request_to_revenue_ratio"]), "What it tells the banker": "Requested exposure relative to reported revenue."},
        {"Signal": "Loan velocity", "Value": _score(signals["loan_velocity_score"]), "What it tells the banker": "Recent borrowing intensity and possible credit stacking."},
        {"Signal": "Payment stress", "Value": _score(signals["payment_stress_score"]), "What it tells the banker": "Late-payment and debt-pressure stress."},
        {"Signal": "External financing pressure", "Value": _score(signals["external_financing_pressure"]), "What it tells the banker": "Financing pressure from request size, debt, and recent borrowing."},
        {"Signal": "Financial distress", "Value": _score(signals["financial_distress_score"]), "What it tells the banker": "Combined debt, payment, collateral, and history stress."},
        {"Signal": "Transaction anomaly", "Value": _score(signals["transaction_anomaly_score"]), "What it tells the banker": "Suspicious transfer and behavior pattern risk."},
        {"Signal": "Cash-flow pressure", "Value": _score(signals["cash_flow_pressure_score"]), "What it tells the banker": "Negative FCF and burn-rate pressure."},
        {"Signal": "Runway risk", "Value": _score(signals["runway_risk_score"]), "What it tells the banker": "Short-runway liquidity risk."},
        {"Signal": "Cash conversion risk", "Value": _score(signals["cash_conversion_risk_score"]), "What it tells the banker": "Weak cash conversion relative to revenue."},
        {"Signal": "Forecast aggressiveness", "Value": _score(signals["forecast_plan_aggressiveness_score"]), "What it tells the banker": "Ambition of the five-year plan relative to current signals."},
        {"Signal": "Forecast execution risk", "Value": _score(signals["forecast_execution_risk_score"]), "What it tells the banker": "Risk that the forecast is hard to execute."},
        {"Signal": "Hiring efficiency risk", "Value": _score(signals["forecast_hiring_efficiency_risk_score"]), "What it tells the banker": "Revenue growth that may be under-supported by headcount growth."},
        {"Signal": "Debt service plan risk", "Value": _score(signals["forecast_debt_service_risk_score"]), "What it tells the banker": "Debt reduction strain under current cash-flow pressure."},
        {"Signal": "Interest rate risk", "Value": _score(signals["interest_rate_risk_score"]), "What it tells the banker": "Pricing level that can increase repayment burden."},
        {"Signal": "Debt service stress", "Value": _score(signals["debt_service_stress_score"]), "What it tells the banker": "Coverage pressure from DSCR and the +2% rate stress test."},
        {"Signal": "Cash conversion cycle", "Value": _days(signals["cash_conversion_cycle_days"]), "What it tells the banker": "Working-capital timing pressure across receivables, inventory, and payables."},
        {"Signal": "Document completeness", "Value": _score(signals["document_completeness_score"]), "What it tells the banker": "How much of the expected application package is present."},
        {"Signal": "Document quality risk", "Value": _score(signals["document_quality_risk_score"]), "What it tells the banker": "Missing documents, edits, and late-stage changes."},
        {"Signal": "Process integrity risk", "Value": _score(signals["process_integrity_risk_score"]), "What it tells the banker": "Workflow deviations and resubmission behavior."},
        {"Signal": "Identity verification risk", "Value": _score(signals["identity_verification_risk_score"]), "What it tells the banker": "Young digital footprint, bank-account age, and location/contact mismatches."},
        {"Signal": "Working-capital pressure", "Value": _score(signals["working_capital_pressure_score"]), "What it tells the banker": "Liquidity ratio weakness and cash conversion pressure."},
        {"Signal": "Financial statement anomaly", "Value": _score(signals["financial_statement_anomaly_score"]), "What it tells the banker": "Revenue/cash-flow mismatch, receivables pressure, and unsupported margin improvement."},
        {"Signal": "Related-party network risk", "Value": _score(signals["related_party_network_risk_score"]), "What it tells the banker": "Ownership, counterparty concentration, and shared identifier concerns."},
        {"Signal": "Narrative consistency risk", "Value": _score(signals["narrative_consistency_risk_score"]), "What it tells the banker": "Potential contradictions between applicant context, documents, and financials."},
    ]
    with st.expander("Calculated Risk Signals", expanded=True):
        st.caption("Fraud and anomaly detection are one component of the broader credit-risk assessment.")
        st.dataframe(pd.DataFrame(signal_rows), width="stretch", hide_index=True)

    action_cols = st.columns([1, 1, 1, 2])
    if action_cols[0].button("Open Case Review", width="stretch"):
        if hasattr(st, "dialog"):
            _review_dialog()
        else:
            st.session_state.show_review_dialog = True
    report = case_summary(application, prediction, explanation, current_review)
    memo = credit_memo(application, prediction, explanation, current_review, loan_terms, monitoring_rows, timeline_rows)
    action_cols[1].download_button(
        "Generate Credit Memo",
        data=memo,
        file_name=f"{application['application_id']}_credit_memo.md",
        mime="text/markdown",
        width="stretch",
    )
    action_cols[2].download_button(
        "Download Audit Summary",
        data=report,
        file_name=f"{application['application_id']}_case_summary.txt",
        mime="text/plain",
        width="stretch",
    )
    if st.session_state.last_email_link and current_review:
        action_cols[3].markdown(f"[Open email draft]({st.session_state.last_email_link})")

    if st.session_state.show_review_dialog and not hasattr(st, "dialog"):
        with st.expander("Case Review", expanded=True):
            _review_form_body()

    st.subheader("Decision History Timeline")
    st.dataframe(pd.DataFrame(timeline_rows), width="stretch", hide_index=True)

    st.write("Risk factors")
    if prediction["flags"]:
        for flag in prediction["flags"]:
            st.warning(flag)
    else:
        st.success("No elevated deterministic risk flags were triggered.")

    st.subheader("Similar Historical Applications")
    st.caption("Nearest historical portfolio cases by company profile, requested terms, and credit/anomaly risk signals.")
    similar = similar_applications(st.session_state.model_bundle, applications, application)
    display_similar = similar.copy()
    for column in ["requested_amount", "free_cash_flow"]:
        if column in display_similar:
            display_similar[column] = display_similar[column].apply(_money)
    if "expected_runway_months" in display_similar:
        display_similar["expected_runway_months"] = display_similar["expected_runway_months"].apply(format_months)
    if "document_completeness_score" in display_similar:
        display_similar["document_completeness_score"] = display_similar["document_completeness_score"].apply(_score)
    for column in ["interest_rate", "forecast_revenue_cagr", "fraud_probability"]:
        if column in display_similar:
            display_similar[column] = display_similar[column].apply(_ratio)
    if "debt_service_coverage_ratio" in display_similar:
        display_similar["debt_service_coverage_ratio"] = display_similar["debt_service_coverage_ratio"].apply(_score)
    display_similar = display_similar.rename(columns={"fraud_probability": "Application risk score"})
    st.dataframe(display_similar, width="stretch", hide_index=True)
else:
    st.info("Submit the form to score an application.")
