# Codex Build Specification: CredRisk.AI Underwriter Workbench

This file is the handoff contract for a fresh Codex session. It must be detailed enough for a new agent to rebuild or maintain the app without relying on unstated product memory. When implementation and this file disagree, inspect the implementation, fix the drift, and update this file in the same change.

## Perfection Standard

A correct rebuild is not a generic credit-risk dashboard. It is this specific local Streamlit product:

1. SME creates a loan intake in the Loan Intake Portal.
2. SME submits a locked snapshot to the lender.
3. Lender opens the submitted snapshot from Home or Personal Workspace.
4. Lender scores with the Random Forest baseline.
5. Lender validates documents, generates AI output, completes Case Review, and publishes.
6. SME returns in the same local demo session and sees a clear YourBank-reviewed result screen.

The build is acceptable only when:

- the role flow is SME -> lender -> SME;
- the lender cannot edit SME-owned intake fields;
- the SME cannot see internal model probabilities, provisional model grades, AI scores, validation metrics, or private analyst notes before publication;
- the visible supervised model workflow is Random Forest only;
- five-year plans are annual five-row tables, not year-5-only inputs;
- sample cases and generated evidence live on the SME side;
- document uploads save real local bytes and hashes;
- Clear Session deletes local demo state, deletes local evidence, logs the user out, and starts a fresh `demo_session`;
- deterministic mode works without external API keys;
- the app launches from `Home.py`.

## Product Identity

Name: `CredRisk.AI Underwriter Workbench`

Core roles:

- `SME company`: applicant-side intake, evidence, submission, and returned rating.
- `Lender analyst`: YourBank-side scoring, review, validation, AI output, and publication.

Primary lender persona:

- name: `Alice Cooper`
- display name: `Ms. Cooper`
- bank: `YourBank`
- email: `alice.cooper@yourbank.com`
- role: `Credit Analyst`
- team: `SME Credit Operations`

Primary SME persona:

- name/display: `A2M Logistics`
- email: `LukeWalker@A2M.com`
- role: `Finance Director`
- team: `Company Finance`

The app is decision support only. Do not frame any model, AI, or document-validation result as legal certainty, automatic rejection, or production underwriting.

## Runtime And Dependencies

Python: 3.10+

Dependencies in `requirements.txt`:

```text
streamlit
pandas
numpy
scikit-learn
openai
shap
pypdf
watchdog
```

Manual run:

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Windows launcher:

```text
Run_App.bat
```

Streamlit config:

```toml
[client]
showSidebarNavigation = false
```

Do not introduce `app.py`. Do not rely on Streamlit's default multipage sidebar; use the custom sidebar in `src/ui/components.py`.

## Required File Structure

Implement this structure:

```text
Home.py
pages/
  1_Personal_Workspace.py
  2_Operations_Desk.py
  3_Risk_Dashboard.py
  4_Model_Insights.py
  5_LLM_Integration.py
  6_SME_Credit_Health.py
  7_Profile_Settings.py
  8_About.py
  9_Support.py
  10_Tutorials.py
  11_Acronym_Guide.py
src/
  constants.py
  core/
    data_pipeline.py
    modeling.py
    runtime.py
  features/
    alignment_features.py
    case_workflow.py
    document_validation.py
    explanations.py
    shap_explanations.py
    workbench_features.py
  ui/
    components.py
    document_validation.py
  utils/
    acronym_guide.py
    demo_persistence.py
    document_examples.py
    document_storage.py
    formatting.py
    llm_profiles.py
    table_views.py
    workflow_transfer.py
tests/
  test_forecast_plan.py
README.md
DEMO.md
requirements.txt
Run_App.bat
```

Ignored local artifacts:

- `.tmp/`
- `.venv/`
- bytecode caches
- local LLM profile files
- generated demo sessions
- generated SME document vault files
- credentials and API tokens

## Page Bootstrap Rule

Every Streamlit page must start with:

```python
st.set_page_config(...)
bootstrap_state()
render_sidebar()
```

Exceptions are only allowed when intentionally passing a sidebar option such as:

```python
render_sidebar(suppress_demo_prompt=True)
```

`bootstrap_state()` must run before reading shared state.

## Authentication And Navigation

Login uses a demo gate with fake credentials.

Visible login contract:

- username field label: `Username`
- default/expected username: `DemoUser`
- account choices: SME company and Lender analyst
- SME SSO button: `SME SSO`
- lender SSO button: `YourBank SSO`
- password and six-digit verification accept any values

Role-scoped navigation:

Lender navigation:

