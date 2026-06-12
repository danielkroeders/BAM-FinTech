from datetime import datetime

import pandas as pd

from src.data_pipeline import add_derived_features
from src.formatting import format_currency, format_months, format_percent, format_score
from src.modeling import score_portfolio


DOCUMENT_FIELDS = [
    ("financial_statements_uploaded", "Financial statements"),
    ("bank_statements_uploaded", "Bank statements"),
    ("tax_return_uploaded", "Tax return"),
    ("ownership_docs_uploaded", "Ownership/KYB"),
    ("forecast_support_uploaded", "Forecast support"),
]


def _number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def missing_documents(application):
    return [label for key, label in DOCUMENT_FIELDS if _number(application.get(key)) < 0.5]


def queue_status(row):
    grade = row.get("grade", "")
    if grade in {"E", "F"}:
        return "Compliance review"
    if _number(row.get("document_completeness_score")) < 0.8:
        return "Request documents"
    if grade in {"C", "D"}:
        return "Manual review"
    return "Ready for approval"


def build_application_queue(model_bundle, applications, limit=None):
    queue = score_portfolio(model_bundle, applications).copy()
    queue["queue_status"] = queue.apply(queue_status, axis=1)
    queue["missing_documents"] = queue.apply(lambda row: len(missing_documents(row)), axis=1)
    analysts = ["Ms. Cooper", "M. van Dijk", "S. Jansen"]
    queue["assigned_analyst"] = [analysts[index % len(analysts)] for index in range(len(queue))]
    queue["sla"] = queue["grade"].map({"A": "3 d", "B": "3 d", "C": "2 d", "D": "1 d", "E": "Same day", "F": "Same day"})
    queue["priority"] = queue["grade"].map({"F": 0, "E": 1, "D": 2, "C": 3, "B": 4, "A": 5})
    queue = queue.sort_values(["priority", "fraud_probability"], ascending=[True, False])
    if limit:
        queue = queue.head(limit)
    return queue


def recommended_loan_terms(application, prediction, signals):
    grade = prediction.get("grade", "C")
    requested_amount = _number(application.get("requested_amount"))
    current_rate = _number(application.get("interest_rate"))
    current_term = int(_number(application.get("term_months"), 36))
    dscr = _number(signals.get("debt_service_coverage_ratio"))
    stressed_dscr = _number(signals.get("stressed_debt_service_coverage_ratio"))

    amount_factor = {"A": 1.0, "B": 0.95, "C": 0.8, "D": 0.6, "E": 0.0, "F": 0.0}.get(grade, 0.75)
    if dscr < 1.0:
        amount_factor = min(amount_factor, max(0.25, dscr / 1.4))
    proposed_amount = round(requested_amount * amount_factor / 1000) * 1000

    rate_uplift = {"A": 0.0, "B": 0.005, "C": 0.015, "D": 0.03, "E": 0.05, "F": 0.07}.get(grade, 0.02)
    proposed_rate = min(max(current_rate + rate_uplift, current_rate), 0.24)
    proposed_term = current_term if grade in {"A", "B", "C"} else min(current_term, 36)
    collateral_target = {"A": 0.6, "B": 0.75, "C": 0.95, "D": 1.15, "E": 1.35, "F": 1.5}.get(grade, 1.0)

    if grade in {"E", "F"}:
        stance = "Do not proceed without refreshed evidence and supervisor sign-off."
    elif stressed_dscr < 1.0:
        stance = "Proceed only after DSCR stress review and revised repayment structure."
    elif grade in {"C", "D"}:
        stance = "Proceed as conditional approval subject to document and covenant review."
    else:
        stance = "Proceed under standard approval conditions."

    return [
        {"Term": "Recommended amount", "Recommendation": format_currency(proposed_amount), "Rationale": "Adjusted for grade, DSCR, and current cash-flow capacity."},
        {"Term": "Suggested interest rate", "Recommendation": format_percent(proposed_rate), "Rationale": "Risk-adjusted pricing based on the current model grade."},
        {"Term": "Tenor", "Recommendation": format_months(proposed_term), "Rationale": "Shorter tenor for higher monitoring or repayment risk."},
        {"Term": "Collateral target", "Recommendation": format_percent(collateral_target), "Rationale": "Coverage target aligned to grade and loss protection."},
        {"Term": "Covenants", "Recommendation": "Monthly bank feed, DSCR floor, no new senior debt", "Rationale": "Protects post-origination monitoring and credit position."},
        {"Term": "Credit stance", "Recommendation": stance, "Rationale": "Summarizes the underwriting path for the banker."},
    ]


