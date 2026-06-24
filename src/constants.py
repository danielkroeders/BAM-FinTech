FIELD_HELP = {
    "company_name": "Applicant company name used for the session case record and downloadable summary.",
    "industry": "Primary business sector. Sector patterns can affect fraud exposure and cash-flow volatility.",
    "region": "Applicant operating region. Regional context contributes to the risk profile.",
    "company_type": "Legal or operating structure, such as LLC, corporation, partnership, or sole proprietorship.",
    "years_in_business": "How long the company has operated. Short histories can reduce verification depth.",
    "employees": "Reported employee count, used to compare company scale with revenue and requested exposure.",
    "requested_amount": "Loan principal requested by the applicant.",
    "term_months": "Requested duration of the loan in months.",
    "interest_rate": "Offered annual interest rate used to estimate debt service, interest expense, and DSCR stress.",
    "collateral_ratio": "Estimated collateral value divided by requested loan amount.",
    "existing_debt": "Reported outstanding business debt at application date.",
    "num_recent_loans": "Number of recent loans in the last 12 months. High values can indicate credit stacking.",
    "annual_revenue": "Reported yearly business revenue.",
    "free_cash_flow": "Annual cash generated after operating and investment needs.",
    "monthly_burn_rate": "Estimated monthly cash consumption at application date.",
    "expected_runway_months": "Estimated months the applicant can sustain current burn with available cash.",
    "cash_flow_to_revenue_ratio": "Free cash flow divided by annual revenue, calculated automatically.",
    "late_payment_ratio": "Share of observed payments that were late in the transaction profile.",
    "suspicious_transfer_ratio": "Share of transfers flagged as unusual in the transaction profile.",
    "country_risk_score": "Jurisdictional risk score from 0 to 1.",
    "forecast_revenue_cagr": "Expected average annual revenue growth over the next five years.",
    "forecast_employee_cagr": "Expected average annual employee growth over the next five years.",
    "forecast_fcf_margin_year5": "Target free-cash-flow margin by year five.",
    "planned_debt_reduction_pct": "Planned reduction in existing debt over the five-year forecast horizon.",
    "current_ratio": "Current assets divided by current liabilities; lower values can signal liquidity pressure.",
    "quick_ratio": "Liquid assets divided by current liabilities; excludes inventory-heavy support.",
    "receivables_days": "Estimated days sales remain outstanding before collection.",
    "payables_days": "Estimated days the applicant takes to pay suppliers.",
    "inventory_days": "Estimated days inventory remains before sale or use.",
    "financial_statements_uploaded": "Whether financial statements are already present in the application package.",
    "bank_statements_uploaded": "Whether bank statements are already present in the application package.",
    "tax_return_uploaded": "Whether recent tax documentation is already present in the application package.",
    "ownership_docs_uploaded": "Whether ownership and KYB documentation is already present in the application package.",
    "forecast_support_uploaded": "Whether supporting material for the five-year plan is already present.",
    "email_domain_age_months": "Estimated age of the applicant email domain in months.",
    "website_age_months": "Estimated age of the applicant website in months.",
    "bank_account_age_months": "Estimated age of the primary business bank account in months.",
    "loan_purpose_context": "Applicant-provided reason for the loan and intended use of funds.",
    "current_business_context": "Applicant-provided context for current operating conditions, recent performance, and key constraints.",
    "future_business_context": "Applicant-provided context for expected changes after funding, outside the formal five-year forecast table.",
    "ceo_context": "CEO narrative context for strategy, market demand, and growth plan.",
    "cfo_context": "CFO narrative context for liquidity, debt, cash flow, and funding need.",
    "coo_context": "COO narrative context for operations, capacity, staffing, and execution risk.",
}

