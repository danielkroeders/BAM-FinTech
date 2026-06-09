import streamlit as st

from src.explanations import explain_prediction
from src.runtime import bootstrap_state
from src.ui import render_sidebar


st.set_page_config(page_title="Loan Intake", layout="wide")
bootstrap_state()
render_sidebar()

st.title("Loan Intake")
st.caption("Score a single B2B loan application for fraud risk.")

applications = st.session_state.seed_data["applications"]
industries = sorted(applications["industry"].unique())
regions = sorted(applications["region"].unique())
company_types = sorted(applications["company_type"].unique())

with st.form("loan_intake_form"):
    left, middle, right = st.columns(3)
    with left:
        industry = st.selectbox("Industry", industries, index=industries.index("Construction") if "Construction" in industries else 0)
        region = st.selectbox("Region", regions)
        company_type = st.selectbox("Company type", company_types)
        requested_amount = st.number_input("Requested amount", min_value=10000, max_value=5000000, value=350000, step=10000)
        term_months = st.slider("Term months", min_value=6, max_value=84, value=36, step=6)
    with middle:
        annual_revenue = st.number_input("Annual revenue", min_value=50000, max_value=50000000, value=1800000, step=50000)
        years_in_business = st.number_input("Years in business", min_value=0.0, max_value=75.0, value=4.0, step=0.5)
        existing_debt = st.number_input("Existing debt", min_value=0, max_value=20000000, value=550000, step=25000)
        num_recent_loans = st.slider("Recent loans in the last 12 months", min_value=0, max_value=12, value=2)
        employees = st.number_input("Employees", min_value=1, max_value=10000, value=42, step=1)
    with right:
        late_payment_ratio = st.slider("Late payment ratio", min_value=0.0, max_value=1.0, value=0.12, step=0.01)
        suspicious_transfer_ratio = st.slider("Suspicious transfer ratio", min_value=0.0, max_value=1.0, value=0.08, step=0.01)
        collateral_ratio = st.slider("Collateral ratio", min_value=0.0, max_value=2.0, value=0.65, step=0.05)
        country_risk_score = st.slider("Country risk score", min_value=0.0, max_value=1.0, value=0.25, step=0.01)

    submitted = st.form_submit_button("Score Application", use_container_width=True)

if submitted:
    application = {
        "application_id": f"SESSION-{len(st.session_state.portfolio_history) + 1:03d}",
        "company_name": "Session Applicant",
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

    st.session_state.last_application = application
    st.session_state.last_prediction = prediction
    st.session_state.last_explanation = explanation
    st.session_state.portfolio_history.append({**application, **prediction})

if st.session_state.last_prediction:
    prediction = st.session_state.last_prediction
    st.subheader("Score Output")
    cols = st.columns(3)
    cols[0].metric("Fraud Probability", f"{prediction['fraud_probability']:.1%}")
    cols[1].metric("Risk Grade", prediction["grade"])
    cols[2].metric("Recommended Action", prediction["decision"])

    st.write("Risk factors")
    if prediction["flags"]:
        for flag in prediction["flags"]:
            st.warning(flag)
    else:
        st.success("No elevated deterministic risk flags were triggered.")

    st.write("AI decision rationale")
    st.info(st.session_state.last_explanation)
else:
    st.info("Submit the form to score an application.")
