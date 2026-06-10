# Claude Instructions: Build the BAM-FinTech App

You are being asked to create a complete Streamlit application for a B2B loan fraud intelligence demo. Build the app from scratch in this repository so it matches the product described below.

## Product Goal

Create a multi-page app called **B2B Loan Fraud Intelligence** for business lenders. The app should score B2B loan applications for fraud risk, assign an A-F grade, recommend an operational action, and explain the decision in plain language.

This is a synthetic demo and decision-support tool, not a production underwriting or legal decision system. High-risk outcomes must be framed as requiring human compliance review.

## Required User Experience

The app must be a real working Streamlit product, not a landing page.

Create these pages:

- `Home.py`: overview page with portfolio size, known fraud count, model ROC-AUC, model recall, and a short workflow summary.
- `pages/Loan_Intake.py`: form for scoring a single B2B loan application.
- `pages/Risk_Dashboard.py`: portfolio-level dashboard with grade distribution, decision mix, highest-risk applications, and live session decisions.
- `pages/Model_Insights.py`: model metrics, confusion matrix, top feature importances, and A-F grading thresholds.
- `pages/LLM_Chat.py`: AI explainability page for the latest scored loan request.

The correct launch command must be:

```bash
streamlit run Home.py
```

Do not use `app.py` as the entrypoint.

## Required Project Structure

Create and use this structure:

```text
Home.py
pages/
  Loan_Intake.py
  Risk_Dashboard.py
  Model_Insights.py
  LLM_Chat.py
src/
  __init__.py
  data_pipeline.py
  modeling.py
  explanations.py
  runtime.py
  ui.py
data/
  seed/
    applications.csv
    company_profiles.csv
    transactions.csv
    decisions.csv
requirements.txt
README.md
```

## Dependencies

Use Python with these runtime dependencies:

```text
streamlit
pandas
numpy
scikit-learn
openai
```

Python 3.10+ is recommended.

## Data Requirements

Generate synthetic seed data automatically when needed. The app should work on first run without the user manually creating CSV files.

`src/data_pipeline.py` must define:

- `SEED_DIR`
- `NUMERIC_COLUMNS`
- `CATEGORICAL_COLUMNS`
- `TARGET_COLUMN`
- `generate_seed_data()`
- `load_seed_data()`
- `ensure_seed_data()`

The app must create/load these CSVs under `data/seed/`:

- `applications.csv`
- `company_profiles.csv`
- `transactions.csv`
- `decisions.csv`

Use at least 400 seed application rows. A default around 1,200 rows is good.

Required numeric model features:

- `requested_amount`
- `term_months`
- `annual_revenue`
- `years_in_business`
- `existing_debt`
- `num_recent_loans`
- `late_payment_ratio`
- `suspicious_transfer_ratio`
- `collateral_ratio`
- `employees`
- `country_risk_score`

Required categorical model features:

- `industry`
- `region`
- `company_type`

Required target:

- `is_fraud`

Synthetic risk should be realistic for B2B lending. Higher risk should be influenced by high debt pressure, high requested amount relative to revenue, many recent loans, suspicious transfer ratio, late payments, country risk, low collateral, and short operating history.

## Modeling Requirements

`src/modeling.py` must train a supervised fraud model using scikit-learn.

Use:

- `Pipeline`
- `ColumnTransformer`
- numeric imputation with median
- numeric scaling with `StandardScaler`
- categorical imputation with most frequent value
- categorical encoding with `OneHotEncoder(handle_unknown="ignore")`
- `RandomForestClassifier`

Create a `ModelBundle` dataclass containing:

- trained pipeline
- metrics dictionary
- feature importance DataFrame
- threshold map

Compute and expose:

- accuracy
- precision
- recall
- F1
- ROC-AUC
- confusion matrix values: `tn`, `fp`, `fn`, `tp`

Implement:

- `train_model(applications)`
- `grade_from_probability(probability)`
- `decision_from_grade(grade)`
- `rule_flags(application)`
- `score_application(model_bundle, application)`
- `score_portfolio(model_bundle, applications)`

## A-F Risk Grade Mapping

Use this exact mapping:

```text
A: fraud probability < 0.15
B: fraud probability < 0.28
C: fraud probability < 0.42
D: fraud probability < 0.58
E: fraud probability < 0.74
F: fraud probability >= 0.74
```

Use this exact decision mapping:

```text
A or B: Approve
C or D: Manual Review
E or F: Reject
```

## Loan Intake Page

The single-loan form must collect:

- industry
- region
- company type
- requested amount
- term months
- annual revenue
- years in business
- existing debt
- recent loans in the last 12 months
- late payment ratio
- suspicious transfer ratio
- collateral ratio
- employees
- country risk score

On submit, display:

- fraud probability
- A-F grade
- recommended action
- risk factors
- AI decision rationale

Store the latest scored application, prediction, and explanation in Streamlit session state. Append each submitted score to a session-level history list so the dashboard can display live session decisions.

