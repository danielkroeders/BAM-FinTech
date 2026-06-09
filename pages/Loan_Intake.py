from datetime import datetime

import streamlit as st

from src.case_workflow import (
    DEMO_SCENARIOS,
    REVIEW_ACTIONS,
    adjusted_prediction,
    case_summary,
    mailto_link,
    similar_applications,
)
from src.explanations import explain_prediction
from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="Loan Intake", layout="wide")
bootstrap_state()
render_sidebar()

applications = st.session_state.seed_data["applications"]
industries = sorted(applications["industry"].unique())
regions = sorted(applications["region"].unique())
company_types = sorted(applications["company_type"].unique())


def _scenario_value(scenario, key, default):
    values = DEMO_SCENARIOS.get(scenario) or {}
    return values.get(key, default)


def _rerun_after_review():
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun:
        rerun()
    st.success("Review saved to the case audit trail.")


def _store_prediction(application, prediction, explanation):
    st.session_state.last_application = application
    st.session_state.last_prediction = prediction
    st.session_state.last_explanation = explanation
    st.session_state.last_review = None
    st.session_state.last_email_link = None
    st.session_state.portfolio_history.append({**application, **prediction, "review_action": "Pending", "final_decision": "Pending Review"})


def _update_latest_history(prediction, review):
    application_id = st.session_state.last_application.get("application_id")
    for row in reversed(st.session_state.portfolio_history):
        if row.get("application_id") == application_id:
            row.update(
                {
                    "fraud_probability": prediction["fraud_probability"],
                    "grade": prediction["grade"],
                    "decision": prediction["decision"],
                    "manual_adjustment": prediction.get("manual_adjustment", False),
                    "review_action": review["action"],
                    "final_decision": review["final_decision"],
                    "supervisor_email": review["supervisor_email"],
                }
            )
            break


