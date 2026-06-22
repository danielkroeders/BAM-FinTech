# Codex Repository Guide: CredRisk.AI Underwriter Workbench

This is the canonical Codex guide for building, maintaining, and extending this repository. It describes the current application and its durable engineering rules. When this document and executable code disagree, inspect the code and update this document in the same change.

## Product Identity

CredRisk.AI Underwriter Workbench is a multi-page Streamlit demo for SME lending operations.

The main user is Alice Cooper, a credit analyst. The app combines:

- an analyst task queue and daily operating context;
- applicant-first SME loan intake;
- supervised application-risk scoring;
- explicit A-F risk grades and model recommendations;
- deterministic explanations and optional LLM second review;
- case-specific SHAP analysis;
- human final-decision capture and audit history;
- portfolio, model-governance, borrower-health, support, and tutorial views.

The product is decision support. It is not a production underwriting, legal, fraud, or compliance decision engine. Keep these outputs separate everywhere:

1. Applicant-provided data and evidence.
2. Selected supervised-model score, grade, and recommendation.
3. Deterministic or LLM-generated second review.
4. Analyst final decision and notes.
5. Audit and session history.

Never present a model or LLM output as legal certainty or as an automatic final credit decision. High-risk cases require human review before external action.

## Running the App

Python 3.10 or newer is recommended.

Manual launch:

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Windows users can run `Run_App.bat`. It creates `.venv` when needed, installs or updates dependencies, and launches `Home.py`.

`Home.py` is the only application entrypoint. Do not introduce or reference `app.py`.

The app normally opens at `http://localhost:8501`.

## Dependencies and Streamlit Configuration

`requirements.txt` contains:

```text
streamlit
pandas
numpy
scikit-learn
openai
shap
pypdf
```

`.streamlit/config.toml` hides Streamlit's automatic page navigation because navigation is rendered by `src/ui/components.py`. It also defines the light theme:

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

## Repository Structure

