from pathlib import Path

import numpy as np
import pandas as pd


SEED_DIR = Path(__file__).resolve().parents[1] / "data" / "seed"

BASE_NUMERIC_COLUMNS = [
    "requested_amount",
    "term_months",
    "annual_revenue",
    "years_in_business",
    "existing_debt",
    "num_recent_loans",
    "late_payment_ratio",
    "suspicious_transfer_ratio",
    "collateral_ratio",
    "employees",
    "country_risk_score",
    "free_cash_flow",
    "monthly_burn_rate",
    "cash_flow_to_revenue_ratio",
    "expected_runway_months",
    "forecast_revenue_cagr",
    "forecast_employee_cagr",
    "forecast_fcf_margin_year5",
    "planned_debt_reduction_pct",
    "forecast_plan_confidence_score",
]

DERIVED_NUMERIC_COLUMNS = [
    "debt_to_revenue_ratio",
    "request_to_revenue_ratio",
    "loan_velocity_score",
    "payment_stress_score",
    "collateral_gap_ratio",
    "external_financing_pressure",
    "financial_distress_score",
    "transaction_anomaly_score",
    "company_scale_mismatch_score",
    "governance_complexity_score",
    "cash_flow_pressure_score",
    "runway_risk_score",
    "cash_conversion_risk_score",
    "forecast_plan_aggressiveness_score",
    "forecast_execution_risk_score",
    "forecast_hiring_efficiency_risk_score",
    "forecast_debt_service_risk_score",
]

NUMERIC_COLUMNS = BASE_NUMERIC_COLUMNS + DERIVED_NUMERIC_COLUMNS

CATEGORICAL_COLUMNS = ["industry", "region", "company_type"]
TARGET_COLUMN = "is_fraud"
FORECAST_YEARS = range(1, 6)


def _sigmoid(value):
    return 1 / (1 + np.exp(-value))


def _numeric(frame, column, default=0):
    if column in frame:
        return pd.to_numeric(frame[column], errors="coerce").fillna(default)
    return pd.Series(default, index=frame.index, dtype="float64")