def portfolio_monitoring_preview(application, prediction, signals):
    probability = _number(prediction.get("fraud_probability"))
    cash_pressure = _number(signals.get("cash_flow_pressure_score"))
    debt_stress = _number(signals.get("debt_service_stress_score"))
    document_risk = _number(signals.get("document_quality_risk_score"))
    trend_delta = (cash_pressure * 0.04) + (debt_stress * 0.04) + (document_risk * 0.02) - 0.02
    projected_probability = min(max(probability + trend_delta, 0), 1)

    if projected_probability >= 0.58:
        watchlist = "Intensive monitoring"
        cadence = "Weekly until evidence improves"
    elif projected_probability >= 0.28:
        watchlist = "Watchlist"
        cadence = "Monthly"
    else:
        watchlist = "Standard monitoring"
        cadence = "Quarterly"

    return [
        {"Monitor": "Watchlist status", "Output": watchlist, "Trigger": "Based on projected risk, DSCR stress, and document quality."},
        {"Monitor": "90-day projected risk", "Output": format_percent(projected_probability), "Trigger": f"Current score {format_percent(probability)} plus trend signals."},
        {"Monitor": "Cash-flow trigger", "Output": format_score(cash_pressure), "Trigger": "Rising burn, negative FCF, or weak runway."},
        {"Monitor": "Debt-service trigger", "Output": format_score(debt_stress), "Trigger": "DSCR and +2% interest-rate stress coverage."},
        {"Monitor": "Review cadence", "Output": cadence, "Trigger": "Post-origination monitoring schedule."},
        {"Monitor": "Data refresh", "Output": "Bank feed, accounting, documents", "Trigger": "Latest source refresh across connected evidence."},
    ]


def grouped_risk_drivers(application, signals):
    return [
        {"Driver group": "Cash flow", "Score": format_score(signals.get("cash_flow_pressure_score", 0)), "Status": "Stronger" if _number(signals.get("cash_flow_pressure_score")) < 0.35 else "Pressure", "Banker signal": f"FCF {format_currency(application.get('free_cash_flow', 0))}; runway {format_months(application.get('expected_runway_months', 0))}"},
        {"Driver group": "Debt service", "Score": format_score(signals.get("debt_service_stress_score", 0)), "Status": "Covered" if _number(signals.get("stressed_debt_service_coverage_ratio")) >= 1 else "Stressed", "Banker signal": f"DSCR {format_score(signals.get('debt_service_coverage_ratio', 0))}; stressed {format_score(signals.get('stressed_debt_service_coverage_ratio', 0))}"},
        {"Driver group": "Documents", "Score": format_score(signals.get("document_quality_risk_score", 0)), "Status": "Ready" if _number(signals.get("document_completeness_score")) >= 0.8 else "Incomplete", "Banker signal": f"Completeness {format_score(signals.get('document_completeness_score', 0))}"},
        {"Driver group": "Identity/KYB", "Score": format_score(signals.get("identity_verification_risk_score", 0)), "Status": "Clear" if _number(signals.get("identity_verification_risk_score")) < 0.35 else "Review", "Banker signal": f"Location mismatch {format_score(application.get('location_mismatch_score', 0))}"},
        {"Driver group": "Forecast", "Score": format_score(signals.get("forecast_execution_risk_score", 0)), "Status": "Supported" if _number(signals.get("forecast_execution_risk_score")) < 0.35 else "Aggressive", "Banker signal": f"Revenue CAGR {format_percent(application.get('forecast_revenue_cagr', 0))}; confidence {format_score(application.get('forecast_plan_confidence_score', 0))}"},
        {"Driver group": "Narrative", "Score": format_score(signals.get("narrative_consistency_risk_score", 0)), "Status": "Aligned" if _number(signals.get("narrative_consistency_risk_score")) < 0.35 else "Check", "Banker signal": "Compares applicant context with financial and document signals."},
    ]


def data_source_badges(application, signals):
    statuses = [
        ("PSD2/Open Banking", "ready" if _number(application.get("bank_statements_uploaded")) >= 0.5 else "review"),
        ("Accounting", "ready" if _number(application.get("financial_statements_uploaded")) >= 0.5 else "review"),
        ("Documents", "ready" if _number(signals.get("document_completeness_score")) >= 0.8 else "partial"),
        ("Registry/KYB", "ready" if _number(application.get("ownership_docs_uploaded")) >= 0.5 else "review"),
        ("Management context", "ready" if str(application.get("loan_purpose_context", "")).strip() else "partial"),
        ("Five-year plan", "ready" if _number(application.get("forecast_support_uploaded")) >= 0.5 else "partial"),
    ]
    labels = {"ready": "Ready", "partial": "Partial", "review": "Needs review"}
    return [{"Source": source, "Tone": tone, "Status": labels[tone]} for source, tone in statuses]


