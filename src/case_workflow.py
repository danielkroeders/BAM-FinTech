from datetime import datetime
from urllib.parse import quote

import numpy as np
import pandas as pd

from src.data_pipeline import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, add_derived_features
from src.formatting import format_currency, format_months, format_percent, format_score
from src.modeling import decision_from_grade, grade_from_probability


DEMO_SCENARIOS = {
    "Custom application": None,
    "Low-risk established borrower": {
        "industry": "Software",
        "region": "Western Europe",
        "company_type": "Corporation",
        "requested_amount": 180000,
        "term_months": 24,
        "annual_revenue": 6200000,
        "years_in_business": 11.0,
        "existing_debt": 420000,
        "num_recent_loans": 0,
        "employees": 58,
        "late_payment_ratio": 0.03,
        "suspicious_transfer_ratio": 0.01,
        "collateral_ratio": 1.15,
        "country_risk_score": 0.08,
        "free_cash_flow": 720000,
        "monthly_burn_rate": 18000,
        "expected_runway_months": 48,
        "forecast_revenue_cagr": 0.11,
        "forecast_employee_cagr": 0.07,
        "forecast_fcf_margin_year5": 0.15,
        "planned_debt_reduction_pct": 0.35,
        "forecast_plan_confidence_score": 0.82,
        "loan_purpose_context": "Applicant requests working capital to expand onboarding capacity for signed enterprise contracts.",
        "current_business_context": "The business is profitable, has positive free cash flow, and reports stable collections from recurring customers.",
        "future_business_context": "Management expects moderate growth from existing contracts while keeping hiring and debt reduction measured.",
        "ceo_context": "CEO notes stable enterprise demand and expects growth from two signed multi-year customer contracts.",
        "cfo_context": "CFO states the loan will replace a smaller credit line and preserve positive free cash flow.",
        "coo_context": "COO expects hiring to stay measured because delivery capacity is supported by automation.",
    },
    "Credit stacking case": {
        "industry": "Construction",
        "region": "North America",
        "company_type": "LLC",
        "requested_amount": 850000,
        "term_months": 36,
        "annual_revenue": 2100000,
        "years_in_business": 3.0,
        "existing_debt": 1750000,
        "num_recent_loans": 6,
        "employees": 23,
        "late_payment_ratio": 0.18,
        "suspicious_transfer_ratio": 0.07,
        "collateral_ratio": 0.48,
        "country_risk_score": 0.22,
        "free_cash_flow": -220000,
        "monthly_burn_rate": 74000,
        "expected_runway_months": 7,
        "forecast_revenue_cagr": 0.24,
        "forecast_employee_cagr": 0.06,
        "forecast_fcf_margin_year5": 0.08,
        "planned_debt_reduction_pct": 0.42,
        "forecast_plan_confidence_score": 0.38,
        "loan_purpose_context": "Applicant requests capital to consolidate recent borrowing and fund materials for upcoming construction projects.",
        "current_business_context": "The company has several active bids but current cash flow is negative and supplier payment timing is tight.",
        "future_business_context": "Management expects new awards to improve utilization, though the plan depends on project wins not yet finalized.",
        "ceo_context": "CEO expects new regional contracts to offset recent cash pressure, but awards are not yet finalized.",
        "cfo_context": "CFO says the facility is needed to consolidate recent borrowing and normalize supplier payments.",
        "coo_context": "COO reports that staffing will remain flat while project volume increases, creating execution pressure.",
    },
    "Suspicious transfers": {
        "industry": "Wholesale",
        "region": "Latin America",
        "company_type": "Partnership",
        "requested_amount": 540000,
        "term_months": 48,
        "annual_revenue": 1600000,
        "years_in_business": 2.0,
        "existing_debt": 980000,
        "num_recent_loans": 3,
        "employees": 17,
        "late_payment_ratio": 0.22,
        "suspicious_transfer_ratio": 0.24,
        "collateral_ratio": 0.36,
        "country_risk_score": 0.50,
        "free_cash_flow": -310000,
        "monthly_burn_rate": 92000,
        "expected_runway_months": 5,
        "forecast_revenue_cagr": 0.28,
        "forecast_employee_cagr": 0.08,
        "forecast_fcf_margin_year5": 0.10,
        "planned_debt_reduction_pct": 0.30,
        "forecast_plan_confidence_score": 0.31,
        "loan_purpose_context": "Applicant requests funding to stabilize inventory purchases and support a new distributor relationship.",
        "current_business_context": "The business reports elevated burn, weak cash conversion, and unusual transfer activity during supplier changes.",
        "future_business_context": "Management expects cash conversion to improve after collection cleanup, but documentation remains incomplete.",
        "ceo_context": "CEO cites a major distributor relationship as the basis for growth, but documentation is incomplete.",
        "cfo_context": "CFO says cash conversion should improve after collection cleanup, while current burn remains elevated.",
        "coo_context": "COO notes rapid supplier changes and cross-border fulfillment complexity in the next two years.",
    },
    "High country-risk borrower": {
        "industry": "Logistics",
        "region": "Middle East",
        "company_type": "Sole Proprietorship",
        "requested_amount": 460000,
        "term_months": 60,
        "annual_revenue": 1250000,
        "years_in_business": 1.0,
        "existing_debt": 760000,
        "num_recent_loans": 4,
        "employees": 9,
        "late_payment_ratio": 0.16,
        "suspicious_transfer_ratio": 0.10,
        "collateral_ratio": 0.40,
        "country_risk_score": 0.68,
        "free_cash_flow": -180000,
        "monthly_burn_rate": 58000,
        "expected_runway_months": 6,
        "forecast_revenue_cagr": 0.21,
        "forecast_employee_cagr": 0.05,
        "forecast_fcf_margin_year5": 0.07,
        "planned_debt_reduction_pct": 0.25,
        "forecast_plan_confidence_score": 0.36,
        "loan_purpose_context": "Applicant requests capital to support trade-lane expansion and bridge short-term liquidity needs.",
        "current_business_context": "The business has short runway, negative free cash flow, and concentrated exposure to higher-risk routes.",
        "future_business_context": "Management expects expansion to improve revenue, but execution depends on new carrier partners and faster collections.",
        "ceo_context": "CEO expects expansion from new trade lanes, with demand concentrated in higher-risk jurisdictions.",
        "cfo_context": "CFO says short-term liquidity depends on the requested loan and faster receivable collection.",
        "coo_context": "COO reports logistics capacity constraints and reliance on new carrier partners.",
    },
}