def add_derived_features(frame):
    enriched = frame.copy()
    if enriched.empty:
        for column in DERIVED_NUMERIC_COLUMNS:
            enriched[column] = []
        return enriched

    revenue = _numeric(enriched, "annual_revenue", 1).clip(lower=1)
    requested_amount = _numeric(enriched, "requested_amount", 0).clip(lower=0)
    existing_debt = _numeric(enriched, "existing_debt", 0).clip(lower=0)
    recent_loans = _numeric(enriched, "num_recent_loans", 0).clip(lower=0)
    late_payment_ratio = _numeric(enriched, "late_payment_ratio", 0).clip(0, 1)
    suspicious_transfer_ratio = _numeric(enriched, "suspicious_transfer_ratio", 0).clip(0, 1)
    collateral_ratio = _numeric(enriched, "collateral_ratio", 0).clip(lower=0)
    years_in_business = _numeric(enriched, "years_in_business", 0).clip(lower=0)
    employees = _numeric(enriched, "employees", 1).clip(lower=1)
    country_risk_score = _numeric(enriched, "country_risk_score", 0).clip(0, 1)
    free_cash_flow = _numeric(enriched, "free_cash_flow", 0)
    monthly_burn_rate = _numeric(enriched, "monthly_burn_rate", 0).clip(lower=0)
    cash_flow_to_revenue = (free_cash_flow / revenue).clip(-1, 1)
    expected_runway = _numeric(enriched, "expected_runway_months", 36).clip(0, 60)
    forecast_revenue_cagr = _numeric(enriched, "forecast_revenue_cagr", 0.08).clip(-0.25, 0.75)
    forecast_employee_cagr = _numeric(enriched, "forecast_employee_cagr", 0.04).clip(-0.10, 0.60)
    forecast_fcf_margin_year5 = _numeric(enriched, "forecast_fcf_margin_year5", 0.08).clip(-0.30, 0.40)
    planned_debt_reduction = _numeric(enriched, "planned_debt_reduction_pct", 0.20).clip(0, 1)
    forecast_confidence = _numeric(enriched, "forecast_plan_confidence_score", 0.55).clip(0, 1)

    debt_to_revenue = (existing_debt / revenue).clip(0, 3)
    request_to_revenue = (requested_amount / revenue).clip(0, 2)
    short_history = ((3 - years_in_business).clip(lower=0) / 3).clip(0, 1)
    collateral_gap = (1 - collateral_ratio).clip(0, 1)
    loan_velocity = (recent_loans / 6).clip(0, 1)
    payment_stress = (0.55 * late_payment_ratio + 0.45 * (debt_to_revenue / 1.25).clip(0, 1)).clip(0, 1)
    external_financing_pressure = (0.45 * (request_to_revenue / 0.55).clip(0, 1) + 0.35 * (debt_to_revenue / 0.85).clip(0, 1) + 0.20 * loan_velocity).clip(0, 1)
    financial_distress = (0.35 * (debt_to_revenue / 0.85).clip(0, 1) + 0.25 * late_payment_ratio + 0.25 * collateral_gap + 0.15 * short_history).clip(0, 1)
    transaction_anomaly = (0.55 * suspicious_transfer_ratio + 0.20 * late_payment_ratio + 0.15 * country_risk_score + 0.10 * loan_velocity).clip(0, 1)

    expected_employees = (revenue / 150_000).clip(lower=1)
    staff_capacity_gap = (1 - (employees / expected_employees)).clip(0, 1)
    request_per_employee = requested_amount / employees
    request_staff_pressure = (request_per_employee / 50_000).clip(0, 1)
    company_scale_mismatch = (0.55 * staff_capacity_gap + 0.45 * request_staff_pressure).clip(0, 1)

    company_type_risk = enriched.get("company_type", pd.Series("", index=enriched.index)).map(
        {"Corporation": 0.05, "LLC": 0.15, "Partnership": 0.28, "Sole Proprietorship": 0.42}
    ).fillna(0.2)
    region_risk = enriched.get("region", pd.Series("", index=enriched.index)).isin(["Eastern Europe", "Latin America", "Middle East"]).astype(float)
    governance_complexity = (0.35 * company_type_risk + 0.30 * region_risk + 0.20 * short_history + 0.15 * country_risk_score).clip(0, 1)

    burn_to_revenue = ((monthly_burn_rate * 12) / revenue).clip(0, 2)
    negative_cash_flow_pressure = (-cash_flow_to_revenue).clip(0, 1)
    cash_flow_pressure = (0.55 * negative_cash_flow_pressure + 0.45 * (burn_to_revenue / 0.35).clip(0, 1)).clip(0, 1)
    runway_risk = ((12 - expected_runway).clip(lower=0) / 12).clip(0, 1)
    low_cash_conversion = ((0.08 - cash_flow_to_revenue).clip(lower=0) / 0.25).clip(0, 1)
    cash_conversion_risk = (0.65 * low_cash_conversion + 0.35 * payment_stress).clip(0, 1)

    aggressive_revenue_growth = ((forecast_revenue_cagr - 0.18).clip(lower=0) / 0.45).clip(0, 1)
    hiring_growth_gap = ((forecast_revenue_cagr - forecast_employee_cagr - 0.08).clip(lower=0) / 0.45).clip(0, 1)
    fcf_improvement_need = ((forecast_fcf_margin_year5 - cash_flow_to_revenue).clip(lower=0) / 0.60).clip(0, 1)
    debt_reduction_strain = (planned_debt_reduction * (0.65 * cash_flow_pressure + 0.35 * debt_to_revenue.clip(0, 1))).clip(0, 1)
    plan_aggressiveness = (
        0.40 * aggressive_revenue_growth
        + 0.25 * hiring_growth_gap
        + 0.25 * fcf_improvement_need
        + 0.10 * (1 - forecast_confidence)
    ).clip(0, 1)
    forecast_execution_risk = (
        0.35 * plan_aggressiveness
        + 0.25 * cash_conversion_risk
        + 0.20 * runway_risk
        + 0.20 * (1 - forecast_confidence)
    ).clip(0, 1)

    enriched["forecast_revenue_cagr"] = forecast_revenue_cagr.round(4)
    enriched["forecast_employee_cagr"] = forecast_employee_cagr.round(4)
    enriched["forecast_fcf_margin_year5"] = forecast_fcf_margin_year5.round(4)
    enriched["planned_debt_reduction_pct"] = planned_debt_reduction.round(4)
    enriched["forecast_plan_confidence_score"] = forecast_confidence.round(4)
    enriched["debt_to_revenue_ratio"] = debt_to_revenue.round(4)
    enriched["request_to_revenue_ratio"] = request_to_revenue.round(4)
    enriched["loan_velocity_score"] = loan_velocity.round(4)
    enriched["payment_stress_score"] = payment_stress.round(4)
    enriched["collateral_gap_ratio"] = collateral_gap.round(4)
    enriched["external_financing_pressure"] = external_financing_pressure.round(4)
    enriched["financial_distress_score"] = financial_distress.round(4)
    enriched["transaction_anomaly_score"] = transaction_anomaly.round(4)
    enriched["company_scale_mismatch_score"] = company_scale_mismatch.round(4)
    enriched["governance_complexity_score"] = governance_complexity.round(4)
    enriched["cash_flow_to_revenue_ratio"] = cash_flow_to_revenue.round(4)
    enriched["cash_flow_pressure_score"] = cash_flow_pressure.round(4)
    enriched["runway_risk_score"] = runway_risk.round(4)
    enriched["cash_conversion_risk_score"] = cash_conversion_risk.round(4)
    enriched["forecast_plan_aggressiveness_score"] = plan_aggressiveness.round(4)
    enriched["forecast_execution_risk_score"] = forecast_execution_risk.round(4)
    enriched["forecast_hiring_efficiency_risk_score"] = hiring_growth_gap.round(4)
    enriched["forecast_debt_service_risk_score"] = debt_reduction_strain.round(4)
    return enriched


