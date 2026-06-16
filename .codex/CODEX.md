# Codex Reconstruction Brief: CredRisk.AI Underwriter Workbench

This file is the canonical handoff for rebuilding and maintaining this repository in a fresh Codex session with no prior conversation context.

## Exact Reproduction Rule

There are two valid reconstruction modes:

1. Exact byte-for-byte repository restore.
   - Preferred path: clone the GitHub remote and check out the intended commit.
   - Remote: `https://github.com/danielkroeders/BAM-FinTech.git`
   - Last upstream commit inspected before this handoff edit: `7b27b03c3c17fc001ed6dee1a18d71912701eb8a`
   - After `codex.md` is committed, use the commit that contains this file instead of the inspected hash above.
   - Commands:

```bash
git clone https://github.com/danielkroeders/BAM-FinTech.git
cd BAM-FinTech
git checkout <commit-that-contains-codex.md>
```

2. Functional rebuild from this document alone.
   - Use this file as the full product and engineering specification.
   - Recreate the source tree, install dependencies, generate deterministic seed CSVs, and run the app from `Home.py`.
   - Binary assets such as PDFs, PPTX files, JPEGs, and PNGs cannot be inferred byte-for-byte from prose. If no Git remote or archive is available, recreate placeholders only where the app requires a file path, then document the limitation.

For a future Codex to reproduce the current repository exactly from only one Markdown file, append a base64 zip archive of the repository to this file and include extraction instructions. Without a cloneable remote or embedded archive, exact binary reproduction is impossible.

## Repository Identity

Project name: `CredRisk.AI Underwriter Workbench`

App type: Streamlit application for SME lending analysts.

Primary user: Ms. Alice Cooper, a credit analyst working a daily portfolio queue.

Product stance: This is decision support, not a production underwriting, legal, or compliance decision system. ML and AI outputs never become the final decision by themselves.

Launch command:

```bash
streamlit run Home.py
```

Do not create or use `app.py`.

## Dependency Contract

Python 3.10+ is recommended.

`requirements.txt` must contain:

```text
streamlit
pandas
numpy
scikit-learn
openai
shap
pypdf
```

The Windows launcher `Run_App.bat` must:

- create `.venv` if missing,
- install `requirements.txt`,
- start `streamlit run Home.py`,
- never call `app.py`.

## File Manifest

Keep this repository shape:

```text
.
|-- .codex/
|   |-- CODEX.md
|-- .streamlit/
|   |-- config.toml
|-- codex.md
|-- README.md
|-- DEMO.md
|-- requirements.txt
|-- Run_App.bat
|-- Home.py
|-- BP.pdf
|-- FinTech Assignment 2-1.pdf
|-- as2 grading.jpeg
|-- as2 overview.jpeg
|-- as2 req.jpeg
|-- docs/
|   |-- CredRiskAI_Pitchdeck.html
|   |-- CredRiskAI_Pitchdeck.pdf
|   |-- CredRiskAI_Pitchdeck.pptx
|   |-- CredRiskAI_Pitchdeck_Speaker_Notes.md
|-- data/
|   |-- assets/
|   |   |-- login-risk-hero.png
|   |-- docs/
|   |   |-- fraud_research.md
|   |   |-- research PDF files used as supporting material
|   |-- seed/
|   |   |-- applications.csv
|   |   |-- cash_flows.csv
|   |   |-- company_profiles.csv
|   |   |-- decisions.csv
|   |   |-- forecasts.csv
|   |   |-- transactions.csv
|   |-- seeds/
|       |-- mirror of the seed CSVs for compatibility
|-- pages/
|   |-- 1_Personal_Workspace.py
|   |-- 2_Operations_Desk.py
|   |-- 3_Risk_Dashboard.py
|   |-- 4_Model_Insights.py
|   |-- 5_LLM_Integration.py
|   |-- 6_SME_Credit_Health.py
|   |-- 7_Profile_Settings.py
|   |-- 8_About.py
|   |-- 9_Support.py
|-- src/
|   |-- __init__.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- data_pipeline.py
|   |   |-- modeling.py
|   |   |-- runtime.py
|   |-- features/
|   |   |-- __init__.py
|   |   |-- alignment_features.py
|   |   |-- case_workflow.py
|   |   |-- explanations.py
|   |   |-- shap_explanations.py
|   |   |-- workbench_features.py
|   |-- ui/
|   |   |-- __init__.py
|   |   |-- components.py
|   |-- utils/
|       |-- __init__.py
|       |-- demo_persistence.py
|       |-- formatting.py
|       |-- table_views.py
```

