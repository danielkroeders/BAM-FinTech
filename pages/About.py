import pandas as pd
import streamlit as st

from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="About", layout="wide")
bootstrap_state()
render_sidebar()

st.title("About")
st.caption("Definitions for the loan intake scoring dimensions used by the fraud risk model.")

st.info(
    "This demo uses synthetic data for decision support. Scores help prioritize analyst review and do not establish legal, "
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
        "Why it matters": "Regional market conditions and synthetic country-risk assumptions affect fraud exposure.",
    },
    {
        "Dimension": "Company type",
        "Definition": "The applicant's legal or operating structure, such as LLC, corporation, partnership, or sole proprietorship.",
        "Why it matters": "Entity structure can correlate with documentation depth and verification complexity.",
    },
    {
        "Dimension": "Requested amount",
        "Definition": "The loan principal requested by the applicant.",
        "Why it matters": "Large requests relative to business scale can indicate elevated repayment or fraud risk.",
    },
    {
        "Dimension": "Term months",
        "Definition": "The requested loan duration in months.",
        "Why it matters": "Loan duration shapes exposure time and can interact with cash-flow risk.",
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
        "Definition": "Share of transfers flagged as unusual in the synthetic transaction profile.",
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
        "Definition": "A synthetic score from 0 to 1 representing jurisdictional or country-level risk.",
        "Why it matters": "Higher values indicate greater contextual risk in the demo's synthetic assumptions.",
    },
]

st.subheader("Scoring Dimensions")
st.dataframe(pd.DataFrame(dimensions), use_container_width=True, hide_index=True)

st.subheader("How To Read The Score")
grade_rows = [
    {"Grade": "A", "Fraud probability": "< 0.15", "Recommended action": "Approve"},
    {"Grade": "B", "Fraud probability": "0.15 to < 0.28", "Recommended action": "Approve"},
    {"Grade": "C", "Fraud probability": "0.28 to < 0.42", "Recommended action": "Manual Review"},
    {"Grade": "D", "Fraud probability": "0.42 to < 0.58", "Recommended action": "Manual Review"},
    {"Grade": "E", "Fraud probability": "0.58 to < 0.74", "Recommended action": "Reject"},
    {"Grade": "F", "Fraud probability": ">= 0.74", "Recommended action": "Reject"},
]
st.dataframe(pd.DataFrame(grade_rows), use_container_width=True, hide_index=True)

st.warning("E and F recommendations should be treated as high-risk decision support requiring human compliance review.")
