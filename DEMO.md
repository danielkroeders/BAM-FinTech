# CredRisk.AI Underwriter Workbench Demo Guide

Use this guide for investor demos and live walkthroughs.

## Before The Demo

1. Double-click `Run_App.bat` or run `pip install -r requirements.txt` and `streamlit run Home.py`.
2. Wait for the browser to open Streamlit.
3. If the browser does not open, go to `http://localhost:8501`.
4. Keep the terminal window open while presenting.

## Core Message

CredRisk.AI shows an end-to-end SME lending journey: the SME owns the intake and evidence package, the analyst reviews a frozen submitted snapshot, and the SME sees only the lender-reviewed published outcome.

This is not a production underwriting, legal, or compliance decision system. High-risk cases require human compliance review.

## Five-Minute Demo Flow

### 1. Loan Intake Portal

Start on the login screen. The default demo account should be `SME company`, and the username field should show `DemoUser`. Use `SME SSO` for the SME account or `YourBank SSO` for the lender account, then enter any random 6-digit code in the two-step authorization screen.

Open the company portal.

Say:

> This is the starting point of the platform. The SME enters its own company and loan data, controls which evidence sources it connects, and submits the file into the lender workflow. Internal lender ratings stay hidden until the lender publishes a reviewed result.

Point out:

- Company and loan data entry
- Detailed company, loan, financial, working-capital, five-year-plan, and executive context fields with help pop-ups for ratios and risk terms
- `Previous step` and `Next step` navigation across the SME portal workflow
- `Load sample intake` in Company Data for a fast demo setup
- Recommended evidence cases:
  - `Clean evidence` for a low-risk established borrower
  - `Neutral evidence` for the A2M Logistics fuel-cost pressure and long-term contract example
  - `Risky evidence` for manual review behavior
  - `Fraudulent evidence` for a high-risk compliance case
  - `Ambiguous evidence` for jurisdictional risk discussion
- PSD2/Open Banking consent simulation
- Accounting and registry/KYB connection simulation
- `Sample document cases` in Data Connections, including generated CSV examples for each document category and sample evidence files seeded when a sample intake is loaded
- Compact sample-file downloads next to each upload box after sample evidence is loaded
- Interest rate is not requested by the SME; lender pricing appears later as a bank-side recommendation
- Real local file uploads for financial statements, bank statements, tax returns, ownership/KYB, and forecast support
- Saved-file metadata, SHA-256 hashes, and lender download access
- Application-readiness checks
- Ways to strengthen the evidence package
- Evidence-source coverage
- Submit Application to Lender Review
- SME Tutorials and Support show applicant-facing guides and consultant contact, not the internal analyst helpdesk

Submit the application.

### 2. Analyst Home

Sign out, choose the `Lender analyst` demo account, complete the password and six-digit verification steps, and start on `Home`.

Say:

> This is Ms. Cooper's working day. She sees the SME intake handoff, Slack updates, and calendar commitments before moving into case work. The SME-submitted application is available from Home and Personal Workspace, while generic queue work stays in Operations Desk.

Point out:

- Welcome message for Ms. Cooper
- Suggested Actions with the SME Portal Intake entry point
- SME Intake and Operations Queue indicators
- Slack Updates or Workspace Updates
- Calendar today
- SME Portal Intake

Open the submitted application from `SME Portal Intake`, or open `Personal Workspace` and select it there.

### 3. Personal Workspace

The submitted SME portal file appears as a read-only loaded intake snapshot. Opening a submitted SME file auto-scores it for lender review; synthetic queue cases can still be handed off separately from Operations Desk.

Point out:

- Applicant data is locked in Personal Workspace; changes must happen in the Loan Intake Portal and be resubmitted
- The loaded intake snapshot: company profile, loan request, financials, five-year plan, narrative, and evidence
- The organized analyst tabs: `Decision Package`, `Risk Analysis`, `AI Output`, `Case Materials`, and `Audit History`
- Random Forest scoring baseline outputting a 0-1 application risk score
- Application risk score
- Risk grade
- Model recommendation
- Final decision status
- Risk flags
- Acronym Guide under Account & Help for DSCR, stressed DSCR, FCF, CAGR, KYB, PSD2, ROC-AUC, and file hashes
- The added interpretation columns in score, evidence, risk-driver, monitoring, and governance tables, which explain how to read each number rather than only displaying the value
- Cash-flow snapshot: FCF, monthly burn, cash-flow-to-revenue, and expected runway
- Loan pricing: offered interest rate, annual debt service, DSCR, and +2% stressed DSCR
- Submitted five-year plan: annual revenue, employees, FCF, and remaining debt for years 1-5
- Applicant narrative: loan purpose, current business context, and future business context
- CEO, CFO, and COO context notes when using a demo scenario
- Calculated credit, pricing, fraud, anomaly, document, and KYB risk signals generated by the model after intake
- Structured explanation
- Similar historical applications
- Data-source coverage for bank/accounting, registry, document, and SME-provided intake signals
- Scenario analysis for revenue growth, margin pressure, contract evidence, debt reduction, and missing documents
- Peer benchmark position against similar SME applications
- Downloadable case summary

