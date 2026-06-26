# Lender workspace for reviewing locked SME submissions and publishing outcomes.
from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st

from src.constants import *
from src.features.alignment_features import (
    apply_scenario,
    data_source_coverage_rows,
    peer_benchmark_rows,
    scenario_comparison_rows,
)
from src.features.case_workflow import (
    REVIEW_ACTIONS,
    case_summary,
    similar_applications,
)
from src.core.data_pipeline import (
    add_derived_features,
    build_forecast_table,
    validate_forecast_plan_rows,
)
from src.utils.demo_persistence import ensure_demo_session, persist_demo_state
from src.utils.document_storage import list_documents, read_document
from src.utils.workflow_transfer import (
    SME_SUBMISSION_SOURCE,
    find_submitted_application,
    submitted_intake_rows,
)
from src.features.explanations import evaluation_signature, explain_prediction
from src.ui.document_validation import (
    latest_document_validation_run,
    render_document_validation_panel,
)
from src.utils.formatting import (
    format_currency,
    format_integer,
    format_months,
    format_percent,
    format_score,
)
from src.core.runtime import bootstrap_state
from src.ui.components import render_sidebar, safe_page_link
from src.features.workbench_features import (
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
render_sidebar(suppress_demo_prompt=True)
demo_session_id = ensure_demo_session()

# Personal Workspace is the lender's active case file. It can load either a
# synthetic queue row or an SME-submitted snapshot, but it never edits the live
# SME draft. All scoring, document verification, AI review, analyst review, and
# publication state is written to session history for auditability.
st.markdown(
    """
    <style>
    .score-panel {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 8px;
        padding: 0;
        margin: 0.35rem 0 0.8rem;
        background: color-mix(in srgb, var(--cr-surface) 94%, transparent);
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
        overflow: visible;
        position: relative;
    }
    .score-panel.low { border-top: 4px solid #22c55e; }
    .score-panel.medium { border-top: 4px solid #f59e0b; }
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
        color: var(--cr-text);
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.05;
    }
    .score-subtitle {
        color: var(--cr-muted);
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
        border-right: 1px solid rgba(148, 163, 184, 0.20);
        min-width: 0;
        padding: 0.75rem 1rem;
    }
    .score-item:last-child {
        border-right: none;
    }
    .score-label {
        color: var(--cr-muted);
        font-size: 0.72rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
    }
    .hover-help {
        cursor: help;
        display: inline-block;
        position: relative;
        text-decoration: underline dotted rgba(100, 116, 139, 0.65);
        text-underline-offset: 0.16rem;
    }
    .hover-help::after {
        background: #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.34);
        border-radius: 8px;
        box-shadow: 0 16px 36px rgba(15, 23, 42, 0.22);
        color: #f8fafc;
        content: attr(data-tip);
        font-size: 0.76rem;
        font-weight: 650;
        left: 0;
        line-height: 1.35;
        max-width: min(16rem, calc(100vw - 2rem));
        min-width: 12rem;
        opacity: 0;
        padding: 0.55rem 0.65rem;
        pointer-events: none;
        position: absolute;
        text-transform: none;
        top: calc(100% + 0.45rem);
        transform: translateY(-0.12rem);
        transition: opacity 120ms ease, transform 120ms ease, visibility 120ms ease;
        visibility: hidden;
        white-space: normal;
        z-index: 20;
    }
    .hover-help:hover::after,
    .hover-help:focus-visible::after {
        opacity: 1;
        transform: translateY(0);
        visibility: visible;
    }
    .score-item:last-child .hover-help::after {
        left: auto;
        right: 0;
    }
    .score-value {
        color: var(--cr-text);
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
        background: color-mix(in srgb, var(--cr-surface) 92%, transparent);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    }
    .decision-panel.approve { border-left: 5px solid #22c55e; }
    .decision-panel.review,
    .decision-panel.pending { border-left: 5px solid #f59e0b; }
    .decision-panel.reject { border-left: 5px solid #ef4444; }
    .decision-title {
        color: var(--cr-text);
        font-size: 1.1rem;
        font-weight: 800;
        line-height: 1.25;
        margin-bottom: 0.25rem;
    }
    .decision-copy {
        color: var(--cr-muted);
        font-size: 0.88rem;
        line-height: 1.45;
        margin-bottom: 0.55rem;
    }
    .decision-list {
        color: var(--cr-muted);
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
        color: var(--cr-text);
        display: inline-flex;
        font-size: 0.78rem;
        font-weight: 750;
        gap: 0.35rem;
        line-height: 1;
        padding: 0.48rem 0.68rem;
    }
    .source-badge.ready { background: rgba(34, 197, 94, 0.14); }
    .source-badge.partial { background: rgba(245, 158, 11, 0.16); }
    .source-badge.review { background: rgba(239, 68, 68, 0.14); }
    .queue-panel {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 8px;
        margin: 0.35rem 0 1rem;
        padding: 0.9rem 1rem;
        background: color-mix(in srgb, var(--cr-surface) 92%, transparent);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    }
    .queue-panel-title {
        color: var(--cr-text);
        font-size: 1rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }
    .queue-panel-copy {
        color: var(--cr-muted);
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
        background: rgba(34, 197, 94, 0.10);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
    }
    .active-case-title {
        color: var(--cr-text);
        font-size: 0.98rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .active-case-copy {
        color: var(--cr-muted);
        font-size: 0.84rem;
        line-height: 1.4;
    }
    .workspace-score-guide {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(20, 184, 166, 0.26);
        border-radius: 8px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
        margin: 0.65rem 0 0.75rem;
        padding: 0.85rem;
    }
    .workspace-score-guide-title {
        color: #f8fafc;
        font-size: 0.95rem;
        font-weight: 850;
        line-height: 1.2;
        margin-bottom: 0.65rem;
    }
    .workspace-score-guide-label {
        color: #5eead4;
        font-size: 0.72rem;
        font-weight: 800;
        line-height: 1.15;
        margin-top: 0.65rem;
        text-transform: uppercase;
    }
    .workspace-score-guide-copy {
        color: rgba(248, 250, 252, 0.86);
        font-size: 0.8rem;
        line-height: 1.42;
        margin-top: 0.2rem;
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
selected_model_key = st.session_state.model_bundle.default_model_key

# All loaded cases are treated as immutable review inputs. The helper functions
# below clear score/review state whenever a different intake is activated so an
# analyst cannot accidentally carry evidence or AI output from one case to the
# next.

def _clear_scored_case():
    # Loading a different intake invalidates prior score, explanation, review, and publication prompts.
    st.session_state.last_application = None
    st.session_state.last_prediction = None
    st.session_state.last_explanation = None
    st.session_state.last_review = None
    st.session_state.last_email_link = None
    st.session_state.show_review_dialog = False


def _activate_intake_case(application, source):
    # Store a snapshot copy so later SME edits cannot mutate the lender's working file in place.
    st.session_state.active_queue_application = dict(application)
    st.session_state.active_intake_source = source
    st.session_state.loan_example_scenario = "Custom application"
    _clear_scored_case()
    persist_demo_state()
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun:
        rerun()


def _clear_active_intake_case():
    st.session_state.active_queue_application = None
    st.session_state.active_intake_source = "Manual entry"
    _clear_scored_case()
    persist_demo_state()
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun:
        rerun()


READ_ONLY_INTAKE_SECTIONS = [
    # This list defines the lender's locked intake tabs. It intentionally shows
    # applicant-entered amounts and derived values together, but as read-only
    # submitted facts rather than editable lender inputs.
    (
        "Company Profile",
        [
            ("Application ID", "application_id"),
            ("Company", "company_name"),
            ("Industry", "industry"),
            ("Region", "region"),
            ("Company type", "company_type"),
            ("Years in business", "years_in_business"),
            ("Employees", "employees"),
        ],
    ),
    (
        "Loan Request",
        [
            ("Requested amount", "requested_amount"),
            ("Term", "term_months"),
            ("Interest rate", "interest_rate"),
            ("Collateral coverage", "collateral_ratio"),
            ("Existing debt", "existing_debt"),
            ("Recent loans", "num_recent_loans"),
        ],
    ),
    (
        "Financial Snapshot",
        [
            ("Annual revenue", "annual_revenue"),
            ("Free cash flow", "free_cash_flow"),
            ("Monthly burn rate", "monthly_burn_rate"),
            ("Cash flow / revenue", "cash_flow_to_revenue_ratio"),
            ("Expected runway", "expected_runway_months"),
            ("Current ratio", "current_ratio"),
            ("Quick ratio", "quick_ratio"),
            ("Receivables days", "receivables_days"),
            ("Payables days", "payables_days"),
            ("Inventory days", "inventory_days"),
        ],
    ),
    (
        "Five-Year Plan",
        [
            ("Revenue growth", "forecast_revenue_cagr"),
            ("Employee growth", "forecast_employee_cagr"),
            ("Year 5 FCF margin", "forecast_fcf_margin_year5"),
            ("Planned debt reduction", "planned_debt_reduction_pct"),
        ],
    ),
    (
        "Evidence",
        [
            ("Financial statements", "financial_statements_uploaded"),
            ("Bank statements", "bank_statements_uploaded"),
            ("Tax return", "tax_return_uploaded"),
            ("Ownership/KYB", "ownership_docs_uploaded"),
            ("Forecast support", "forecast_support_uploaded"),
        ],
    ),
]

READ_ONLY_NARRATIVE_FIELDS = [
    ("Loan purpose", "loan_purpose_context"),
    ("Current business context", "current_business_context"),
    ("Future business context", "future_business_context"),
    ("CEO context", "ceo_context"),
    ("CFO context", "cfo_context"),
    ("COO context", "coo_context"),
]

READ_ONLY_PERCENT_FIELDS = {
    "interest_rate",
    "collateral_ratio",
    "cash_flow_to_revenue_ratio",
    "forecast_revenue_cagr",
    "forecast_employee_cagr",
    "forecast_fcf_margin_year5",
    "planned_debt_reduction_pct",
}
READ_ONLY_CURRENCY_FIELDS = {
    "requested_amount",
    "existing_debt",
    "annual_revenue",
    "free_cash_flow",
    "monthly_burn_rate",
}
READ_ONLY_MONTH_FIELDS = {"term_months", "expected_runway_months"}
READ_ONLY_DOCUMENT_FIELDS = {
    "financial_statements_uploaded",
    "bank_statements_uploaded",
    "tax_return_uploaded",
    "ownership_docs_uploaded",
    "forecast_support_uploaded",
}


def _present(value):
    # pandas/numpy missing values behave differently from plain None, so keep
    # this small wrapper before applying display formatting.
    if value is None:
        return False
    try:
        return not pd.isna(value)
    except (TypeError, ValueError):
        return True


def _read_only_value(application, field_name):
    value = application.get(field_name)
    if not _present(value):
        return "N/A"
    # Render locked SME fields with lender-friendly formatting while keeping raw data unchanged.
    if field_name in READ_ONLY_CURRENCY_FIELDS:
        return format_currency(value)
    if field_name in READ_ONLY_PERCENT_FIELDS:
        return format_percent(value)
    if field_name in READ_ONLY_MONTH_FIELDS:
        return format_months(value)
    if field_name in READ_ONLY_DOCUMENT_FIELDS:
        return _yes_no(value)
    if field_name in {"years_in_business", "current_ratio", "quick_ratio"}:
        return format_score(value)
    if field_name in {"employees", "num_recent_loans", "receivables_days", "payables_days", "inventory_days"}:
        return format_integer(value)
    return str(value)


def _read_only_rows(application, fields):
    return [
        {"Field": label, "Submitted value": _read_only_value(application, field_name)}
        for label, field_name in fields
    ]


def _has_submitted_forecast_plan(application):
    rows, errors = validate_forecast_plan_rows(application.get("forecast_plan_rows"))
    return bool(rows) and not errors


def _forecast_plan_display(application):
    # Lender views should show the SME-submitted annual rows when present. Older
    # demo sessions without forecast_plan_rows still render through the legacy
    # generated fallback inside build_forecast_table().
    forecast = build_forecast_table(pd.DataFrame([application]))
    if forecast.empty:
        return pd.DataFrame(
            columns=[
                "Year",
                "Projected revenue",
                "Projected employees",
                "Projected FCF",
                "Projected debt",
            ]
        )
    display = forecast.rename(
        columns={
            "forecast_year": "Year",
            "projected_revenue": "Projected revenue",
            "projected_employees": "Projected employees",
            "projected_free_cash_flow": "Projected FCF",
            "projected_debt": "Projected debt",
        }
    )[
        [
            "Year",
            "Projected revenue",
            "Projected employees",
            "Projected FCF",
            "Projected debt",
        ]
    ].copy()
    for column in ["Projected revenue", "Projected FCF", "Projected debt"]:
        display[column] = display[column].apply(format_currency)
    display["Projected employees"] = display["Projected employees"].apply(
        format_integer
    )
    return display


def _render_read_only_intake(application):
    # The SME Portal owns application intake. The lender sees a frozen copy for scoring and review.
    # If a lender notices an incorrect value, the fix is to ask the SME to edit
    # and resubmit from the Loan Intake Portal instead of changing it here.
    st.subheader("Loaded Intake Snapshot")
    st.caption(
        "Read-only lender view. Change applicant data from the Loan Intake Portal and resubmit the application."
    )
    tabs = st.tabs([section[0] for section in READ_ONLY_INTAKE_SECTIONS] + ["Narrative"])
    for tab, (section_title, fields) in zip(tabs, READ_ONLY_INTAKE_SECTIONS):
        with tab:
            if section_title == "Five-Year Plan":
                st.dataframe(
                    _forecast_plan_display(application),
                    width="stretch",
                    hide_index=True,
                )
                if not _has_submitted_forecast_plan(application):
                    st.caption(
                        "Legacy intake: annual rows are generated from saved year-5 assumptions because no submitted plan rows exist."
                    )
                st.caption("Model-derived summary")
            st.dataframe(
                pd.DataFrame(_read_only_rows(application, fields)),
                width="stretch",
                hide_index=True,
            )
    with tabs[-1]:
        narrative_rows = [
            {"Field": label, "Submitted value": str(application.get(field_name, "")).strip()}
            for label, field_name in READ_ONLY_NARRATIVE_FIELDS
            if str(application.get(field_name, "")).strip()
        ]
        if narrative_rows:
            st.dataframe(pd.DataFrame(narrative_rows), width="stretch", hide_index=True)
        else:
            st.info("No applicant narrative was submitted with this intake.")


def _score_loaded_intake(application, model_key):
    # Scoring normalizes a few fields that may be absent on blank/manual intakes,
    # then hands the application to the model bundle. The original loaded
    # snapshot remains untouched; only scored_application is enriched for audit.
    scored_application = dict(application)
    # Manual or blank intakes may not have an ID yet; scoring still needs a stable audit key.
    scored_application["application_id"] = scored_application.get(
        "application_id"
    ) or f"INTAKE-{len(st.session_state.portfolio_history) + 1:03d}"
    scored_application["company_name"] = (
        scored_application.get("company_name") or "Submitted Applicant"
    )
    annual_revenue = float(scored_application.get("annual_revenue", 0) or 0)
    free_cash_flow = float(scored_application.get("free_cash_flow", 0) or 0)
    scored_application["cash_flow_to_revenue_ratio"] = free_cash_flow / max(
        annual_revenue, 1
    )
    prediction = st.session_state.model_bundle.score_one(
        scored_application, model_key=model_key
    )
    explanation = explain_prediction(scored_application, prediction, use_llm=False)
    _store_prediction(scored_application, prediction, explanation)


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


def _tip_label(label, help_text):
    escaped_help = escape(help_text, quote=True)
    return (
        f'<span class="hover-help" tabindex="0" data-tip="{escaped_help}" '
        f'title="{escaped_help}">{escape(label)}</span>'
    )


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
    return [
        label
        for key, label in document_fields
        if float(application.get(key, 0) or 0) < 0.5
    ]


def _readiness_status(score):
    if score >= 0.8:
        return "Ready"
    if score >= 0.5:
        return "Partial"
    return "Needs review"


def _data_readiness_rows(application, signals):
    # Readiness rows translate low-level binary/document/narrative indicators
    # into source-oriented review guidance. This is the analyst's explanation of
    # which evidence source supports which decision use.
    missing_documents = _missing_documents(application)
    document_score = float(signals.get("document_completeness_score", 0) or 0)
    context_status = _context_completeness(application)
    context_score = {"Complete": 1.0, "Partial": 0.6, "Missing": 0.0}.get(
        context_status, 0.0
    )
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
    management_coverage = (
        ", ".join(management_notes)
        if management_notes
        else "No applicant or management narrative provided"
    )
    forecast_score = (
        0.60 * float(application.get("forecast_support_uploaded", 0) or 0)
        + 0.40 * context_score
    )
    accounting_score = (
        0.45 * float(application.get("financial_statements_uploaded", 0) or 0)
        + 0.35 * float(application.get("tax_return_uploaded", 0) or 0)
        + 0.20 * min(max(float(application.get("current_ratio", 0) or 0) / 2, 0), 1)
    )
    registry_score = (
        0.50 * float(application.get("ownership_docs_uploaded", 0) or 0)
        + 0.25 * min(float(application.get("email_domain_age_months", 0) or 0) / 24, 1)
        + 0.25 * min(float(application.get("website_age_months", 0) or 0) / 24, 1)
    )
    banking_score = 0.70 * float(
        application.get("bank_statements_uploaded", 0) or 0
    ) + 0.30 * min(float(application.get("bank_account_age_months", 0) or 0) / 24, 1)

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
            "Evidence coverage": (
                "All expected documents received."
                if not missing_documents
                else f"Missing required evidence: {', '.join(missing_documents)}."
            ),
            "Decision use": "Determines whether the file is complete enough to support a credit decision.",
        },
        {
            "Source": "Registry / KYB",
            "Readiness": _readiness_status(registry_score),
            "Evidence coverage": (
                f"Ownership/KYB documents received: {_yes_no(application.get('ownership_docs_uploaded', 0))}. "
                f"Email domain age: {format_months(application.get('email_domain_age_months', 0))}; "
                f"website age: {format_months(application.get('website_age_months', 0))}."
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
                f"Applicant narrative status: {context_status}."
            ),
            "Decision use": "Assesses growth realism, free-cash-flow margin, debt reduction, and execution risk.",
        },
    ]


def _decision_conditions(application, prediction, signals):
    # Conditions are generated from the model score, evidence status, and major
    # rule flags. They become suggested review conditions, not binding policy.
    conditions = []
    missing_documents = _missing_documents(application)
    if missing_documents:
        conditions.append(
            f"Collect or validate missing items: {', '.join(missing_documents)}."
        )
    if float(signals.get("stressed_debt_service_coverage_ratio", 0) or 0) < 1.1:
        conditions.append(
            "Review debt-service coverage under the +2% interest-rate stress case."
        )
    if float(signals.get("document_quality_risk_score", 0) or 0) >= 0.35:
        conditions.append(
            "Request or verify the missing document package before release."
        )
    if float(signals.get("narrative_consistency_risk_score", 0) or 0) >= 0.4:
        conditions.append(
            "Resolve narrative contradictions against financial and document evidence."
        )
    for flag in prediction.get("flags", [])[:2]:
        if flag not in conditions:
            conditions.append(flag)
    if not conditions:
        conditions.append(
            "No extra conditions flagged beyond standard credit covenants."
        )
    return conditions[:4]


def _decision_copy(application, prediction, review, signals):
    decision = review["final_decision"] if review else "Pending Review"
    if review:
        return (
            f"{review['action']} saved by the analyst at {review['timestamp']}. "
            f"The analyst rating is {review.get('analyst_grade', prediction['grade'])}; "
            f"the unchanged model grade is {prediction['grade']} with an application risk score of "
            f"{_ratio(prediction['fraud_probability'])}."
        )
    return (
        f"Model recommends {prediction['decision']} at grade {prediction['grade']} "
        f"with a {_risk_label(prediction['fraud_probability']).lower()} profile. Analyst decision is still pending."
    )


def _dscr_interpretation(value):
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0
    if number >= 1.25:
        return "This is comfortable coverage: cash flow is meaningfully above estimated debt service after the stress."
    if number >= 1.0:
        return "This covers estimated debt service, but the cushion is thin. The analyst should check cash-flow durability and covenants."
    return "This does not fully cover estimated debt service under stress. The structure may need a lower amount, longer tenor, stronger collateral, or rejection."


def _risk_score_interpretation(probability):
    if probability >= 0.58:
        return "The score is in the high-risk range for this demo portfolio. Treat the model result as a reason for deeper evidence review, not as an automatic decision."
    if probability >= 0.28:
        return "The score is in the moderate-risk range. The decision usually depends on evidence quality, repayment cushion, and analyst judgment."
    return "The score is in the lower-risk range, but the analyst still needs to confirm documents, repayment capacity, and policy fit."


def _render_workspace_metric_guide(application, prediction, signals):
    # The sidebar score guide follows the active case. It gives a cold reader a
    # quick interpretation of the most important risk and repayment-capacity
    # numbers while keeping detailed definitions in the Acronym Guide.
    with st.sidebar:
        st.divider()
        guide_rows = [
            (
                "Application risk score",
                f"{_ratio(prediction['fraud_probability'])} means: "
                f"{_risk_score_interpretation(prediction['fraud_probability'])}",
            ),
            (
                "Stressed DSCR",
                f"{_score(signals['stressed_debt_service_coverage_ratio'])} means: "
                f"{_dscr_interpretation(signals['stressed_debt_service_coverage_ratio'])}",
            ),
            (
                "Document completeness",
                f"{_score(signals['document_completeness_score'])} means the expected evidence package is "
                "substantially present when it is close to 1.00. It still needs lender validation for content and category fit.",
            ),
            (
                "Free cash flow",
                f"{_money(application.get('free_cash_flow', 0))} is the annual cash available after operating and investment needs. "
                "Positive values support repayment; weak or negative values increase cash-flow pressure.",
            ),
        ]
        guide_html = "".join(
            f"""
            <div class="workspace-score-guide-label">{escape(label)}</div>
            <div class="workspace-score-guide-copy">{escape(copy)}</div>
            """
            for label, copy in guide_rows
        )
        st.markdown(
            f"""
            <section class="workspace-score-guide">
                <div class="workspace-score-guide-title">How to read this score</div>
                {guide_html}
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "For DSCR, FCF, CAGR, KYB, PSD2, ROC-AUC, and SHA-256 definitions, open the Help glossary."
        )
        safe_page_link(
            "pages/11_Acronym_Guide.py",
            "Open Acronym Guide",
            ":material/menu_book:",
        )


def _summary_table(rows):
    # Most tables on this page use the same "Metric / Value / How to read it"
    # pattern. The helper adds default explanations so new metrics remain
    # understandable even if a page author omits custom copy.
    normalized_rows = []
    for row in rows:
        metric = row[0]
        value = row[1]
        explanation = (
            row[2]
            if len(row) > 2
            else METRIC_EXPLANATIONS.get(
                metric,
                "Read this value together with the surrounding credit, evidence, and narrative signals before making a decision.",
            )
        )
        normalized_rows.append(
            {"Metric": metric, "Value": value, "How to read it": explanation}
        )
    return pd.DataFrame(normalized_rows)


def _add_signal_interpretations(rows):
    interpreted_rows = []
    for row in rows:
        enriched = dict(row)
        enriched["How to read it"] = SIGNAL_INTERPRETATIONS.get(
            row.get("Signal"),
            "Most normalized risk signals use 0.00 as lower concern and 1.00 as higher concern. Use the value as a review prompt, not as a standalone decision.",
        )
        interpreted_rows.append(enriched)
    return interpreted_rows


def _context_completeness(application):
    fields = [
        "loan_purpose_context",
        "current_business_context",
        "future_business_context",
    ]
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


def _upsert_portfolio_history(application_id, values):
    # Portfolio history is a session-level current-state table for dashboards.
    # Updating the latest row avoids counting the same case multiple times when
    # the analyst scores, reviews, and publishes it in one demo run.
    for row in reversed(st.session_state.portfolio_history):
        if row.get("application_id") == application_id:
            row.update(values)
            return
    st.session_state.portfolio_history.append(values)


def _lifecycle_for(application_id):
    return dict(st.session_state.application_lifecycle.get(application_id, {}))


def _evaluation_package_for(application, prediction):
    package = st.session_state.llm_evaluation_packages.get(
        application.get("application_id")
    )
    # The signature prevents stale AI output from being reused after a case or score changes.
    if not package or package.get("signature") != evaluation_signature(
        application, prediction
    ):
        return None
    return dict(package)


def _render_ai_output(application, prediction):
    package = _evaluation_package_for(application, prediction)
    if not package:
        # Case Review is intentionally gated behind AI output for the assignment demo flow.
        st.warning(
            "Please use the AI before continuing. Open LLM Integration and generate the Internal + SME Reports package for this scored case."
        )
        safe_page_link(
            "pages/5_LLM_Integration.py",
            "Open LLM Integration",
            ":material/psychology:",
        )
        return None

    st.success("AI evaluation package is attached to this scored case.")
    meta_cols = st.columns(4)
    meta_cols[0].metric("Package ID", package.get("evaluation_package_id", "N/A"))
    meta_cols[1].metric("Provider", package.get("provider", "N/A"))
    meta_cols[2].metric("Source", package.get("internal_source", "N/A"))
    meta_cols[3].metric("Generated", package.get("generated_at", "N/A"))
    st.caption(
        "Copy-ready AI output from LLM Integration. The internal report stays lender-only; the SME report is the draft used for publication."
    )
    st.markdown("**Internal lender AI output**")
    st.code(
        package.get("internal_report", "No internal AI output available."),
        language="markdown",
    )
    st.markdown("**SME-facing AI output draft**")
    st.code(
        package.get("sme_report", "No SME-facing AI draft available."),
        language="markdown",
    )
    return package


def _update_lifecycle(application_id, **values):
    lifecycle = _lifecycle_for(application_id)
    lifecycle.update(values)
    lifecycle["application_id"] = application_id
    st.session_state.application_lifecycle[application_id] = lifecycle
    return lifecycle


def _update_sme_submission_status(application_id, status, **values):
    # Walk backward so the latest resubmission wins if an SME sends the same case more than once.
    for submission in reversed(st.session_state.sme_submission_history):
        if submission.get("application_id") == application_id:
            submission.update({"status": status, **values})
            return


def _render_review_publication(
    application,
    prediction,
    current_review,
    final_decision,
    publication_status,
    prediction_model_label,
    decision_conditions,
):
    # This section sits after scoring and review. It summarizes the human
    # decision state, exposes the attached AI package for audit, and opens the
    # publication form only after a lender review exists.
    review_cols = st.columns(4)
    review_cols[0].metric(
        "Final decision", final_decision, help=WORKSPACE_HELP["final_decision"]
    )
    review_cols[1].metric(
        "Analyst rating",
        (
            current_review.get("analyst_grade", "Pending")
            if current_review
            else "Pending"
        ),
        help="Reviewed lender rating kept separately from the model grade.",
    )
    review_cols[2].metric("Publication", publication_status)
    review_cols[3].metric(
        "Scoring model", prediction_model_label, help=WORKSPACE_HELP["ml_technique"]
    )
    st.dataframe(
        pd.DataFrame({"Review condition": decision_conditions}),
        width="stretch",
        hide_index=True,
    )
    if current_review:
        adjustment_label = (
            "Adjusted from model"
            if current_review.get("rating_adjusted")
            else "Aligned with model"
        )
        st.info(
            f"{adjustment_label}: model grade {prediction['grade']} \u2192 analyst rating "
            f"{current_review.get('analyst_grade', prediction['grade'])}. "
            f"Rationale: {current_review.get('rating_rationale', 'No rationale recorded.')}"
        )
        evaluation_package = _evaluation_package_for(application, prediction)
        if evaluation_package:
            with st.expander("AI evaluation package", expanded=False):
                st.caption(
                    f"Generated {evaluation_package.get('generated_at', 'N/A')} via "
                    f"{evaluation_package.get('provider', evaluation_package.get('internal_source', 'N/A'))}. "
                    "The internal report stays private; the SME draft is attached only when the rating is published."
                )
                st.markdown("**Internal lender report**")
                st.markdown(
                    evaluation_package.get(
                        "internal_report", "No internal report available."
                    )
                )
                st.markdown("**SME report draft**")
                st.markdown(
                    evaluation_package.get("sme_report", "No SME report available.")
                )
        else:
            st.warning("No current AI evaluation package is attached to this score.")
            safe_page_link(
                "pages/5_LLM_Integration.py",
                "Generate Evaluation Package",
                ":material/psychology:",
            )
        with st.expander(
            "Publish rating to SME",
            expanded=publication_status != "Rating published",
        ):
            _rating_publication_form(application, prediction, current_review)
    else:
        st.warning("Complete the lender evaluation before publishing any rating to the SME.")


def _render_score_history(application):
    # Score and review events are append-only histories. Showing them side by
    # side helps a reader see that model output and analyst action are separate
    # records even when they happen in one demo session.
    score_events = [
        row
        for row in st.session_state.score_history
        if row.get("application_id") == application["application_id"]
    ]
    review_events = [
        row
        for row in st.session_state.review_history
        if row.get("application_id") == application["application_id"]
    ]
    history_cols = st.columns(2)
    with history_cols[0]:
        st.caption("Score events")
        st.dataframe(score_events[-8:], width="stretch", hide_index=True)
    with history_cols[1]:
        st.caption("Review events")
        st.dataframe(review_events[-8:], width="stretch", hide_index=True)


def _render_lender_document_validation(application):
    # Lender verification is a second-pass check on the SME-uploaded evidence.
    # The original files remain unchanged; validation writes only result
    # metadata into lifecycle/session state.
    st.markdown("**Saved SME-uploaded files**")
    _render_saved_application_files(application["application_id"])
    # Validation results update lifecycle state, but do not alter the original SME-uploaded evidence.
    _, new_validation_run = render_document_validation_panel(
        demo_session_id,
        application["application_id"],
        "lender_verification",
        "Lender document verification",
        (
            "Run the formal lender-side check after intake. AI-assisted validation can classify the visible "
            "content, but final acceptance remains an analyst decision."
        ),
        "Run Lender Document Verification",
    )
    if new_validation_run:
        summary = new_validation_run.get("summary", {})
        _update_lifecycle(
            application["application_id"],
            document_validation_status=summary.get("status", "Unknown"),
            document_validation_run_id=new_validation_run.get("run_id"),
            document_validation_at=new_validation_run.get("validated_at"),
        )
        persist_demo_state()


def _render_saved_application_files(application_id):
    # The lender can inspect and download files saved by the SME portal. The
    # table uses hashes and metadata to make sample/fraudulent packs traceable
    # without exposing the local storage path in the UI.
    documents = list_documents(demo_session_id, application_id)
    if not documents:
        st.info("No saved SME-uploaded files are attached to this application.")
        return

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Category": document["category_label"],
                    "File": document["original_name"],
                    "Size": f"{document['size_bytes'] / 1024:.1f} KB",
                    "Saved": document["uploaded_at"],
                    "SHA-256": document["sha256"][:16] + "…",
                }
                for document in documents
            ]
        ),
        width="stretch",
        hide_index=True,
    )
    download_cols = st.columns(min(max(len(documents), 1), 3))
    for index, document in enumerate(documents):
        content, metadata = read_document(
            demo_session_id,
            application_id,
            document["document_id"],
        )
        with download_cols[index % len(download_cols)]:
            short_name = metadata["original_name"]
            if len(short_name) > 24:
                short_name = short_name[:21] + "..."
            st.caption(f"{metadata['category_label']}: {short_name}")
            st.download_button(
                "Download",
                data=content,
                file_name=metadata["original_name"],
                mime=metadata["content_type"],
                key=f"lender_download_{metadata['document_id']}",
                width="stretch",
            )


