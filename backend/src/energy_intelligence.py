import pandas as pd
import numpy as np

def compute_energy_intelligence(df):
    df = df.copy()

    # -----------------------------------------
    # BASIC DERIVED METRICS
    # -----------------------------------------
    df["energy_intensity"] = df["total_energy"] / (df["total_process_time"] + 1e-6)

    # rolling stats
    df["energy_roll_mean"] = df["total_energy"].rolling(10, min_periods=1).mean()
    df["energy_roll_std"] = df["total_energy"].rolling(10, min_periods=1).std().fillna(0)

    # drift from normal
    baseline = df["total_energy"].mean()
    df["energy_drift"] = (df["total_energy"] - baseline) / baseline

    # -----------------------------------------
    # Normalize energy for stability detection
    # -----------------------------------------
    df["energy_norm"] = (
        df["total_energy"] - df["total_energy"].mean()
    ) / (df["total_energy"].std() + 1e-6)

    # Rolling instability on normalized signal
    df["instability_score"] = (
        df["energy_norm"]
        .rolling(10, min_periods=1)
        .std()
        .fillna(0)
    )

    # -----------------------------------------
    # RELIABILITY FLAGS
    # -----------------------------------------
    states = []
    drift_threshold = df["energy_drift"].std() * 0.5
    instability_threshold = df["instability_score"].mean() + df["instability_score"].std()
    for _, row in df.iterrows():

        if row["energy_drift"] > drift_threshold:
            states.append("Efficiency Loss")

        elif row["instability_score"] > instability_threshold:
            states.append("Process Instability")

        elif row["energy_drift"] < -drift_threshold:
            states.append("Calibration Gain")

        else:
            states.append("Stable")

    df["reliability_state"] = states

    return df