```text
Credit Work
  Home -> Home.py
  Personal Workspace -> pages/1_Personal_Workspace.py
  LLM Integration -> pages/5_LLM_Integration.py
Operations & Risk
  Operations Desk -> pages/2_Operations_Desk.py
  Risk Dashboard -> pages/3_Risk_Dashboard.py
  Model Insights -> pages/4_Model_Insights.py
Account & Help
  Profile & Settings -> pages/7_Profile_Settings.py
  Tutorials -> pages/10_Tutorials.py
  Support -> pages/9_Support.py
  Acronym Guide -> pages/11_Acronym_Guide.py
  About -> pages/8_About.py
```

SME navigation:

```text
Company Portal
  Company Setup & Credit Health -> pages/6_SME_Credit_Health.py
Help
  Tutorials -> pages/10_Tutorials.py
  Support -> pages/9_Support.py
  Acronym Guide -> pages/11_Acronym_Guide.py
```

SME users who open Home must be routed to the Loan Intake Portal. Lender users who open the SME portal must see a blocked message and links back to lender pages.

## State And Persistence

Local refresh-safe state lives at:

```text
.tmp/demo_sessions/<demo_session>.json
```

The URL query parameter is:

```text
demo_session=<session-id>
```

Persist exactly JSON-safe workflow state. Do not persist model objects, DataFrames, secrets, or local API tokens.

Persisted keys:

```text
authenticated
remember_me
login_stage
login_transition
user_profile
portfolio_history
score_history
review_history
last_application
last_prediction
last_explanation
last_explanation_source
last_explanation_error
last_review
last_email_link
show_review_dialog
llm_chat_provider
llm_chat_explanation
llm_chat_source
llm_chat_error
llm_chat_signature
llm_chat_last_run
llm_review_history
llm_evaluation_packages
document_validation_results
explanation_model
bulk_final_decisions
bulk_action_history
support_ticket_history
active_queue_application
active_intake_source
sme_company_application
sme_connection_status
sme_submission_history
application_lifecycle
rating_publication_history
loan_example_scenario
profile_settings_saved
demo_prompt_remembered
demo_prompt_choice
```

Clear Session must:

1. determine the current `demo_session`;
2. delete `.tmp/demo_sessions/<demo_session>.json`;
3. delete `.tmp/sme_documents/<demo_session>/`;
4. remove Streamlit session keys;
5. create a fresh `demo-<12 hex>` session id;
6. update the query parameter;
7. set `authenticated = False`;
8. set `login_stage = "credentials"`;
9. rerun into the login screen.

Streamlit cannot cleanly stop its own server from a sidebar button. README must tell users to stop the instance with `Control-C` in the terminal.

## Data Schema

Synthetic portfolio data lives under:

```text
data/seed/
```

`data/seeds/` may exist only as compatibility history. Do not make it the active source.

Core constants:

```text
TARGET_COLUMN = is_fraud
CATEGORICAL_COLUMNS = industry, region, company_type
FORECAST_YEARS = 1..5
DEPRECATED_COLUMNS = forecast_plan_confidence_score
```

Base numeric model inputs:

```text
requested_amount
term_months
interest_rate
annual_revenue
years_in_business
existing_debt
num_recent_loans
late_payment_ratio
suspicious_transfer_ratio
collateral_ratio
employees
country_risk_score
free_cash_flow
monthly_burn_rate
cash_flow_to_revenue_ratio
expected_runway_months
forecast_revenue_cagr
forecast_employee_cagr
forecast_fcf_margin_year5
planned_debt_reduction_pct
current_ratio
quick_ratio
receivables_days
payables_days
inventory_days
financial_statements_uploaded
bank_statements_uploaded
tax_return_uploaded
ownership_docs_uploaded
forecast_support_uploaded
document_edit_count
late_stage_change_count
process_deviation_score
email_domain_age_months
website_age_months
bank_account_age_months
location_mismatch_score
duplicate_contact_score
related_party_exposure_score
counterparty_concentration_score
shared_identifier_score
narrative_contradiction_score
```

Derived numeric model inputs:

