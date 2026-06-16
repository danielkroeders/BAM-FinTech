import json

import pandas as pd

from src.core.data_pipeline import add_derived_features
from src.utils.formatting import format_currency, format_months, format_percent, format_score
from src.core.modeling import score_application, score_portfolio


def _number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _yes_no(value):
    return "Yes" if _number(value) >= 0.5 else "No"


def _bounded(value, low=0.0, high=1.0):
    return min(max(_number(value), low), high)


def apply_scenario(
    application,
    revenue_growth_delta=0.0,
    fcf_margin_delta=0.0,
    operating_cost_pressure=0.0,
    contract_evidence="Current file",
    complete_documents=False,
    debt_reduction_delta=0.0,
):
    scenario = dict(application)
    annual_revenue = max(_number(scenario.get("annual_revenue")), 1)

    scenario["forecast_revenue_cagr"] = _bounded(
        _number(scenario.get("forecast_revenue_cagr")) + revenue_growth_delta,
        -0.25,
        0.75,
    )
    scenario["forecast_fcf_margin_year5"] = _bounded(
        _number(scenario.get("forecast_fcf_margin_year5")) + fcf_margin_delta,
        -0.30,
        0.45,
    )
    scenario["free_cash_flow"] = _number(scenario.get("free_cash_flow")) + (annual_revenue * fcf_margin_delta) - (
        annual_revenue * operating_cost_pressure
    )
    scenario["cash_flow_to_revenue_ratio"] = scenario["free_cash_flow"] / annual_revenue
    scenario["monthly_burn_rate"] = max(
        0,
        _number(scenario.get("monthly_burn_rate")) + (annual_revenue * max(operating_cost_pressure, 0)) / 12,
    )
    scenario["planned_debt_reduction_pct"] = _bounded(
        _number(scenario.get("planned_debt_reduction_pct")) + debt_reduction_delta
    )

    if contract_evidence == "Signed and documented":
        scenario["narrative_contradiction_score"] = _bounded(
            _number(scenario.get("narrative_contradiction_score")) - 0.10
        )
        scenario["forecast_support_uploaded"] = 1
    elif contract_evidence == "Unconfirmed":
        scenario["narrative_contradiction_score"] = _bounded(
            _number(scenario.get("narrative_contradiction_score")) + 0.12
        )

    if complete_documents:
        for key in [
            "financial_statements_uploaded",
            "bank_statements_uploaded",
            "tax_return_uploaded",
            "ownership_docs_uploaded",
            "forecast_support_uploaded",
        ]:
            scenario[key] = 1
        scenario["document_edit_count"] = min(_number(scenario.get("document_edit_count")), 1)
        scenario["late_stage_change_count"] = min(_number(scenario.get("late_stage_change_count")), 0)

    return scenario


def scenario_comparison_rows(model_bundle, application, baseline_prediction, scenario_application, model_key=None):
    selected_key = model_key or baseline_prediction.get("model_key")
    scenario_prediction = score_application(model_bundle, scenario_application, model_key=selected_key)
    base_signals = add_derived_features(pd.DataFrame([application])).iloc[0]
    scenario_signals = add_derived_features(pd.DataFrame([scenario_application])).iloc[0]
    return scenario_prediction, [
        {
            "Measure": "Application risk score",
            "Current file": format_percent(baseline_prediction.get("fraud_probability", 0)),
            "Scenario": format_percent(scenario_prediction.get("fraud_probability", 0)),
        },
        {"Measure": "Grade", "Current file": baseline_prediction.get("grade", ""), "Scenario": scenario_prediction.get("grade", "")},
        {
            "Measure": "Model recommendation",
            "Current file": baseline_prediction.get("decision", ""),
            "Scenario": scenario_prediction.get("decision", ""),
        },
        {
            "Measure": "Free cash flow",
            "Current file": format_currency(application.get("free_cash_flow", 0)),
            "Scenario": format_currency(scenario_application.get("free_cash_flow", 0)),
        },
        {
            "Measure": "Forecast support",
            "Current file": _yes_no(application.get("forecast_support_uploaded", 0)),
            "Scenario": _yes_no(scenario_application.get("forecast_support_uploaded", 0)),
        },
        {
            "Measure": "Document completeness",
            "Current file": format_score(base_signals.get("document_completeness_score", 0)),
            "Scenario": format_score(scenario_signals.get("document_completeness_score", 0)),
        },
        {
            "Measure": "Stressed DSCR",
            "Current file": format_score(base_signals.get("stressed_debt_service_coverage_ratio", 0)),
            "Scenario": format_score(scenario_signals.get("stressed_debt_service_coverage_ratio", 0)),
        },
    ]


