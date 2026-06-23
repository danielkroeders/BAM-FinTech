# CredRisk.AI Underwriter Workbench

CredRisk.AI Underwriter Workbench is an SME lending workspace. It gives credit analysts a live task view, application scoring, credit and anomaly signals, A-F grading, operational recommendations, explanations, and analyst review history.

This is not a production underwriting, compliance, or legal decision system. High-risk outcomes are framed as requiring human compliance review.

## Setup

Python 3.10+ is recommended.

## Run automatically on Windows

For Windows users, double-click:

```text
Run_App.bat
```

The launcher creates a local `.venv`, installs dependencies from `requirements.txt`, and starts the Streamlit app. Note, this process may take a few minutes. Its therefore suggested to run it manually, if possible. 

## Run manually through a terminal

```bash
pip install -r requirements.txt
streamlit run Home.py
```

The app prepares a local portfolio on first run.

The demo login screen offers a lender-analyst account and an SME-company account, followed by a password step and a six-digit verification code.
The lender account opens the underwriting workspace. The SME account opens the company portal for entering company data, managing simulated data connections, reviewing credit health, and submitting the application to lender review.
The sidebar includes a dark-mode toggle, and the same preference can be saved from Profile & Settings.
During a local demo, temporary page state is restored after browser refresh through a local `.tmp/demo_sessions` file keyed by the `demo_session` URL parameter. Use `Clear Demo State` in the sidebar to reset it.

## Walkthrough

For a full presentation runbook, see `DEMO.md`.
For the research grounding behind the risk ratios, cash-flow signals, anomaly measures, and detection measures, see [`data/docs/fraud_research.md`](data/docs/fraud_research.md).

1. Use the `SME company` demo account to enter company and loan data, choose simulated PSD2/accounting/registry connections, upload real local application files, and submit the application.
2. Sign out and use the `Lender analyst` account.
3. Open `Personal Workspace`, score the submitted file, and inspect the immutable model grade, recommendation, evidence, and explanation.
4. Open `LLM Integration` and generate the evaluation package: a private internal report plus an applicant-safe SME report draft.
5. Open Case Review, choose the lender action, set a separate analyst rating, and record the rationale for any difference from the model.
6. Review or edit the SME report draft, then publish the rating and attached report. The numerical score remains private unless the lender explicitly includes it.
7. Sign back in as the SME to view the published rating, lender message, and downloadable evaluation report.
8. Use `Operations Desk`, `Risk Dashboard`, and `Model Insights` to demonstrate operations, monitoring, and governance.

## Optional LLM Providers

The app works without an external LLM by using deterministic explanations. The supervised ML layer can score with Random Forest or Logistic Regression, both returning a continuous 0-1 application risk score. Hosted or local LLMs can act as a second reviewer on the LLM Integration page and generate two persisted outputs: a private detailed lender report and an applicant-safe SME report draft. The lender reviews the SME draft and publishes the exact approved copy with the final rating.

For hosted explanations, set `OPENAI_API_KEY` in Streamlit secrets or the environment, then choose `OpenAI API` on the LLM Integration page and click `Generate Internal + SME Reports`.

For a local model, score an application first, open LLM Integration, choose `Local server`, enter the local endpoint/model/token, and click `Generate Internal + SME Reports`. You can save the endpoint and model name for future local runs. The profile is stored outside the Git repository in the operating system's user configuration area:

- Windows: `%LOCALAPPDATA%\CredRiskAI\llm_models\local_server.json`
- macOS: `~/Library/Application Support/CredRiskAI/llm_models/local_server.json`
- Linux: `${XDG_CONFIG_HOME:-~/.config}/CredRiskAI/llm_models/local_server.json`

Only the endpoint/IP and model name are written. API tokens are not saved by the app; they remain in the current Streamlit session unless provided separately through an environment variable. The storage folder can be overridden with `CREDRISK_LLM_MODELS_DIR`.

Defaults:

- `LOCAL_LLM_BASE_URL`: `http://localhost:1234/v1`
- `LOCAL_LLM_MODEL`: `local-model`
- `LOCAL_LLM_API_KEY`: `local`

The local path works with tools that expose OpenAI-style chat completions, such as LM Studio or Ollama's `/v1` endpoint.
You may enter either the server root, such as `http://localhost:1234`, or the `/v1` base URL. The app normalizes this and calls `/v1/chat/completions` only after you generate the reports. If a local call fails, the affected report uses its deterministic fallback and the page shows the error.

## Pages

- `Home.py`: employee homepage with current tasks, Slack Updates, and Calendar Today.
- `pages/1_Personal_Workspace.py`: score one SME loan application, review evidence, save a final decision, and store the latest decision in session state.
- `pages/6_SME_Credit_Health.py`: role-aware SME company portal for data entry, simulated evidence connections, application readiness, lender submission, and lender-controlled publication of reviewed ratings.
- `pages/2_Operations_Desk.py`: team workboard for incoming applications, evidence gaps, SLA status, and case handoff.
- `pages/3_Risk_Dashboard.py`: grade distribution, decision mix, highest-risk applications, live session decisions, and review audit history.
- `pages/4_Model_Insights.py`: model metrics, confusion matrix, feature importances, grading thresholds, derived signal design, and API contract preview.
- `pages/5_LLM_Integration.py`: creates a persisted internal lender evaluation and separate applicant-safe SME report draft for the latest scored request.
- `pages/7_Profile_Settings.py`: analyst profile, personal connected apps such as Slack/Teams, Gmail/Outlook, Drive/OneDrive/SharePoint, Zoom, user type, permissions, and team manager settings.
- `pages/10_Tutorials.py`: searchable panel-based learning hub with detailed guides and feature maps for every application page.
- `pages/8_About.py`: definitions for workspace scoring dimensions and risk grade interpretation.
- `pages/9_Support.py`: representative email contacts, support request form, scripted live chat, and FAQ.

## Local application file storage

Files uploaded through the SME company portal are genuinely written to the
local `.tmp/sme_documents/<demo-session>/<application>/` vault. The app stores
the original filename, document category, MIME type, byte size, save timestamp,
and SHA-256 hash in a manifest. The lender can download the same saved bytes
from Personal Workspace.

The vault survives page refreshes, sign-out, and role changes within the same
demo-session link. It is excluded from Git and is deleted when `Clear Demo
State` is used. PSD2, accounting, and registry connections remain simulated
until real providers and credentials are configured.

## A-F Risk Grade Mapping

| Grade | Application risk score | Action |
| --- | --- | --- |
| A | `Below 0.15` | Approve |
| B | `0.15 to 0.28` | Approve |
| C | `0.28 to 0.42` | Manual Review |
| D | `0.42 to 0.58` | Manual Review |
| E | `0.58 to 0.74` | Reject |
| F | `Above 0.74` | Reject |

## License and copyright

Copyright (c) 2026 Daniël Kroeders and Joost Gaasbeek.

This project is released under the [MIT License](LICENSE). Research publications
and course materials included for academic context remain the property of their
respective authors and publishers.