```text
debt_to_revenue_ratio
request_to_revenue_ratio
loan_velocity_score
payment_stress_score
collateral_gap_ratio
external_financing_pressure
financial_distress_score
transaction_anomaly_score
company_scale_mismatch_score
governance_complexity_score
cash_flow_pressure_score
runway_risk_score
cash_conversion_risk_score
forecast_plan_aggressiveness_score
forecast_execution_risk_score
forecast_hiring_efficiency_risk_score
forecast_debt_service_risk_score
annual_interest_expense
annual_debt_service
debt_service_coverage_ratio
stressed_annual_debt_service
stressed_debt_service_coverage_ratio
interest_rate_risk_score
debt_service_stress_score
cash_conversion_cycle_days
document_completeness_score
document_quality_risk_score
process_integrity_risk_score
identity_verification_risk_score
working_capital_pressure_score
financial_statement_anomaly_score
related_party_network_risk_score
narrative_consistency_risk_score
```

Seed generation requirements:

- deterministic synthetic data;
- default row count: 1,200;
- seed: 42;
- real-like company names, not `Company 1`;
- regenerate when seed files are missing, stale, missing base columns, or still contain generic company names;
- drop deprecated columns on load.

## Forecast Plan Contract

The SME five-year plan is stored in `forecast_plan_rows`.

Required row shape:

```python
{
    "forecast_year": 1,
    "projected_revenue": 0.0,
    "projected_employees": 1,
    "projected_free_cash_flow": 0.0,
    "projected_debt": 0.0,
}
```

Validation:

- exactly five rows;
- years exactly `1, 2, 3, 4, 5`;
- projected revenue `>= 0`;
- projected employees `>= 1`;
- projected free cash flow is required and may be negative;
- projected debt `>= 0`;
- reject empty manual rows on save/submission.

Derived compatibility fields from year 5:

```text
forecast_revenue_year5
forecast_employees_year5
forecast_fcf_year5
planned_debt_reduction_amount
forecast_revenue_cagr
forecast_employee_cagr
forecast_fcf_margin_year5
planned_debt_reduction_pct
```

`build_forecast_table()` behavior:

- if valid `forecast_plan_rows` exist, return those exact rows plus application/company ids;
- for legacy records without rows, generate five fallback rows from CAGR/margin/debt assumptions;
- never mutate the application record while rendering.

## Sample Cases

SME sample intake cases:

```text
Blank manual intake -> empty manual application, no prefilled plan values
Clean evidence -> Low-risk established borrower -> NoviCore Software B.V.
Neutral evidence -> A2M Logistics Loan -> A2M Logistics B.V.
Risky evidence -> Credit stacking case -> Riverton Buildworks LLC
Fraudulent evidence -> Suspicious transfers -> Mercado Azul Trading S.A.S.
Ambiguous evidence -> High country-risk borrower -> Al Noor Freight Services
```

Only the fraudulent evidence case should set `sample_document_profile = "fraudulent"` and pre-seed all five document categories.

Forecast profile factors:

```text
Clean evidence
  revenue: 1.07, 1.16, 1.28, 1.40, 1.54
  employees: 1.03, 1.08, 1.15, 1.24, 1.34
  fcf margins: 0.12, 0.125, 0.135, 0.145, 0.16
  debt: 0.90, 0.80, 0.70, 0.58, 0.45

Neutral evidence
  revenue: 0.97, 1.02, 1.10, 1.19, 1.29
  employees: 0.99, 1.00, 1.05, 1.10, 1.16
  fcf margins: 0.00, 0.018, 0.035, 0.055, 0.075
  debt: 0.98, 0.94, 0.86, 0.78, 0.70

Risky evidence
  revenue: 1.18, 1.06, 1.28, 1.42, 1.68
  employees: 1.00, 1.02, 1.05, 1.12, 1.18
  fcf margins: -0.11, -0.07, -0.025, 0.02, 0.06
  debt: 0.99, 0.98, 0.94, 0.88, 0.82

Fraudulent evidence
  revenue: 1.35, 2.05, 3.10, 4.35, 5.75
  employees: 1.00, 1.02, 1.03, 1.05, 1.07
  fcf margins: -0.02, 0.14, 0.24, 0.33, 0.42
  debt: 0.92, 1.08, 0.74, 0.96, 0.38

Ambiguous evidence
  revenue: 1.12, 0.96, 1.30, 1.18, 1.46
  employees: 1.05, 1.00, 1.12, 1.10, 1.22
  fcf margins: 0.02, -0.04, 0.06, 0.01, 0.08
  debt: 0.95, 0.91, 0.97, 0.79, 0.72
```

## Model Contract

Visible model workflow: Random Forest only.

Do not expose an ML model selector in SME or lender workflow.

Internal constants:

```text
MODEL_CACHE_VERSION = rf-only-v1
DEFAULT_MODEL_KEY = random_forest
MODEL_LABELS = {"random_forest": "Random Forest"}
```

Training pipeline:

- `add_derived_features()` first;
- features: all `NUMERIC_COLUMNS + CATEGORICAL_COLUMNS`;
- target: `is_fraud`;
- train/test split: 75/25;
- random state: 42;
- stratified split;
- numeric preprocessing: median imputation + standard scaling;
- categorical preprocessing: most-frequent imputation + one-hot encoding;
- classifier: `RandomForestClassifier(n_estimators=220, min_samples_leaf=4, random_state=42, class_weight="balanced")`.

Validation metrics:

```text
accuracy
balanced_accuracy
precision
recall
f1
roc_auc
average_precision
mcc
precision_at_5pct
precision_at_10pct
precision_at_20pct
false_positive_rate
false_negative_rate
predicted_review_rate
estimated_review_cost
estimated_false_positive_cost
estimated_false_negative_cost
estimated_total_error_cost
tn
fp
fn
tp
```

Risk grade thresholds:

```text
A: score < 0.15
B: score < 0.28
C: score < 0.42
D: score < 0.58
E: score < 0.74
F: score >= 0.74
```

Model recommendation:

```text
A-B -> Approve
C-D -> Manual Review
E-F -> Reject
```

Rule flags should cover high request/revenue, debt pressure, recent loans, late payments, suspicious transfers, low collateral, short operating history, country risk, financing pressure, distress, transaction anomaly, scale mismatch, negative FCF, cash-flow pressure, runway risk, weak cash conversion, missing forecast support with aggressive growth, forecast execution risk, hiring efficiency risk, debt-service risk, high interest rate, DSCR below 1.0, stressed DSCR below 1.0, document completeness, document quality, process integrity, identity/KYB risk, working-capital risk, statement anomaly, related-party risk, and narrative consistency risk.

## Document Storage And Validation

Document categories:

```text
financial_statements -> Financial statements
bank_statements -> Bank statements
tax_returns -> Tax returns
ownership_kyb -> Ownership / KYB
forecast_support -> Forecast support
```

Vault path:

```text
.tmp/sme_documents/<demo_session>/<application_id>/<category>/
```

Manifest path:

```text
.tmp/sme_documents/<demo_session>/<application_id>/manifest.json
```

Manifest fields:

```text
document_id
application_id
category
category_label
original_name
stored_name
content_type
size_bytes
sha256
uploaded_at
```

Save behavior:

- store exact uploaded/generated bytes;
- generate `DOC-<12 hex>` ids;
- preserve original filename in metadata;
- de-duplicate by category + SHA-256 hash;
- use atomic manifest writes;
- lender downloads must read through manifest entries only;
- clearing a demo session deletes that session's document vault.

Document validation:

- deterministic local validation always runs first;
- optional OpenAI/local validation must be explicit-click only;
- hosted/local AI receives bounded previews and metadata, not full binary files;
- validation is category/triage support, not legal authenticity.

Red-flag markers:

```text
unreconciled
manual revenue adjustment
missing invoice
negative ledger export
audit trail
same-day
round-number
related party
shared director
undisclosed affiliate
tax turnover materially below
unresolved arrears
older than 12 months
registration number format differs
ubo not present
not disclosed
possible sanctions
fuzzy match
unsupported growth
unsigned loi
```

Forecast-support sample CSV columns:

```text
forecast_year
projected_revenue_eur
projected_employees
projected_free_cash_flow_eur
projected_debt_eur
assumptions_evidence_note
```

## LLM And AI Review

Providers:

```text
Deterministic
OpenAI API
Local server
```

External calls occur only when the user clicks the generation button.

OpenAI:

- read `OPENAI_API_KEY` from Streamlit secrets or environment;
- do not persist the key.

Local server defaults:

```text
LOCAL_LLM_BASE_URL = http://localhost:1234/v1
LOCAL_LLM_MODEL = local-model
LOCAL_LLM_API_KEY = local
```

Local profile stores only:

```json
{"ip": "...", "model_name": "..."}
```

Default profile paths:

```text
Windows: %LOCALAPPDATA%\CredRiskAI\llm_models\local_server.json
macOS: ~/Library/Application Support/CredRiskAI/llm_models/local_server.json
Linux: ${XDG_CONFIG_HOME:-~/.config}/CredRiskAI/llm_models/local_server.json
```

`CREDRISK_LLM_MODELS_DIR` overrides the profile folder.

AI package behavior:

- requires latest scored case;
- uses `evaluation_signature(application, prediction)` to prevent stale reuse;
- creates a private internal lender report;
- creates a separate applicant-safe SME report draft;
- stores package in `llm_evaluation_packages`;
- Personal Workspace requires this package before Case Review;
- publication copies the reviewed SME report text into `application_lifecycle`.

