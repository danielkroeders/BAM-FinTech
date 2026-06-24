from html import escape
from urllib.parse import urlencode

import streamlit as st

from src.core.runtime import bootstrap_state
from src.ui.components import (
    get_profile,
    is_sme_profile,
    render_sidebar,
    safe_page_link,
)

st.set_page_config(page_title="Tutorials", layout="wide")
bootstrap_state()
render_sidebar()
profile = get_profile()
sme_mode = is_sme_profile(profile)


TUTORIALS = [
    {
        "slug": "home",
        "title": "Home",
        "page": "Home.py",
        "icon": "⌂",
        "category": "Getting started",
        "time": "4 min",
        "level": "Beginner",
        "summary": "Orient yourself, resume assigned work, and read the day’s operational signals.",
        "features": ["Task snapshot", "Quick actions", "Team updates", "Calendar"],
        "objectives": [
            "Read the four workload indicators",
            "Resume the right assigned case",
            "Use updates and calendar context",
        ],
        "steps": [
            {
                "title": "Read your workload snapshot",
                "body": "Start with My Open Tasks, High Priority, Due This Week, and Evidence Follow-Up. Together they tell you how much work is assigned, which cases carry the most risk, and where missing evidence may block a decision.",
                "action": "Use High Priority and Due This Week to decide what deserves attention first.",
                "tip": "A case can be urgent without being high risk. Check both the risk grade and its SLA.",
            },
            {
                "title": "Resume an assigned task",
                "body": "Use Continue task to choose an application from your personal queue. The label includes the application ID, applicant, and grade so you can identify the case before opening it.",
                "action": "Select a task and choose Continue Selected Task to load it into Personal Workspace.",
                "tip": "The handoff preserves the selected application as the active intake case.",
            },
            {
                "title": "Scan the current-task table",
                "body": "The table adds requested amount, risk score, queue status, evidence gaps, and SLA. Use it for a more complete comparison when several cases look equally urgent.",
                "action": "Compare evidence gaps before starting cases that require same-day completion.",
                "tip": "A high missing-document count usually means the next action is evidence follow-up, not scoring.",
            },
            {
                "title": "Use the daily context",
                "body": "Workspace or Slack updates show handoffs and queue events. Calendar Today shows scheduled reviews, stand-ups, and escalation checks that may affect your sequencing.",
                "action": "Open the page you need from the quick links beneath the task table.",
                "tip": "Treat Home as a launchpad; detailed case work happens in Personal Workspace.",
            },
        ],
    },
    {
        "slug": "personal-workspace",
        "title": "Personal Workspace",
        "page": "pages/1_Personal_Workspace.py",
        "icon": "◎",
        "category": "Credit work",
        "time": "10 min",
        "level": "Core workflow",
        "summary": "Load a case, review evidence, score the application, and record the analyst decision.",
        "features": [
            "Case queue",
            "Application intake",
            "Risk result",
            "Metric guide",
            "Case review",
        ],
        "objectives": [
            "Start from a queue or SME-submitted intake",
            "Understand the scoring inputs and output",
            "Save a human review to the audit trail",
        ],
        "steps": [
            {
                "title": "Load a lender snapshot",
                "body": "Start a case from SME Portal Intake or Current Tasks. The active-intake banner confirms which submitted snapshot is loaded and where it came from.",
                "action": "For the full SME-to-lender walkthrough, load a sample intake in the SME Company Portal, submit it, then open it from SME Portal Intake.",
                "tip": "Submitted SME applications auto-score when opened in Personal Workspace. Other loaded task snapshots can be scored with Score Loaded Intake.",
            },
            {
                "title": "Review the locked intake",
                "body": "Inspect the read-only company profile, loan request, financial snapshot, five-year plan, applicant narrative, and evidence checklist. Applicant data changes belong in the SME Company Portal.",
                "action": "Check requested amount, free cash flow, recent loans, suspicious transfers, and evidence readiness, then choose Score Loaded Intake if the snapshot has not already been scored.",
                "tip": "Do not interpret a single field in isolation. The model combines pressure, anomaly, liquidity, and evidence signals.",
            },
            {
                "title": "Interpret the scored result",
                "body": "After scoring, use the A–F grade, application risk score, model recommendation, affordability measures, flags, and explanation together. The result tables explain how to read each number, and the separate Acronym Guide under Account & Help explains DSCR, stressed DSCR, FCF, CAGR, KYB, PSD2, ROC-AUC, and file hashes.",
                "action": "Compare the model recommendation with DSCR, stressed DSCR, missing evidence, and the table interpretation columns. Open Acronym Guide when a term is unfamiliar.",
                "tip": "A model recommendation supports review; it is not the final legal or credit decision. If a number is unclear, use the How to read it column before drawing a conclusion.",
            },
            {
                "title": "Record the human decision",
                "body": "Open Case Review, select an analyst action, and add a concise note that explains the evidence considered. Saving the review stores the final action separately from the model recommendation.",
                "action": "Write a note that names the decisive risk and mitigating factors.",
                "tip": "For high-risk E/F cases, keep a human compliance-style review in the loop before external communication.",
            },
        ],
    },
    {
        "slug": "llm-integration",
        "title": "LLM Integration",
        "page": "pages/5_LLM_Integration.py",
        "icon": "✦",
        "category": "Credit work",
        "time": "8 min",
        "level": "Advanced",
        "summary": "Generate internal and SME-facing evaluation reports and inspect SHAP drivers.",
        "features": [
            "Provider choice",
            "Internal report",
            "SME report draft",
            "SHAP drivers",
        ],
        "objectives": [
            "Choose the appropriate review provider",
            "Compare AI and supervised-model outputs",
            "Review the applicant-safe report before publication",
            "Interpret case-specific Random Forest contributions",
        ],
        "steps": [
            {
                "title": "Prepare a scored case",
                "body": "LLM Integration works from the latest application and prediction in session state. Score an application in Personal Workspace first so the page has a complete case to review.",
                "action": "Confirm the Random Forest baseline score, grade, and recommendation before running a review.",
                "tip": "The deterministic option works without external credentials and is the safest demo path.",
            },
            {
                "title": "Select and configure a provider",
                "body": "Choose deterministic analysis, the OpenAI API, or a local OpenAI-compatible server. Hosted and local providers are optional second-review paths and may fall back when unavailable.",
                "action": "For hosted or local reviews, choose the detail level. Local server review also requires an endpoint and model.",
                "tip": "Never place secrets in the repository. Use environment variables, Streamlit secrets, or session-only controls.",
            },
            {
                "title": "Compare the review output",
                "body": "Every run creates an evaluation package with a private lender report and a separate SME-facing draft. Successful hosted or local output can also show a qualitative AI review score, implied grade, and comparison with the Random Forest grade.",
                "action": "Review both tabs. Investigate material model disagreement and check that the SME draft is fair, understandable, and actionable.",
                "tip": "The SME draft is not visible to the company until the lender reviews it and publishes the final outcome.",
            },
            {
                "title": "Inspect SHAP driver analysis",
                "body": "The SHAP section uses the Random Forest baseline and shows how individual features move this application away from its baseline risk. The chart and table rank the largest positive and negative contributions.",
                "action": "Translate the largest drivers back to source evidence in the application file.",
                "tip": "SHAP contributions explain the Random Forest baseline. A contribution does not prove causality.",
            },
        ],
    },
    {
        "slug": "operations-desk",
        "title": "Operations Desk",
        "page": "pages/2_Operations_Desk.py",
        "icon": "▦",
        "category": "Operations & risk",
        "time": "6 min",
        "level": "Intermediate",
        "summary": "Filter the team queue, manage evidence work, apply bulk actions, and hand off cases.",
        "features": ["Queue KPIs", "Filters", "Bulk actions", "Case handoff"],
        "objectives": [
            "Narrow the workboard to the right queue",
            "Use bulk actions carefully",
            "Send a selected case into review",
        ],
        "steps": [
            {
                "title": "Read the team queue",
                "body": "Open Work Items, Manual / Compliance, Evidence Follow-Up, and Rejected Today summarize the current operating load.",
                "action": "Use the metrics to decide whether the team needs triage, evidence work, or review capacity.",
                "tip": "Team-level counts may differ from the personal queue shown on Home.",
            },
            {
                "title": "Filter the workboard",
                "body": "Combine status, grade, and analyst filters to isolate a meaningful slice of work. The table retains risk, decision, evidence, owner, and SLA context.",
                "action": "For urgent review, filter to Manual review and Compliance review, then inspect E/F grades.",
                "tip": "Keep at least one analyst selected; an empty filter combination produces no cases.",
            },
            {
                "title": "Apply a controlled bulk action",
                "body": "Bulk Actions lets you select visible cases and record one rejection note. The action updates final-decision history and the audit trail.",
                "action": "Verify every selected application supports the same decision rationale before submitting.",
                "tip": "Avoid generic notes when cases have materially different evidence or risk drivers.",
            },
            {
                "title": "Hand off a single case",
                "body": "Select an application to see its risk, grade, recommendation, document readiness, SLA, and business details. Start This Case In Personal Workspace loads it into the analyst workflow.",
                "action": "Use the detail panel as a final identity and context check before handoff.",
                "tip": "The Operations Desk organizes work; the full evidence review happens in Personal Workspace.",
            },
        ],
    },
    {
        "slug": "risk-dashboard",
        "title": "Risk Dashboard",
        "page": "pages/3_Risk_Dashboard.py",
        "icon": "◒",
        "category": "Operations & risk",
        "time": "7 min",
        "level": "Intermediate",
        "summary": "Monitor portfolio composition, review queues, high-risk cases, and analyst activity.",
        "features": [
            "Portfolio filters",
            "Risk KPIs",
            "Distributions",
            "Review activity",
        ],
        "objectives": [
            "Build a relevant portfolio slice",
            "Read grade and decision distributions",
            "Investigate high-risk applications",
        ],
        "steps": [
            {
                "title": "Define the portfolio view",
                "body": "Use grade, decision, industry, region, and application-risk-score range filters to create the population you want to monitor. Every metric, chart, and table below responds to this selection.",
                "action": "Start broad, then narrow one dimension at a time so you can see what changes.",
                "tip": "A small filtered population can make percentages look dramatic; always check the case count.",
            },
            {
                "title": "Read the headline indicators",
                "body": "The KPI strip summarizes applications, exposure, average risk, and review or compliance load for the selected population.",
                "action": "Compare risk level with exposure rather than ranking segments on probability alone.",
                "tip": "A moderate-risk segment can still be material when its total exposure is large.",
            },
            {
                "title": "Interpret portfolio distributions",
                "body": "Grade and decision charts show whether the selected book is concentrated in approvals, manual review, or rejection bands. Supporting tabs expose queue and risk detail.",
                "action": "Look for concentration in D/E/F grades and the size of the manual and compliance review queues.",
                "tip": "Distribution changes can reflect portfolio mix, filter choices, or model changes.",
            },
            {
                "title": "Investigate and open cases",
                "body": "Highest-risk and activity views help identify applications that need attention and show decisions made during the session. Selected cases can be handed into Personal Workspace.",
                "action": "Open the application only after checking both its score and the evidence or review context.",
                "tip": "Use activity history to distinguish a new alert from a case that has already been reviewed.",
            },
        ],
    },
    {
        "slug": "model-insights",
        "title": "Model Insights",
        "page": "pages/4_Model_Insights.py",
        "icon": "⌁",
        "category": "Operations & risk",
        "time": "9 min",
        "level": "Advanced",
        "summary": "Inspect the model baseline, validation metrics, thresholds, and signal design.",
        "features": ["Model baseline", "Metrics", "Feature importance", "Governance"],
        "objectives": [
            "Interpret the Random Forest scoring baseline",
            "Interpret performance beyond accuracy",
            "Understand thresholds, governance, and signal design",
        ],
        "steps": [
            {
                "title": "Review the scoring baseline",
                "body": "Review the Random Forest probability output, ROC-AUC, balanced accuracy, and precision in the highest-risk queue.",
                "action": "Use the Model Insights page to explain the single deterministic baseline used across lender pages.",
                "tip": "Plain Linear Regression is not suitable for probability output because its raw output is not naturally bounded to 0-1.",
            },
            {
                "title": "Select meaningful metrics",
                "body": "Metric presets and the visible-metrics control cover ranking quality, class balance, queue precision, error rates, review workload, and estimated financial cost. The custom metric area calculates one portfolio aggregate or ratio from selected numeric fields.",
                "action": "Pair a quality metric such as ROC-AUC with an operating metric such as review rate or total error cost.",
                "tip": "Raw accuracy can hide poor high-risk detection when risky cases are rare.",
            },
            {
                "title": "Inspect thresholds and drivers",
                "body": "Review grading thresholds, confusion behavior, feature importances, and research-backed derived signals. These sections explain how model output becomes an operational grade and recommendation.",
                "action": "Check whether the most important drivers are supported by reliable source data.",
                "tip": "Global feature importance is different from the case-specific SHAP explanation on LLM Integration.",
            },
            {
                "title": "Review governance and signal design",
                "body": "Governance Notes covers data lineage, human review, audit trail, threshold policy, and model limitations. Top Feature Importances and Research-Backed Derived Signals show the global model inputs and calculated fields exposed by the current page.",
                "action": "Use Governance Notes to explain intended use, then connect important global features to the derived-signal definitions.",
                "tip": "This page does not currently expose a live API or API contract preview.",
            },
        ],
    },
    {
        "slug": "profile-settings",
        "title": "Profile & Settings",
        "page": "pages/7_Profile_Settings.py",
        "icon": "♙",
        "category": "Account & help",
        "time": "5 min",
        "level": "Beginner",
        "summary": "Review your profile, connected apps, controlled fields, notifications, and theme.",
        "features": ["Profile", "Personal apps", "Admin controls", "Preferences"],
        "objectives": [
            "Verify analyst identity and permissions",
            "Understand personal app connections",
            "Save session preferences safely",
        ],
        "steps": [
            {
                "title": "Verify your profile",
                "body": "The Profile tab lists ID, name, email, bank, role, team, user type, permission, manager, and preferred email app.",
                "action": "Check identity and permission fields before beginning sensitive review work.",
                "tip": "Profile values in this demo are session-oriented and do not represent a production identity system.",
            },
            {
                "title": "Review connected apps",
                "body": "Personal Apps lists messaging, email, calendar, storage, and meeting connections with their account and intended use.",
                "action": "Distinguish personal productivity connections from risk-model evidence sources.",
                "tip": "A connected personal app does not automatically make its data a model input.",
            },
            {
                "title": "Use controlled admin fields",
                "body": "The demo's Admin Controls lets the current user update selected profile settings. User type, permission, and manager remain disabled until controlled fields are explicitly enabled.",
                "action": "Enable controlled fields only when you intend to change access-related demo values.",
                "tip": "In production, changes to permissions should require stronger authorization and audit controls.",
            },
            {
                "title": "Save channels and preferences",
                "body": "Choose preferred channel and email app, toggle personal app access, notification settings, daily digest, and dark mode, then save.",
                "action": "Connect Slack or Teams before selecting it as the preferred channel.",
                "tip": "Dark mode is also available from the sidebar toggle.",
            },
        ],
    },
    {
        "slug": "support",
        "title": "Support",
        "page": "pages/9_Support.py",
        "icon": "?",
        "category": "Account & help",
        "time": "4 min",
        "level": "Beginner",
        "summary": "Contact a specialist, prepare a support request, use scripted chat, or browse FAQs.",
        "features": ["Representatives", "Request form", "Live chat", "FAQ"],
        "objectives": [
            "Choose the right support route",
            "Prepare a useful case-linked request",
            "Find quick answers in chat or FAQ",
        ],
        "steps": [
            {
                "title": "Choose a representative",
                "body": "The representative cards describe each person’s focus: onboarding and workflow, scoring and model questions, or account and training help.",
                "action": "Match the issue to the representative’s focus before opening an email.",
                "tip": "Include an application or case ID when the question relates to a specific review.",
            },
            {
                "title": "Prepare a support request",
                "body": "Select a representative and category, choose a preferred contact channel, add the case ID, and describe the issue. Submitting prepares a session ticket and email draft.",
                "action": "State what you expected, what happened, and the page where it occurred.",
                "tip": "Do not put passwords, API keys, or sensitive applicant data in a support message.",
            },
            {
                "title": "Use the scripted live chat",
                "body": "The chat provides immediate demo responses for scoring, DSCR, documents, integrations, and case review. It does not contact a real support desk.",
                "action": "Ask one focused question and include the relevant feature name.",
                "tip": "Use a representative for issues that require investigation or follow-up.",
            },
            {
                "title": "Browse common answers",
                "body": "FAQ expanders cover intended use, data sources, affordability, overrides, high-risk handling, and integrations.",
                "action": "Check the FAQ before creating a request for a general product question.",
                "tip": "For field and signal definitions, the About page is the more complete reference.",
            },
        ],
    },
    {
        "slug": "acronym-guide",
        "title": "Acronym Guide",
        "page": "pages/11_Acronym_Guide.py",
        "icon": "A",
        "category": "Account & help",
        "time": "3 min",
        "level": "Reference",
        "summary": "Search analyst acronyms and metric explanations used across scoring, evidence, monitoring, and governance.",
        "features": ["Acronyms", "Metric meanings", "Search", "Workspace links"],
        "objectives": [
            "Look up DSCR, FCF, CAGR, KYB, PSD2, ROC-AUC, and SHA-256",
            "Understand how to read common score and evidence metrics",
            "Jump back to the right workflow page",
        ],
        "steps": [
            {
                "title": "Search for a term",
                "body": "Use the search field to find acronyms, metric names, and related explanations. The page filters both acronym and metric tables.",
                "action": "Try DSCR, FCF, document completeness, or ROC-AUC.",
                "tip": "If you see DCSR in rough notes, read it as DSCR.",
            },
            {
                "title": "Read the acronym table",
                "body": "The acronym table expands each abbreviation into a plain-language meaning and shows where it appears in the application.",
                "action": "Use Where used to return to the relevant workflow context.",
                "tip": "The glossary explains terms; it does not replace the case-specific evidence review.",
            },
            {
                "title": "Read metric meanings",
                "body": "The metric table explains how to interpret common numbers like application risk score, document completeness, and grade boundary distance.",
                "action": "Use the metric explanation before making a conclusion from a single value.",
                "tip": "Most model and risk outputs are review prompts, not automatic final decisions.",
            },
        ],
    },
    {
        "slug": "about",
        "title": "About",
        "page": "pages/8_About.py",
        "icon": "i",
        "category": "Account & help",
        "time": "6 min",
        "level": "Reference",
        "summary": "Look up model dimensions, derived signals, grade meanings, and usage boundaries.",
        "features": [
            "Input definitions",
            "Derived signals",
            "Grade policy",
            "Limitations",
        ],
        "objectives": [
            "Look up unfamiliar scoring terms",
            "Understand why a signal matters",
            "Apply the grade policy appropriately",
        ],
        "steps": [
            {
                "title": "Start with the usage boundary",
                "body": "The page explains that scores prioritize analyst review and do not establish legal, credit, or compliance certainty.",
                "action": "Use this statement when presenting the workspace to a new user.",
                "tip": "A clear intended-use statement prevents a decision-support score from being mistaken for an automated decision.",
            },
            {
                "title": "Look up input dimensions",
                "body": "The definitions table covers company, loan, financial, forecast, evidence, identity, and transaction fields, with an explanation of why each matters.",
                "action": "Search the table when a label in Personal Workspace is unfamiliar.",
                "tip": "Definitions explain the concept; source documents determine whether the value is trustworthy.",
            },
            {
                "title": "Understand derived signals",
                "body": "Derived signals combine raw inputs into interpretable measures such as debt pressure, payment stress, anomaly risk, liquidity pressure, and forecast aggressiveness.",
                "action": "Trace a derived signal back to its component inputs before challenging the result.",
                "tip": "Derived signals can amplify data-quality problems when an underlying input is wrong.",
            },
            {
                "title": "Use grades as routing policy",
                "body": "The A–F mapping connects score ranges to approve, manual-review, or reject recommendations, while preserving the requirement for human judgment.",
                "action": "Use the grade to route work, then review evidence and affordability before final action.",
                "tip": "Thresholds are policy choices and should be validated against portfolio outcomes before production use.",
            },
        ],
    },
]

