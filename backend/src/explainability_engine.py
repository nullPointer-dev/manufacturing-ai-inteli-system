import joblib
import numpy as np
import pandas as pd
import shap
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
# GLOBAL SHAP FEATURE IMPORTANCE
# =========================================================
def get_global_feature_importance():
    """
    Returns mean absolute SHAP values averaged across all target outputs.
    Uses shap.TreeExplainer on each estimator inside MultiOutputRegressor.
    """
    from data_pipeline import build_pipeline

    model, feature_cols = _load_model()

    try:
        df = build_pipeline()
        # Build feature matrix aligned to training columns
        X = df.reindex(columns=feature_cols).apply(
            pd.to_numeric, errors="coerce"
        ).fillna(0.0)

        # Use up to 100 rows as SHAP background for speed
        background = X.sample(min(100, len(X)), random_state=42).values

        shap_importances = []  # one array per target estimator

        for est in model.estimators_:
            explainer = shap.TreeExplainer(
                est,
                data=background,
                feature_perturbation="interventional",
            )
            # Compute SHAP values for the same background sample
            sv = explainer.shap_values(background, check_additivity=False)
            # sv shape: (n_samples, n_features)
            mean_abs = np.abs(sv).mean(axis=0)
            shap_importances.append(mean_abs)

        if not shap_importances:
            return None

        avg_importance = np.mean(shap_importances, axis=0)

        result_df = pd.DataFrame({
            "feature": feature_cols,
            "importance": avg_importance
        }).sort_values("importance", ascending=False)

        return result_df.reset_index(drop=True)

    except Exception as exc:
        print(f"[SHAP] Error computing SHAP values: {exc}")
        # Fallback to built-in RF feature importances
        try:
            importances = [
                est.feature_importances_
                for est in model.estimators_
                if hasattr(est, "feature_importances_")
            ]
            if not importances:
                return None
            avg = np.mean(importances, axis=0)
            return pd.DataFrame({
                "feature": feature_cols,
                "importance": avg
            }).sort_values("importance", ascending=False).reset_index(drop=True)
        except Exception:
            return None


# =========================================================
# LOCAL SHAP EXPLANATION FOR ONE ROW
# =========================================================
def explain_prediction(row_dict):
    """
    Returns SHAP-based feature contributions for a single row.
    """
    from data_pipeline import build_pipeline

    model, feature_cols = _load_model()

    try:
        df = build_pipeline()
        background = df.reindex(columns=feature_cols).apply(
            pd.to_numeric, errors="coerce"
        ).fillna(0.0).sample(min(50, len(df)), random_state=0).values

        row = pd.DataFrame([row_dict]).reindex(columns=feature_cols)
        row = row.apply(pd.to_numeric, errors="coerce").fillna(0.0)

        contributions = []
        for est in model.estimators_:
            explainer = shap.TreeExplainer(
                est,
                data=background,
                feature_perturbation="interventional",
            )
            sv = explainer.shap_values(row.values, check_additivity=False)
            contributions.append(sv[0])

        avg_contributions = np.mean(contributions, axis=0)

        return pd.DataFrame({
            "feature": feature_cols,
            "impact": avg_contributions
        }).sort_values("impact", key=np.abs, ascending=False).reset_index(drop=True)

    except Exception as exc:
        print(f"[SHAP] Local explanation error: {exc}")
        return None