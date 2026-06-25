from datetime import datetime

import pandas as pd
import streamlit as st

from src.constants import *
from src.core.data_pipeline import add_derived_features, build_forecast_table
from src.core.modeling import score_application
from src.core.runtime import bootstrap_state
from src.features.alignment_features import (
    apply_scenario,
    data_source_coverage_rows,
    peer_benchmark_rows,
    sme_action_rows,
)
from src.features.case_workflow import DEMO_SCENARIOS
from src.ui.components import (
    get_profile,
    is_sme_profile,
    render_sidebar,
    safe_page_link,
)
from src.utils.demo_persistence import ensure_demo_session, persist_demo_state
from src.utils.document_examples import build_document_examples
from src.utils.document_storage import (
    DOCUMENT_CATEGORIES,
    document_counts,
    list_documents,
    read_document,
    save_document,
)
from src.utils.formatting import (
    format_currency,
    format_integer,
    format_months,
    format_percent,
    format_score,
)
from src.utils.workflow_transfer import SME_SUBMISSION_SOURCE

st.set_page_config(page_title="Loan Intake Portal", layout="wide")
bootstrap_state()
render_sidebar()

profile = get_profile()
company_mode = is_sme_profile(profile)
applications = st.session_state.seed_data["applications"]
selected_model_key = st.session_state.model_bundle.default_model_key
demo_session_id = ensure_demo_session()
MAX_DOCUMENT_BYTES = 20 * 1024 * 1024
TERM_OPTIONS = [12, 18, 24, 36, 48, 60, 72, 84]
SME_WORKFLOW_STEPS = [
    "1. Company Data",
    "2. Data Connections",
    "3. Credit Health",
    "4. Submit to Lender",
]
EVIDENCE_CASES = {
    "Blank manual intake": {
        "scenario": None,
        "company_name": "",
        "is_blank": True,
        "description": "Start with an empty SME-owned intake and enter your own company data.",
    },
    "Clean evidence": {
        "scenario": "Low-risk established borrower",
        "company_name": "NoviCore Software B.V.",
        "description": "Complete evidence package with strong liquidity and low anomaly pressure.",
    },
    "Neutral evidence": {
        "scenario": "A2M Logistics Loan",
        "company_name": "A2M Logistics B.V.",
        "description": "Mostly complete package with some margin and forecast-support questions.",
    },
    "Risky evidence": {
        "scenario": "Credit stacking case",
        "company_name": "Riverton Buildworks LLC",
        "description": "Debt pressure, negative cash flow, and missing support that need manual review.",
    },
    "Fraudulent evidence": {
        "scenario": "Suspicious transfers",
        "company_name": "Mercado Azul Trading S.A.S.",
        "document_profile": "fraudulent",
        "document_categories": [
            "financial_statements",
            "bank_statements",
            "tax_returns",
            "ownership_kyb",
            "forecast_support",
        ],
        "description": "High anomaly and process-integrity concerns for compliance discussion.",
    },
    "Ambiguous evidence": {
        "scenario": "High country-risk borrower",
        "company_name": "Al Noor Freight Services",
        "description": "Mixed evidence where jurisdiction, identity, and cash-flow context matter.",
    },
}
SAMPLE_CASE_OPTIONS = list(EVIDENCE_CASES)
SELECT_PLACEHOLDER = "Select..."
SAMPLE_DOCUMENT_FIELDS = {
    "financial_statements": "financial_statements_uploaded",
    "bank_statements": "bank_statements_uploaded",
    "tax_returns": "tax_return_uploaded",
    "ownership_kyb": "ownership_docs_uploaded",
    "forecast_support": "forecast_support_uploaded",
}


def _default_company_application():
    application = dict(DEMO_SCENARIOS["A2M Logistics Loan"])
    application.update(
        {
            "application_id": "SME-A2M-001",
            "company_id": "SME-CO-001",
            "company_name": "A2M Logistics B.V.",
            "open_banking_connected": 1,
            "accounting_connected": 1,
            "registry_connected": 1,
            "documents_connected": 0,
            "financial_statements_uploaded": 0,
            "bank_statements_uploaded": 0,
            "tax_return_uploaded": 0,
            "ownership_docs_uploaded": 0,
            "forecast_support_uploaded": 0,
        }
    )
    return application


def _blank_company_application():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]
    return {
        "application_id": f"SME-MANUAL-{timestamp}",
        "company_id": f"SME-CO-MANUAL-{timestamp}",
        "company_name": "",
        "industry": "",
        "region": "",
        "company_type": "",
        "requested_amount": 0.0,
        "term_months": 60,
        "annual_revenue": 0.0,
        "years_in_business": 0.0,
        "existing_debt": 0.0,
        "num_recent_loans": 0,
        "employees": 1,
        "collateral_value": 0.0,
        "collateral_ratio": 0.0,
        "free_cash_flow": 0.0,
        "monthly_burn_rate": 0.0,
        "cash_balance_at_application": 0.0,
        "expected_runway_months": 0.0,
        "current_assets": 0.0,
        "current_liabilities": 0.0,
        "liquid_assets": 0.0,
        "current_ratio": 0.0,
        "quick_ratio": 0.0,
        "receivables_days": 0,
        "payables_days": 0,
        "inventory_days": 0,
        "forecast_revenue_year5": 0.0,
        "forecast_employees_year5": 1,
        "forecast_fcf_year5": 0.0,
        "planned_debt_reduction_amount": 0.0,
        "forecast_revenue_cagr": 0.0,
        "forecast_employee_cagr": 0.0,
        "forecast_fcf_margin_year5": 0.0,
        "planned_debt_reduction_pct": 0.0,
        "loan_purpose_context": "",
        "current_business_context": "",
        "future_business_context": "",
        "ceo_context": "",
        "cfo_context": "",
        "coo_context": "",
        "open_banking_connected": 0,
        "accounting_connected": 0,
        "registry_connected": 0,
        "documents_connected": 0,
        "financial_statements_uploaded": 0,
        "bank_statements_uploaded": 0,
        "tax_return_uploaded": 0,
        "ownership_docs_uploaded": 0,
        "forecast_support_uploaded": 0,
        "document_edit_count": 0,
        "late_stage_change_count": 0,
        "process_deviation_score": 0.0,
        "email_domain_age_months": 0,
        "website_age_months": 0,
        "bank_account_age_months": 0,
        "late_payment_ratio": 0.0,
        "suspicious_transfer_ratio": 0.0,
        "country_risk_score": 0.0,
        "location_mismatch_score": 0.0,
        "duplicate_contact_score": 0.0,
        "related_party_exposure_score": 0.0,
        "counterparty_concentration_score": 0.0,
        "shared_identifier_score": 0.0,
        "narrative_contradiction_score": 0.0,
        "sample_case_name": "Blank manual intake",
        "sample_document_profile": "standard",
        "sample_document_categories": [],
        "source_scenario_name": "Manual input",
        "evidence_case_description": EVIDENCE_CASES["Blank manual intake"][
            "description"
        ],
    }


