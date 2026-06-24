LENDER_ACRONYM_ROWS = [
    {
        "Term": "DSCR",
        "Meaning": "Debt Service Coverage Ratio",
        "How to read it": "Compares cash available for debt service with required loan payments. A value above 1.00 means estimated cash flow covers payments; below 1.00 means it does not.",
        "Where used": "Personal Workspace score output, risk drivers, loan terms, monitoring preview",
    },
    {
        "Term": "Stressed DSCR",
        "Meaning": "Debt Service Coverage Ratio under stress",
        "How to read it": "Recalculates DSCR after a +2 percentage point interest-rate stress. It shows whether repayment still works if rates or pricing move against the borrower.",
        "Where used": "Personal Workspace score output and debt-service risk",
    },
    {
        "Term": "FCF",
        "Meaning": "Free Cash Flow",
        "How to read it": "Cash generated after operating and investment needs. Positive FCF supports repayment; weak or negative FCF increases cash-flow pressure.",
        "Where used": "Financial snapshot, score output, forecast, risk drivers",
    },
    {
        "Term": "CAGR",
        "Meaning": "Compound Annual Growth Rate",
        "How to read it": "Average annual growth assumption over a period. High CAGR needs support from contracts, pipeline, staffing, and capacity evidence.",
        "Where used": "Five-Year Plan, forecast signals, scenario analysis",
    },
    {
        "Term": "KYB",
        "Meaning": "Know Your Business",
        "How to read it": "Business identity and ownership verification, including registry, directors, UBOs, sanctions, and related-party checks.",
        "Where used": "Evidence checklist, data readiness, risk drivers",
    },
    {
        "Term": "UBO",
        "Meaning": "Ultimate Beneficial Owner",
        "How to read it": "The person or persons who ultimately own or control the business. Weak UBO evidence can increase KYB review needs.",
        "Where used": "Ownership/KYB documents and registry checks",
    },
    {
        "Term": "PSD2",
        "Meaning": "Payment Services Directive 2",
        "How to read it": "Represents consented open-banking access in the demo. It supports bank-account history, balance, inflow, outflow, and transaction-behavior checks.",
        "Where used": "SME portal connections, Personal Workspace evidence readiness",
    },
    {
        "Term": "ROC-AUC",
        "Meaning": "Receiver Operating Characteristic - Area Under Curve",
        "How to read it": "Model validation metric for ranking high-risk cases above lower-risk cases. It explains model quality overall, not one individual decision.",
        "Where used": "Model confidence and governance",
    },
    {
        "Term": "LLM",
        "Meaning": "Large Language Model",
        "How to read it": "Optional second-review and report-generation layer. It must remain separate from the supervised model score and human analyst decision.",
        "Where used": "LLM Integration and AI evaluation package",
    },
    {
        "Term": "SHA-256",
        "Meaning": "Cryptographic file hash",
        "How to read it": "A fingerprint of saved document bytes. If the same bytes are downloaded later, the hash confirms the demo vault file did not silently change.",
        "Where used": "SME uploads, lender evidence tab, document validation",
    },
    {
        "Term": "SLA",
        "Meaning": "Service Level Agreement",
        "How to read it": "Operational deadline or review expectation for the case. SLA urgency is separate from credit risk.",
        "Where used": "Home, Operations Desk, queue views",
    },
]

