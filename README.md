# B2B Loan Fraud Intelligence

A synthetic Streamlit decision-support demo for business lenders. The app scores B2B loan applications for fraud risk, assigns an A-F grade, recommends an operational action, and explains the result in plain language.

This is not a production underwriting, compliance, or legal decision system. High-risk outcomes are framed as requiring human compliance review.

## Setup

Python 3.10+ is recommended.

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run Home.py
```

The app generates synthetic seed CSV files under `data/seed/` automatically on first run.

## Optional OpenAI Key

The app works without an OpenAI API key by using deterministic explanations. If an `OPENAI_API_KEY` is available in Streamlit secrets or the environment, the Loan Intake and AI Explainability pages can optionally use LLM explanations.

## Pages

- `Home.py`: portfolio metrics, known fraud count, model ROC-AUC, recall, and workflow overview.
- `pages/About.py`: definitions for Loan Intake scoring dimensions and risk grade interpretation.
- `pages/Loan_Intake.py`: score one B2B loan application and store the latest decision in session state.
- `pages/Risk_Dashboard.py`: grade distribution, decision mix, highest-risk applications, and live session decisions.
- `pages/Model_Insights.py`: model metrics, confusion matrix, feature importances, and grading thresholds.
- `pages/LLM_Chat.py`: explainability view for the latest scored loan request.

## A-F Risk Grade Mapping

| Grade | Fraud probability | Action |
| --- | --- | --- |
| A | `< 0.15` | Approve |
| B | `0.15 to < 0.28` | Approve |
| C | `0.28 to < 0.42` | Manual Review |
| D | `0.42 to < 0.58` | Manual Review |
| E | `0.58 to < 0.74` | Reject |
| F | `>= 0.74` | Reject |
