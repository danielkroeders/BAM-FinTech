# B2B Loan Fraud Intelligence Demo Guide

Use this guide for investor demos, grading presentations, and live walkthroughs.

## Before The Demo

1. Double-click `Run_App.bat` or in terminal pip install -r  requirements.txt and run streamlit run Home.py
2. Wait for the browser to open Streamlit.
3. If the browser does not open, go to `http://localhost:8501`.
4. Keep the terminal window open while presenting.

## Core Message

B2B Loan Fraud Intelligence is a synthetic decision-support MVP for business lenders. It helps analysts triage loan applications, explain fraud-risk drivers, route cases to human review, and preserve an audit trail.

This is not a production underwriting, legal, or compliance decision system. High-risk cases require human compliance review.

## Five-Minute Demo Flow

### 1. Home

Start on the home page.

Say:

> This is the portfolio command center. It shows the synthetic lending book, known fraud count, model performance, and the operational workflow from intake to analyst review.

Point out:

- Portfolio size
- Known fraud count
- ROC-AUC and recall
- Grade and decision distribution
- Highest-risk applications

### 2. Loan Intake

Open `Loan Intake`.

Use the top-right demo generator and select one scenario:

- `Low-risk established borrower` for a clean approval case
- `Credit stacking case` for manual review behavior
- `Suspicious transfers` for a high-risk compliance case
- `High country-risk borrower` for jurisdictional risk discussion

Click `Score Application`.

Point out:

- Fraud probability
- Risk grade
- Model recommendation
- Final decision status
- Risk flags
- Structured explanation
- Similar historical applications
- Downloadable case summary

### 3. Case Review

Click `Open Case Review`.

Choose an analyst action such as `Approve`, `Reject`, `Request Documents`, or `Escalate to Compliance`.

For approve/reject cases, show that a manual score adjustment requires supervisor approval and a supervisor email.

Save the review.

Point out:

- The page now shows the saved `Final Decision`
- The model recommendation remains visible separately
- An email draft can be prepared for supervisor review
- The case summary preserves the decision rationale

### 4. Risk Dashboard

Open `Risk Dashboard`.

Say:

> This turns individual scoring into portfolio operations. Analysts can filter the book, focus on exposure, and work from manual review and compliance queues.

Point out:

- Portfolio filters
- Filtered exposure
- Manual review queue for C-D grades
- Compliance review queue for E-F grades
- Live session decisions
- Analyst review audit trail

### 5. Model Insights

Open `Model Insights`.

Point out:

- Accuracy, precision, recall, F1, ROC-AUC
- Confusion matrix
- A-F grading policy
- Top feature importances

Say:

> The model is intentionally transparent for a demo. The thresholds are explicit, and analysts can see which variables matter most.

### 6. AI Explainability

Open `AI Explainability` after scoring an application.

Point out:

- Plain-language explanation
- SHAP driver analysis
- Baseline risk versus application risk
- Drivers that raise or lower fraud probability

Say:

> This gives analysts an explanation they can understand without reading raw model features.

## Two-Minute Backup Demo

Use this if time is short:

1. Open `Loan Intake`.
2. Select `Suspicious transfers`.
3. Score the application.
4. Show risk flags, explanation, similar applications, and final decision workflow.
5. Open `Risk Dashboard`.
6. Show compliance queue and review audit trail.

## Suggested Closing

> The MVP demonstrates the full fraud-review loop: synthetic data, model scoring, explainability, analyst override governance, supervisor routing, and portfolio queues. The next step would be connecting real lender systems, document verification, and production monitoring.

## Demo Safety Notes

- All data is synthetic.
- Do not enter real customer information.
- Do not present model output as a final legal or compliance determination.
- Keep high-risk outcomes framed as requiring human compliance review.

## Troubleshooting

If the app does not start:

1. Confirm Python 3.10 or newer is installed.
2. Reopen `Run_App.bat`.
3. Check your internet connection if dependency installation fails.
4. As a fallback, run:

```bash
streamlit run Home.py
```
