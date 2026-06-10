# Fraud Research Notes

These notes summarize the local PDFs in `docs/` and translate their fraud-detection themes into MVP signals used by the synthetic Streamlit app. The papers are used for research grounding only; the app remains synthetic decision support.

## Source Themes

| Local PDF | Useful theme for this MVP |
| --- | --- |
| `applsci-12-09637-v2.pdf` | Machine-learning fraud detection review; supports transaction analysis, anomaly detection, class-imbalance awareness, and metrics beyond accuracy. |
| `CCFDBookchapter.pdf` | Credit-card fraud review; highlights transaction pattern/frequency, class imbalance, ensemble models, precision, recall, and F-measure. |
| `jrfm-18-00598.pdf` | Financial statement fraud analytics review; supports ratio analysis, anomaly detection, network-style review, continuous monitoring, governance, and explainability. |
| `Md+Jamil+Ahmmed_ijbeiv5i32513291369.pdf` | Financial-services ML trust and auditability; supports audit trails, model confidence, drift monitoring, and precision-at-k for alert queues. |
| `Paper+7+(2024.6.1)+A+Review+on+Financial+Fraud+Detection+using+AI+and+Machine+Learning.pdf` | AI/ML fraud review; supports Random Forest/SVM/neural model comparisons, ROC-AUC, precision, recall, F1, and explainability. |
| `s10796-016-9647-9.pdf` | Fraud-triangle risk factors; supports pressure/incentive signals such as poor performance, external financing need, and financial distress. |
| `s41599-024-03606-0.pdf` | ML financial fraud literature review; supports feature engineering, Random Forest, XGBoost, autoencoders, and evolving fraud patterns. |
| `s42979-024-02772-x.pdf` | ML/DL fraud review; supports preprocessing, interpretability, imbalanced data handling, and transaction amount/pattern anomalies. |
| `s44230-022-00004-0.pdf` | Credit-card fraud ML review; supports real-time transaction behavior, prior/current transaction correlation, and imbalance-aware metrics. |

## Implemented Derived Signals

The app computes these fields automatically from seed and intake data in `src/data_pipeline.py`.

| Signal | Research motivation | How it helps the demo |
| --- | --- | --- |
| `debt_to_revenue_ratio` | Financial pressure and distress indicators. | Shows whether existing obligations are large relative to business scale. |
| `request_to_revenue_ratio` | Ratio analysis and exposure proportionality. | Flags requests that may be outsized compared with reported revenue. |
| `loan_velocity_score` | Transaction frequency and recent behavioral change. | Captures possible credit stacking or rapid borrowing behavior. |
| `payment_stress_score` | Payment behavior and pressure/incentive signals. | Combines late payments with debt pressure for analyst triage. |
| `collateral_gap_ratio` | Loss exposure and financial distress indicators. | Captures weak collateral coverage behind the requested amount. |
| `external_financing_pressure` | Fraud-triangle pressure from need for external financing. | Combines request size, debt, and recent loans into one pressure score. |
| `financial_distress_score` | Fraud-triangle research and accounting fraud indicators. | Combines debt, payment stress, collateral gap, and short history. |
| `transaction_anomaly_score` | Anomaly detection and suspicious transaction behavior. | Summarizes suspicious transfers, payment stress, country risk, and velocity. |
| `company_scale_mismatch_score` | Pattern/anomaly detection against business scale. | Flags cases where employee scale looks stretched relative to exposure. |
| `governance_complexity_score` | Governance, auditability, entity complexity, and jurisdictional risk. | Helps explain why some cases may need more human review. |
| `free_cash_flow` | Fraud-triangle pressure, financial distress, and cash-conversion analysis. | Shows whether the applicant generates or consumes cash at application date. |
| `monthly_burn_rate` | Liquidity pressure and continuous monitoring of cash consumption. | Highlights applicants whose operating burn may create urgency for financing. |
| `cash_flow_to_revenue_ratio` | Ratio analysis and cash-conversion quality. | Distinguishes reported revenue from usable cash generation. |
| `expected_runway_months` | Financial distress and short-term liquidity pressure. | Estimates how long cash reserves can sustain current burn. |
| `cash_flow_pressure_score` | Pressure/incentive and burn-rate stress. | Combines negative FCF and burn intensity into a review signal. |
| `runway_risk_score` | Liquidity runway and distress indicators. | Flags short-runway applicants for closer analyst review. |
| `cash_conversion_risk_score` | Weak cash conversion and payment stress. | Captures revenue quality concerns that may not be visible from revenue alone. |
| `forecast_revenue_cagr` | Forward-looking plan assessment and growth assumption review. | Captures expected annual revenue growth over the five-year plan. |
| `forecast_employee_cagr` | Operational capacity and execution feasibility. | Compares planned headcount growth with revenue growth. |
| `forecast_fcf_margin_year5` | Cash-flow quality and margin improvement assumptions. | Captures whether management expects cash conversion to improve materially. |
| `planned_debt_reduction_pct` | Financing pressure and debt service credibility. | Measures whether the applicant expects to reduce leverage during the forecast horizon. |
| `forecast_plan_confidence_score` | Governance, auditability, and documentation confidence. | Captures banker confidence in the applicant's plan quality. |
| `forecast_plan_aggressiveness_score` | Forecast realism and anomaly-style plan review. | Flags ambitious plans when current signals do not support them. |
| `forecast_execution_risk_score` | Combined plan, liquidity, and confidence risk. | Measures whether the five-year plan is difficult to execute. |
| `forecast_hiring_efficiency_risk_score` | Operational scale consistency. | Flags revenue growth that may be under-supported by employee growth. |
| `forecast_debt_service_risk_score` | Debt plan realism under cash-flow pressure. | Flags debt reduction plans that may be strained by weak cash flow. |

## Evaluation Measures

The app reports standard and imbalance-aware metrics in `pages/Model_Insights.py`:

- Accuracy
- Balanced accuracy
- Precision
- Recall
- F1
- ROC-AUC
- Average precision
- Matthews correlation coefficient
- Precision at top 10% review queue

These measures are useful because fraud datasets are often imbalanced, and a demo should show review-queue quality rather than accuracy alone.

## Demo Framing

Use this language when discussing the research grounding:

> The MVP does not claim production-grade fraud detection. It uses synthetic data and literature-inspired signals to demonstrate how a lender could combine financial pressure ratios, transaction anomalies, explainability, manual review governance, and audit trails in a responsible decision-support workflow.
