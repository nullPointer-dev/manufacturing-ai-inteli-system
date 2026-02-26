from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import json
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from data_pipeline import build_pipeline


# =========================================================
# GLOBAL MODEL DIRECTORY (PROJECT ROOT /models)
# =========================================================
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "model.pkl"
FEATURE_FILE = MODEL_DIR / "feature_columns.pkl"
METRICS_FILE = MODEL_DIR / "model_metrics.json"


# =========================================================
# TRAIN & SAVE MODEL
# =========================================================
def train_and_save_model(data_folder=None):
    """
    Trains multi-target regression model.
    Saves:
        - model.pkl
        - feature_columns.pkl
        - model_metrics.json
    Returns:
        model, aggregate_metrics
    """

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------
    df = build_pipeline()

    targets = [
        "Hardness",
        "Dissolution_Rate",
        "Content_Uniformity",
        "yield_score",
        "performance_score",
        "total_energy"
    ]

    missing_targets = [t for t in targets if t not in df.columns]
    if missing_targets:
        raise KeyError(f"Missing target columns in dataframe: {missing_targets}")

    # -----------------------------------------------------
    # FEATURE SELECTION
    # -----------------------------------------------------
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c not in targets and c != "Batch_ID"]

    if len(feature_cols) == 0:
        raise ValueError("No numeric feature columns found after excluding targets and Batch_ID")

    # Save feature order for prediction consistency
    joblib.dump(feature_cols, FEATURE_FILE)

    X = df[feature_cols]
    y = df[targets]

    # -----------------------------------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # -----------------------------------------------------
    # MODEL
    # -----------------------------------------------------
    base_estimator = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=1
    )

    model = MultiOutputRegressor(base_estimator)

    print("Training model...")
    model.fit(X_train, y_train)

    print("Evaluating model on test set...")
    preds = model.predict(X_test)

    # -----------------------------------------------------
    # PER-TARGET METRICS
    # -----------------------------------------------------
    metrics = {}

    for i, target in enumerate(targets):
        mae = mean_absolute_error(y_test.iloc[:, i], preds[:, i])
        r2 = r2_score(y_test.iloc[:, i], preds[:, i])

        metrics[target] = {
            "mae": float(mae),
            "r2": float(r2)
        }

    # Save detailed metrics
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    # -----------------------------------------------------
    # AGGREGATE METRICS (FOR GOVERNANCE)
    # -----------------------------------------------------
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mape = np.mean(np.abs((y_test - preds) / (y_test + 1e-6))) * 100

    # -----------------------------------------------------
    # SAVE MODEL
    # -----------------------------------------------------
    joblib.dump(model, MODEL_FILE)

    print(f"\nModel saved to: {MODEL_FILE}")
    print(f"Feature columns saved to: {FEATURE_FILE}")
    print(f"Metrics saved to: {METRICS_FILE}")

    return model, {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": float(mape)
    }


# =========================================================
# SCRIPT ENTRY
# =========================================================
if __name__ == "__main__":
    train_and_save_model()