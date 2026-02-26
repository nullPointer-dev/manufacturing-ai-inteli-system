import pandas as pd
import numpy as np

from data_pipeline import build_pipeline
from context_engine import assign_context_clusters
from optimizer_nsga2 import nsga2_optimize
from golden_updater import check_if_better
from batch_scorer import attach_predictions
from scenario_utils import normalize_weights, scenario_key_from_weights


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
    # ------------------------------------------------------
    hist_df = build_pipeline()
    hist_df = attach_predictions(hist_df)
    hist_df, _ = assign_context_clusters(hist_df)

    current_cluster = hist_df["context_cluster"].mode()[0]

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