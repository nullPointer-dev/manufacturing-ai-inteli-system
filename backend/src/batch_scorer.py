import logging
from pathlib import Path
import json
import joblib
import pandas as pd

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

from constants import CO2_FACTOR

# =========================================================
# MODULE-LEVEL MODEL CACHE (invalidated by file mtime)
# =========================================================
_model_cache: dict = {"model": None, "feature_cols": None, "mtime": None}
_scaling_cache: dict = {"params": None, "mtime": None}

_SCALING_FILE = MODEL_DIR / "scaling_params.json"


def _get_model():
    model_path = MODEL_DIR / "model.pkl"
    cols_path = MODEL_DIR / "feature_columns.pkl"
    try:
        mtime = model_path.stat().st_mtime
    except OSError:
        mtime = None

    if _model_cache["model"] is None or _model_cache["mtime"] != mtime:
        if not model_path.exists() or not cols_path.exists():
            return None, None
        _model_cache["model"] = joblib.load(model_path)
        _model_cache["feature_cols"] = joblib.load(cols_path)
        _model_cache["mtime"] = mtime
        logger.debug("batch_scorer: model loaded from disk")

    return _model_cache["model"], _model_cache["feature_cols"]


def _get_scaling_params() -> dict:
    try:
        mtime = _SCALING_FILE.stat().st_mtime
    except OSError:
        mtime = None

    if _scaling_cache["params"] is None or _scaling_cache["mtime"] != mtime:
        if _SCALING_FILE.exists():
            with open(_SCALING_FILE) as f:
                _scaling_cache["params"] = json.load(f)
        else:
            _scaling_cache["params"] = {
                "content_uniformity_min": 89.8,
                "yield_scale_range": 16.5,
                "performance_score_min": -1.82,
                "perf_scale_range": 3.5,
            }
        _scaling_cache["mtime"] = mtime

    return _scaling_cache["params"]


def attach_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attach model predictions and derived KPIs to dataframe.

    Guarantees presence of:
    Quality, Yield, Performance, Energy, CO2
    """

    df = df.copy()

    model, feature_cols = _get_model()

    if model is None or feature_cols is None:
        # model not trained yet → return safe defaults
        for col in ["Quality", "Yield", "Performance", "Energy", "CO2"]:
            if col not in df.columns:
                df[col] = 0.0
        return df

    # ensure required feature columns exist
    missing = [c for c in feature_cols if c not in df.columns]
    for m in missing:
        df[m] = 0.0

    X = df[feature_cols].copy()

    preds = model.predict(X)

    df["Hardness"] = preds[:, 0]
    df["Dissolution_Rate"] = preds[:, 1]
    df["Content_Uniformity"] = preds[:, 2]

    # Dynamic rescaling — use params saved at training time
    sp = _get_scaling_params()
    cu_min = sp["content_uniformity_min"]
    cu_range = sp["yield_scale_range"]
    df["Yield"] = 80.0 + (preds[:, 2] - cu_min) * (20.0 / cu_range)
    df["Yield"] = df["Yield"].clip(80, 100)

    ps_min = sp["performance_score_min"]
    ps_range = sp["perf_scale_range"]
    df["Performance"] = ((preds[:, 4] - ps_min) / ps_range) * 100
    df["Performance"] = df["Performance"].clip(0, 100)

    df["Energy"] = preds[:, 5]

    df["Quality"] = (
        0.4 * df["Hardness"]
        + 0.3 * df["Dissolution_Rate"]
        + 0.3 * df["Content_Uniformity"]
    )

    df["CO2"] = df["Energy"] * CO2_FACTOR

    return df