WORKSPACE_HELP = {
    "assigned_cases": "Applications currently assigned to Ms. Cooper in the demo work queue. This is a workload indicator, not a risk signal.",
    "same_day_sla": "Assigned applications marked for same-day review. A higher count means the analyst should triage time-sensitive files first.",
    "due_this_week": "Assigned applications due this week after same-day items. This helps separate operational urgency from credit risk.",
    "manual_or_compliance": "Assigned applications routed to manual review or compliance review because the model, documents, or operating signals require human attention.",
    "missing_documents": "Assigned applications that still have one or more missing documents. Missing evidence can reduce confidence even when the model grade looks acceptable.",
    "application_risk_score": "Model-estimated application risk on a 0-100% scale. Higher percentages mean the file looks riskier relative to the synthetic training portfolio; this is decision support, not an automatic rejection.",
    "risk_grade": "Immutable A-F model grade derived from the application risk score. The analyst can publish a separate reviewed rating, but the model grade remains visible for auditability.",
    "model_recommendation": "Decision-support recommendation produced by the local scoring model. It summarizes what the model suggests before the analyst checks documents, context, and policy exceptions.",
    "ml_technique": "Supervised ML technique used for this score. Both options convert the same application fields into a 0-1 application risk probability so analysts can compare model behavior.",
    "stressed_dscr": "Debt Service Coverage Ratio after adding a +2 percentage point interest-rate stress. Above 1.00 means projected cash flow still covers estimated debt service; below 1.00 means the borrower may not cover payments under stress.",
    "final_decision": "Latest analyst decision recorded for this case. Pending Review means no final human action has been saved, even if the model already produced a grade.",
    "review_status": "Timestamp of the latest saved review, or Awaiting analyst before review submission. This separates scoring from the human decision trail.",
}

METRIC_EXPLANATIONS = {
    "Interest rate": "Annual pricing used to estimate interest expense and debt-service burden. A higher rate can make an otherwise acceptable borrower look stressed because payments become harder to cover.",
    "Annual interest": "Estimated yearly interest cost on the requested facility. Read it together with free cash flow: if interest consumes too much cash generation, repayment resilience weakens.",
    "Annual debt service": "Estimated total yearly principal and interest payments. This is the denominator used in DSCR-style repayment-capacity checks.",
    "DSCR": "Debt Service Coverage Ratio before the rate stress. Values above 1.00 indicate expected cash flow covers debt service; values closer to or below 1.00 leave little room for shocks.",
    "Stressed DSCR (+2%)": "Debt Service Coverage Ratio after adding a +2 percentage point rate stress. This is intentionally conservative and shows whether repayment still works if pricing or rates deteriorate.",
    "Stress DSCR (+2%)": "Debt Service Coverage Ratio after adding a +2 percentage point rate stress. This is intentionally conservative and shows whether repayment still works if pricing or rates deteriorate.",
    "Free cash flow": "Cash available after operations and investment needs. Positive FCF is a repayment strength; weak or negative FCF pushes the analyst toward conditions, lower exposure, or rejection.",
    "Monthly burn": "Estimated cash consumed per month. High burn shortens runway and makes the timing of new funding more important.",
    "Cash flow / revenue": "Free cash flow divided by revenue. This shows whether sales turn into usable cash; weak conversion can expose fragile reported growth.",
    "Expected runway": "How many months the business can continue at current burn. Short runway increases liquidity risk and may require faster monitoring or additional evidence.",
    "Current ratio": "Current assets divided by current liabilities. It is a broad liquidity check: higher values usually mean more short-term resources to meet obligations.",
    "Quick ratio": "Liquid assets divided by current liabilities, excluding inventory-heavy support. It is stricter than current ratio and useful when inventory may not convert to cash quickly.",
    "Cash conversion cycle": "Working-capital timing in days. Longer cycles mean cash is tied up in receivables or inventory for longer before it returns to the business.",
    "Revenue CAGR": "Average annual revenue-growth assumption in the five-year plan. Strong growth improves scale only when contracts, pipeline, staffing, and cash conversion support it.",
    "Employee CAGR": "Average annual employee-growth assumption. If revenue grows much faster than staff or capacity, the plan may need operational support evidence.",
    "Y5 FCF margin": "Forecast free-cash-flow margin in year five. This tests whether the growth plan improves cash generation, not just revenue.",
    "Debt reduction": "Planned reduction in existing debt. It is positive when realistic, but aggressive reduction can strain cash if current FCF is weak.",
    "Applicant narrative": "Completeness of applicant-provided context. Complete narrative makes it easier to reconcile the loan purpose, operating position, and forecast with documents.",
    "Statement anomaly": "Normalized signal for revenue/cash-flow mismatch, receivables pressure, or unsupported margin improvement. Higher values deserve closer evidence review.",
    "Document complete": "Share of expected document categories present. A high score means the file is complete; it does not prove every document is genuine.",
    "Document risk": "Normalized risk from missing or weak evidence. Higher values mean the analyst should validate the package before relying on the model result.",
    "Process risk": "Normalized signal for late-stage edits, process deviations, or unusual submission metadata. Higher values indicate the intake trail deserves review.",
    "Identity risk": "Normalized KYB and digital-footprint risk. Higher values mean company identity, account age, address, or duplicate-contact signals need confirmation.",
    "Working capital risk": "Normalized liquidity and cash-conversion pressure. Higher values suggest cash may be tied up before it can service debt.",
    "Network risk": "Normalized related-party, concentration, or shared-identifier concern. Higher values indicate the ownership/counterparty network should be reviewed.",
    "Narrative risk": "Normalized contradiction signal between applicant story, financials, and documents. Higher values mean the analyst should ask clarifying questions.",
}

