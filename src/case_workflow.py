from datetime import datetime
from urllib.parse import quote

import numpy as np
import pandas as pd

from src.data_pipeline import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS
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
        f"Requested amount: ${float(application.get('requested_amount', 0)):,.0f}",
        "",
        f"Fraud probability: {prediction['fraud_probability']:.1%}",
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
    portfolio = applications.copy()
    probabilities = model_bundle.pipeline.predict_proba(portfolio[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS])[:, 1]
    portfolio["fraud_probability"] = probabilities
    portfolio["grade"] = [grade_from_probability(probability) for probability in probabilities]
    portfolio["decision"] = [decision_from_grade(grade) for grade in portfolio["grade"]]

    numeric = portfolio[NUMERIC_COLUMNS].astype(float)
    center = pd.Series({column: float(application.get(column, numeric[column].median())) for column in NUMERIC_COLUMNS})
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
        "fraud_probability",
        "grade",
        "decision",
        "is_fraud",
    ]
    return portfolio.sort_values("similarity_score").head(limit)[columns]
