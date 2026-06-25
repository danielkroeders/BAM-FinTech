# CredRisk.AI Pitchdeck Speaker Notes - Fully Assignment Aligned

Timing target: **3-minute investor pitch deck + 7-minute live product demo**. Total video must stay under **10 minutes**.

Use this as a cue script, not as text to read word-for-word. The video should prove three things at once:

1. CredRisk.AI is an investor-oriented FinTech MVP.
2. The MVP is implemented as working software, not only a slide concept.
3. The repository and AI-agent workflow satisfy the assignment deliverables.

## Non-Negotiable Assignment Points To Mention

Before recording, make sure these are either shown or clearly said:

- Main MVP features: SME intake, evidence upload, Random Forest scoring, AI Output, analyst review, publication, SME result.
- Architecture: role-aware Streamlit UI, data/evidence pipeline, Random Forest engine, AI report layer, runtime state, audit trail.
- GUI and UX: guided applicant intake, role separation, frozen lender snapshot, gated AI Output before Case Review, applicant-safe publication.
- Deployment/use: `pip install -r requirements.txt`, then `Run_App.bat` on Windows or `streamlit run Home.py`.
- Investor orientation: problem, solution, why it wins, value for lenders and SMEs.
- Coding agents at the end: **Codex was used as the repo-aware coding agent**; `.codex/CODEX.md` orchestrates page structure, workflows, constraints, and acceptance checks.
- Repository proof: README in root, requirements file, demo/launcher, commented code, visible commit history, `.codex/CODEX.md`, public repo description, and topic tags.

---

# Core Message

CredRisk.AI is a loan intake portal and underwriter workbench for SME lending. It connects the applicant journey, evidence upload, Random Forest risk scoring, AI-assisted report generation, analyst review, publication, and SME-facing outcome in one traceable workflow.

The product is **not** an automatic credit decision tool. The Random Forest model and AI report support the analyst. The final rating, final action, and applicant-facing publication remain human-controlled.

---

# 3-Minute Pitch Deck

## Slide 1 - CredRisk.AI `(0:00-0:20)`

CredRisk.AI is an end-to-end SME credit workflow. The journey starts with the SME, moves through a governed underwriter workbench, and ends with a lender-approved result back to the SME.

The core idea is simple: instead of intake, documents, model output, analyst notes, and publication living in separate tools, we connect them in one traceable case file.

Key point: this is not an automatic credit decision tool. The model supports the decision, but the analyst remains accountable.

## Slide 2 - The Problem `(0:20-0:45)`

SME underwriting breaks when information is fragmented. The bank needs speed, but cannot lose traceability.

The problem has three parts. First, SME intake is often incomplete or unstructured. Second, evidence creates friction because documents can be missing, ambiguous, risky, clean, or even fraudulent. Third, governance becomes difficult when model scores, AI advice, analyst ratings, and SME-facing communication are mixed together.

That is the problem CredRisk.AI solves: faster underwriting without losing control over evidence, model output, and the human final decision.

## Slide 3 - The Solution `(0:45-1:15)`

CredRisk.AI turns the loan file into a controlled workflow.

First, the SME fills in the Loan Intake Portal and submits evidence. Second, the lender opens a frozen snapshot and applies one governed Random Forest baseline that returns a 0-1 application risk score. Third, the analyst reviews the generated AI package before Case Review. Fourth, the SME receives only the lender-approved rating, message, and applicant-safe report.

The A-F grading policy makes the score interpretable, but the final decision remains separate from the model output.

## Slide 4 - Why This Wins `(1:15-1:40)`

The value proposition is faster decisions with control.

For SMEs, the app gives a structured intake flow with sample cases, blank intake, and help pop-ups. For analysts, it gives evidence readiness, risk drivers, ratios, and interpretation columns. For governance, it separates the Random Forest grade, AI-generated reports, analyst action, and SME publication.

That separation is important because it prevents automation from quietly becoming the final credit decision.

## Slide 5 - Architecture `(1:40-2:10)`

The MVP is implemented as working software, not just a mockup.

The front end is a role-aware Streamlit interface with SME intake, lender Home, Personal Workspace, Operations Desk, dashboards, settings, tutorials, and support. The data and evidence pipeline uses synthetic SME cases, realistic company data, a local document vault, hashes, and sample evidence packs.

The risk engine uses scikit-learn preprocessing and a single Random Forest baseline. On top of that, the AI report layer can use deterministic fallback, OpenAI, or a local LLM path to generate internal and applicant-safe reports. Runtime state stores submitted snapshots, reviews, AI outputs, publications, and audit trail information.

This maps the Assignment 1 business concept into code: intake becomes a UI workflow, underwriting becomes a governed scoring and review engine, and communication becomes a controlled publication layer.

## Slide 6 - Demo Path `(2:10-2:25)`

The demo follows the same logic as the product: SME to analyst to SME.

We start with the SME intake, then move to the lender handoff, Random Forest scoring, AI Output, Case Review, publication, and finally the SME-facing result.