def _store_prediction(application, prediction, explanation):
    # A score event is append-only for audit history; the latest prediction fields drive the live UI.
    st.session_state.last_application = application
    st.session_state.last_prediction = prediction
    st.session_state.last_explanation = explanation
    st.session_state.last_review = None
    st.session_state.last_email_link = None
    score_event = {
        "score_event_id": f"SCORE-{len(st.session_state.score_history) + 1:03d}",
        "application_id": application["application_id"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "fraud_probability": prediction["fraud_probability"],
        "grade": prediction["grade"],
        "decision": prediction["decision"],
        "model": prediction.get("model_label", "Random Forest"),
    }
    st.session_state.score_history.append(score_event)
    _upsert_portfolio_history(
        application["application_id"],
        {
            **application,
            **prediction,
            "review_action": "Pending",
            "final_decision": "Pending Review",
        },
    )
    _update_lifecycle(
        application["application_id"],
        status="Scored by lender",
        scored_at=score_event["timestamp"],
        model_grade=prediction["grade"],
        model_probability=prediction["fraud_probability"],
        model_recommendation=prediction["decision"],
        model_label=prediction.get("model_label", "Random Forest"),
    )
    _update_sme_submission_status(
        application["application_id"],
        "Scored by lender",
        scored_at=score_event["timestamp"],
    )
    persist_demo_state()


def _last_prediction_matches(application_id, model_key):
    application = st.session_state.get("last_application") or {}
    prediction = st.session_state.get("last_prediction") or {}
    return (
        application.get("application_id") == application_id
        and prediction.get("model_key", selected_model_key) == model_key
    )


def _auto_score_submitted_intake(application, model_key):
    # Submitted SME cases auto-score once when first opened by the lender. This
    # keeps the demo flow smooth while still allowing manual "Score Loaded
    # Intake" for synthetic queue cases or rescoring after a reset.
    application_id = application.get("application_id")
    if (
        not application_id
        or st.session_state.get("active_intake_source") != SME_SUBMISSION_SOURCE
    ):
        return False
    if _last_prediction_matches(application_id, model_key):
        return False

    # Only auto-score fresh lender-submitted files, not already published or closed lifecycle states.
    lifecycle = _lifecycle_for(application_id)
    if lifecycle.get("status") not in {
        "Submitted to lender review",
        "Scored by lender",
        None,
    }:
        return False

    prediction = st.session_state.model_bundle.score_one(
        application, model_key=model_key
    )
    explanation = explain_prediction(application, prediction, use_llm=False)
    _store_prediction(dict(application), prediction, explanation)
    score_event = (
        st.session_state.score_history[-1] if st.session_state.score_history else {}
    )
    _update_lifecycle(
        application_id,
        auto_scored_at=score_event.get("timestamp"),
        auto_score_source="Lender workspace auto-score",
    )
    persist_demo_state()
    return True


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
                    "analyst_grade": review["analyst_grade"],
                    "rating_adjusted": review["rating_adjusted"],
                }
            )
            break


