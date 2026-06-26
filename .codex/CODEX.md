# Codex Repository Guide: CredRisk.AI Underwriter Workbench

This is the working guide for future Codex sessions in this repository. Treat it as the first orientation document before making changes. If this file and the live code disagree, inspect the code, update the implementation, and refresh this guide in the same change.

## Product Shape

CredRisk.AI Underwriter Workbench is a local multi-page Streamlit demo for SME lending.

The current demo workflow is:

1. SME creates and submits a loan intake.
2. Lender analyst reviews the locked submitted snapshot.
3. Lender publishes a reviewed rating and applicant-safe report.
4. SME returns to view the published result.

The app is decision support only. It is not a production underwriting, legal, compliance, or fraud-decision system. Keep these records separate throughout the app:

- applicant-provided data and evidence;
- Random Forest model score, grade, and recommendation;
- deterministic or optional AI second-review output;
- analyst final action, rating, rationale, and audit history;
- SME-facing published rating, message, and report.

Do not present model, AI, or document-validation output as legal certainty or as an automatic final credit decision.

## Run Contract

Use Python 3.10+.

Manual run:

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Windows users can run:

```text
Run_App.bat
```

`Home.py` is the only app entrypoint. Do not add or document an `app.py` entrypoint.

The app normally runs at:

```text
http://localhost:8501
```

## Current Login Contract

The demo login uses two roles:

- `SME company`
- `Lender analyst`

The username field is `DemoUser`. The role-specific SSO buttons are:

- SME page: `SME SSO`
- bank/lender page: `YourBank SSO`

The password and six-digit verification step are demo controls. Any values are accepted.

## Main Workflow

### SME Side

The SME uses `pages/6_SME_Credit_Health.py`, shown as `Loan Intake Portal`.

The SME can:

- load clean, neutral, risky, fraudulent, ambiguous, or blank manual intake cases;
- enter company profile, loan request, financial snapshot, working-capital amounts, loan purpose, current/future context, and executive context;
- fill a required five-row five-year plan;
- simulate PSD2/Open Banking, accounting, registry/KYB, and document connections;
- save fictional sample evidence files into the local document vault;
- upload local evidence files;
- submit a locked snapshot to lender review;
- later view the lender-published rating and report.

The five-year plan field is `forecast_plan_rows`.

Shape:

```python
[
    {
        "forecast_year": 1,
        "projected_revenue": 0.0,
        "projected_employees": 1,
        "projected_free_cash_flow": 0.0,
        "projected_debt": 0.0,
    },
    ...
]
```

Rules:

- exactly five rows;
- years exactly `1` through `5`;
- revenue and debt must be `>= 0`;
- employees must be `>= 1`;
- free cash flow is required and may be negative.

The model still consumes derived legacy fields. Derive these from year 5 of the submitted plan:

- `forecast_revenue_year5`
- `forecast_employees_year5`
- `forecast_fcf_year5`
- `planned_debt_reduction_amount`
- `forecast_revenue_cagr`
- `forecast_employee_cagr`
- `forecast_fcf_margin_year5`
- `planned_debt_reduction_pct`

Do not reintroduce the old SME form pattern where the applicant only enters four year-5 targets.

### Lender Side

The lender uses `Home.py`, `pages/1_Personal_Workspace.py`, `pages/5_LLM_Integration.py`, and supporting dashboard/governance pages.

The submitted SME intake is read-only for the lender. If applicant data is wrong, the SME must update and resubmit from the Loan Intake Portal.

The lender flow is:

1. Open the submitted SME case from Home or Personal Workspace.
2. Review the locked intake snapshot.
3. Score the case using the Random Forest baseline.
4. Validate saved documents on the lender side.
5. Open LLM Integration and generate the AI output package.
6. Return to Personal Workspace and complete Case Review.
7. Publish the reviewed rating, message, and SME-safe report.

Case Review is intentionally gated behind AI output for the assignment workflow. If no AI package exists, the UI should say clearly that the analyst must use AI first.

## Sample Evidence Cases

Sample cases are loaded in the SME portal, not Personal Workspace.

Keep these case types available:

- `Clean evidence`: coherent evidence, steady growth, improving FCF, debt decreasing.
- `Neutral evidence`: modest dip/recovery and controlled growth.
- `Risky evidence`: lumpy growth, weak or negative early FCF, slow debt reduction.
- `Fraudulent evidence`: aggressive jumps, unsupported FCF improvement, inconsistent debt story, and red-flag wording in generated documents.
- `Ambiguous evidence`: volatile but not automatically bad.
- `Blank manual intake`: empty applicant path requiring user input before submission.

Forecast-support sample CSVs should contain annual five-year rows matching the submitted plan fields plus an assumptions/evidence note. Fraudulent forecast-support files should contain year-level contradiction text that deterministic document validation can surface.

## Model Contract

The user-facing app is Random Forest only. Do not expose an ML model selector in the lender or SME workflow.

The current model bundle may still contain historical support code for other supervised models. Treat Random Forest as the default and visible baseline unless the user explicitly asks to restore model comparison.