If `docs/CredRiskAI_Pitchdeck_Speaker_Notes.md` is ignored by `.gitignore`, either remove that ignore rule before committing the handoff or treat the notes as a local-only companion file. A clone of GitHub will only contain files that are committed.

## Product Rules

- The app is an operational workspace, not a landing page.
- The SME loan application is applicant-provided information. It is the first contact point between the applicant data and the analyst.
- Do not require prior bank review, banker review input, plan confidence score, supervisor approval, or any field that suggests the application has already been reviewed before the analyst sees it.
- Keep the analyst final decision separate from the ML recommendation and separate from any AI second review.
- Allow the analyst to review the application manually, inspect ML output, inspect the AI review, and then save a final action.
- Use clear banker language. Avoid unexplained abbreviations and internal placeholders.
- High-risk outputs require human analyst or compliance handling before communication to the applicant.
- Do not include secrets, live customer data, or real production credentials.

## Navigation And Pages

### Home.py

Purpose: employee homepage for Ms. Cooper.

Required content:

- demo authentication flow with password and six-digit verification step,
- sidebar profile area with dark-mode toggle and demo state reset,
- welcome message for Ms. Cooper,
- current tasks table,
- Slack Updates,
- Calendar Today,
- summary metrics focused on assigned work, high-priority work, due-this-week items, and evidence follow-up.

Do not turn Home into a marketing page. Keep source status panels, model controls, and explanation controls out of Home.

### pages/1_Personal_Workspace.py

Purpose: single-case work surface.

Required flow:

1. Pick an assigned case, select a demo scenario, or enter a custom application.
2. Choose the supervised ML model.
3. Score the application.
4. Read the score output and deterministic rationale.
5. Review evidence readiness, calculated signals, similar cases, recommended terms, monitoring preview, and timeline.
6. Optionally open case review and save an analyst final decision.
7. Optionally continue to LLM Integration for an AI second review.

Required scenario options:

- `A2M Logistics Loan`
- `Low-risk established borrower`
- `Credit stacking case`
- `Suspicious transfers`
- `High country-risk borrower`
- `Custom application`

Required input groups:

- company profile,
- loan request,
- financial snapshot,
- five-year plan,
- applicant narrative,
- executive context,
- documents and verification,
- advanced signals.

Required score output near the top:

- application risk score,
- A-F grade,
- selected ML model label,
- model recommendation,
- final decision status,
- review status,
- stressed DSCR.

The page must show hover info boxes for key Personal Workspace metrics and labels. Implement these as small `?` help affordances using the local `.hover-help` styling pattern.

Data readiness labels must be plain:

- `Forecast support document received: Yes/No`
- `Financial statements received: Yes/No`
- `Bank statements received: Yes/No`
- `Tax return received: Yes/No`
- `Ownership/KYB documents received: Yes/No`
- `Decision use: Checks liquidity and whether free cash flow can cover estimated debt service.`

Do not use `forecast_plan_confidence_score`. If an old CSV contains that column, drop it.

### pages/2_Operations_Desk.py

Purpose: team workboard.

Required content:

- open work items,
- manual or compliance work,
- evidence follow-up,
- rejected-today count,
- filters,
- task table,
- selected-case detail,
- bulk rejection for selected visible cases,
- handoff into Personal Workspace for a single case.

Bulk rejections must update:

- `review_history`,
- `portfolio_history`,
- `bulk_final_decisions`,
- `bulk_action_history`.

### pages/3_Risk_Dashboard.py

Purpose: portfolio monitoring.

Required content:

- portfolio filters,
- filtered exposure,
- manual review queue,
- compliance review queue,
- highest-risk applications,
- live session decisions,
- analyst review audit trail.

