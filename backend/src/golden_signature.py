import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from core_fitness import compute_fitness
from batch_scorer import attach_predictions


# =========================================================
# SCENARIO WEIGHTS
# =========================================================
def scenario_weights(mode, custom_weights=None):
    if mode == "custom":
        return custom_weights

    if mode == "eco":
        return {"quality":0.2,"yield":0.2,"performance":0.1,"energy":0.4,"co2":0.1}
    elif mode == "quality":
        return {"quality":0.5,"yield":0.2,"performance":0.2,"energy":0.05,"co2":0.05}
    elif mode == "balanced":
        return {"quality":0.3,"yield":0.3,"performance":0.2,"energy":0.1,"co2":0.1}
    elif mode == "yield":
        return {"quality":0.2,"yield":0.5,"performance":0.2,"energy":0.05,"co2":0.05}
    elif mode == "performance":
        return {"quality":0.2,"yield":0.2,"performance":0.5,"energy":0.05,"co2":0.05}
    else:
        return {"quality":0.3,"yield":0.3,"performance":0.2,"energy":0.1,"co2":0.1}


# =========================================================
# SELECT TOP PERFORMERS
# =========================================================
def _select_top_batches(df, top_frac=0.25, mode="balanced", custom_weights=None):
    df = df.copy()
    weights = scenario_weights(mode, custom_weights) 

    df["gold_score"] = compute_fitness(df, weights)

    if len(df) < 10:
        return df

    top_n = max(5, int(len(df) * top_frac))
    return df.sort_values("gold_score", ascending=False).head(top_n)


# =========================================================
# CLUSTER GOLDEN (STABLE)
# =========================================================
def _cluster_golden(df, feature_cols):
    if len(df) < 5:
        return df

    X = df[feature_cols].fillna(df[feature_cols].median())

    kmeans = KMeans(
        n_clusters=2,
        random_state=42,
        n_init=10
    )

    df["cluster"] = kmeans.fit_predict(X)

    best_cluster = (
        df.groupby("cluster")["gold_score"]
        .mean()
        .idxmax()
    )

    return df[df["cluster"] == best_cluster]


# =========================================================
# BUILD PARAMETER RANGES
# =========================================================
def _compute_ranges(df, feature_cols):
    ranges = {}

    for col in feature_cols:
        series = df[col]

        std_val = series.std()
        if std_val == 0 or np.isnan(std_val):
            std_val = abs(series.mean()) * 0.05

        ranges[col] = {
            "mean": float(series.mean()),
            "min": float(series.min()),
            "max": float(series.max()),
            "std": float(std_val),
        }

    return ranges


# =========================================================
# BEST HISTORICAL ROW
# =========================================================
def _best_historical_row(df):
    return df.sort_values("gold_score", ascending=False).iloc[0]


# =========================================================
# BLEND HIST + OPTIMIZER
# =========================================================
def _blend_rows(hist_row, opt_row, feature_cols, w_hist=0.7, w_opt=0.3):
    if opt_row is None:
        return hist_row[feature_cols].to_dict()

    final = {}

    for col in feature_cols:
        h = hist_row[col]
        o = opt_row.get(col, h)

        final[col] = float(w_hist * h + w_opt * o)

    return final


# =========================================================
# MAIN ENTRY
# =========================================================
def identify_golden_signatures(df, optimizer_best=None, mode="balanced", cluster_id=None, custom_weights=None):

    df = attach_predictions(df)

    # ensure required KPI columns exist
    required = ["Quality","Yield","Performance","Energy","CO2"]
    for col in required:
        if col not in df.columns:
            df[col] = 0.0

    # filter by context cluster if provided
    if cluster_id is not None and "context_cluster" in df.columns:
        filtered = df[df["context_cluster"] == cluster_id]
        if len(filtered) > 10:
            df = filtered

    # columns NOT used for optimization
    NON_DECISION_COLS = [
        "Batch_ID",
        "Quality","Yield","Performance","Energy","CO2",
        "gold_score",
        "cluster",
        "anomaly_flag",
        "risk_level",
        "instability_score",
        "energy_drift",
        "reliability_state",
        "context_cluster"
    ]

    feature_cols = [c for c in df.columns if c not in NON_DECISION_COLS]

    # select top batches
    top_df = _select_top_batches(df, mode=mode, custom_weights=custom_weights)

    # cluster best region
    golden_cluster_df = _cluster_golden(top_df, feature_cols)

    # compute ranges
    golden_ranges = _compute_ranges(golden_cluster_df, feature_cols)

    # best historical row
    hist_best = _best_historical_row(golden_cluster_df)

    # blend with optimizer best
    literal_golden = _blend_rows(
        hist_best,
        optimizer_best,
        feature_cols
    )

    golden_batches = (
        golden_cluster_df["Batch_ID"].tolist()
        if "Batch_ID" in golden_cluster_df.columns
        else []
    )

    return golden_batches, golden_ranges, literal_golden