```text
.
|-- .codex/
|   `-- CODEX.md
|-- .streamlit/
|   `-- config.toml
|-- Home.py
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
|   `-- 10_Tutorials.py
|-- src/
|   |-- core/
|   |   |-- data_pipeline.py
|   |   |-- modeling.py
|   |   `-- runtime.py
|   |-- features/
|   |   |-- alignment_features.py
|   |   |-- case_workflow.py
|   |   |-- explanations.py
|   |   |-- shap_explanations.py
|   |   `-- workbench_features.py
|   |-- ui/
|   |   `-- components.py
|   `-- utils/
|       |-- demo_persistence.py
|       |-- formatting.py
|       |-- llm_profiles.py
|       `-- table_views.py
|-- data/
|   |-- assets/
|   |-- docs/
|   |-- seed/
|   `-- seeds/
|-- docs/
|   |-- CredRiskAI_Pitchdeck.html
|   |-- CredRiskAI_Pitchdeck.pdf
|   `-- CredRiskAI_Pitchdeck.pptx
|-- README.md
|-- DEMO.md
|-- Run_App.bat
|-- requirements.txt
|-- BP.pdf
`-- FinTech Assignment 2-1.pdf
```

`data/seed` is the canonical generated data directory. `data/seeds` is retained as a compatibility mirror.

`.tmp`, `.venv`, bytecode, local `llm_models` directories, and local pitch-deck speaker notes are ignored. Do not commit generated demo sessions or credentials.

## Shared Page Lifecycle

Every Streamlit page follows this order:

```python
st.set_page_config(...)
bootstrap_state()
render_sidebar()
```

Use `bootstrap_state()` before reading shared state. Use `render_sidebar()` for authentication, theme, navigation, profile controls, onboarding, and demo-state reset.

The sidebar navigation is defined by `NAV_SECTIONS` in `src/ui/components.py`. Update it when adding, removing, or renaming a page.

Use `safe_page_link()` for internal links and `open_application_in_workspace()` when handing a case into Personal Workspace.

## Page Contracts

### `Home.py`

Home is an employee operations console, not a marketing landing page.

It contains:

- the demo login and two-step verification experience through the shared sidebar;
- a welcome header for Alice Cooper;
- personal queue metrics;
- a task selector and handoff into Personal Workspace;
- the current-task table;
- quick links;
- Slack or workspace updates based on profile connections;
- Calendar Today.

The workload metrics are My Open Tasks, High Priority, Due This Week, and Evidence Follow-Up.

### `pages/1_Personal_Workspace.py`

This is the main single-case analyst workflow.

The user can:

- start a selected assigned case;
- start the A2M Logistics example directly;
- use manual entry;
- load a scenario from Example Cases;
- select Random Forest or Logistic Regression;
- complete applicant, financial, forecast, narrative, evidence, and advanced inputs;
- score the application;
- inspect score, evidence, review, and history tabs;
- save a human case review;
- download case summary and credit memo;
- compare similar applications and peers;
- continue to LLM Integration.

Current example scenarios are:

- Custom application
- A2M Logistics Loan
- Low-risk established borrower
- Credit stacking case
- Suspicious transfers
- High country-risk borrower

Input sections are:

- Company Profile
- Loan Request
- Financial Snapshot
- Working Capital Ratios
- Five-Year Plan
- Applicant Narrative
- Executive Context
- Applicant Evidence Checklist
- Advanced Signals

The scored workflow includes:

- application risk score and grade;
- selected model label and recommendation;
- final-decision and review state;
- affordability and stressed DSCR;
- deterministic rationale and rule flags;
- recommended loan terms;
- portfolio monitoring preview;
- model-confidence and governance rows;
- data readiness;
- scenario analysis;
- grouped risk drivers;
- generated five-year forecast;
- applicant and executive context;
- evidence review and calculated signals;
- decision timeline;
- similar historical applications;
- peer benchmark.

Keep hover-help affordances for dense fields and metrics. Preserve European number parsing and formatting.

Case review actions are:

```text
Approve
Reject
Manual Review
Request Documents
Escalate to Compliance
```

Saving an analyst review must not overwrite the model score, model recommendation, or AI review.

### `pages/2_Operations_Desk.py`

This is the team workboard.

It contains:

- open-work, manual/compliance, evidence-follow-up, and rejected-today metrics;
- status, grade, and analyst filters;
- a visible task table;
- controlled bulk rejection;
- selected-case detail;
- handoff to Personal Workspace.

Bulk rejection updates `review_history`, `portfolio_history`, `bulk_final_decisions`, and `bulk_action_history`.

### `pages/3_Risk_Dashboard.py`

This is the portfolio-monitoring surface.

It contains:

- grade, recommendation, industry, region, and score filters;
- filtered application, exposure, average-risk, and review-load metrics;
- grade and decision distributions;
- manual and compliance queues;
- highest-risk applications;
- live session decisions;
- analyst review audit trail;
- selected-case handoff to Personal Workspace.

All displayed results must respond to the active filter set.

### `pages/4_Model_Insights.py`

This is the model-comparison and governance surface.

It contains:

- Random Forest and Logistic Regression selection;
- model comparison;
- configurable metric views;
- a custom portfolio metric builder;
- confusion matrix;
- A-F grading thresholds;
- governance notes;
- global feature importance;
- research-backed derived signals.

Metrics available from each model include:

- accuracy;
- balanced accuracy;
- precision;
- recall;
- F1;
- ROC-AUC;
- average precision;
- Matthews correlation coefficient;
- precision at the top 5%, 10%, and 20%;
- false-positive and false-negative rates;
- predicted review rate;
- estimated review, false-positive, false-negative, and total error costs;
- confusion-matrix counts.

The old Risk Score API Contract Preview is currently commented out. Do not document or present it as a live page feature unless it is re-enabled and verified.

### `pages/5_LLM_Integration.py`

This is the optional AI second-review and case-specific explainability surface.

It requires a previously scored application. When no scored case exists, show a clear link back to Personal Workspace.

The page must:

- show the selected supervised model baseline first;
- show a compact card naming the deterministic model used;
- keep the baseline score, grade, recommendation, and validation metrics visible;
- offer Deterministic, OpenAI API, and Local server providers;
- offer Detailed analyst memo and Concise summary detail levels;
- call external models only after `Run LLM Review`;
- show deterministic fallback output if an external call fails;
- parse `AI review score: NN/100`;
- parse `AI suggested grade: X`;
- normalize the AI score to the shared A-F thresholds;
- compare the AI grade with the selected ML grade;
- retain recent LLM runs for the current demo session;
- show SHAP driver analysis.

The deterministic model card dynamically names Random Forest or Logistic Regression and explains that it produces the baseline before any optional LLM review.

The SHAP helper currently explains the default Random Forest pipeline. If the selected model is Logistic Regression, do not imply that SHAP is explaining the selected Logistic Regression model unless `shap_explanations.py` is deliberately extended.

Hosted OpenAI calls use `OPENAI_API_KEY` from Streamlit secrets or the environment.

Local OpenAI-compatible calls accept:

```text
LOCAL_LLM_BASE_URL
LOCAL_LLM_MODEL
LOCAL_LLM_API_KEY
```

The URL normalizer accepts a server root, `/v1`, or a pasted chat-completions path and resolves it to the OpenAI-compatible `/v1/chat/completions` route.

Local model profiles are handled by `src/utils/llm_profiles.py`:

- save exactly `ip` and `model_name`;
- never write the API token to the profile;
- automatically create the per-user `llm_models` directory;
- load the profile during runtime bootstrap;
- allow `CREDRISK_LLM_MODELS_DIR` as an explicit override.

Default profile locations:

```text
Windows: %LOCALAPPDATA%\CredRiskAI\llm_models\local_server.json
macOS:   ~/Library/Application Support/CredRiskAI/llm_models/local_server.json
Linux:   ${XDG_CONFIG_HOME:-~/.config}/CredRiskAI/llm_models/local_server.json
```

These files are outside the Git checkout. The token field is password-masked and session-only unless supplied through an environment variable. Do not add reversible token scrambling and describe it as encryption.

### `pages/6_SME_Credit_Health.py`

This is a borrower-facing concept preview using the same synthetic scoring logic.

It contains:

- a selectable latest or portfolio case;
- credit-health grade, score, lender view, and runway;
- company snapshot;
- practical next actions;
- what-if changes to growth, FCF margin, cost pressure, evidence, documents, and debt reduction;
- current-versus-scenario comparison;
- peer benchmark;
- evidence sources;
- five-year forecast view.

Frame results as directional ways to improve evidence or resilience, never as promises of approval.

### `pages/7_Profile_Settings.py`

This is the analyst profile and connected-app simulation.

It contains Profile, Personal Apps, and Admin Controls tabs. It manages:

- analyst identity and organization;
- user type, permission, and manager;
- Slack, Teams, Gmail, Outlook, Google Drive, OneDrive, SharePoint, and Zoom simulation;
- preferred channel and email app;
- review alerts and daily digest;
- dark-mode preference;
- controlled editing of access-related fields.

This is a demo profile system, not production identity and access management.

### `pages/8_About.py`

This is the terminology and policy reference.

It contains:

- the decision-support usage boundary;
- searchable scoring-dimension definitions;
- derived-signal definitions;
- A-F grade policy and recommendation mapping.

Keep the language understandable to analysts and bankers.

### `pages/9_Support.py`

This is the simulated support surface.

It contains:

- representative contact cards;
- support request form;
- recent support request history;
- scripted live chat;
- FAQ.

Support requests are demo session records and email drafts. Do not imply that a real support desk was contacted. Never invite users to include passwords, API keys, or sensitive applicant data.

### `pages/10_Tutorials.py`

This is the searchable, text-first learning hub for every application page.

Each tutorial includes:

- slug, title, target page, category, time, and level;
- summary and feature tags;
- learning objectives;
- four step-by-step sections;
- action and tip guidance;
- internal navigation to the live page.

The hub uses query parameters to open individual guides. Keep links in the current browser tab. Tutorials must remain aligned with actual page behavior whenever a feature, label, or workflow changes.

Do not add decorative placeholder screenshots or generated product mockups unless explicitly requested. The current tutorial direction is text-first.

## Core Architecture

### `src/core/data_pipeline.py`

Owns schema, derived features, synthetic data generation, loading, validation, and five-year forecast creation.

Public contracts:

```text
BASE_NUMERIC_COLUMNS
DERIVED_NUMERIC_COLUMNS
NUMERIC_COLUMNS
CATEGORICAL_COLUMNS
TARGET_COLUMN
DEPRECATED_COLUMNS
add_derived_features()
build_forecast_table()
generate_seed_data()
load_seed_data()
ensure_seed_data()
```

The target is `is_fraud`, while the UI generally describes the prediction as an application risk score to fit the wider credit-risk workflow.

`forecast_plan_confidence_score` is deprecated. Drop it when encountered and do not reintroduce it.

If canonical seed data is missing, stale, lacks required columns, or contains placeholder company names, regenerate deterministic data. The normal generator uses 1,200 rows and seed 42.

Derived features cover:

- debt and requested-exposure ratios;
- recent-loan velocity and payment pressure;
- collateral and external-financing pressure;
- financial distress and transaction anomaly;
- company-scale and governance mismatch;
- cash-flow, runway, and cash-conversion pressure;
- forecast aggressiveness and execution;
- interest expense, annual debt service, DSCR, and +2% stress;
- document completeness, quality, and process integrity;
- identity/KYB, working-capital, financial-statement, related-party, and narrative risk.

When adding a model input:

1. Add it to the correct schema list.
2. Populate or derive it consistently.
3. Handle stale seed regeneration.
4. Add input UI or explain why it is system-derived.
5. Update About and Tutorials where user-facing.
6. Update this guide.

### `src/core/modeling.py`

Owns training, metrics, score generation, grade mapping, recommendation mapping, rule flags, and portfolio scoring.

Supported models:

```text
random_forest       -> Random Forest
logistic_regression -> Logistic Regression
```

Default model: `random_forest`.

Both models use a shared scikit-learn preprocessing pipeline:

- median imputation and standard scaling for numeric fields;
- most-frequent imputation and one-hot encoding for categorical fields;
- a stratified 75/25 train/test split with random state 42.

Current classifiers:

```python
RandomForestClassifier(
    n_estimators=220,
    min_samples_leaf=4,
    random_state=42,
    class_weight="balanced",
)

