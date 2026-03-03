import pandas as pd
import numpy as np
import logging
from pathlib import Path

from data_pipeline import build_pipeline
from context_engine import assign_context_clusters
from optimizer_nsga2 import nsga2_optimize
from golden_updater import check_if_better
from batch_scorer import attach_predictions
from scenario_utils import normalize_weights, scenario_key_from_weights

logger = logging.getLogger(__name__)

_MODEL_DIR = Path(__file__).resolve().parent.parent / "models"


# =========================================================
# AUTO OPTIMIZER ENTRY
# =========================================================
def optimize_auto(
    mode="balanced",
    engine="nsga2",
    population_size=60,
    generations=20,
    custom_weights=None
):
    """
    Runs automatic optimization.

    Returns:
        results_df
        proposal_flag (bool)
        cluster_id
        scenario_key (only for custom mode)
    """

    scenario_key = None

    # ------------------------------------------------------
    # HANDLE CUSTOM MODE
    # ------------------------------------------------------
    if mode == "custom":
        if custom_weights is None:
            raise ValueError("custom_weights must be provided for custom mode")

        custom_weights = normalize_weights(custom_weights)
        scenario_key = scenario_key_from_weights(custom_weights)

    # ------------------------------------------------------
    # RUN OPTIMIZER
    # ------------------------------------------------------
    if engine == "nsga2":
        results = nsga2_optimize(
            pop_size=population_size,
            generations=generations,
            mode=mode,
            custom_weights=custom_weights
        )
    else:
        raise ValueError("Unknown optimizer engine")

    if results is None or len(results) == 0:
        return None, False, None, scenario_key

    results = results.reset_index(drop=True)
    best_row = results.iloc[0]

    # ------------------------------------------------------
    # DETERMINE CONTEXT CLUSTER
    # Use the persisted KMeans model to avoid a redundant
    # build_pipeline() + attach_predictions() round-trip.
    # Falls back to a single pipeline call only when the
    # persisted model is not yet available.
    # ------------------------------------------------------
    CLUSTER_FILE = _MODEL_DIR / "context_cluster.pkl"
    SCALER_FILE  = _MODEL_DIR / "context_scaler.pkl"
    CONTEXT_FEATURES = ["Batch_Size", "Machine_Speed", "Compression_Force",
                        "avg_temperature", "avg_pressure"]

    current_cluster = 1  # safe default
    try:
        import joblib
        if CLUSTER_FILE.exists() and SCALER_FILE.exists():
            hist_df = build_pipeline()   # uses cache — effectively free
            scaler = joblib.load(SCALER_FILE)
            kmeans = joblib.load(CLUSTER_FILE)
            avail = [f for f in CONTEXT_FEATURES if f in hist_df.columns]
            if len(avail) >= 2:
                X = hist_df[avail].fillna(hist_df[avail].median())
                X_scaled = scaler.transform(X)
                clusters = kmeans.predict(X_scaled)
                vals, counts = np.unique(clusters, return_counts=True)
                current_cluster = int(vals[counts.argmax()])
        else:
            hist_df = build_pipeline()
            hist_df = attach_predictions(hist_df)
            hist_df, _ = assign_context_clusters(hist_df)
            current_cluster = int(hist_df["context_cluster"].mode()[0])
    except Exception:
        logger.warning("Could not determine context cluster; using default %d", current_cluster)

    # ------------------------------------------------------
    # CHECK AGAINST GOLDEN
    # ------------------------------------------------------
    proposal = check_if_better(
        best_row,
        mode,
        current_cluster,
        scenario_key=scenario_key
    )

    return results, proposal, current_cluster, scenario_key