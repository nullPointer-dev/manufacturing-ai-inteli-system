import logging
import pandas as pd
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# =========================================================
# MODULE-LEVEL PIPELINE CACHE (invalidated on file mtime change)
# =========================================================
_pipeline_cache: dict = {
    "df": None,
    "mtime_production": None,
    "mtime_process": None,
}


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

    logger.debug("Production rows: %d", len(production_df))
    logger.debug("Process rows: %d", len(process_df))
    logger.debug("Unique batches: %d", process_df["Batch_ID"].nunique())

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
    data_path = Path(data_folder)
    prod_file = data_path / "batch_production_data.xlsx"
    proc_file = data_path / "batch_process_data.xlsx"

    # --- cache invalidation by file modification time ---
    try:
        mtime_prod = prod_file.stat().st_mtime if prod_file.exists() else None
        mtime_proc = proc_file.stat().st_mtime if proc_file.exists() else None
    except OSError:
        mtime_prod = mtime_proc = None

    cache = _pipeline_cache
    if (
        cache["df"] is not None
        and cache["mtime_production"] == mtime_prod
        and cache["mtime_process"] == mtime_proc
        and data_folder == DATA_DIR          # only cache the default path
    ):
        return cache["df"]

    production_df, process_df = load_data(data_folder)

    agg_process_df = aggregate_process_data(process_df)
    merged_df = merge_datasets(production_df, agg_process_df)
    final_df = clean_data(merged_df)

    from feature_engineering import engineer_features
    final_df = engineer_features(final_df)

    logger.debug("Final batches: %d", len(final_df))
    logger.debug("total_energy stats: min=%.2f max=%.2f mean=%.2f",
                 final_df["total_energy"].min(),
                 final_df["total_energy"].max(),
                 final_df["total_energy"].mean())

    # store in cache
    if data_folder == DATA_DIR:
        cache["df"] = final_df
        cache["mtime_production"] = mtime_prod
        cache["mtime_process"] = mtime_proc

    return final_df


def invalidate_pipeline_cache():
    """Call this after new data files are uploaded so the next call rebuilds."""
    _pipeline_cache["df"] = None
    _pipeline_cache["mtime_production"] = None
    _pipeline_cache["mtime_process"] = None


# =========================================================
# FILE CLASSIFICATION
# =========================================================
def classify_excel_file(file_path: Path) -> str:
    """
    Classify an Excel file as either 'production' or 'process' based on its structure.

    Process files have:
    - Multiple sheets (one per batch, named like "Batch_*")
    - Columns: Time_Minutes, Phase, Temperature_C, etc.

    Production files have:
    - Single sheet (or fewer sheets)
    - Columns: Granulation_Time, Binder_Amount, Drying_Temp, etc.

    Returns 'production' or 'process'.
    Raises Exception if the file cannot be read.
    """
    try:
        with pd.ExcelFile(file_path) as xl_file:
            sheet_names = xl_file.sheet_names

            if len(sheet_names) > 3:
                batch_sheets = [
                    s for s in sheet_names
                    if s.startswith("Batch_") or "batch" in s.lower()
                ]
                if len(batch_sheets) > 2:
                    return "process"

            first_sheet = pd.read_excel(xl_file, sheet_name=0)
            columns = set(first_sheet.columns)

        process_indicators = {"Time_Minutes", "Phase", "Temperature_C", "Pressure_Bar", "Power_Consumption_kW"}
        production_indicators = {"Granulation_Time", "Binder_Amount", "Drying_Temp", "Compression_Force", "Machine_Speed"}

        process_matches = len(process_indicators.intersection(columns))
        production_matches = len(production_indicators.intersection(columns))

        if process_matches > production_matches:
            return "process"
        if production_matches > process_matches:
            return "production"

        return "process" if len(sheet_names) > 1 else "production"

    except Exception as exc:
        raise Exception(f"Failed to classify file {file_path}: {exc}") from exc


if __name__ == "__main__":
    df = build_pipeline()