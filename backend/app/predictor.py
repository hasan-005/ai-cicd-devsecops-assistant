from pathlib import Path
from typing import Any

import joblib
import pandas as pd


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "failure_model.joblib"
)


FEATURES = [
    "build_time",
    "tests_failed",
    "cpu_usage",
    "memory_usage",
    "vulnerabilities"
]


# Cached ML model
_model = None

# Used to detect whether the model file was retrained/changed
_model_modified_time = None


# ============================================================
# MODEL LOADING
# ============================================================

def get_model():
    """
    Load the ML model only when prediction is requested.

    This prevents FastAPI / pytest from crashing during startup
    when the model file is not available.

    The model is cached after loading and automatically reloaded
    if the model file changes.
    """

    global _model
    global _model_modified_time

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found at: {MODEL_PATH}. "
            "Run 'python ml/train_model.py' first."
        )

    current_modified_time = MODEL_PATH.stat().st_mtime

    model_needs_reload = (
        _model is None
        or _model_modified_time != current_modified_time
    )

    if model_needs_reload:
        _model = joblib.load(MODEL_PATH)

        _model_modified_time = current_modified_time

    return _model


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_inputs(
    build_time: float,
    tests_failed: int,
    cpu_usage: float,
    memory_usage: float,
    vulnerabilities: int
):
    """
    Validate prediction inputs before they reach the ML model.
    """

    if build_time < 0:
        raise ValueError(
            "Build time cannot be negative."
        )

    if tests_failed < 0:
        raise ValueError(
            "Failed tests cannot be negative."
        )

    if not 0 <= cpu_usage <= 100:
        raise ValueError(
            "CPU usage must be between 0 and 100."
        )

    if memory_usage < 0:
        raise ValueError(
            "Memory usage cannot be negative."
        )

    if vulnerabilities < 0:
        raise ValueError(
            "Vulnerability count cannot be negative."
        )


# ============================================================
# RISK LEVEL
# ============================================================

def calculate_risk_level(
    failure_probability: float
):
    """
    Convert failure probability into a risk category.
    """

    if failure_probability >= 90:
        return "Critical"

    if failure_probability >= 75:
        return "High"

    if failure_probability >= 50:
        return "Medium"

    if failure_probability >= 25:
        return "Low"

    return "Minimal"


# ============================================================
# RISK FLAGS
# ============================================================

def generate_risk_flags(
    build_time: float,
    tests_failed: int,
    cpu_usage: float,
    memory_usage: float,
    vulnerabilities: int
):
    """
    Generate human-readable risk factors.

    These explanations are rule-based.
    They are not direct explanations produced by the ML model.
    """

    flags = []

    # --------------------------------------------------------
    # Failed tests
    # --------------------------------------------------------

    if tests_failed >= 8:
        flags.append({
            "factor": "tests_failed",
            "severity": "critical",
            "message":
                "A very high number of tests are failing."
        })

    elif tests_failed >= 3:
        flags.append({
            "factor": "tests_failed",
            "severity": "high",
            "message":
                "Multiple automated tests are failing."
        })

    elif tests_failed > 0:
        flags.append({
            "factor": "tests_failed",
            "severity": "medium",
            "message":
                "Some automated tests are failing."
        })


    # --------------------------------------------------------
    # Build time
    # --------------------------------------------------------

    if build_time >= 300:
        flags.append({
            "factor": "build_time",
            "severity": "high",
            "message":
                "Build duration is significantly high."
        })

    elif build_time >= 210:
        flags.append({
            "factor": "build_time",
            "severity": "medium",
            "message":
                "Build duration is higher than expected."
        })


    # --------------------------------------------------------
    # CPU
    # --------------------------------------------------------

    if cpu_usage >= 90:
        flags.append({
            "factor": "cpu_usage",
            "severity": "high",
            "message":
                "CPU utilization is extremely high."
        })

    elif cpu_usage >= 70:
        flags.append({
            "factor": "cpu_usage",
            "severity": "medium",
            "message":
                "CPU utilization is elevated."
        })


    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------

    if memory_usage >= 900:
        flags.append({
            "factor": "memory_usage",
            "severity": "high",
            "message":
                "Memory consumption is extremely high."
        })

    elif memory_usage >= 600:
        flags.append({
            "factor": "memory_usage",
            "severity": "medium",
            "message":
                "Memory consumption is elevated."
        })


    # --------------------------------------------------------
    # Security vulnerabilities
    # --------------------------------------------------------

    if vulnerabilities >= 6:
        flags.append({
            "factor": "vulnerabilities",
            "severity": "critical",
            "message":
                "A large number of security vulnerabilities were detected."
        })

    elif vulnerabilities >= 2:
        flags.append({
            "factor": "vulnerabilities",
            "severity": "high",
            "message":
                "Multiple security vulnerabilities were detected."
        })

    elif vulnerabilities == 1:
        flags.append({
            "factor": "vulnerabilities",
            "severity": "medium",
            "message":
                "A security vulnerability was detected."
        })


    # --------------------------------------------------------
    # Healthy pipeline
    # --------------------------------------------------------

    if not flags:
        flags.append({
            "factor": "overall",
            "severity": "safe",
            "message":
                "Pipeline metrics are within normal ranges."
        })

    return flags


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def generate_recommendations(
    build_time: float,
    tests_failed: int,
    cpu_usage: float,
    memory_usage: float,
    vulnerabilities: int
):
    """
    Generate practical recommendations based on pipeline metrics.
    """

    recommendations = []

    if tests_failed > 0:
        recommendations.append(
            "Investigate and fix failing automated tests "
            "before deployment."
        )

    if build_time >= 210:
        recommendations.append(
            "Optimize build steps, dependency installation, "
            "and caching."
        )

    if cpu_usage >= 70:
        recommendations.append(
            "Review CPU-intensive operations and parallel "
            "build processes."
        )

    if memory_usage >= 600:
        recommendations.append(
            "Inspect memory-heavy processes and reduce "
            "unnecessary allocations."
        )

    if vulnerabilities > 0:
        recommendations.append(
            "Review Trivy findings and patch vulnerable "
            "dependencies."
        )

    if not recommendations:
        recommendations.append(
            "Pipeline metrics look healthy. "
            "Continue monitoring future runs."
        )

    return recommendations