def _sample_company_application(evidence_case_name):
    evidence_case = EVIDENCE_CASES.get(evidence_case_name)
    if not evidence_case:
        raise ValueError("Choose a named evidence case before loading it.")
    if evidence_case.get("is_blank"):
        return _blank_company_application()

    scenario_name = evidence_case["scenario"]
    sample_values = DEMO_SCENARIOS.get(scenario_name)
    if not isinstance(sample_values, dict):
        raise ValueError("Choose a named sample case before loading it.")

    application = dict(sample_values)
    document_categories = evidence_case.get("document_categories")
    if document_categories:
        for category in document_categories:
            field_name = SAMPLE_DOCUMENT_FIELDS.get(category)
            if field_name:
                application[field_name] = 1

    sample_code = "".join(
        character for character in scenario_name.upper() if character.isalnum()
    )[:8]
    application.update(
        {
            "application_id": (
                "SME-A2M-001"
                if scenario_name == "A2M Logistics Loan"
                else f"SME-{sample_code or 'CASE'}-001"
            ),
            "company_id": (
                "SME-CO-001"
                if scenario_name == "A2M Logistics Loan"
                else f"SME-CO-{sample_code or 'CASE'}"
            ),
            "company_name": evidence_case["company_name"],
            "sample_case_name": evidence_case_name,
            "sample_document_profile": evidence_case.get(
                "document_profile", "standard"
            ),
            "sample_document_categories": list(document_categories or []),
            "source_scenario_name": scenario_name,
            "evidence_case_description": evidence_case["description"],
            "open_banking_connected": int(
                bool(application.get("bank_statements_uploaded", 0))
            ),
            "accounting_connected": int(
                bool(application.get("financial_statements_uploaded", 0))
            ),
            "registry_connected": int(
                bool(application.get("ownership_docs_uploaded", 0))
            ),
            "documents_connected": int(
                any(
                    application.get(field, 0)
                    for field in [
                        "financial_statements_uploaded",
                        "bank_statements_uploaded",
                        "tax_return_uploaded",
                        "ownership_docs_uploaded",
                        "forecast_support_uploaded",
                    ]
                )
            ),
        }
    )
    return application


def _company_application():
    if st.session_state.get("sme_company_application"):
        return dict(st.session_state.sme_company_application)
    application = _default_company_application()
    st.session_state.sme_company_application = dict(application)
    return application


def _store_company_application(application):
    st.session_state.sme_company_application = dict(application)
    persist_demo_state()


def _save_sample_documents(application):
    examples = build_document_examples(application)
    saved_count = 0
    sample_categories = application.get("sample_document_categories") or [
        category
        for category, field_name in SAMPLE_DOCUMENT_FIELDS.items()
        if application.get(field_name)
    ]
    for category in sample_categories:
        field_name = SAMPLE_DOCUMENT_FIELDS.get(category)
        if category not in examples:
            continue
        example = examples[category]
        _, created = save_document(
            demo_session_id,
            application["application_id"],
            category,
            example["file_name"],
            example["content"],
            example["mime_type"],
        )
        if field_name:
            application[field_name] = 1
        if created:
            saved_count += 1
    if sample_categories:
        application["documents_connected"] = 1
    if application.get("bank_statements_uploaded"):
        application["open_banking_connected"] = 1
    if application.get("financial_statements_uploaded"):
        application["accounting_connected"] = 1
    if application.get("ownership_docs_uploaded"):
        application["registry_connected"] = 1
    return saved_count


def _term_option_index(value):
    try:
        term = int(value)
    except (TypeError, ValueError):
        term = 60
    if term in TERM_OPTIONS:
        return TERM_OPTIONS.index(term)
    return min(range(len(TERM_OPTIONS)), key=lambda index: abs(TERM_OPTIONS[index] - term))


def _select_options(values):
    return [SELECT_PLACEHOLDER] + list(values)


def _select_index(options, value):
    return options.index(value) if value in options else 0


def _select_value(value):
    return "" if value == SELECT_PLACEHOLDER else value


def _field_help(field_name):
    return FIELD_HELP.get(
        field_name,
        "Application input used to prepare the SME file before lender submission.",
    )


def _number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _positive(value, default=0.0):
    return max(_number(value, default), 0.0)


def _safe_ratio(numerator, denominator):
    return _positive(numerator) / max(_positive(denominator), 1.0)


def _default_collateral_value(application):
    value = application.get("collateral_value")
    if value is not None:
        return _positive(value)
    return _positive(application.get("collateral_ratio")) * _positive(
        application.get("requested_amount")
    )


def _default_current_liabilities(application):
    value = application.get("current_liabilities")
    if value is not None:
        return max(_positive(value), 1.0)
    annual_revenue = _positive(application.get("annual_revenue"))
    existing_debt = _positive(application.get("existing_debt"))
    return max(existing_debt * 0.25, annual_revenue * 0.12, 1.0)


def _default_current_assets(application):
    value = application.get("current_assets")
    if value is not None:
        return _positive(value)
    return _positive(application.get("current_ratio"), 1.0) * _default_current_liabilities(
        application
    )


def _default_liquid_assets(application):
    value = application.get("liquid_assets")
    if value is not None:
        return _positive(value)
    return _positive(application.get("quick_ratio"), 1.0) * _default_current_liabilities(
        application
    )


def _default_cash_balance(application):
    value = application.get("cash_balance_at_application")
    if value is not None:
        return _positive(value)
    monthly_outflow = _positive(application.get("monthly_burn_rate"))
    runway = _positive(application.get("expected_runway_months"))
    if monthly_outflow and runway:
        return monthly_outflow * runway
    return _positive(application.get("annual_revenue")) * 0.08


def _future_value_from_cagr(base_value, cagr, years=5):
    return _positive(base_value) * (1 + _number(cagr)) ** years


def _default_year5_revenue(application):
    value = application.get("forecast_revenue_year5")
    if value is not None:
        return _positive(value)
    return _future_value_from_cagr(
        application.get("annual_revenue"), application.get("forecast_revenue_cagr")
    )


def _default_year5_employees(application):
    value = application.get("forecast_employees_year5")
    if value is not None:
        return max(int(_positive(value)), 1)
    return max(
        int(
            round(
                _future_value_from_cagr(
                    application.get("employees"),
                    application.get("forecast_employee_cagr"),
                )
            )
        ),
        1,
    )


def _default_year5_free_cash_flow(application):
    value = application.get("forecast_fcf_year5")
    if value is not None:
        return _number(value)
    return _default_year5_revenue(application) * _number(
        application.get("forecast_fcf_margin_year5")
    )


def _default_debt_reduction_amount(application):
    value = application.get("planned_debt_reduction_amount")
    if value is not None:
        return _positive(value)
    return _positive(application.get("existing_debt")) * _positive(
        application.get("planned_debt_reduction_pct")
    )


