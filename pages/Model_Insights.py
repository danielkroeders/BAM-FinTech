import pandas as pd
import streamlit as st

from src.data_pipeline import NUMERIC_COLUMNS, add_derived_features
from src.formatting import format_currency, format_score
from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="Model Insights", layout="wide")
bootstrap_state()
render_sidebar()

bundle = st.session_state.model_bundle
metrics = bundle.metrics
applications = add_derived_features(st.session_state.seed_data["applications"])

st.title("Model Insights")
st.caption("Supervised SME application-risk model performance, grading policy, and research-backed signal design.")

metric_catalog = {
    "Accuracy": "accuracy",
    "Balanced Accuracy": "balanced_accuracy",
    "Precision": "precision",
    "Recall": "recall",
    "F1": "f1",
    "ROC-AUC": "roc_auc",
    "Average Precision": "average_precision",
    "MCC": "mcc",
    "Precision At Top 5%": "precision_at_5pct",
    "Precision At Top 10%": "precision_at_10pct",
    "Precision At Top 20%": "precision_at_20pct",
    "False Positive Rate": "false_positive_rate",
    "False Negative Rate": "false_negative_rate",
    "Predicted Review Rate": "predicted_review_rate",
    "Estimated Review Cost": "estimated_review_cost",
    "Estimated False Positive Cost": "estimated_false_positive_cost",
    "Estimated False Negative Cost": "estimated_false_negative_cost",
    "Estimated Total Error Cost": "estimated_total_error_cost",
}
default_metric_labels = [
    "Balanced Accuracy",
    "Precision",
    "Recall",
    "ROC-AUC",
    "Average Precision",
    "MCC",
    "Precision At Top 10%",
    "Estimated Total Error Cost",
]
selected_metric_labels = st.multiselect(
    "Visible metrics",
    list(metric_catalog.keys()),
    default=default_metric_labels,
)
cols = st.columns(4)
for index, label in enumerate(selected_metric_labels):
    key = metric_catalog[label]
    col = cols[index % 4]
    value = format_currency(metrics[key]) if key.startswith("estimated_") else format_score(metrics[key], 3)
    col.metric(label, value)

queue_rows = pd.DataFrame(
    [
        {"Review queue": "Top 5%", "Precision": format_score(metrics["precision_at_5pct"], 3)},
        {"Review queue": "Top 10%", "Precision": format_score(metrics["precision_at_10pct"], 3)},
        {"Review queue": "Top 20%", "Precision": format_score(metrics["precision_at_20pct"], 3)},
    ]
)
st.dataframe(queue_rows, width="stretch", hide_index=True)

st.subheader("Custom Portfolio Metric")
metric_left, metric_middle, metric_right, metric_extra = st.columns(4)
numeric_options = [column for column in NUMERIC_COLUMNS if column in applications.columns]
with metric_left:
    custom_metric_name = st.text_input("Metric name", value="Custom portfolio metric")
with metric_middle:
    numerator_column = st.selectbox(
        "Numerator",
        numeric_options,
        index=numeric_options.index("requested_amount") if "requested_amount" in numeric_options else 0,
    )
with metric_right:
    denominator_options = ["None"] + numeric_options
    denominator_column = st.selectbox(
        "Denominator",
        denominator_options,
        index=denominator_options.index("annual_revenue") if "annual_revenue" in denominator_options else 0,
    )
with metric_extra:
    aggregation = st.selectbox("Aggregation", ["Average", "Median", "Sum", "P90"])

metric_series = pd.to_numeric(applications[numerator_column], errors="coerce")
if denominator_column != "None":
    denominator = pd.to_numeric(applications[denominator_column], errors="coerce").replace(0, pd.NA)
    metric_series = metric_series / denominator
metric_series = metric_series.dropna()
if aggregation == "Median":
    custom_value = metric_series.median()
elif aggregation == "Sum":
    custom_value = metric_series.sum()
elif aggregation == "P90":
    custom_value = metric_series.quantile(0.90)
else:
    custom_value = metric_series.mean()
money_like = denominator_column == "None" and any(token in numerator_column for token in ["amount", "revenue", "debt", "cash", "burn"])
st.metric(custom_metric_name or "Custom metric", format_currency(custom_value) if money_like else format_score(custom_value, 3))

left, right = st.columns(2)
with left:
    st.subheader("Confusion Matrix")
    matrix = pd.DataFrame(
        [[metrics["tn"], metrics["fp"]], [metrics["fn"], metrics["tp"]]],
        index=["Actual lower risk", "Actual high risk"],
        columns=["Predicted lower risk", "Predicted high risk"],
    )
    st.dataframe(matrix, width="stretch")
