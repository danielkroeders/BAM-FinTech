# Codex Instructions: Recreate The CredRisk.AI Underwriter Workbench

Build and maintain **CredRisk.AI Underwriter Workbench** as a Streamlit application for SME lending analysts. The product should feel like a real bank employee workspace already in motion: Ms. Cooper starts from her workday, opens assigned cases, scores applications, reviews evidence, records final decisions, monitors portfolio risk, and can optionally run an AI second review.

Launch command:

```bash
streamlit run Home.py
```

Do not create or use `app.py`.

## Product Shape

The application is an operational lending workbench, not a landing page. It supports:

- RF model scoring for SME loan applications.
- A-F risk grading and model recommendations.
- Case-level evidence readiness and calculated risk signals.
- Analyst final decisions that remain separate from model recommendations.
- Bulk actions on the team workboard.
- Portfolio monitoring and review audit history.
- Deterministic explanations by default.
- Optional hosted or local LLM second-review output from the AI Explainability page only.

High-risk outputs require human compliance review. Never present model or LLM output as a final legal, credit, or compliance determination.

## Required Structure

Keep this Streamlit page layout:

```text
Home.py
pages/
  Personal_Workspace.py
  Operations_Desk.py
  Risk_Dashboard.py
  Model_Insights.py
  LLM_Chat.py
  About.py
  Support.py
src/
  __init__.py
  case_workflow.py
  data_pipeline.py
  explanations.py
  formatting.py
  modeling.py
  runtime.py
  shap_explanations.py
  ui.py
  workbench_features.py
data/
  seed/
docs/
  fraud_research.md
README.md
DEMO.md
Run_App.bat
requirements.txt
```

Do not recreate `pages/Loan_Intake.py` or `pages/Application_Queue.py`; those concepts are now `Personal_Workspace.py` and `Operations_Desk.py`.

## Page Requirements

### Home

`Home.py` is Ms. Cooper's employee homepage. It must show only:

- Welcome message for Ms. Cooper.
- Current tasks table.
- `Slack Updates`.
- `Calendar Today`.

Do not put source-status panels, connected-data panels, portfolio charts, RF model metrics, product walkthrough content, or explanation controls on Home.

### Personal Workspace

`pages/Personal_Workspace.py` is the case work surface. It must:

- Let Ms. Cooper start an assigned case, start the A2M example case, or use manual entry.
- Keep clearly marked example cases available for presentations.
- Group intake fields around company profile, loan request, financial snapshot, five-year plan, applicant narrative, executive context, documents, verification, and advanced signals.
- Score an application through the RF model.
- Store latest application, prediction, deterministic explanation, and session history.
- Show score output near the top: application risk score, risk grade, model recommendation, final decision status, review status, and stressed DSCR.
- Show `Decision Rationale` immediately after the score panel. This rationale is deterministic in Personal Workspace.
- Keep model recommendation separate from analyst final decision.
- Provide case review, audit summary download, credit memo generation, similar historical applications, decision timeline, calculated risk signals, data readiness, recommended terms, and monitoring preview.

Data Readiness must use plain banker language. Avoid shorthand like "support no" or unexplained scores. Use labels such as:

- `Forecast support document received: Yes/No`.
- `Banker confidence score: 0,38 / 1,00`.
- `Financial statements received: Yes/No`.
- `Decision use: Checks liquidity and whether free cash flow can cover estimated debt service.`

### Operations Desk

`pages/Operations_Desk.py` is the team workboard. It must:

- Show open work items, manual/compliance work, evidence follow-up, rejected-today count, filters, task table, and selected-case detail.
- Support selecting multiple visible cases and applying `Reject Selected Cases`.
- Record bulk rejections in `review_history`, `portfolio_history`, and `bulk_final_decisions`.
- Link into Personal Workspace for single-case work.

### Risk Dashboard

`pages/Risk_Dashboard.py` must show:

- Portfolio filters.
- Filtered exposure.
- Manual review queue.
- Compliance review queue.
- Highest-risk applications.
- Live session decisions.
- Analyst review audit trail.

### Model Insights

`pages/Model_Insights.py` must show:

- Accuracy, balanced accuracy, precision, recall, F1, ROC-AUC, average precision, MCC, false-positive/false-negative rates, review-rate and error-cost metrics.
- Precision at top 5%, 10%, and 20% review queues.
- Confusion matrix.
- A-F grading thresholds.
- Governance notes.
- Feature importances.
- Research-backed derived signals.

### AI Explainability

`pages/LLM_Chat.py` is the only place where hosted or local LLM calls may run.

The flow must be:

1. Score an application in Personal Workspace.
2. Open AI Explainability.
3. Show the RF model baseline first.
4. Show deterministic explanation by default.
5. Let the user choose `Deterministic`, `OpenAI API`, or `Local server`.
6. Let the user choose `Detailed analyst memo` or `Concise summary`.
7. Call the chosen LLM provider only after the user clicks `Run Explanation`.
8. Render the returned output on the page.

The RF baseline must show:

- RF application risk score.
- RF grade.
- RF recommendation.
- RF ROC-AUC.
- RF recall.
- RF precision.
- Balanced accuracy.
- Precision at top 10%.

LLM output must act as a second reviewer. The prompt must ask the LLM to:

- Use the RF model output, RF validation metrics, and loan intake inputs as evidence.
- Run its own qualitative assessment.
- Say whether it agrees, partially agrees, or disagrees with the RF recommendation.
- Output exactly one line in the form `AI review score: NN/100`.
- Output exactly one line in the form `AI suggested grade: X`.
- Use the same A-F thresholds as the RF model.
- Explain if the case looks more severe or less severe than the RF grade, for example "more like grade E than RF grade C".
- Suggest follow-up actions and questions.
- Avoid inventing facts or claiming legal certainty.

The UI must parse the AI review score, compute the implied A-F grade, and compare it with the RF grade. If the LLM's written grade conflicts with the implied grade, show a warning and treat the implied grade as the normalized comparison.

### About

`pages/About.py` defines scoring dimensions and derived risk signals. Keep it explanatory and banker-readable.

### Support

`pages/Support.py` provides representative contacts, support request form, scripted chat, and FAQ.

## Decisioning Policy

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

The RF model recommendation is never the final analyst decision. Final decision is saved through review workflow or bulk action.

## Model And Data Requirements

`src/modeling.py` must use scikit-learn with:

- `Pipeline`.
- `ColumnTransformer`.
- numeric imputation with median.
- numeric scaling with `StandardScaler`.
- categorical imputation with most frequent value.
- categorical encoding with `OneHotEncoder(handle_unknown="ignore")`.
- `RandomForestClassifier`.

Expose:

- `ModelBundle`.
- `train_model(applications)`.
- `grade_from_probability(probability)`.
- `decision_from_grade(grade)`.
- `rule_flags(application)`.
- `score_application(model_bundle, application)`.
- `score_portfolio(model_bundle, applications)`.

`src/data_pipeline.py` must keep the local portfolio data available automatically and maintain derived features for:

- debt pressure.
- request-to-revenue exposure.
- loan velocity.
- payment stress.
- collateral gap.
- transaction anomaly.
- company scale mismatch.
- governance complexity.
- free cash flow.
- monthly burn.
- cash-flow-to-revenue.
- runway risk.
- cash conversion.
- five-year forecast realism.
- interest-rate and debt-service stress.
- document completeness and document quality.
- process integrity.
- identity/KYB verification.
- working-capital pressure.
- financial-statement anomaly.
- related-party network risk.
- narrative consistency.

Keep cash-flow fields, forecast fields, document/KYB fields, applicant narrative, and executive context in the case file.

## Explanations

`src/explanations.py` must provide:

- deterministic explanation that works without any API key or local model.
- OpenAI API explanation through `OPENAI_API_KEY`.
- local model explanation through an OpenAI-compatible chat-completions endpoint.
- local URL normalization so server root, `/v1`, or an accidentally pasted `/chat/completions` path still resolves to the correct base URL.
- visible fallback error messages when LLM calls fail.

Local LLM fields are entered on AI Explainability and kept only in Streamlit session state. Do not write server URLs or tokens to files.

Local defaults:

```text
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=local-model
LOCAL_LLM_API_KEY=local
```

## Runtime State

`src/runtime.py` must initialize:

- `seed_data`.
- `model_bundle`.
- `portfolio_history`.
- `review_history`.
- `last_application`.
- `last_prediction`.
- `last_explanation`.
- `last_explanation_source`.
- `last_explanation_error`.
- `last_review`.
- `last_email_link`.
- `show_review_dialog`.
- LLM page state: provider, latest output, source, error, case signature, local URL/model/token.
- bulk action state.
- active case state.

Every page must call `bootstrap_state()` before using shared state.

## UI And Copy Rules

- Keep the UI operational and compact.
- Do not make a marketing landing page.
- Do not use app-facing words that reveal staging or sample data, except for clearly marked example cases in Personal Workspace.
- Use employee language: current tasks, workboard, evidence follow-up, case review, final decision, audit trail, supervisor routing.
- Keep data-source readiness inside Personal Workspace because readiness differs per applicant.
- Use European formatting helpers from `src/formatting.py`.
- Use `width="stretch"` instead of deprecated `use_container_width=True`.
- Keep buttons and tables readable on desktop and mobile.
- Never include secrets or real customer data.

## Documentation

Maintain:

- `README.md`: product summary, Windows launcher, manual launch, LLM provider setup, page overview, A-F grade policy.
- `DEMO.md`: walkthrough runbook for presentations.
- `docs/fraud_research.md`: research grounding for derived signals.

`README.md` must mention `Run_App.bat` before manual command-line setup.

## Dependencies

Required runtime dependencies:

```text
streamlit
pandas
numpy
scikit-learn
openai
shap
pypdf
```

Python 3.10+ is recommended.

## Acceptance Checks

Before finishing meaningful changes, verify:

```bash
python -m compileall src Home.py pages
streamlit run Home.py
```

Functional checks:

- Home loads and shows only current tasks, Slack Updates, and Calendar Today.
- Personal Workspace scores an application and shows deterministic Decision Rationale near the score output.
- Personal Workspace Data Readiness uses clear evidence labels.
- Case review saves final decision separately from model recommendation.
- Operations Desk supports bulk rejection and audit history.
- Risk Dashboard shows manual/compliance queues and session history.
- Model Insights shows metrics, thresholds, confusion matrix, and feature importance.
- AI Explainability handles no-scored-case state.
- AI Explainability shows RF baseline metrics.
- AI Explainability runs no LLM call until `Run Explanation` is clicked.
- AI Explainability can run deterministic, OpenAI API, or local-server explanations.
- AI Explainability extracts AI review score, maps it to A-F grade thresholds, and compares it to RF grade.
- App works without `OPENAI_API_KEY` and without a local model.