def _cagr_from_target(base_value, target_value, years=5):
    base = _positive(base_value)
    target = _positive(target_value)
    if base <= 0 or target <= 0:
        return 0.0
    return (target / base) ** (1 / years) - 1


def _rerun():
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun:
        rerun()


def _set_sme_workflow_step(offset):
    current_step = st.session_state.get("sme_workflow_step", SME_WORKFLOW_STEPS[0])
    current_index = (
        SME_WORKFLOW_STEPS.index(current_step)
        if current_step in SME_WORKFLOW_STEPS
        else 0
    )
    next_index = min(max(current_index + offset, 0), len(SME_WORKFLOW_STEPS) - 1)
    st.session_state.sme_workflow_step = SME_WORKFLOW_STEPS[next_index]


def _render_sme_step_buttons(selected_step, location):
    current_index = SME_WORKFLOW_STEPS.index(selected_step)
    nav_cols = st.columns([1, 1, 3])
    if nav_cols[0].button(
        "Previous step",
        disabled=current_index == 0,
        width="stretch",
        on_click=_set_sme_workflow_step,
        args=(-1,),
        key=f"sme_prev_step_{location}",
    ):
        pass
    if nav_cols[1].button(
        "Next step",
        disabled=current_index == len(SME_WORKFLOW_STEPS) - 1,
        width="stretch",
        on_click=_set_sme_workflow_step,
        args=(1,),
        key=f"sme_next_step_{location}",
    ):
        pass


def _render_sme_workflow_nav():
    if "sme_workflow_step" not in st.session_state:
        st.session_state.sme_workflow_step = SME_WORKFLOW_STEPS[0]
    selected_step = st.radio(
        "Workflow step",
        SME_WORKFLOW_STEPS,
        key="sme_workflow_step",
        horizontal=True,
    )
    _render_sme_step_buttons(selected_step, "top")
    return selected_step


def _documents_by_category(documents):
    grouped = {category: [] for category in DOCUMENT_CATEGORIES}
    for document in documents:
        category = document.get("category")
        if category in grouped:
            grouped[category].append(document)
    return grouped


def _render_compact_download(application, document):
    content, metadata = read_document(
        demo_session_id,
        application["application_id"],
        document["document_id"],
    )
    short_name = metadata["original_name"]
    if len(short_name) > 22:
        short_name = short_name[:19] + "..."
    st.caption(short_name)
    st.download_button(
        "Download",
        data=content,
        file_name=metadata["original_name"],
        mime=metadata["content_type"],
        key=f"sme_inline_download_{metadata['document_id']}",
        width="stretch",
    )


def _sync_document_evidence(application):
    counts = document_counts(demo_session_id, application["application_id"])
    documents = list_documents(demo_session_id, application["application_id"])
    application.update(
        {
            "financial_statements_uploaded": int(counts["financial_statements"] > 0),
            "bank_statements_uploaded": int(counts["bank_statements"] > 0),
            "tax_return_uploaded": int(counts["tax_returns"] > 0),
            "ownership_docs_uploaded": int(counts["ownership_kyb"] > 0),
            "forecast_support_uploaded": int(counts["forecast_support"] > 0),
            "documents_connected": int(bool(documents)),
            "stored_document_count": len(documents),
            "stored_documents": documents,
        }
    )
    return counts, documents


def _document_table(documents):
    return pd.DataFrame(
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
    )


def _render_saved_documents(application):
    documents = list_documents(demo_session_id, application["application_id"])
    if not documents:
        st.info("No files have been saved for this application yet.")
        return
    st.dataframe(_document_table(documents), width="stretch", hide_index=True)


def _example_document_table(examples, category_counts):
    return pd.DataFrame(
        [
            {
                "Category": example["label"],
                "Example file": example["file_name"],
                "What it shows": example["description"],
                "Current status": (
                    "Already has saved file"
                    if category_counts.get(category, 0)
                    else "Missing"
                ),
            }
            for category, example in examples.items()
        ]
    )


def _render_document_examples(
    application, category_counts, saved_documents, connection_status, prediction
):
    examples = build_document_examples(application)
    with st.expander("Sample document cases and evidence checklist", expanded=True):
        st.caption(
            "These fictional document cases show what each upload slot expects. Save the example pack to populate "
            "missing categories, or upload your own local demo files below."
        )
        st.dataframe(
            _example_document_table(examples, category_counts),
            width="stretch",
            hide_index=True,
        )

        missing_categories = [
            category for category in examples if category_counts.get(category, 0) == 0
        ]
        button_label = (
            f"Save Example Files for Missing Categories ({len(missing_categories)})"
        )
        if st.button(
            button_label,
            disabled=not missing_categories,
            help="Adds fictional demo files only where this application has no saved file for that document category.",
            width="stretch",
        ):
            saved_count = 0
            duplicate_count = 0
            errors = []
            for category in missing_categories:
                example = examples[category]
                try:
                    _, created = save_document(
                        demo_session_id,
                        application["application_id"],
                        category,
                        example["file_name"],
                        example["content"],
                        example["mime_type"],
                    )
                except (OSError, ValueError) as exc:
                    errors.append(f"{example['file_name']}: {exc}")
                    continue
                if created:
                    saved_count += 1
                else:
                    duplicate_count += 1

            category_counts, saved_documents = _sync_document_evidence(application)
            connection_status["documents"] = bool(saved_documents)
            st.session_state.sme_connection_status = connection_status
            _store_company_application(application)
            prediction = score_application(
                st.session_state.model_bundle, application, model_key=selected_model_key
            )
            if saved_count:
                st.success(
                    f"{saved_count} example file(s) saved to the local application vault."
                )
            if duplicate_count:
                st.info(
                    f"{duplicate_count} example file(s) already existed and were not copied again."
                )
            for error in errors:
                st.error(error)

        if not missing_categories:
            st.caption("All document categories already have at least one saved file.")

    return category_counts, saved_documents, prediction


def _lifecycle_for(application_id):
    return dict(st.session_state.application_lifecycle.get(application_id, {}))


def _update_lifecycle(application_id, **values):
    lifecycle = _lifecycle_for(application_id)
    lifecycle.update(values)
    lifecycle["application_id"] = application_id
    st.session_state.application_lifecycle[application_id] = lifecycle
    return lifecycle