LogisticRegression(
    max_iter=2500,
    class_weight="balanced",
    solver="lbfgs",
)
```

Both output `predict_proba(...)[..., 1]` between 0 and 1.

Feature importance uses Random Forest `feature_importances_` or absolute Logistic Regression coefficients.

### Risk Grade Policy

Use this mapping everywhere:

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

Do not duplicate threshold logic with different values. Reuse the modeling policy or keep any display-only mapping exactly synchronized.

### `src/core/runtime.py`

Owns shared Streamlit bootstrap.

It:

- restores demo state;
- ensures current seed schema and named companies;
- trains or refreshes the two-model bundle;
- initializes shared workflow state;
- loads local LLM profile values;
- reads LLM environment variables;
- persists the serializable demo state.

Default selected model is Random Forest. Invalid saved model keys reset to the default.

### `src/features/case_workflow.py`

Owns:

- demo scenarios;
- analyst review actions;
- case-summary export;
- similar-application calculation.

### `src/features/workbench_features.py`

Owns:

- missing-document and queue-status logic;
- Alice Cooper's workload assignment;
- recommended loan terms;
- portfolio-monitoring preview;
- grouped risk drivers;
- data-source status;
- decision timeline;
- model-confidence rows;
- downloadable credit memo.

Alice's queue contract:

```text
Maximum assigned tasks: 20
Same-day tasks:         2 when available
This-week tasks:        5 when available
Remaining tasks:        next week
Other analysts:         M. van Dijk and S. Jansen
```

Queue routing:

```text
E-F                         -> Compliance review
Document completeness < .8 -> Request documents
C-D                         -> Manual review
Otherwise                   -> Ready for approval
```

### `src/features/alignment_features.py`

Owns:

- what-if scenario transformation;
- scenario comparison;
- peer benchmarking;
- evidence-source coverage;
- borrower action suggestions;
- dormant API payload helpers;
- latest-or-sample case selection.

The API payload helper exists, but the Model Insights UI for it is currently disabled.

### `src/features/explanations.py`

Owns:

- offline deterministic explanation;
- hosted OpenAI explanation;
- local OpenAI-compatible explanation;
- URL normalization;
- visible error state;
- deterministic fallback.

The deterministic explanation includes:

- decision, grade, and risk score;
- applicant context;
- top risk drivers;
- mitigating factors;
- recommended analyst action;
- compliance note.

LLM prompts must use the selected model label, prediction, validation metrics, applicant inputs, and shared grade thresholds. They must prohibit invented facts and legal certainty.

### `src/features/shap_explanations.py`

Owns case-specific SHAP contribution analysis. It currently uses the model bundle's default Random Forest pipeline.

### `src/ui/components.py`

Owns:

- default Alice Cooper profile;
- navigation sections;
- profile merging and saving;
- internal page links and case handoff;
- global light/dark styling;
- demo login and verification;
- login transition;
- first-session tutorial prompt;
- sidebar rendering;
- sign-out and demo-state reset.

Keep shared app chrome here instead of copying it into individual pages.

### Utilities

`src/utils/demo_persistence.py` stores selected JSON-safe session values under:

```text
.tmp/demo_sessions/<demo_session>.json
```

The `demo_session` query parameter reconnects a browser refresh to its local demo state. `.tmp` is ignored by Git.

Do not add secrets or API tokens to `PERSISTED_KEYS`.

`src/utils/formatting.py` provides European-style number and currency formatting and parsing.

`src/utils/table_views.py` centralizes application-table labels and formatting.

`src/utils/llm_profiles.py` stores only the local endpoint/IP and model name outside the repository.

## State and Persistence Rules

Shared state is initialized in `bootstrap_state()`. Important groups include:

- seed data and model bundle;
- score, portfolio, and review histories;
- latest application, prediction, explanation, and review;
- selected supervised model;
- LLM provider, output, source, error, signature, and run history;
- local LLM endpoint, model, token, and saved-setting state;
- bulk-decision state;
- support-ticket history;
- active queue/intake case;
- profile, theme, authentication, and onboarding preferences.

Persist only values listed in `PERSISTED_KEYS`. Model objects and data frames are reconstructed rather than serialized into demo JSON.

When adding state:

1. Initialize it in `bootstrap_state()`.
2. Decide explicitly whether it should survive refresh.
3. Add it to `PERSISTED_KEYS` only if it is JSON-safe and non-secret.
4. Clear or invalidate dependent state when its source case changes.

## Security and Local Data Rules

- Never commit credentials, API tokens, customer data, or secret-bearing config files.
- Use Streamlit secrets or environment variables for hosted credentials.
- Keep manually entered local API tokens session-only.
- Never add API tokens to demo persistence or local model-profile JSON.
- Store reusable local model endpoint and model-name settings outside the checkout.
- Do not use reversible obfuscation as a substitute for secure secret storage.
- All included portfolio and applicant data is synthetic.
- Support and connected-app integrations are simulations.
- Production claims must be framed as future integration paths, not current capabilities.

## UI and Copy Conventions

- Keep a compact operational bank-workbench feel.
- Avoid turning pages into marketing surfaces.
- Prefer plain analyst and banker language.
- Preserve the teal/slate design system and shared theme behavior.
- Use `width="stretch"` for new Streamlit tables, controls, and charts where appropriate.
- Use `st.container(border=True)` for small informational cards.
- Use tabs and expanders to organize dense analysis without hiding essential decisions.
- Keep model recommendation, AI review, and final analyst action visibly distinct.
- Use European formatting helpers instead of hand-formatting monetary values.
- Keep desktop and mobile readability.
- Do not add decorative visuals that do not improve the workflow.

## Documentation and Demo Materials

Maintain these alongside product changes:

- `README.md`: setup, launch, walkthrough, page map, LLM configuration, local profile storage, and grade policy.
- `DEMO.md`: live presentation sequence and safety notes.
- `pages/10_Tutorials.py`: detailed user guidance for every page.
- `pages/8_About.py`: field, derived-signal, and grade definitions.
- `data/docs/fraud_research.md`: research grounding.
- pitch-deck HTML/PDF/PPTX when a product change affects the presentation story.

Avoid documenting commented-out or aspirational UI as if it is currently live.

## Change Discipline

Before editing:

- inspect the relevant page and shared helper modules;
- check `git status --short`;
- preserve unrelated user changes;
- look for duplicated labels or policies in About, Tutorials, README, DEMO, and this file.

When changing scoring:

- keep both models functional;
- preserve 0-1 probability output;
- keep grade thresholds synchronized;
- verify selected-model propagation between pages;
- update explanations and governance copy.

When changing a workflow:

- update session initialization;
- update persistence only when appropriate;
- keep handoffs between Home, Operations Desk, Risk Dashboard, Personal Workspace, SME Credit Health, and LLM Integration intact;
- update the matching tutorial.

When changing LLM behavior:

- retain deterministic offline operation;
- do not make external calls before explicit user action;
- retain visible fallback errors;
- keep API tokens out of disk persistence;
- preserve the distinction between baseline model and AI second review.

## Verification

Use the available interpreter (`python3` on macOS/Linux, often `python` inside the Windows virtual environment).

Syntax check without importing the app:

```bash
python3 - <<'PY'
from pathlib import Path

