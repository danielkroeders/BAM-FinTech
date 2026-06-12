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

The launcher creates a local `.venv`, installs dependencies from `requirements.txt`, and starts the Streamlit app.

## Run manually through a terminal

```bash
pip install -r requirements.txt
streamlit run Home.py
```

The app prepares a local portfolio on first run.

## Walkthrough

For a full presentation runbook, see `DEMO.md`.
For the research grounding behind the risk ratios, cash-flow signals, anomaly measures, and detection measures, see `docs/fraud_research.md`.

1. Start on `Home.py` and introduce the app as Ms. Cooper's operations console with current tasks, Slack Updates, and today's calendar.
2. Open `Personal Workspace` and choose an example case such as `A2M Logistics Loan`, `Low-risk established borrower`, `Credit stacking case`, or `Suspicious transfers`.
3. Score the application, then point out the A-F grade, model recommendation, final-decision status, risk flags, structured explanation, similar historical applications, and downloadable case summary.
4. Click `Open Case Review`, choose an analyst action, optionally prepare the email-ready analysis, and save the review to the audit trail.
5. For approve/reject outcomes, show that manual score adjustment requires supervisor approval and supervisor email routing.
6. Open `Operations Desk` to show the team workboard, evidence follow-up, bulk rejection, selected-case detail, and handoff into Personal Workspace.
7. Open `Risk Dashboard` to show filtered portfolio monitoring, the manual review queue, the compliance review queue, live session decisions, and the analyst review audit trail.
8. Open `Model Insights` and `AI Explainability` to discuss model metrics, grading thresholds, feature importance, and SHAP driver analysis.

## Optional LLM Providers

The app works without an LLM by using deterministic explanations. The RF model remains the baseline score; hosted or local LLMs can act as a second reviewer on the AI Explainability page, produce a qualitative `AI review score`, map that score back to the A-F grade policy, and suggest follow-up actions.

For hosted explanations, set `OPENAI_API_KEY` in Streamlit secrets or the environment, then choose `OpenAI API` on the AI Explainability page and click `Run Explanation`.

For a local model, score an application first, open AI Explainability, choose `Local server`, enter the local endpoint/model/token, and click `Run Explanation`. Defaults:

- `LOCAL_LLM_BASE_URL`: `http://localhost:1234/v1`
- `LOCAL_LLM_MODEL`: `local-model`
- `LOCAL_LLM_API_KEY`: `local`

The local path works with tools that expose OpenAI-style chat completions, such as LM Studio or Ollama's `/v1` endpoint.
Those values stay in Streamlit session state and are not written to the repository. You may enter either the server root, such as `http://localhost:1234`, or the `/v1` base URL. The app normalizes this and calls `/v1/chat/completions` only after you click `Run Explanation`. If the local call fails, the explanation area shows the error and uses the deterministic analyst explanation.

## Pages

- `Home.py`: employee homepage with current tasks, Slack Updates, and Calendar Today.
- `pages/Personal_Workspace.py`: score one SME loan application, review evidence, save a final decision, and store the latest decision in session state.
- `pages/Operations_Desk.py`: team workboard for incoming applications, evidence gaps, SLA status, and case handoff.
- `pages/Risk_Dashboard.py`: grade distribution, decision mix, highest-risk applications, live session decisions, and review audit history.
- `pages/Model_Insights.py`: model metrics, confusion matrix, feature importances, grading thresholds, and derived signal design.
- `pages/LLM_Chat.py`: explainability view for the latest scored loan request.
- `pages/About.py`: definitions for workspace scoring dimensions and risk grade interpretation.
- `pages/Support.py`: representative contact details, support request form, scripted live chat, and FAQ.

## A-F Risk Grade Mapping

| Grade | Application risk score | Action |
| --- | --- | --- |
| A | `< 0.15` | Approve |
| B | `0.15 to < 0.28` | Approve |
| C | `0.28 to < 0.42` | Manual Review |
| D | `0.42 to < 0.58` | Manual Review |
| E | `0.58 to < 0.74` | Reject |
| F | `>= 0.74` | Reject |
