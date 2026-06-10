import pandas as pd
import streamlit as st

from src.formatting import format_score
from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="Model Insights", layout="wide")
bootstrap_state()
render_sidebar()

bundle = st.session_state.model_bundle
metrics = bundle.metrics

st.title("Model Insights")
st.caption("Supervised fraud model performance, grading policy, and research-backed signal design.")

metric_keys = ["accuracy", "balanced_accuracy", "precision", "recall", "f1", "roc_auc", "average_precision", "mcc"]
cols = st.columns(4)
for index, key in enumerate(metric_keys):
    col = cols[index % 4]
    col.metric(key.replace("_", " ").title(), format_score(metrics[key], 3))
st.metric("Precision At Top 10% Review Queue", format_score(metrics["precision_at_10pct"], 3))

left, right = st.columns(2)
with left:
    st.subheader("Confusion Matrix")
    matrix = pd.DataFrame(
        [[metrics["tn"], metrics["fp"]], [metrics["fn"], metrics["tp"]]],
        index=["Actual legitimate", "Actual fraud"],
        columns=["Predicted legitimate", "Predicted fraud"],
    )
    st.dataframe(matrix, use_container_width=True)
with right:
    st.subheader("A-F Grading Thresholds")
    thresholds = pd.DataFrame(
        [
            {"Grade": "A", "Fraud probability": "< 0.15", "Decision": "Approve"},
            {"Grade": "B", "Fraud probability": "0.15 to < 0.28", "Decision": "Approve"},
            {"Grade": "C", "Fraud probability": "0.28 to < 0.42", "Decision": "Manual Review"},
            {"Grade": "D", "Fraud probability": "0.42 to < 0.58", "Decision": "Manual Review"},
            {"Grade": "E", "Fraud probability": "0.58 to < 0.74", "Decision": "Reject"},
            {"Grade": "F", "Fraud probability": ">= 0.74", "Decision": "Reject"},
        ]
    )
    st.dataframe(thresholds, use_container_width=True, hide_index=True)

st.subheader("Top Feature Importances")
importance_display = bundle.feature_importance.head(20).copy()
importance_display["importance"] = importance_display["importance"].apply(lambda value: format_score(value, 4))
st.dataframe(importance_display, use_container_width=True, hide_index=True)
st.bar_chart(bundle.feature_importance.head(12).set_index("feature")["importance"])

st.subheader("Research-Backed Derived Signals")
derived_signals = pd.DataFrame(
    [
        {"Signal": "debt_to_revenue_ratio", "Purpose": "Measures financial pressure from existing obligations."},
        {"Signal": "request_to_revenue_ratio", "Purpose": "Compares requested exposure with business scale."},
        {"Signal": "loan_velocity_score", "Purpose": "Captures rapid recent borrowing behavior and possible credit stacking."},
        {"Signal": "payment_stress_score", "Purpose": "Combines late-payment behavior with debt pressure."},
        {"Signal": "collateral_gap_ratio", "Purpose": "Estimates uncovered exposure when collateral is weak."},
        {"Signal": "external_financing_pressure", "Purpose": "Approximates fraud-triangle pressure from request size, debt, and loan velocity."},
        {"Signal": "financial_distress_score", "Purpose": "Combines debt, payment, collateral, and short-history stress."},
        {"Signal": "transaction_anomaly_score", "Purpose": "Summarizes suspicious transfers, payment stress, country risk, and borrowing velocity."},
        {"Signal": "company_scale_mismatch_score", "Purpose": "Flags employee scale that appears stretched relative to requested exposure."},
        {"Signal": "governance_complexity_score", "Purpose": "Approximates review complexity from entity type, region, history, and country risk."},
        {"Signal": "free_cash_flow", "Purpose": "Captures annual cash generation available after operating and investment needs."},
        {"Signal": "monthly_burn_rate", "Purpose": "Estimates monthly cash consumption at application date."},
        {"Signal": "cash_flow_to_revenue_ratio", "Purpose": "Shows whether reported revenue converts into free cash flow."},
        {"Signal": "expected_runway_months", "Purpose": "Estimates how long cash reserves can cover current burn."},
        {"Signal": "cash_flow_pressure_score", "Purpose": "Combines negative cash flow and burn intensity into a liquidity stress signal."},
        {"Signal": "runway_risk_score", "Purpose": "Flags applicants with short expected runway."},
        {"Signal": "cash_conversion_risk_score", "Purpose": "Highlights weak cash conversion relative to reported revenue."},
        {"Signal": "forecast_revenue_cagr", "Purpose": "Captures the applicant's expected annual revenue growth over five years."},
        {"Signal": "forecast_employee_cagr", "Purpose": "Captures expected employee growth supporting the revenue plan."},
        {"Signal": "forecast_fcf_margin_year5", "Purpose": "Represents the target year-five free-cash-flow margin."},
        {"Signal": "planned_debt_reduction_pct", "Purpose": "Represents the applicant's planned debt reduction over five years."},
        {"Signal": "forecast_plan_confidence_score", "Purpose": "Captures confidence in the applicant's five-year plan."},
        {"Signal": "forecast_plan_aggressiveness_score", "Purpose": "Flags ambitious growth and margin plans that may not be supported by current signals."},
        {"Signal": "forecast_execution_risk_score", "Purpose": "Combines plan ambition, liquidity risk, and confidence into a forecast execution signal."},
        {"Signal": "forecast_hiring_efficiency_risk_score", "Purpose": "Measures whether headcount growth supports projected revenue growth."},
        {"Signal": "forecast_debt_service_risk_score", "Purpose": "Measures whether debt reduction plans are strained by cash-flow pressure."},
    ]
)
st.dataframe(derived_signals, use_container_width=True, hide_index=True)
st.caption("These derived fields are computed automatically from seed and intake data; analysts do not need to enter them manually.")