paths = [Path("Home.py"), *Path("pages").glob("*.py"), *Path("src").rglob("*.py")]
for path in paths:
    compile(path.read_text(encoding="utf-8"), str(path), "exec")
print(f"syntax ok: {len(paths)} files")
PY
```

Model and queue smoke test:

```bash
python3 - <<'PY'
from src.core.data_pipeline import ensure_seed_data
from src.core.modeling import train_model
from src.features.workbench_features import build_application_queue

seed = ensure_seed_data()
bundle = train_model(seed["applications"])
assert set(bundle.models) == {"random_forest", "logistic_regression"}

sample = seed["applications"].iloc[0].to_dict()
for key in bundle.models:
    prediction = bundle.score_one(sample, model_key=key)
    assert 0 <= prediction["fraud_probability"] <= 1
    assert prediction["model_key"] == key

    queue = build_application_queue(bundle, seed["applications"], model_key=key)
    alice = queue[queue["assigned_analyst"].eq("Ms. Cooper")]
    assert len(alice) <= 20
    assert alice["sla"].eq("Same day").sum() <= 2
    assert alice["sla"].eq("This week").sum() <= 5

print("model and queue smoke ok")
PY
```

Local LLM profile smoke test:

```bash
tmp_dir="$(mktemp -d)"
CREDRISK_LLM_MODELS_DIR="$tmp_dir/llm_models" python3 - <<'PY'
import json
from src.utils.llm_profiles import load_local_llm_profile, save_local_llm_profile