### pages/4_Model_Insights.py

Purpose: model governance and comparison.

Required content:

- model selector for Random Forest and Logistic Regression,
- accuracy,
- balanced accuracy,
- precision,
- recall,
- F1,
- ROC-AUC,
- average precision,
- MCC,
- false-positive rate,
- false-negative rate,
- review-rate metrics,
- estimated error costs,
- precision at top 5, 10, and 20 percent review queues,
- confusion matrix,
- A-F thresholds,
- governance notes,
- feature importances,
- research-backed derived signals,
- risk score API contract preview.

### pages/5_LLM_Integration.py

Purpose: optional AI second review for the latest scored application.

Required flow:

1. If no case has been scored, show a no-case state.
2. Show the selected ML model baseline first.
3. Show deterministic explanation by default.
4. Let the user choose `Deterministic`, `OpenAI API`, or `Local server`.
5. Let the user choose `Detailed analyst memo` or `Concise summary`.
6. Call a hosted or local LLM only after the user clicks `Run LLM Review`.
7. Parse the returned AI review score and AI suggested grade.
8. Compare the normalized AI grade with the selected ML model grade.

The LLM prompt must ask for:

- independent AI credit assessment,
- agreement, partial agreement, or disagreement with the ML recommendation,
- exactly one line matching `AI review score: NN/100`,
- exactly one line matching `AI suggested grade: X`,
- A-F mapping using the same thresholds as the ML model,
- follow-up actions and questions,
- no invented facts,
- no legal certainty.

Local LLM defaults:

```text
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=local-model
LOCAL_LLM_API_KEY=local
```

Local URL normalization must accept server root, `/v1`, or a pasted `/chat/completions` path and call the correct OpenAI-compatible chat completions endpoint.

### pages/6_SME_Credit_Health.py

Purpose: borrower-facing MVP preview.

Required content:

- borrower credit-health score view,
- score drivers,
- what-if simulation,
- evidence source coverage,
- peer benchmarks.

### pages/7_Profile_Settings.py

Purpose: analyst profile and connected-app simulation.

Required content:

- analyst profile fields,
- user type and permissions,
- dark-mode preference,
- simulated connected apps such as Slack, Teams, Gmail, Outlook, Drive, OneDrive, SharePoint, and Zoom,
- team manager settings where relevant.

### pages/8_About.py

Purpose: explain scoring dimensions and derived signals in banker-readable language.

### pages/9_Support.py

Purpose: representative support surface.

Required content:

- email contacts,
- support request form,
- scripted live chat,
- FAQ.

## Data Contract

The canonical generated seed path is `data/seed`. The app may also keep `data/seeds` as a mirrored compatibility directory.

`src/core/data_pipeline.py` must expose:

- `BASE_NUMERIC_COLUMNS`
- `DERIVED_NUMERIC_COLUMNS`
- `NUMERIC_COLUMNS`
- `CATEGORICAL_COLUMNS`
- `TARGET_COLUMN`
- `DEPRECATED_COLUMNS = ["forecast_plan_confidence_score"]`
- `add_derived_features(frame)`
- `generate_seed_data(rows=1200, seed=42)`
- `load_seed_data()`
- `ensure_seed_data()`

Base numeric columns:

```text
requested_amount, term_months, interest_rate, annual_revenue, years_in_business,
existing_debt, num_recent_loans, late_payment_ratio, suspicious_transfer_ratio,
collateral_ratio, employees, country_risk_score, free_cash_flow, monthly_burn_rate,
cash_flow_to_revenue_ratio, expected_runway_months, forecast_revenue_cagr,
forecast_employee_cagr, forecast_fcf_margin_year5, planned_debt_reduction_pct,
current_ratio, quick_ratio, receivables_days, payables_days, inventory_days,
financial_statements_uploaded, bank_statements_uploaded, tax_return_uploaded,
ownership_docs_uploaded, forecast_support_uploaded, document_edit_count,
late_stage_change_count, process_deviation_score, email_domain_age_months,
website_age_months, bank_account_age_months, location_mismatch_score,
duplicate_contact_score, related_party_exposure_score,
counterparty_concentration_score, shared_identifier_score,
narrative_contradiction_score
```