Applicant-safety filter must remove internal model probabilities, AI scores, provisional grades, validation metrics, and routing/internal language from SME-facing text.

## Module Contracts

Keep page files as workflow composition layers. Shared behavior belongs in `src/` so multiple pages can use the same state, scoring, document, and formatting rules.

### `src/core/runtime.py`

Owns application bootstrapping.

Required behavior:

- `get_seed_data()` returns current-schema synthetic portfolio data.
- `get_model_bundle()` returns the cached RF-only model bundle.
- `bootstrap_state()` restores demo-session JSON, initializes seed data and model bundle, hydrates saved local LLM endpoint/model settings, creates default profile/workflow stores, and persists JSON-safe state.
- Schema/model cache checks must invalidate stale cached data when model inputs, metric keys, or generated company naming rules change.

### `src/core/data_pipeline.py`

Owns schema, generated seed data, derived features, forecast validation, and forecast rendering.

Required public helpers:

```text
validate_forecast_plan_rows(value)
forecast_metrics_from_plan_rows(application, forecast_plan_rows)
add_derived_features(frame)
build_forecast_table(applications)
generate_seed_data(rows=1200, seed=42)
load_seed_data()
ensure_seed_data()
```

Rules:

- keep `BASE_NUMERIC_COLUMNS`, `DERIVED_NUMERIC_COLUMNS`, `CATEGORICAL_COLUMNS`, and `TARGET_COLUMN` as the canonical model schema;
- `validate_forecast_plan_rows()` must normalize numeric values, reject missing/invalid rows, and return a clear error list;
- `forecast_metrics_from_plan_rows()` must derive year-5 and CAGR compatibility fields without requiring the SME to enter those legacy fields directly;
- `add_derived_features()` must tolerate missing input columns by filling safe defaults;
- `build_forecast_table()` must preserve submitted annual rows exactly when available;
- `ensure_seed_data()` must regenerate stale seeds instead of letting old schema drift break the demo.

### `src/core/modeling.py`

Owns supervised model training, scoring, grade mapping, recommendations, and rule flags.

Required public helpers:

```text
train_model(applications)
grade_from_probability(probability)
decision_from_grade(grade)
rule_flags(application)
score_application(model_bundle, application, model_key=None)
score_portfolio(model_bundle, applications, model_key=None)
```

Rules:

- default `model_key` must resolve to `random_forest`;
- user-facing labels must say `Random Forest`;
- `score_application()` returns probability, grade, recommendation, model label/key, rule flags, metrics, and top drivers;
- `rule_flags()` should be readable business logic, not a black-box duplicate of model probability.

### `src/ui/components.py`

Owns shared layout, login, role profile state, sidebar navigation, theme handling, and global reset controls.

Required behavior:

- login starts with account-type selection, username `DemoUser`, role-specific fake SSO buttons, and any-value demo password/verification;
- `get_profile()` and `save_profile()` keep lender and SME profile defaults distinct;
- `is_sme_profile()` is the role boundary used by pages;
- `open_application_in_workspace()` sets the active lender case and clears stale scored-case state;
- `render_sidebar()` must show only role-appropriate navigation and include Clear Session at the lower-left/sidebar footer area;
- Clear Session must show a confirmation safeguard before calling `clear_demo_state()`.

### `src/utils/demo_persistence.py`

Owns refresh-safe local state.

Required public helpers:

```text
ensure_demo_session()
restore_demo_state()
persist_demo_state()
clear_demo_state()
```

Rules:

- the session id format is `demo-<12 hex>`;
- `restore_demo_state()` only restores keys listed in `PERSISTED_KEYS`;
- `persist_demo_state()` must JSON-normalize values and skip unserializable objects;
- `clear_demo_state()` must remove the current session JSON, delete matching SME document vault files, clear session keys, create a fresh session id, and return the app to logged-out credentials state.

### `src/utils/workflow_transfer.py`

Owns submitted SME snapshot transfer into lender workflow.

Required public helpers:

```text
submission_snapshot(submission, active_application=None, sme_application=None)
submitted_intake_rows(...)
find_submitted_application(...)
```

Rules:

- source label is `SME Portal submission`;
- snapshots are lender-read-only copies;
- table rows must show enough context for lender Home and Personal Workspace to open the correct submitted case;
- connection and document counts come from the submitted snapshot, not from synthetic queue defaults.

### `src/utils/document_storage.py`

