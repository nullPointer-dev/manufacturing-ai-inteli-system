from optimizer_nsga2 import nsga2_optimize
from reliability_gate import reliability_filter
from core_fitness import compute_fitness
from golden_signature import scenario_weights


# =========================================================
# TARGET-BASED OPTIMIZER
# =========================================================
def optimize_target(
    required_reduction=None,
    min_quality=None,
    min_yield=None,
    min_performance=None,
    mode="balanced",
    pop_size=60,
    generations=20
):

    # ---------------------------------------------
    # Build constraints dictionary
    # ---------------------------------------------
    constraints = {
        "min_quality": min_quality,
        "min_yield": min_yield,
        "min_performance": min_performance,
        "min_reduction": required_reduction
    }

    # ---------------------------------------------
    # Run unified NSGA-II optimizer
    # ---------------------------------------------
    results = nsga2_optimize(
        pop_size=pop_size,
        generations=generations,
        mode=mode,
        constraints=constraints
    )

    if results is None or len(results) == 0:
        return None

    # ---------------------------------------------
    # Reliability filter (hard gate)
    # ---------------------------------------------
    results = reliability_filter(results)

    if len(results) == 0:
        return None

    # ---------------------------------------------
    # Compute Score using scenario weights
    # ---------------------------------------------
    weights = scenario_weights(mode)
    results["Score"] = compute_fitness(results, weights)

    results = results.sort_values("Score", ascending=False)

    return results.head(15).reset_index(drop=True)