SIGNAL_INTERPRETATIONS = {
    "Debt / revenue": "Lower is generally easier to support. A high ratio means existing obligations are large relative to the company’s operating scale, so new lending may need tighter covenants or a lower amount.",
    "Request / revenue": "This compares the requested exposure with annual revenue. A high value does not automatically reject a case, but it means the loan is material enough to require stronger evidence and repayment rationale.",
    "Loan velocity": "Higher values indicate many recent loans or borrowing events. That can be normal for some firms, but it can also signal credit stacking or funding stress.",
    "Payment stress": "Higher values combine late-payment behavior and debt pressure. Read this as a warning that historical payment discipline may not support the requested structure.",
    "External financing pressure": "Higher values mean the company is leaning more heavily on outside financing relative to its size and recent debt activity.",
    "Financial distress": "This rolls up debt load, payment pressure, collateral support, and business history. Higher values tell the analyst to slow down and reconcile repayment capacity before approval.",
    "Transaction anomaly": "Higher values indicate unusual transfer patterns in the synthetic transaction profile. It is a review prompt, not proof of fraud.",
    "Cash-flow pressure": "Higher values mean weaker free cash flow, burn-rate pressure, or limited runway. This is one of the most practical repayment-capacity signals.",
    "Runway risk": "Higher values mean the applicant has fewer months of cash cushion. Short runway increases the chance that timing, not just profitability, drives the decision.",
    "Cash conversion risk": "Higher values mean revenue is not translating into cash quickly enough. The analyst should check receivables, inventory, and customer payment terms.",
    "Forecast aggressiveness": "Higher values mean the five-year plan assumes a larger jump from current performance. It needs stronger contract, pipeline, or operating evidence.",
    "Forecast execution risk": "Higher values mean the forecast may be difficult to execute given current margins, staffing, cash flow, or evidence quality.",
    "Hiring efficiency risk": "Higher values mean revenue growth may be under-supported by staffing or capacity growth. The plan may need operational proof.",
    "Debt service plan risk": "Higher values mean the proposed debt reduction or repayment plan may strain cash flow instead of improving resilience.",
    "Interest rate risk": "Higher values mean pricing itself creates repayment burden. This is especially important when market rates or margin pressure could rise.",
    "Debt service stress": "Higher values mean DSCR weakens under normal and stressed payment assumptions. Check whether cash flow still covers debt service with a cushion.",
    "Cash conversion cycle": "Longer cycles mean cash is tied up for more days before returning to the business. That can create liquidity pressure even when revenue is growing.",
    "Document completeness": "Higher is better here. It means the expected application package is present, but the lender still needs validation for content and category fit.",
    "Document quality risk": "Higher values mean the file has missing, weak, or potentially inconsistent evidence. Treat it as a reason to validate documents before relying on the score.",
    "Process integrity risk": "Higher values indicate late edits or unusual intake-process metadata. The issue may be benign, but the audit trail needs attention.",
    "Identity verification risk": "Higher values mean KYB, account age, digital footprint, or location consistency is weaker. Confirm ownership and business identity.",
    "Working-capital pressure": "Higher values mean liquidity ratios and cash-conversion timing are less comfortable. It affects whether the borrower can absorb delays or shocks.",
    "Financial statement anomaly": "Higher values mean reported performance may not line up with cash flow or working-capital behavior. Ask for reconciliation evidence.",
    "Related-party network risk": "Higher values indicate concentration, shared identifiers, or relationship patterns that may affect independence or repayment reliability.",
    "Narrative consistency risk": "Higher values mean the applicant story does not fully line up with documents or financial signals. The analyst should resolve the contradiction before publication.",
}