## Slide 7 - Scale And Risk `(2:25-2:45)`

The MVP is intentionally focused. To scale it, the next steps would be PSD2 or open banking data, accounting APIs, registry and KYB data, document ingestion, role-based access, secure secrets, deployment controls, and model monitoring.

The main risks are false positives, fraud misses, AI hallucination, data leakage, model drift, and over-reliance on automation. The design mitigates these through review gates, validation metrics, human final decision-making, and auditability.

## Slide 8 - Execution Proof `(2:45-3:00)`

This is built for the assignment deliverables: a working MVP, a clean repository, collaboration history, and AI-agent orchestration.

The repository includes the README, requirements, demo script, Windows launcher, commented Python files, research notes, and `.codex/CODEX.md` for agent guidance. That file documents page structure, workflows, acceptance checks, and product constraints so repo-aware coding changes stay consistent.

## Slide 9 - Now The Demo `(3:00)`

The pitch is: CredRisk.AI turns SME lending from a file chase into an explainable decision workflow.

Now I will show the MVP working live.

---

# 7-Minute Live Demo

## 0:00-0:25 - Launch And Deployment

Say:

The app can be started after installing the requirements with `pip install -r requirements.txt`. On Windows, it can be launched with `Run_App.bat`, or manually with `streamlit run Home.py`. For this recording, I am using the local Streamlit MVP.

Show:

- App running locally.
- Login or start screen.
- Role selection if visible.

Point:

This covers how the software is deployed and used in the MVP setting. It is a local working demo, not just a slide prototype.

## 0:25-1:35 - SME Login And Loan Intake Portal

Say:

We begin on the applicant side. The SME selects its company, logs in with DemoUser and SME SSO, and opens the Loan Intake Portal.

This is the first contact point between the applicant data and the underwriting workflow. The SME can either load a sample case or start from a blank application.

Show:

- SME company selection.
- DemoUser / SME SSO.
- Loan Intake Portal.
- Company context fields.
- Financial information.
- Loan purpose.
- Five-year plan.
- Help pop-ups if quick to show.

Point:

The UX goal is to reduce incomplete intake. The applicant is guided into providing company context, financials, loan purpose, and planning information in one structured flow.

## 1:35-2:20 - Evidence Upload And Submission

Say:

The SME also submits evidence. The demo includes different evidence situations, such as clean, neutral, risky, fraudulent, and ambiguous document cases.

That matters because underwriting is not only about the financial fields. Document readiness and evidence risk affect how quickly and confidently a case can be reviewed.

Show:

- Sample evidence case or upload area.
- Attached documents.
- Evidence checklist or validation results.
- Submit button.

Point:

After submission, the applicant side creates a case that can be handed over to the lender. From here, the lender reviews a frozen snapshot rather than an editable applicant form.

## 2:20-3:00 - Lender Handoff And Home

Say:

Now we switch roles. The lender logs in with YourBank SSO. Home shows suggested actions and the newly submitted SME Portal Intake snapshot.

Show:

- YourBank SSO / lender login.
- Home screen.
- Suggested Actions.
- SME Portal Intake snapshot.

Point:

This shows the handoff from applicant to analyst. The submitted SME case stays traceable and appears in the lender workspace.

## 3:00-4:05 - Personal Workspace And Random Forest Scoring

Say:

In Personal Workspace, the analyst opens the locked intake. The analyst can inspect the applicant details, evidence, and risk signals before running the scoring step.

The MVP uses a single governed Random Forest baseline. It returns a 0-1 application risk score and translates that score into an A-F grade using the grading thresholds from the pitch deck.

Show:

- Locked intake snapshot.
- Applicant details.
- Evidence status.
- Random Forest score / Run Risk Analysis button.
- 0-1 risk score.
- A-F grade.
- Main risk drivers, ratios, and interpretation columns.

Point:

There is no model shopping in the demo. The Random Forest is the governed baseline, and the output is made readable for underwriting through the grade, ratios, and risk drivers.

## 4:05-5:00 - AI Output Before Case Review

Say:

Before the analyst records the final case review, the workflow requires the AI Output step. This keeps the AI-generated package visible, but separate from the final human decision.

The app generates two versions: a private lender-facing report and an applicant-safe SME draft. The lender report can be more detailed, while the SME version must be safe to publish back to the applicant.

If the external or local LLM path is unavailable, the app can use a deterministic fallback. That is intentional: the workflow should remain stable and auditable even when an optional AI service is not available.

Show:

- AI Output page or section.
- Generate internal report.
- Generate SME-facing draft.
- Any comparison between model output and AI text.
- Any warning, fallback, or deterministic option if visible.

Point:

The AI is useful for structured explanation and report drafting, but it does not approve or reject the loan. It prepares information for the analyst.

## 5:00-5:55 - Case Review, Human Decision, And Publication

Say:

Now we move into Case Review. This is where Ms. Cooper records the analyst action, rating, notes, and publication decision separately from both the Random Forest grade and the AI report.