def peer_benchmark_rows(model_bundle, applications, application, prediction, model_key=None):
    selected_key = model_key or prediction.get("model_key")
    scored = score_portfolio(model_bundle, applications, model_key=selected_key)
    app_signals = add_derived_features(pd.DataFrame([application])).iloc[0]
    industry_peers = scored[scored["industry"].eq(application.get("industry"))].copy()
    regional_peers = industry_peers[industry_peers["region"].eq(application.get("region"))].copy()
    peers = regional_peers if len(regional_peers) >= 8 else industry_peers
    if len(peers) < 8:
        peers = scored.copy()

    def percentile(series, value):
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if numeric.empty:
            return "N/A"
        return format_percent((numeric <= _number(value)).mean(), 0)

    metrics = [
        (
            "Application risk score",
            prediction.get("fraud_probability", 0),
            peers["fraud_probability"],
            format_percent,
            "Higher percentile means riskier than more peers.",
        ),
        (
            "Requested amount",
            application.get("requested_amount", 0),
            peers["requested_amount"],
            format_currency,
            "Shows whether requested exposure is above the peer group.",
        ),
        (
            "Request / revenue",
            app_signals.get("request_to_revenue_ratio", 0),
            peers["request_to_revenue_ratio"],
            format_percent,
            "Compares requested loan size with business scale.",
        ),
        (
            "Cash-flow pressure",
            app_signals.get("cash_flow_pressure_score", 0),
            peers["cash_flow_pressure_score"],
            format_score,
            "Higher values indicate more liquidity pressure.",
        ),
        (
            "Stressed DSCR",
            app_signals.get("stressed_debt_service_coverage_ratio", 0),
            peers["stressed_debt_service_coverage_ratio"],
            format_score,
            "Shows repayment resilience under +2% rate stress.",
        ),
        (
            "Document completeness",
            app_signals.get("document_completeness_score", 0),
            peers["document_completeness_score"],
            format_score,
            "Shows whether the file is complete compared with peers.",
        ),
    ]

    return [
        {
            "Benchmark": label,
            "Applicant": formatter(value),
            "Peer median": formatter(series.median()),
            "Applicant percentile": percentile(series, value),
            "Peer group": f"{len(peers)} cases",
            "Interpretation": interpretation,
        }
        for label, value, series, formatter, interpretation in metrics
    ]


def data_source_coverage_rows(application, signals):
    return [
        {
            "Source": "PSD2 / Open Banking",
            "MVP handling": "Simulated from bank-statement presence, account age, payment behavior, and transfer anomaly fields.",
            "Current status": "Ready" if _number(application.get("bank_statements_uploaded")) else "Needs review",
            "Production path": "Connect consented bank feeds for real-time transaction and cash-balance refresh.",
        },
        {
            "Source": "Accounting APIs",
            "MVP handling": "Simulated from financial statements, working-capital ratios, cash flow, and forecast support.",
            "Current status": "Ready" if _number(application.get("financial_statements_uploaded")) else "Needs review",
            "Production path": "Integrate Exact, Twinfield, Visma, Xero, or bank accounting partners.",
        },
        {
            "Source": "Registry / KYB",
            "MVP handling": "Simulated through ownership document status, digital footprint age, and mismatch scores.",
            "Current status": "Ready" if _number(application.get("ownership_docs_uploaded")) else "Needs review",
            "Production path": "Connect KvK/CoC registry, UBO, sanctions, and entity-resolution checks.",
        },
        {
            "Source": "Document ingestion",
            "MVP handling": f"Uses checklist and metadata; document completeness is {format_score(signals.get('document_completeness_score', 0))}.",
            "Current status": "Ready" if _number(signals.get("document_completeness_score")) >= 0.8 else "Partial",
            "Production path": "Parse uploaded statements, tax files, contracts, and forecast support documents.",
        },
        {
            "Source": "Contextual signals",
            "MVP handling": "Captured as applicant narrative, executive context, sector, country risk, and forecast realism.",
            "Current status": "Ready" if str(application.get("loan_purpose_context", "")).strip() else "Partial",
            "Production path": "Add verified market feeds, sector stress indicators, and contract evidence.",
        },
    ]