METRIC_CATALOG = {
    "Accuracy": "accuracy",
    "Balanced Accuracy": "balanced_accuracy",
    "Precision": "precision",
    "Recall": "recall",
    "F1": "f1",
    "ROC-AUC": "roc_auc",
    "Average Precision": "average_precision",
    "MCC": "mcc",
    "Precision At Top 5%": "precision_at_5pct",
    "Precision At Top 10%": "precision_at_10pct",
    "Precision At Top 20%": "precision_at_20pct",
    "False Positive Rate": "false_positive_rate",
    "False Negative Rate": "false_negative_rate",
    "Predicted Review Rate": "predicted_review_rate",
    "Estimated Review Cost": "estimated_review_cost",
    "Estimated False Positive Cost": "estimated_false_positive_cost",
    "Estimated False Negative Cost": "estimated_false_negative_cost",
    "Estimated Total Error Cost": "estimated_total_error_cost",
}

METRIC_HELP = {
    "Accuracy": "Share of all predictions that are correct. Misleading when high-risk cases are rare — prefer Balanced Accuracy.",
    "Balanced Accuracy": "Average accuracy across high-risk and low-risk classes. Corrects for class imbalance; a fairer headline score than raw Accuracy.",
    "Precision": "Of every application the model flags as high-risk, the share that truly is. High Precision means fewer good applicants wrongly declined.",
    "Recall": "Of every genuinely high-risk application, the share the model catches. High Recall means fewer defaults slip through undetected.",
    "F1": "Harmonic mean of Precision and Recall. Useful when you need a single number that balances both miss types.",
    "ROC-AUC": "Probability that the model ranks a random high-risk case above a random low-risk one. 0.5 = coin flip; 1.0 = perfect separation.",
    "Average Precision": "Area under the Precision-Recall curve. More informative than ROC-AUC when defaults are rare; penalises models that miss the tail.",
    "MCC": "Matthews Correlation Coefficient — a single quality score robust to class imbalance. Ranges from −1 (worse than random) to +1 (perfect).",
    "Precision At Top 5%": "Of the 5% of applications the model scores as highest-risk, the share that are genuinely high-risk. Relevant for a very selective review queue.",
    "Precision At Top 10%": "Of the top-decile highest-risk applications, the share that are genuinely high-risk. The primary queue-efficiency metric for most review teams.",
    "Precision At Top 20%": "Of the top quintile, the share that are genuinely high-risk. Useful when bandwidth allows a broader review sweep.",
    "False Positive Rate": "Share of low-risk applicants incorrectly flagged as high-risk. Drives unnecessary review cost and approval friction for good customers.",
    "False Negative Rate": "Share of high-risk applicants the model misses entirely. Each miss is a potential default that reaches the portfolio undetected.",
    "Predicted Review Rate": "Fraction of all applications the model routes to manual review under current thresholds. Directly sets analyst workload.",
    "Estimated Review Cost": "Total estimated cost of manually reviewing every flagged case at current review-rate and cost assumptions.",
    "Estimated False Positive Cost": "Revenue lost by declining or over-scrutinising applications that would have performed well.",
    "Estimated False Negative Cost": "Expected default losses from high-risk applications the model approved or under-flagged.",
    "Estimated Total Error Cost": "Sum of false-positive (lost revenue) and false-negative (default loss) costs. The primary financial headline for portfolio risk.",
}

PROVIDERS = ["Deterministic", "OpenAI API", "Local server"]

MODEL_DESCRIPTIONS = {
    "random_forest": "Tree-based ensemble used to produce the baseline application risk score.",
    "logistic_regression": "Linear probability model used to produce the baseline application risk score.",
}

ALLOWED_DOCUMENT_TYPES = ["pdf", "csv", "xlsx", "xls", "docx", "png", "jpg", "jpeg"]

PROFILE_TYPES = [
    "Team Member",
    "Team Manager",
    "Risk Lead",
    "Support Specialist",
    "Read-only Reviewer",
]
PERMISSIONS = [
    "Credit review and manual decision approval",
    "Credit review",
    "Portfolio monitoring",
    "Team management",
    "Read-only portfolio access",
    "Administrator",
]
MANAGERS = ["Ravi Meijer", "Mila Verhoeven", "Daan Peters", "Sofia de Vries"]

CHANNELS = ["Slack", "Teams", "Email"]

EMAIL_APPS = ["Outlook", "Gmail"]

