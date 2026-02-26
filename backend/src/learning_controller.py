from pathlib import Path
import joblib
import json
from datetime import datetime

from data_pipeline import build_pipeline
from energy_intelligence import compute_energy_intelligence
from anomaly_detection import detect_anomalies
from model_governance import detect_model_drift
from train_model import train_and_save_model

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
VERSION_LOG = MODEL_DIR / "model_versions.json"


# =========================================================
# MAIN RETRAIN CONTROLLER
# =========================================================
def check_and_retrain(cooldown_hours=6):
    """
    Checks for drift and retrains model if required.
    Logs metrics + governance history.
    """

    # -----------------------------
    # Build latest dataset
    # -----------------------------
    df = build_pipeline()
    df = compute_energy_intelligence(df)
    df = detect_anomalies(df)

    drift_detected, flags = detect_model_drift(df)

    if not drift_detected:
        return False, flags

    now = datetime.now()

    # -----------------------------
    # Load version history safely
    # -----------------------------
    if VERSION_LOG.exists():
        try:
            with open(VERSION_LOG, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    else:
        history = []

    # -----------------------------
    # Cooldown check
    # -----------------------------
    if history:
        last_time = datetime.fromisoformat(history[-1]["time"])
        hours_since = (now - last_time).total_seconds() / 3600

        if hours_since < cooldown_hours:
            return False, {"cooldown_active": True}

    # -----------------------------
    # Retrain model
    # train_and_save_model must return (model, metrics)
    # -----------------------------
    model, metrics = train_and_save_model()

    # ensure flags are json-safe
    clean_flags = {k: bool(v) for k, v in flags.items()}

    # -----------------------------
    # Create governance entry
    # -----------------------------
    entry = {
        "time": now.isoformat(),
        "reason": clean_flags,
        "metrics": {
            "mae": float(metrics.get("mae", 0)),
            "rmse": float(metrics.get("rmse", 0)),
            "mape": float(metrics.get("mape", 0)),
        },
        "dataset_size": int(len(df)),
        "model_version": len(history) + 1
    }

    history.append(entry)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with open(VERSION_LOG, "w") as f:
        json.dump(history, f, indent=2)

    return True, clean_flags