Show:

- Case Review page.
- Analyst action.
- Analyst rating.
- Notes.
- Save review.
- Publish approved applicant-safe copy.
- Audit trail entry.

Point:

This is the governance core of the product. Model score, AI report, analyst rating, and SME-facing publication are separate objects in the workflow. That makes the decision traceable and keeps the final credit decision human-controlled.

## 5:55-6:25 - SME Outcome

Say:

Finally, we return to the SME side. The SME does not see the internal analyst report or private model reasoning. The SME receives only the lender-approved rating, lender message, and applicant-safe evaluation report.

Show:

- SME login again if needed.
- Published rating.
- Lender message.
- Downloadable evaluation report.

Point:

This closes the full value loop: SME intake, lender review, Random Forest scoring, AI Output, human decision, publication, and SME-facing result.

## 6:25-7:00 - Agent Orchestration And Repository Proof

Say:

To close the assignment-specific part: the coding agent I used was Codex as a repo-aware coding assistant. It was a good choice because it can follow the existing project structure, work across multiple files, and make targeted changes while respecting the Streamlit page layout and product logic.

I orchestrated it through `.codex/CODEX.md`. That file defines the page structure, workflow constraints, product rules, and acceptance checks, so AI-assisted changes stay aligned with the MVP instead of becoming disconnected features.

The public repository also includes the root README, requirements, launch script, demo notes, commented code, visible commit history, and topic tags, which supports handoff and meets the repository requirements.

Show if time:

- GitHub repository root.
- README in the root folder.
- `requirements.txt`.
- `.codex/CODEX.md`.
- Commit history.
- Repository description/topic tags.

Close:

That is CredRisk.AI: a working MVP for SME credit intake and underwriting that connects product value, software architecture, responsible AI use, and a traceable human decision workflow.

---

# Assignment Coverage Check

Do **not** read this section aloud unless you need it for preparation. It is here to verify that the slides and demo match the assignment brief exactly.

| Assignment requirement | Where it is covered | Status |
|---|---|---|
| Develop a working MVP | Slides 5, 6, 8 and full live demo | Covered |
| Record a demonstration of features and functioning | 7-minute demo path | Covered |
| Main MVP features | Slides 1-4 and demo: SME intake, evidence, scoring, AI Output, review, publication, SME result | Covered |
| Architecture and concept-to-code mapping | Slide 5: Streamlit UI, data/evidence pipeline, Random Forest engine, AI report layer, runtime state and audit trail | Covered |
| GUI design and UX | Slides 3-6 and demo: role-aware flow, guided intake, frozen lender snapshot, gated review, applicant-safe publication | Covered |
| Deployment and use | Demo start: `pip install -r requirements.txt`, `Run_App.bat`, `streamlit run Home.py` | Covered |
| Investor orientation | Slides 1-4: problem, solution, differentiation, product promise | Covered |
| Coding agent(s) used | Final demo section: Codex as repo-aware coding assistant | Covered |
| Why agents were a good choice | Final demo section: follows structure, works across files, targeted changes | Covered |
| Agent orchestration | Slide 8 and final demo section: `.codex/CODEX.md`, page structure, workflow constraints, acceptance checks | Covered |
| Scale prerequisites | Slide 7: PSD2/open banking, accounting APIs, KYB, document ingestion, RBAC, secure secrets, monitoring | Covered |
| Technological risks | Slide 7 and AI Output section: AI hallucination, model drift, fallback, validation, auditability | Covered |
| Operations and maintenance | Slides 4, 7, 8: clean operations, monitoring, audit trail, repository handoff | Covered |
| Security risks | Slide 7: data leakage, secure secrets, role-based access, auditability | Covered |
| Clean GitHub repository | Slide 8 and final demo section: README, requirements, launcher, comments, research notes, agent instructions | Covered verbally; verify actual repo |
| Collaboration history over time | Final demo section: visible commit history | Covered verbally; verify actual repo |
| README in root folder | Final demo section and repository proof | Covered verbally; verify actual repo |
| Agent instructions file | Slide 8 and final demo section: `.codex/CODEX.md` | Covered |
| Clear description and topic tags | Final demo section | Covered verbally; verify actual repo |
| Video under 10 minutes | 3-minute pitch + 7-minute demo | Covered if rehearsed |

## Strict Recording Notes

- Do **not** spend time on generic dashboards unless the core SME-to-analyst-to-SME loop is already complete.
- Do **not** say the AI makes the credit decision. Say it drafts/reviews, while the analyst decides.
- Do **not** mention Logistic Regression in the recording. The aligned pitch uses one governed Random Forest baseline.
- Do **not** rely on the local LLM live if it is unstable. Use deterministic fallback or a pre-generated AI output and frame this as a governance feature.
- Do **not** claim repository topic tags, commit history, or README quality unless they are actually present in the public GitHub repo.
- The final 30-35 seconds must explicitly answer the coding-agent requirement, because the assignment asks for this at the end.
