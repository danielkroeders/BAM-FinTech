from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data_pipeline import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, TARGET_COLUMN


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


def train_model(applications):
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
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
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
    revenue = max(float(application.get("annual_revenue", 1)), 1)
    requested_amount = float(application.get("requested_amount", 0))
    existing_debt = float(application.get("existing_debt", 0))

    if requested_amount / revenue > 0.35:
        flags.append("Requested amount is high relative to annual revenue.")
    if existing_debt / revenue > 0.65:
        flags.append("Existing debt pressure is elevated.")
    if float(application.get("num_recent_loans", 0)) >= 4:
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
    return flags


def score_application(model_bundle, application):
    frame = pd.DataFrame([application])
    probability = float(model_bundle.pipeline.predict_proba(frame[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS])[:, 1][0])
    grade = grade_from_probability(probability)
    return {
        "fraud_probability": probability,
        "grade": grade,
        "decision": decision_from_grade(grade),
        "flags": rule_flags(application),
    }


def score_portfolio(model_bundle, applications):
    scored = applications.copy()
    probabilities = model_bundle.pipeline.predict_proba(scored[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS])[:, 1]
    scored["fraud_probability"] = probabilities
    scored["grade"] = [grade_from_probability(probability) for probability in probabilities]
    scored["decision"] = [decision_from_grade(grade) for grade in scored["grade"]]
    return scored