path = save_local_llm_profile("http://localhost:1234/v1", "local-model")
payload = json.loads(path.read_text(encoding="utf-8"))
assert payload == {"ip": "http://localhost:1234/v1", "model_name": "local-model"}
assert load_local_llm_profile() == payload
assert "token" not in path.read_text(encoding="utf-8").lower()
print("local profile smoke ok")
PY
```

For UI changes, use `streamlit.testing.v1.AppTest` when practical and verify the affected authenticated state and conditional controls. Then run:

```bash
git diff --check
git status --short
```

Run the full app with `streamlit run Home.py` for final visual verification when the change affects layout, navigation, dialogs, forms, theme, or cross-page state.

## Non-Regression Checklist

Before handing off a material change, confirm:

- Home still launches from `Home.py`.
- Authentication and sidebar navigation still work.
- Both supervised models train and score.
- A-F thresholds and recommendations remain consistent.
- A case can move from a queue into Personal Workspace.
- Scoring populates the latest application and prediction.
- Analyst review remains separate from model and AI output.
- Risk Dashboard and Operations Desk reflect session decisions.
- SME Credit Health can use the latest scored case.
- LLM Integration works deterministically without credentials.
- External LLM calls require explicit user action.
- Local model profiles contain only endpoint/IP and model name.
- Tutorials and user-facing documentation match the live app.
- No secrets or generated demo-session files are added to Git.