def build_forecast_table(applications):
    enriched = add_derived_features(applications)
    rows = []
    for _, row in enriched.iterrows():
        current_margin = float(row["cash_flow_to_revenue_ratio"])
        target_margin = float(row["forecast_fcf_margin_year5"])
        annual_revenue = float(row["annual_revenue"])
        employees = float(row["employees"])
        existing_debt = float(row["existing_debt"])
        revenue_growth = float(row["forecast_revenue_cagr"])
        employee_growth = float(row["forecast_employee_cagr"])
        debt_reduction = float(row["planned_debt_reduction_pct"])

        for year in FORECAST_YEARS:
            projected_revenue = annual_revenue * ((1 + revenue_growth) ** year)
            projected_employees = max(1, round(employees * ((1 + employee_growth) ** year)))
            projected_margin = current_margin + ((target_margin - current_margin) * year / 5)
            projected_free_cash_flow = projected_revenue * projected_margin
            projected_debt = max(existing_debt * (1 - debt_reduction * year / 5), 0)
            rows.append(
                {
                    "application_id": row.get("application_id", ""),
                    "company_id": row.get("company_id", ""),
                    "forecast_year": year,
                    "projected_revenue": round(projected_revenue, 2),
                    "projected_employees": int(projected_employees),
                    "projected_free_cash_flow": round(projected_free_cash_flow, 2),
                    "projected_debt": round(projected_debt, 2),
                }
            )
    return pd.DataFrame(rows)