# ============================================================
# GLOBAL FEATURE IMPORTANCE
# ============================================================

def get_feature_importance(
    model
) -> list[dict[str, Any]]:
    """
    Return Random Forest global feature importance.

    This explains which features are important to the model
    overall.

    It does NOT explain one individual prediction.
    """

    if not hasattr(
        model,
        "feature_importances_"
    ):
        return []

    importance_values = model.feature_importances_

    results = []

    for feature, importance in zip(
        FEATURES,
        importance_values
    ):
        results.append({
            "feature": feature,
            "importance_percent": round(
                float(importance) * 100,
                2
            )
        })

    results.sort(
        key=lambda item:
            item["importance_percent"],
        reverse=True
    )

    return results


# ============================================================
# MAIN PREDICTION FUNCTION
# ============================================================

def predict_failure(
    build_time: float,
    tests_failed: int,
    cpu_usage: float,
    memory_usage: float,
    vulnerabilities: int
):
    """
    Predict CI/CD pipeline failure probability.
    """

    # --------------------------------------------------------
    # Validate values
    # --------------------------------------------------------

    validate_inputs(
        build_time,
        tests_failed,
        cpu_usage,
        memory_usage,
        vulnerabilities
    )


    # --------------------------------------------------------
    # Load model only when prediction is requested
    # --------------------------------------------------------

    model = get_model()


    # --------------------------------------------------------
    # Prepare ML input
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = int(
        model.predict(
            input_data
        )[0]
    )


    # --------------------------------------------------------
    # Probabilities
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        input_data
    )[0]


    classes = list(
        model.classes_
    )


    if 1 not in classes:
        raise ValueError(
            "The trained model does not contain "
            "the failure class (1)."
        )


    failed_class_index = classes.index(1)


    failure_probability = (
        float(
            probabilities[
                failed_class_index
            ]
        )
        * 100
    )


    success_probability = (
        100 - failure_probability
    )


    # --------------------------------------------------------
    # Predicted status
    # --------------------------------------------------------

    predicted_status = (
        "failed"
        if prediction == 1
        else "success"
    )


    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = max(
        failure_probability,
        success_probability
    )


    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    risk_level = calculate_risk_level(
        failure_probability
    )


    # --------------------------------------------------------
    # Risk explanations
    # --------------------------------------------------------

    risk_flags = generate_risk_flags(
        build_time,
        tests_failed,
        cpu_usage,
        memory_usage,
        vulnerabilities
    )


    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = generate_recommendations(
        build_time,
        tests_failed,
        cpu_usage,
        memory_usage,
        vulnerabilities
    )


    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    feature_importance = get_feature_importance(
        model
    )


    # --------------------------------------------------------
    # Final API-friendly result
    # --------------------------------------------------------

    return {

        "prediction": {

            "predicted_status":
                predicted_status,

            "failure_probability":
                round(
                    failure_probability,
                    2
                ),

            "success_probability":
                round(
                    success_probability,
                    2
                ),

            "confidence":
                round(
                    confidence,
                    2
                ),

            "risk_level":
                risk_level
        },


        "risk_flags":
            risk_flags,


        "recommendations":
            recommendations,


        "global_feature_importance":
            feature_importance,


        "model_info": {

            "algorithm":
                type(model).__name__,

            "features_used":
                FEATURES,

            "number_of_features":
                len(FEATURES),

            "model_file":
                MODEL_PATH.name
        }
    }


# ============================================================
# MODEL STATUS
# ============================================================

def get_model_status():
    """
    Return basic model status information.

    Later this can be displayed on the dashboard.
    """

    return {

        "model_exists":
            MODEL_PATH.exists(),

        "model_path":
            str(MODEL_PATH),

        "features":
            FEATURES,

        "feature_count":
            len(FEATURES),

        "loaded_in_memory":
            _model is not None
    }