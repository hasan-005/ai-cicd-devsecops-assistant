from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "failure_model.joblib"


model = joblib.load(MODEL_PATH)


FEATURES = [
    "build_time",
    "tests_failed",
    "cpu_usage",
    "memory_usage",
    "vulnerabilities"
]


def predict_failure(
    build_time,
    tests_failed,
    cpu_usage,
    memory_usage,
    vulnerabilities
):
    input_data = pd.DataFrame(
        [[
            build_time,
            tests_failed,
            cpu_usage,
            memory_usage,
            vulnerabilities
        ]],
        columns=FEATURES
    )

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    failed_class_index = list(
        model.classes_
    ).index(1)

    failure_probability = (
        probabilities[failed_class_index] * 100
    )

    predicted_status = (
        "failed"
        if prediction == 1
        else "success"
    )

    # -----------------------------
    # Risk level
    # -----------------------------

    if failure_probability >= 75:
        risk_level = "High"

    elif failure_probability >= 50:
        risk_level = "Medium"

    elif failure_probability >= 25:
        risk_level = "Low"

    else:
        risk_level = "Minimal"


    # -----------------------------
    # Simple explanation
    # -----------------------------

    reasons = []

    if tests_failed >= 3:
        reasons.append(
            "High number of failed tests"
        )

    if build_time >= 210:
        reasons.append(
            "Build time is relatively high"
        )

    if cpu_usage >= 70:
        reasons.append(
            "CPU usage is high"
        )

    if memory_usage >= 600:
        reasons.append(
            "Memory usage is high"
        )

    if vulnerabilities >= 2:
        reasons.append(
            "Multiple security vulnerabilities detected"
        )

    if not reasons:
        reasons.append(
            "Pipeline metrics are within normal ranges"
        )


    # -----------------------------
    # Global model feature importance
    # -----------------------------

    importance_values = (
        model.feature_importances_
    )

    feature_importance = {
        feature: round(
            float(importance) * 100,
            2
        )
        for feature, importance
        in zip(
            FEATURES,
            importance_values
        )
    }


    return {
        "predicted_status":
            predicted_status,

        "failure_probability":
            round(
                failure_probability,
                2
            ),

        "risk_level":
            risk_level,

        "reasons":
            reasons,

        "feature_importance":
            feature_importance
    }