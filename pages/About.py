import pandas as pd
import streamlit as st

from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="About", layout="wide")
bootstrap_state()
render_sidebar()

st.title("About")
st.caption("Definitions for the workspace scoring dimensions used by the SME application-risk model.")

st.info(
    "Scores help prioritize analyst review and do not establish legal, "
    "credit, or compliance certainty."
)

dimensions = [
    {
        "Dimension": "Industry",
        "Definition": "The applicant company's primary business sector.",
        "Why it matters": "Fraud patterns and cash-flow volatility can differ by sector.",
    },
    {
        "Dimension": "Region",
        "Definition": "The applicant's operating or lending region.",
        "Why it matters": "Regional market conditions and country-risk assumptions affect fraud exposure.",
    },
    {
        "Dimension": "Company type",
        "Definition": "The applicant's legal or operating structure, such as LLC, corporation, partnership, or sole proprietorship.",
        "Why it matters": "Entity structure can correlate with documentation depth and verification complexity.",
    },
    {
        "Dimension": "Requested amount",
        "Definition": "The loan principal requested by the applicant.",
        "Why it matters": "Large requests relative to business scale can indicate elevated repayment or anomaly risk.",
    },
    {
        "Dimension": "Term months",
        "Definition": "The requested loan duration in months.",
        "Why it matters": "Loan duration shapes exposure time and can interact with cash-flow risk.",
    },
    {
        "Dimension": "Interest rate",
        "Definition": "The offered annual interest rate for the requested facility.",
        "Why it matters": "Higher pricing can materially increase debt-service burden and reduce repayment coverage.",
    },
    {
        "Dimension": "Annual revenue",
        "Definition": "The applicant's reported yearly business revenue.",
        "Why it matters": "Revenue is used to assess business scale and whether the requested amount is proportionate.",
    },
    {
        "Dimension": "Years in business",
        "Definition": "How long the company has been operating.",
        "Why it matters": "Short operating histories may provide less evidence for identity, stability, and repayment behavior.",
    },
    {
        "Dimension": "Existing debt",
        "Definition": "The applicant's reported outstanding business debt.",
        "Why it matters": "High debt pressure relative to revenue can signal credit stacking or financial stress.",
    },
    {
        "Dimension": "Recent loans in the last 12 months",
        "Definition": "Count of new or recent loan obligations within the past year.",
        "Why it matters": "Multiple recent loans can indicate rapid borrowing behavior that merits review.",
    },
    {
        "Dimension": "Late payment ratio",
        "Definition": "Share of observed payments that were late.",
        "Why it matters": "Higher late-payment behavior can indicate repayment stress or unreliable payment patterns.",
    },
    {
        "Dimension": "Suspicious transfer ratio",
        "Definition": "Share of transfers flagged as unusual in the transaction profile.",
        "Why it matters": "Unusual transfer patterns can be a fraud indicator and are weighted heavily in the model.",
    },
    {
        "Dimension": "Collateral ratio",
        "Definition": "Estimated collateral value divided by the requested loan amount.",
        "Why it matters": "Lower collateral coverage can increase loss exposure and raise review priority.",
    },
    {
        "Dimension": "Employees",
        "Definition": "Reported number of employees at the applicant company.",
        "Why it matters": "Employee count helps establish company scale and consistency with revenue and loan size.",
    },
    {
        "Dimension": "Country risk score",
        "Definition": "A score from 0 to 1 representing jurisdictional or country-level risk.",
        "Why it matters": "Higher values indicate greater contextual risk assumptions.",
    },
    {
        "Dimension": "Free cash flow",
        "Definition": "Annual cash generated after operating and investment needs.",
        "Why it matters": "Positive free cash flow can mitigate risk, while negative cash flow can indicate liquidity pressure.",
    },
    {
        "Dimension": "Monthly burn rate",
        "Definition": "Estimated monthly cash consumption at application date.",
        "Why it matters": "High burn can shorten runway and increase pressure to obtain external financing.",
    },
    {
        "Dimension": "Cash flow / revenue",
        "Definition": "Free cash flow divided by annual revenue.",
        "Why it matters": "Shows whether reported revenue is converting into usable cash.",
    },
    {
        "Dimension": "Expected runway months",
        "Definition": "Estimated months cash reserves can support the current burn rate.",
        "Why it matters": "Short runway can raise liquidity risk and review priority.",
    },
    {
        "Dimension": "Expected annual revenue growth",
        "Definition": "Applicant's expected compound annual revenue growth over five years.",
        "Why it matters": "Aggressive growth assumptions can increase execution risk when unsupported by current signals.",
    },
    {
        "Dimension": "Expected annual employee growth",
        "Definition": "Applicant's expected compound annual employee growth over five years.",
        "Why it matters": "Employee growth helps assess whether revenue growth is operationally supported.",
    },
    {
        "Dimension": "Year 5 FCF margin target",
        "Definition": "Target free-cash-flow margin at the end of the five-year plan.",
        "Why it matters": "Large margin improvement from weak current cash flow can signal plan risk.",
    },
    {
        "Dimension": "Planned debt reduction",
        "Definition": "Share of existing debt management expects to reduce over five years.",
        "Why it matters": "Debt reduction plans can be strained when current cash-flow pressure is high.",
    },
    {
        "Dimension": "Plan confidence score",
        "Definition": "Banker-assessed confidence in the five-year plan from 0 to 1.",
        "Why it matters": "Lower confidence increases execution risk and supports manual review.",
    },
    {
        "Dimension": "Current and quick ratios",
        "Definition": "Liquidity ratios summarizing current assets and liquid assets against current liabilities.",
        "Why it matters": "Weak short-term liquidity can reveal stress not visible from revenue alone.",
    },
    {
        "Dimension": "Receivables, payables, and inventory days",
        "Definition": "Working-capital timing assumptions used to estimate cash conversion cycle.",
        "Why it matters": "Long collection or inventory cycles can pressure cash flow and repayment capacity.",
    },
    {
        "Dimension": "Document checklist",
        "Definition": "Present/not-present status for financial statements, bank statements, tax return, KYB, and forecast support.",
        "Why it matters": "Missing support can reduce audit readiness and increase manual review priority.",
    },
    {
        "Dimension": "Document edits and late-stage changes",
        "Definition": "Observed resubmission or change counts after initial intake.",
        "Why it matters": "Repeated edits or late changes can indicate process anomalies or weak documentation quality.",
    },
    {
        "Dimension": "Digital identity age",
        "Definition": "Age of email domain, website, and primary business bank account in months.",
        "Why it matters": "Very young identity markers can increase KYB verification risk.",
    },
    {
        "Dimension": "Mismatch and duplicate signals",
        "Definition": "Scores for location mismatch, duplicate contact details, and shared identifiers.",
        "Why it matters": "Shared or inconsistent identifiers can indicate entity-resolution or application-channel risk.",
    },
    {
        "Dimension": "Related-party and counterparty signals",
        "Definition": "Scores for related-party exposure and counterparty concentration.",
        "Why it matters": "Entity complexity and concentrated counterparties can require deeper network review.",
    },
]