with right:
    st.subheader("A-F Grading Thresholds")
    thresholds = pd.DataFrame(
        [
            {"Grade": "A", "Application risk score": "< 0.15", "Decision": "Approve"},
            {"Grade": "B", "Application risk score": "0.15 to < 0.28", "Decision": "Approve"},
            {"Grade": "C", "Application risk score": "0.28 to < 0.42", "Decision": "Manual Review"},
            {"Grade": "D", "Application risk score": "0.42 to < 0.58", "Decision": "Manual Review"},
            {"Grade": "E", "Application risk score": "0.58 to < 0.74", "Decision": "Reject"},
            {"Grade": "F", "Application risk score": ">= 0.74", "Decision": "Reject"},
        ]
    )
    st.dataframe(thresholds, width="stretch", hide_index=True)

st.subheader("Governance Notes")
governance_rows = pd.DataFrame(
    [
        {
            "Area": "Data lineage",
            "Control": "Application records are prepared locally and enriched with derived ratios, verification metadata, and review outcomes.",
        },
        {
            "Area": "Human review",
            "Control": "C-D cases route to manual review; E-F cases require compliance-style review before final action.",
        },
        {
            "Area": "Audit trail",
            "Control": "Case review captures final decision, analyst action, notes, supervisor mailbox, and manual score adjustment status.",
        },
        {
            "Area": "Threshold policy",
            "Control": "A-F grades are fixed policy thresholds over the application risk score and are displayed next to model metrics.",
        },
        {
            "Area": "Model limitations",
            "Control": "The app is decision support; outputs are not legal, credit, or compliance determinations.",
        },
    ]
)
st.dataframe(governance_rows, width="stretch", hide_index=True)

st.subheader("Top Feature Importances")
importance_display = bundle.feature_importance.head(20).copy()
importance_display["importance"] = importance_display["importance"].apply(lambda value: format_score(value, 4))
st.dataframe(importance_display, width="stretch", hide_index=True)
st.bar_chart(bundle.feature_importance.head(12).set_index("feature")["importance"])

st.subheader("Research-Backed Derived Signals")
derived_signals = pd.DataFrame(
    [
        {"Signal": "debt_to_revenue_ratio", "Purpose": "Measures financial pressure from existing obligations."},
        {"Signal": "request_to_revenue_ratio", "Purpose": "Compares requested exposure with business scale."},
        {"Signal": "loan_velocity_score", "Purpose": "Captures rapid recent borrowing behavior and possible credit stacking."},
        {"Signal": "payment_stress_score", "Purpose": "Combines late-payment behavior with debt pressure."},
        {"Signal": "collateral_gap_ratio", "Purpose": "Estimates uncovered exposure when collateral is weak."},
        {"Signal": "external_financing_pressure", "Purpose": "Approximates financing pressure from request size, debt, and loan velocity."},
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
        {"Signal": "interest_rate", "Purpose": "Captures the offered annual loan rate used in repayment and stress calculations."},
        {"Signal": "annual_interest_expense", "Purpose": "Estimates first-year interest burden on the requested facility."},
        {"Signal": "annual_debt_service", "Purpose": "Estimates first-year principal and interest payments from rate, amount, and term."},
        {"Signal": "debt_service_coverage_ratio", "Purpose": "Compares free cash flow with estimated annual debt service."},
        {"Signal": "stressed_debt_service_coverage_ratio", "Purpose": "Recomputes DSCR under a +2 percentage point interest-rate stress."},
        {"Signal": "debt_service_stress_score", "Purpose": "Flags repayment sensitivity when DSCR or stressed DSCR is weak."},
        {"Signal": "cash_conversion_cycle_days", "Purpose": "Combines receivables, inventory, and payables timing into a working-capital pressure view."},
        {"Signal": "document_completeness_score", "Purpose": "Measures whether the expected application package is present without requiring actual file upload."},
        {"Signal": "document_quality_risk_score", "Purpose": "Flags missing documents, repeated edits, and late-stage changes."},
        {"Signal": "process_integrity_risk_score", "Purpose": "Captures workflow deviations and unusual resubmission behavior."},
        {"Signal": "identity_verification_risk_score", "Purpose": "Summarizes digital footprint age, bank-account age, and mismatch signals."},
        {"Signal": "working_capital_pressure_score", "Purpose": "Combines current ratio, quick ratio, cash conversion cycle, and receivables pressure."},
        {"Signal": "financial_statement_anomaly_score", "Purpose": "Captures revenue/cash-flow mismatch, receivables pressure, and unsupported margin improvement."},
        {"Signal": "related_party_network_risk_score", "Purpose": "Summarizes related-party exposure, concentrated counterparties, and shared identifiers."},
        {"Signal": "narrative_consistency_risk_score", "Purpose": "Flags contradictions between applicant context, document status, and financial signals."},
    ]
)
st.dataframe(derived_signals, width="stretch", hide_index=True)
st.caption("These derived fields are computed automatically from portfolio and workspace intake data; analysts do not need to enter them manually.")