REVIEW_ACTIONS = ["Approve", "Reject", "Manual Review", "Request Documents", "Escalate to Compliance"]


def adjusted_prediction(base_prediction, manual_probability):
    probability = float(manual_probability)
    grade = grade_from_probability(probability)
    return {
        **base_prediction,
        "fraud_probability": probability,
        "grade": grade,
        "decision": decision_from_grade(grade),
        "manual_adjustment": True,
    }


def case_summary(application, prediction, explanation, review=None):
    flags = prediction.get("flags") or []
    flag_lines = [f"- {flag}" for flag in flags] if flags else ["- No deterministic risk flags were triggered."]
    lines = [
        "B2B Loan Fraud Intelligence Case Summary",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Application ID: {application.get('application_id', 'Session application')}",
        f"Company: {application.get('company_name', 'Session Applicant')}",
        f"Industry: {application.get('industry', '')}",
        f"Region: {application.get('region', '')}",
        f"Requested amount: {format_currency(application.get('requested_amount', 0))}",
        f"Free cash flow: {format_currency(application.get('free_cash_flow', 0))}",
        f"Monthly burn rate: {format_currency(application.get('monthly_burn_rate', 0))}",
        f"Cash flow / revenue: {format_percent(application.get('cash_flow_to_revenue_ratio', 0))}",
        f"Expected runway: {format_months(application.get('expected_runway_months', 0), 1)}",
        f"Forecast revenue CAGR: {format_percent(application.get('forecast_revenue_cagr', 0))}",
        f"Forecast employee CAGR: {format_percent(application.get('forecast_employee_cagr', 0))}",
        f"Year 5 FCF margin target: {format_percent(application.get('forecast_fcf_margin_year5', 0))}",
        f"Planned debt reduction: {format_percent(application.get('planned_debt_reduction_pct', 0))}",
        f"Plan confidence score: {format_score(application.get('forecast_plan_confidence_score', 0))}",
        "",
        f"Fraud probability: {format_percent(prediction['fraud_probability'])}",
        f"Risk grade: {prediction['grade']}",
        f"Recommended action: {prediction['decision']}",
        f"Manual adjustment: {'Yes' if prediction.get('manual_adjustment') else 'No'}",
        "",
        "Risk factors:",
        *flag_lines,
        "",
        "Explanation:",
        explanation,
    ]
    applicant_context_lines = [
        ("Loan purpose", application.get("loan_purpose_context", "")),
        ("Current business context", application.get("current_business_context", "")),
        ("Future business context", application.get("future_business_context", "")),
    ]
    if any(text for _, text in applicant_context_lines):
        lines.extend(["", "Applicant narrative:"])
        lines.extend(f"{label}: {text}" for label, text in applicant_context_lines if text)
    context_lines = [
        ("CEO context", application.get("ceo_context", "")),
        ("CFO context", application.get("cfo_context", "")),
        ("COO context", application.get("coo_context", "")),
    ]
    if any(text for _, text in context_lines):
        lines.extend(["", "Executive context:"])
        lines.extend(f"{label}: {text}" for label, text in context_lines if text)
    if review:
        lines.extend(
            [
                "",
                "Analyst review:",
                f"Final decision: {review.get('final_decision', review.get('action', ''))}",
                f"Model recommendation: {review.get('model_recommendation', '')}",
                f"Supervisor email: {review.get('supervisor_email', '')}",
                f"Analyst note: {review.get('analyst_note', '')}",
            ]
        )
    return "\n".join(lines)