## Explanation Requirements

`src/explanations.py` must provide deterministic explanations and optional LLM explanations.

The app must work without an API key. If no OpenAI key is present, or if the LLM call fails, use deterministic fallback.

Read the API key from:

- Streamlit secrets: `OPENAI_API_KEY`
- environment variable: `OPENAI_API_KEY`

The deterministic explanation must:

- state decision, grade, and fraud probability
- mention applicant context, such as company type, industry, and requested amount
- list top risk drivers
- state that this is decision support and high-risk cases need human compliance review

The optional LLM explanation must:

- use the model output and flags as source material
- explain the result in concise plain language
- avoid claiming legal certainty
- avoid inventing facts
- fail back to deterministic explanation

## Runtime and Session State

`src/runtime.py` must provide cached bootstrap helpers:

- `get_seed_data()` with `st.cache_data`
- `get_model_bundle()` with `st.cache_resource`
- `bootstrap_state()`

`bootstrap_state()` must initialize:

- `seed_data`
- `model_bundle`
- `portfolio_history`
- `last_application`
- `last_prediction`

Each page must call `bootstrap_state()` before using shared data or model objects.

## Shared UI

`src/ui.py` must provide a shared sidebar with:

- toggle for LLM explanations
- explanation model selectbox
- API key detected indicator

Keep the UI professional, compact, and operational. It should feel like a risk tool for lending analysts, not a marketing site.

## Acceptance Checks

Before finishing, verify:

```bash
python3 -m compileall src Home.py pages
streamlit run Home.py
```

Functional acceptance:

- Home page loads from `Home.py`.
- Seed data is created or loaded automatically.
- Model trains and metrics display.
- Loan Intake scores a sample application.
- Score output includes fraud probability, grade, decision, flags, and explanation.
- App works without `OPENAI_API_KEY`.
- Risk Dashboard shows grade distribution, decision mix, highest-risk applications, and session history after scoring.
- Model Insights shows metrics, confusion matrix, feature importances, and thresholds.
- AI Explainability handles the case where no application has been scored yet.

## Documentation

Create or update `README.md` with:

- product summary
- setup instructions
- correct launch command: `streamlit run Home.py`
- optional OpenAI key behavior
- page overview
- A-F risk grade mapping

Never include secrets or real customer data.

## Investor Demo Enhancements

Keep these MVP demo workflows available and maintained:

- `pages/Loan_Intake.py` must include a top-right demo generator with preset B2B borrower scenarios for reliable investor demos.
- After scoring an application, Loan Intake must show similar historical synthetic applications with their fraud probability, grade, decision, and historical fraud outcome.
- Loan Intake must provide a case review pop-up or fallback review panel where analysts can choose an action, add notes, prepare an email-ready case analysis, and save the review to session audit history.
- Manual score adjustment is only allowed for approve/reject review outcomes and must require explicit supervisor approval plus a supervisor or review mailbox.
- Any manual adjustment must store the final probability, grade, decision, manual-adjustment flag, supervisor email, and analyst note in the session audit trail.
- Loan Intake must offer a downloadable case summary for the latest scored application.
- `pages/Risk_Dashboard.py` must include portfolio filters, a manual review queue for C-D grades, a compliance review queue for E-F grades, live session decisions, and analyst review audit history.
- Deterministic explanations must remain structured for analyst use, including decision, top risk drivers, mitigating factors, recommended analyst action, and compliance note.
- `README.md` must include a short demo script suitable for grading and investor presentation.

## Final Decision Review Behavior

Append and preserve these Loan Intake review rules:

- After a case review is saved, the selected analyst action must be reflected on the page as the case `Final Decision`.
- The score output should keep the model result visible as `Model Recommendation` while showing the analyst outcome separately as `Final Decision`.
- Do not show `Manual Adjustment` as the primary score output metric; manual adjustment should remain an audit detail only.
- Saving a case review from the pop-up must trigger a page refresh or rerun so the updated final decision is immediately visible.
- Live session decision tables should include `final_decision` so reviewed cases clearly show the analyst outcome.
- Case summaries should include both the final decision and the original model recommendation.

## First-Time User Launcher

Append and preserve these launcher rules:

- The repository should include a double-clickable Windows launcher named `Run_App.bat`.
- The launcher must run from the project root, create a local `.venv` when needed, install dependencies from `requirements.txt`, and start the app with `streamlit run Home.py`.
- The launcher must not require users to run terminal commands manually for first-time setup.
- The launcher should provide clear error messages when Python 3.10+ is missing or dependency installation fails.
- Generated local environments such as `.venv/` must remain ignored by git.
- `README.md` should mention the double-click launcher before the manual Streamlit command.

## Demo Runbook Documentation

Append and preserve these demo documentation rules:

