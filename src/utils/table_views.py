# DataFrame display helpers that keep lender tables readable and consistent.
from src.utils.formatting import (
    format_currency,
    format_integer,
    format_months,
    format_percent,
    format_score,
)

APPLICATION_COLUMN_LABELS = {
    # These labels are shared by Home, Operations Desk, Risk Dashboard, and
    # Personal Workspace. Centralizing them keeps the same field from appearing
    # under different names across lender pages.
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
    # The helper is intentionally small: it selects columns, formats known value
    # types, and renames labels. It does not sort, filter, or mutate the source
    # dataframe because each page owns those workflow decisions.
    # Only requested columns that exist are shown, so shared table calls work across different page data.
    available_columns = [column for column in columns if column in frame.columns]
    display = frame[available_columns].copy()
    # Format values after column selection so source dataframes remain numeric
    # for filtering, scoring, and charting.
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
    # Aliases let individual pages override generic labels without mutating the source dataframe.
    return display.rename(columns=labels)