SME_ACRONYM_ROWS = [
    {
        "Term": "PSD2",
        "Meaning": "Payment Services Directive 2",
        "How to read it": "In this MVP, it represents simulated consent for open-banking evidence. It shows how a company would connect bank data in production.",
        "Where used": "Company Portal connections",
    },
    {
        "Term": "Open Banking",
        "Meaning": "Consented bank-data sharing",
        "How to read it": "A way for a company to share bank-account evidence with a lender. In this demo it is simulated and does not connect to a real bank.",
        "Where used": "Company Portal connections",
    },
    {
        "Term": "KYB",
        "Meaning": "Know Your Business",
        "How to read it": "Checks that help a lender understand company identity, ownership, and registration details.",
        "Where used": "Ownership/KYB document upload and application readiness",
    },
    {
        "Term": "UBO",
        "Meaning": "Ultimate Beneficial Owner",
        "How to read it": "The person or persons who ultimately own or control the company.",
        "Where used": "Ownership/KYB evidence",
    },
    {
        "Term": "FCF",
        "Meaning": "Free Cash Flow",
        "How to read it": "Cash left after operating and investment needs. A stronger cash-flow profile can help a company explain repayment capacity.",
        "Where used": "Company profile and published improvement guidance",
    },
    {
        "Term": "CAGR",
        "Meaning": "Compound Annual Growth Rate",
        "How to read it": "Average yearly growth in a forecast. Growth assumptions are more useful when supported by contracts, pipeline, or operating plans.",
        "Where used": "Company forecast and post-rating what-if planner",
    },
    {
        "Term": "DSCR",
        "Meaning": "Debt Service Coverage Ratio",
        "How to read it": "A repayment-capacity measure. The SME portal does not expose the lender's internal scoring logic, but stronger cash flow generally helps repayment resilience.",
        "Where used": "General lending language and consultant conversations",
    },
    {
        "Term": "SHA-256",
        "Meaning": "File fingerprint",
        "How to read it": "A technical fingerprint for saved files. It helps show that the uploaded demo file bytes stayed the same.",
        "Where used": "Saved documents",
    },
]

LENDER_METRIC_ROWS = [
    {
        "Metric": "Application risk score",
        "How to read it": "Model-estimated risk on a 0-100% scale. Higher means the file looks riskier relative to the synthetic portfolio; it is decision support, not an automatic rejection.",
        "Where used": "Personal Workspace score output",
    },
    {
        "Metric": "Model grade",
        "How to read it": "A-F grade derived from the model risk score. It remains separate from the analyst's reviewed rating for auditability.",
        "Where used": "Personal Workspace, Risk Dashboard, LLM Integration",
    },
    {
        "Metric": "Document completeness",
        "How to read it": "Share of expected document categories present. Higher is better, but it does not prove authenticity or category correctness.",
        "Where used": "Evidence, data readiness, risk drivers",
    },
    {
        "Metric": "Document quality risk",
        "How to read it": "Risk from missing, weak, or potentially inconsistent evidence. Higher values mean document validation should happen before relying on the score.",
        "Where used": "Risk drivers and calculated risk signals",
    },
    {
        "Metric": "Grade boundary distance",
        "How to read it": "How close the score is to an A-F threshold. Lower values mean fresh evidence or analyst judgment could more easily change the reviewed outcome.",
        "Where used": "Model confidence and governance",
    },
    {
        "Metric": "Narrative consistency risk",
        "How to read it": "Potential contradiction between applicant story, financials, and documents. Higher values mean the analyst should resolve the mismatch before publication.",
        "Where used": "Risk drivers and calculated risk signals",
    },
]

SME_METRIC_ROWS = [
    {
        "Metric": "Application readiness",
        "How to read it": "Shows whether the company profile, documents, and simulated connections are ready for lender review. It is not a lender decision.",
        "Where used": "Company Portal Credit Health",
    },
    {
        "Metric": "Published rating",
        "How to read it": "The lender-reviewed rating shown only after publication. Before publication, the SME portal does not expose internal lender scores.",
        "Where used": "Company Portal after publication",
    },
    {
        "Metric": "Numerical score",
        "How to read it": "Appears only if the lender chooses to publish it. If not published, the SME sees the rating, decision, message, and report instead.",
        "Where used": "Company Portal after publication",
    },
    {
        "Metric": "Evidence package",
        "How to read it": "Applicant-safe summary of document readiness. It helps show whether a future review may benefit from stronger or more complete evidence.",
        "Where used": "Post-rating improvement planner",
    },
    {
        "Metric": "What-if band",
        "How to read it": "Directional planning output for future improvements. It does not change the lender's published rating or decision.",
        "Where used": "Post-rating what-if planner",
    },
]


def acronym_rows(sme_mode=False):
    return SME_ACRONYM_ROWS if sme_mode else LENDER_ACRONYM_ROWS


def metric_rows(sme_mode=False):
    return SME_METRIC_ROWS if sme_mode else LENDER_METRIC_ROWS
