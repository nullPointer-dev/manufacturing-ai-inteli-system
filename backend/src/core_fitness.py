import numpy as np
import pandas as pd

def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

def compute_reliability_penalty(df):
    if "Energy" not in df.columns:
        return 0
    
    mean_energy = df["Energy"].mean()
    deviation = (df["Energy"] - mean_energy).abs()
    penalty = deviation / (mean_energy + 1e-9)
    return penalty

def compute_fitness(
    df,
    weights,
    include_reliability=False
):
    df = df.copy()

    q = normalize(df["Quality"])
    y = normalize(df["Yield"])
    p = normalize(df["Performance"])
    e = normalize(df["Energy"])
    c = normalize(df["CO2"])

    fitness = (
        weights["quality"] * q
        + weights["yield"] * y
        + weights["performance"] * p
        - weights["energy"] * e
        - weights["co2"] * c
    )

    if include_reliability and "instability_score" in df.columns:
        r = normalize(df["instability_score"])
        fitness -= weights.get("reliability", 0.1) * r

    if include_reliability:
        penalty = compute_reliability_penalty(df)
        fitness -= weights.get("reliability", 0.05) * penalty

    return fitness