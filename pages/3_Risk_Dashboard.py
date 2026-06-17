import altair as alt
import pandas as pd
import streamlit as st

from src.utils.formatting import format_currency, format_integer, format_percent
from src.core.modeling import score_portfolio
from src.core.runtime import bootstrap_state
from src.utils.table_views import application_table
from src.ui.components import open_application_in_workspace, render_sidebar


st.set_page_config(page_title="Risk Dashboard", layout="wide")
bootstrap_state()
render_sidebar()

st.markdown(
    """
    <style>
    .risk-kicker {
        color: var(--cr-teal);
        font-size: 0.78rem;
        font-weight: 850;
        line-height: 1;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
    }
    .risk-header-copy {
        color: var(--cr-muted);
        font-size: 0.95rem;
        line-height: 1.45;
        margin-bottom: 1rem;
        max-width: 58rem;
    }
    .risk-panel-title {
        color: var(--cr-text);
        font-size: 1.02rem;
        font-weight: 850;
        line-height: 1.2;
        margin-bottom: 0.2rem;
    }
    .risk-panel-copy {
        color: var(--cr-muted);
        font-size: 0.84rem;
        line-height: 1.35;
        margin-bottom: 0.7rem;
    }
    .risk-filter-note {
        color: var(--cr-muted);
        font-size: 0.82rem;
        line-height: 1.4;
        padding-top: 1.75rem;
    }
    div[data-testid="stTabs"] button p {
        font-weight: 750;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

selected_model_key = st.session_state.get("selected_ml_model", st.session_state.model_bundle.default_model_key)
portfolio = score_portfolio(
    st.session_state.model_bundle,
    st.session_state.seed_data["applications"],
    model_key=selected_model_key,
)


def _bordered_container():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def _display_table(frame, columns):
    return application_table(frame, columns)


def _chart_style(chart):
    dark = bool(st.session_state.get("dark_mode_preference", st.session_state.get("dark_mode", False)))
    text = "#cbd5e1" if dark else "#475569"
    grid = "rgba(148, 163, 184, 0.24)" if dark else "rgba(148, 163, 184, 0.28)"
    return (
        chart.configure_axis(
            domain=False,
            gridColor=grid,
            labelColor=text,
            labelFontSize=12,
            titleColor=text,
            titleFontSize=12,
            tickColor=grid,
        )
        .configure_view(strokeOpacity=0)
        .configure_legend(labelColor=text, titleColor=text)
    )


def _grade_chart(frame):
    grade_palette = ["#1e3a8a", "#0f766e", "#64748b", "#b45309", "#9f1239", "#7f1d1d"]
    chart_data = (
        frame["grade"]
        .value_counts()
        .reindex(list("ABCDEF"), fill_value=0)
        .rename_axis("Grade")
        .reset_index(name="Applications")
    )
    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, opacity=0.88)
        .encode(
            x=alt.X("Grade:N", sort=list("ABCDEF"), axis=alt.Axis(title=None)),
            y=alt.Y("Applications:Q", axis=alt.Axis(title=None, minExtent=30)),
            color=alt.Color(
                "Grade:N",
                scale=alt.Scale(
                    domain=list("ABCDEF"),
                    range=grade_palette,
                ),
                legend=None,
            ),
            tooltip=["Grade:N", "Applications:Q"],
        )
        .properties(height=260)
    )
    return _chart_style(chart)


def _decision_chart(frame):
    decision_palette = ["#0f766e", "#b45309", "#9f1239"]
    decision_order = ["Approve", "Manual Review", "Reject"]
    chart_data = (
        frame["decision"]
        .value_counts()
        .reindex(decision_order, fill_value=0)
        .rename_axis("Decision")
        .reset_index(name="Applications")
    )
    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, opacity=0.88)
        .encode(
            y=alt.Y("Decision:N", sort=decision_order, axis=alt.Axis(title=None)),
            x=alt.X("Applications:Q", axis=alt.Axis(title=None, minExtent=30)),
            color=alt.Color(
                "Decision:N",
                scale=alt.Scale(domain=decision_order, range=decision_palette),
                legend=None,
            ),
            tooltip=["Decision:N", "Applications:Q"],
        )
        .properties(height=260)
    )
    return _chart_style(chart)


def _activity_table(history):
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
    return _display_table(history, available_columns)


st.markdown('<div class="risk-kicker">Portfolio Control</div>', unsafe_allow_html=True)
st.title("Risk Dashboard")
st.markdown(
    '<div class="risk-header-copy">A balanced portfolio view for triage, compliance queues, '
    "and live analyst review activity.</div>",
    unsafe_allow_html=True,
)

with _bordered_container():
    st.markdown('<div class="risk-panel-title">Portfolio Filters</div>', unsafe_allow_html=True)
    filter_top = st.columns(4)
    selected_grades = filter_top[0].multiselect("Grades", list("ABCDEF"), default=list("ABCDEF"))
    selected_decisions = filter_top[1].multiselect(
        "Decisions",
        sorted(portfolio["decision"].unique()),
        default=sorted(portfolio["decision"].unique()),
    )
    selected_industries = filter_top[2].multiselect(
        "Industries",
        sorted(portfolio["industry"].unique()),
        default=sorted(portfolio["industry"].unique()),
    )
    selected_regions = filter_top[3].multiselect(
        "Regions",
        sorted(portfolio["region"].unique()),
        default=sorted(portfolio["region"].unique()),
    )
    filter_bottom = st.columns([2.4, 1])
    probability_range = filter_bottom[0].slider("Application risk score", 0.0, 1.0, (0.0, 1.0), step=0.01)
    filter_bottom[1].markdown(
        f'<div class="risk-filter-note">Showing scores from {format_percent(probability_range[0])} '
        f"to {format_percent(probability_range[1])}.</div>",
        unsafe_allow_html=True,
    )

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
review_load = (len(high_risk) + len(manual_review)) / len(filtered) if len(filtered) else 0
average_risk = filtered["fraud_probability"].mean() if len(filtered) else 0

metric_cols = st.columns(4)
metric_cols[0].metric("Filtered Applications", format_integer(len(filtered)))
metric_cols[1].metric("Filtered Exposure", format_currency(total_exposure))
metric_cols[2].metric("Average Risk Score", format_percent(average_risk))
metric_cols[3].metric("Review Load", format_percent(review_load))

chart_cols = st.columns(2)
with chart_cols[0]:
    with _bordered_container():
        st.markdown('<div class="risk-panel-title">Grade Distribution</div>', unsafe_allow_html=True)
        st.markdown('<div class="risk-panel-copy">A-F portfolio risk composition across the active filter set.</div>', unsafe_allow_html=True)
        st.altair_chart(_grade_chart(filtered), width="stretch")
with chart_cols[1]:
    with _bordered_container():
        st.markdown('<div class="risk-panel-title">Decision Mix</div>', unsafe_allow_html=True)
        st.markdown('<div class="risk-panel-copy">Approve, manual review, and reject recommendations in balance.</div>', unsafe_allow_html=True)
        st.altair_chart(_decision_chart(filtered), width="stretch")

if filtered.empty:
    st.info("No applications match the selected filters.")
else:
    action_cols = st.columns([2, 1], vertical_alignment="bottom")
    open_options = [
        f"{row.application_id} - {row.company_name} | Grade {row.grade} | {format_percent(row.fraud_probability)}"
        for row in filtered.sort_values("fraud_probability", ascending=False).head(50).itertuples()
    ]
    selected_open_label = action_cols[0].selectbox("Open filtered application", open_options)
    selected_open_id = selected_open_label.split(" - ", 1)[0]
    selected_open = filtered[filtered["application_id"] == selected_open_id].iloc[0].to_dict()
    if action_cols[1].button("Open In Workspace", width="stretch"):
        open_application_in_workspace(selected_open, "Risk Dashboard")

review_tab, highest_tab, activity_tab = st.tabs(["Review Queues", "Highest Risk", "Session Activity"])

table_columns = [
    "application_id",
    "company_name",
    "industry",
    "region",
    "requested_amount",
    "fraud_probability",
    "grade",
    "decision",
]

with review_tab:
    queue_cols = st.columns(2)
    with queue_cols[0]:
        st.subheader("Manual Review")
        st.caption("C-D cases for analyst review and evidence follow-up.")
        st.dataframe(
            _display_table(manual_review.sort_values("fraud_probability", ascending=False).head(15), table_columns),
            width="stretch",
            hide_index=True,
        )
    with queue_cols[1]:
        st.subheader("Compliance Review")
        st.caption("E-F outcomes require human compliance review before final action.")
        st.dataframe(
            _display_table(high_risk.sort_values("fraud_probability", ascending=False).head(15), table_columns),
            width="stretch",
            hide_index=True,
        )

with highest_tab:
    st.subheader("Highest-Risk Applications")
    st.caption("Top visible applications by application risk score.")
    st.dataframe(
        _display_table(filtered.sort_values("fraud_probability", ascending=False).head(25), table_columns),
        width="stretch",
        hide_index=True,
    )

with activity_tab:
    activity_cols = st.columns(2)
    with activity_cols[0]:
        st.subheader("Live Session Decisions")
        if st.session_state.portfolio_history:
            history = pd.DataFrame(st.session_state.portfolio_history)
            st.dataframe(_activity_table(history), width="stretch", hide_index=True)
        else:
            st.info("No applications have been scored in this session yet.")
    with activity_cols[1]:
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