SME_TUTORIALS = [
    {
        "slug": "sme-application-start",
        "title": "Start Your Application",
        "page": "pages/6_SME_Credit_Health.py",
        "icon": "♥",
        "category": "SME application",
        "time": "5 min",
        "level": "Beginner",
        "summary": "Enter company details, loan request, financial snapshot, and business context before submitting to YourBank.",
        "features": [
            "Company data",
            "Loan request",
            "Financial snapshot",
            "Business context",
        ],
        "objectives": [
            "Complete the company profile",
            "Explain the loan purpose",
            "Save the application draft",
        ],
        "steps": [
            {
                "title": "Open Company Data",
                "body": "Use the SME company portal to enter the company name, industry, region, legal type, years in business, employees, revenue, debt, and requested loan amount.",
                "action": "Fill the Company Data tab and choose Save Company Data.",
                "tip": "Saved company data updates the readiness preview but does not submit the file yet.",
            },
            {
                "title": "Describe the financing need",
                "body": "Use the loan-purpose and business-context fields to explain why financing is requested, what is happening now, and what assumptions support the plan.",
                "action": "Write concise, factual context that a lender can compare with the documents.",
                "tip": "The applicant-facing view does not show YourBank's internal model score.",
            },
            {
                "title": "Check readiness",
                "body": "The Credit Health tab shows application-readiness indicators and practical next actions before any lender rating is published.",
                "action": "Use the readiness indicators to decide what to complete before submission.",
                "tip": "Readiness guidance is not a loan approval or rejection.",
            },
            {
                "title": "Keep ownership of the draft",
                "body": "The SME controls what is entered and which evidence sources are selected before submitting the application to YourBank review.",
                "action": "Review the saved values before moving to Submit to Lender.",
                "tip": "After submission, the lender performs its own checks and decides when to publish an outcome.",
            },
        ],
    },
    {
        "slug": "sme-documents-connections",
        "title": "Documents and Connections",
        "page": "pages/6_SME_Credit_Health.py",
        "icon": "▤",
        "category": "SME application",
        "time": "6 min",
        "level": "Core task",
        "summary": "Select simulated data connections, inspect example files, and save application documents to the local vault.",
        "features": [
            "PSD2 consent",
            "Example files",
            "Document uploads",
            "Saved-file vault",
        ],
        "objectives": [
            "Understand the simulated connections",
            "Use example files as format guidance",
            "Save real local files to the application vault",
        ],
        "steps": [
            {
                "title": "Choose data sources",
                "body": "Open Data Connections and select PSD2/Open Banking, accounting, and registry/KYB sources. In this MVP they demonstrate consent and source selection only.",
                "action": "Save connections after confirming the consent checkbox for PSD2/Open Banking.",
                "tip": "No real bank, accounting, or registry data is transmitted in the demo.",
            },
            {
                "title": "Use the example document pack",
                "body": "The example pack shows fictional CSV structures for financial statements, bank statements, tax returns, ownership/KYB, and forecast support.",
                "action": "Download examples for reference or save them for a demo package.",
                "tip": "Saving examples writes actual CSV bytes into the same local vault as uploaded files.",
            },
            {
                "title": "Upload application evidence",
                "body": "Use the file uploaders to add documents to the right category. The app saves exact bytes, original filename, MIME type, size, timestamp, and SHA-256 hash.",
                "action": "Choose files and click Save Uploaded Files.",
                "tip": "YourBank verifies submitted evidence on the lender side after submission.",
            },
            {
                "title": "Download what was saved",
                "body": "Saved files appear in the document table and can be downloaded from the portal. The lender can later download the same saved bytes.",
                "action": "Use the download buttons to confirm the files that are attached to the application.",
                "tip": "Use Clear Demo State only when you intentionally want to remove demo-session files.",
            },
        ],
    },
    {
        "slug": "sme-submit-result",
        "title": "Submit and View Results",
        "page": "pages/6_SME_Credit_Health.py",
        "icon": "✓",
        "category": "SME application",
        "time": "5 min",
        "level": "Beginner",
        "summary": "Submit the application, wait for lender review, and view the published rating and evaluation report.",
        "features": [
            "Submission",
            "Lender review",
            "Published rating",
            "Post-rating what-if",
        ],
        "objectives": [
            "Submit the saved application",
            "Understand what remains private",
            "Download the published evaluation report",
        ],
        "steps": [
            {
                "title": "Submit to lender review",
                "body": "Open Submit to Lender, review the summary, and submit the file. The submitted application snapshot becomes available to the lender in SME Portal Intake.",
                "action": "Submit only after company data, connections, and files are ready.",
                "tip": "Submission does not immediately publish a rating.",
            },
            {
                "title": "Understand lender review",
                "body": "The lender opens the submission, receives an automatic baseline score in Personal Workspace, checks evidence, may generate an internal evaluation, and chooses when to publish a reviewed outcome.",
                "action": "Wait for the published result or consultant follow-up.",
                "tip": "Internal model probabilities, verification notes, and private lender reports stay lender-only.",
            },
            {
                "title": "Read the published outcome",
                "body": "After publication, the SME portal shows the lender rating, decision, company-facing message, and attached evaluation report.",
                "action": "Open Credit Health after publication to view the result.",
                "tip": "The numerical risk score appears only if the lender explicitly publishes it.",
            },
            {
                "title": "Use the report and what-if planner",
                "body": "The SME-facing report explains strengths, weaknesses, and practical improvement areas in applicant-safe language. After publication, the Credit Health tab also shows a directional what-if planner for future-readiness improvements.",
                "action": "Download the report, then use the what-if controls to test evidence, cash-flow, growth, and debt-plan improvements.",
                "tip": "The planner is not a new lender decision and does not change the published rating.",
            },
        ],
    },
    {
        "slug": "sme-consultant-support",
        "title": "Connect with a Consultant",
        "page": "pages/9_Support.py",
        "icon": "?",
        "category": "Help",
        "time": "4 min",
        "level": "Beginner",
        "summary": "Use the SME support page to request help from a YourBank consultant.",
        "features": ["Consultants", "Request form", "Applicant chat", "FAQ"],
        "objectives": [
            "Choose the right consultant route",
            "Prepare an application-linked request",
            "Find quick answers for applicant questions",
        ],
        "steps": [
            {
                "title": "Choose a consultant",
                "body": "The SME support page shows YourBank consultants focused on application readiness, lending questions, upload issues, and next-step planning.",
                "action": "Pick the consultant whose focus matches the question.",
                "tip": "This is applicant support, not the internal lender helpdesk.",
            },
            {
                "title": "Submit a consultant request",
                "body": "Choose a category, preferred contact method, application ID, and message. The page prepares a request and email draft.",
                "action": "Include the application ID when the question is about a submitted file.",
                "tip": "Do not include passwords, API keys, or unnecessary sensitive data in the request.",
            },
            {
                "title": "Use applicant chat",
                "body": "The scripted chat answers basic SME questions about documents, submission, data connections, and published reports.",
                "action": "Ask one focused applicant question.",
                "tip": "The chat does not contact a real support desk in the MVP.",
            },
            {
                "title": "Check common answers",
                "body": "The FAQ explains ratings, simulated connections, document issues, and consultant contact.",
                "action": "Read the FAQ before creating a general request.",
                "tip": "For lender-side review decisions, wait for the published outcome or consultant follow-up.",
            },
        ],
    },
    {
        "slug": "sme-acronym-guide",
        "title": "Acronym Guide",
        "page": "pages/11_Acronym_Guide.py",
        "icon": "A",
        "category": "Help",
        "time": "3 min",
        "level": "Beginner",
        "summary": "Look up applicant-facing terms used in the company portal, documents, connections, and published results.",
        "features": ["Glossary", "Applicant metrics", "Search", "Helpful links"],
        "objectives": [
            "Understand PSD2, KYB, UBO, FCF, CAGR, DSCR, and file hashes",
            "Read applicant-safe metric explanations",
            "Know which terms to ask a consultant about",
        ],
        "steps": [
            {
                "title": "Search a term",
                "body": "Use the search box to filter applicant-facing acronyms and metric explanations.",
                "action": "Try PSD2, KYB, FCF, or published rating.",
                "tip": "The SME glossary avoids internal lender scoring rules.",
            },
            {
                "title": "Read the applicant meaning",
                "body": "Each row explains what the term means, how to interpret it, and where it appears in the SME portal.",
                "action": "Use the Where used column to connect the term to the portal step you are working on.",
                "tip": "If a published report still feels unclear, use Support to connect with a YourBank consultant.",
            },
            {
                "title": "Jump back to help",
                "body": "The page links back to the Company Portal, Support, and Tutorials so the guide can be used during application preparation or after publication.",
                "action": "Open the page you need from the bottom of the guide.",
                "tip": "The glossary is explanatory only; it does not change a submitted application or a published lender outcome.",
            },
        ],
    },
]

