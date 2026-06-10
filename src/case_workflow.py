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
        "interest_rate": 0.055,
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
        "current_ratio": 2.40,
        "quick_ratio": 2.05,
        "receivables_days": 34,
        "payables_days": 31,
        "inventory_days": 8,
        "financial_statements_uploaded": 1,
        "bank_statements_uploaded": 1,
        "tax_return_uploaded": 1,
        "ownership_docs_uploaded": 1,
        "forecast_support_uploaded": 1,
        "document_edit_count": 1,
        "late_stage_change_count": 0,
        "process_deviation_score": 0.03,
        "email_domain_age_months": 96,
        "website_age_months": 108,
        "bank_account_age_months": 84,
        "location_mismatch_score": 0.02,
        "duplicate_contact_score": 0.01,
        "related_party_exposure_score": 0.04,
        "counterparty_concentration_score": 0.18,
        "shared_identifier_score": 0.01,
        "narrative_contradiction_score": 0.04,
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
        "interest_rate": 0.135,
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
        "current_ratio": 0.92,
        "quick_ratio": 0.64,
        "receivables_days": 82,
        "payables_days": 76,
        "inventory_days": 44,
        "financial_statements_uploaded": 1,
        "bank_statements_uploaded": 1,
        "tax_return_uploaded": 0,
        "ownership_docs_uploaded": 1,
        "forecast_support_uploaded": 0,
        "document_edit_count": 5,
        "late_stage_change_count": 2,
        "process_deviation_score": 0.32,
        "email_domain_age_months": 14,
        "website_age_months": 20,
        "bank_account_age_months": 8,
        "location_mismatch_score": 0.12,
        "duplicate_contact_score": 0.18,
        "related_party_exposure_score": 0.16,
        "counterparty_concentration_score": 0.42,
        "shared_identifier_score": 0.14,
        "narrative_contradiction_score": 0.42,
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
        "interest_rate": 0.165,
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
        "current_ratio": 0.72,
        "quick_ratio": 0.48,
        "receivables_days": 96,
        "payables_days": 88,
        "inventory_days": 78,
        "financial_statements_uploaded": 1,
        "bank_statements_uploaded": 0,
        "tax_return_uploaded": 0,
        "ownership_docs_uploaded": 1,
        "forecast_support_uploaded": 0,
        "document_edit_count": 8,
        "late_stage_change_count": 4,
        "process_deviation_score": 0.58,
        "email_domain_age_months": 5,
        "website_age_months": 9,
        "bank_account_age_months": 4,
        "location_mismatch_score": 0.35,
        "duplicate_contact_score": 0.28,
        "related_party_exposure_score": 0.34,
        "counterparty_concentration_score": 0.62,
        "shared_identifier_score": 0.22,
        "narrative_contradiction_score": 0.58,
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
        "interest_rate": 0.155,
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
        "current_ratio": 0.82,
        "quick_ratio": 0.55,
        "receivables_days": 85,
        "payables_days": 90,
        "inventory_days": 38,
        "financial_statements_uploaded": 1,
        "bank_statements_uploaded": 1,
        "tax_return_uploaded": 0,
        "ownership_docs_uploaded": 0,
        "forecast_support_uploaded": 0,
        "document_edit_count": 6,
        "late_stage_change_count": 3,
        "process_deviation_score": 0.47,
        "email_domain_age_months": 7,
        "website_age_months": 11,
        "bank_account_age_months": 6,
        "location_mismatch_score": 0.45,
        "duplicate_contact_score": 0.16,
        "related_party_exposure_score": 0.37,
        "counterparty_concentration_score": 0.52,
        "shared_identifier_score": 0.18,
        "narrative_contradiction_score": 0.45,
        "loan_purpose_context": "Applicant requests capital to support trade-lane expansion and bridge short-term liquidity needs.",
        "current_business_context": "The business has short runway, negative free cash flow, and concentrated exposure to higher-risk routes.",
        "future_business_context": "Management expects expansion to improve revenue, but execution depends on new carrier partners and faster collections.",
        "ceo_context": "CEO expects expansion from new trade lanes, with demand concentrated in higher-risk jurisdictions.",
        "cfo_context": "CFO says short-term liquidity depends on the requested loan and faster receivable collection.",
        "coo_context": "COO reports logistics capacity constraints and reliance on new carrier partners.",
    },
}