INTEGRATION_CATALOG = [
    {
        "key": "slack",
        "name": "Slack",
        "category": "Messaging",
        "account": "#sme-credit-ops",
        "use": "Queue alerts and analyst handoffs.",
    },
    {
        "key": "teams",
        "name": "Microsoft Teams",
        "category": "Messaging",
        "account": "SME Credit Review",
        "use": "Team calls, approvals, and case escalations.",
    },
    {
        "key": "gmail",
        "name": "Gmail",
        "category": "Email & Calendar",
        "account": "alice.cooper@yourbank.com",
        "use": "Personal inbox, drafts, and email follow-ups.",
    },
    {
        "key": "outlook",
        "name": "Outlook",
        "category": "Email & Calendar",
        "account": "alice.cooper@yourbank.com",
        "use": "Personal calendar, mailbox, and reminders.",
    },
    {
        "key": "google_drive",
        "name": "Google Drive",
        "category": "Personal Files",
        "account": "Alice Cooper Drive",
        "use": "Personal notes, exports, and working files.",
    },
    {
        "key": "onedrive",
        "name": "OneDrive",
        "category": "Personal Files",
        "account": "Alice Cooper OneDrive",
        "use": "Personal drafts, downloads, and local working files.",
    },
    {
        "key": "sharepoint",
        "name": "SharePoint",
        "category": "Personal Files",
        "account": "Alice Cooper workspace",
        "use": "Personal team folders and shared working documents.",
    },
    {
        "key": "zoom",
        "name": "Zoom",
        "category": "Meetings",
        "account": "alice.cooper@yourbank.com",
        "use": "Personal meeting links and review calls.",
    },
]

DIMENSIONS = [
    {
        "Dimension": "Industry",
        "Definition": "The applicant company's primary business sector.",
        "Why it matters": "Fraud patterns and cash-flow volatility can differ by sector.",
    },
    {
        "Dimension": "Region",
        "Definition": "The applicant's operating or lending region.",
        "Why it matters": "Regional market conditions and country-risk assumptions affect fraud exposure.",
    },
    {
        "Dimension": "Company type",
        "Definition": "The applicant's legal or operating structure, such as LLC, corporation, partnership, or sole proprietorship.",
        "Why it matters": "Entity structure can correlate with documentation depth and verification complexity.",
    },
    {
        "Dimension": "Requested amount",
        "Definition": "The loan principal requested by the applicant.",
        "Why it matters": "Large requests relative to business scale can indicate elevated repayment or anomaly risk.",
    },
    {
        "Dimension": "Term months",
        "Definition": "The requested loan duration in months.",
        "Why it matters": "Loan duration shapes exposure time and can interact with cash-flow risk.",
    },
    {
        "Dimension": "Interest rate",
        "Definition": "The offered annual interest rate for the requested facility.",
        "Why it matters": "Higher pricing can materially increase debt-service burden and reduce repayment coverage.",
    },
    {
        "Dimension": "Annual revenue",
        "Definition": "The applicant's reported yearly business revenue.",
        "Why it matters": "Revenue is used to assess business scale and whether the requested amount is proportionate.",
    },
    {
        "Dimension": "Years in business",
        "Definition": "How long the company has been operating.",
        "Why it matters": "Short operating histories may provide less evidence for identity, stability, and repayment behavior.",
    },
    {
        "Dimension": "Existing debt",
        "Definition": "The applicant's reported outstanding business debt.",
        "Why it matters": "High debt pressure relative to revenue can signal credit stacking or financial stress.",
    },
    {
        "Dimension": "Recent loans in the last 12 months",
        "Definition": "Count of new or recent loan obligations within the past year.",
        "Why it matters": "Multiple recent loans can indicate rapid borrowing behavior that merits review.",
    },
    {
        "Dimension": "Late payment ratio",
        "Definition": "Share of observed payments that were late.",
        "Why it matters": "Higher late-payment behavior can indicate repayment stress or unreliable payment patterns.",
    },
    {
        "Dimension": "Suspicious transfer ratio",
        "Definition": "Share of transfers flagged as unusual in the transaction profile.",
        "Why it matters": "Unusual transfer patterns can be a fraud indicator and are weighted heavily in the model.",
    },
    {
        "Dimension": "Collateral ratio",
        "Definition": "Estimated collateral value divided by the requested loan amount.",
        "Why it matters": "Lower collateral coverage can increase loss exposure and raise review priority.",
    },
    {
        "Dimension": "Employees",
        "Definition": "Reported number of employees at the applicant company.",
        "Why it matters": "Employee count helps establish company scale and consistency with revenue and loan size.",
    },
    {
        "Dimension": "Country risk score",
        "Definition": "A score from 0 to 1 representing jurisdictional or country-level risk.",
        "Why it matters": "Higher values indicate greater contextual risk assumptions.",
    },
    {
        "Dimension": "Free cash flow",
        "Definition": "Annual cash generated after operating and investment needs.",
        "Why it matters": "Positive free cash flow can mitigate risk, while negative cash flow can indicate liquidity pressure.",
    },
    {
        "Dimension": "Monthly burn rate",
        "Definition": "Estimated monthly cash consumption at application date.",
        "Why it matters": "High burn can shorten runway and increase pressure to obtain external financing.",
    },
    {
        "Dimension": "Cash flow / revenue",
        "Definition": "Free cash flow divided by annual revenue.",
        "Why it matters": "Shows whether reported revenue is converting into usable cash.",
    },
    {
        "Dimension": "Expected runway months",
        "Definition": "Estimated months cash reserves can support the current burn rate.",
        "Why it matters": "Short runway can raise liquidity risk and review priority.",
    },
    {
        "Dimension": "Expected annual revenue growth",
        "Definition": "Applicant's expected compound annual revenue growth over five years.",
        "Why it matters": "Aggressive growth assumptions can increase execution risk when unsupported by current signals.",
    },
    {
        "Dimension": "Expected annual employee growth",
        "Definition": "Applicant's expected compound annual employee growth over five years.",
        "Why it matters": "Employee growth helps assess whether revenue growth is operationally supported.",
    },
    {
        "Dimension": "Year 5 FCF margin target",
        "Definition": "Target free-cash-flow margin at the end of the five-year plan.",
        "Why it matters": "Large margin improvement from weak current cash flow can signal plan risk.",
    },
    {
        "Dimension": "Planned debt reduction",
        "Definition": "Share of existing debt management expects to reduce over five years.",
        "Why it matters": "Debt reduction plans can be strained when current cash-flow pressure is high.",
    },
    {
        "Dimension": "Current and quick ratios",
        "Definition": "Liquidity ratios summarizing current assets and liquid assets against current liabilities.",
        "Why it matters": "Weak short-term liquidity can reveal stress not visible from revenue alone.",
    },
    {
        "Dimension": "Receivables, payables, and inventory days",
        "Definition": "Working-capital timing assumptions used to estimate cash conversion cycle.",
        "Why it matters": "Long collection or inventory cycles can pressure cash flow and repayment capacity.",
    },
    {
        "Dimension": "Document checklist",
        "Definition": "Present/not-present status for financial statements, bank statements, tax return, KYB, and forecast support.",
        "Why it matters": "Missing support can reduce audit readiness and increase manual review priority.",
    },
    {
        "Dimension": "Digital identity age",
        "Definition": "Age of email domain, website, and primary business bank account in months.",
        "Why it matters": "Very young identity markers can increase KYB verification risk.",
    },
    {
        "Dimension": "Mismatch and duplicate signals",
        "Definition": "Scores for location mismatch, duplicate contact details, and shared identifiers.",
        "Why it matters": "Shared or inconsistent identifiers can indicate entity-resolution or application-channel risk.",
    },
    {
        "Dimension": "Related-party and counterparty signals",
        "Definition": "Scores for related-party exposure and counterparty concentration.",
        "Why it matters": "Entity complexity and concentrated counterparties can require deeper network review.",
    },
]

