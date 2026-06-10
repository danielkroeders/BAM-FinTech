from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data_pipeline import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, TARGET_COLUMN, add_derived_features


THRESHOLD_MAP = {"A": 0.15, "B": 0.28, "C": 0.42, "D": 0.58, "E": 0.74, "F": 1.0}


@dataclass
class ModelBundle:
    pipeline: Pipeline
    metrics: dict
    feature_importance: pd.DataFrame
    threshold_map: dict

    def score_one(self, application):
        return score_application(self, application)


def _one_hot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def _precision_at_top_percent(y_true, probabilities, percent=0.10):
    scored = pd.DataFrame({"actual": y_true, "probability": probabilities}).sort_values("probability", ascending=False)
    top_n = max(1, int(len(scored) * percent))
    return float(scored.head(top_n)["actual"].mean())


def train_model(applications):
    applications = add_derived_features(applications)
    X = applications[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS]
    y = applications[TARGET_COLUMN]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", _one_hot_encoder()),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_COLUMNS),
            ("categorical", categorical_pipeline, CATEGORICAL_COLUMNS),
        ]
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=220, min_samples_leaf=4, random_state=42, class_weight="balanced")),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]
    tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "balanced_accuracy": balanced_accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "average_precision": average_precision_score(y_test, probabilities),
        "mcc": matthews_corrcoef(y_test, predictions),
        "precision_at_10pct": _precision_at_top_percent(y_test, probabilities),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }

    feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
    feature_names = [name.replace("numeric__", "").replace("categorical__", "") for name in feature_names]
    importances = pipeline.named_steps["classifier"].feature_importances_
    feature_importance = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    return ModelBundle(pipeline=pipeline, metrics=metrics, feature_importance=feature_importance, threshold_map=THRESHOLD_MAP)


def grade_from_probability(probability):
    if probability < 0.15:
        return "A"
    if probability < 0.28:
        return "B"
    if probability < 0.42:
        return "C"
    if probability < 0.58:
        return "D"
    if probability < 0.74:
        return "E"
    return "F"


def decision_from_grade(grade):
    if grade in {"A", "B"}:
        return "Approve"
    if grade in {"C", "D"}:
        return "Manual Review"
    return "Reject"


def rule_flags(application):
    flags = []
    derived = add_derived_features(pd.DataFrame([application])).iloc[0]

    if float(derived["request_to_revenue_ratio"]) > 0.35:
        flags.append("Requested amount is high relative to annual revenue.")
    if float(derived["debt_to_revenue_ratio"]) > 0.65:
        flags.append("Existing debt pressure is elevated.")
    if float(derived["loan_velocity_score"]) >= 0.67:
        flags.append("Multiple recent loans suggest possible credit stacking.")
    if float(application.get("late_payment_ratio", 0)) >= 0.2:
        flags.append("Late payment ratio is above normal portfolio levels.")
    if float(application.get("suspicious_transfer_ratio", 0)) >= 0.12:
        flags.append("Suspicious transfer ratio is elevated.")
    if float(application.get("collateral_ratio", 0)) < 0.45:
        flags.append("Collateral coverage is low.")
    if float(application.get("years_in_business", 0)) < 2:
        flags.append("Operating history is short.")
    if float(application.get("country_risk_score", 0)) >= 0.55:
        flags.append("Country risk score is elevated.")
    if float(derived["external_financing_pressure"]) >= 0.72:
        flags.append("External financing pressure is high based on debt, request size, and recent borrowing.")
    if float(derived["financial_distress_score"]) >= 0.55:
        flags.append("Financial distress score is elevated.")
    if float(derived["transaction_anomaly_score"]) >= 0.22:
        flags.append("Transaction anomaly score is elevated.")
    if float(derived["company_scale_mismatch_score"]) >= 0.65:
        flags.append("Reported company scale looks stretched relative to the requested exposure.")
    if float(derived.get("free_cash_flow", 0)) < 0:
        flags.append("Free cash flow is negative at application date.")
    if float(derived["cash_flow_pressure_score"]) >= 0.55:
        flags.append("Cash-flow pressure is elevated based on burn rate and free cash flow.")
    if float(derived["runway_risk_score"]) >= 0.50:
        flags.append("Expected runway is under six months.")
    if float(derived["cash_conversion_risk_score"]) >= 0.55:
        flags.append("Cash conversion is weak relative to reported revenue.")
    if float(derived["forecast_revenue_cagr"]) >= 0.25 and float(derived["forecast_plan_confidence_score"]) < 0.45:
        flags.append("Five-year revenue growth forecast is aggressive with low plan confidence.")
    if float(derived["forecast_plan_aggressiveness_score"]) >= 0.45:
        flags.append("Five-year plan assumptions appear aggressive relative to current operating signals.")
    if float(derived["forecast_execution_risk_score"]) >= 0.50:
        flags.append("Forecast execution risk is elevated.")
    if float(derived["forecast_hiring_efficiency_risk_score"]) >= 0.45:
        flags.append("Revenue growth plan may be under-supported by employee growth.")
    if float(derived["forecast_debt_service_risk_score"]) >= 0.45:
        flags.append("Debt reduction plan may be strained by current cash-flow pressure.")
    return flags


def score_application(model_bundle, application):
    frame = add_derived_features(pd.DataFrame([application]))
    probability = float(model_bundle.pipeline.predict_proba(frame[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS])[:, 1][0])
    grade = grade_from_probability(probability)
    return {
        "fraud_probability": probability,
        "grade": grade,
        "decision": decision_from_grade(grade),
        "flags": rule_flags(application),
    }


def score_portfolio(model_bundle, applications):
    scored = add_derived_features(applications)
    probabilities = model_bundle.pipeline.predict_proba(scored[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS])[:, 1]
    scored["fraud_probability"] = probabilities
    scored["grade"] = [grade_from_probability(probability) for probability in probabilities]
    scored["decision"] = [decision_from_grade(grade) for grade in scored["grade"]]
    return scored