def _render_application_readiness(application, prediction):
    signals = add_derived_features(pd.DataFrame([application])).iloc[0]
    st.info(
        "No lender rating has been published yet. This view helps prepare the application but does not expose "
        "the lender's model score, provisional grade, or internal recommendation."
    )
    readiness_cols = st.columns(4)
    readiness_cols[0].metric(
        "Evidence completeness",
        format_percent(signals.get("document_completeness_score", 0)),
    )
    readiness_cols[1].metric(
        "Expected runway", format_months(application.get("expected_runway_months", 0))
    )
    readiness_cols[2].metric(
        "Stressed DSCR",
        format_score(signals.get("stressed_debt_service_coverage_ratio", 0)),
    )
    readiness_cols[3].metric(
        "Forecast support",
        "Ready" if application.get("forecast_support_uploaded") else "Missing",
    )

    readiness_left, readiness_right = st.columns(2)
    with readiness_left:
        st.subheader("Application Snapshot")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Field": "Company",
                        "Value": application.get("company_name", "Applicant"),
                    },
                    {
                        "Field": "Requested amount",
                        "Value": format_currency(
                            application.get("requested_amount", 0)
                        ),
                    },
                    {
                        "Field": "Annual revenue",
                        "Value": format_currency(application.get("annual_revenue", 0)),
                    },
                    {
                        "Field": "Free cash flow",
                        "Value": format_currency(application.get("free_cash_flow", 0)),
                    },
                    {
                        "Field": "Existing debt",
                        "Value": format_currency(application.get("existing_debt", 0)),
                    },
                ]
            ),
            width="stretch",
            hide_index=True,
        )
    with readiness_right:
        st.subheader("Ways to Strengthen the File")
        st.dataframe(
            pd.DataFrame(sme_action_rows(application, signals, prediction)),
            width="stretch",
            hide_index=True,
        )

    source_tab, forecast_tab = st.tabs(["Evidence Readiness", "Five-Year Plan"])
    with source_tab:
        st.dataframe(
            pd.DataFrame(data_source_coverage_rows(application, signals)),
            width="stretch",
            hide_index=True,
        )
    with forecast_tab:
        forecast = build_forecast_table(pd.DataFrame([application]))
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
        st.dataframe(display, width="stretch", hide_index=True)


def _render_published_rating(application, lifecycle):
    st.success("The lender has published a reviewed rating for this application.")
    published_cols = st.columns(4)
    published_cols[0].metric(
        "Published rating", lifecycle.get("published_grade", "N/A")
    )
    published_cols[1].metric(
        "Lender decision", lifecycle.get("published_decision", "N/A")
    )
    published_cols[2].metric(
        "Risk score",
        (
            format_percent(lifecycle.get("published_score", 0))
            if lifecycle.get("published_score_visible")
            else "Not disclosed"
        ),
    )
    published_cols[3].metric("Published", lifecycle.get("published_at", "N/A"))
    st.subheader("Message from the lender")
    st.info(lifecycle.get("published_message", "The lender has completed its review."))
    published_sme_report = lifecycle.get("published_sme_report")
    if lifecycle.get("published_sme_report_attached") and published_sme_report:
        st.subheader("Your Evaluation Report")
        st.caption(
            "This lender-published report explains the reviewed outcome and practical ways to clarify or strengthen the application."
        )
        with st.container(border=True):
            st.markdown(published_sme_report)
        st.download_button(
            "Download Evaluation Report",
            data=published_sme_report,
            file_name=f"{application.get('application_id', 'application')}_published_evaluation.md",
            mime="text/markdown",
            width="stretch",
        )
        st.caption(
            f"Report source: {lifecycle.get('published_sme_report_source', 'Lender-reviewed draft')}. "
            "The internal lender evaluation and private analyst notes are not included."
        )
    if lifecycle.get("rating_adjusted"):
        st.caption(
            "The published rating reflects the lender's evidence review and differs from the original model grade."
        )
    st.caption(
        "The published rating is the lender's reviewed outcome. Internal model outputs and analyst audit notes remain private."
    )


def _status_label(value, strong=0.8, partial=0.5):
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0
    if number >= strong:
        return "Strong"
    if number >= partial:
        return "Partial"
    return "Needs attention"


