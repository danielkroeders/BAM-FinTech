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
