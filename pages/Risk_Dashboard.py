import pandas as pd
import streamlit as st

from src.modeling import score_portfolio
from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="Risk Dashboard", layout="wide")
bootstrap_state()
render_sidebar()

st.title("Risk Dashboard")
st.caption("Portfolio-level fraud monitoring for lending analysts.")

portfolio = score_portfolio(st.session_state.model_bundle, st.session_state.seed_data["applications"])

left, right = st.columns(2)
with left:
    st.subheader("Grade Distribution")
    grade_counts = portfolio["grade"].value_counts().reindex(list("ABCDEF"), fill_value=0)
    st.bar_chart(grade_counts)
with right:
    st.subheader("Decision Mix")
    st.bar_chart(portfolio["decision"].value_counts())

st.subheader("Highest-Risk Applications")
st.dataframe(
    portfolio.sort_values("fraud_probability", ascending=False)[
        ["application_id", "company_name", "industry", "region", "requested_amount", "fraud_probability", "grade", "decision"]
    ].head(25),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Live Session Decisions")
if st.session_state.portfolio_history:
    history = pd.DataFrame(st.session_state.portfolio_history)
    st.dataframe(
        history[["application_id", "industry", "requested_amount", "fraud_probability", "grade", "decision"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No applications have been scored in this session yet.")
