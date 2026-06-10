import pandas as pd

from src.data_pipeline import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, add_derived_features
from src.formatting import format_currency, format_months, format_percent, format_score


def _fraud_class_values(values):
    if isinstance(values, list):
        return values[1][0]
    if getattr(values, "ndim", 0) == 3:
        return values[0, :, 1]
    return values[0]


def _fraud_expected_value(expected_value):
    if isinstance(expected_value, (list, tuple)):
        return float(expected_value[1])
    if getattr(expected_value, "shape", None) and len(expected_value.shape) > 0:
        return float(expected_value[1])
    return float(expected_value)


def _feature_group(feature_name):
    for column in CATEGORICAL_COLUMNS:
        if feature_name.startswith(f"{column}_"):
            return column
    return feature_name


def _format_value(application, feature):
    value = application.get(feature, "")
    if feature.endswith("_uploaded"):
        return "Yes" if float(value or 0) >= 0.5 else "No"
    if feature in {
        "requested_amount",
        "annual_revenue",
        "existing_debt",
        "free_cash_flow",
        "monthly_burn_rate",
        "annual_interest_expense",
        "annual_debt_service",
        "stressed_annual_debt_service",
    }:
        return format_currency(value)
    if feature in {
        "interest_rate",
        "late_payment_ratio",
        "suspicious_transfer_ratio",
        "collateral_ratio",
        "country_risk_score",
        "debt_to_revenue_ratio",
        "request_to_revenue_ratio",
        "cash_flow_to_revenue_ratio",
        "collateral_gap_ratio",
        "forecast_revenue_cagr",
        "forecast_employee_cagr",
        "forecast_fcf_margin_year5",
        "planned_debt_reduction_pct",
    }:
        return format_percent(value)
    if feature in {"expected_runway_months", "email_domain_age_months", "website_age_months", "bank_account_age_months"}:
        return format_months(value, 1)
    if feature in {"receivables_days", "payables_days", "inventory_days", "cash_conversion_cycle_days"}:
        return f"{format_score(value, 0)} days"
    if feature in {"debt_service_coverage_ratio", "stressed_debt_service_coverage_ratio"}:
        return format_score(value)
    if feature.endswith("_score") or feature == "external_financing_pressure":
        return format_score(value)
    if isinstance(value, float):
        return format_score(value)
    return str(value)


def shap_driver_table(model_bundle, application):
    import shap

    pipeline = model_bundle.pipeline
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]

    application_frame = add_derived_features(pd.DataFrame([application]))
    enriched_application = application_frame.iloc[0].to_dict()
    model_columns = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS
    transformed = preprocessor.transform(application_frame[model_columns])
    feature_names = [name.replace("numeric__", "").replace("categorical__", "") for name in preprocessor.get_feature_names_out()]

    explainer = shap.TreeExplainer(classifier)
    shap_values = _fraud_class_values(explainer.shap_values(transformed))
    expected_value = _fraud_expected_value(explainer.expected_value)

    rows = []
    for feature_name, contribution in zip(feature_names, shap_values):
        group = _feature_group(feature_name)
        rows.append({"driver": group, "contribution": float(contribution)})

    grouped = pd.DataFrame(rows).groupby("driver", as_index=False)["contribution"].sum()
    grouped["application_value"] = grouped["driver"].apply(lambda feature: _format_value(enriched_application, feature))
    grouped["impact"] = grouped["contribution"].apply(
        lambda value: "Raises fraud risk" if value > 0 else "Lowers fraud risk" if value < 0 else "Neutral"
    )
    grouped["absolute_contribution"] = grouped["contribution"].abs()
    grouped = grouped.sort_values("absolute_contribution", ascending=False).reset_index(drop=True)

    predicted_probability = float(model_bundle.pipeline.predict_proba(application_frame[model_columns])[:, 1][0])
    return grouped, expected_value, predicted_probability