REVIEW_ACTIONS = ["Approve", "Reject", "Manual Review", "Request Documents", "Escalate to Compliance"]


def _yes_no(value):
    return "Yes" if float(value or 0) >= 0.5 else "No"


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
    derived = add_derived_features(pd.DataFrame([application])).iloc[0]
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
        f"Interest rate: {format_percent(application.get('interest_rate', 0))}",
        f"Annual interest expense: {format_currency(derived.get('annual_interest_expense', 0))}",
        f"Annual debt service: {format_currency(derived.get('annual_debt_service', 0))}",
        f"Debt service coverage ratio: {format_score(derived.get('debt_service_coverage_ratio', 0))}",
        f"Stressed DSCR (+2%): {format_score(derived.get('stressed_debt_service_coverage_ratio', 0))}",
        f"Free cash flow: {format_currency(application.get('free_cash_flow', 0))}",
        f"Monthly burn rate: {format_currency(application.get('monthly_burn_rate', 0))}",
        f"Cash flow / revenue: {format_percent(application.get('cash_flow_to_revenue_ratio', 0))}",
        f"Expected runway: {format_months(application.get('expected_runway_months', 0), 1)}",
        f"Forecast revenue CAGR: {format_percent(application.get('forecast_revenue_cagr', 0))}",
        f"Forecast employee CAGR: {format_percent(application.get('forecast_employee_cagr', 0))}",
        f"Year 5 FCF margin target: {format_percent(application.get('forecast_fcf_margin_year5', 0))}",
        f"Planned debt reduction: {format_percent(application.get('planned_debt_reduction_pct', 0))}",
        f"Plan confidence score: {format_score(application.get('forecast_plan_confidence_score', 0))}",
        f"Current ratio: {format_score(application.get('current_ratio', 0))}",
        f"Quick ratio: {format_score(application.get('quick_ratio', 0))}",
        f"Cash conversion cycle: {format_score(derived.get('cash_conversion_cycle_days', 0), 0)} days",
        f"Financial statements uploaded: {_yes_no(application.get('financial_statements_uploaded', 0))}",
        f"Bank statements uploaded: {_yes_no(application.get('bank_statements_uploaded', 0))}",
        f"Tax return uploaded: {_yes_no(application.get('tax_return_uploaded', 0))}",
        f"Ownership/KYB docs uploaded: {_yes_no(application.get('ownership_docs_uploaded', 0))}",
        f"Forecast support uploaded: {_yes_no(application.get('forecast_support_uploaded', 0))}",
        f"Document completeness score: {format_score(derived.get('document_completeness_score', 0))}",
        f"Document quality risk: {format_score(derived.get('document_quality_risk_score', 0))}",
        f"Identity verification risk: {format_score(derived.get('identity_verification_risk_score', 0))}",
        f"Working-capital pressure: {format_score(derived.get('working_capital_pressure_score', 0))}",
        f"Financial statement anomaly: {format_score(derived.get('financial_statement_anomaly_score', 0))}",
        f"Related-party network risk: {format_score(derived.get('related_party_network_risk_score', 0))}",
        f"Narrative consistency risk: {format_score(derived.get('narrative_consistency_risk_score', 0))}",
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
        "interest_rate",
        "debt_service_coverage_ratio",
        "free_cash_flow",
        "expected_runway_months",
        "document_completeness_score",
        "forecast_revenue_cagr",
        "fraud_probability",
        "grade",
        "decision",
        "is_fraud",
    ]
    return portfolio.sort_values("similarity_score").head(limit)[columns]
