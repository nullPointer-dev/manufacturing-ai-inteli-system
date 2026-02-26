import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# =========================================================
# LOAD DATA
# =========================================================
def load_data(data_folder=DATA_DIR):
    """Load production + all batch worksheets (ignore Summary sheet)."""

    data_path = Path(data_folder)

    production_df = pd.read_excel(data_path / "batch_production_data.xlsx")

    # Read ALL sheets
    sheets = pd.read_excel(
        data_path / "batch_process_data.xlsx",
        sheet_name=None
    )

    process_frames = []

    for sheet_name, sheet_df in sheets.items():

        # 🚫 skip summary sheet
        if sheet_name.lower() == "summary":
            continue

        # skip empty sheets
        if sheet_df.empty:
            continue

        df = sheet_df.copy()
        df["Batch_ID"] = sheet_name.replace("Batch_", "")
        process_frames.append(df)

    process_df = pd.concat(process_frames, ignore_index=True)

    production_df["Batch_ID"] = production_df["Batch_ID"].astype(str)
    process_df["Batch_ID"] = process_df["Batch_ID"].astype(str)

    print("Production rows:", len(production_df))
    print("Process rows:", len(process_df))
    print("Unique batches:", process_df["Batch_ID"].nunique())

    return production_df, process_df


# =========================================================
# AGGREGATE PROCESS DATA
# =========================================================
def aggregate_process_data(process_df):
    """Convert time-series → batch-level features."""

    df = process_df.copy()

    # 🔥 correct energy calculation
    df["row_energy_kwh"] = (
        df["Power_Consumption_kW"] * df["Time_Minutes"] / 60.0
    )

    # phase durations
    phase_duration = df.groupby(["Batch_ID", "Phase"]).size().reset_index(name="duration")
    phase_pivot = phase_duration.pivot(index="Batch_ID", columns="Phase", values="duration")
    phase_pivot.columns = [f"duration_{c.lower().replace(' ', '_')}" for c in phase_pivot.columns]
    phase_pivot = phase_pivot.reset_index()

    agg_features = df.groupby("Batch_ID").agg(
        avg_power_consumption=("Power_Consumption_kW", "mean"),
        max_power_consumption=("Power_Consumption_kW", "max"),
        total_energy=("row_energy_kwh", "sum"),   # ← REAL ENERGY
        avg_temperature=("Temperature_C", "mean"),
        max_temperature=("Temperature_C", "max"),
        avg_pressure=("Pressure_Bar", "mean"),
        avg_vibration=("Vibration_mm_s", "mean"),
        total_process_time=("Time_Minutes", "sum"),
        number_of_phases=("Phase", "nunique")
    ).reset_index()

    agg_features = agg_features.merge(phase_pivot, on="Batch_ID", how="left")

    return agg_features


# =========================================================
# MERGE
# =========================================================
def merge_datasets(production_df, agg_process_df):
    return production_df.merge(agg_process_df, on="Batch_ID", how="left")


# =========================================================
# CLEAN
# =========================================================
def clean_data(df):

    df = df.drop_duplicates(subset="Batch_ID", keep="first").copy()

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    df.fillna(0, inplace=True)

    return df


# =========================================================
# PIPELINE
# =========================================================
def build_pipeline(data_folder=DATA_DIR):

    production_df, process_df = load_data(data_folder)

    agg_process_df = aggregate_process_data(process_df)
    merged_df = merge_datasets(production_df, agg_process_df)
    final_df = clean_data(merged_df)

    from feature_engineering import engineer_features
    final_df = engineer_features(final_df)

    print("Final batches:", len(final_df))
    print(final_df["total_energy"].describe())

    return final_df


if __name__ == "__main__":
    df = build_pipeline()