def _render_post_publication_health_view(application, prediction, lifecycle):
    signals = add_derived_features(pd.DataFrame([application])).iloc[0]
    published_grade = lifecycle.get("published_grade") or "Published"
    published_decision = lifecycle.get("published_decision") or "Reviewed"
    published_score = lifecycle.get("published_score")
    score_visible = (
        bool(lifecycle.get("published_score_visible")) and published_score is not None
    )

    st.subheader("Plan improvements after the published rating")
    st.caption(
        "Use this applicant-facing planning view after publication to understand which evidence or operating "
        "assumptions could strengthen a future review. It does not change the lender's published decision."
    )
    summary_cols = st.columns(4)
    summary_cols[0].metric("Published rating", published_grade)
    summary_cols[1].metric("Lender decision", published_decision)
    summary_cols[2].metric(
        "Numerical score",
        format_percent(published_score) if score_visible else "Not published",
    )
    summary_cols[3].metric(
        "Runway", format_months(application.get("expected_runway_months", 0))
    )

    overview_left, overview_right = st.columns([1, 1])
    with overview_left:
        st.subheader("Company Snapshot")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Field": "Company",
                        "Value": application.get("company_name", "Applicant"),
                    },
                    {"Field": "Industry", "Value": application.get("industry", "")},
                    {"Field": "Region", "Value": application.get("region", "")},
                    {
                        "Field": "Requested amount",
                        "Value": format_currency(
                            application.get("requested_amount", 0)
                        ),
                    },
                    {
                        "Field": "Annual revenue",
                        "Value": format_currency(application.get("annual_revenue", 0)),
                    },
                    {
                        "Field": "Free cash flow",
                        "Value": format_currency(application.get("free_cash_flow", 0)),
                    },
                    {
                        "Field": "Evidence package",
                        "Value": _status_label(
                            signals.get("document_completeness_score", 0),
                            strong=0.95,
                            partial=0.6,
                        ),
                    },
                    {
                        "Field": "Repayment resilience",
                        "Value": _status_label(
                            signals.get("stressed_debt_service_coverage_ratio", 0),
                            strong=1.2,
                            partial=1.0,
                        ),
                    },
                ]
            ),
            width="stretch",
            hide_index=True,
        )
    with overview_right:
        st.subheader("Most Useful Next Actions")
        st.dataframe(
            pd.DataFrame(sme_action_rows(application, signals, prediction)),
            width="stretch",
            hide_index=True,
        )

    st.subheader("What-If Simulation")
    st.caption(
        "Adjust the plan to see how stronger evidence or operating assumptions could affect a future readiness band. "
        "This is directional and is not a new lender decision."
    )
    scenario_left, scenario_middle, scenario_right = st.columns(3)
    with scenario_left:
        revenue_growth_delta = st.slider(
            "Revenue growth change",
            -0.15,
            0.20,
            0.00,
            0.01,
            format="%.2f",
            key="sme_post_revenue_growth",
        )
        fcf_margin_delta = st.slider(
            "FCF margin change",
            -0.10,
            0.15,
            0.00,
            0.01,
            format="%.2f",
            key="sme_post_fcf_margin",
        )
    with scenario_middle:
        operating_cost_pressure = st.slider(
            "Operating cost pressure",
            0.00,
            0.15,
            0.00,
            0.01,
            format="%.2f",
            key="sme_post_cost_pressure",
        )
        debt_reduction_delta = st.slider(
            "Debt reduction plan change",
            -0.20,
            0.35,
            0.00,
            0.05,
            format="%.2f",
            key="sme_post_debt_reduction",
        )
    with scenario_right:
        contract_evidence = st.selectbox(
            "Contract evidence",
            ["Current file", "Signed and documented", "Unconfirmed"],
            key="sme_post_contract_evidence",
        )
        complete_documents = st.checkbox(
            "Complete missing documents", value=False, key="sme_post_complete_documents"
        )

    scenario_application = apply_scenario(
        application,
        revenue_growth_delta=revenue_growth_delta,
        fcf_margin_delta=fcf_margin_delta,
        operating_cost_pressure=operating_cost_pressure,
        contract_evidence=contract_evidence,
        complete_documents=complete_documents,
        debt_reduction_delta=debt_reduction_delta,
    )
    scenario_prediction = score_application(
        st.session_state.model_bundle,
        scenario_application,
        model_key=prediction.get("model_key", selected_model_key),
    )
    scenario_signals = add_derived_features(pd.DataFrame([scenario_application])).iloc[
        0
    ]
    scenario_rows = [
        {
            "Measure": "Rating / planning band",
            "Published file": published_grade,
            "What-if": scenario_prediction.get("grade", ""),
        },
        {
            "Measure": "Free cash flow",
            "Published file": format_currency(application.get("free_cash_flow", 0)),
            "What-if": format_currency(scenario_application.get("free_cash_flow", 0)),
        },
        {
            "Measure": "Forecast support",
            "Published file": (
                "Ready" if application.get("forecast_support_uploaded") else "Missing"
            ),
            "What-if": (
                "Ready"
                if scenario_application.get("forecast_support_uploaded")
                else "Missing"
            ),
        },
        {
            "Measure": "Evidence package",
            "Published file": _status_label(
                signals.get("document_completeness_score", 0), strong=0.95, partial=0.6
            ),
            "What-if": _status_label(
                scenario_signals.get("document_completeness_score", 0),
                strong=0.95,
                partial=0.6,
            ),
        },
        {
            "Measure": "Repayment resilience",
            "Published file": _status_label(
                signals.get("stressed_debt_service_coverage_ratio", 0),
                strong=1.2,
                partial=1.0,
            ),
            "What-if": _status_label(
                scenario_signals.get("stressed_debt_service_coverage_ratio", 0),
                strong=1.2,
                partial=1.0,
            ),
        },
    ]
    st.dataframe(pd.DataFrame(scenario_rows), width="stretch", hide_index=True)
    st.caption(
        f"Directional what-if band: {scenario_prediction['grade']}. This is a planning aid only; "
        "the published lender rating remains unchanged."
    )

    benchmark_tab, sources_tab, forecast_tab = st.tabs(
        ["Peer Benchmark", "Evidence Sources", "Five-Year View"]
    )
    with benchmark_tab:
        st.caption(
            "Synthetic applicant-facing peer context for the sector and region. Internal risk scores are not shown here."
        )
        benchmark_rows = [
            row
            for row in peer_benchmark_rows(
                st.session_state.model_bundle,
                applications,
                application,
                prediction,
                model_key=prediction.get("model_key", selected_model_key),
            )
            if row.get("Benchmark")
            in {"Requested amount", "Stressed DSCR", "Document completeness"}
        ]
        st.dataframe(
            pd.DataFrame(benchmark_rows),
            width="stretch",
            hide_index=True,
        )
    with sources_tab:
        st.caption(
            "Demo connection coverage. Production would use consented bank, accounting, registry, and document APIs."
        )
        st.dataframe(
            pd.DataFrame(data_source_coverage_rows(application, signals)),
            width="stretch",
            hide_index=True,
        )
    with forecast_tab:
        forecast = build_forecast_table(pd.DataFrame([application]))
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
        st.dataframe(display, width="stretch", hide_index=True)