def _review_form_body():
    application = st.session_state.last_application
    prediction = st.session_state.last_prediction
    explanation = st.session_state.last_explanation
    current_probability = float(prediction["fraud_probability"])

    with st.form("case_review_form"):
        action = st.selectbox("Analyst action", REVIEW_ACTIONS)
        supervisor_email = st.text_input("Supervisor or review mailbox", value="supervisor@example.com")
        send_email = st.checkbox("Prepare email with case analysis", value=True)
        analyst_note = st.text_area(
            "Analyst note",
            value="Reviewed model score, deterministic flags, and explanation. Pending supervisor sign-off where required.",
        )

        manual_allowed = action in {"Approve", "Reject"}
        manual_approved = False
        manual_probability = current_probability
        if manual_allowed:
            manual_approved = st.checkbox("Supervisor approved manual score adjustment")
            if manual_approved:
                manual_probability = st.slider(
                    "Manual-adjust fraud probability",
                    min_value=0.0,
                    max_value=1.0,
                    value=current_probability,
                    step=0.01,
                )
        else:
            st.caption("Manual score adjustment is only available for approve/reject review outcomes.")

        submitted = st.form_submit_button("Save Review", use_container_width=True)

    if submitted:
        final_prediction = prediction
        if manual_allowed and manual_approved:
            if not supervisor_email:
                st.error("Supervisor email is required for manual score adjustments.")
                return
            final_prediction = adjusted_prediction(prediction, manual_probability)
            explanation = explain_prediction(
                application,
                final_prediction,
                use_llm=st.session_state.use_llm_explanations,
                model=st.session_state.explanation_model,
            )
            st.session_state.last_prediction = final_prediction
            st.session_state.last_explanation = explanation

        review = {
            "review_id": f"REV-{len(st.session_state.review_history) + 1:03d}",
            "application_id": application["application_id"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "supervisor_email": supervisor_email,
            "send_email": send_email,
            "analyst_note": analyst_note,
            "manual_adjustment": bool(final_prediction.get("manual_adjustment", False)),
            "final_probability": final_prediction["fraud_probability"],
            "final_grade": final_prediction["grade"],
            "model_recommendation": final_prediction["decision"],
            "final_decision": action,
        }
        st.session_state.last_review = review
        st.session_state.review_history.append(review)
        _update_latest_history(final_prediction, review)

        st.session_state.last_email_link = None
        if send_email:
            summary = case_summary(application, final_prediction, explanation, review)
            link = mailto_link(
                supervisor_email,
                f"Review required: {application['application_id']} grade {final_prediction['grade']}",
                summary,
            )
            st.session_state.last_email_link = link
        _rerun_after_review()


if hasattr(st, "dialog"):

    @st.dialog("Case Review")
    def _review_dialog():
        _review_form_body()


header_left, header_right = st.columns([3, 1])
with header_left:
    st.title("Loan Intake")
    st.caption("Score a single B2B loan application for fraud risk.")
with header_right:
    scenario = st.selectbox("Demo generator", list(DEMO_SCENARIOS.keys()), key="loan_demo_scenario")

scenario_values = DEMO_SCENARIOS.get(scenario) or {}

with st.form("loan_intake_form"):
    left, middle, right = st.columns(3)
    with left:
        industry_default = _scenario_value(scenario, "industry", "Construction")
        region_default = _scenario_value(scenario, "region", regions[0])
        type_default = _scenario_value(scenario, "company_type", company_types[0])
        industry = st.selectbox("Industry", industries, index=industries.index(industry_default) if industry_default in industries else 0)
        region = st.selectbox("Region", regions, index=regions.index(region_default) if region_default in regions else 0)
        company_type = st.selectbox(
            "Company type",
            company_types,
            index=company_types.index(type_default) if type_default in company_types else 0,
        )
        requested_amount = st.number_input(
            "Requested amount",
            min_value=10000,
            max_value=5000000,
            value=int(_scenario_value(scenario, "requested_amount", 350000)),
            step=10000,
        )
        term_months = st.slider("Term months", min_value=6, max_value=84, value=int(_scenario_value(scenario, "term_months", 36)), step=6)
    with middle:
        annual_revenue = st.number_input(
            "Annual revenue",
            min_value=50000,
            max_value=50000000,
            value=int(_scenario_value(scenario, "annual_revenue", 1800000)),
            step=50000,
        )
        years_in_business = st.number_input(
            "Years in business",
            min_value=0.0,
            max_value=75.0,
            value=float(_scenario_value(scenario, "years_in_business", 4.0)),
            step=0.5,
        )
        existing_debt = st.number_input(
            "Existing debt",
            min_value=0,
            max_value=20000000,
            value=int(_scenario_value(scenario, "existing_debt", 550000)),
            step=25000,
        )
        num_recent_loans = st.slider(
            "Recent loans in the last 12 months",
            min_value=0,
            max_value=12,
            value=int(_scenario_value(scenario, "num_recent_loans", 2)),
        )
        employees = st.number_input("Employees", min_value=1, max_value=10000, value=int(_scenario_value(scenario, "employees", 42)), step=1)
    with right:
        late_payment_ratio = st.slider(
            "Late payment ratio",
            min_value=0.0,
            max_value=1.0,
            value=float(_scenario_value(scenario, "late_payment_ratio", 0.12)),
            step=0.01,
        )
        suspicious_transfer_ratio = st.slider(
            "Suspicious transfer ratio",
            min_value=0.0,
            max_value=1.0,
            value=float(_scenario_value(scenario, "suspicious_transfer_ratio", 0.08)),
            step=0.01,
        )
        collateral_ratio = st.slider(
            "Collateral ratio",
            min_value=0.0,
            max_value=2.0,
            value=float(_scenario_value(scenario, "collateral_ratio", 0.65)),
            step=0.05,
        )
        country_risk_score = st.slider(
            "Country risk score",
            min_value=0.0,
            max_value=1.0,
            value=float(_scenario_value(scenario, "country_risk_score", 0.25)),
            step=0.01,
        )

    submitted = st.form_submit_button("Score Application", use_container_width=True)

if submitted:
    application = {
        "application_id": f"SESSION-{len(st.session_state.portfolio_history) + 1:03d}",
        "company_name": "Session Applicant" if scenario == "Custom application" else scenario,
        "industry": industry,
        "region": region,
        "company_type": company_type,
        "requested_amount": requested_amount,
        "term_months": term_months,
        "annual_revenue": annual_revenue,
        "years_in_business": years_in_business,
        "existing_debt": existing_debt,
        "num_recent_loans": num_recent_loans,
        "late_payment_ratio": late_payment_ratio,
        "suspicious_transfer_ratio": suspicious_transfer_ratio,
        "collateral_ratio": collateral_ratio,
        "employees": employees,
        "country_risk_score": country_risk_score,
    }
    prediction = st.session_state.model_bundle.score_one(application)
    explanation = explain_prediction(
        application,
        prediction,
        use_llm=st.session_state.use_llm_explanations,
        model=st.session_state.explanation_model,
    )
    _store_prediction(application, prediction, explanation)

if st.session_state.last_prediction:
    application = st.session_state.last_application
    prediction = st.session_state.last_prediction
    explanation = st.session_state.last_explanation
    current_review = st.session_state.last_review
    if current_review and current_review.get("application_id") != application["application_id"]:
        current_review = None
    final_decision = current_review["final_decision"] if current_review else "Pending Review"

    st.subheader("Score Output")
    cols = st.columns(4)
    cols[0].metric("Fraud Probability", f"{prediction['fraud_probability']:.1%}")
    cols[1].metric("Risk Grade", prediction["grade"])
    cols[2].metric("Model Recommendation", prediction["decision"])
    cols[3].metric("Final Decision", final_decision)

    if current_review:
        st.success(
            f"Final decision: {current_review['final_decision']} | Saved {current_review['timestamp']} | "
            f"Analyst action: {current_review['action']}"
        )
    else:
        st.info("Final decision: pending analyst review.")

    action_cols = st.columns([1, 1, 2])
    if action_cols[0].button("Open Case Review", use_container_width=True):
        if hasattr(st, "dialog"):
            _review_dialog()
        else:
            st.session_state.show_review_dialog = True
    report = case_summary(application, prediction, explanation, current_review)
    action_cols[1].download_button(
        "Download Summary",
        data=report,
        file_name=f"{application['application_id']}_case_summary.txt",
        mime="text/plain",
        use_container_width=True,
    )
    if st.session_state.last_email_link and current_review:
        action_cols[2].markdown(f"[Open email draft]({st.session_state.last_email_link})")

    if st.session_state.show_review_dialog and not hasattr(st, "dialog"):
        with st.expander("Case Review", expanded=True):
            _review_form_body()

    st.write("Risk factors")
    if prediction["flags"]:
        for flag in prediction["flags"]:
            st.warning(flag)
    else:
        st.success("No elevated deterministic risk flags were triggered.")

    st.write("AI decision rationale")
    st.info(explanation)

    if st.session_state.last_review and st.session_state.last_review.get("application_id") == application["application_id"]:
        review = st.session_state.last_review
        st.write("Latest analyst review")
        st.success(
            f"{review['action']} saved at {review['timestamp']} with final grade {review['final_grade']} "
            f"and final decision {review['final_decision']}."
        )

    st.subheader("Similar Historical Applications")
    st.caption("Nearest synthetic portfolio cases by company profile, requested terms, and risk signals.")
    similar = similar_applications(st.session_state.model_bundle, applications, application)
    st.dataframe(similar, use_container_width=True, hide_index=True)
else:
    st.info("Submit the form to score an application.")