def sme_action_rows(application, signals, prediction):
    rows = []
    if _number(signals.get("document_completeness_score")) < 0.95:
        rows.append(
            {
                "Action": "Complete the evidence package",
                "Why it helps": "Missing statements, KYB, tax, or forecast support can keep the case in manual review.",
                "Current signal": format_score(signals.get("document_completeness_score", 0)),
            }
        )
    if _number(signals.get("stressed_debt_service_coverage_ratio")) < 1.2:
        rows.append(
            {
                "Action": "Improve repayment coverage",
                "Why it helps": "Higher free cash flow or a smaller requested amount improves DSCR and rate-stress resilience.",
                "Current signal": format_score(signals.get("stressed_debt_service_coverage_ratio", 0)),
            }
        )
    if _number(signals.get("cash_flow_pressure_score")) >= 0.35:
        rows.append(
            {
                "Action": "Reduce cash-flow pressure",
                "Why it helps": "Lower burn, better collections, or stronger cash conversion makes the score more resilient.",
                "Current signal": format_score(signals.get("cash_flow_pressure_score", 0)),
            }
        )
    if _number(signals.get("forecast_execution_risk_score")) >= 0.35:
        rows.append(
            {
                "Action": "Support the five-year plan",
                "Why it helps": "Documented contracts and realistic growth assumptions reduce forecast execution risk.",
                "Current signal": format_score(signals.get("forecast_execution_risk_score", 0)),
            }
        )
    if _number(signals.get("narrative_consistency_risk_score")) >= 0.35:
        rows.append(
            {
                "Action": "Align the applicant story with evidence",
                "Why it helps": "Consistent management context and financial evidence reduce follow-up questions.",
                "Current signal": format_score(signals.get("narrative_consistency_risk_score", 0)),
            }
        )
    if not rows:
        rows.append(
            {
                "Action": "Maintain current evidence quality",
                "Why it helps": f"The current grade {prediction.get('grade')} already has a relatively strong evidence profile.",
                "Current signal": format_percent(prediction.get("fraud_probability", 0)),
            }
        )
    return rows


def api_contract_payloads(application, prediction, metrics):
    request = {
        "application_id": application.get("application_id", "APP-001"),
        "company": {
            "name": application.get("company_name", "Applicant"),
            "industry": application.get("industry"),
            "region": application.get("region"),
            "company_type": application.get("company_type"),
        },
        "loan_request": {
            "requested_amount": application.get("requested_amount"),
            "term_months": application.get("term_months"),
            "interest_rate": application.get("interest_rate"),
        },
        "evidence": {
            "open_banking": bool(_number(application.get("bank_statements_uploaded"))),
            "accounting": bool(_number(application.get("financial_statements_uploaded"))),
            "registry_kyb": bool(_number(application.get("ownership_docs_uploaded"))),
            "forecast_support": bool(_number(application.get("forecast_support_uploaded"))),
        },
        "financial_snapshot": {
            "annual_revenue": application.get("annual_revenue"),
            "free_cash_flow": application.get("free_cash_flow"),
            "existing_debt": application.get("existing_debt"),
            "expected_runway_months": application.get("expected_runway_months"),
        },
    }
    response = {
        "application_id": request["application_id"],
        "application_risk_score": round(_number(prediction.get("fraud_probability")), 4),
        "grade": prediction.get("grade"),
        "model_recommendation": prediction.get("decision"),
        "model_context": {
            "model_type": prediction.get("model_label", "ML model"),
            "roc_auc": round(_number(metrics.get("roc_auc")), 4),
            "balanced_accuracy": round(_number(metrics.get("balanced_accuracy")), 4),
            "precision_at_10pct": round(_number(metrics.get("precision_at_10pct")), 4),
        },
        "governance": {
            "final_decision": "Human analyst required",
            "production_status": "MVP contract preview",
        },
    }
    return json.dumps(request, indent=2), json.dumps(response, indent=2)


def latest_or_sample_application(seed_data, model_bundle, model_key=None):
    applications = seed_data["applications"]
    scored = score_portfolio(model_bundle, applications, model_key=model_key)
    sample = scored.sort_values("fraud_probability", ascending=False).iloc[len(scored) // 3].to_dict()
    prediction = {
        "fraud_probability": sample["fraud_probability"],
        "grade": sample["grade"],
        "decision": sample["decision"],
        "model_key": sample.get("model_key"),
        "model_label": sample.get("model_label"),
        "flags": [],
    }
    return sample, prediction