DERIVED_DIMENSIONS = [
    {
        "Signal": "Debt-to-revenue ratio",
        "Definition": "Existing debt divided by annual revenue.",
        "Why it matters": "Higher debt pressure can indicate financial distress or incentive pressure.",
    },
    {
        "Signal": "Request-to-revenue ratio",
        "Definition": "Requested loan amount divided by annual revenue.",
        "Why it matters": "Large exposure relative to business scale can merit closer review.",
    },
    {
        "Signal": "Loan velocity score",
        "Definition": "Normalized count of recent loans.",
        "Why it matters": "Rapid borrowing can suggest credit stacking or liquidity stress.",
    },
    {
        "Signal": "Payment stress score",
        "Definition": "Combined late-payment behavior and debt pressure.",
        "Why it matters": "Payment stress is a practical early warning signal for risk triage.",
    },
    {
        "Signal": "Transaction anomaly score",
        "Definition": "Combined suspicious transfer ratio, payment behavior, country risk, and borrowing velocity.",
        "Why it matters": "Fraud literature emphasizes unusual transaction patterns and behavioral anomalies.",
    },
    {
        "Signal": "Financial distress score",
        "Definition": "Combined debt, late payments, collateral gap, and short operating history.",
        "Why it matters": "Fraud-triangle research highlights financial pressure and distress as important risk factors.",
    },
    {
        "Signal": "Cash-flow pressure score",
        "Definition": "Combined negative free cash flow and burn intensity.",
        "Why it matters": "Weak liquidity can create pressure to seek financing or misstate business health.",
    },
    {
        "Signal": "Runway risk score",
        "Definition": "A normalized short-runway measure based on expected runway months.",
        "Why it matters": "Applicants with limited runway may require closer analyst review.",
    },
    {
        "Signal": "Cash conversion risk score",
        "Definition": "Measures weak free-cash-flow conversion relative to revenue, adjusted by payment stress.",
        "Why it matters": "Revenue that does not convert to cash can signal fragility or documentation concerns.",
    },
    {
        "Signal": "Forecast plan aggressiveness score",
        "Definition": "Combines aggressive revenue growth, hiring gap, FCF improvement need, and missing forecast support.",
        "Why it matters": "Ambitious plans can be risky when current operating signals do not support them.",
    },
    {
        "Signal": "Forecast execution risk score",
        "Definition": "Combines plan aggressiveness, cash conversion risk, runway risk, forecast support, and applicant narrative coverage.",
        "Why it matters": "Helps analysts judge whether the five-year plan is credible.",
    },
    {
        "Signal": "Forecast hiring efficiency risk score",
        "Definition": "Measures revenue growth that may be under-supported by employee growth.",
        "Why it matters": "Growth without capacity can indicate execution or documentation risk.",
    },
    {
        "Signal": "Forecast debt service risk score",
        "Definition": "Measures debt reduction ambition under current debt and cash-flow pressure.",
        "Why it matters": "Debt plans may be less credible when cash flow is weak.",
    },
    {
        "Signal": "Annual debt service",
        "Definition": "Estimated first-year principal and interest payments based on requested amount, term, and interest rate.",
        "Why it matters": "Shows whether the new loan is affordable under current cash flow.",
    },
    {
        "Signal": "Debt service coverage ratio",
        "Definition": "Free cash flow divided by estimated annual debt service.",
        "Why it matters": "A DSCR below 1.0 means free cash flow does not cover estimated debt service.",
    },
    {
        "Signal": "Stressed DSCR",
        "Definition": "Debt service coverage recomputed after adding two percentage points to the interest rate.",
        "Why it matters": "Stress testing shows whether the applicant remains resilient if pricing or rates move against them.",
    },
    {
        "Signal": "Debt service stress score",
        "Definition": "Combines DSCR weakness, stressed DSCR weakness, and elevated interest-rate pricing.",
        "Why it matters": "Helps analysts see repayment sensitivity from the loan terms themselves.",
    },
    {
        "Signal": "Cash conversion cycle days",
        "Definition": "Receivables days plus inventory days minus payables days.",
        "Why it matters": "Long cycles can create working-capital strain and financing pressure.",
    },
    {
        "Signal": "Document completeness score",
        "Definition": "Share of expected application documents marked present.",
        "Why it matters": "Completeness helps analysts separate supported cases from cases requiring document follow-up.",
    },
    {
        "Signal": "Document quality risk score",
        "Definition": "Combines missing documents with any available process metadata.",
        "Why it matters": "Weak documentation quality can reduce auditability and increase review burden.",
    },
    {
        "Signal": "Process integrity risk score",
        "Definition": "Uses system-supplied process metadata when available; defaults to neutral during applicant-first intake.",
        "Why it matters": "Keeps internal workflow signals separate from the SME-provided application.",
    },
    {
        "Signal": "Identity verification risk score",
        "Definition": "Combines digital footprint age, bank-account age, location mismatch, and duplicate contact risk.",
        "Why it matters": "Application-channel and KYB signals help identify cases needing deeper verification.",
    },
    {
        "Signal": "Working-capital pressure score",
        "Definition": "Combines current ratio, quick ratio, cash conversion cycle, and receivables pressure.",
        "Why it matters": "Adds liquidity depth beyond free cash flow and runway.",
    },
    {
        "Signal": "Financial statement anomaly score",
        "Definition": "Combines revenue/cash-flow mismatch, receivables pressure, FCF improvement need, and document quality.",
        "Why it matters": "Financial-statement fraud research supports ratio and anomaly checks around reported performance.",
    },
    {
        "Signal": "Related-party network risk score",
        "Definition": "Combines related-party exposure, counterparty concentration, shared identifiers, and suspicious transfer behavior.",
        "Why it matters": "Network-style review can reveal connected-entity or concentrated exposure risk.",
    },
    {
        "Signal": "Narrative consistency risk score",
        "Definition": "Flags contradictions between applicant narrative, document status, and financial signals.",
        "Why it matters": "A credible lending review compares management context with observable evidence.",
    },
]

