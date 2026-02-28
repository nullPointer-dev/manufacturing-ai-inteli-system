import pandas as pd
import numpy as np


# =========================================================
# ASSET CAUSE DIAGNOSIS
# =========================================================
_ASSET_PARAM_MAP = {
    # (column_to_check, quantile_threshold, cause_label, action_label)
    "Efficiency Loss": [
        ("equipment_load",        0.80, "High equipment load",           "Inspect motor windings / lubrication"),
        ("avg_temperature",       0.85, "Elevated temperature",          "Check cooling system / heat exchangers"),
        ("avg_pressure",          0.85, "Excess process pressure",       "Review compression force calibration"),
        ("avg_power_consumption", 0.80, "Abnormal power draw",           "Audit power distribution & motor health"),
    ],
    "Process Instability": [
        ("Moisture_Content",  0.80, "High moisture in feed",          "Adjust drying parameters / check raw material"),
        ("Machine_Speed",     0.85, "Machine speed variance",         "Recalibrate speed controller"),
        ("avg_vibration",     0.85, "Elevated vibration",             "Check bearing alignment & balance"),
        ("Compression_Force", 0.85, "Excess compression force",       "Inspect punch tooling & die set"),
    ],
    "Calibration Gain": [
        ("avg_power_consumption", 0.20, "Below-baseline power draw",    "Verify output quality - possible under-processing"),
        ("Machine_Speed",         0.20, "Below-normal machine speed",   "Confirm throughput targets are met"),
    ],
    "Stable": [],
}


def _diagnose_asset_cause(df):
    """
    For each row determine which asset parameters are outside normal bounds
    and return cause + maintenance action labels.
    """
    # Pre-compute per-column quantile thresholds
    thresholds = {}
    for state_rules in _ASSET_PARAM_MAP.values():
        for col, q, *_ in state_rules:
            if col in df.columns and (col, q) not in thresholds:
                thresholds[(col, q)] = float(df[col].quantile(q))

    causes = []
    actions = []

    for _, row in df.iterrows():
        state = row.get("reliability_state", "Stable")
        rules = _ASSET_PARAM_MAP.get(state, [])

        batch_causes = []
        batch_actions = []
        for col, q, cause, action in rules:
            if col not in df.columns:
                continue
            threshold = thresholds.get((col, q))
            if threshold is None:
                continue
            value = row.get(col, None)
            if value is None:
                continue
            # High-end checks q >= 0.5; low-end checks q < 0.5
            if q >= 0.5 and float(value) > threshold:
                batch_causes.append(cause)
                batch_actions.append(action)
            elif q < 0.5 and float(value) < threshold:
                batch_causes.append(cause)
                batch_actions.append(action)

        causes.append(" | ".join(batch_causes) if batch_causes else "Normal operation")
        actions.append(" | ".join(batch_actions) if batch_actions else "No action required")

    return causes, actions


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
    # Use percentile-based thresholds so states are distributed across the
    # population rather than all collapsing into one bucket.
    #   Top 20% positive drift  -> Efficiency Loss (overconsumption)
    #   Bottom 20% (negative)   -> Calibration Gain (underconsumption)
    #   Top 15% instability     -> Process Instability (erratic behaviour)
    #   Everything else         -> Stable
    states = []
    eff_loss_threshold  = float(df["energy_drift"].quantile(0.80))   # top 20%
    cal_gain_threshold  = float(df["energy_drift"].quantile(0.20))   # bottom 20%
    instability_threshold = float(df["instability_score"].quantile(0.85))  # top 15%

    for _, row in df.iterrows():
        if row["instability_score"] > instability_threshold:
            states.append("Process Instability")
        elif row["energy_drift"] > eff_loss_threshold:
            states.append("Efficiency Loss")
        elif row["energy_drift"] < cal_gain_threshold:
            states.append("Calibration Gain")
        else:
            states.append("Stable")

    df["reliability_state"] = states

    # -----------------------------------------
    # ASSET CAUSE ATTRIBUTION
    # -----------------------------------------
    causes, actions = _diagnose_asset_cause(df)
    df["asset_cause"] = causes
    df["maintenance_action"] = actions

    return df