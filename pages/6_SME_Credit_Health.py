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

st.set_page_config(page_title="SME Company Portal", layout="wide")
bootstrap_state()
render_sidebar()

profile = get_profile()
company_mode = is_sme_profile(profile)
applications = st.session_state.seed_data["applications"]
selected_model_key = st.session_state.model_bundle.default_model_key
demo_session_id = ensure_demo_session()
MAX_DOCUMENT_BYTES = 20 * 1024 * 1024
TERM_OPTIONS = [12, 18, 24, 36, 48, 60, 72, 84]
SAMPLE_CASE_OPTIONS = [
    name for name, values in DEMO_SCENARIOS.items() if isinstance(values, dict)
]
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
            "company_name": "A2M Logistics",
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


def _sample_company_application(scenario_name):
    sample_values = DEMO_SCENARIOS.get(scenario_name)
    if not isinstance(sample_values, dict):
        raise ValueError("Choose a named sample case before loading it.")

    application = dict(sample_values)
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
            "company_name": (
                "A2M Logistics"
                if scenario_name == "A2M Logistics Loan"
                else scenario_name
            ),
            "sample_case_name": scenario_name,
            "open_banking_connected": int(
                bool(sample_values.get("bank_statements_uploaded", 0))
            ),
            "accounting_connected": int(
                bool(sample_values.get("financial_statements_uploaded", 0))
            ),
            "registry_connected": int(
                bool(sample_values.get("ownership_docs_uploaded", 0))
            ),
            "documents_connected": int(
                any(
                    sample_values.get(field, 0)
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
    for category, field_name in SAMPLE_DOCUMENT_FIELDS.items():
        if not application.get(field_name):
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
        if created:
            saved_count += 1
    return saved_count


def _term_option_index(value):
    try:
        term = int(value)
    except (TypeError, ValueError):
        term = 60
    if term in TERM_OPTIONS:
        return TERM_OPTIONS.index(term)
    return min(range(len(TERM_OPTIONS)), key=lambda index: abs(TERM_OPTIONS[index] - term))


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
    for document in documents:
        content, metadata = read_document(
            demo_session_id,
            application["application_id"],
            document["document_id"],
        )
        st.download_button(
            f"Download {metadata['category_label']}: {metadata['original_name']}",
            data=content,
            file_name=metadata["original_name"],
            mime=metadata["content_type"],
            key=f"sme_download_{metadata['document_id']}",
            width="stretch",
        )


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
    with st.expander(
        "Example files and evidence checklist", expanded=not bool(saved_documents)
    ):
        st.caption(
            "Download fictional CSV examples to see the expected structure. For demo runs, you can also save "
            "the example pack into missing categories; those files are written through the same local vault as uploads."
        )
        st.dataframe(
            _example_document_table(examples, category_counts),
            width="stretch",
            hide_index=True,
        )

        download_columns = st.columns(2)
        for index, (category, example) in enumerate(examples.items()):
            with download_columns[index % 2]:
                st.download_button(
                    f"Download example: {example['label']}",
                    data=example["content"],
                    file_name=example["file_name"],
                    mime=example["mime_type"],
                    key=f"sme_example_download_{category}",
                    width="stretch",
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
    st.title(f"{profile['name']} Company Portal")
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

    setup_tab, connections_tab, health_tab, submit_tab = st.tabs(
        [
            "1. Company Data",
            "2. Data Connections",
            "3. Credit Health",
            "4. Submit to Lender",
        ]
    )

    with setup_tab:
        st.subheader("Company and loan application data")
        st.caption(
            "The SME enters and owns this information before sharing the application with a lender."
        )
        industries = sorted(applications["industry"].dropna().unique())
        regions = sorted(applications["region"].dropna().unique())
        company_types = sorted(applications["company_type"].dropna().unique())

        with st.expander("Load sample intake", expanded=False):
            st.caption(
                "Sample intake starts on the SME side. After loading it, review the data and submit the snapshot to the lender."
            )
            sample_case_name = st.selectbox(
                "Sample case", SAMPLE_CASE_OPTIONS, key="sme_sample_case_name"
            )
            if st.button("Load Sample Case", width="stretch"):
                try:
                    application = _sample_company_application(sample_case_name)
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
                        sample_case_name=sample_case_name,
                    )
                    st.success(
                        f"{sample_case_name} loaded into the SME intake. "
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
                    "Company name", value=str(application.get("company_name", ""))
                )
                industry = st.selectbox(
                    "Industry",
                    industries,
                    index=(
                        industries.index(application.get("industry"))
                        if application.get("industry") in industries
                        else 0
                    ),
                )
                company_type = st.selectbox(
                    "Company type",
                    company_types,
                    index=(
                        company_types.index(application.get("company_type"))
                        if application.get("company_type") in company_types
                        else 0
                    ),
                )
                years_in_business = st.number_input(
                    "Years in business",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(application.get("years_in_business", 0)),
                )
                employees = st.number_input(
                    "Employees",
                    min_value=1,
                    max_value=100000,
                    value=int(application.get("employees", 1)),
                )
            with company_right:
                region = st.selectbox(
                    "Region",
                    regions,
                    index=(
                        regions.index(application.get("region"))
                        if application.get("region") in regions
                        else 0
                    ),
                )
                annual_revenue = st.number_input(
                    "Annual revenue (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=float(application.get("annual_revenue", 0)),
                    step=50_000.0,
                )
                existing_debt = st.number_input(
                    "Existing debt (EUR)",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=float(application.get("existing_debt", 0)),
                    step=25_000.0,
                )
                requested_amount = st.number_input(
                    "Requested loan amount (EUR)",
                    min_value=0.0,
                    max_value=100_000_000.0,
                    value=float(application.get("requested_amount", 0)),
                    step=25_000.0,
                )
                term_months = st.selectbox(
                    "Requested term",
                    TERM_OPTIONS,
                    index=_term_option_index(application.get("term_months", 60)),
                    format_func=lambda value: f"{value} months",
                )

            st.markdown("**Financial snapshot and plan**")
            finance_left, finance_middle, finance_right = st.columns(3)
            with finance_left:
                free_cash_flow = st.number_input(
                    "Free cash flow (EUR)",
                    min_value=-100_000_000.0,
                    max_value=1_000_000_000.0,
                    value=float(application.get("free_cash_flow", 0)),
                    step=25_000.0,
                )
                monthly_burn_rate = st.number_input(
                    "Monthly burn rate (EUR)",
                    min_value=0.0,
                    max_value=100_000_000.0,
                    value=float(application.get("monthly_burn_rate", 0)),
                    step=5_000.0,
                )
            with finance_middle:
                current_ratio = st.number_input(
                    "Current ratio",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(application.get("current_ratio", 1)),
                    step=0.05,
                )
                quick_ratio = st.number_input(
                    "Quick ratio",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(application.get("quick_ratio", 1)),
                    step=0.05,
                )
            with finance_right:
                expected_runway_months = st.number_input(
                    "Expected runway (months)",
                    min_value=0.0,
                    max_value=120.0,
                    value=float(application.get("expected_runway_months", 0)),
                    step=1.0,
                )
                forecast_revenue_pct = st.number_input(
                    "Forecast annual revenue growth (%)",
                    min_value=-50.0,
                    max_value=100.0,
                    value=float(application.get("forecast_revenue_cagr", 0)) * 100,
                    step=1.0,
                )

            loan_purpose_context = st.text_area(
                "What will the financing be used for?",
                value=str(application.get("loan_purpose_context", "")),
            )
            current_business_context = st.text_area(
                "Current business context",
                value=str(application.get("current_business_context", "")),
            )
            future_business_context = st.text_area(
                "Future plan and assumptions",
                value=str(application.get("future_business_context", "")),
            )
            saved_company_data = st.form_submit_button(
                "Save Company Data", width="stretch"
            )

        if saved_company_data:
            application.update(
                {
                    "company_name": company_name.strip() or "SME Applicant",
                    "industry": industry,
                    "region": region,
                    "company_type": company_type,
                    "years_in_business": years_in_business,
                    "employees": employees,
                    "annual_revenue": annual_revenue,
                    "existing_debt": existing_debt,
                    "requested_amount": requested_amount,
                    "term_months": term_months,
                    "free_cash_flow": free_cash_flow,
                    "monthly_burn_rate": monthly_burn_rate,
                    "cash_flow_to_revenue_ratio": free_cash_flow
                    / max(annual_revenue, 1),
                    "current_ratio": current_ratio,
                    "quick_ratio": quick_ratio,
                    "expected_runway_months": expected_runway_months,
                    "forecast_revenue_cagr": forecast_revenue_pct / 100,
                    "loan_purpose_context": loan_purpose_context,
                    "current_business_context": current_business_context,
                    "future_business_context": future_business_context,
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

    with connections_tab:
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

        st.subheader("Saved application files")
        st.caption(
            "These uploads are written to the local demo-session vault. They survive refresh and sign-out, "
            "are excluded from Git, and are removed only when Clear Demo State is used."
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
        upload_columns = st.columns(2)
        upload_widgets = {}
        category_items = list(DOCUMENT_CATEGORIES.items())
        for index, (category, label) in enumerate(category_items):
            with upload_columns[index % 2]:
                upload_widgets[category] = st.file_uploader(
                    label,
                    type=ALLOWED_DOCUMENT_TYPES,
                    accept_multiple_files=True,
                    key=f"sme_upload_{category}",
                )

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

    with health_tab:
        st.subheader("Application status and credit health")
        lifecycle = _lifecycle_for(application["application_id"])
        if lifecycle.get("status") == "Rating published":
            _render_published_rating(application, lifecycle)
            _render_post_publication_health_view(application, prediction, lifecycle)
        else:
            _render_application_readiness(application, prediction)

    with submit_tab:
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
else:
    st.title("SME Company Portal")
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

persist_demo_state()