Derived numeric columns:

```text
debt_to_revenue_ratio, request_to_revenue_ratio, loan_velocity_score,
payment_stress_score, collateral_gap_ratio, external_financing_pressure,
financial_distress_score, transaction_anomaly_score, company_scale_mismatch_score,
governance_complexity_score, cash_flow_pressure_score, runway_risk_score,
cash_conversion_risk_score, forecast_plan_aggressiveness_score,
forecast_execution_risk_score, forecast_hiring_efficiency_risk_score,
forecast_debt_service_risk_score, annual_interest_expense, annual_debt_service,
debt_service_coverage_ratio, stressed_annual_debt_service,
stressed_debt_service_coverage_ratio, interest_rate_risk_score,
debt_service_stress_score, cash_conversion_cycle_days,
document_completeness_score, document_quality_risk_score,
process_integrity_risk_score, identity_verification_risk_score,
working_capital_pressure_score, financial_statement_anomaly_score,
related_party_network_risk_score, narrative_consistency_risk_score
```

Categorical columns:

```text
industry, region, company_type
```

Target column:

```text
is_fraud
```

Seed CSVs:

- `applications.csv`
- `company_profiles.csv`
- `cash_flows.csv`
- `forecasts.csv`
- `transactions.csv`
- `decisions.csv`

If seed files are missing, stale, or have placeholder names, `ensure_seed_data()` must regenerate them with `generate_seed_data(rows=1200, seed=42)`.

## ML Scoring Contract

`src/core/modeling.py` must use scikit-learn and expose:

- `ModelSpec`
- `ModelBundle`
- `train_model(applications)`
- `grade_from_probability(probability)`
- `decision_from_grade(grade)`
- `rule_flags(application)`
- `score_application(model_bundle, application, model_key=None)`
- `score_portfolio(model_bundle, applications, model_key=None)`

Supported models:

- `random_forest`: label `Random Forest`
- `logistic_regression`: label `Logistic Regression`

The default model key is `random_forest`.

Both models must output a continuous risk score between `0` and `1` using `predict_proba(...)[..., 1]`.

Shared preprocessing:

- `Pipeline`
- `ColumnTransformer`
- numeric median imputation
- numeric `StandardScaler`
- categorical most-frequent imputation
- categorical `OneHotEncoder(handle_unknown="ignore")`

Random Forest classifier:

```text
RandomForestClassifier(
    n_estimators=220,
    min_samples_leaf=4,
    random_state=42,
    class_weight="balanced",
)
```

Logistic Regression classifier:

```text
LogisticRegression(
    max_iter=2500,
    class_weight="balanced",
    solver="lbfgs",
)
```

Metrics required for each model:

- accuracy,
- balanced accuracy,
- precision,
- recall,
- F1,
- ROC-AUC,
- average precision,
- MCC,
- precision at 5, 10, and 20 percent,
- false-positive rate,
- false-negative rate,
- predicted review rate,
- estimated review cost,
- estimated false-positive cost,
- estimated false-negative cost,
- estimated total error cost,
- confusion matrix counts.

Feature importance:

- use `feature_importances_` for Random Forest,
- use absolute coefficients for Logistic Regression,
- normalize names by removing `numeric__` and `categorical__`.

## Risk Grade Policy

Use this A-F grade mapping everywhere:

```text
A: application risk score < 0.15
B: application risk score < 0.28
C: application risk score < 0.42
D: application risk score < 0.58
E: application risk score < 0.74
F: application risk score >= 0.74
```

Use this model recommendation mapping:

```text
A or B: Approve
C or D: Manual Review
E or F: Reject
```

`Manual Review` is a post-score analyst workflow state. It is not a required prior bank review input.

## Work Queue Contract

`src/features/workbench_features.py` must define:

```text
ALICE_ANALYST = "Ms. Cooper"
ALICE_MAX_TASKS = 20
ALICE_SAME_DAY_TASKS = 2
ALICE_THIS_WEEK_TASKS = 5
```

