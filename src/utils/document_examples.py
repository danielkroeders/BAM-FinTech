# Fictional document pack generator for SME sample evidence cases.
import csv
import re
from datetime import datetime
from io import StringIO

import pandas as pd

from src.core.data_pipeline import build_forecast_table
from src.utils.document_storage import DOCUMENT_CATEGORIES

# Sample evidence files are intentionally CSV and fictional. They are realistic
# enough for the validation workflow to detect categories/red flags, but they
# never represent real companies or real financial statements.

def _safe_filename(value):
    # Generated file names use the company name but must remain safe for local storage.
    cleaned = re.sub(r"[^a-z0-9]+", "-", str(value or "sme-applicant").lower()).strip(
        "-"
    )
    return cleaned[:48] or "sme-applicant"


def _number(application, key, fallback=0.0):
    # Sample documents are generated from whatever fields are currently present
    # on the application, so missing or blank values need safe numeric fallbacks.
    try:
        return float(application.get(key, fallback) or fallback)
    except (TypeError, ValueError):
        return float(fallback)


def _csv_bytes(rows, fieldnames):
    # CSV examples are simple text files so users can inspect and download them without special tooling.
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _month_label(year_month_index):
    year = (year_month_index - 1) // 12
    month = (year_month_index - 1) % 12 + 1
    return f"{year}-{month:02d}"


def _annual_forecast_support_rows(application, loan_purpose, fraudulent=False):
    # Forecast support mirrors the exact five annual rows the SME submits. That
    # keeps sample evidence aligned with the intake table and avoids pretending
    # that a monthly pipeline file is the same thing as a five-year plan.
    forecast = build_forecast_table(pd.DataFrame([application]))
    standard_notes = {
        1: "Run-rate bridge from current revenue and signed near-term work.",
        2: "Pipeline conversion and operating-cost assumptions reviewed by management.",
        3: "Capacity, staffing, and gross-margin assumptions tied to the submitted plan.",
        4: "Debt schedule assumes normal amortisation and no hidden refinancing.",
        5: f"Long-range plan case supporting the loan purpose: {loan_purpose[:80]}",
    }
    fraudulent_notes = {
        1: "Unsupported growth assumption introduced after bank statements; audit trail missing.",
        2: "Unsigned LOI treated as contracted revenue; manual revenue adjustment not disclosed.",
        3: "Pipeline revenue conflicts with tax turnover; related-party concentration not disclosed.",
        4: "Debt paydown jumps despite negative bank cash flow; repayment source not reconciled.",
        5: "Free-cash-flow improvement unsupported by contracts; late-stage spreadsheet override.",
    }
    notes = fraudulent_notes if fraudulent else standard_notes

    rows = []
    for record in forecast.to_dict("records"):
        year = int(record["forecast_year"])
        rows.append(
            {
                "forecast_year": year,
                "projected_revenue_eur": round(float(record["projected_revenue"])),
                "projected_employees": int(record["projected_employees"]),
                "projected_free_cash_flow_eur": round(
                    float(record["projected_free_cash_flow"])
                ),
                "projected_debt_eur": round(float(record["projected_debt"])),
                "assumptions_evidence_note": notes.get(
                    year, "Annual plan assumption supplied by the applicant."
                ),
            }
        )
    return rows


