import pandas as pd
import streamlit as st

from src.formatting import format_currency, format_integer, format_percent
from src.modeling import score_portfolio
from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="Risk Dashboard", layout="wide")
bootstrap_state()
render_sidebar()

st.title("Risk Dashboard")
st.caption("Portfolio-level SME credit risk monitoring for lending analysts.")

portfolio = score_portfolio(st.session_state.model_bundle, st.session_state.seed_data["applications"])


def _display_table(frame, columns):
    display = frame[columns].copy()
    if "requested_amount" in display:
        display["requested_amount"] = display["requested_amount"].apply(format_currency)
    if "fraud_probability" in display:
        display["fraud_probability"] = display["fraud_probability"].apply(format_percent)
        display = display.rename(columns={"fraud_probability": "Application risk score"})
    return display

with st.expander("Portfolio Filters", expanded=True):
    filter_cols = st.columns(5)
    selected_grades = filter_cols[0].multiselect("Grades", list("ABCDEF"), default=list("ABCDEF"))
    selected_decisions = filter_cols[1].multiselect(
        "Decisions",
        sorted(portfolio["decision"].unique()),
        default=sorted(portfolio["decision"].unique()),
    )
    selected_industries = filter_cols[2].multiselect(
        "Industries",
        sorted(portfolio["industry"].unique()),
        default=sorted(portfolio["industry"].unique()),
    )
    selected_regions = filter_cols[3].multiselect(
        "Regions",
        sorted(portfolio["region"].unique()),
        default=sorted(portfolio["region"].unique()),
    )
    probability_range = filter_cols[4].slider("Application risk score", 0.0, 1.0, (0.0, 1.0), step=0.01)

filtered = portfolio[
    portfolio["grade"].isin(selected_grades)
    & portfolio["decision"].isin(selected_decisions)
    & portfolio["industry"].isin(selected_industries)
    & portfolio["region"].isin(selected_regions)
    & portfolio["fraud_probability"].between(probability_range[0], probability_range[1])
].copy()

total_exposure = filtered["requested_amount"].sum()
high_risk = filtered[filtered["grade"].isin(["E", "F"])]
manual_review = filtered[filtered["grade"].isin(["C", "D"])]

metric_cols = st.columns(4)
metric_cols[0].metric("Filtered Applications", format_integer(len(filtered)))
metric_cols[1].metric("Filtered Exposure", format_currency(total_exposure))
metric_cols[2].metric("Manual Review Queue", format_integer(len(manual_review)))
metric_cols[3].metric("Compliance Queue", format_integer(len(high_risk)))

left, right = st.columns(2)
with left:
    st.subheader("Grade Distribution")
    grade_counts = filtered["grade"].value_counts().reindex(list("ABCDEF"), fill_value=0)
    st.bar_chart(grade_counts)
with right:
    st.subheader("Decision Mix")
    st.bar_chart(filtered["decision"].value_counts())

st.subheader("Compliance Review Queue")
st.caption("High-risk E/F outcomes require human compliance review before final action.")
st.dataframe(
    _display_table(
        high_risk.sort_values("fraud_probability", ascending=False).head(20),
        [
            "application_id",
            "company_name",
            "industry",
            "region",
            "requested_amount",
            "fraud_probability",
            "grade",
            "decision",
        ],
    ),
    width="stretch",
    hide_index=True,
)

st.subheader("Manual Review Queue")
st.dataframe(
    _display_table(
        manual_review.sort_values("fraud_probability", ascending=False).head(20),
        [
            "application_id",
            "company_name",
            "industry",
            "region",
            "requested_amount",
            "fraud_probability",
            "grade",
            "decision",
        ],
    ),
    width="stretch",
    hide_index=True,
)

st.subheader("Highest-Risk Applications")
st.dataframe(
    _display_table(
        filtered.sort_values("fraud_probability", ascending=False).head(25),
        ["application_id", "company_name", "industry", "region", "requested_amount", "fraud_probability", "grade", "decision"],
    ),
    width="stretch",
    hide_index=True,
)

st.subheader("Live Session Decisions")
if st.session_state.portfolio_history:
    history = pd.DataFrame(st.session_state.portfolio_history)
    visible_columns = [
        "application_id",
        "industry",
        "requested_amount",
        "fraud_probability",
        "grade",
        "decision",
        "review_action",
        "final_decision",
    ]
    available_columns = [column for column in visible_columns if column in history.columns]
    display_history = history[available_columns].copy()
    if "requested_amount" in display_history:
        display_history["requested_amount"] = display_history["requested_amount"].apply(format_currency)
    if "fraud_probability" in display_history:
        display_history["fraud_probability"] = display_history["fraud_probability"].apply(format_percent)
        display_history = display_history.rename(columns={"fraud_probability": "Application risk score"})
    st.dataframe(display_history, width="stretch", hide_index=True)
else:
    st.info("No applications have been scored in this session yet.")

st.subheader("Analyst Review Audit Trail")
if st.session_state.review_history:
    reviews = pd.DataFrame(st.session_state.review_history)
    display_reviews = reviews.copy()
    if "final_probability" in display_reviews:
        display_reviews["final_probability"] = display_reviews["final_probability"].apply(format_percent)
        display_reviews = display_reviews.rename(columns={"final_probability": "Final application risk score"})
    st.dataframe(display_reviews, width="stretch", hide_index=True)
else:
    st.info("No analyst reviews have been saved in this session yet.")
