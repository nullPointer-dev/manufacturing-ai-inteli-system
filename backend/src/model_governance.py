import numpy as np

def detect_model_drift(df):
    if "anomaly_flag" in df.columns:
        anomaly_rate = df["anomaly_flag"].mean()
    else:
        anomaly_rate = 0.0

    if "energy_drift" in df.columns:
        energy_drift_mean = df["energy_drift"].abs().mean()
    elif "total_energy" in df.columns:
        baseline = df["total_energy"].mean() + 1e-6
        energy_drift = (df["total_energy"] - baseline) / baseline
        energy_drift_mean = energy_drift.abs().mean()
    else:
        energy_drift_mean = 0.0

    drift_flags = {
        "high_anomaly_rate": anomaly_rate > 0.15,
        "high_energy_drift": energy_drift_mean > 0.05
    }

    drift_detected = any(drift_flags.values())

    return drift_detected, drift_flags
