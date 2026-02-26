import pandas as pd
import numpy as np


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add engineered features for optimization + anomaly detection.
    """

    df = df.copy()

    # =========================
    # Basic engineered features
    # =========================

    df["energy_per_tablet"] = np.where(
        df["Tablet_Weight"] != 0,
        df["total_energy"] / df["Tablet_Weight"],
        0
    )

    df["process_efficiency"] = np.where(
        df["total_energy"] != 0,
        df["Hardness"] / df["total_energy"],
        0
    )

    df["quality_score"] = (
        0.4 * df["Hardness"]
        + 0.3 * df["Content_Uniformity"]
        + 0.3 * df["Dissolution_Rate"]
    )

    denom = df["Friability"] + df["Disintegration_Time"]
    df["stability_index"] = np.where(denom != 0, 1 / denom, 0)

    df["temperature_pressure_ratio"] = np.where(
        df["avg_pressure"] != 0,
        df["avg_temperature"] / df["avg_pressure"],
        0
    )

    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    # =========================
    # LEARNED YIELD SCORE
    # =========================

    yield_features = df[
        ["Hardness", "Content_Uniformity", "Friability"]
    ].copy()

    yield_features = yield_features.fillna(yield_features.mean())

    scaler = StandardScaler()
    yield_scaled = scaler.fit_transform(yield_features)

    pca_yield = PCA(n_components=1)
    df["yield_score"] = pca_yield.fit_transform(yield_scaled)


    # =========================
    # LEARNED PERFORMANCE SCORE
    # =========================

    perf_features = df[
        ["total_process_time", "avg_power_consumption"]
    ].copy()

    perf_features = perf_features.fillna(perf_features.mean())

    perf_scaled = scaler.fit_transform(perf_features)

    pca_perf = PCA(n_components=1)
    df["performance_score"] = -pca_perf.fit_transform(perf_scaled)

    # =========================
    # Advanced industrial KPIs
    # =========================

    # energy efficiency relative to mean
    mean_energy = df["total_energy"].mean()
    df["energy_efficiency_score"] = (mean_energy - df["total_energy"]) / mean_energy

    # process intensity
    df["process_intensity"] = (
        df["avg_power_consumption"] * df["total_process_time"]
    )

    # equipment load proxy
    df["equipment_load"] = (
        df["Machine_Speed"] * df["Compression_Force"]
    )

    # =========================
    # Z-score features for anomaly detection
    # =========================

    for col in ["Hardness", "Dissolution_Rate", "Content_Uniformity", "total_energy"]:
        df[f"{col}_zscore"] = (df[col] - df[col].mean()) / df[col].std()

    return df