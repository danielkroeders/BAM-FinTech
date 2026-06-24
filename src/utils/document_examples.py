import csv
import re
from datetime import datetime
from io import StringIO

from src.utils.document_storage import DOCUMENT_CATEGORIES


def _safe_filename(value):
    cleaned = re.sub(r"[^a-z0-9]+", "-", str(value or "sme-applicant").lower()).strip("-")
    return cleaned[:48] or "sme-applicant"


def _number(application, key, fallback=0.0):
    try:
        return float(application.get(key, fallback) or fallback)
    except (TypeError, ValueError):
        return float(fallback)


def _csv_bytes(rows, fieldnames):
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _month_label(year_month_index):
    year = (year_month_index - 1) // 12
    month = (year_month_index - 1) % 12 + 1
    return f"{year}-{month:02d}"


def build_document_examples(application, generated_on=None):
    """Build fictional SME document examples from the current application values.

    The returned files are deliberately simple CSVs so they can be downloaded,
    inspected, and re-uploaded through the same Streamlit document flow.
    """

    generated_on = generated_on or datetime.now()
    company = str(application.get("company_name") or "SME Applicant").strip() or "SME Applicant"
    safe_company = _safe_filename(company)
    prior_year = generated_on.year - 1
    revenue = max(_number(application, "annual_revenue", 850_000), 1.0)
    requested_amount = max(_number(application, "requested_amount", 250_000), 1.0)
    existing_debt = max(_number(application, "existing_debt", 0), 0.0)
    free_cash_flow = _number(application, "free_cash_flow", revenue * 0.08)
    monthly_burn_rate = max(_number(application, "monthly_burn_rate", revenue / 18), 1.0)
    forecast_growth = _number(application, "forecast_revenue_cagr", 0.12)
    base_monthly_revenue = revenue / 12
    loan_purpose = str(application.get("loan_purpose_context") or "Working-capital and growth financing").strip()

    financial_rows = [
        {
            "statement_year": prior_year,
            "line_item": "Revenue",
            "amount_eur": round(revenue),
            "notes": "Replace with audited or management-account revenue.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Cost of sales",
            "amount_eur": round(revenue * 0.58),
            "notes": "Direct delivery, materials, and fulfillment costs.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Gross profit",
            "amount_eur": round(revenue * 0.42),
            "notes": "Revenue minus cost of sales.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Operating expenses",
            "amount_eur": round(revenue * 0.27),
            "notes": "Payroll, rent, software, marketing, and admin.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Free cash flow",
            "amount_eur": round(free_cash_flow),
            "notes": "Operating cash flow after maintenance capex.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Cash and equivalents",
            "amount_eur": round(max(monthly_burn_rate * 4, requested_amount * 0.2)),
            "notes": "Closing bank and cash balance.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Existing debt",
            "amount_eur": round(existing_debt),
            "notes": "Loans, leases, overdrafts, and other financial debt.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Equity",
            "amount_eur": round(max(revenue * 0.18, 1)),
            "notes": "Share capital plus retained earnings.",
        },
    ]

    first_month = generated_on.year * 12 + generated_on.month - 5
    bank_rows = []
    ending_balance = max(monthly_burn_rate * 3, requested_amount * 0.15)
    for offset in range(6):
        inflows = base_monthly_revenue * (0.92 + offset * 0.025)
        outflows = min(inflows * 0.88, inflows - free_cash_flow / 12)
        ending_balance += inflows - outflows
        bank_rows.append(
            {
                "period": _month_label(first_month + offset),
                "account": "Operating account",
                "total_inflows_eur": round(inflows),
                "total_outflows_eur": round(outflows),
                "ending_balance_eur": round(max(ending_balance, 0)),
                "overdraft_days": 0 if ending_balance > monthly_burn_rate else 2,
                "largest_counterparty": "Example customer / supplier",
            }
        )

    taxable_profit = max(free_cash_flow * 0.85, revenue * 0.04)
    tax_rows = [
        {
            "tax_year": prior_year,
            "field": "Taxpayer legal name",
            "example_value": company,
            "notes": "Use the exact name from the filed return.",
        },
        {
            "tax_year": prior_year,
            "field": "Reported turnover",
            "example_value": round(revenue),
            "notes": "Should reconcile to the financial statements.",
        },
        {
            "tax_year": prior_year,
            "field": "Taxable profit",
            "example_value": round(taxable_profit),
            "notes": "Profit after allowable deductions.",
        },
        {
            "tax_year": prior_year,
            "field": "Corporate income tax paid",
            "example_value": round(taxable_profit * 0.25),
            "notes": "Use the final assessment or filed return.",
        },
        {
            "tax_year": prior_year,
            "field": "VAT / sales tax filing status",
            "example_value": "Filed through latest quarter",
            "notes": "Mention any arrears or payment plans.",
        },
    ]

    kyb_rows = [
        {
            "evidence_type": "Company registry extract",
            "example_value": company,
            "owner_or_source": "National business registry",
            "status": "Current",
        },
        {
            "evidence_type": "Registration number",
            "example_value": f"DEMO-{safe_company[:8].upper()}-2026",
            "owner_or_source": "National business registry",
            "status": "Current",
        },
        {
            "evidence_type": "Director identity",
            "example_value": "Managing director verified",
            "owner_or_source": "Board / company secretary",
            "status": "Current",
        },
        {
            "evidence_type": "Ultimate beneficial owner",
            "example_value": "Founder shareholder - 70%",
            "owner_or_source": "Shareholder register",
            "status": "Current",
        },
        {
            "evidence_type": "Ultimate beneficial owner",
            "example_value": "Management shareholder - 30%",
            "owner_or_source": "Shareholder register",
            "status": "Current",
        },
        {
            "evidence_type": "Sanctions / PEP screening",
            "example_value": "No demo alerts",
            "owner_or_source": "KYB provider",
            "status": "Replace with real screening result",
        },
    ]

    forecast_rows = []
    for offset in range(1, 7):
        growth_factor = 1 + forecast_growth * (offset / 12)
        expected_revenue = base_monthly_revenue * growth_factor
        contracted_revenue = expected_revenue * 0.62
        operating_costs = max(monthly_burn_rate, expected_revenue * 0.72)
        debt_service = requested_amount / max(_number(application, "term_months", 60), 1) * 1.08
        forecast_rows.append(
            {
                "forecast_month": _month_label(generated_on.year * 12 + generated_on.month + offset),
                "contracted_revenue_eur": round(contracted_revenue),
                "pipeline_revenue_eur": round(expected_revenue - contracted_revenue),
                "operating_costs_eur": round(operating_costs),
                "planned_debt_service_eur": round(debt_service),
                "evidence_note": loan_purpose[:120],
            }
        )

    generated_date = generated_on.strftime("%Y-%m-%d")
    return {
        "financial_statements": {
            "label": DOCUMENT_CATEGORIES["financial_statements"],
            "file_name": f"{safe_company}_example_financial_statements.csv",
            "mime_type": "text/csv",
            "description": "Prior-year income statement, cash, debt, and equity line items.",
            "content": _csv_bytes(financial_rows, ["statement_year", "line_item", "amount_eur", "notes"]),
            "generated_date": generated_date,
        },
        "bank_statements": {
            "label": DOCUMENT_CATEGORIES["bank_statements"],
            "file_name": f"{safe_company}_example_bank_statements.csv",
            "mime_type": "text/csv",
            "description": "Six months of inflows, outflows, balances, overdraft days, and counterparties.",
            "content": _csv_bytes(
                bank_rows,
                [
                    "period",
                    "account",
                    "total_inflows_eur",
                    "total_outflows_eur",
                    "ending_balance_eur",
                    "overdraft_days",
                    "largest_counterparty",
                ],
            ),
            "generated_date": generated_date,
        },
        "tax_returns": {
            "label": DOCUMENT_CATEGORIES["tax_returns"],
            "file_name": f"{safe_company}_example_tax_return_summary.csv",
            "mime_type": "text/csv",
            "description": "Filed turnover, taxable profit, tax paid, and filing status.",
            "content": _csv_bytes(tax_rows, ["tax_year", "field", "example_value", "notes"]),
            "generated_date": generated_date,
        },
        "ownership_kyb": {
            "label": DOCUMENT_CATEGORIES["ownership_kyb"],
            "file_name": f"{safe_company}_example_ownership_kyb.csv",
            "mime_type": "text/csv",
            "description": "Registry, director, UBO, shareholder, and screening evidence.",
            "content": _csv_bytes(kyb_rows, ["evidence_type", "example_value", "owner_or_source", "status"]),
            "generated_date": generated_date,
        },
        "forecast_support": {
            "label": DOCUMENT_CATEGORIES["forecast_support"],
            "file_name": f"{safe_company}_example_forecast_support.csv",
            "mime_type": "text/csv",
            "description": "Monthly revenue forecast, committed pipeline, costs, debt service, and assumptions.",
            "content": _csv_bytes(
                forecast_rows,
                [
                    "forecast_month",
                    "contracted_revenue_eur",
                    "pipeline_revenue_eur",
                    "operating_costs_eur",
                    "planned_debt_service_eur",
                    "evidence_note",
                ],
            ),
            "generated_date": generated_date,
        },
    }
