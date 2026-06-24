from src.utils.formatting import (
    format_currency,
    format_integer,
    format_months,
    format_percent,
    format_score,
)

APPLICATION_COLUMN_LABELS = {
    "application_id": "Application ID",
    "company_name": "Company",
    "industry": "Industry",
    "region": "Region",
    "requested_amount": "Requested amount",
    "fraud_probability": "Application risk score",
    "final_probability": "Final application risk score",
    "grade": "Grade",
    "decision": "Model recommendation",
    "queue_status": "Task status",
    "review_action": "Review action",
    "final_decision": "Final decision",
    "missing_documents": "Missing docs",
    "assigned_analyst": "Assigned analyst",
    "sla": "SLA",
    "interest_rate": "Interest rate",
    "free_cash_flow": "Free cash flow",
    "expected_runway_months": "Expected runway",
    "document_completeness_score": "Document completeness",
}


def application_table(frame, columns, aliases=None):
    available_columns = [column for column in columns if column in frame.columns]
    display = frame[available_columns].copy()
    for column in [
        "requested_amount",
        "existing_debt",
        "annual_revenue",
        "free_cash_flow",
        "final_probability",
    ]:
        if column in display and column != "final_probability":
            display[column] = display[column].apply(format_currency)
    for column in ["fraud_probability", "interest_rate"]:
        if column in display:
            display[column] = display[column].apply(format_percent)
    if "final_probability" in display:
        display["final_probability"] = display["final_probability"].apply(
            format_percent
        )
    if "expected_runway_months" in display:
        display["expected_runway_months"] = display["expected_runway_months"].apply(
            format_months
        )
    if "document_completeness_score" in display:
        display["document_completeness_score"] = display[
            "document_completeness_score"
        ].apply(format_score)
    if "missing_documents" in display:
        display["missing_documents"] = display["missing_documents"].apply(
            format_integer
        )

    labels = {**APPLICATION_COLUMN_LABELS, **(aliases or {})}
    return display.rename(columns=labels)