ACTIVE_TUTORIALS = SME_TUTORIALS if sme_mode else TUTORIALS

PAGE_MAPS = {
    "home": [
        {
            "kind": "metrics",
            "title": "Workload snapshot",
            "detail": "My Open Tasks · High Priority · Due This Week · Evidence Follow-Up",
        },
        {
            "kind": "action",
            "title": "Quick Actions",
            "detail": "Continue task → Continue Selected Task",
        },
        {
            "kind": "table",
            "title": "Current Tasks",
            "detail": "Task ID · Applicant · Application risk score · Evidence gaps · SLA",
        },
        {
            "kind": "split",
            "title": "Daily context",
            "detail": "Slack or Workspace Updates | Calendar Today",
        },
    ],
    "personal-workspace": [
        {
            "kind": "queue",
            "title": "Current Tasks",
            "detail": "Next application · Start Selected Case · SME Portal Intake",
        },
        {
            "kind": "form",
            "title": "Loaded intake snapshot",
            "detail": "Company · Loan · Financials · Five-Year Plan · Context · Evidence",
        },
        {
            "kind": "score",
            "title": "Score Output",
            "detail": "Application risk score · Risk grade · Recommendation · Random Forest · Stressed DSCR",
        },
        {
            "kind": "review",
            "title": "Case Review",
            "detail": "Analyst action · Analyst note · Save Review",
        },
    ],
    "llm-integration": [
        {
            "kind": "metrics",
            "title": "Model Baseline",
            "detail": "Risk score · Model grade · Recommendation · ROC-AUC · Recall · Precision",
        },
        {
            "kind": "form",
            "title": "Run LLM Review",
            "detail": "Explanation source · Detail level · Provider-specific settings",
        },
        {
            "kind": "review",
            "title": "LLM Review Output",
            "detail": "Provider · Source · Last run · Status · Optional AI score and grade",
        },
        {
            "kind": "chart",
            "title": "SHAP Driver Analysis",
            "detail": "Random Forest baseline · Contribution chart · Driver table",
        },
    ],
    "operations-desk": [
        {
            "kind": "metrics",
            "title": "Team queue",
            "detail": "Open Work Items · Manual / Compliance · Evidence Follow-Up · Rejected Today",
        },
        {
            "kind": "table",
            "title": "Filtered workboard",
            "detail": "Status · Grade · Analyst filters above the application table",
        },
        {
            "kind": "review",
            "title": "Bulk Actions",
            "detail": "Cases · Decision note · Reject Selected Cases",
        },
        {
            "kind": "action",
            "title": "Selected Application",
            "detail": "Risk · Grade · Decision · Doc readiness · SLA → Personal Workspace",
        },
    ],
    "risk-dashboard": [
        {
            "kind": "controls",
            "title": "Portfolio Filters",
            "detail": "Grades · Decisions · Industries · Regions · Application risk score",
        },
        {
            "kind": "metrics",
            "title": "Portfolio KPIs",
            "detail": "Filtered Applications · Exposure · Average Risk Score · Review Load",
        },
        {
            "kind": "chart",
            "title": "Portfolio distributions",
            "detail": "Grade Distribution | Decision Mix",
        },
        {
            "kind": "tabs",
            "title": "Investigation views",
            "detail": "Review Queues · Highest Risk · Session Activity · Open In Workspace",
        },
    ],
    "model-insights": [
        {
            "kind": "table",
            "title": "Model comparison",
            "detail": "Random Forest · ROC-AUC · Balanced accuracy · Precision top 10%",
        },
        {
            "kind": "metrics",
            "title": "Metric analysis",
            "detail": "Metric preset · Visible metrics · Top 5/10/20% queue precision",
        },
        {
            "kind": "split",
            "title": "Policy and custom analysis",
            "detail": "Custom Portfolio Metric | Confusion Matrix | A-F Grading Thresholds",
        },
        {
            "kind": "table",
            "title": "Governance and signals",
            "detail": "Governance Notes · Top Feature Importances · Research-Backed Derived Signals",
        },
    ],
    "profile-settings": [
        {
            "kind": "tabs",
            "title": "Settings navigation",
            "detail": "Profile · Personal Apps · Admin Controls",
        },
        {
            "kind": "table",
            "title": "Profile",
            "detail": "Identity · Bank · Role · Team · Permission · Manager · Email app",
        },
        {
            "kind": "table",
            "title": "Personal Connected Apps",
            "detail": "Messaging · Email & Calendar · Personal Files · Meetings",
        },
        {
            "kind": "form",
            "title": "Admin Controls",
            "detail": "Enable controlled profile fields · Preferred channels · App access · Alerts · Dark mode · Save Admin Controls",
        },
    ],
    "support": [
        {
            "kind": "cards",
            "title": "Contact A Representative",
            "detail": "Implementation · Risk support · Customer success",
        },
        {
            "kind": "form",
            "title": "Support Request",
            "detail": "Representative · Category · Contact · Case ID · Message",
        },
        {
            "kind": "chat",
            "title": "Live Chat",
            "detail": "Scripted answers for scoring, DSCR, documents, integrations, and review",
        },
        {
            "kind": "accordion",
            "title": "FAQ",
            "detail": "Intended use · Data · Affordability · Overrides · High-risk handling · Apps",
        },
    ],
    "acronym-guide": [
        {
            "kind": "search",
            "title": "Search glossary",
            "detail": "DSCR · FCF · PSD2 · KYB · ROC-AUC · SHA-256",
        },
        {
            "kind": "table",
            "title": "Acronyms",
            "detail": "Term · Meaning · How to read it · Where used",
        },
        {
            "kind": "table",
            "title": "Metric meanings",
            "detail": "Application risk score · Document completeness · Grade boundary distance",
        },
        {
            "kind": "action",
            "title": "Workflow links",
            "detail": "Personal Workspace · Support · About",
        },
    ],
    "sme-acronym-guide": [
        {
            "kind": "search",
            "title": "Search glossary",
            "detail": "PSD2 · KYB · UBO · FCF · CAGR · DSCR",
        },
        {
            "kind": "table",
            "title": "Applicant acronyms",
            "detail": "Term · Meaning · How to read it · Where used",
        },
        {
            "kind": "table",
            "title": "Applicant metrics",
            "detail": "Application readiness · Published rating · What-if band",
        },
        {
            "kind": "action",
            "title": "Help links",
            "detail": "Company Portal · Consultant Support · Tutorials",
        },
    ],
    "about": [
        {
            "kind": "notice",
            "title": "Usage boundary",
            "detail": "Decision support; not legal, credit, or compliance certainty",
        },
        {
            "kind": "search",
            "title": "Search glossary",
            "detail": "Search document, DSCR, forecast, KYB, grade, and other terms",
        },
        {
            "kind": "tabs",
            "title": "Reference tables",
            "detail": "Scoring Dimensions · Derived Signals · Grade Policy",
        },
        {
            "kind": "notice",
            "title": "High-risk warning",
            "detail": "E and F require human compliance review",
        },
    ],
}


