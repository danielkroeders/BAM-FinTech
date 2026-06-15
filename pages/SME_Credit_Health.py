import pandas as pd
import streamlit as st

from src.alignment_features import (
    apply_scenario,
    data_source_coverage_rows,
    peer_benchmark_rows,
    scenario_comparison_rows,
    sme_action_rows,
)
from src.data_pipeline import add_derived_features, build_forecast_table
from src.demo_persistence import persist_demo_state
from src.formatting import format_currency, format_integer, format_months, format_percent, format_score
from src.modeling import score_application, score_portfolio
from src.runtime import bootstrap_state
from src.ui import render_sidebar, safe_page_link


st.set_page_config(page_title="SME Credit Health", layout="wide")
bootstrap_state()
render_sidebar()

st.title("SME Credit Health Preview")
st.caption("Borrower-facing MVP preview for understanding risk drivers before and after a loan application review.")
st.info(
    "This page previews the SME self-service concept. It uses the same synthetic case data as the "
    "underwriter workbench and does not represent a final credit decision."
)

applications = st.session_state.seed_data["applications"]
portfolio = score_portfolio(st.session_state.model_bundle, applications)

case_options = []
if st.session_state.get("last_application") and st.session_state.get("last_prediction"):
    latest = st.session_state.last_application
    case_options.append(
        f"Latest scored case - {latest.get('application_id', 'Session')} - {latest.get('company_name', 'Applicant')}"
    )
case_options.extend(
    f"{row.application_id} - {row.company_name} | Grade {row.grade}"
    for row in portfolio.sort_values("fraud_probability", ascending=False).head(30).itertuples()
)

selected_case = st.selectbox("Credit health file", case_options)
if selected_case.startswith("Latest scored case"):
    application = dict(st.session_state.last_application)
    prediction = dict(st.session_state.last_prediction)
else:
    selected_id = selected_case.split(" - ", 1)[0]
    application = portfolio[portfolio["application_id"] == selected_id].iloc[0].to_dict()
    prediction = score_application(st.session_state.model_bundle, application)

signals = add_derived_features(pd.DataFrame([application])).iloc[0]

summary_cols = st.columns(4)
summary_cols[0].metric("Current grade", prediction["grade"])
summary_cols[1].metric("Risk score", format_percent(prediction["fraud_probability"]))
summary_cols[2].metric("Lender view", prediction["decision"])
summary_cols[3].metric("Runway", format_months(application.get("expected_runway_months", 0)))

overview_left, overview_right = st.columns([1, 1])
with overview_left:
    st.subheader("Company Snapshot")
    st.dataframe(
        pd.DataFrame(
            [
                {"Field": "Company", "Value": application.get("company_name", "Applicant")},
                {"Field": "Industry", "Value": application.get("industry", "")},
                {"Field": "Region", "Value": application.get("region", "")},
                {"Field": "Requested amount", "Value": format_currency(application.get("requested_amount", 0))},
                {"Field": "Annual revenue", "Value": format_currency(application.get("annual_revenue", 0))},
                {"Field": "Free cash flow", "Value": format_currency(application.get("free_cash_flow", 0))},
                {"Field": "Stressed DSCR", "Value": format_score(signals.get("stressed_debt_service_coverage_ratio", 0))},
            ]
        ),
        width="stretch",
        hide_index=True,
    )
with overview_right:
    st.subheader("Most Useful Next Actions")
    st.dataframe(pd.DataFrame(sme_action_rows(application, signals, prediction)), width="stretch", hide_index=True)

st.subheader("What-If Simulation")
st.caption("Adjust the applicant plan to see how stronger evidence or operating assumptions could change the model view.")
scenario_left, scenario_middle, scenario_right = st.columns(3)
with scenario_left:
    revenue_growth_delta = st.slider("Revenue growth change", -0.15, 0.20, 0.00, 0.01, format="%.2f")
    fcf_margin_delta = st.slider("FCF margin change", -0.10, 0.15, 0.00, 0.01, format="%.2f")
with scenario_middle:
    operating_cost_pressure = st.slider("Operating cost pressure", 0.00, 0.15, 0.00, 0.01, format="%.2f")
    debt_reduction_delta = st.slider("Debt reduction plan change", -0.20, 0.35, 0.00, 0.05, format="%.2f")
with scenario_right:
    contract_evidence = st.selectbox("Contract evidence", ["Current file", "Signed and documented", "Unconfirmed"])
    complete_documents = st.checkbox("Complete missing documents", value=False)

scenario_application = apply_scenario(
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
    scenario_application,
)
st.dataframe(pd.DataFrame(scenario_rows), width="stretch", hide_index=True)
st.caption(
    f"What-if result: grade {scenario_prediction['grade']} with a "
    f"{format_percent(scenario_prediction['fraud_probability'])} risk score."
)

benchmark_tab, sources_tab, forecast_tab = st.tabs(["Peer Benchmark", "Evidence Sources", "Five-Year View"])
with benchmark_tab:
    st.caption("Synthetic peer view for the sector and region where enough comparable cases exist.")
    st.dataframe(
        pd.DataFrame(peer_benchmark_rows(st.session_state.model_bundle, applications, application, prediction)),
        width="stretch",
        hide_index=True,
    )
with sources_tab:
    st.caption("MVP source coverage. Production would connect live bank, accounting, registry, and document systems.")
    st.dataframe(pd.DataFrame(data_source_coverage_rows(application, signals)), width="stretch", hide_index=True)
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
    )[["Year", "Projected revenue", "Projected employees", "Projected FCF", "Projected debt"]].copy()
    for column in ["Projected revenue", "Projected FCF", "Projected debt"]:
        display[column] = display[column].apply(format_currency)
    display["Projected employees"] = display["Projected employees"].apply(format_integer)
    st.dataframe(display, width="stretch", hide_index=True)

nav_cols = st.columns([1, 1, 3])
with nav_cols[0]:
    safe_page_link("pages/Personal_Workspace.py", "Open Underwriter View", ":material/person_search:")
with nav_cols[1]:
    safe_page_link("pages/Risk_Dashboard.py", "Open Portfolio View", ":material/monitoring:")

persist_demo_state()
