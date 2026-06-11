# CredRisk.AI Underwriter Workbench

A synthetic Streamlit MVP for SME lenders. The app demonstrates CredRisk.AI's lender-side Underwriter Workbench: it scores SME loan applications for credit, pricing, fraud, and anomaly risk, assigns an A-F grade, recommends an operational action, and explains the result in plain language.

This is not a production underwriting, compliance, or legal decision system. High-risk outcomes are framed as requiring human compliance review.

## Setup

Python 3.10+ is recommended.

## Run manually through a terminal

```bash
streamlit run Home.py
```

```bash
pip install -r requirements.txt
```


## Run automatically (only available on Windows 11)

For Windows users, double-click:

```text
Run_App.bat
```

The launcher creates a local `.venv`, installs dependencies from `requirements.txt`, and starts the Streamlit app.

Or run manually:



The app generates synthetic seed CSV files under `data/seed/` automatically on first run.

## Demo Script

For a full presentation runbook, see `DEMO.md`.
For the research grounding behind the risk ratios, cash-flow signals, anomaly measures, and detection measures, see `docs/fraud_research.md`.

1. Start on `Home.py` and introduce the app as the CredRisk.AI Underwriter Workbench MVP for SME credit-risk assessment.
2. Open `Loan Intake` and choose a demo generator scenario such as `A2M Logistics Loan`, `Low-risk established borrower`, `Credit stacking case`, or `Suspicious transfers`.
3. Score the application, then point out the A-F grade, recommended action, risk flags, structured explanation, similar historical applications, and downloadable case summary.
4. Click `Open Case Review`, choose an analyst action, optionally prepare the email-ready analysis, and save the review to the audit trail.
5. For approve/reject outcomes, demonstrate that manual score adjustment requires supervisor approval and supervisor email routing.
6. Open `Risk Dashboard` to show filtered portfolio monitoring, the manual review queue, the compliance review queue, live session decisions, and the analyst review audit trail.
7. Open `Model Insights` and `AI Explainability` to discuss model metrics, grading thresholds, feature importance, and SHAP driver analysis.

## Optional OpenAI Key

The app works without an OpenAI API key by using deterministic explanations. If an `OPENAI_API_KEY` is available in Streamlit secrets or the environment, the Loan Intake and AI Explainability pages can optionally use LLM explanations.

## Pages

- `Home.py`: portfolio metrics, high-risk case count, model ROC-AUC, recall, simulated data sources, and workflow overview.
- `pages/About.py`: definitions for Loan Intake scoring dimensions and risk grade interpretation.
- `pages/Loan_Intake.py`: score one B2B loan application and store the latest decision in session state.
- `pages/Risk_Dashboard.py`: grade distribution, decision mix, highest-risk applications, and live session decisions.
- `pages/Model_Insights.py`: model metrics, confusion matrix, feature importances, and grading thresholds.
- `pages/LLM_Chat.py`: explainability view for the latest scored loan request.
- `pages/Support.py`: representative contact details, support request form, scripted demo live chat, and FAQ.

## A-F Risk Grade Mapping

| Grade | Application risk score | Action |
| --- | --- | --- |
| A | `< 0.15` | Approve |
| B | `0.15 to < 0.28` | Approve |
| C | `0.28 to < 0.42` | Manual Review |
| D | `0.42 to < 0.58` | Manual Review |
| E | `0.58 to < 0.74` | Reject |
| F | `>= 0.74` | Reject |