def _fraudulent_document_rows(
    company,
    safe_company,
    prior_year,
    generated_on,
    revenue,
    requested_amount,
    existing_debt,
    free_cash_flow,
    monthly_burn_rate,
    base_monthly_revenue,
):
    """Return fictional non-forecast document rows with deliberate red flags."""

    # Fraudulent packs intentionally contradict tax, bank, KYB, and forecast evidence for lender validation.
    # The contradictions use phrases from RED_FLAG_MARKERS in document_validation
    # so the lender can demonstrate a mismatch/needs-review workflow.
    claimed_revenue = revenue * 1.48
    tax_reported_revenue = revenue * 0.56
    adjusted_cash_flow = max(abs(free_cash_flow) * 0.6, revenue * 0.06)
    financial_rows = [
        {
            "statement_year": prior_year,
            "line_item": "Revenue",
            "amount_eur": round(claimed_revenue),
            "notes": "Applicant-submitted revenue is unreconciled to tax turnover and bank deposits.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Manual revenue adjustment",
            "amount_eur": round(claimed_revenue - revenue),
            "notes": "Late-stage spreadsheet override with missing invoice identifiers.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Gross profit",
            "amount_eur": round(claimed_revenue * 0.54),
            "notes": "Margin uplift conflicts with supplier payment history.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Operating expenses",
            "amount_eur": round(revenue * 0.24),
            "notes": "Expense lines exclude related-party service fees found in bank activity.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Free cash flow",
            "amount_eur": round(adjusted_cash_flow),
            "notes": "Restated from negative ledger export without source-system audit trail.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Cash and equivalents",
            "amount_eur": round(max(requested_amount * 0.42, monthly_burn_rate * 5)),
            "notes": "Closing cash balance conflicts with ending bank statement balance.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Existing debt",
            "amount_eur": round(existing_debt * 0.45),
            "notes": "Excludes two same-day lender advances disclosed in transaction notes.",
        },
        {
            "statement_year": prior_year,
            "line_item": "Equity",
            "amount_eur": round(max(revenue * 0.22, 1)),
            "notes": "Equity figure cannot be tied to filed accounts.",
        },
    ]

    first_month = generated_on.year * 12 + generated_on.month - 5
    bank_rows = []
    ending_balance = max(monthly_burn_rate, requested_amount * 0.05)
    related_parties = [
        "Azul Trade Partners - related party",
        "North Coast Procurement - shared director",
        "Blue Market Holdings - undisclosed affiliate",
    ]
    for offset in range(6):
        circular_transfer = requested_amount * (0.12 + offset * 0.01)
        inflows = base_monthly_revenue * (0.72 + offset * 0.02) + circular_transfer
        outflows = inflows * 0.97 + monthly_burn_rate * 0.12
        ending_balance += inflows - outflows
        bank_rows.append(
            {
                "period": _month_label(first_month + offset),
                "account": f"Operating account DEMO-{safe_company[:6].upper()}",
                "total_inflows_eur": round(inflows),
                "total_outflows_eur": round(outflows),
                "ending_balance_eur": round(max(ending_balance, 0)),
                "overdraft_days": 9 + offset,
                "largest_counterparty": (
                    f"{related_parties[offset % len(related_parties)]}; "
                    "round-number same-day in/out transfer"
                ),
            }
        )

    taxable_profit = max(tax_reported_revenue * 0.03, 1)
    tax_rows = [
        {
            "tax_year": prior_year,
            "field": "Taxpayer legal name",
            "example_value": company,
            "notes": "Filed return uses shortened trade name; legal-name match needs confirmation.",
        },
        {
            "tax_year": prior_year,
            "field": "Reported turnover",
            "example_value": round(tax_reported_revenue),
            "notes": "Tax turnover materially below submitted financial statements.",
        },
        {
            "tax_year": prior_year,
            "field": "Taxable profit",
            "example_value": round(taxable_profit),
            "notes": "Low profit conflicts with high claimed cash generation.",
        },
        {
            "tax_year": prior_year,
            "field": "Corporate income tax paid",
            "example_value": round(taxable_profit * 0.25),
            "notes": "Payment reference missing from bank statement extracts.",
        },
        {
            "tax_year": prior_year,
            "field": "VAT / sales tax filing status",
            "example_value": "Late filings and unresolved arrears",
            "notes": "Compliance status conflicts with applicant declaration.",
        },
    ]

    kyb_rows = [
        {
            "evidence_type": "Company registry extract",
            "example_value": company,
            "owner_or_source": "National business registry",
            "status": "Extract is older than 12 months.",
        },
        {
            "evidence_type": "Registration number",
            "example_value": f"DEMO-{safe_company[:8].upper()}-2026",
            "owner_or_source": "National business registry",
            "status": "Registration number format differs across submitted files.",
        },
        {
            "evidence_type": "Director identity",
            "example_value": "Managing director unresolved",
            "owner_or_source": "Board / company secretary",
            "status": "Director name does not match bank mandate.",
        },
        {
            "evidence_type": "Ultimate beneficial owner",
            "example_value": "Founder shareholder - 70%",
            "owner_or_source": "Shareholder register",
            "status": "UBO not present in registry extract.",
        },
        {
            "evidence_type": "Ultimate beneficial owner",
            "example_value": "Blue Market Holdings - 30%",
            "owner_or_source": "Shareholder register",
            "status": "Related-party exposure not disclosed in application narrative.",
        },
        {
            "evidence_type": "Sanctions / PEP screening",
            "example_value": "Possible sanctions fuzzy match",
            "owner_or_source": "KYB provider",
            "status": "Unresolved screening alert requires compliance escalation.",
        },
    ]

    return financial_rows, bank_rows, tax_rows, kyb_rows