Owns local document bytes and manifests.

Required public helpers:

```text
save_document(...)
list_documents(...)
read_document(...)
document_counts(...)
clear_session_documents(...)
```

Rules:

- never fake document availability without saved bytes;
- downloads must read the stored bytes through manifest metadata;
- document ids use `DOC-<12 hex>`;
- all application/category path segments must be sanitized.

### `src/utils/document_examples.py`

Owns generated fictional evidence files for SME sample cases.

Required behavior:

- `build_document_examples(application, generated_on=None)` returns one example per document category;
- generated files must be CSV bytes with realistic but fictional values;
- forecast-support examples must contain annual five-year rows and `assumptions_evidence_note`;
- fraudulent examples must include red-flag text that `src/features/document_validation.py` can detect;
- example saving in the SME portal must use `save_document()`.

### `src/features/document_validation.py` And `src/ui/document_validation.py`

Own document validation logic and rendering.

Required behavior:

- deterministic validation detects expected category, category mismatch, red-flag markers, preview text, and confidence/status;
- optional OpenAI/local validation is explicit-click only and bounded by `MAX_PREVIEW_CHARS`;
- validation summaries are stored per application and scope;
- the UI panel can run validation over saved document manifests and render prior runs.

### `src/features/explanations.py`

Owns deterministic and optional AI second-review output.

Required public helpers:

```text
evaluation_signature(application, prediction)
deterministic_explanation(application, prediction)
deterministic_sme_report(application, prediction)
generate_evaluation_package(application, prediction, provider, ...)
explain_prediction(application, prediction, ...)
```

Rules:

- deterministic output must work offline;
- hosted/local calls may run only after an explicit user action;
- applicant-safe reports must pass through `_sanitize_sme_report()`;
- evaluation packages must be keyed to the current application/prediction signature.

### `src/features/workbench_features.py`

Owns lender workbench helpers.

Required public helpers:

```text
missing_documents(application)
queue_status(row)
build_application_queue(model_bundle, applications, limit=None, model_key=None)
recommended_loan_terms(application, prediction, signals)
portfolio_monitoring_preview(application, prediction, signals)
grouped_risk_drivers(application, signals)
data_source_badges(application, signals)
decision_timeline(application, prediction, review=None)
model_confidence_rows(metrics, prediction, signals)
credit_memo(...)
```

Rules:

- Operations Desk queue data is synthetic and separate from submitted SME cases;
- recommended loan terms are lender-side only and must not ask the SME to request an interest rate;
- expensive portfolio scoring should use Streamlit caching keyed by model cache identity and model key.

### `src/features/alignment_features.py`, `src/features/case_workflow.py`, And `src/features/shap_explanations.py`

Own what-if planning, review summaries, similar-case context, peer/data-source rows, and SHAP driver tables.

Rules:

- what-if tools must remain decision-support simulations;
- case summaries must keep model recommendation, AI view, analyst action, and final publication distinct;
- SHAP output is explanatory support for the RF model, not a separate decision engine.

### `src/constants.py`, `src/utils/formatting.py`, `src/utils/table_views.py`, And `src/utils/acronym_guide.py`

Own shared labels, help text, formatting, tables, and glossary content.

Rules:

- SME help text must explain applicant-facing form fields in plain language;
- lender metric explanations may include internal risk terminology;
- financial inputs should accept European numeric formatting through shared parse/format helpers;
- table column aliases should live in shared helpers instead of one-off page dictionaries when reused.

## Page Specifications

### `Home.py`

Page title: `CredRisk.AI Home`

Lender view:

- title: `Welcome, <name>`;
- metrics: SME Intake, High Priority Queue, Due This Week, Evidence Follow-Up, Operations Queue;
- `Suggested Actions`;
- SME Portal Intake table when submissions exist;
- submitted application selectbox and `Open SME Submission` button;
- quick links to Personal Workspace, LLM Integration, Tutorials, Operations Desk;
- Slack Updates when Slack connected; otherwise Workspace Updates;
- Calendar Today.

SME view:

- welcome message;
- explanation that Home is lender-facing;
- link to `pages/6_SME_Credit_Health.py`;
- stop page execution.

### `pages/6_SME_Credit_Health.py`

Page title: `Loan Intake Portal`

Workflow steps:

```text
1. Company Data
2. Data Connections
3. Credit Health
4. Submit to Lender
```

Top and bottom Previous/Next buttons must move between these steps.

Company Data:

- load/start intake expander;
- fixed sample case dropdown;
- applicant-owned form;
- company profile, loan request, financial snapshot, working-capital amounts;
- five-row `st.data_editor` for forecast plan;
- text areas for loan purpose, current business context, future plan, CEO, CFO, COO;
- save validates forecast rows and derives model-facing fields.

Data Connections:

- checkboxes for PSD2/Open Banking, consent, accounting, registry;
- sample document cases section;
- generated example file save action fills only missing categories;
- upload slots for all document categories;
- small download action beside upload slot when a file exists;
- max file size: 20 MB.

Credit Health before publication:

- no internal score/provisional grade;
- show evidence completeness, runway, stressed DSCR, forecast support;
- application snapshot;
- ways to strengthen the file;
- evidence readiness tab;
- five-year plan tab.

Credit Health after publication:

- auto-focus returning SME to this step once per publication;
- show `YourBank reviewed your credit application`;
- show final reviewed rating, lender decision, published score if disclosed, reviewed timestamp;
- show message from YourBank;
- show downloadable SME evaluation report if attached;
- show applicant-safe post-publication what-if planning.

Submit:

- company identity check;
- loan request check;
- Open Banking consent status;
- evidence connection count;
- five-year plan check;
- lender rating status;
- confirmation checkbox;
- submit disabled until confirmed and forecast plan valid;
- creates `SUB-###`, appends `sme_submission_history`, sets `active_queue_application`, sets `active_intake_source = SME_SUBMISSION_SOURCE`, updates lifecycle to `Submitted to lender review`.

### `pages/1_Personal_Workspace.py`

Page title: `Personal Workspace`

Only lender-side. Main tabs after scoring:

```text
Decision Package
Risk Analysis
AI Output
Case Materials
Audit History
```

Loaded intake:

- read-only tabs: Company Profile, Loan Request, Financial Snapshot, Five-Year Plan, Evidence, Narrative;
- Five-Year Plan tab shows submitted annual rows first, then model-derived summary;
- lender must not edit SME-owned intake.

Scoring:

- `Score Loaded Intake`;
- Random Forest only;
- auto-score submitted SME cases when opened if not already scored;
- keep score history append-only.

AI gate:

- Case Review cannot proceed without a current evaluation package;
- warning copy should tell analyst to use AI first;
- internal report remains private;
- SME report draft is editable at publication.

Publication:

- show model grade, analyst rating, lender decision;
- publication form includes message to SME, SME-facing evaluation report, include-score checkbox;
- on publish, lifecycle status becomes `Rating published`;
- store published grade, decision, message, optional score, report, report source, evaluation package id, timestamp;
- success copy says the reviewed rating is visible in the Loan Intake Portal.

### `pages/5_LLM_Integration.py`

Page title: `LLM Integration`

Requires latest scored case. If absent, show link back to Personal Workspace.

Show:

- Random Forest model baseline;
- risk score, model grade, recommendation, ROC-AUC, recall, balanced accuracy, precision at top decile, estimated total error cost;
- provider radio: Deterministic, OpenAI API, Local server;
- detail-level radio;
- local endpoint/model/token fields when local selected;
- one generation button that creates both internal and SME reports;
- Evaluation Package status and tabs: Internal Lender Report, SME Report Draft;
- saved LLM review runs;
- SHAP Driver Analysis.

### `pages/2_Operations_Desk.py`

Page title: `Operations Desk`

Purpose: synthetic queue workboard separate from SME-submitted intake.

Must show:

- Open Work Items;
- Manual / Compliance;
- Evidence Follow-Up;
- Rejected Today;
- filters;
- queue table;
- selected application detail;
- handoff to Personal Workspace;
- controlled bulk actions.

Queue routing:

```text
E-F -> Compliance review
document_completeness_score < 0.8 -> Request documents
C-D -> Manual review
otherwise -> Ready for approval
```

Alice workload constants:

```text
ALICE_ANALYST = Ms. Cooper
ALICE_MAX_TASKS = 20
ALICE_SAME_DAY_TASKS = 2
ALICE_THIS_WEEK_TASKS = 5
BANK_BASE_INTEREST_RATE = 0.065
```

### `pages/3_Risk_Dashboard.py`

Page title: `Risk Dashboard`

Must show:

- filters by grade, recommendation, industry, region, score;
- metrics: Filtered Applications, Filtered Exposure, Average Risk Score, Review Load;
- grade and decision distributions;
- tabs for review queues, highest-risk applications, live activity;
- selected-case handoff to Personal Workspace;
- live session decisions and analyst review audit trail.

### `pages/4_Model_Insights.py`

Page title: `Model Insights`