Open `Risk Analysis` to download the exact files saved by the SME and run lender document verification. Use deterministic validation for the fully local path, or choose OpenAI/local model validation to show AI-assisted document classification on bounded previews. If the validation finds a likely mismatch, show how the lender can reject or request clarification using the evidence-mismatch rationale.

### 4. Case Review

Open `LLM Integration` and click `Generate Internal + SME Reports`. Return to `Personal Workspace` and show `AI Output`.

Click `Open Case Review`.

Choose an analyst action such as `Approve`, `Reject`, `Request Documents`, or `Escalate to Compliance`.
Set the separate analyst rating. If it differs from the model grade, explain why.

Save the review.

Point out:

- The page now shows the saved `Final Decision`
- The immutable model grade remains visible separately from the analyst rating
- The analyst note is stored separately from the model output and AI review
- The case summary preserves the decision rationale
- `Open Case Review` stays disabled until the AI output package exists

Open `LLM Integration` and click `Generate Internal + SME Reports`. Show that the internal lender report is private while the second tab contains an applicant-safe improvement report.

Return to `Personal Workspace`, open `Publish rating to SME`, review or edit the attached SME report, write the company-facing message, decide whether to disclose the numerical risk score, and publish.

### 5. SME Published Outcome

Sign out, choose the `SME company` demo account again, and open the company portal.

Say:

> The SME sees only the lender-reviewed outcome. The internal model output, analyst notes, and private lender report remain inside the lender workspace.

Point out:

- Published rating
- Lender decision
- Company-facing message
- Downloadable SME evaluation report
- Numerical risk score only if the analyst chose to disclose it
- Applicant-safe post-rating what-if planning in the SME portal
- The rating and report were not visible before publication

### 6. Operations Desk

Open `Operations Desk`.

Say:

> This is the synthetic queue workboard. It is for triage, evidence gaps, SLA visibility, bulk actions, and handoff into an analyst's personal workspace without mixing with the SME-submitted demo intake.

Point out:

- Open work items
- Manual and compliance reviews
- Evidence follow-up volume
- High-priority cases
- Filters by task status, grade, and analyst
- Selected-case detail and handoff to Personal Workspace

### 7. Risk Dashboard

Open `Risk Dashboard`.

Say:

> This turns individual scoring into portfolio operations. Analysts can filter the book, focus on exposure, and monitor manual review and compliance queues.

Point out:

- Portfolio filters
- Filtered exposure
- Manual review queue for C-D grades
- Compliance review queue for E-F grades
- Live session decisions
- Analyst review audit trail

### 8. Model Insights

Open `Model Insights`.

Point out:

- Accuracy, precision, recall, F1, ROC-AUC
- Balanced accuracy, average precision, MCC, and precision at top review queues
- Confusion matrix
- Random Forest model validation and governance metrics
- A-F grading policy
- Sample risk-score API request and response
- Top feature importances

Say:

> The model is intentionally transparent for a demo. The thresholds are explicit, analysts can see which variables matter most, and the API preview shows how the score could be embedded into a lender workflow.

### 9. AI Evaluation Package

Open `LLM Integration` after scoring an application.

Point out:

- Private detailed lender evaluation
- Separate SME-facing report draft
- Lender review before publication
- Published SME report download
- SHAP driver analysis
- Baseline risk versus application risk
- Drivers that raise or lower the application risk score

Say:

> The AI creates two audiences from the same evaluation. Analysts retain the detailed internal reasoning, while the company receives only the lender-reviewed explanation and practical improvement steps after publication.

## Two-Minute Backup Demo

Use this if time is short:

1. Log in as `SME company`.
2. Load `Fraudulent evidence` from `Load sample intake`.
3. Submit the application to lender review.
4. Sign out and log in as `Lender analyst`.
5. Open the submitted file from `SME Portal Intake` in Personal Workspace.
6. Show the locked intake snapshot, Random Forest score, risk flags, explanation, and `Risk Analysis` tab.
7. Save a case review, generate the SME report draft if time allows, and publish the rating.
8. Sign back in as `SME company` and show the published rating/report.

## Suggested Closing

> CredRisk.AI connects the full SME-to-lender-to-SME journey: applicant-owned intake, frozen lender review, explainability, analyst publication, and a clear company-facing outcome. The next step would be connecting PSD2, accounting, registry, document verification, and production monitoring systems.

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
