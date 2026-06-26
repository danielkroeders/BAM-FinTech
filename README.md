# CredRisk.AI Underwriter Workbench

CredRisk.AI Underwriter Workbench is a local Streamlit demo for SME lending. It combines an applicant-owned Loan Intake Portal, a lender Personal Workspace, Random Forest application-risk scoring, document validation, optional AI review, analyst publication, and an applicant-facing returned rating.

This is a decision-support demo for academic and product exploration. It is not a production underwriting, legal, compliance, or fraud-decision system.

## Simplified Walkthrough

### Start The App

Python 3.10+ is recommended.

Windows:

```text
Run_App.bat
```

Manual terminal run:

```bash
pip install -r requirements.txt
streamlit run Home.py
```

The app normally opens at `http://localhost:8501`.

### Demo Workflow

1. Log in as `SME company` with username `DemoUser`.
2. Use `SME SSO`, enter any password, then enter any six-digit verification code.
3. Open `Loan Intake Portal`.
4. Load a sample intake or choose `Blank manual intake`.
5. Complete the company data, including the required five-row five-year plan.
6. Save or upload evidence documents, then submit the application to lender review.
7. Sign out and log in as `Lender analyst` with `YourBank SSO`.
8. Open the submitted case from `Home` or `Personal Workspace`.
9. Review the locked intake, validate documents, generate the AI output, complete Case Review, and publish the lender rating/report.
10. Sign out and log back in as `SME company` to view the published outcome.

### Clear Session

Use `Clear Session` at the bottom-left sidebar. Confirm the warning checkbox and click `Clear`.

This removes local demo-session state, saved SME documents, sample evidence files, lender reviews, AI outputs, validation results, support tickets, and login state. It also creates a new local `demo_session` link and sends you back to the login screen.

### End The Instance

To stop the running app, return to the terminal where Streamlit is running and press:

```text
Control-C
```

Close the browser tab after the terminal process has stopped.

## Detailed Walkthrough

### 1. Login And Roles

The login screen has two demo roles:

- `SME company`: applicant-side data entry, evidence upload, submission, and published-rating view.
- `Lender analyst`: bank-side case review, scoring, document validation, AI output, decision recording, and publication.

Use username `DemoUser`. The SSO buttons are role-specific:

- SME login: `SME SSO`
- Bank login: `YourBank SSO`

The password and six-digit verification code are demo controls; any values are accepted.

### 2. SME Loan Intake Portal

The SME owns the intake. The lender does not edit applicant data.

In `Loan Intake Portal`, the SME can:

- load prepared evidence cases: clean, neutral, risky, fraudulent, ambiguous, or blank manual intake;
- enter company profile, loan request, financial snapshot, working-capital amounts, business context, and executive context;
- complete a required five-year plan with one row per year for revenue, employees, free cash flow, and remaining debt;
- simulate PSD2/Open Banking, accounting, registry/KYB, and document connections;
- save generated fictional CSV evidence examples into the local document vault;
- upload local evidence files;
- review credit-health readiness before lender submission;
- submit a locked snapshot to lender review.

The five-year plan is stored as annual submitted rows. The app derives the older model-facing year-5 and CAGR fields from that submitted table so the Random Forest model remains compatible.

### 3. Sample Evidence Cases

The sample cases live on the SME side because the SME creates the intake:

- `Clean evidence`: complete package, stable growth, improving cash flow, and gradually declining debt.
- `Neutral evidence`: modest dip and recovery, then controlled growth.
- `Risky evidence`: lumpy growth, weak or negative early cash flow, and slow debt reduction.
- `Fraudulent evidence`: aggressive jumps, unsupported cash-flow improvement, debt-story contradictions, and red-flag wording in generated documents.
- `Ambiguous evidence`: volatile plan and mixed evidence without being clearly fraudulent.
- `Blank manual intake`: empty manual entry path requiring the user to fill the application and five-year plan.

Generated documents are fictional CSV files for financial statements, bank statements, tax returns, ownership/KYB, and forecast support. Forecast-support examples contain annual five-year plan rows.

### 4. Lender Personal Workspace

After submission, the lender opens the SME-submitted file from `Home` or `Personal Workspace`.

The lender view treats the intake as read-only. The analyst can:

- inspect the locked company profile, loan request, financial snapshot, five-year plan, applicant narrative, executive context, and evidence checklist;
- score the submitted case with the Random Forest baseline;
- review application risk score, A-F grade, model recommendation, repayment metrics, DSCR, stressed DSCR, risk drivers, and interpretation columns;
- validate saved SME documents using deterministic local checks and optional explicit AI assistance;
- generate the required AI output in `LLM Integration`;
- complete Case Review only after AI output exists;
- choose lender action, analyst rating, internal note, and adjustment rationale;
- publish a lender-reviewed rating, message, and applicant-safe SME evaluation report.

The model score, AI output, analyst review, and published SME report are kept separate for auditability.

### 5. LLM Integration

The app works without external AI. Deterministic output is available by default.

Optional providers:

- `OpenAI API`: requires `OPENAI_API_KEY` in Streamlit secrets or the environment.
- `Local server`: works with OpenAI-compatible local endpoints such as LM Studio or Ollama `/v1`.

Local settings can save only:

- endpoint/IP;
- model name.

API tokens are not saved to disk. They remain session-only unless supplied through environment variables.

Default local profile locations:

- Windows: `%LOCALAPPDATA%\CredRiskAI\llm_models\local_server.json`
- macOS: `~/Library/Application Support/CredRiskAI/llm_models/local_server.json`
- Linux: `${XDG_CONFIG_HOME:-~/.config}/CredRiskAI/llm_models/local_server.json`

Override with:

```bash
CREDRISK_LLM_MODELS_DIR=/path/to/local/profile/folder
```

### 6. SME Return Flow

After the lender publishes, log back in as `SME company`.

The SME can see:

- published lender rating;
- lender decision label;
- lender message;
- downloadable SME evaluation report if attached;
- applicant-safe credit-health and what-if planning views.

Internal lender details such as provisional scores, AI scores, validation metrics, and private notes remain lender-side.

## Page Map

- `Home.py`: employee homepage with SME Portal Intake, suggested actions, Slack/workspace updates, and calendar context.
- `pages/1_Personal_Workspace.py`: lender single-case review, scoring, document validation, AI-output gate, analyst review, and publication.
- `pages/2_Operations_Desk.py`: synthetic queue workboard for non-SME demo queue cases, evidence gaps, SLA status, and bulk actions.
- `pages/3_Risk_Dashboard.py`: portfolio monitoring, grade distribution, review history, and live session decisions.
- `pages/4_Model_Insights.py`: Random Forest performance, feature importance, grade thresholds, and derived-signal explanations.
- `pages/5_LLM_Integration.py`: deterministic, hosted, or local AI evaluation package generation.
- `pages/6_SME_Credit_Health.py`: SME-only Loan Intake Portal, data connections, document uploads, submission, and published results.
- `pages/7_Profile_Settings.py`: profile, connected-app simulation, permissions, and dark-mode preference.
- `pages/8_About.py`: lender-only scoring and policy reference.
- `pages/9_Support.py`: role-aware lender support and SME consultant-support simulation.
- `pages/10_Tutorials.py`: text-first role-aware tutorials.
- `pages/11_Acronym_Guide.py`: role-aware acronym and metric guide.

## Local Data And Reset Behavior

The app writes local demo state under `.tmp/`.

Important paths:

- `.tmp/demo_sessions/<demo_session>.json`: refresh-safe session state.
- `.tmp/sme_documents/<demo_session>/<application>/`: saved SME uploads and generated sample evidence.

Both paths are ignored by Git.

`Clear Session` deletes the active local demo-session file and document vault, creates a fresh `demo_session` token, logs the user out, and returns the browser to a new login-state demo.

To fully stop the instance, press `Control-C` in the Streamlit terminal.

## A-F Risk Grade Mapping

| Grade | Application risk score | Model recommendation |
| --- | --- | --- |
| A | Below `0.15` | Approve |
| B | `0.15` to `<0.28` | Approve |
| C | `0.28` to `<0.42` | Manual Review |
| D | `0.42` to `<0.58` | Manual Review |
| E | `0.58` to `<0.74` | Reject |
| F | `0.74` and above | Reject |

## Verification

Useful local checks:

```bash
python3 -m compileall -q Home.py pages src tests
python3 -m unittest discover -s tests
git diff --check
```

Run the full app for visual workflow validation:

```bash
streamlit run Home.py
```

For a presentation runbook, see [`DEMO.md`](DEMO.md). For the research grounding behind risk ratios, fraud signals, cash-flow signals, and detection measures, see [`data/docs/fraud_research.md`](data/docs/fraud_research.md).

## License And Copyright

Copyright (c) 2026 Daniel Kroeders and Joost Gaasbeek.
