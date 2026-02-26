import pandas as pd
import numpy as np

from data_pipeline import build_pipeline
from context_engine import assign_context_clusters
from golden_signature import identify_golden_signatures, scenario_weights
from reliability_gate import reliability_filter
from core_fitness import compute_fitness
from batch_scorer import attach_predictions


# =========================================================
# INIT POPULATION FROM GOLDEN
# =========================================================
def initialize_population(pop_size, golden_ranges):

    if golden_ranges is None or len(golden_ranges) == 0:
        return pd.DataFrame()

    rows = []

    for _ in range(pop_size):
        r = {}
        for p, stats in golden_ranges.items():
            r[p] = np.random.uniform(stats["min"], stats["max"])
        rows.append(r)

    return pd.DataFrame(rows)


# =========================================================
# REALISM CLAMP
# =========================================================
def clamp_energy(pop_df, hist_df):

    if len(pop_df) == 0:
        return pop_df

    hist_energy = hist_df["Energy"].mean()

    lower = hist_energy * 0.90
    upper = hist_energy * 1.10

    pop_df["Energy"] = pop_df["Energy"].clip(lower, upper)
    pop_df["CO2"] = pop_df["Energy"] * 0.82

    return pop_df


# =========================================================
# CONSTRAINT FILTER
# =========================================================
def apply_constraints(df, constraints, baseline_co2):

    if constraints is None or len(df) == 0:
        return df

    df = df.copy()

    if constraints.get("min_quality") is not None:
        df = df[df["Quality"] >= constraints["min_quality"]]

    if constraints.get("min_yield") is not None:
        df = df[df["Yield"] >= constraints["min_yield"]]

    if constraints.get("min_performance") is not None:
        df = df[df["Performance"] >= constraints["min_performance"]]

    if constraints.get("min_reduction") is not None:
        reduction = (baseline_co2 - df["CO2"]) / baseline_co2 * 100
        df = df[reduction >= constraints["min_reduction"]]

    return df


# =========================================================
# MAIN OPTIMIZER
# =========================================================
def nsga2_optimize(
    pop_size=60,
    generations=20,
    mode="balanced",
    constraints=None,
    custom_weights=None
):
    """
    NSGA-II style multi-objective optimizer.
    Supports preset and custom weight scenarios.
    """

    # ------------------------------------------------------
    # CUSTOM MODE VALIDATION
    # ------------------------------------------------------
    if mode == "custom" and custom_weights is None:
        raise ValueError("custom_weights required for custom mode")

    # ------------------------------------------------------
    # HISTORICAL DATA
    # ------------------------------------------------------
    hist_df = build_pipeline()
    hist_df = attach_predictions(hist_df)
    hist_df, _ = assign_context_clusters(hist_df)

    if len(hist_df) == 0:
        return None

    current_cluster = hist_df["context_cluster"].mode()[0]
    baseline_co2 = hist_df["CO2"].mean()

    # ------------------------------------------------------
    # GOLDEN RANGES
    # ------------------------------------------------------
    _, golden_ranges, _ = identify_golden_signatures(
        hist_df,
        mode=mode,
        cluster_id=current_cluster,
        custom_weights=custom_weights
    )

    if golden_ranges is None or len(golden_ranges) == 0:
        return None

    population = initialize_population(pop_size, golden_ranges)

    if len(population) == 0:
        return None

    # ------------------------------------------------------
    # RESOLVE FITNESS WEIGHTS ONCE
    # ------------------------------------------------------
    weights = scenario_weights(mode, custom_weights)

    # ------------------------------------------------------
    # EVOLUTION LOOP
    # ------------------------------------------------------
    for _ in range(generations):

        population = attach_predictions(population)
        population = clamp_energy(population, hist_df)
        population = apply_constraints(population, constraints, baseline_co2)

        if len(population) < max(5, pop_size // 3):
            population = initialize_population(pop_size, golden_ranges)
            population = attach_predictions(population)

        if len(population) == 0:
            return None

        population["Score"] = compute_fitness(population, weights)

        population = (
            population
            .sort_values("Score", ascending=False)
            .head(pop_size)
            .reset_index(drop=True)
        )

    # ------------------------------------------------------
    # RELIABILITY FILTER
    # ------------------------------------------------------
    population = reliability_filter(population)

    if population is None or len(population) == 0:
        return None

    population = population.sort_values("Score", ascending=False)

    return population.head(20)