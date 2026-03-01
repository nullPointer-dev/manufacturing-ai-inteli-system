"""
Test script to check Performance values with default industrial validation parameters
"""
import sys
sys.path.append('backend/src')

from prediction_service import predict_batch

# Default batch parameters from industrial_validation.py
default_params = {
    'Machine_Speed': 50.0,
    'Compression_Force': 15.0,
    'Tablet_Weight': 500.0,
    'avg_temperature': 25.0,
    'avg_pressure': 1.5,
    'avg_power_consumption': 45.0,
    'total_process_time': 90.0,
    'Granulation_Time': 25.0,
    'Binder_Amount': 10.0,
    'Drying_Temp': 60.0,
    'Drying_Time': 90.0,
    'Lubricant_Conc': 1.0,
    'Moisture_Content': 2.0,
}

print("=" * 80)
print("TESTING DEFAULT INDUSTRIAL VALIDATION PARAMETERS")
print("=" * 80)

prediction = predict_batch(default_params)

print("\nPrediction Results:")
print(f"  Quality: {prediction['Quality']:.2f}")
print(f"  Yield: {prediction['Yield']:.2f}%")
print(f"  Performance: {prediction['Performance']:.2f}%")
print(f"  Energy: {prediction['Energy']:.2f} kWh")
print(f"  CO2: {prediction['CO2']:.2f} kg")

print("\nRaw model outputs:")
print(f"  Hardness: {prediction['Hardness']:.2f}")
print(f"  Dissolution_Rate: {prediction['Dissolution_Rate']:.2f}")
print(f"  Content_Uniformity: {prediction['Content_Uniformity']:.2f}")

# Check if we need to load the raw model to see the PCA score
print("\n" + "=" * 80)
print("CHECKING RAW PCA SCORES")
print("=" * 80)

from prediction_service import _load_model
import pandas as pd

model, feature_cols = _load_model()

# Create dataframe with default values
df = pd.DataFrame([default_params])

# Add missing features with 0
for col in feature_cols:
    if col not in df.columns:
        df[col] = 0.0

df = df[feature_cols]

preds = model.predict(df)[0]

print(f"\nRaw model predictions:")
print(f"  [0] Hardness: {preds[0]:.4f}")
print(f"  [1] Dissolution_Rate: {preds[1]:.4f}")
print(f"  [2] Content_Uniformity: {preds[2]:.4f}")
print(f"  [3] yield_score (PCA): {preds[3]:.4f}")
print(f"  [4] performance_score (PCA): {preds[4]:.4f}")
print(f"  [5] Energy: {preds[5]:.4f}")

# Test scaling formulas
yield_raw = preds[3]
yield_scaled = ((yield_raw + 4.33) / 7.41) * 100
print(f"\nYield scaling:")
print(f"  Raw: {yield_raw:.4f}")
print(f"  Scaled: {yield_scaled:.2f}%")

perf_raw = preds[4]
perf_scaled = ((perf_raw + 1.82) / 3.5) * 100
print(f"\nPerformance scaling:")
print(f"  Raw: {perf_raw:.4f}")
print(f"  Scaled: {perf_scaled:.2f}%")
print(f"  Expected range: 0-100%")
print(f"  Actual PCA range: -1.82 to +1.68")

print("\n" + "=" * 80)
