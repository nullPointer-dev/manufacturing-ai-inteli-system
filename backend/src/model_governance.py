import numpy as np
import json
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
DRIFT_BASELINE_FILE = MODEL_DIR / "drift_baseline.json"

# Thresholds for drift
_ANOMALY_RATE_THRESHOLD = 0.15   # >15% anomaly rate
_ENERGY_SHIFT_THRESHOLD = 0.10   # >10% shift in mean total_energy vs baseline


def _load_baseline():
    """Load saved training baseline, or return None if not found."""
    if DRIFT_BASELINE_FILE.exists():
        try:
            with open(DRIFT_BASELINE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def detect_model_drift(df):
    """
    Compare current data statistics against the baseline saved at last training.
    If no baseline exists, save one now and report no drift (first-run).
    """
    baseline = _load_baseline()

    current_anomaly_rate = float(df["anomaly_flag"].mean()) if "anomaly_flag" in df.columns else 0.0
    current_energy_mean = float(df["total_energy"].mean()) if "total_energy" in df.columns else 0.0

    if baseline is None:
        # No prior baseline — save current stats and report no drift
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(DRIFT_BASELINE_FILE, "w") as f:
            json.dump({
                "energy_mean": current_energy_mean,
                "energy_std": float(df["total_energy"].std()) if "total_energy" in df.columns else 0.0,
                "anomaly_rate": current_anomaly_rate,
                "n_samples": int(len(df)),
            }, f, indent=2)
        return False, {"high_anomaly_rate": False, "high_energy_drift": False}

    # Relative shift in energy mean vs training baseline
    ref_mean = baseline.get("energy_mean", current_energy_mean) or current_energy_mean
    energy_shift = abs(current_energy_mean - ref_mean) / (abs(ref_mean) + 1e-6)

    drift_flags = {
        "high_anomaly_rate": current_anomaly_rate > _ANOMALY_RATE_THRESHOLD,
        "high_energy_drift": energy_shift > _ENERGY_SHIFT_THRESHOLD,
    }

    drift_detected = any(drift_flags.values())
    return drift_detected, drift_flags
