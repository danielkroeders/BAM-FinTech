from pathlib import Path

import numpy as np
import pandas as pd


SEED_DIR = Path(__file__).resolve().parents[1] / "data" / "seed"

NUMERIC_COLUMNS = [
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
]

CATEGORICAL_COLUMNS = ["industry", "region", "company_type"]
TARGET_COLUMN = "is_fraud"


def _sigmoid(value):
    return 1 / (1 + np.exp(-value))


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
    short_history = np.maximum(0, 3 - years_in_business) / 3
    low_collateral = np.maximum(0, 0.65 - collateral_ratio)
    region_risk = np.isin(region, ["Eastern Europe", "Latin America", "Middle East"]).astype(float)
    industry_risk = np.isin(industry, ["Construction", "Wholesale", "Logistics"]).astype(float)

    risk_score = (
        -3.1
        + 2.2 * debt_pressure
        + 2.4 * request_pressure
        + 0.22 * num_recent_loans
        + 4.2 * suspicious_transfer_ratio
        + 2.9 * late_payment_ratio
        + 1.6 * country_risk_score
        + 1.3 * low_collateral
        + 0.8 * short_history
        + 0.45 * region_risk
        + 0.25 * industry_risk
        + rng.normal(0, 0.45, rows)
    )
    fraud_probability = _sigmoid(risk_score)
    is_fraud = rng.binomial(1, fraud_probability).astype(int)

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
            "is_fraud": is_fraud,
        }
    )

    company_profiles = applications[
        ["company_id", "company_name", "industry", "region", "company_type", "annual_revenue", "years_in_business", "employees"]
    ].copy()
    transactions = applications[
        ["application_id", "late_payment_ratio", "suspicious_transfer_ratio", "existing_debt", "num_recent_loans"]
    ].copy()
    decisions = applications[["application_id", "is_fraud"]].copy()
    decisions["historical_action"] = np.where(decisions["is_fraud"] == 1, "Fraud confirmed", "No fraud found")

    applications.to_csv(SEED_DIR / "applications.csv", index=False)
    company_profiles.to_csv(SEED_DIR / "company_profiles.csv", index=False)
    transactions.to_csv(SEED_DIR / "transactions.csv", index=False)
    decisions.to_csv(SEED_DIR / "decisions.csv", index=False)


def load_seed_data():
    return {
        "applications": pd.read_csv(SEED_DIR / "applications.csv"),
        "company_profiles": pd.read_csv(SEED_DIR / "company_profiles.csv"),
        "transactions": pd.read_csv(SEED_DIR / "transactions.csv"),
        "decisions": pd.read_csv(SEED_DIR / "decisions.csv"),
    }


def ensure_seed_data():
    required = ["applications.csv", "company_profiles.csv", "transactions.csv", "decisions.csv"]
    if not SEED_DIR.exists() or any(not (SEED_DIR / name).exists() for name in required):
        generate_seed_data()
    return load_seed_data()