def build_document_examples(application, generated_on=None):
    """Build fictional SME document examples from the current application values.

    The returned files are deliberately simple CSVs so they can be downloaded,
    inspected, and re-uploaded through the same Streamlit document flow.
    """

    generated_on = generated_on or datetime.now()
    # The sample pack is derived from the active application so filenames and values match the scenario.
    # Standard packs are mostly coherent; fraudulent packs below replace the row
    # contents with deliberately inconsistent evidence.
    company = (
        str(application.get("company_name") or "SME Applicant").strip()
        or "SME Applicant"
    )
    safe_company = _safe_filename(company)
    prior_year = generated_on.year - 1
    revenue = max(_number(application, "annual_revenue", 850_000), 1.0)
    requested_amount = max(_number(application, "requested_amount", 250_000), 1.0)
    existing_debt = max(_number(application, "existing_debt", 0), 0.0)
    free_cash_flow = _number(application, "free_cash_flow", revenue * 0.08)
    monthly_burn_rate = max(
        _number(application, "monthly_burn_rate", revenue / 18), 1.0
    )
    base_monthly_revenue = revenue / 12
    loan_purpose = str(
        application.get("loan_purpose_context")
        or "Working-capital and growth financing"
    ).strip()

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

    forecast_rows = _annual_forecast_support_rows(application, loan_purpose)

    file_variant = "example"
    descriptions = {
        "financial_statements": "Prior-year income statement, cash, debt, and equity line items.",
        "bank_statements": "Six months of inflows, outflows, balances, overdraft days, and counterparties.",
        "tax_returns": "Filed turnover, taxable profit, tax paid, and filing status.",
        "ownership_kyb": "Registry, director, UBO, shareholder, and screening evidence.",
        "forecast_support": "Annual five-year plan rows, free-cash-flow assumptions, debt path, and evidence notes.",
    }
    if str(application.get("sample_document_profile", "")).lower() == "fraudulent":
        (
            financial_rows,
            bank_rows,
            tax_rows,
            kyb_rows,
        ) = _fraudulent_document_rows(
            company,
            safe_company,
            prior_year,
            generated_on,
            revenue,
            requested_amount,
            existing_debt,
            free_cash_flow,
            monthly_burn_rate,
            base_monthly_revenue,
        )
        forecast_rows = _annual_forecast_support_rows(
            application, loan_purpose, fraudulent=True
        )
        file_variant = "flagged"
        descriptions = {
            "financial_statements": "Financial statements with unreconciled manual adjustments and debt omissions.",
            "bank_statements": "Bank activity with round-number transfers, overdrafts, and related-party counterparties.",
            "tax_returns": "Tax summary that conflicts with the submitted financial statements.",
            "ownership_kyb": "KYB evidence with UBO, registry, and screening inconsistencies.",
            "forecast_support": "Annual forecast support with unsupported jumps, debt contradictions, and unsigned assumptions.",
        }

    generated_date = generated_on.strftime("%Y-%m-%d")
    return {
        "financial_statements": {
            "label": DOCUMENT_CATEGORIES["financial_statements"],
            "file_name": f"{safe_company}_{file_variant}_financial_statements.csv",
            "mime_type": "text/csv",
            "description": descriptions["financial_statements"],
            "content": _csv_bytes(
                financial_rows, ["statement_year", "line_item", "amount_eur", "notes"]
            ),
            "generated_date": generated_date,
        },
        "bank_statements": {
            "label": DOCUMENT_CATEGORIES["bank_statements"],
            "file_name": f"{safe_company}_{file_variant}_bank_statements.csv",
            "mime_type": "text/csv",
            "description": descriptions["bank_statements"],
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
            "file_name": f"{safe_company}_{file_variant}_tax_return_summary.csv",
            "mime_type": "text/csv",
            "description": descriptions["tax_returns"],
            "content": _csv_bytes(
                tax_rows, ["tax_year", "field", "example_value", "notes"]
            ),
            "generated_date": generated_date,
        },
        "ownership_kyb": {
            "label": DOCUMENT_CATEGORIES["ownership_kyb"],
            "file_name": f"{safe_company}_{file_variant}_ownership_kyb.csv",
            "mime_type": "text/csv",
            "description": descriptions["ownership_kyb"],
            "content": _csv_bytes(
                kyb_rows,
                ["evidence_type", "example_value", "owner_or_source", "status"],
            ),
            "generated_date": generated_date,
        },
        "forecast_support": {
            "label": DOCUMENT_CATEGORIES["forecast_support"],
            "file_name": f"{safe_company}_{file_variant}_forecast_support.csv",
            "mime_type": "text/csv",
            "description": descriptions["forecast_support"],
            "content": _csv_bytes(
                forecast_rows,
                [
                    "forecast_year",
                    "projected_revenue_eur",
                    "projected_employees",
                    "projected_free_cash_flow_eur",
                    "projected_debt_eur",
                    "assumptions_evidence_note",
                ],
            ),
            "generated_date": generated_date,
        },
    }
