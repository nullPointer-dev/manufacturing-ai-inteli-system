import pandas as pd

def reliability_filter(
    df,
    energy_col="Energy",
    threshold_std=2.5
):
    """
    Remove unstable candidates based on deviation
    from historical production energy distribution.
    """

    if energy_col not in df.columns:
        return df

    df = df.copy()

    try:
        from data_pipeline import build_pipeline
        hist_df = build_pipeline()

        hist_mean = hist_df["total_energy"].mean()
        hist_std = hist_df["total_energy"].std()

        if hist_std == 0:
            return df

        z_score = (df[energy_col] - hist_mean).abs() / hist_std

        filtered = df[z_score < threshold_std]

        # never return empty set
        if len(filtered) == 0:
            return df

        return filtered

    except:
        return df