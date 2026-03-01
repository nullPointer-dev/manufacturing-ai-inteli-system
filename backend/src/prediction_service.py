import joblib
import pandas as pd
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_FILE = MODEL_DIR / "model.pkl"
FEATURE_FILE = MODEL_DIR / "feature_columns.pkl"

CO2_FACTOR = 0.82


# =========================================================
# LOAD MODEL + FEATURES
# =========================================================
def _load_model():
    model = joblib.load(MODEL_FILE)
    feature_cols = joblib.load(FEATURE_FILE)
    return model, feature_cols


# =========================================================
# REAL-TIME BATCH PREDICTION
# =========================================================
def predict_batch(input_params: dict):
    """
    Predict full KPI set for a new batch.
    Returns:
    Quality, Yield, Performance, Energy, CO2
    + raw chemistry metrics
    
    Handles missing features by providing reasonable defaults.
    """

    model, feature_cols = _load_model()

    df = pd.DataFrame([input_params])
    
    # Fill missing features with reasonable defaults
    defaults = {
        # Production parameters
        'Granulation_Time': 30.0,
        'Binder_Amount': 10.0,
        'Drying_Temp': 60.0,
        'Drying_Time': 120.0,
        'Lubricant_Conc': 1.0,
        'Moisture_Content': 2.0,
        
        # Process metrics
        'max_power_consumption': df.get('avg_power_consumption', [60.0])[0] * 1.5 if 'avg_power_consumption' in df.columns else 60.0,
        'max_temperature': df.get('avg_temperature', [30.0])[0] * 1.2 if 'avg_temperature' in df.columns else 30.0,
        'avg_vibration': 0.5,
        'number_of_phases': 8.0,
        
        # Phase durations (minutes)
        'duration_blending': 15.0,
        'duration_coating': 30.0,
        'duration_compression': 45.0,
        'duration_drying': 120.0,
        'duration_granulation': 30.0,
        'duration_milling': 20.0,
        'duration_preparation': 10.0,
        'duration_quality_testing': 15.0,
        
        # Engineered features (computed from inputs where possible)
        'energy_per_tablet': (df.get('total_process_time', [120.0])[0] * df.get('avg_power_consumption', [50.0])[0] / 60.0) / df.get('Tablet_Weight', [500.0])[0] if 'Tablet_Weight' in df.columns and df.get('Tablet_Weight', [500.0])[0] != 0 else 0.3,
        'process_efficiency': 0.5,
        'quality_score': 70.0,
        'stability_index': 0.15,
        'temperature_pressure_ratio': df.get('avg_temperature', [25.0])[0] / df.get('avg_pressure', [1.5])[0] if 'avg_pressure' in df.columns and df.get('avg_pressure', [1.5])[0] != 0 else 16.7,
        'energy_efficiency_score': 0.0,
        'process_intensity': df.get('total_process_time', [120.0])[0] * df.get('avg_power_consumption', [50.0])[0] if 'total_process_time' in df.columns and 'avg_power_consumption' in df.columns else 6000.0,
        'equipment_load': df.get('Machine_Speed', [50.0])[0] * df.get('Compression_Force', [15.0])[0] if 'Machine_Speed' in df.columns and 'Compression_Force' in df.columns else 750.0,
        
        # Z-scores (neutral defaults)
        'Hardness_zscore': 0.0,
        'Dissolution_Rate_zscore': 0.0,
        'Content_Uniformity_zscore': 0.0,
        'total_energy_zscore': 0.0,
    }
    
    # Fill missing columns with defaults
    for col in feature_cols:
        if col not in df.columns:
            if col in defaults:
                df[col] = defaults[col]
            else:
                df[col] = 0.0  # fallback for any unexpected features

    df = df[feature_cols]

    preds = model.predict(df)[0]

    hardness = float(preds[0])
    dissolution = float(preds[1])
    uniformity = float(preds[2])
    yield_val = float(preds[3])
    perf_val = float(preds[4])
    energy = float(preds[5])

    # Scale Content_Uniformity from actual range (89.8-106.3%) to 80-100%
    # Formula: 80 + (uniformity - 89.8) * 20 / 16.5
    yield_scaled = 80.0 + (uniformity - 89.8) * (20.0 / 16.5)
    yield_scaled = max(80.0, min(100.0, yield_scaled))  # Clamp to 80-100%

    # Scale performance_score from PCA range (-1.82 to +1.68) to percentage (0-100%)
    perf_scaled = ((perf_val + 1.82) / 3.5) * 100
    perf_scaled = max(0.0, min(100.0, perf_scaled))  # Clamp to 0-100%

    quality = (
        0.4 * hardness
        + 0.3 * dissolution
        + 0.3 * uniformity
    )

    co2 = energy * CO2_FACTOR

    return {
        # raw model outputs
        "Hardness": hardness,
        "Dissolution_Rate": dissolution,
        "Content_Uniformity": uniformity,

        # system KPIs
        "Quality": quality,
        "Yield": yield_scaled,  # Scaled Content_Uniformity (89.8-106.3% → 80-100%)
        "Performance": perf_scaled,  # Scaled performance_score (-1.82 to +1.68 → 0-100%)
        "Energy": energy,
        "CO2": co2
    }