def mailto_link(recipient, subject, body):
    return f"mailto:{recipient}?subject={quote(subject)}&body={quote(body)}"


def similar_applications(model_bundle, applications, application, limit=5):
    portfolio = add_derived_features(applications)
    application_features = add_derived_features(pd.DataFrame([application])).iloc[0]
    probabilities = model_bundle.pipeline.predict_proba(portfolio[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS])[:, 1]
    portfolio["fraud_probability"] = probabilities
    portfolio["grade"] = [grade_from_probability(probability) for probability in probabilities]
    portfolio["decision"] = [decision_from_grade(grade) for grade in portfolio["grade"]]

    numeric = portfolio[NUMERIC_COLUMNS].astype(float)
    center = pd.Series({column: float(application_features.get(column, numeric[column].median())) for column in NUMERIC_COLUMNS})
    scale = numeric.std().replace(0, 1)
    numeric_distance = (((numeric - center) / scale) ** 2).sum(axis=1) ** 0.5

    category_distance = np.zeros(len(portfolio))
    for column in CATEGORICAL_COLUMNS:
        category_distance += (portfolio[column] != application.get(column)).astype(float)

    portfolio["similarity_score"] = numeric_distance + category_distance
    columns = [
        "application_id",
        "company_name",
        "industry",
        "region",
        "requested_amount",
        "free_cash_flow",
        "expected_runway_months",
        "forecast_revenue_cagr",
        "fraud_probability",
        "grade",
        "decision",
        "is_fraud",
    ]
    return portfolio.sort_values("similarity_score").head(limit)[columns]