if company_mode:
    st.title("Loan Intake Portal")
    st.caption(
        "Enter company data, manage evidence connections, review credit health, and submit the file to a lender."
    )
    st.info(
        "This is a role-based MVP workflow. Connections and consent are simulated for the demo; "
        "no real bank, accounting, registry, or customer data is transmitted."
    )

    application = _company_application()
    document_category_counts, saved_documents = _sync_document_evidence(application)
    _store_company_application(application)
    lifecycle = _lifecycle_for(application["application_id"])
    connection_status = {
        "open_banking": bool(
            application.get(
                "open_banking_connected", application.get("bank_statements_uploaded", 0)
            )
        ),
        "accounting": bool(
            application.get(
                "accounting_connected",
                application.get("financial_statements_uploaded", 0),
            )
        ),
        "registry": bool(
            application.get(
                "registry_connected", application.get("ownership_docs_uploaded", 0)
            )
        ),
        "documents": bool(saved_documents),
        **st.session_state.get("sme_connection_status", {}),
    }
    connection_status["documents"] = bool(saved_documents)
    prediction = score_application(
        st.session_state.model_bundle, application, model_key=selected_model_key
    )

    profile_complete = bool(
        application.get("company_name") and application.get("annual_revenue")
    )
    connected_count = sum(
        bool(connection_status.get(key))
        for key in ["open_banking", "accounting", "registry", "documents"]
    )
    submitted_count = len(st.session_state.sme_submission_history)
    progress_cols = st.columns(4)
    progress_cols[0].metric(
        "Company profile", "Complete" if profile_complete else "Incomplete"
    )
    progress_cols[1].metric("Data connections", f"{connected_count}/4")
    progress_cols[2].metric("Application status", lifecycle.get("status", "Draft"))
    progress_cols[3].metric("Lender submissions", format_integer(submitted_count))

    selected_step = _render_sme_workflow_nav()

    if selected_step == SME_WORKFLOW_STEPS[0]:
        st.subheader("Company and loan application data")
        st.caption(
            "The SME enters and owns this information before sharing the application with a lender."
        )
        industries = sorted(applications["industry"].dropna().unique())
        regions = sorted(applications["region"].dropna().unique())
        company_types = sorted(applications["company_type"].dropna().unique())
        industry_options = _select_options(industries)
        region_options = _select_options(regions)
        company_type_options = _select_options(company_types)

        with st.expander("Start or load intake", expanded=False):
            st.caption(
                "Start from a blank manual intake or load a prepared evidence case on the SME side."
            )
            evidence_case_name = st.selectbox(
                "Intake option", SAMPLE_CASE_OPTIONS, key="sme_sample_case_name"
            )
            st.caption(EVIDENCE_CASES[evidence_case_name]["description"])
            if st.button("Load Selected Intake", width="stretch"):
                try:
                    application = _sample_company_application(evidence_case_name)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    # Keep sample cases SME-owned; the lender receives only the submitted snapshot.
                    document_seed_error = None
                    try:
                        saved_sample_documents = _save_sample_documents(application)
                    except (OSError, ValueError) as exc:
                        saved_sample_documents = 0
                        document_seed_error = str(exc)
                    st.session_state.sme_connection_status = {
                        "open_banking": bool(application.get("open_banking_connected")),
                        "open_banking_consent": bool(
                            application.get("open_banking_connected")
                        ),
                        "accounting": bool(application.get("accounting_connected")),
                        "registry": bool(application.get("registry_connected")),
                        "documents": bool(application.get("documents_connected")),
                        "refreshed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    _store_company_application(application)
                    _update_lifecycle(
                        application["application_id"],
                        status="Draft",
                        company_name=application["company_name"],
                        sample_case_name=evidence_case_name,
                    )
                    if EVIDENCE_CASES[evidence_case_name].get("is_blank"):
                        st.success(
                            "Blank manual intake started. Enter company data and upload your own evidence files."
                        )
                    else:
                        st.success(
                            f"{evidence_case_name} loaded into the SME intake. "
                            f"{saved_sample_documents} sample evidence file(s) were saved."
                        )
                    if document_seed_error:
                        st.warning(
                            f"The intake loaded, but sample evidence files could not all be saved: {document_seed_error}"
                        )
                    rerun = getattr(st, "rerun", None) or getattr(
                        st, "experimental_rerun", None
                    )
                    if rerun:
                        rerun()

        with st.form("sme_company_data_form"):
            company_left, company_right = st.columns(2)
            with company_left:
                company_name = st.text_input(
                    "Company name",
                    value=str(application.get("company_name", "")),
                    help=_field_help("company_name"),
                )
                industry = st.selectbox(
                    "Industry",
                    industry_options,
                    index=_select_index(industry_options, application.get("industry")),
                    help=_field_help("industry"),
                )
                company_type = st.selectbox(
                    "Company type",
                    company_type_options,
                    index=_select_index(
                        company_type_options, application.get("company_type")
                    ),
                    help=_field_help("company_type"),
                )
                years_in_business = st.number_input(
                    "Years in business",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(application.get("years_in_business", 0)),
                    help=_field_help("years_in_business"),
                )
                employees = st.number_input(
                    "Employees",
                    min_value=1,
                    max_value=100000,
                    value=int(application.get("employees", 1)),
                    help=_field_help("employees"),
                )
            with company_right:
                region = st.selectbox(
                    "Region",
                    region_options,
                    index=_select_index(region_options, application.get("region")),
                    help=_field_help("region"),
                )
                annual_revenue = st.number_input(
                    "Annual revenue (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=float(application.get("annual_revenue", 0)),
                    step=50_000.0,
                    help=_field_help("annual_revenue"),
                )
                existing_debt = st.number_input(
                    "Existing debt (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=float(application.get("existing_debt", 0)),
                    step=25_000.0,
                    help=_field_help("existing_debt"),
                )
                requested_amount = st.number_input(
                    "Requested loan amount (EUR)",
                    min_value=0.0,
                    max_value=100_000_000.0,
                    value=float(application.get("requested_amount", 0)),
                    step=25_000.0,
                    help=_field_help("requested_amount"),
                )
                term_months = st.selectbox(
                    "Requested term",
                    TERM_OPTIONS,
                    index=_term_option_index(application.get("term_months", 60)),
                    format_func=lambda value: f"{value} months",
                    help=_field_help("term_months"),
                )

            st.markdown("**Loan request and collateral**")
            st.caption(
                "The company requests amount, term, and collateral details. Interest pricing is set by the lender during review."
            )
            loan_left, loan_right = st.columns(2)
            with loan_left:
                collateral_value = st.number_input(
                    "Estimated collateral value (EUR)",
                    min_value=0.0,
                    max_value=250_000_000.0,
                    value=_default_collateral_value(application),
                    step=25_000.0,
                    help=_field_help("collateral_value"),
                )
            with loan_right:
                num_recent_loans = st.number_input(
                    "New business loans in last 12 months",
                    min_value=0,
                    max_value=20,
                    value=int(application.get("num_recent_loans", 0)),
                    step=1,
                    help=_field_help("num_recent_loans"),
                )

            st.markdown("**Financial snapshot**")
            finance_left, finance_middle, finance_right = st.columns(3)
            with finance_left:
                free_cash_flow = st.number_input(
                    "Free cash flow (EUR)",
                    min_value=-100_000_000.0,
                    max_value=1_000_000_000.0,
                    value=float(application.get("free_cash_flow", 0)),
                    step=25_000.0,
                    help=_field_help("free_cash_flow"),
                )
                monthly_burn_rate = st.number_input(
                    "Average monthly cash outflow (EUR)",
                    min_value=0.0,
                    max_value=100_000_000.0,
                    value=float(application.get("monthly_burn_rate", 0)),
                    step=5_000.0,
                    help=_field_help("monthly_burn_rate"),
                )
            with finance_middle:
                current_assets = st.number_input(
                    "Current assets (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=_default_current_assets(application),
                    step=25_000.0,
                    help=_field_help("current_assets"),
                )
                current_liabilities = st.number_input(
                    "Current liabilities (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=_default_current_liabilities(application),
                    step=25_000.0,
                    help=_field_help("current_liabilities"),
                )
            with finance_right:
                liquid_assets = st.number_input(
                    "Cash and near-cash assets (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=_default_liquid_assets(application),
                    step=25_000.0,
                    help=_field_help("liquid_assets"),
                )
                cash_balance = st.number_input(
                    "Current cash balance (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=_default_cash_balance(application),
                    step=25_000.0,
                    help=_field_help("cash_balance_at_application"),
                )

            st.markdown("**Working capital**")
            wc_left, wc_middle, wc_right = st.columns(3)
            with wc_left:
                receivables_days = st.number_input(
                    "Receivables days",
                    min_value=0,
                    max_value=240,
                    value=int(application.get("receivables_days", 45)),
                    step=1,
                    help=_field_help("receivables_days"),
                )
            with wc_middle:
                payables_days = st.number_input(
                    "Payables days",
                    min_value=0,
                    max_value=240,
                    value=int(application.get("payables_days", 45)),
                    step=1,
                    help=_field_help("payables_days"),
                )
            with wc_right:
                inventory_days = st.number_input(
                    "Inventory days",
                    min_value=0,
                    max_value=240,
                    value=int(application.get("inventory_days", 30)),
                    step=1,
                    help=_field_help("inventory_days"),
                )

            st.markdown("**Five-year plan**")
            plan_left, plan_middle, plan_right, plan_fourth = st.columns(4)
            with plan_left:
                forecast_revenue_year5 = st.number_input(
                    "Projected year 5 revenue (EUR)",
                    min_value=0.0,
                    max_value=2_000_000_000.0,
                    value=_default_year5_revenue(application),
                    step=50_000.0,
                    help=_field_help("forecast_revenue_year5"),
                )
            with plan_middle:
                forecast_employees_year5 = st.number_input(
                    "Projected year 5 employees",
                    min_value=1,
                    max_value=100000,
                    value=_default_year5_employees(application),
                    step=1,
                    help=_field_help("forecast_employees_year5"),
                )
            with plan_right:
                forecast_fcf_year5 = st.number_input(
                    "Projected year 5 free cash flow (EUR)",
                    min_value=-100_000_000.0,
                    max_value=1_000_000_000.0,
                    value=_default_year5_free_cash_flow(application),
                    step=25_000.0,
                    help=_field_help("forecast_fcf_year5"),
                )
            with plan_fourth:
                planned_debt_reduction_amount = st.number_input(
                    "Planned debt paydown (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=_default_debt_reduction_amount(application),
                    step=25_000.0,
                    help=_field_help("planned_debt_reduction_amount"),
                )

            loan_purpose_context = st.text_area(
                "What will the financing be used for?",
                value=str(application.get("loan_purpose_context", "")),
                help=_field_help("loan_purpose_context"),
            )
            current_business_context = st.text_area(
                "Current business context",
                value=str(application.get("current_business_context", "")),
                help=_field_help("current_business_context"),
            )
            future_business_context = st.text_area(
                "Future plan and assumptions",
                value=str(application.get("future_business_context", "")),
                help=_field_help("future_business_context"),
            )

            st.markdown("**Executive context**")
            exec_left, exec_middle, exec_right = st.columns(3)
            with exec_left:
                ceo_context = st.text_area(
                    "CEO context",
                    value=str(application.get("ceo_context", "")),
                    height=110,
                    help=_field_help("ceo_context"),
                )
            with exec_middle:
                cfo_context = st.text_area(
                    "CFO context",
                    value=str(application.get("cfo_context", "")),
                    height=110,
                    help=_field_help("cfo_context"),
                )
            with exec_right:
                coo_context = st.text_area(
                    "COO context",
                    value=str(application.get("coo_context", "")),
                    height=110,
                    help=_field_help("coo_context"),
                )

            saved_company_data = st.form_submit_button(
                "Save Company Data", width="stretch"
            )

        if saved_company_data:
            application.update(
                {
                    "company_name": company_name.strip(),
                    "industry": _select_value(industry),
                    "region": _select_value(region),
                    "company_type": _select_value(company_type),
                    "years_in_business": years_in_business,
                    "employees": employees,
                    "annual_revenue": annual_revenue,
                    "existing_debt": existing_debt,
                    "requested_amount": requested_amount,
                    "term_months": term_months,
                    "collateral_value": collateral_value,
                    "collateral_ratio": _safe_ratio(collateral_value, requested_amount),
                    "free_cash_flow": free_cash_flow,
                    "monthly_burn_rate": monthly_burn_rate,
                    "cash_balance_at_application": cash_balance,
                    "cash_flow_to_revenue_ratio": free_cash_flow
                    / max(annual_revenue, 1),
                    "num_recent_loans": num_recent_loans,
                    "current_assets": current_assets,
                    "current_liabilities": current_liabilities,
                    "liquid_assets": liquid_assets,
                    "current_ratio": _safe_ratio(
                        current_assets, current_liabilities
                    ),
                    "quick_ratio": _safe_ratio(liquid_assets, current_liabilities),
                    "receivables_days": receivables_days,
                    "payables_days": payables_days,
                    "inventory_days": inventory_days,
                    "expected_runway_months": _safe_ratio(
                        cash_balance, monthly_burn_rate
                    ),
                    "forecast_revenue_year5": forecast_revenue_year5,
                    "forecast_employees_year5": forecast_employees_year5,
                    "forecast_fcf_year5": forecast_fcf_year5,
                    "planned_debt_reduction_amount": planned_debt_reduction_amount,
                    "forecast_revenue_cagr": _cagr_from_target(
                        annual_revenue, forecast_revenue_year5
                    ),
                    "forecast_employee_cagr": _cagr_from_target(
                        employees, forecast_employees_year5
                    ),
                    "forecast_fcf_margin_year5": forecast_fcf_year5
                    / max(forecast_revenue_year5, 1),
                    "planned_debt_reduction_pct": planned_debt_reduction_amount
                    / max(existing_debt, 1),
                    "loan_purpose_context": loan_purpose_context,
                    "current_business_context": current_business_context,
                    "future_business_context": future_business_context,
                    "ceo_context": ceo_context,
                    "cfo_context": cfo_context,
                    "coo_context": coo_context,
                    "company_data_updated_at": datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                }
            )
            _store_company_application(application)
            prediction = score_application(
                st.session_state.model_bundle, application, model_key=selected_model_key
            )
            st.success(
                "Company data saved. The credit-health preview has been recalculated."
            )

    if selected_step == SME_WORKFLOW_STEPS[1]:
        st.subheader("Company-controlled data connections")
        st.caption(
            "These controls demonstrate consent and source selection. Production integrations would use authorised providers and secure OAuth flows."
        )
        with st.form("sme_connections_form"):
            open_banking = st.checkbox(
                "PSD2 / Open Banking",
                value=bool(connection_status.get("open_banking")),
                help="Share consented account balances and transaction history.",
            )
            open_banking_consent = st.checkbox(
                "I consent to sharing the selected bank-account data for this application",
                value=bool(
                    connection_status.get(
                        "open_banking_consent", connection_status.get("open_banking")
                    )
                ),
            )
            accounting = st.checkbox(
                "Accounting platform",
                value=bool(connection_status.get("accounting")),
                help="Simulates Exact, Twinfield, Visma, or Xero financial data.",
            )
            registry = st.checkbox(
                "Registry and KYB",
                value=bool(connection_status.get("registry")),
                help="Simulates company registry, ownership, and identity verification.",
            )
            saved_connections = st.form_submit_button(
                "Save Connections and Refresh Evidence", width="stretch"
            )

        if saved_connections:
            if open_banking and not open_banking_consent:
                st.error("Open Banking requires explicit company consent.")
            else:
                refreshed_at = datetime.now().strftime("%Y-%m-%d %H:%M")
                connection_status = {
                    "open_banking": open_banking,
                    "open_banking_consent": open_banking_consent,
                    "accounting": accounting,
                    "registry": registry,
                    "documents": bool(saved_documents),
                    "refreshed_at": refreshed_at,
                }
                st.session_state.sme_connection_status = connection_status
                application.update(
                    {
                        "open_banking_connected": int(open_banking),
                        "accounting_connected": int(accounting),
                        "registry_connected": int(registry),
                        "connection_refreshed_at": refreshed_at,
                    }
                )
                _sync_document_evidence(application)
                _store_company_application(application)
                prediction = score_application(
                    st.session_state.model_bundle,
                    application,
                    model_key=selected_model_key,
                )
                st.success("Connections saved and evidence coverage refreshed.")

        st.subheader("Sample document cases")
        st.caption(
            "Use this area to inspect or seed example evidence before uploading files to the matching slots."
        )
        document_category_counts, saved_documents, prediction = (
            _render_document_examples(
                application,
                document_category_counts,
                saved_documents,
                connection_status,
                prediction,
            )
        )

        st.subheader("Saved application files")
        st.caption(
            "These uploads are written to the local demo-session vault. They survive refresh and sign-out, "
            "are excluded from Git, and are removed only when Clear Session is used."
        )
        upload_columns = st.columns(2)
        upload_widgets = {}
        category_items = list(DOCUMENT_CATEGORIES.items())
        saved_by_category = _documents_by_category(saved_documents)
        for index, (category, label) in enumerate(category_items):
            with upload_columns[index % 2]:
                uploader_col, download_col = st.columns([3, 1.15])
                with uploader_col:
                    upload_widgets[category] = st.file_uploader(
                        label,
                        type=ALLOWED_DOCUMENT_TYPES,
                        accept_multiple_files=True,
                        key=f"sme_upload_{category}",
                        help=f"Upload {label.lower()} for this application.",
                    )
                with download_col:
                    category_documents = saved_by_category.get(category, [])
                    if category_documents:
                        _render_compact_download(application, category_documents[0])
                    else:
                        st.caption("No file loaded")

        if st.button("Save Uploaded Files", type="primary", width="stretch"):
            saved_count = 0
            duplicate_count = 0
            errors = []
            for category, uploaded_files in upload_widgets.items():
                for uploaded_file in uploaded_files or []:
                    content = uploaded_file.getvalue()
                    if len(content) > MAX_DOCUMENT_BYTES:
                        errors.append(f"{uploaded_file.name} exceeds the 20 MB limit.")
                        continue
                    try:
                        _, created = save_document(
                            demo_session_id,
                            application["application_id"],
                            category,
                            uploaded_file.name,
                            content,
                            uploaded_file.type,
                        )
                    except (OSError, ValueError) as exc:
                        errors.append(f"{uploaded_file.name}: {exc}")
                        continue
                    if created:
                        saved_count += 1
                    else:
                        duplicate_count += 1

            document_category_counts, saved_documents = _sync_document_evidence(
                application
            )
            connection_status["documents"] = bool(saved_documents)
            st.session_state.sme_connection_status = connection_status
            _store_company_application(application)
            prediction = score_application(
                st.session_state.model_bundle, application, model_key=selected_model_key
            )
            if saved_count:
                st.success(
                    f"{saved_count} file(s) saved to the local application vault."
                )
            if duplicate_count:
                st.info(
                    f"{duplicate_count} duplicate file(s) were already saved and were not copied again."
                )
            for error in errors:
                st.error(error)

        _render_saved_documents(application)

        current_signals = add_derived_features(pd.DataFrame([application])).iloc[0]
        st.dataframe(
            pd.DataFrame(data_source_coverage_rows(application, current_signals)),
            width="stretch",
            hide_index=True,
        )
        if connection_status.get("refreshed_at"):
            st.caption(f"Last evidence refresh: {connection_status['refreshed_at']}")

    if selected_step == SME_WORKFLOW_STEPS[2]:
        st.subheader("Application status and credit health")
        lifecycle = _lifecycle_for(application["application_id"])
        if lifecycle.get("status") == "Rating published":
            _render_published_rating(application, lifecycle)
            _render_post_publication_health_view(application, prediction, lifecycle)
        else:
            _render_application_readiness(application, prediction)

    if selected_step == SME_WORKFLOW_STEPS[3]:
        st.subheader("Submit the application to lender review")
        st.caption(
            "Submission shares the current company snapshot and connection statuses with the lender-side Personal Workspace."
        )
        submission_rows = [
            {
                "Check": "Company identity",
                "Status": "Ready" if application.get("company_name") else "Missing",
            },
            {
                "Check": "Loan request",
                "Status": (
                    "Ready" if application.get("requested_amount", 0) > 0 else "Missing"
                ),
            },
            {
                "Check": "Open Banking consent",
                "Status": (
                    "Ready"
                    if connection_status.get("open_banking_consent")
                    else "Optional"
                ),
            },
            {
                "Check": "Evidence connections",
                "Status": f"{connected_count}/4 connected",
            },
            {
                "Check": "Lender rating",
                "Status": lifecycle.get("status", "Not submitted"),
            },
        ]
        st.dataframe(pd.DataFrame(submission_rows), width="stretch", hide_index=True)
        submission_confirmed = st.checkbox(
            "I confirm that the company information is accurate for this demo submission.",
            key="sme_submission_confirmation",
        )
        if st.button(
            "Submit Application to Lender Review",
            width="stretch",
            disabled=not submission_confirmed,
            type="primary",
        ):
            submission = {
                "submission_id": f"SUB-{len(st.session_state.sme_submission_history) + 1:03d}",
                "application_id": application["application_id"],
                "company_name": application["company_name"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "connection_count": connected_count,
                "document_count": len(saved_documents),
                "application_snapshot": dict(application),
                "status": "Submitted to lender review",
            }
            st.session_state.sme_submission_history.append(submission)
            st.session_state.active_queue_application = dict(application)
            st.session_state.active_intake_source = SME_SUBMISSION_SOURCE
            _update_lifecycle(
                application["application_id"],
                status="Submitted to lender review",
                submitted_at=submission["timestamp"],
                submission_id=submission["submission_id"],
                company_name=application["company_name"],
                published_at=None,
                published_grade=None,
                published_decision=None,
                published_message=None,
                published_score_visible=False,
                published_score=None,
                published_sme_report=None,
                published_sme_report_attached=False,
                published_sme_report_source=None,
                evaluation_package_id=None,
            )
            persist_demo_state()
            st.success(
                f"{submission['submission_id']} submitted. Sign out and use the Lender analyst account to continue the case."
            )

        if st.session_state.sme_submission_history:
            st.markdown("**Submission history**")
            st.dataframe(
                pd.DataFrame(st.session_state.sme_submission_history),
                width="stretch",
                hide_index=True,
            )
    st.divider()
    _render_sme_step_buttons(selected_step, "bottom")
else:
    st.title("Loan Intake Portal")
    st.warning(
        "This page is available only to the SME company account. The lender workspace no longer includes an SME "
        "Credit Health preview."
    )
    st.write(
        "Use Personal Workspace for scoring, document verification, case review, and publication. "
        "Use the SME account to enter company data, upload documents, and view published ratings."
    )
    link_cols = st.columns(3)
    with link_cols[0]:
        safe_page_link(
            "pages/1_Personal_Workspace.py",
            "Open Personal Workspace",
            ":material/person_search:",
        )
    with link_cols[1]:
        safe_page_link(
            "pages/5_LLM_Integration.py",
            "Open LLM Integration",
            ":material/psychology:",
        )
    with link_cols[2]:
        safe_page_link("pages/10_Tutorials.py", "Open Tutorials", ":material/school:")