Risk score means application risk probability on a 0-1 scale.

A-F mapping:

```text
A: score < 0.15
B: score < 0.28
C: score < 0.42
D: score < 0.58
E: score < 0.74
F: score >= 0.74
```

Recommendations:

```text
A-B -> Approve
C-D -> Manual Review
E-F -> Reject
```

Keep the score, model grade, analyst rating, and published rating visibly distinct.

## Repository Structure

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
data/
  docs/
  seed/
docs/
  CredRiskAI_Pitchdeck.html
  CredRiskAI_Pitchdeck.pdf
  CredRiskAI_Pitchdeck.pptx
tests/
README.md
DEMO.md
requirements.txt
Run_App.bat
```

`.tmp/`, `.venv/`, bytecode, local LLM profile folders, and generated demo files are not source artifacts. Do not commit them.

## Page Contracts

### `Home.py`

Home is the lender employee homepage, not a marketing page.

It shows:

- welcome context for the lender analyst;
- suggested actions;
- SME Portal Intake entries;
- operations queue indicators;
- Slack/workspace updates;
- calendar context;
- links into Personal Workspace and Operations Desk.

SME-submitted rows must hand off the exact submitted snapshot into Personal Workspace using `SME_SUBMISSION_SOURCE`.

### `pages/1_Personal_Workspace.py`

This is the lender single-case workspace.

It must:

- load SME-submitted snapshots as read-only intake;
- show the submitted annual five-year plan table when available;
- keep legacy generated forecast fallback for older sessions without `forecast_plan_rows`;
- score with the Random Forest baseline;
- show evidence, risk analysis, decision package, AI output, case materials, and audit history;
- require AI output before final Case Review;
- keep document validation lender-side;
- publish only applicant-safe report text to the SME lifecycle record.

Do not add editable intake fields for SME-owned data here.

### `pages/2_Operations_Desk.py`

This is the synthetic queue workboard for non-SME demo operations.

It covers:

- queue filtering;
- evidence gaps;
- SLA and routing visibility;
- bulk actions;
- handoff into Personal Workspace.

Keep it separate from the SME-submitted intake list so open tasks and submitted SME cases do not look like the same object.

### `pages/3_Risk_Dashboard.py`

This is portfolio monitoring.

It covers:

- filtered portfolio metrics;
- grade and decision distributions;
- live session decisions;
- highest-risk cases;
- review audit history.

Displayed results should respond to active filters.

### `pages/4_Model_Insights.py`

This is model governance and explanation.

It should align with the RF-only app surface:

- Random Forest baseline metrics;
- confusion matrix or model quality views;
- A-F thresholds;
- feature importance;
- derived signal explanations;
- governance notes.

Do not document a disabled API preview or hidden model selector as live behavior.

### `pages/5_LLM_Integration.py`

This creates the AI evaluation package for the latest scored case.

It must:

- work deterministically without external credentials;
- support explicit OpenAI API and local OpenAI-compatible calls only after a button click;
- show the supervised Random Forest baseline separately from AI output;
- generate a private internal lender report and a separate applicant-safe SME report draft;
- persist the package by case/signature so Personal Workspace can require it before Case Review.

Do not save API tokens to disk.

### `pages/6_SME_Credit_Health.py`

This is the SME Loan Intake Portal.

It must:

- block lender users from editing SME intake;
- load sample cases on the SME side;
- support blank manual intake;
- require the five-row five-year plan before save/submission;
- save sample/generated files through the same document vault as uploads;
- submit a locked application snapshot to lender review;
- show readiness before publication;
- show published rating/report after lender publication;
- avoid exposing internal lender probabilities, provisional grades, AI scores, or validation metrics to the SME.

### `pages/7_Profile_Settings.py`

This is profile and connected-app simulation.

It manages user profile, role, permissions, manager/team fields, Slack/Teams, email, storage, Zoom, digest, alerts, and dark-mode preference.

### `pages/8_About.py`

This is lender-only reference material for scoring dimensions, derived ratios, grade policy, and recommendation mapping.

If opened by an SME profile, it should block internal content and route the user back to SME-safe pages.

### `pages/9_Support.py`

This is role-aware support.

Lenders see platform support language. SMEs see YourBank consultant-support language. Support requests are local demo records, not real support tickets.

### `pages/10_Tutorials.py`

This is the text-first tutorial hub.

Keep it aligned with live page behavior and current labels. Do not add generated placeholder screenshots unless explicitly requested.

### `pages/11_Acronym_Guide.py`

This is the role-aware glossary.

SMEs should see applicant-safe language. Lenders can see internal metric and governance explanations.

## Core Modules

### `src/core/runtime.py`

Every page should call:

```python
st.set_page_config(...)
bootstrap_state()
render_sidebar()
```

`bootstrap_state()` restores local demo state, ensures seed data and model bundle, initializes workflow stores, and loads local LLM profile values.

### `src/core/data_pipeline.py`

Owns schema, generated seed data, derived features, forecast validation, forecast table rendering, and model-facing feature preparation.

Important forecast helpers:

- `validate_forecast_plan_rows()`
- `forecast_metrics_from_plan_rows()`
- `build_forecast_table()`

`build_forecast_table()` should return submitted `forecast_plan_rows` exactly when valid. For older data without those rows, keep the generated fallback.

### `src/core/modeling.py`

Owns training, metrics, scoring, grade mapping, recommendations, and rule flags.

The visible workflow uses Random Forest. Keep any underlying compatibility code from leaking into app copy unless intentionally exposed.

### `src/utils/demo_persistence.py`

Stores JSON-safe local demo state in:

```text
.tmp/demo_sessions/<demo_session>.json
```

The `demo_session` query parameter reconnects refreshes to local demo state.

`Clear Session` must:

- delete the active demo-session JSON file;
- delete the active local SME document vault;
- create a new `demo_session` id;
- set authentication to false;
- return the app to login state.

Do not add secrets, API keys, or model objects to persisted state.

### `src/utils/document_storage.py`

Owns local saved document bytes and manifests under:

```text
.tmp/sme_documents/<demo_session>/<application>/
```

The lender should download the same bytes the SME saved. Do not fake evidence flags without saved bytes.

### `src/utils/document_examples.py`

Generates fictional CSV sample evidence.

Keep generated files:

- synthetic;
- category-specific;
- realistic enough for validation demos;
- aligned with the current submitted intake fields;
- saved through `document_storage.py` when the SME chooses to save examples.

### `src/features/document_validation.py`

Owns lender-side deterministic and optional AI document checks.

Validation is triage/classification support, not proof of authenticity. Hosted/local AI calls should use bounded previews and metadata, not full binary documents.

### `src/utils/llm_profiles.py`

Stores local endpoint/IP and model name outside the repository. It must not store tokens.

Default profile locations:

```text
Windows: %LOCALAPPDATA%\CredRiskAI\llm_models\local_server.json
macOS:   ~/Library/Application Support/CredRiskAI/llm_models/local_server.json
Linux:   ${XDG_CONFIG_HOME:-~/.config}/CredRiskAI/llm_models/local_server.json
```

`CREDRISK_LLM_MODELS_DIR` may override the folder.

## State Rules

When adding state:

1. Initialize it in `bootstrap_state()`.
2. Decide whether it should survive refresh.
3. Add it to `PERSISTED_KEYS` only if it is JSON-safe and non-secret.
4. Clear or invalidate dependent state when the source case changes.
5. Make reset behavior explicit if Clear Session should remove it.

Keep these boundaries:

- model/data caches are reconstructed, not persisted as JSON;
- local API tokens are session-only;
- local LLM endpoint/model profile is outside the repo;
- demo documents live under `.tmp/sme_documents`;
- demo session JSON lives under `.tmp/demo_sessions`.

## UI And Copy Rules

- Build the actual workflow screen, not a landing page.
- Use compact operational bank-workbench layouts.
- Keep SME language applicant-safe.
- Keep lender language clear but not legalistic.
- Prefer tabs/expanders for dense workflow surfaces.
- Keep model recommendation, AI review, analyst action, and published rating distinct.
- Use helper formatting functions for money, percentages, months, integers, and scores.
- Add comments to Python code where they help a new reader understand non-obvious workflow, state, model, or validation logic.
- Do not add decorative visuals that do not improve the workflow.

## Documentation Rules

Update these when behavior changes:

- `README.md`
- `DEMO.md`
- `.codex/CODEX.md`
- `pages/10_Tutorials.py`
- `pages/8_About.py`
- `pages/11_Acronym_Guide.py`
- pitchdeck files when the product story changes

Avoid documenting commented-out or aspirational UI as live behavior.

## Verification

Use:

```bash
python3 -m compileall -q Home.py pages src tests
python3 -m unittest discover -s tests
git diff --check
git status --short
```

For workflow or UI changes, also run the app when local port binding is available:

```bash
streamlit run Home.py
```

Manual workflow smoke path:

1. Log in as SME.
2. Load a sample or blank intake.
3. Save company data with a complete five-year plan.
4. Save or upload evidence.
5. Submit to lender.
6. Log in as lender.
7. Open the submitted case.
8. Generate AI output.
9. Complete Case Review.
10. Publish rating/report.
11. Log back in as SME and view the published result.
12. Use Clear Session and verify the app returns to login with a fresh `demo_session`.

## Non-Regression Checklist

Before handing off a material change, confirm:

- `Home.py` still launches the app.
- Authentication and role routing still work.
- SME users can access Loan Intake Portal and cannot access lender-only internals.
- Lender users can open submitted SME snapshots but cannot edit SME intake data.
- Five-year plan rows are required on SME save/submission.
- Blank manual intake cannot be submitted with empty plan rows.
- Sample evidence cases load without errors.
- Fraudulent sample documents include detectable red-flag wording.
- Personal Workspace requires AI output before Case Review.
- Publication returns an applicant-safe result to the SME.
- Clear Session deletes local demo state, logs out, and starts a new session id.
- Deterministic LLM/document paths work without external credentials.
- No generated `.tmp` files, credentials, or local profile JSON are staged.