Must align with RF-only app:

- Random Forest performance metrics;
- custom portfolio metric;
- confusion matrix;
- A-F grading thresholds;
- governance notes;
- top feature importances;
- research-backed derived signals.

Do not present a live model selector or disabled API preview.

### `pages/7_Profile_Settings.py`

Page title: `Profile & Settings`

Tabs:

```text
Profile
Personal Connected Apps
Admin Controls
```

Manages profile identity, integrations, preferred channel/email app, alerts, digest, dark mode, permission, user type, manager/team fields.

### `pages/8_About.py`

Page title: `About`

Lender-only reference. SME users should see a blocked safe message and links to SME-safe pages.

Tabs:

```text
Scoring Dimensions
Derived Signals
Grade Policy
```

### `pages/9_Support.py`

Page title depends on role:

- SME: `Connect with a YourBank Consultant`
- lender: `Support`

Support requests are local demo records. Do not imply a real support desk was contacted.

### `pages/10_Tutorials.py`

Page title: `Tutorials`

Text-first, role-aware tutorial hub. No generated placeholder screenshots.

SME tutorials must describe application setup, documents/connections, submission/results, consultant support, and the Acronym Guide.

Lender tutorials must describe Home, Personal Workspace, LLM Integration, Operations Desk, Risk Dashboard, Model Insights, Profile, Support, About, and Acronym Guide.

### `pages/11_Acronym_Guide.py`

Page title: `Acronym & Metric Guide`

Tabs:

```text
Acronyms
How to read metrics
```

Role-aware content:

- lender sees internal metric/governance terms;
- SME sees applicant-safe terms only.

## Formatting And UI Rules

Use shared formatting helpers for:

- currency;
- percentages;
- scores;
- integers;
- months;
- European numeric parsing.

Use compact operational layouts. Avoid marketing pages, oversized hero sections, decorative cards, and illustrative filler.

Use `width="stretch"` for Streamlit tables and primary full-width actions.

Use `st.container(border=True)` for important small panels like reviewed-result cards or report boxes.

Use comments where workflow/state/model behavior is non-obvious. Comments should explain why, not restate what the next line does.

## Documentation Contract

Keep these aligned when behavior changes:

- `README.md`
- `DEMO.md`
- `.codex/CODEX.md`
- `pages/10_Tutorials.py`
- `pages/8_About.py`
- `pages/11_Acronym_Guide.py`
- pitchdeck files if the product story changes

README must include:

- simplified start/workflow/clear/end instructions;
- detailed SME -> lender -> SME walkthrough;
- LLM provider setup;
- local data/reset behavior;
- grade mapping;
- verification commands.

## Verification Commands

Required for normal code changes:

```bash
python3 -m compileall -q Home.py pages src tests
python3 -m unittest discover -s tests
git diff --check
git status --short
```

Run the app when local port binding is available:

```bash
streamlit run Home.py
```

Manual end-to-end smoke path:

1. Log in as SME using `DemoUser` and `SME SSO`.
2. Load `Clean evidence` or create `Blank manual intake`.
3. Complete and save Company Data, including five-year plan.
4. Save sample documents or upload files.
5. Submit to lender.
6. Sign out.
7. Log in as lender using `DemoUser` and `YourBank SSO`.
8. Open SME submission from Home or Personal Workspace.
9. Score Loaded Intake.
10. Validate documents.
11. Generate AI output in LLM Integration.
12. Return to Personal Workspace.
13. Complete Case Review.
14. Publish rating/report.
15. Sign out.
16. Log in as SME.
17. Confirm `YourBank reviewed your credit application` result screen.
18. Use Clear Session.
19. Confirm fresh login state and new `demo_session`.

## Non-Regression Checklist

Before handoff, confirm:

- `Home.py` launches.
- login roles and fake SSO work.
- SME navigation is restricted to applicant-safe pages.
- lender navigation includes credit/risk/governance pages.
- sample SME cases load without errors.
- blank manual intake cannot submit without a valid five-year plan.
- sample documents save real bytes and hashes.
- fraudulent documents include red-flag markers.
- submitted SME intake appears in Home and Personal Workspace.
- Personal Workspace intake is read-only.
- Random Forest score appears and no ML selector is exposed.
- AI output is required before Case Review.
- publication creates SME-visible result.
- SME result screen is obvious and uses YourBank language.
- Clear Session logs out and creates a fresh demo session.
- deterministic AI/document paths work offline.
- no `.tmp`, `.venv`, credentials, local profile files, or generated bytecode are staged.
