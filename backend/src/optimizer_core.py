import numpy as np
import pandas as pd


# =========================================================
# PARETO FRONT COMPUTATION
# =========================================================
def compute_pareto_front(df):
    """
    Compute Pareto optimal solutions.

    Assumes:
    - Quality, Yield, Performance → maximize
    - Energy, CO2 → minimize
    """

    if df is None or len(df) == 0:
        return df

    df = df.copy().reset_index(drop=True)

    objectives = df[["Quality", "Yield", "Performance", "Energy", "CO2"]].values

    is_pareto = np.ones(len(objectives), dtype=bool)

    for i in range(len(objectives)):
        for j in range(len(objectives)):
            if i == j:
                continue

            better_or_equal = (
                objectives[j][0] >= objectives[i][0] and
                objectives[j][1] >= objectives[i][1] and
                objectives[j][2] >= objectives[i][2] and
                objectives[j][3] <= objectives[i][3] and
                objectives[j][4] <= objectives[i][4]
            )

            strictly_better = (
                objectives[j][0] > objectives[i][0] or
                objectives[j][1] > objectives[i][1] or
                objectives[j][2] > objectives[i][2] or
                objectives[j][3] < objectives[i][3] or
                objectives[j][4] < objectives[i][4]
            )

            if better_or_equal and strictly_better:
                is_pareto[i] = False
                break

    return df[is_pareto].reset_index(drop=True)