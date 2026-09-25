from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "pipeline_data.csv"
MODEL_FILE = BASE_DIR / "failure_model.joblib"


# Load dataset
data = pd.read_csv(DATA_FILE)


# Features used for prediction
features = [
    "build_time",
    "tests_failed",
    "cpu_usage",
    "memory_usage",
    "vulnerabilities"
]


X = data[features]


# Convert status into numbers
# success = 0
# failed = 1
y = data["status"].map({
    "success": 0,
    "failed": 1
})


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)


# Create Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# Train model
model.fit(X_train, y_train)


# Test model
predictions = model.predict(X_test)


accuracy = accuracy_score(
    y_test,
    predictions
)


print("\n--- MODEL RESULTS ---")

print(
    f"\nAccuracy: {accuracy:.2f}"
)


print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Success",
            "Failed"
        ],
        zero_division=0
    )
)


# Save trained model
joblib.dump(
    model,
    MODEL_FILE
)


print(
    f"\nModel saved to: {MODEL_FILE}"
)