Alice Cooper's assigned queue must be capped at 20 tasks:

- exactly 2 same-day SLA tasks when enough same-day cases exist,
- exactly 5 due-this-week tasks when enough eligible cases exist,
- remaining Alice tasks due next week,
- include manual/compliance and missing-document work in the visible metrics,
- assign all other cases to `M. van Dijk` or `S. Jansen`.

Queue status logic:

- grade E or F: `Compliance review`,
- document completeness below 0.8: `Request documents`,
- grade C or D: `Manual review`,
- otherwise: `Ready for approval`.

SLA defaults:

- A or B: `Next week`,
- C or D: `This week`,
- E or F: `Same day`.

## Runtime State Contract

Every Streamlit page must call `bootstrap_state()` before using shared state.

`src/core/runtime.py` must initialize:

- `seed_data`
- `model_bundle`
- `portfolio_history`
- `score_history`
- `review_history`
- `last_application`
- `last_prediction`
- `last_explanation`
- `last_explanation_source`
- `last_explanation_error`
- `last_review`
- `last_email_link`
- `show_review_dialog`
- `use_llm_explanations`
- `llm_chat_provider`
- `llm_chat_explanation`
- `llm_chat_source`
- `llm_chat_error`
- `llm_chat_signature`
- `llm_review_history`
- `llm_provider`
- `selected_ml_model`
- `explanation_model`
- local LLM base URL, model, API key, and draft settings
- `bulk_final_decisions`
- `bulk_action_history`
- `support_ticket_history`
- `active_queue_application`
- `active_intake_source`

Default `selected_ml_model` is `random_forest`, and it must be reset if the selected key is not in the trained model registry.

## Explanation Contract

`src/features/explanations.py` must provide:

- deterministic explanation that works offline,
- hosted OpenAI explanation through `OPENAI_API_KEY`,
- local OpenAI-compatible server explanation,
- local URL normalization,
- visible fallback errors,
- deterministic fallback when hosted or local calls fail.

The deterministic explanation must include:

- decision,
- grade,
- application risk score,
- applicant context,
- top risk drivers,
- mitigating factors,
- recommended analyst action,
- compliance note.

The LLM explanation must use selected ML model output and metrics, not hard-coded Random Forest text.

## Review Workflow Contract

`src/features/case_workflow.py` owns demo scenarios, review rows, audit exports, and final-decision separation.

Analyst final decisions are saved after scoring. They do not rewrite the model score or AI review. Keep these concepts separate:

- applicant-provided loan application,
- selected ML model recommendation,
- deterministic or LLM AI review,
- analyst final decision,
- audit history.

## UI And Styling Contract

- Operational, compact, bank-workbench feel.
- No marketing landing page.
- No visible developer or sample-data caveats except clearly marked presentation examples.
- Use European formatting helpers from `src/utils/formatting.py`.
- Use custom components from `src/ui/components.py` where they already exist.
- Use `width="stretch"` rather than deprecated `use_container_width=True` in new Streamlit tables and charts.
- Use hover help/info boxes for dense workspace metrics.
- Keep labels readable on desktop and mobile.
- Do not add unrelated decorative visuals.

`.streamlit/config.toml` should keep sidebar navigation hidden and use the light theme:

```toml
[client]
showSidebarNavigation = false

[theme]
base = "light"
primaryColor = "#14B8A6"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#0F172A"
```

## Documentation Contract

Maintain:

- `README.md`: product summary, setup, `Run_App.bat`, manual launch, walkthrough, LLM providers, page overview, A-F grade policy.
- `DEMO.md`: presentation runbook.
- `docs/CredRiskAI_Pitchdeck.html`: browser pitch deck.
- `docs/CredRiskAI_Pitchdeck.pdf`: exported pitch deck.
- `docs/CredRiskAI_Pitchdeck.pptx`: slide deck file.
- `docs/CredRiskAI_Pitchdeck_Speaker_Notes.md`: speaker notes when included in the handoff.
- `data/docs/fraud_research.md`: research grounding for derived signals.

Pitch materials must describe:

