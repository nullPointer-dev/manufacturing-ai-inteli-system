import joblib
import pandas as pd
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_FILE = MODEL_DIR / "model.pkl"
FEATURE_FILE = MODEL_DIR / "feature_columns.pkl"

CO2_FACTOR = 0.82


# =========================================================
# LOAD MODEL + FEATURES
# =========================================================
def _load_model():
    model = joblib.load(MODEL_FILE)
    feature_cols = joblib.load(FEATURE_FILE)
    return model, feature_cols


# =========================================================
# REAL-TIME BATCH PREDICTION
# =========================================================
def predict_batch(input_params: dict):
    """
    Predict full KPI set for a new batch.
    Returns:
    Quality, Yield, Performance, Energy, CO2
    + raw chemistry metrics
    """

    model, feature_cols = _load_model()

    df = pd.DataFrame([input_params])

    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required features: {missing}")

    df = df[feature_cols]

    preds = model.predict(df)[0]

    hardness = float(preds[0])
    dissolution = float(preds[1])
    uniformity = float(preds[2])
    yield_val = float(preds[3])
    perf_val = float(preds[4])
    energy = float(preds[5])

    quality = (
        0.4 * hardness
        + 0.3 * dissolution
        + 0.3 * uniformity
    )

    co2 = energy * CO2_FACTOR

    return {
        # raw model outputs
        "Hardness": hardness,
        "Dissolution_Rate": dissolution,
        "Content_Uniformity": uniformity,

        # system KPIs
        "Quality": quality,
        "Yield": yield_val,
        "Performance": perf_val,
        "Energy": energy,
        "CO2": co2
    }