def generate_seed_data(rows=1200, seed=42):
    rng = np.random.default_rng(seed)
    SEED_DIR.mkdir(parents=True, exist_ok=True)

    industries = np.array(["Construction", "Wholesale", "Manufacturing", "Logistics", "Healthcare", "Software", "Retail"])
    regions = np.array(["North America", "Western Europe", "Eastern Europe", "Latin America", "Middle East", "APAC"])
    company_types = np.array(["LLC", "Corporation", "Partnership", "Sole Proprietorship"])

    annual_revenue = rng.lognormal(mean=14.6, sigma=1.0, size=rows).clip(80_000, 80_000_000)
    requested_amount = (annual_revenue * rng.uniform(0.04, 0.55, size=rows)).clip(15_000, 7_500_000)
    years_in_business = rng.gamma(shape=2.4, scale=3.2, size=rows).clip(0.2, 60)
    existing_debt = (annual_revenue * rng.uniform(0.02, 0.95, size=rows)).clip(0, 50_000_000)
    num_recent_loans = rng.poisson(1.5, rows).clip(0, 12)
    late_payment_ratio = rng.beta(1.5, 9.0, rows).clip(0, 1)
    suspicious_transfer_ratio = rng.beta(1.1, 14.0, rows).clip(0, 1)
    collateral_ratio = rng.beta(2.5, 2.2, rows).clip(0, 2)
    employees = np.maximum((annual_revenue / rng.uniform(80_000, 230_000, rows)).astype(int), 1).clip(1, 12000)
    country_risk_score = rng.beta(1.7, 4.8, rows).clip(0, 1)
    term_months = rng.choice([12, 18, 24, 36, 48, 60, 72, 84], size=rows, p=[0.05, 0.08, 0.16, 0.32, 0.18, 0.13, 0.05, 0.03])

    industry = rng.choice(industries, size=rows)
    region = rng.choice(regions, size=rows, p=[0.29, 0.24, 0.12, 0.12, 0.08, 0.15])
    company_type = rng.choice(company_types, size=rows, p=[0.42, 0.34, 0.15, 0.09])

    debt_pressure = existing_debt / np.maximum(annual_revenue, 1)
    request_pressure = requested_amount / np.maximum(annual_revenue, 1)
    industry_cash_margin = {
        "Software": 0.14,
        "Healthcare": 0.08,
        "Manufacturing": 0.06,
        "Logistics": 0.04,
        "Retail": 0.03,
        "Wholesale": 0.025,
        "Construction": 0.02,
    }
    base_cash_margin = np.array([industry_cash_margin[item] for item in industry])
    cash_flow_margin = (
        base_cash_margin
        + rng.normal(0, 0.08, rows)
        - 0.10 * debt_pressure
        - 0.10 * request_pressure
        - 0.10 * late_payment_ratio
        - 0.04 * np.minimum(num_recent_loans / 6, 1)
        - 0.04 * country_risk_score
    ).clip(-0.45, 0.35)
    free_cash_flow = annual_revenue * cash_flow_margin
    baseline_burn = (annual_revenue / 12) * rng.uniform(0.004, 0.025, rows)
    monthly_burn_rate = np.where(free_cash_flow < 0, np.abs(free_cash_flow) / 12 + baseline_burn, baseline_burn)
    liquidity_ratio = (rng.uniform(0.03, 0.32, rows) - 0.08 * debt_pressure - 0.04 * late_payment_ratio).clip(0.01, 0.45)
    cash_balance = annual_revenue * liquidity_ratio
    expected_runway_months = np.where(
        monthly_burn_rate > 0,
        cash_balance / np.maximum(monthly_burn_rate, 1),
        60,
    ).clip(0, 60)
    industry_growth = {
        "Software": 0.16,
        "Healthcare": 0.10,
        "Manufacturing": 0.07,
        "Logistics": 0.08,
        "Retail": 0.05,
        "Wholesale": 0.06,
        "Construction": 0.07,
    }
    base_growth = np.array([industry_growth[item] for item in industry])
    forecast_revenue_cagr = (
        base_growth
        + rng.normal(0, 0.06, rows)
        + 0.03 * (years_in_business < 3)
        + 0.02 * (requested_amount / np.maximum(annual_revenue, 1))
    ).clip(-0.12, 0.55)
    forecast_employee_cagr = (
        forecast_revenue_cagr * rng.uniform(0.35, 0.85, rows)
        + rng.normal(0, 0.025, rows)
    ).clip(-0.05, 0.40)
    forecast_fcf_margin_year5 = (
        cash_flow_margin
        + rng.uniform(0.02, 0.14, rows)
        - 0.05 * late_payment_ratio
        - 0.03 * country_risk_score
    ).clip(-0.20, 0.30)
    planned_debt_reduction_pct = (
        rng.uniform(0.05, 0.45, rows)
        + 0.10 * (free_cash_flow > 0)
        - 0.08 * (expected_runway_months < 9)
    ).clip(0, 0.75)
    forecast_plan_confidence_score = (
        0.70
        - 0.30 * (forecast_revenue_cagr > 0.24)
        - 0.22 * (expected_runway_months < 9)
        - 0.18 * (cash_flow_margin < 0)
        - 0.10 * (years_in_business < 2)
        + rng.normal(0, 0.08, rows)
    ).clip(0.15, 0.95)

    applications = pd.DataFrame(
        {
            "application_id": [f"APP-{i:05d}" for i in range(1, rows + 1)],
            "company_id": [f"CO-{i:05d}" for i in range(1, rows + 1)],
            "company_name": [f"Company {i:05d}" for i in range(1, rows + 1)],
            "industry": industry,
            "region": region,
            "company_type": company_type,
            "requested_amount": requested_amount.round(2),
            "term_months": term_months,
            "annual_revenue": annual_revenue.round(2),
            "years_in_business": years_in_business.round(1),
            "existing_debt": existing_debt.round(2),
            "num_recent_loans": num_recent_loans,
            "late_payment_ratio": late_payment_ratio.round(3),
            "suspicious_transfer_ratio": suspicious_transfer_ratio.round(3),
            "collateral_ratio": collateral_ratio.round(3),
            "employees": employees,
            "country_risk_score": country_risk_score.round(3),
            "free_cash_flow": free_cash_flow.round(2),
            "monthly_burn_rate": monthly_burn_rate.round(2),
            "cash_flow_to_revenue_ratio": cash_flow_margin.round(4),
            "expected_runway_months": expected_runway_months.round(1),
            "forecast_revenue_cagr": forecast_revenue_cagr.round(4),
            "forecast_employee_cagr": forecast_employee_cagr.round(4),
            "forecast_fcf_margin_year5": forecast_fcf_margin_year5.round(4),
            "planned_debt_reduction_pct": planned_debt_reduction_pct.round(4),
            "forecast_plan_confidence_score": forecast_plan_confidence_score.round(4),
        }
    )
    applications = add_derived_features(applications)

    region_risk = np.isin(region, ["Eastern Europe", "Latin America", "Middle East"]).astype(float)
    industry_risk = np.isin(industry, ["Construction", "Wholesale", "Logistics"]).astype(float)
    risk_score = (
        -3.45
        + 1.15 * applications["debt_to_revenue_ratio"]
        + 1.25 * applications["request_to_revenue_ratio"]
        + 0.90 * applications["loan_velocity_score"]
        + 1.20 * applications["payment_stress_score"]
        + 1.10 * applications["collateral_gap_ratio"]
        + 0.95 * applications["external_financing_pressure"]
        + 1.10 * applications["financial_distress_score"]
        + 1.65 * applications["transaction_anomaly_score"]
        + 0.55 * applications["company_scale_mismatch_score"]
        + 0.75 * applications["governance_complexity_score"]
        + 1.20 * applications["cash_flow_pressure_score"]
        + 0.95 * applications["runway_risk_score"]
        + 0.85 * applications["cash_conversion_risk_score"]
        + 0.70 * applications["forecast_plan_aggressiveness_score"]
        + 1.05 * applications["forecast_execution_risk_score"]
        + 0.45 * applications["forecast_debt_service_risk_score"]
        + 0.35 * region_risk
        + 0.25 * industry_risk
        + rng.normal(0, 0.45, rows)
    )
    fraud_probability = _sigmoid(risk_score)
    applications["is_fraud"] = rng.binomial(1, fraud_probability).astype(int)

    company_profiles = applications[
        ["company_id", "company_name", "industry", "region", "company_type", "annual_revenue", "years_in_business", "employees"]
    ].copy()
    cash_flows = applications[
        [
            "application_id",
            "company_id",
            "free_cash_flow",
            "monthly_burn_rate",
            "cash_flow_to_revenue_ratio",
            "expected_runway_months",
            "cash_flow_pressure_score",
            "runway_risk_score",
            "cash_conversion_risk_score",
        ]
    ].copy()
    cash_flows["cash_balance_at_application"] = cash_balance.round(2)
    forecasts = build_forecast_table(applications)
    transactions = applications[
        [
            "application_id",
            "late_payment_ratio",
            "suspicious_transfer_ratio",
            "existing_debt",
            "num_recent_loans",
            "loan_velocity_score",
            "payment_stress_score",
            "transaction_anomaly_score",
            "cash_flow_pressure_score",
            "runway_risk_score",
        ]
    ].copy()
    decisions = applications[["application_id", "is_fraud"]].copy()
    decisions["historical_action"] = np.where(decisions["is_fraud"] == 1, "Fraud confirmed", "No fraud found")

    applications.to_csv(SEED_DIR / "applications.csv", index=False)
    company_profiles.to_csv(SEED_DIR / "company_profiles.csv", index=False)
    cash_flows.to_csv(SEED_DIR / "cash_flows.csv", index=False)
    forecasts.to_csv(SEED_DIR / "forecasts.csv", index=False)
    transactions.to_csv(SEED_DIR / "transactions.csv", index=False)
    decisions.to_csv(SEED_DIR / "decisions.csv", index=False)


