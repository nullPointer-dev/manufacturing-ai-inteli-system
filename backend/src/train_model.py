from pathlib import Path
import logging
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

logger = logging.getLogger(__name__)


# =========================================================
# GLOBAL MODEL DIRECTORY (PROJECT ROOT /models)
# =========================================================
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "model.pkl"
FEATURE_FILE = MODEL_DIR / "feature_columns.pkl"
METRICS_FILE = MODEL_DIR / "model_metrics.json"
AGGREGATE_METRICS_FILE = MODEL_DIR / "model_aggregate_metrics.json"
DRIFT_BASELINE_FILE = MODEL_DIR / "drift_baseline.json"
SCALING_PARAMS_FILE = MODEL_DIR / "scaling_params.json"
VERSION_LOG = MODEL_DIR / "model_versions.json"


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

    logger.info("Training model on %d samples with %d features...", len(X_train), len(feature_cols))
    model.fit(X_train, y_train)

    logger.info("Evaluating model on test set (%d samples)...", len(X_test))
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
    r2 = float(np.mean([r2_score(y_test.iloc[:, i], preds[:, i]) for i in range(preds.shape[1])]))
    # MAPE per target (guarded against divide-by-zero), then averaged
    mape = float(np.mean([
        np.mean(np.abs((y_test.iloc[:, i].values - preds[:, i]) / (np.abs(y_test.iloc[:, i].values) + 1e-6)))
        for i in range(preds.shape[1])
    ]))

    # Save aggregate metrics separately so the governance backfill
    # can always find mae, rmse, r2, mape without re-computing them.
    aggregate = {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": r2,
        "mape": mape,
    }
    with open(AGGREGATE_METRICS_FILE, "w") as f:
        json.dump(aggregate, f, indent=2)

    # -----------------------------------------------------
    # SAVE DRIFT BASELINE (used by drift detection on next run)
    # -----------------------------------------------------
    baseline = {
        "energy_mean": float(df["total_energy"].mean()),
        "energy_std": float(df["total_energy"].std()),
        "anomaly_rate": float(df["anomaly_flag"].mean()) if "anomaly_flag" in df.columns else 0.0,
        "n_samples": int(len(df)),
    }
    with open(DRIFT_BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=2)

    # -----------------------------------------------------
    # SAVE SCALING PARAMS (used by prediction_service and batch_scorer)
    # These replace all hardcoded min/max constants so rescaling
    # remains correct automatically after any re-train.
    # -----------------------------------------------------
    cu_min = float(df["Content_Uniformity"].min())
    cu_max = float(df["Content_Uniformity"].max())
    ps_min = float(df["performance_score"].min())
    ps_max = float(df["performance_score"].max())
    ys_min = float(df["yield_score"].min())
    ys_max = float(df["yield_score"].max())

    scaling_params = {
        "content_uniformity_min": cu_min,
        "content_uniformity_max": cu_max,
        "performance_score_min": ps_min,
        "performance_score_max": ps_max,
        "yield_score_min": ys_min,
        "yield_score_max": ys_max,
        # derived helpers used directly in rescaling formulas
        "yield_scale_range": cu_max - cu_min if cu_max != cu_min else 1.0,
        "yield_score_range": ys_max - ys_min if ys_max != ys_min else 1.0,
        "perf_scale_range": ps_max - ps_min if ps_max != ps_min else 1.0,
    }
    with open(SCALING_PARAMS_FILE, "w") as f:
        json.dump(scaling_params, f, indent=2)

    # -----------------------------------------------------
    # SAVE MODEL
    # -----------------------------------------------------
    joblib.dump(model, MODEL_FILE)

    logger.info("Model saved to: %s", MODEL_FILE)
    logger.info("Feature columns saved to: %s", FEATURE_FILE)
    logger.info("Metrics: MAE=%.4f  RMSE=%.4f  R2=%.4f", mae, rmse, r2)
    logger.info("Scaling params saved to: %s", SCALING_PARAMS_FILE)

    # -----------------------------------------------------------------
    # WRITE VERSION LOG (read by governance page via api_get_model_history)
    # Same schema used by learning_controller.py so both code paths produce
    # consistent entries in model_versions.json.
    # -----------------------------------------------------------------
    if VERSION_LOG.exists():
        try:
            with open(VERSION_LOG, "r") as f:
                version_history = json.load(f)
        except Exception:
            version_history = []
    else:
        version_history = []

    version_entry = {
        "time": datetime.now().isoformat(),
        "reason": {"initial_training": True},
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": r2,
            "mape": mape,
        },
        "dataset_size": int(len(df)),
        "model_version": len(version_history) + 1,
    }
    version_history.append(version_entry)
    with open(VERSION_LOG, "w") as f:
        json.dump(version_history, f, indent=2)

    logger.info("Version log updated: v%d", version_entry["model_version"])

    return model, {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": r2,
        "mape": mape
    }


# =========================================================
# SCRIPT ENTRY
# =========================================================
if __name__ == "__main__":
    train_and_save_model()