st.subheader("Scoring Dimensions")
st.dataframe(pd.DataFrame(dimensions), width="stretch", hide_index=True)

st.subheader("Derived Risk Signals")
derived_dimensions = [
    {
        "Signal": "Debt-to-revenue ratio",
        "Definition": "Existing debt divided by annual revenue.",
        "Why it matters": "Higher debt pressure can indicate financial distress or incentive pressure.",
    },
    {
        "Signal": "Request-to-revenue ratio",
        "Definition": "Requested loan amount divided by annual revenue.",
        "Why it matters": "Large exposure relative to business scale can merit closer review.",
    },
    {
        "Signal": "Loan velocity score",
        "Definition": "Normalized count of recent loans.",
        "Why it matters": "Rapid borrowing can suggest credit stacking or liquidity stress.",
    },
    {
        "Signal": "Payment stress score",
        "Definition": "Combined late-payment behavior and debt pressure.",
        "Why it matters": "Payment stress is a practical early warning signal for risk triage.",
    },
    {
        "Signal": "Transaction anomaly score",
        "Definition": "Combined suspicious transfer ratio, payment behavior, country risk, and borrowing velocity.",
        "Why it matters": "Fraud literature emphasizes unusual transaction patterns and behavioral anomalies.",
    },
    {
        "Signal": "Financial distress score",
        "Definition": "Combined debt, late payments, collateral gap, and short operating history.",
        "Why it matters": "Fraud-triangle research highlights financial pressure and distress as important risk factors.",
    },
    {
        "Signal": "Cash-flow pressure score",
        "Definition": "Combined negative free cash flow and burn intensity.",
        "Why it matters": "Weak liquidity can create pressure to seek financing or misstate business health.",
    },
    {
        "Signal": "Runway risk score",
        "Definition": "A normalized short-runway measure based on expected runway months.",
        "Why it matters": "Applicants with limited runway may require closer analyst review.",
    },
    {
        "Signal": "Cash conversion risk score",
        "Definition": "Measures weak free-cash-flow conversion relative to revenue, adjusted by payment stress.",
        "Why it matters": "Revenue that does not convert to cash can signal fragility or documentation concerns.",
    },
    {
        "Signal": "Forecast plan aggressiveness score",
        "Definition": "Combines aggressive revenue growth, hiring gap, FCF improvement need, and low confidence.",
        "Why it matters": "Ambitious plans can be risky when current operating signals do not support them.",
    },
    {
        "Signal": "Forecast execution risk score",
        "Definition": "Combines plan aggressiveness, cash conversion risk, runway risk, and plan confidence.",
        "Why it matters": "Helps analysts judge whether the five-year plan is credible.",
    },
    {
        "Signal": "Forecast hiring efficiency risk score",
        "Definition": "Measures revenue growth that may be under-supported by employee growth.",
        "Why it matters": "Growth without capacity can indicate execution or documentation risk.",
    },
    {
        "Signal": "Forecast debt service risk score",
        "Definition": "Measures debt reduction ambition under current debt and cash-flow pressure.",
        "Why it matters": "Debt plans may be less credible when cash flow is weak.",
    },
    {
        "Signal": "Annual debt service",
        "Definition": "Estimated first-year principal and interest payments based on requested amount, term, and interest rate.",
        "Why it matters": "Shows whether the new loan is affordable under current cash flow.",
    },
    {
        "Signal": "Debt service coverage ratio",
        "Definition": "Free cash flow divided by estimated annual debt service.",
        "Why it matters": "A DSCR below 1.0 means free cash flow does not cover estimated debt service.",
    },
    {
        "Signal": "Stressed DSCR",
        "Definition": "Debt service coverage recomputed after adding two percentage points to the interest rate.",
        "Why it matters": "Stress testing shows whether the applicant remains resilient if pricing or rates move against them.",
    },
    {
        "Signal": "Debt service stress score",
        "Definition": "Combines DSCR weakness, stressed DSCR weakness, and elevated interest-rate pricing.",
        "Why it matters": "Helps analysts see repayment sensitivity from the loan terms themselves.",
    },
    {
        "Signal": "Cash conversion cycle days",
        "Definition": "Receivables days plus inventory days minus payables days.",
        "Why it matters": "Long cycles can create working-capital strain and financing pressure.",
    },
    {
        "Signal": "Document completeness score",
        "Definition": "Share of expected application documents marked present.",
        "Why it matters": "Completeness helps analysts separate supported cases from cases requiring document follow-up.",
    },
    {
        "Signal": "Document quality risk score",
        "Definition": "Combines missing documents, document edits, late-stage changes, and process deviation.",
        "Why it matters": "Weak documentation quality can reduce auditability and increase review burden.",
    },
    {
        "Signal": "Process integrity risk score",
        "Definition": "Combines workflow deviation, late-stage changes, and document edit behavior.",
        "Why it matters": "Business-process fraud literature emphasizes deviations from normal review flows.",
    },
    {
        "Signal": "Identity verification risk score",
        "Definition": "Combines digital footprint age, bank-account age, location mismatch, and duplicate contact risk.",
        "Why it matters": "Application-channel and KYB signals help identify cases needing deeper verification.",
    },
    {
        "Signal": "Working-capital pressure score",
        "Definition": "Combines current ratio, quick ratio, cash conversion cycle, and receivables pressure.",
        "Why it matters": "Adds liquidity depth beyond free cash flow and runway.",
    },
    {
        "Signal": "Financial statement anomaly score",
        "Definition": "Combines revenue/cash-flow mismatch, receivables pressure, FCF improvement need, and document quality.",
        "Why it matters": "Financial-statement fraud research supports ratio and anomaly checks around reported performance.",
    },
    {
        "Signal": "Related-party network risk score",
        "Definition": "Combines related-party exposure, counterparty concentration, shared identifiers, and suspicious transfer behavior.",
        "Why it matters": "Network-style review can reveal connected-entity or concentrated exposure risk.",
    },
    {
        "Signal": "Narrative consistency risk score",
        "Definition": "Flags contradictions between applicant narrative, document status, and financial signals.",
        "Why it matters": "A credible lending review compares management context with observable evidence.",
    },
]
st.dataframe(pd.DataFrame(derived_dimensions), width="stretch", hide_index=True)

st.subheader("How To Read The Score")
grade_rows = [
    {"Grade": "A", "Application risk score": "< 0.15", "Recommended action": "Approve"},
    {"Grade": "B", "Application risk score": "0.15 to < 0.28", "Recommended action": "Approve"},
    {"Grade": "C", "Application risk score": "0.28 to < 0.42", "Recommended action": "Manual Review"},
    {"Grade": "D", "Application risk score": "0.42 to < 0.58", "Recommended action": "Manual Review"},
    {"Grade": "E", "Application risk score": "0.58 to < 0.74", "Recommended action": "Reject"},
    {"Grade": "F", "Application risk score": ">= 0.74", "Recommended action": "Reject"},
]
st.dataframe(pd.DataFrame(grade_rows), width="stretch", hide_index=True)

st.warning("E and F recommendations should be treated as high-risk decision support requiring human compliance review.")