def _review_form_body():
    application = st.session_state.last_application
    prediction = st.session_state.last_prediction
    if not _evaluation_package_for(application, prediction):
        st.error("Please use the AI before saving the lender review.")
        safe_page_link(
            "pages/5_LLM_Integration.py",
            "Open LLM Integration",
            ":material/psychology:",
        )
        return
    existing_review = st.session_state.get("last_review") or {}
    lender_validation = latest_document_validation_run(
        application["application_id"], "lender_verification"
    )
    validation_summary = (
        lender_validation.get("summary", {}) if lender_validation else {}
    )
    validation_mismatch = int(validation_summary.get("mismatches", 0) or 0) > 0
    grade_options = list("ABCDEF")
    current_grade = existing_review.get(
        "analyst_grade", "F" if validation_mismatch else prediction["grade"]
    )
    current_action = existing_review.get(
        "action", "Reject" if validation_mismatch else prediction["decision"]
    )
    default_action_index = (
        REVIEW_ACTIONS.index(current_action) if current_action in REVIEW_ACTIONS else 0
    )

    with st.form("case_review_form"):
        st.caption(
            "The model output remains unchanged. The analyst can set a separate final rating after evaluating the evidence."
        )
        if validation_mismatch:
            st.warning(
                "Lender document verification found a likely category mismatch. Review the validation details before "
                "saving the final decision.",
                icon=":material/gpp_maybe:",
            )
        comparison_cols = st.columns(2)
        comparison_cols[0].metric("Model grade", prediction["grade"])
        comparison_cols[1].metric("Model recommendation", prediction["decision"])
        action = st.selectbox(
            "Analyst action", REVIEW_ACTIONS, index=default_action_index
        )
        analyst_grade = st.selectbox(
            "Analyst rating",
            grade_options,
            index=(
                grade_options.index(current_grade)
                if current_grade in grade_options
                else grade_options.index(prediction["grade"])
            ),
            help="This is the lender's reviewed A-F rating. It does not overwrite the model grade.",
        )
        analyst_note = st.text_area(
            "Internal analyst note",
            value=existing_review.get(
                "analyst_note",
                (
                    "Document verification found submitted evidence that appears inconsistent with its declared category."
                    if validation_mismatch
                    else "Reviewed model score, deterministic flags, evidence coverage, and explanation."
                ),
            ),
        )
        rating_rationale = st.text_area(
            "Rating rationale",
            value=existing_review.get(
                "rating_rationale",
                (
                    "The application cannot proceed because the submitted evidence could not be verified against the requested document categories."
                    if validation_mismatch
                    else "The final rating reflects the model output together with verified financial, evidence, and contextual factors."
                ),
            ),
            help="Required when the analyst rating differs from the model grade. This rationale supports the audit trail.",
        )
        submitted = st.form_submit_button("Save Review", width="stretch")

    if submitted:
        final_prediction = prediction
        rating_adjusted = analyst_grade != prediction["grade"]
        if rating_adjusted and not rating_rationale.strip():
            st.error("Explain why the analyst rating differs from the model grade.")
            return
        review = {
            "review_id": f"REV-{len(st.session_state.review_history) + 1:03d}",
            "application_id": application["application_id"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "analyst_note": analyst_note,
            "rating_rationale": rating_rationale.strip(),
            "analyst_grade": analyst_grade,
            "rating_adjusted": rating_adjusted,
            "manual_adjustment": rating_adjusted,
            "final_probability": final_prediction["fraud_probability"],
            "final_grade": analyst_grade,
            "model_grade": final_prediction["grade"],
            "model_recommendation": final_prediction["decision"],
            "final_decision": action,
        }
        st.session_state.last_review = review
        st.session_state.review_history.append(review)
        _update_latest_history(final_prediction, review)
        _update_lifecycle(
            application["application_id"],
            status="Evaluated by lender",
            evaluated_at=review["timestamp"],
            analyst_grade=analyst_grade,
            analyst_action=action,
            rating_adjusted=rating_adjusted,
            rating_rationale=rating_rationale.strip(),
        )
        _update_sme_submission_status(
            application["application_id"],
            "Evaluated by lender",
            evaluated_at=review["timestamp"],
        )

        st.session_state.last_email_link = None
        persist_demo_state()
        _rerun_after_review()


def _rating_publication_form(application, prediction, review):
    application_id = application["application_id"]
    lifecycle = _lifecycle_for(application_id)
    evaluation_package = _evaluation_package_for(application, prediction)
    already_published = lifecycle.get("status") == "Rating published"
    # Publication defaults to the latest approved SME draft, while allowing the analyst to edit the exact copy.
    default_message = lifecycle.get("published_message") or (
        f"Your application has been reviewed. The lender rating is {review['analyst_grade']} "
        f"and the current lender decision is {review['final_decision']}."
    )
    default_sme_report = lifecycle.get("published_sme_report") or (
        evaluation_package.get("sme_report", "") if evaluation_package else ""
    )
    report_source = lifecycle.get("published_sme_report_source") or (
        evaluation_package.get("sme_source") if evaluation_package else None
    )

    if not default_sme_report:
        st.warning(
            "Generate an evaluation package in LLM Integration before publishing. "
            "Publication requires an SME-facing report to be attached."
        )

    with st.form(f"rating_publication_form_{application_id}"):
        st.caption(
            "Nothing is visible to the SME until this publication step. The internal evaluation remains private; "
            "the editable SME report below is attached to the published outcome."
        )
        publication_cols = st.columns(3)
        publication_cols[0].metric("Model grade", prediction["grade"])
        publication_cols[1].metric("Analyst rating", review["analyst_grade"])
        publication_cols[2].metric("Lender decision", review["final_decision"])
        published_message = st.text_area("Message to the SME", value=default_message)
        published_sme_report = st.text_area(
            "SME-facing evaluation report",
            value=default_sme_report,
            height=420,
            disabled=not bool(default_sme_report),
            help="Review and edit this applicant-safe report. This exact version will be attached to the publication.",
        )
        if report_source:
            st.caption(f"Report draft source: {report_source}")
        include_score = st.checkbox(
            "Include numerical risk score",
            value=bool(lifecycle.get("published_score_visible", False)),
            help="Leave off when the lender wants to publish only the A-F rating and decision.",
        )
        publish = st.form_submit_button(
            "Update Published Rating" if already_published else "Publish Rating to SME",
            width="stretch",
            type="primary",
            disabled=not bool(default_sme_report),
        )

    if publish:
        if not published_sme_report.strip():
            st.error("The SME-facing evaluation report cannot be empty.")
            return
        published_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        publication = {
            "publication_id": f"PUB-{len(st.session_state.rating_publication_history) + 1:03d}",
            "application_id": application_id,
            "company_name": application.get("company_name", "Applicant"),
            "published_at": published_at,
            "published_grade": review["analyst_grade"],
            "published_decision": review["final_decision"],
            "published_message": published_message.strip(),
            "published_score_visible": include_score,
            "published_score": (
                prediction["fraud_probability"] if include_score else None
            ),
            "model_grade": prediction["grade"],
            "rating_adjusted": review["rating_adjusted"],
            "published_sme_report": published_sme_report.strip(),
            "published_sme_report_attached": True,
            "published_sme_report_source": report_source or "Lender-authored",
            "evaluation_package_id": (
                evaluation_package.get("evaluation_package_id")
                if evaluation_package
                else lifecycle.get("evaluation_package_id")
            ),
        }
        st.session_state.rating_publication_history.append(publication)
        _update_lifecycle(
            application_id,
            status="Rating published",
            **{
                key: value
                for key, value in publication.items()
                if key != "application_id"
            },
        )
        _update_sme_submission_status(
            application_id,
            "Rating published",
            published_at=published_at,
            published_grade=review["analyst_grade"],
        )
        persist_demo_state()
        st.success("The reviewed rating is now visible in the Loan Intake Portal.")
        rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
        if rerun:
            rerun()


if hasattr(st, "dialog"):

    @st.dialog("Case Review")
    def _review_dialog():
        # Newer Streamlit builds support modal review. Older builds fall back to
        # the inline form below, so the review body remains a separate helper.
        _review_form_body()


st.title("Personal Workspace")
st.caption("Analyst review surface for SME-submitted loan intake snapshots.")

# Submitted rows are lightweight queue cards built from immutable SME snapshots
# plus lifecycle status. Opening one activates the exact snapshot that was
# stored at submission time.
submitted_rows = submitted_intake_rows(
    st.session_state.sme_submission_history,
    st.session_state.application_lifecycle,
    active_application=st.session_state.get("active_queue_application"),
    sme_application=st.session_state.get("sme_company_application"),
)
if submitted_rows:
    with st.container():
        st.markdown(
            """
            <div class="queue-panel">
                <div class="queue-panel-title">SME Portal Intake</div>
                <div class="queue-panel-copy">Applications submitted by the company account. Opening one loads the exact submitted snapshot into the lender working file.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(submitted_rows, width="stretch", hide_index=True)
        intake_options = [
            f"{row['Application ID']} - {row['Company']} | {row['Status']}"
            for row in submitted_rows
        ]
        intake_cols = st.columns([2, 1],vertical_alignment="bottom")
        selected_intake_label = intake_cols[0].selectbox(
            "Submitted SME application", intake_options
        )
        selected_intake_id = selected_intake_label.split(" - ", 1)[0]
        if intake_cols[1].button("Open Submitted Application", width="stretch"):
            submitted_application = find_submitted_application(
                st.session_state.sme_submission_history,
                selected_intake_id,
                active_application=st.session_state.get("active_queue_application"),
                sme_application=st.session_state.get("sme_company_application"),
            )
            if submitted_application:
                _activate_intake_case(submitted_application, SME_SUBMISSION_SOURCE)
            else:
                st.error("The submitted application snapshot could not be found.")
else:
    st.info(
        "No SME-submitted intake is loaded yet. Submit one from the Loan Intake Portal, "
        "or use Operations Desk for the generic synthetic work queue."
    )
    empty_cols = st.columns([1, 1, 2])
    with empty_cols[0]:
        safe_page_link(
            "pages/6_SME_Credit_Health.py",
            "Open Loan Intake Portal",
            ":material/domain:",
        )
    with empty_cols[1]:
        safe_page_link(
            "pages/2_Operations_Desk.py",
            "Open Operations Desk",
            ":material/view_list:",
        )

active_case = st.session_state.get("active_queue_application")
if active_case:
    # active_queue_application is the current lender working file. It may come
    # from the SME portal or a synthetic dashboard/operations row, so the source
    # label is shown to avoid confusion during demos.
    active_lifecycle = _lifecycle_for(active_case.get("application_id"))
    st.markdown(
        f"""
        <div class="active-case-card">
            <div class="active-case-title">Active intake: {escape(str(active_case.get("application_id", "Session")))} - {escape(str(active_case.get("company_name", "Applicant")))}</div>
            <div class="active-case-copy">Source: {escape(st.session_state.get("active_intake_source", "Loaded snapshot"))}. Applicant data is locked in the lender workspace; use the Loan Intake Portal to change and resubmit intake data.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.get("active_intake_source") == SME_SUBMISSION_SOURCE:
        st.info(
            "SME journey status: "
            f"{active_lifecycle.get('status', 'Submitted to lender review')}. "
            "Score the submitted snapshot, save the lender evaluation, then publish the reviewed rating when it is ready for the company."
        )
        if _auto_score_submitted_intake(active_case, selected_model_key):
            st.success(
                "Submitted SME application was automatically scored for the lender review. "
                "Open LLM Integration to generate the internal and SME-facing evaluation package."
            )

    _render_read_only_intake(active_case)
    active_application_id = active_case.get("application_id")
    already_scored = bool(
        active_application_id
        and _last_prediction_matches(active_application_id, selected_model_key)
    )
    intake_actions = st.columns([1, 1, 2])
    if intake_actions[0].button(
        "Score Loaded Intake",
        width="stretch",
        disabled=already_scored,
        help="Scores the immutable intake snapshot with the Random Forest model.",
    ):
        _score_loaded_intake(active_case, selected_model_key)
        st.success("Loaded intake snapshot scored with the Random Forest model.")
    if intake_actions[1].button("Clear Loaded Intake", width="stretch"):
        _clear_active_intake_case()
    if already_scored:
        st.caption("This loaded intake has already been scored with the current Random Forest model.")
else:
    st.info(
        "No active intake loaded. Open a submitted SME application above, or use Operations Desk for generic queue work."
    )

if st.session_state.last_prediction:
    # The rest of the page is visible only after a score exists. From here the
    # workflow is: inspect risk/evidence, generate AI output, save review, and
    # publish an SME-safe result if appropriate.
    application = st.session_state.last_application
    prediction = st.session_state.last_prediction
    explanation = st.session_state.last_explanation
    current_review = st.session_state.last_review
    if (
        current_review
        and current_review.get("application_id") != application["application_id"]
    ):
        current_review = None
    final_decision = (
        current_review["final_decision"] if current_review else "Pending Review"
    )
    application_lifecycle = _lifecycle_for(application["application_id"])
    publication_status = application_lifecycle.get("status", "Not published")
    calculated = add_derived_features(pd.DataFrame([application]))
    signals = calculated.iloc[0]
    risk_tone = _risk_tone(prediction["fraud_probability"])
    risk_label = _risk_label(prediction["fraud_probability"])
    decision_tone = _decision_tone(final_decision)
    review_status = (
        current_review["timestamp"] if current_review else "Awaiting analyst"
    )
    flag_count = len(prediction.get("flags", []))
    flag_label = (
        f"{flag_count} elevated flag"
        if flag_count == 1
        else f"{flag_count} elevated flags"
    )
    decision_conditions = _decision_conditions(application, prediction, signals)
    condition_html = "".join(
        f"<li>{escape(condition)}</li>" for condition in decision_conditions
    )
    loan_terms = recommended_loan_terms(application, prediction, signals)
    monitoring_rows = portfolio_monitoring_preview(application, prediction, signals)
    timeline_rows = decision_timeline(application, prediction, current_review)
    driver_rows = grouped_risk_drivers(application, signals)
    prediction_model_key = prediction.get("model_key", selected_model_key)
    prediction_model_label = prediction.get(
        "model_label", st.session_state.model_bundle.label_for(prediction_model_key)
    )
    confidence_rows = model_confidence_rows(
        st.session_state.model_bundle.metrics_for(prediction_model_key),
        prediction,
        signals,
    )
    ai_evaluation_package = _evaluation_package_for(application, prediction)
    _render_workspace_metric_guide(application, prediction, signals)

    detail_tabs = st.tabs(
        [
            "Decision Package",
            "Risk Analysis",
            "AI Output",
            "Case Materials",
            "Audit History",
        ]
    )
    with detail_tabs[0]:
        # Decision Package is the analyst's main working tab: model output,
        # recommended terms, monitoring view, confidence checks, and the final
        # human review form all live here.
        st.subheader("Score Output")
        risk_score_label = _tip_label(
            "Application risk score", WORKSPACE_HELP["application_risk_score"]
        )
        risk_grade_label = _tip_label("Model grade", WORKSPACE_HELP["risk_grade"])
        recommendation_label = _tip_label(
            "Model recommendation", WORKSPACE_HELP["model_recommendation"]
        )
        ml_technique_label = _tip_label("Scoring model", WORKSPACE_HELP["ml_technique"])
        review_status_label = _tip_label("Review status", WORKSPACE_HELP["review_status"])
        stressed_dscr_label = _tip_label("Stressed DSCR", WORKSPACE_HELP["stressed_dscr"])
        st.markdown(
            f"""
            <div class="score-panel {risk_tone}">
                <div class="score-panel-header">
                    <div>
                        <div class="score-label">{risk_score_label}</div>
                        <div class="score-headline">{escape(_ratio(prediction["fraud_probability"]))}</div>
                        <div class="score-subtitle">{escape(risk_label)} profile with {escape(flag_label)}.</div>
                    </div>
                    <div class="decision-badge {decision_tone}" title="{escape(WORKSPACE_HELP["final_decision"], quote=True)}">{escape(final_decision)}</div>
                </div>
                <div class="score-strip">
                    <div class="score-item">
                        <div class="score-label">{risk_grade_label}</div>
                        <div class="score-value">{escape(prediction["grade"])}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">{recommendation_label}</div>
                        <div class="score-value">{escape(prediction["decision"])}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">{ml_technique_label}</div>
                        <div class="score-value">{escape(prediction_model_label)}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">{review_status_label}</div>
                        <div class="score-value">{escape(review_status)}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">{stressed_dscr_label}</div>
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
        st.caption(
            "Explanation source: deterministic analyst explanation. Open LLM Integration to run a local or hosted model."
        )
        st.info(explanation)
        safe_page_link(
            "pages/5_LLM_Integration.py", "Open LLM Integration", ":material/psychology:"
        )

        terms_col, monitoring_col = st.columns(2)
        with terms_col:
            st.subheader("Recommended Loan Terms")
            st.dataframe(pd.DataFrame(loan_terms), width="stretch", hide_index=True)
        with monitoring_col:
            st.subheader("Portfolio Monitoring Preview")
            st.dataframe(pd.DataFrame(monitoring_rows), width="stretch", hide_index=True)

        st.subheader("Model Confidence and Governance")
        st.dataframe(pd.DataFrame(confidence_rows), width="stretch", hide_index=True)
        st.caption(
            "Output is analyst decision support. Model scores, AI review, and final analyst action remain separate."
        )

    with detail_tabs[1]:
        # Risk Analysis is evidence-heavy. It connects source readiness,
        # document validation, what-if scenarios, peer context, and feature
        # drivers before a review decision is saved.
        st.subheader("Data Readiness")
        source_badges = data_source_badges(application, signals)
        badge_html = "".join(
            f'<span class="source-badge {escape(badge["Tone"])}">{escape(badge["Source"])}: {escape(badge["Status"])}</span>'
            for badge in source_badges
        )
        st.markdown(f'<div class="badge-row">{badge_html}</div>', unsafe_allow_html=True)
        st.dataframe(
            pd.DataFrame(_data_readiness_rows(application, signals)),
            width="stretch",
            hide_index=True,
        )
        st.caption(
            "MVP source coverage is simulated from the local case file. Production would connect consented bank feeds, accounting APIs, registry/KYB, and document ingestion."
        )
        st.dataframe(
            pd.DataFrame(data_source_coverage_rows(application, signals)),
            width="stretch",
            hide_index=True,
        )
        _render_lender_document_validation(application)

        with st.expander("Scenario Analysis", expanded=False):
            st.caption(
                "Use this to show how forward-looking evidence can move the risk profile before a final human decision."
            )
            scenario_left, scenario_middle, scenario_right = st.columns(3)
            with scenario_left:
                revenue_growth_delta = st.slider(
                    "Revenue growth change",
                    min_value=-0.15,
                    max_value=0.20,
                    value=0.00,
                    step=0.01,
                    format="%.2f",
                )
                fcf_margin_delta = st.slider(
                    "FCF margin change",
                    min_value=-0.10,
                    max_value=0.15,
                    value=0.00,
                    step=0.01,
                    format="%.2f",
                )
            with scenario_middle:
                operating_cost_pressure = st.slider(
                    "Operating cost pressure",
                    min_value=0.00,
                    max_value=0.15,
                    value=0.00,
                    step=0.01,
                    format="%.2f",
                )
                debt_reduction_delta = st.slider(
                    "Debt reduction plan change",
                    min_value=-0.20,
                    max_value=0.35,
                    value=0.00,
                    step=0.05,
                    format="%.2f",
                )
            with scenario_right:
                contract_evidence = st.selectbox(
                    "Contract evidence",
                    ["Current file", "Signed and documented", "Unconfirmed"],
                )
                complete_documents = st.checkbox("Complete missing documents", value=False)
            simulated_application = apply_scenario(
                application,
                revenue_growth_delta=revenue_growth_delta,
                fcf_margin_delta=fcf_margin_delta,
                operating_cost_pressure=operating_cost_pressure,
                contract_evidence=contract_evidence,
                complete_documents=complete_documents,
                debt_reduction_delta=debt_reduction_delta,
            )
            scenario_prediction, scenario_rows = scenario_comparison_rows(
                st.session_state.model_bundle,
                application,
                prediction,
                simulated_application,
                model_key=prediction_model_key,
            )
            st.dataframe(pd.DataFrame(scenario_rows), width="stretch", hide_index=True)
            st.caption(
                f"Scenario output: grade {scenario_prediction['grade']} and model recommendation "
                f"{scenario_prediction['decision']}. This is a what-if view, not a saved final decision."
            )

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
                        (
                            "Stressed DSCR (+2%)",
                            _score(signals["stressed_debt_service_coverage_ratio"]),
                        ),
                        ("Free cash flow", _money(application.get("free_cash_flow", 0))),
                        ("Monthly burn", _money(application.get("monthly_burn_rate", 0))),
                        (
                            "Cash flow / revenue",
                            _ratio(application.get("cash_flow_to_revenue_ratio", 0)),
                        ),
                        (
                            "Expected runway",
                            format_months(application.get("expected_runway_months", 0)),
                        ),
                        ("Current ratio", _score(application.get("current_ratio", 0))),
                        ("Quick ratio", _score(application.get("quick_ratio", 0))),
                        (
                            "Cash conversion cycle",
                            _days(signals["cash_conversion_cycle_days"]),
                        ),
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
        with snapshot_middle:
            st.dataframe(
                _summary_table(
                    [
                        (
                            "Revenue CAGR",
                            _ratio(application.get("forecast_revenue_cagr", 0)),
                        ),
                        (
                            "Employee CAGR",
                            _ratio(application.get("forecast_employee_cagr", 0)),
                        ),
                        (
                            "Y5 FCF margin",
                            _ratio(application.get("forecast_fcf_margin_year5", 0)),
                        ),
                        (
                            "Debt reduction",
                            _ratio(application.get("planned_debt_reduction_pct", 0)),
                        ),
                        ("Applicant narrative", _context_completeness(application)),
                        (
                            "Statement anomaly",
                            _score(signals["financial_statement_anomaly_score"]),
                        ),
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
        with snapshot_right:
            st.dataframe(
                _summary_table(
                    [
                        (
                            "Document complete",
                            _score(signals["document_completeness_score"]),
                        ),
                        ("Document risk", _score(signals["document_quality_risk_score"])),
                        ("Process risk", _score(signals["process_integrity_risk_score"])),
                        (
                            "Identity risk",
                            _score(signals["identity_verification_risk_score"]),
                        ),
                        (
                            "Working capital risk",
                            _score(signals["working_capital_pressure_score"]),
                        ),
                        (
                            "Network risk",
                            _score(signals["related_party_network_risk_score"]),
                        ),
                        (
                            "Narrative risk",
                            _score(signals["narrative_consistency_risk_score"]),
                        ),
                    ]
                ),
                width="stretch",
                hide_index=True,
            )

        forecast_label = (
            "Submitted Five-Year Plan"
            if _has_submitted_forecast_plan(application)
            else "Generated Five-Year Forecast"
        )
        with st.expander(forecast_label, expanded=False):
            st.dataframe(
                _forecast_plan_display(application), width="stretch", hide_index=True
            )

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
            {
                "Context": "Loan purpose",
                "Applicant input": application.get("loan_purpose_context", ""),
            },
            {
                "Context": "Current business",
                "Applicant input": application.get("current_business_context", ""),
            },
            {
                "Context": "Future business",
                "Applicant input": application.get("future_business_context", ""),
            },
        ]
        applicant_rows = [row for row in applicant_rows if row["Applicant input"]]
        if applicant_rows:
            with st.expander("Applicant Narrative", expanded=False):
                st.dataframe(applicant_rows, width="stretch", hide_index=True)

        document_rows = [
            {
                "Document": "Financial statements",
                "Present": _yes_no(application.get("financial_statements_uploaded", 0)),
            },
            {
                "Document": "Bank statements",
                "Present": _yes_no(application.get("bank_statements_uploaded", 0)),
            },
            {
                "Document": "Tax return",
                "Present": _yes_no(application.get("tax_return_uploaded", 0)),
            },
            {
                "Document": "Ownership/KYB",
                "Present": _yes_no(application.get("ownership_docs_uploaded", 0)),
            },
            {
                "Document": "Forecast support",
                "Present": _yes_no(application.get("forecast_support_uploaded", 0)),
            },
        ]
        verification_rows = [
            {
                "Check": "Email domain age",
                "Value": format_months(application.get("email_domain_age_months", 0)),
            },
            {
                "Check": "Website age",
                "Value": format_months(application.get("website_age_months", 0)),
            },
            {
                "Check": "Bank account age",
                "Value": format_months(application.get("bank_account_age_months", 0)),
            },
        ]
        with st.expander("Applicant Evidence Review", expanded=False):
            review_left, review_right = st.columns(2)
            with review_left:
                st.dataframe(pd.DataFrame(document_rows), width="stretch", hide_index=True)
            with review_right:
                st.dataframe(
                    pd.DataFrame(verification_rows), width="stretch", hide_index=True
                )

        signal_rows = [
            {
                "Signal": "Debt / revenue",
                "Value": _ratio(signals["debt_to_revenue_ratio"]),
                "What it tells the analyst": "Debt pressure relative to business size.",
            },
            {
                "Signal": "Request / revenue",
                "Value": _ratio(signals["request_to_revenue_ratio"]),
                "What it tells the analyst": "Requested exposure relative to reported revenue.",
            },
            {
                "Signal": "Loan velocity",
                "Value": _score(signals["loan_velocity_score"]),
                "What it tells the analyst": "Recent borrowing intensity and possible credit stacking.",
            },
            {
                "Signal": "Payment stress",
                "Value": _score(signals["payment_stress_score"]),
                "What it tells the analyst": "Late-payment and debt-pressure stress.",
            },
            {
                "Signal": "External financing pressure",
                "Value": _score(signals["external_financing_pressure"]),
                "What it tells the analyst": "Financing pressure from request size, debt, and recent borrowing.",
            },
            {
                "Signal": "Financial distress",
                "Value": _score(signals["financial_distress_score"]),
                "What it tells the analyst": "Combined debt, payment, collateral, and history stress.",
            },
            {
                "Signal": "Transaction anomaly",
                "Value": _score(signals["transaction_anomaly_score"]),
                "What it tells the analyst": "Suspicious transfer and behavior pattern risk.",
            },
            {
                "Signal": "Cash-flow pressure",
                "Value": _score(signals["cash_flow_pressure_score"]),
                "What it tells the analyst": "Negative FCF and burn-rate pressure.",
            },
            {
                "Signal": "Runway risk",
                "Value": _score(signals["runway_risk_score"]),
                "What it tells the analyst": "Short-runway liquidity risk.",
            },
            {
                "Signal": "Cash conversion risk",
                "Value": _score(signals["cash_conversion_risk_score"]),
                "What it tells the analyst": "Weak cash conversion relative to revenue.",
            },
            {
                "Signal": "Forecast aggressiveness",
                "Value": _score(signals["forecast_plan_aggressiveness_score"]),
                "What it tells the analyst": "Ambition of the five-year plan relative to current signals.",
            },
            {
                "Signal": "Forecast execution risk",
                "Value": _score(signals["forecast_execution_risk_score"]),
                "What it tells the analyst": "Risk that the forecast is hard to execute.",
            },
            {
                "Signal": "Hiring efficiency risk",
                "Value": _score(signals["forecast_hiring_efficiency_risk_score"]),
                "What it tells the analyst": "Revenue growth that may be under-supported by employee growth.",
            },
            {
                "Signal": "Debt service plan risk",
                "Value": _score(signals["forecast_debt_service_risk_score"]),
                "What it tells the analyst": "Debt reduction strain under current cash-flow pressure.",
            },
            {
                "Signal": "Interest rate risk",
                "Value": _score(signals["interest_rate_risk_score"]),
                "What it tells the analyst": "Pricing level that can increase repayment burden.",
            },
            {
                "Signal": "Debt service stress",
                "Value": _score(signals["debt_service_stress_score"]),
                "What it tells the analyst": "Coverage pressure from DSCR and the +2% rate stress test.",
            },
            {
                "Signal": "Cash conversion cycle",
                "Value": _days(signals["cash_conversion_cycle_days"]),
                "What it tells the analyst": "Working-capital timing pressure across receivables, inventory, and payables.",
            },
            {
                "Signal": "Document completeness",
                "Value": _score(signals["document_completeness_score"]),
                "What it tells the analyst": "How much of the expected application package is present.",
            },
            {
                "Signal": "Document quality risk",
                "Value": _score(signals["document_quality_risk_score"]),
                "What it tells the analyst": "Missing evidence and document-package gaps.",
            },
            {
                "Signal": "Process integrity risk",
                "Value": _score(signals["process_integrity_risk_score"]),
                "What it tells the analyst": "System-supplied process metadata, where available.",
            },
            {
                "Signal": "Identity verification risk",
                "Value": _score(signals["identity_verification_risk_score"]),
                "What it tells the analyst": "Digital footprint age, bank-account age, and consistency signals.",
            },
            {
                "Signal": "Working-capital pressure",
                "Value": _score(signals["working_capital_pressure_score"]),
                "What it tells the analyst": "Liquidity ratio weakness and cash conversion pressure.",
            },
            {
                "Signal": "Financial statement anomaly",
                "Value": _score(signals["financial_statement_anomaly_score"]),
                "What it tells the analyst": "Revenue/cash-flow mismatch, receivables pressure, and unsupported margin improvement.",
            },
            {
                "Signal": "Related-party network risk",
                "Value": _score(signals["related_party_network_risk_score"]),
                "What it tells the analyst": "Ownership, counterparty concentration, and shared identifier concerns.",
            },
            {
                "Signal": "Narrative consistency risk",
                "Value": _score(signals["narrative_consistency_risk_score"]),
                "What it tells the analyst": "Potential contradictions between applicant context, documents, and financials.",
            },
        ]
        with st.expander("Calculated Risk Signals", expanded=False):
            st.caption(
                "Fraud and anomaly detection are one component of the broader credit-risk assessment. "
                "Most normalized risk scores run from 0.00 to 1.00, where higher means more concern unless the row says otherwise."
            )
            st.dataframe(
                pd.DataFrame(_add_signal_interpretations(signal_rows)),
                width="stretch",
                hide_index=True,
            )

    with detail_tabs[2]:
        _render_ai_output(application, prediction)

    with detail_tabs[3]:
        if not ai_evaluation_package:
            st.warning(
                "Please use the AI before case review. Generate the Internal + SME Reports package in LLM Integration first."
            )
            safe_page_link(
                "pages/5_LLM_Integration.py",
                "Open LLM Integration",
                ":material/psychology:",
            )
            st.session_state.show_review_dialog = False
        action_cols = st.columns([1, 1, 1, 2])
        if action_cols[0].button(
            "Open Case Review",
            width="stretch",
            disabled=not bool(ai_evaluation_package),
            help=(
                "Generate the AI output package before reviewing."
                if not ai_evaluation_package
                else "Open the lender review form."
            ),
        ):
            st.session_state.show_review_dialog = True
            rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
            if rerun:
                rerun()
        report = case_summary(application, prediction, explanation, current_review)
        memo = credit_memo(
            application,
            prediction,
            explanation,
            current_review,
            loan_terms,
            monitoring_rows,
            timeline_rows,
        )
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
            action_cols[3].markdown(
                f"[Open email draft]({st.session_state.last_email_link})"
            )

        if st.session_state.show_review_dialog and ai_evaluation_package:
            with st.expander("Case Review", expanded=True):
                _review_form_body()

        st.subheader("Review and SME Publication")
        _render_review_publication(
            application,
            prediction,
            current_review,
            final_decision,
            publication_status,
            prediction_model_label,
            decision_conditions,
        )

        st.subheader("Decision History Timeline")
        st.dataframe(pd.DataFrame(timeline_rows), width="stretch", hide_index=True)

        st.subheader("Risk Factors")
        st.caption(
            "These are plain-language flags produced by the deterministic model. They explain why the file deserves attention, "
            "but the final lender decision still comes from the saved analyst review."
        )
        if prediction["flags"]:
            for flag in prediction["flags"]:
                st.warning(flag)
        else:
            st.success("No elevated deterministic risk flags were triggered.")

        st.subheader("Similar Historical Applications")
        st.caption(
            "Nearest historical portfolio cases by company profile, requested terms, and credit/anomaly risk signals."
        )
        similar = similar_applications(
            st.session_state.model_bundle,
            applications,
            application,
            model_key=prediction_model_key,
        )
        display_similar = similar.copy()
        for column in ["requested_amount", "free_cash_flow"]:
            if column in display_similar:
                display_similar[column] = display_similar[column].apply(_money)
        if "expected_runway_months" in display_similar:
            display_similar["expected_runway_months"] = display_similar[
                "expected_runway_months"
            ].apply(format_months)
        if "document_completeness_score" in display_similar:
            display_similar["document_completeness_score"] = display_similar[
                "document_completeness_score"
            ].apply(_score)
        for column in ["interest_rate", "forecast_revenue_cagr", "fraud_probability"]:
            if column in display_similar:
                display_similar[column] = display_similar[column].apply(_ratio)
        if "debt_service_coverage_ratio" in display_similar:
            display_similar["debt_service_coverage_ratio"] = display_similar[
                "debt_service_coverage_ratio"
            ].apply(_score)
        display_similar = display_similar.rename(
            columns={"fraud_probability": "Application risk score"}
        )
        st.dataframe(display_similar, width="stretch", hide_index=True)

        st.subheader("Peer Benchmark")
        st.caption(
            "Synthetic peer comparison for the applicant's sector and region where enough peers are available."
        )
        st.dataframe(
            pd.DataFrame(
                peer_benchmark_rows(
                    st.session_state.model_bundle,
                    applications,
                    application,
                    prediction,
                    model_key=prediction_model_key,
                )
            ),
            width="stretch",
            hide_index=True,
        )
    with detail_tabs[4]:
        st.subheader("Score and Review Events")
        _render_score_history(application)
else:
    st.info("Submit the form to score an application.")

persist_demo_state()
