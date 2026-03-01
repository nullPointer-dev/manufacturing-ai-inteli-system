from pathlib import Path
import joblib
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

CO2_FACTOR = 0.82


def attach_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attach model predictions and derived KPIs to dataframe.

    Guarantees presence of:
    Quality, Yield, Performance, Energy, CO2
    """

    df = df.copy()

    model_path = MODEL_DIR / "model.pkl"
    cols_path = MODEL_DIR / "feature_columns.pkl"

    if not model_path.exists() or not cols_path.exists():
        # model not trained yet → return safe defaults
        for col in ["Quality", "Yield", "Performance", "Energy", "CO2"]:
            if col not in df.columns:
                df[col] = 0.0
        return df

    model = joblib.load(model_path)
    feature_cols = joblib.load(cols_path)

    # ensure required feature columns exist
    missing = [c for c in feature_cols if c not in df.columns]
    for m in missing:
        df[m] = 0.0

    X = df[feature_cols].copy()

    preds = model.predict(X)

    df["Hardness"] = preds[:, 0]
    df["Dissolution_Rate"] = preds[:, 1]
    df["Content_Uniformity"] = preds[:, 2]
    
    # Scale Content_Uniformity from actual range (89.8-106.3%) to 80-100%
    # Formula: 80 + (uniformity - 89.8) * 20 / 16.5
    uniformity = preds[:, 2]
    df["Yield"] = 80.0 + (uniformity - 89.8) * (20.0 / 16.5)
    df["Yield"] = df["Yield"].clip(80, 100)  # Clamp to 80-100%
    
    # Scale performance_score from PCA range (-1.82 to +1.68) to percentage (0-100%)
    perf_raw = preds[:, 4]
    df["Performance"] = ((perf_raw + 1.82) / 3.5) * 100
    df["Performance"] = df["Performance"].clip(0, 100)  # Clamp to 0-100%
    
    df["Energy"] = preds[:, 5]

    df["Quality"] = (
        0.4 * df["Hardness"]
        + 0.3 * df["Dissolution_Rate"]
        + 0.3 * df["Content_Uniformity"]
    )

    df["CO2"] = df["Energy"] * CO2_FACTOR

    return df