def decision_timeline(application, prediction, review=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = [
        {"Step": "1", "Event": "Application intake", "Status": "Received", "Detail": application.get("company_name", "Session Applicant")},
        {"Step": "2", "Event": "Data readiness", "Status": "Checked", "Detail": f"{len(missing_documents(application))} missing document item(s)"},
        {"Step": "3", "Event": "Model score", "Status": prediction.get("decision", ""), "Detail": f"Grade {prediction.get('grade', '')}; score {format_percent(prediction.get('fraud_probability', 0))}"},
    ]
    if review:
        rows.append({"Step": "4", "Event": "Analyst review", "Status": review.get("final_decision", ""), "Detail": f"Saved {review.get('timestamp', now)}"})
        if review.get("send_email"):
            rows.append({"Step": "5", "Event": "Supervisor package", "Status": "Email prepared", "Detail": review.get("supervisor_email", "")})
    else:
        rows.append({"Step": "4", "Event": "Analyst review", "Status": "Pending", "Detail": "Awaiting case review action"})
    return rows


def model_confidence_rows(metrics, prediction, signals):
    probability = _number(prediction.get("fraud_probability"))
    nearest_boundary = min(abs(probability - 0.15), abs(probability - 0.28), abs(probability - 0.42), abs(probability - 0.58), abs(probability - 0.74))
    evidence_strength = (
        0.35 * _number(signals.get("document_completeness_score"))
        + 0.25 * (1 - _number(signals.get("narrative_consistency_risk_score")))
        + 0.20 * (1 - _number(signals.get("process_integrity_risk_score")))
        + 0.20 * min(nearest_boundary / 0.12, 1)
    )
    confidence = "High" if evidence_strength >= 0.75 else "Medium" if evidence_strength >= 0.5 else "Low"
    return [
        {"Item": "Model confidence", "Value": confidence, "Meaning": "Combines data completeness, narrative consistency, process integrity, and distance from grade thresholds."},
        {"Item": "Training ROC-AUC", "Value": format_score(metrics.get("roc_auc", 0), 3), "Meaning": "Validation metric for ranking high-risk cases."},
        {"Item": "Grade boundary distance", "Value": format_percent(nearest_boundary), "Meaning": "Lower values mean the case is closer to a grade threshold."},
        {"Item": "Human review rule", "Value": "Required for C-F or manual adjustments", "Meaning": "Supports banker decisioning and governance."},
    ]


def credit_memo(application, prediction, explanation, review, terms, monitoring, timeline):
    lines = [
        "# CredRisk.AI Credit Memo",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Applicant",
        f"Company: {application.get('company_name', 'Session Applicant')}",
        f"Application ID: {application.get('application_id', 'Session application')}",
        f"Industry: {application.get('industry', '')}",
        f"Region: {application.get('region', '')}",
        f"Requested amount: {format_currency(application.get('requested_amount', 0))}",
        f"Term: {format_months(application.get('term_months', 0))}",
        f"Interest rate: {format_percent(application.get('interest_rate', 0))}",
        "",
        "## Decision",
        f"Application risk score: {format_percent(prediction.get('fraud_probability', 0))}",
        f"Risk grade: {prediction.get('grade', '')}",
        f"Model recommendation: {prediction.get('decision', '')}",
        f"Final decision: {review.get('final_decision', 'Pending Review') if review else 'Pending Review'}",
        "",
        "## Recommended Loan Terms",
    ]
    lines.extend(f"- {row['Term']}: {row['Recommendation']} ({row['Rationale']})" for row in terms)
    lines.extend(["", "## Portfolio Monitoring"])
    lines.extend(f"- {row['Monitor']}: {row['Output']} ({row['Trigger']})" for row in monitoring)
    lines.extend(["", "## Decision Timeline"])
    lines.extend(f"- {row['Step']}. {row['Event']}: {row['Status']} - {row['Detail']}" for row in timeline)
    lines.extend(["", "## Rationale", explanation])
    if review:
        lines.extend(
            [
                "",
                "## Analyst Review",
                f"Action: {review.get('action', '')}",
                f"Supervisor mailbox: {review.get('supervisor_email', '')}",
                f"Analyst note: {review.get('analyst_note', '')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Governance Note",
            "This memo is generated for banker decision support. It is not a legal credit decision or a production risk model output.",
        ]
    )
    return "\n".join(lines)