def load_seed_data():
    applications = pd.read_csv(SEED_DIR / "applications.csv")
    cash_flows = pd.read_csv(SEED_DIR / "cash_flows.csv")
    forecasts = pd.read_csv(SEED_DIR / "forecasts.csv")
    cash_flow_columns = [
        "free_cash_flow",
        "monthly_burn_rate",
        "cash_flow_to_revenue_ratio",
        "expected_runway_months",
    ]
    missing_cash_flow_columns = [column for column in cash_flow_columns if column not in applications.columns]
    if missing_cash_flow_columns:
        applications = applications.merge(cash_flows[["application_id", *missing_cash_flow_columns]], on="application_id", how="left")
    applications = add_derived_features(applications)
    transactions = pd.read_csv(SEED_DIR / "transactions.csv")
    derived_transaction_columns = [
        "loan_velocity_score",
        "payment_stress_score",
        "transaction_anomaly_score",
        "cash_flow_pressure_score",
        "runway_risk_score",
    ]
    if any(column not in transactions.columns for column in derived_transaction_columns):
        transactions = transactions.merge(applications[["application_id", *derived_transaction_columns]], on="application_id", how="left")
    return {
        "applications": applications,
        "company_profiles": pd.read_csv(SEED_DIR / "company_profiles.csv"),
        "cash_flows": cash_flows,
        "forecasts": forecasts,
        "transactions": transactions,
        "decisions": pd.read_csv(SEED_DIR / "decisions.csv"),
    }


def ensure_seed_data():
    required = ["applications.csv", "company_profiles.csv", "cash_flows.csv", "forecasts.csv", "transactions.csv", "decisions.csv"]
    missing_files = not SEED_DIR.exists() or any(not (SEED_DIR / name).exists() for name in required)
    missing_columns = False
    if not missing_files:
        application_columns = set(pd.read_csv(SEED_DIR / "applications.csv", nrows=1).columns)
        missing_columns = any(column not in application_columns for column in BASE_NUMERIC_COLUMNS)
    if missing_files or missing_columns:
        generate_seed_data()
    return load_seed_data()