- The repository should include a standalone `DEMO.md` file for investor demos, grading presentations, and live walkthroughs.
- `DEMO.md` should include first-time startup steps, the core product message, a five-minute demo flow, a two-minute backup flow, suggested presenter language, safety notes, and troubleshooting.
- The demo guide should emphasize that all data is synthetic and that high-risk outcomes require human compliance review.
- `README.md` should link to `DEMO.md` from the demo script section so presenters can find the full runbook quickly.

## Research-Backed Fraud Signals

Append and preserve these signal-design rules:

- Local fraud research PDFs may be summarized in `docs/fraud_research.md`; do not paste full paper text into Codex instructions.
- `src/data_pipeline.py` should maintain `add_derived_features()` for research-backed synthetic fraud measures derived from seed and intake fields.
- Keep derived features automatic and hidden from the Loan Intake form unless there is a strong demo reason to expose them.
- Maintain derived pressure, anomaly, velocity, distress, collateral, scale-mismatch, and governance signals in the model feature set.
- `src/modeling.py` must derive these features before training, portfolio scoring, and single-application scoring.
- Similar-case matching and SHAP explanations should use the derived feature set so comparable cases and explanations reflect the same model inputs.
- Model Insights should include imbalance-aware metrics such as balanced accuracy, average precision, Matthews correlation coefficient, and precision at the top review queue, not accuracy alone.
- `README.md` should link to `docs/fraud_research.md` so graders can inspect the research grounding.

## Cash-Flow Risk Signals

Append and preserve these cash-flow signal rules:

- Synthetic seed data should include `data/seed/cash_flows.csv` in addition to the original seed tables.
- Cash-flow analysis must include free cash flow, monthly burn rate, cash flow as a percentage of revenue, and expected runway at application date.
- `src/data_pipeline.py` should generate these cash-flow fields automatically and include them in model features.
- Loan Intake should capture cash-flow inputs compactly and compute cash flow / revenue automatically from free cash flow and annual revenue.
- Derived cash-flow risk measures should include cash-flow pressure, runway risk, and cash conversion risk.
- Rule flags, SHAP explanations, similar-case matching, About, Model Insights, and case summaries should reflect cash-flow signals where relevant.
- Keep cash-flow fields synthetic and never use real company financials.

## Banker-First Loan Intake

Append and preserve these Loan Intake usability rules:

- Loan Intake should feel like a banker reviewing an incoming application, not a model-lab control panel.
- Visible intake fields should be grouped around company profile, loan request, and financial snapshot.
- Advanced synthetic controls such as late-payment ratio, suspicious-transfer ratio, and country risk should live under an `Advanced Demo Signals` expander.
- Derived ratios and risk scores must be calculated by the model pipeline, not manually entered by the banker.
- After scoring, show a `Calculated Risk Signals` section with the model-calculated ratios and scores used to support the decision.
- Keep the demo generator because it helps presentations, but it should populate banker-facing inputs rather than exposing all model internals up front.

## Five-Year Forecast And Executive Context

Append and preserve these forward-looking intake rules:

- Synthetic seed data should include `data/seed/forecasts.csv` with annual five-year forecast rows for each application.
- The five-year forecast should include projected annual revenue, projected employees, projected free cash flow, and projected debt.
- Loan Intake should capture forecast assumptions such as expected revenue growth, employee growth, year-five FCF margin target, planned debt reduction, and plan confidence.
- The model should grade forecast realism through derived plan-aggressiveness, execution-risk, hiring-efficiency-risk, and debt-service-risk signals.
- After scoring, Loan Intake should show a generated five-year forecast table and include forecast-derived risk signals in `Calculated Risk Signals`.
- Loan Intake should include CEO, CFO, and COO context text areas. Demo scenarios may prefill them; the custom template should leave them empty.
- Executive context should supplement the case summary and presentation narrative, but raw text should not be used as a model feature unless explicitly designed and documented later.

## Applicant Narrative Context

Append and preserve these applicant-context rules:

- Loan Intake should include a separate applicant narrative section for loan purpose, current business context, and future business context.
- This applicant narrative is distinct from the CEO, CFO, and COO executive context and does not need to duplicate the five-year forecast text.
- Demo scenarios may prefill applicant narrative fields; the custom template should leave them empty.
- Applicant narrative should appear in the post-score review output and case summary.
- The app may show a simple narrative completeness indicator, but raw applicant narrative text should not be used directly as a model feature unless explicitly designed and documented later.

## European Number Formatting

Append and preserve these display-formatting rules:

- User-facing currency should use the euro sign, for example `€ 1.234,56`.
- User-facing numbers should use `.` as the thousands separator and `,` as the decimal separator.
- Keep underlying dataframe and model values numeric; apply European formatting only to UI display strings, reports, summaries, and exported text.
- Prefer the shared helpers in `src/formatting.py` for currency, percentages, scores, integers, and month values.
- Loan Intake currency input fields should display formatted euro values such as `€1.000.000,00` while parsing values back into numeric model inputs.