GRADE_ROWS = [
    {"Grade": "A", "Application risk score": "< 0.15", "Recommended action": "Approve"},
    {
        "Grade": "B",
        "Application risk score": "0.15 to < 0.28",
        "Recommended action": "Approve",
    },
    {
        "Grade": "C",
        "Application risk score": "0.28 to < 0.42",
        "Recommended action": "Manual Review",
    },
    {
        "Grade": "D",
        "Application risk score": "0.42 to < 0.58",
        "Recommended action": "Manual Review",
    },
    {
        "Grade": "E",
        "Application risk score": "0.58 to < 0.74",
        "Recommended action": "Reject",
    },
    {"Grade": "F", "Application risk score": ">= 0.74", "Recommended action": "Reject"},
]

LENDER_SUPPORT_REPS = [
    {
        "name": "Mila Verhoeven",
        "role": "Risk Platform Lead",
        "email": "mila.verhoeven@yourbank.com",
        "focus": "Workspace setup, lender workflow questions, and analyst onboarding.",
    },
    {
        "name": "Daan Peters",
        "role": "Risk Support Specialist",
        "email": "daan.peters@yourbank.com",
        "focus": "Scoring, DSCR, risk flags, document verification, and model explanation questions.",
    },
    {
        "name": "Sofia de Vries",
        "role": "Operations Enablement",
        "email": "sofia.devries@yourbank.com",
        "focus": "Account access, support routing, and training material.",
    },
]