def _query_value(name):
    if hasattr(st, "query_params"):
        value = st.query_params.get(name)
    else:
        value = st.experimental_get_query_params().get(name)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _current_query_params():
    try:
        params = dict(st.query_params)
    except Exception:
        try:
            params = st.experimental_get_query_params()
        except Exception:
            params = {}
    return params


def _tutorial_href(slug=None):
    params = {
        key: value for key, value in _current_query_params().items() if key != "guide"
    }
    if slug:
        params["guide"] = slug
    query = urlencode(params, doseq=True)
    return f"?{query}" if query else "?"


def _map_preview(kind):
    if kind == "metrics":
        return '<div class="map-metrics"><i></i><i></i><i></i><i></i></div>'
    if kind in {"table", "queue"}:
        return (
            '<div class="map-filter-row"><i></i><i></i><i></i></div>'
            '<div class="map-table"><b></b><i></i><i></i><i></i></div>'
        )
    if kind in {"form", "controls"}:
        return (
            '<div class="map-form">'
            '<i></i><i></i><i class="wide"></i><span></span><span></span>'
            "</div>"
        )
    if kind == "score":
        return (
            '<div class="map-score"><strong>0.42</strong><i>C</i><i>Manual Review</i></div>'
            '<div class="map-tabs"><b></b><b></b><b></b><b></b></div>'
        )
    if kind == "chart":
        return (
            '<div class="map-chart">'
            '<i class="bar-one"></i><i class="bar-two"></i><i class="bar-three"></i><i class="bar-four"></i>'
            "</div>"
        )
    if kind == "split":
        return '<div class="map-split"><i></i><i></i></div>'
    if kind == "tabs":
        return (
            '<div class="map-tabs"><b></b><b></b><b></b></div>'
            '<div class="map-table compact"><i></i><i></i><i></i></div>'
        )
    if kind == "review":
        return (
            '<div class="map-review"><i></i><i></i><i class="wide"></i></div>'
            '<div class="map-button"></div>'
        )
    if kind == "action":
        return (
            '<div class="map-select"></div><div class="map-button long"></div>'
            '<div class="map-table compact"><i></i><i></i></div>'
        )
    if kind == "cards":
        return '<div class="map-cards"><i></i><i></i><i></i></div>'
    if kind == "chat":
        return '<div class="map-chat"><i></i><i></i><i></i></div>'
    if kind == "accordion":
        return '<div class="map-accordion"><i></i><i></i><i></i></div>'
    if kind == "search":
        return '<div class="map-search"></div><div class="map-table compact"><i></i><i></i></div>'
    if kind == "notice":
        return '<div class="map-notice"><i></i><i></i></div>'
    return '<div class="map-table compact"><i></i><i></i><i></i></div>'