- SME-provided application as the first data-to-analyst contact point,
- supervised ML scoring with Random Forest and Logistic Regression,
- optional deterministic, hosted, or local AI second review,
- analyst review of the application and AI output,
- no plan confidence score,
- no prior bank-review requirement.

## Rebuild Steps For A Fresh Codex

If starting from an empty folder and no cloneable remote:

1. Create the file tree above.
2. Write `requirements.txt`.
3. Implement `src/core/data_pipeline.py` with the data contract and deterministic generator.
4. Implement `src/core/modeling.py` with the two-model registry and risk grade policy.
5. Implement `src/core/runtime.py` with all session-state keys.
6. Implement utilities in `src/utils/formatting.py`, `src/utils/table_views.py`, and `src/utils/demo_persistence.py`.
7. Implement reusable UI helpers in `src/ui/components.py`.
8. Implement case, explanation, SHAP, alignment, and workbench feature modules under `src/features`.
9. Implement `Home.py` and all pages under `pages/` with the page contracts above.
10. Create documentation files from the documentation contract.
11. Create or import binary assets. For exact reproduction, obtain them from the remote repo or a repository archive.
12. Run seed generation by importing `ensure_seed_data()`.
13. Run compile checks and the ML smoke test.
14. Start Streamlit with `streamlit run Home.py`.

## Verification Commands

Compile:

```bash
python -m compileall src Home.py pages
```

Model and queue smoke test:

```bash
python - <<'PY'
from src.core.data_pipeline import ensure_seed_data
from src.core.modeling import train_model
from src.features.workbench_features import build_application_queue

seed = ensure_seed_data()
bundle = train_model(seed["applications"])
assert {"random_forest", "logistic_regression"}.issubset(bundle.models)

for key in ["random_forest", "logistic_regression"]:
    queue = build_application_queue(bundle, seed["applications"], model_key=key)
    alice = queue[queue["assigned_analyst"].eq("Ms. Cooper")]
    assert len(alice) <= 20
    assert alice["sla"].eq("Same day").sum() <= 2
    assert alice["sla"].eq("This week").sum() <= 5
    sample = seed["applications"].iloc[0].to_dict()
    prediction = bundle.score_one(sample, model_key=key)
    assert 0 <= prediction["fraud_probability"] <= 1
    assert prediction["model_key"] == key
print("smoke ok")
PY
```

PowerShell equivalent:

```powershell
@'
from src.core.data_pipeline import ensure_seed_data
from src.core.modeling import train_model
from src.features.workbench_features import build_application_queue

seed = ensure_seed_data()
bundle = train_model(seed["applications"])
assert {"random_forest", "logistic_regression"}.issubset(bundle.models)

for key in ["random_forest", "logistic_regression"]:
    queue = build_application_queue(bundle, seed["applications"], model_key=key)
    alice = queue[queue["assigned_analyst"].eq("Ms. Cooper")]
    assert len(alice) <= 20
    assert alice["sla"].eq("Same day").sum() <= 2
    assert alice["sla"].eq("This week").sum() <= 5
    sample = seed["applications"].iloc[0].to_dict()
    prediction = bundle.score_one(sample, model_key=key)
    assert 0 <= prediction["fraud_probability"] <= 1
    assert prediction["model_key"] == key
print("smoke ok")
'@ | python -
```

Run app:

```bash
streamlit run Home.py
```

Functional checks:

- Home loads after demo login and shows Ms. Cooper's workday.
- Personal Workspace can score assigned, demo, and custom applications.
- Hover help boxes appear for dense Personal Workspace metrics.
- Random Forest and Logistic Regression both return 0-1 risk scores.
- Data readiness uses plain evidence labels.
- No plan confidence score appears anywhere.
- No prior bank-review requirement appears anywhere.
- Analyst final decision remains separate from model recommendation and AI review.
- Operations Desk bulk rejection records audit history.
- Risk Dashboard shows queues and live session decisions.
- Model Insights compares model metrics and feature importances.
- LLM Integration makes no hosted/local call until `Run LLM Review` is clicked.
- App works without `OPENAI_API_KEY` and without a local LLM server.
