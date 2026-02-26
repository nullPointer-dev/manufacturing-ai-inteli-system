import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_FILE = MODEL_DIR / "model.pkl"
FEATURE_FILE = MODEL_DIR / "feature_columns.pkl"


# =========================================================
# LOAD MODEL + FEATURES
# =========================================================
def _load_model():
    model = joblib.load(MODEL_FILE)
    feature_cols = joblib.load(FEATURE_FILE)
    return model, feature_cols


# =========================================================
# GLOBAL FEATURE IMPORTANCE
# =========================================================
def get_global_feature_importance():
    """
    Returns feature importance averaged across all outputs.
    Works with RandomForest inside MultiOutputRegressor.
    """

    model, feature_cols = _load_model()

    try:
        # MultiOutputRegressor → list of estimators
        importances = []

        for est in model.estimators_:
            if hasattr(est, "feature_importances_"):
                importances.append(est.feature_importances_)

        if not importances:
            return None

        avg_importance = np.mean(importances, axis=0)

        df = pd.DataFrame({
            "feature": feature_cols,
            "importance": avg_importance
        }).sort_values("importance", ascending=False)

        return df.reset_index(drop=True)

    except Exception:
        return None


# =========================================================
# LOCAL EXPLANATION FOR ONE ROW
# =========================================================
def explain_prediction(row_dict):
    """
    Returns feature contribution proxy for a single optimized row.
    Lightweight version without SHAP dependency.
    """

    model, feature_cols = _load_model()

    try:
        row = pd.DataFrame([row_dict])
        row = row[feature_cols]

        baseline = np.zeros(len(feature_cols))
        contributions = []

        for i, col in enumerate(feature_cols):
            temp = row.copy()
            temp[col] = baseline[i]

            pred_full = model.predict(row)[0]
            pred_zero = model.predict(temp)[0]

            diff = pred_full - pred_zero
            contributions.append(float(np.mean(diff)))

        df = pd.DataFrame({
            "feature": feature_cols,
            "impact": contributions
        }).sort_values("impact", ascending=False)

        return df.reset_index(drop=True)

    except Exception:
        return None