def _feature_map(tutorial):
    sections = PAGE_MAPS[tutorial["slug"]]
    cards = "".join(f"""
        <div class="page-map-card">
            <div class="page-map-number">{index:02d}</div>
            <div class="page-map-preview">{_map_preview(section["kind"])}</div>
            <div class="page-map-title">{escape(section["title"])}</div>
            <div class="page-map-detail">{escape(section["detail"])}</div>
        </div>
        """ for index, section in enumerate(sections, start=1))
    return f"""
    <div class="feature-map">
        <div class="page-map-browser">
            <div class="feature-browser-top">
                <span></span><span></span><span></span>
                <div class="feature-address">CredRisk.AI / {escape(tutorial["title"])}</div>
            </div>
            <div class="page-map-header">
                <div>
                    <div class="feature-kicker">{escape(tutorial["category"])}</div>
                    <div class="page-map-page-title">{escape(tutorial["title"])}</div>
                </div>
                <div class="page-map-badge">Current page controls</div>
            </div>
            <div class="page-map-grid">{cards}</div>
        </div>
        <div class="page-map-note">
            This feature map mirrors the current page labels and workflow. It is a compact guide diagram, not a screenshot.
        </div>
    </div>
    """


def _render_styles():
    st.markdown(
        """
        <style>
        .tutorial-hero {
            background-position: center;
            background-size: cover;
            border: 1px solid rgba(45, 212, 191, 0.24);
            border-radius: 14px;
            box-shadow: 0 22px 52px rgba(15, 23, 42, 0.16);
            min-height: 310px;
            margin-bottom: 1.4rem;
            overflow: hidden;
            position: relative;
        }
        .tutorial-hero::after {
            background: linear-gradient(90deg, rgba(2, 6, 23, 0.96) 0%, rgba(2, 6, 23, 0.82) 37%, rgba(2, 6, 23, 0.08) 72%);
            content: "";
            inset: 0;
            position: absolute;
        }
        .tutorial-hero-copy {
            max-width: 34rem;
            padding: 3.4rem 3rem;
            position: relative;
            z-index: 1;
        }
        .tutorial-kicker {
            color: #5eead4;
            font-size: 0.76rem;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .tutorial-hero-title {
            color: #f8fafc;
            font-size: clamp(2rem, 4vw, 3.2rem);
            font-weight: 850;
            letter-spacing: -0.04em;
            line-height: 1.02;
            margin: 0.65rem 0 0.85rem;
        }
        .tutorial-hero-text {
            color: rgba(226, 232, 240, 0.80);
            font-size: 1rem;
            line-height: 1.55;
        }
        .tutorial-hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1.2rem;
        }
        .tutorial-hero-meta span,
        .objective-chip {
            background: rgba(15, 118, 110, 0.24);
            border: 1px solid rgba(94, 234, 212, 0.24);
            border-radius: 999px;
            color: #ccfbf1;
            font-size: 0.76rem;
            font-weight: 750;
            padding: 0.42rem 0.65rem;
        }
        .tutorial-section-heading {
            align-items: end;
            display: flex;
            gap: 1rem;
            justify-content: space-between;
            margin: 1.5rem 0 0.75rem;
        }
        .tutorial-section-title {
            color: var(--cr-text);
            font-size: 1.25rem;
            font-weight: 850;
        }
        .tutorial-section-copy {
            color: var(--cr-muted);
            font-size: 0.86rem;
            margin-top: 0.2rem;
        }
        .tutorial-intro {
            background: color-mix(in srgb, var(--cr-surface) 95%, transparent);
            border: 1px solid var(--cr-border);
            border-left: 5px solid var(--cr-teal);
            border-radius: 12px;
            box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
            margin-bottom: 1.4rem;
            padding: 2rem;
        }
        .tutorial-intro-title {
            color: var(--cr-text);
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 850;
            letter-spacing: -0.04em;
            line-height: 1.05;
            margin: 0.55rem 0 0.75rem;
        }
        .tutorial-intro-copy {
            color: var(--cr-muted);
            line-height: 1.55;
            max-width: 44rem;
        }
        a.tutorial-panel {
            background: color-mix(in srgb, var(--cr-surface) 94%, transparent);
            border: 1px solid var(--cr-border);
            border-radius: 12px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
            color: inherit;
            display: block;
            min-height: 220px;
            overflow: hidden;
            position: relative;
            text-decoration: none;
            transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
        }
        a.tutorial-panel:hover {
            border-color: rgba(20, 184, 166, 0.58);
            box-shadow: 0 18px 36px rgba(15, 118, 110, 0.13);
            transform: translateY(-4px);
        }
        .panel-preview {
            background:
                radial-gradient(circle at 82% 16%, rgba(34, 211, 238, 0.22), transparent 32%),
                linear-gradient(145deg, #0f172a, #0b3b46);
            height: 132px;
            overflow: hidden;
            padding: 1rem;
            position: relative;
        }
        .panel-preview-window {
            background: rgba(248, 250, 252, 0.96);
            border: 1px solid rgba(255,255,255,0.24);
            border-radius: 7px;
            box-shadow: 0 14px 24px rgba(2, 6, 23, 0.28);
            display: grid;
            grid-template-columns: 26px 1fr;
            height: 104px;
            overflow: hidden;
            transform: rotate(-1.5deg) translateY(4px);
        }
        .panel-mini-sidebar {
            background: #111827;
            padding: 12px 6px;
        }
        .panel-mini-sidebar i {
            background: rgba(94, 234, 212, 0.34);
            border-radius: 5px;
            display: block;
            height: 4px;
            margin-bottom: 8px;
        }
        .panel-mini-main { padding: 12px; }
        .panel-mini-title {
            background: #0f172a;
            border-radius: 4px;
            height: 7px;
            margin-bottom: 10px;
            width: 38%;
        }
        .panel-mini-metrics {
            display: grid;
            gap: 6px;
            grid-template-columns: repeat(3, 1fr);
        }
        .panel-mini-metrics i {
            background: #ecfeff;
            border: 1px solid #ccfbf1;
            border-radius: 4px;
            height: 24px;
        }
        .panel-mini-chart {
            background:
                linear-gradient(90deg, transparent 24%, #e2e8f0 25%, transparent 26%, transparent 49%, #e2e8f0 50%, transparent 51%, transparent 74%, #e2e8f0 75%, transparent 76%),
                linear-gradient(#ffffff, #f8fafc);
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            height: 37px;
            margin-top: 7px;
            position: relative;
        }
        .panel-mini-chart::after {
            background: linear-gradient(90deg, #14b8a6 0 18%, #2563eb 18% 42%, #06b6d4 42% 68%, #f59e0b 68% 100%);
            border-radius: 3px 3px 0 0;
            bottom: 6px;
            content: "";
            height: 12px;
            left: 8px;
            position: absolute;
            width: 68%;
        }
        .panel-icon {
            align-items: center;
            background: linear-gradient(135deg, #2dd4bf, #2563eb);
            border: 3px solid rgba(255,255,255,0.82);
            border-radius: 11px;
            bottom: -18px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.24);
            color: white;
            display: flex;
            font-size: 1.25rem;
            font-style: normal;
            font-weight: 900;
            height: 44px;
            justify-content: center;
            left: 1.15rem;
            position: absolute;
            width: 44px;
        }
        .panel-body { padding: 1.25rem; }
        .panel-category {
            color: var(--cr-teal);
            font-size: 0.7rem;
            font-weight: 850;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        .panel-title {
            color: var(--cr-text);
            font-size: 1.16rem;
            font-weight: 850;
            margin: 0.22rem 0 0.35rem;
        }
        .panel-summary {
            color: var(--cr-muted);
            font-size: 0.84rem;
            line-height: 1.45;
            min-height: 3.7rem;
        }
        .panel-footer {
            align-items: center;
            border-top: 1px solid var(--cr-border);
            color: var(--cr-muted);
            display: flex;
            font-size: 0.74rem;
            font-weight: 700;
            justify-content: space-between;
            margin-top: 0.85rem;
            padding-top: 0.75rem;
        }
        .panel-open { color: var(--cr-blue); font-weight: 850; }
        .guide-back {
            color: var(--cr-muted);
            display: inline-block;
            font-size: 0.82rem;
            font-weight: 750;
            margin-bottom: 0.8rem;
            text-decoration: none;
        }
        .guide-back:hover { color: var(--cr-teal); }
        .guide-header {
            background:
                radial-gradient(circle at 92% 10%, rgba(45, 212, 191, 0.18), transparent 34%),
                color-mix(in srgb, var(--cr-surface) 94%, transparent);
            border: 1px solid var(--cr-border);
            border-radius: 14px;
            padding: 1.7rem;
        }
        .guide-heading-row {
            align-items: center;
            display: flex;
            gap: 1rem;
        }
        .guide-icon {
            align-items: center;
            background: linear-gradient(135deg, #14b8a6, #2563eb);
            border-radius: 13px;
            color: white;
            display: flex;
            flex: 0 0 54px;
            font-size: 1.5rem;
            font-weight: 900;
            height: 54px;
            justify-content: center;
        }
        .guide-title {
            color: var(--cr-text);
            font-size: clamp(1.8rem, 3vw, 2.6rem);
            font-weight: 850;
            letter-spacing: -0.035em;
            line-height: 1.05;
        }
        .guide-summary {
            color: var(--cr-muted);
            line-height: 1.55;
            margin: 1rem 0;
            max-width: 56rem;
        }
        .guide-meta, .objective-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .guide-meta span {
            background: var(--cr-surface-soft);
            border: 1px solid var(--cr-border);
            border-radius: 999px;
            color: var(--cr-text);
            font-size: 0.75rem;
            font-weight: 750;
            padding: 0.4rem 0.62rem;
        }
        .objective-chip {
            background: rgba(20, 184, 166, 0.10);
            border-color: rgba(20, 184, 166, 0.22);
            color: var(--cr-text);
        }
        .feature-map {
            background: color-mix(in srgb, var(--cr-surface) 94%, transparent);
            border: 1px solid var(--cr-border);
            border-radius: 14px;
            margin: 1rem 0 1.6rem;
            overflow: hidden;
            padding: 1.25rem;
        }
        .feature-browser {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.14);
            overflow: hidden;
        }
        .feature-browser-top {
            align-items: center;
            background: #e2e8f0;
            display: flex;
            gap: 5px;
            height: 28px;
            padding: 0 10px;
        }
        .feature-browser-top > span {
            background: #94a3b8;
            border-radius: 50%;
            height: 7px;
            width: 7px;
        }
        .feature-address {
            background: rgba(255,255,255,0.72);
            border-radius: 5px;
            color: #64748b;
            font-size: 9px;
            margin-left: 8px;
            padding: 3px 8px;
            width: min(320px, 55%);
        }
        .page-map-browser {
            background: linear-gradient(180deg, #f8fafc, #ecfeff);
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.14);
            overflow: hidden;
        }
        .page-map-header {
            align-items: center;
            display: flex;
            justify-content: space-between;
            padding: 1.35rem 1.4rem 0.6rem;
        }
        .page-map-page-title {
            color: #0f172a;
            font-size: 1.25rem;
            font-weight: 850;
            margin-top: 0.2rem;
        }
        .page-map-badge {
            background: #ccfbf1;
            border: 1px solid #99f6e4;
            border-radius: 999px;
            color: #115e59;
            font-size: 0.66rem;
            font-weight: 850;
            padding: 0.35rem 0.55rem;
        }
        .page-map-grid {
            display: grid;
            gap: 0.8rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            padding: 0.8rem 1.4rem 1.4rem;
        }
        .page-map-card {
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-radius: 9px;
            box-shadow: 0 7px 18px rgba(15, 23, 42, 0.05);
            min-height: 185px;
            padding: 0.85rem;
            position: relative;
        }
        .page-map-number {
            align-items: center;
            background: linear-gradient(135deg, #14b8a6, #2563eb);
            border-radius: 7px;
            color: #ffffff;
            display: flex;
            font-size: 0.65rem;
            font-weight: 900;
            height: 25px;
            justify-content: center;
            position: absolute;
            right: 0.7rem;
            top: 0.7rem;
            width: 25px;
            z-index: 2;
        }
        .page-map-preview {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 7px;
            height: 82px;
            margin-bottom: 0.7rem;
            overflow: hidden;
            padding: 0.65rem;
        }
        .page-map-title {
            color: #0f172a;
            font-size: 0.82rem;
            font-weight: 850;
        }
        .page-map-detail {
            color: #64748b;
            font-size: 0.68rem;
            line-height: 1.4;
            margin-top: 0.25rem;
        }
        .page-map-note {
            color: var(--cr-muted);
            font-size: 0.73rem;
            line-height: 1.45;
            margin-top: 0.85rem;
        }
        .map-metrics, .map-cards, .map-split {
            display: grid;
            gap: 0.4rem;
            grid-template-columns: repeat(4, 1fr);
            height: 100%;
        }
        .map-metrics i, .map-cards i, .map-split i {
            background: linear-gradient(180deg, #ffffff, #ecfeff);
            border: 1px solid #bae6fd;
            border-radius: 5px;
        }
        .map-cards { grid-template-columns: repeat(3, 1fr); }
        .map-split { grid-template-columns: repeat(2, 1fr); }
        .map-filter-row {
            display: grid;
            gap: 0.35rem;
            grid-template-columns: repeat(3, 1fr);
            margin-bottom: 0.45rem;
        }
        .map-filter-row i, .map-select, .map-search {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            height: 12px;
        }
        .map-table {
            display: grid;
            gap: 0.3rem;
        }
        .map-table b, .map-table i {
            background: #cbd5e1;
            border-radius: 3px;
            display: block;
            height: 7px;
        }
        .map-table b { background: #0f766e; }
        .map-table.compact { margin-top: 0.45rem; }
        .map-form, .map-review {
            display: grid;
            gap: 0.45rem;
            grid-template-columns: repeat(2, 1fr);
        }
        .map-form i, .map-review i {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            height: 16px;
        }
        .map-form i.wide, .map-review i.wide { grid-column: 1 / -1; }
        .map-form span {
            background: #14b8a6;
            border-radius: 999px;
            height: 5px;
            margin-top: 5px;
        }
        .map-score {
            display: grid;
            gap: 0.4rem;
            grid-template-columns: 1.2fr 0.7fr 1.4fr;
        }
        .map-score strong, .map-score i {
            align-items: center;
            background: #ecfeff;
            border: 1px solid #99f6e4;
            border-radius: 5px;
            color: #0f766e;
            display: flex;
            font-size: 0.65rem;
            font-style: normal;
            justify-content: center;
            min-height: 30px;
        }
        .map-tabs {
            display: flex;
            gap: 0.35rem;
            margin-top: 0.55rem;
        }
        .map-tabs b {
            background: #bae6fd;
            border-radius: 999px;
            height: 6px;
            width: 20%;
        }
        .map-chart {
            align-items: end;
            background: repeating-linear-gradient(0deg, transparent 0 14px, #e2e8f0 15px);
            display: flex;
            gap: 10%;
            height: 100%;
            justify-content: center;
            padding: 0 12%;
        }
        .map-chart i {
            background: linear-gradient(180deg, #2dd4bf, #2563eb);
            border-radius: 3px 3px 0 0;
            width: 13%;
        }
        .map-chart .bar-one { height: 35%; }
        .map-chart .bar-two { height: 70%; }
        .map-chart .bar-three { height: 50%; }
        .map-chart .bar-four { height: 82%; }
        .map-button {
            background: linear-gradient(135deg, #14b8a6, #2563eb);
            border-radius: 4px;
            height: 14px;
            margin-top: 0.5rem;
            width: 42%;
        }
        .map-button.long { width: 62%; }
        .map-chat {
            display: grid;
            gap: 0.35rem;
        }
        .map-chat i {
            background: #ccfbf1;
            border-radius: 7px 7px 7px 2px;
            height: 14px;
            width: 72%;
        }
        .map-chat i:nth-child(2) {
            background: #dbeafe;
            border-radius: 7px 7px 2px 7px;
            justify-self: end;
            width: 54%;
        }
        .map-accordion {
            display: grid;
            gap: 0.38rem;
        }
        .map-accordion i {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            height: 16px;
        }
        .map-search { height: 18px; width: 82%; }
        .map-notice {
            background: #ecfeff;
            border-left: 4px solid #14b8a6;
            border-radius: 4px;
            display: grid;
            gap: 0.4rem;
            padding: 0.75rem;
        }
        .map-notice i {
            background: #99f6e4;
            border-radius: 3px;
            height: 7px;
        }
        .map-notice i:last-child { width: 68%; }
        .feature-app { display: grid; grid-template-columns: 118px 1fr; min-height: 390px; }
        .feature-sidebar { background: linear-gradient(180deg, #111827, #0f3c46); padding: 28px 18px; }
        .feature-brand { background: #5eead4; border-radius: 4px; height: 9px; margin-bottom: 34px; width: 58px; }
        .feature-nav { background: rgba(226, 232, 240, 0.34); border-radius: 4px; height: 7px; margin-bottom: 18px; width: 72px; }
        .feature-nav.active { background: #2dd4bf; }
        .feature-nav.short { width: 48px; }
        .feature-main { background: linear-gradient(180deg, #f8fafc, #ecfeff); padding: 34px; }
        .feature-heading { align-items: center; display: flex; justify-content: space-between; }
        .feature-kicker { color: #0f766e; font-size: 9px; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }
        .feature-title-line { background: #0f172a; border-radius: 5px; height: 13px; margin-top: 8px; width: 178px; }
        .feature-action { background: linear-gradient(135deg, #14b8a6, #2563eb); border-radius: 6px; height: 30px; width: 92px; }
        .feature-metrics { display: grid; gap: 12px; grid-template-columns: repeat(3, 1fr); margin: 26px 0 18px; }
        .feature-metrics > div { background: white; border: 1px solid #dbeafe; border-radius: 8px; box-shadow: 0 6px 14px rgba(15,23,42,.05); padding: 14px; }
        .feature-metrics b { color: #0f766e; display: block; font-size: 17px; }
        .feature-metrics span { color: #475569; display: block; font-size: 9px; font-weight: 700; margin-top: 5px; }
        .feature-content { display: grid; gap: 16px; grid-template-columns: 1.6fr 1fr; }
        .feature-chart, .feature-detail { background: white; border: 1px solid #dbeafe; border-radius: 8px; min-height: 185px; position: relative; }
        .feature-chart { align-items: end; display: flex; gap: 9%; overflow: hidden; padding: 28px 12% 24px; }
        .chart-grid { background: repeating-linear-gradient(0deg, #e2e8f0 0 1px, transparent 1px 32px); inset: 16px; position: absolute; }
        .chart-bar { background: linear-gradient(180deg, #2dd4bf, #2563eb); border-radius: 4px 4px 0 0; flex: 1; max-width: 30px; position: relative; z-index: 1; }
        .chart-bar.h1 { height: 42%; }.chart-bar.h2 { height: 72%; }.chart-bar.h3 { height: 56%; }.chart-bar.h4 { height: 86%; }
        .feature-detail { padding: 22px; }
        .detail-label { color: #0f766e; font-size: 10px; font-weight: 850; }
        .detail-title { color: #0f172a; font-size: 13px; font-weight: 850; margin: 7px 0 20px; }
        .detail-row { background: #cbd5e1; border-radius: 4px; height: 7px; margin-bottom: 13px; width: 100%; }
        .detail-row.medium { width: 78%; }.detail-row.short { width: 52%; }
        .detail-button { background: #14b8a6; border-radius: 5px; height: 27px; margin-top: 26px; width: 84px; }
        .feature-callout {
            align-items: center;
            background: #f59e0b;
            border: 3px solid white;
            border-radius: 50%;
            box-shadow: 0 5px 12px rgba(15, 23, 42, .22);
            color: #0f172a;
            display: flex;
            font-size: 11px;
            font-weight: 900;
            height: 25px;
            justify-content: center;
            position: absolute;
            width: 25px;
            z-index: 2;
        }
        .callout-one { left: 7%; top: 12%; }.callout-two { right: 8%; top: 24%; }.callout-three { bottom: 10%; right: 9%; }
        .feature-legend { display: grid; gap: 8px; grid-template-columns: repeat(3, 1fr); margin-top: 1rem; }
        .feature-legend div { color: var(--cr-muted); font-size: 0.76rem; line-height: 1.4; }
        .feature-legend span {
            align-items: center;
            background: #f59e0b;
            border-radius: 50%;
            color: #0f172a;
            display: inline-flex;
            font-size: 0.68rem;
            font-weight: 900;
            height: 20px;
            justify-content: center;
            margin-right: 5px;
            width: 20px;
        }
        .step-card {
            background: color-mix(in srgb, var(--cr-surface) 95%, transparent);
            border: 1px solid var(--cr-border);
            border-radius: 12px;
            box-shadow: 0 9px 22px rgba(15,23,42,.04);
            display: grid;
            gap: 1rem;
            grid-template-columns: 48px 1fr;
            margin-bottom: 0.85rem;
            padding: 1.15rem;
        }
        .step-number {
            align-items: center;
            background: linear-gradient(135deg, #14b8a6, #2563eb);
            border-radius: 11px;
            color: white;
            display: flex;
            font-size: 1rem;
            font-weight: 900;
            height: 42px;
            justify-content: center;
            width: 42px;
        }
        .step-title { color: var(--cr-text); font-size: 1rem; font-weight: 850; }
        .step-body { color: var(--cr-muted); font-size: 0.86rem; line-height: 1.55; margin: 0.35rem 0 0.7rem; }
        .step-action {
            background: rgba(37, 99, 235, 0.08);
            border-left: 3px solid #2563eb;
            border-radius: 0 6px 6px 0;
            color: var(--cr-text);
            font-size: 0.8rem;
            line-height: 1.45;
            padding: 0.58rem 0.7rem;
        }
        .step-tip { color: var(--cr-muted); font-size: 0.76rem; line-height: 1.4; margin-top: 0.55rem; }
        .guide-finish {
            background: linear-gradient(135deg, rgba(20,184,166,.13), rgba(37,99,235,.10));
            border: 1px solid rgba(20,184,166,.24);
            border-radius: 12px;
            margin-top: 1.25rem;
            padding: 1.2rem;
        }
        .guide-finish-title { color: var(--cr-text); font-size: 1.02rem; font-weight: 850; }
        .guide-finish-copy { color: var(--cr-muted); font-size: .84rem; line-height: 1.5; margin: .3rem 0 .9rem; }
        @media (max-width: 760px) {
            .tutorial-hero-copy { padding: 2.3rem 1.4rem; }
            .tutorial-hero::after { background: rgba(2, 6, 23, 0.82); }
            .page-map-header { align-items: flex-start; gap: 0.7rem; }
            .page-map-badge { display: none; }
            .page-map-grid { grid-template-columns: 1fr; padding: 0.8rem; }
            .feature-app { grid-template-columns: 52px 1fr; }
            .feature-sidebar { padding: 24px 10px; }
            .feature-nav { width: 30px; }
            .feature-brand { width: 30px; }
            .feature-main { padding: 18px; }
            .feature-content { grid-template-columns: 1fr; }
            .feature-legend { grid-template-columns: 1fr; }
            .feature-metrics span { display: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _panel_html(tutorial):
    guide_href = escape(_tutorial_href(tutorial["slug"]), quote=True)
    return f"""
    <a class="tutorial-panel" href="{guide_href}" target="_self">
        <div class="panel-body">
            <div class="panel-category">{escape(tutorial["category"])}</div>
            <div class="panel-title">{escape(tutorial["title"])}</div>
            <div class="panel-summary">{escape(tutorial["summary"])}</div>
            <div class="panel-footer">
                <span>{escape(tutorial["time"])} · {escape(tutorial["level"])}</span>
                <span class="panel-open">View guide →</span>
            </div>
        </div>
    </a>
    """


def _render_hub():
    area_options = ["All areas"]
    for tutorial in ACTIVE_TUTORIALS:
        if tutorial["category"] not in area_options:
            area_options.append(tutorial["category"])
    intro_title = (
        "Prepare and track your application, one step at a time."
        if sme_mode
        else "Learn the workspace, one page at a time."
    )
    intro_copy = (
        "Open a panel for SME-facing guidance on company data, documents, submission, published results, and consultant support."
        if sme_mode
        else "Open a panel for a practical, text-based walkthrough of the page, its key features, and the decisions it helps you make."
    )
    st.markdown(
        f"""
        <section class="tutorial-intro">
            <div class="panel-category">{"YourBank SME Guide" if sme_mode else "CredRisk.AI Learning Hub"}</div>
            <div class="tutorial-intro-title">{escape(intro_title)}</div>
            <div class="tutorial-intro-copy">
                {escape(intro_copy)}
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    filter_left, filter_right = st.columns([2, 1])
    with filter_left:
        search = st.text_input(
            "Find a tutorial",
            placeholder="Search by page, feature, or task...",
            label_visibility="collapsed",
        )
    with filter_right:
        category = st.selectbox(
            "Tutorial area",
            area_options,
            label_visibility="collapsed",
        )

    search_value = search.strip().lower()
    visible = []
    for tutorial in ACTIVE_TUTORIALS:
        haystack = " ".join(
            [
                tutorial["title"],
                tutorial["summary"],
                tutorial["category"],
                *tutorial["features"],
                *tutorial["objectives"],
            ]
        ).lower()
        if search_value and search_value not in haystack:
            continue
        if category != "All areas" and tutorial["category"] != category:
            continue
        visible.append(tutorial)

    st.markdown(
        f"""
        <div class="tutorial-section-heading">
            <div>
                <div class="tutorial-section-title">Page tutorials</div>
                <div class="tutorial-section-copy">{len(visible)} guide{"s" if len(visible) != 1 else ""} available</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not visible:
        st.info(
            "No tutorials match that search. Try “documents”, “support”, or “application”."
        )
        return

    for start in range(0, len(visible), 3):
        columns = st.columns(3)
        for column, tutorial in zip(columns, visible[start : start + 3]):
            with column:
                st.markdown(_panel_html(tutorial), unsafe_allow_html=True)


def _render_guide(tutorial):
    hub_href = escape(_tutorial_href(), quote=True)
    st.markdown(
        f'<a class="guide-back" href="{hub_href}" target="_self">← Back to all tutorials</a>',
        unsafe_allow_html=True,
    )
    objectives = "".join(
        f'<span class="objective-chip">{escape(objective)}</span>'
        for objective in tutorial["objectives"]
    )
    st.markdown(
        f"""
        <section class="guide-header">
            <div class="guide-heading-row">
                <div>
                    <div class="tutorial-kicker">{escape(tutorial["category"])} tutorial</div>
                    <div class="guide-title">{escape(tutorial["title"])}</div>
                </div>
            </div>
            <div class="guide-summary">{escape(tutorial["summary"])}</div>
            <div class="guide-meta">
                <span>{escape(tutorial["time"])}</span>
                <span>{escape(tutorial["level"])}</span>
                <span>4 guided steps</span>
            </div>
            <div class="objective-row" style="margin-top: .9rem;">{objectives}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="tutorial-section-heading">
            <div>
                <div class="tutorial-section-title">Step-by-step guide</div>
                <div class="tutorial-section-copy">Follow the normal path through this page.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for index, step in enumerate(tutorial["steps"], start=1):
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-number">{index:02d}</div>
                <div>
                    <div class="step-title">{escape(step["title"])}</div>
                    <div class="step-body">{escape(step["body"])}</div>
                    <div class="step-action"><strong>Try this:</strong> {escape(step["action"])}</div>
                    <div class="step-tip"><strong>Good to know:</strong> {escape(step["tip"])}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="guide-finish">
            <div class="guide-finish-title">Ready to try it in the workspace?</div>
            <div class="guide-finish-copy">
                Open {escape(tutorial["title"])} and follow the four steps with the live demo data.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    link_col, back_col, _ = st.columns([1, 1, 2])
    with link_col:
        safe_page_link(
            tutorial["page"], f"Open {tutorial['title']}", ":material/open_in_new:"
        )
    with back_col:
        st.markdown(
            f'<a class="guide-back" href="{hub_href}" target="_self">Browse another guide</a>',
            unsafe_allow_html=True,
        )


_render_styles()
selected_slug = _query_value("guide")
selected_tutorial = next(
    (tutorial for tutorial in ACTIVE_TUTORIALS if tutorial["slug"] == selected_slug),
    None,
)

if selected_tutorial:
    _render_guide(selected_tutorial)
else:
    _render_hub()