SME_CONSULTANTS = [
    {
        "name": "Emma de Vries",
        "role": "SME Finance Consultant",
        "email": "emma.devries@yourbank.com",
        "focus": "Application readiness, lender questions, and next-step planning.",
    },
    {
        "name": "Noah Bakker",
        "role": "Business Lending Consultant",
        "email": "noah.bakker@yourbank.com",
        "focus": "Loan-purpose discussion, affordability questions, and document expectations.",
    },
    {
        "name": "Sofia de Vries",
        "role": "Applicant Support Consultant",
        "email": "sme.support@yourbank.com",
        "focus": "Portal access, upload issues, and scheduling a consultant conversation.",
    },
]

LENDER_FAQ_ITEMS = [
    (
        "Is this a production credit decision system?",
        "No. This is a decision-support workspace. It helps analysts review risk signals, explanations, and workflow controls, but it does not make legal, compliance, or final credit decisions.",
    ),
    (
        "Where does the data come from?",
        "The workspace uses application, accounting, document, KYB, transaction, forecast, and pricing inputs available to the review file.",
    ),
    (
        "Does the model consider interest rates and repayment affordability?",
        "Yes. Personal Workspace includes an offered interest rate, annual debt service, DSCR, and a +2 percentage point stressed DSCR.",
    ),
    (
        "Can analysts override the model result?",
        "Yes. The Case Review workflow stores the analyst's final action separately from the model recommendation and AI review output.",
    ),
    (
        "How should high-risk outcomes be handled?",
        "High-risk E/F outcomes should be routed to human compliance-style review before any external decision is communicated.",
    ),
    (
        "What integrations are supported?",
        "Personal connected apps include Slack, Teams, Gmail, Outlook, file storage, and meeting tools. Risk-model data sources are handled separately from personal app connections.",
    ),
]

SME_FAQ_ITEMS = [
    (
        "Can I speak with someone about my application?",
        "Yes. Use the consultant cards or request form to connect with a YourBank SME consultant about your application, documents, or next steps.",
    ),
    (
        "Does submitting an application show me the lender's internal score?",
        "No. Internal model scores, verification notes, and lender review details stay private unless the lender publishes a reviewed result.",
    ),
    (
        "What happens if my documents are incomplete or inconsistent?",
        "The lender may request clarification, ask for updated evidence, or decline the application if submitted evidence cannot be verified.",
    ),
    (
        "Are PSD2, accounting, and registry connections live?",
        "In this MVP they are simulated. The portal demonstrates consent and source selection without connecting to real bank, accounting, or registry systems.",
    ),
    (
        "When will I see a rating or evaluation report?",
        "Only after the lender completes review and chooses to publish the outcome. Until then, the SME portal shows readiness guidance rather than an internal lender rating.",
    ),
]