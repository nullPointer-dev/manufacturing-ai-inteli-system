"""
Debug yield calculation discrepancy
"""
import sys
sys.path.append('backend/src')

# Test manual calculation
raw_pca = 0.3068
scaled_manual = ((raw_pca + 4.33) / 7.41) * 100
print(f"Manual calculation: {raw_pca} → {scaled_manual:.2f}%")

# Test what predict_batch returns
from prediction_service import predict_batch

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

prediction = predict_batch(default_params)
print(f"\npredict_batch returns: {prediction['Yield']:.2f}%")

# Check the raw model prediction directly
from prediction_service import _load_model
import pandas as pd

model, feature_cols = _load_model()
df = pd.DataFrame([default_params])

# Add missing features
for col in feature_cols:
    if col not in df.columns:
        df[col] = 0.0

df = df[feature_cols]
preds = model.predict(df)[0]

print(f"\nRaw PCA yield_score from model: {preds[3]:.6f}")

# Apply the scaling formula
yield_scaled = ((preds[3] + 4.33) / 7.41) * 100
yield_clamped = max(0.0, min(100.0, yield_scaled))

print(f"After scaling formula: {yield_scaled:.2f}%")
print(f"After clamping: {yield_clamped:.2f}%")

# Check if there's a difference between what the model predicts with defaults vs without
print("\n" + "=" * 80)
print("INVESTIGATING FEATURE DEFAULTS")
print("=" * 80)

# Let's see what features are actually being set
from prediction_service import predict_batch
import pandas as pd

# Monkey patch to see what's happening
import prediction_service

# Call with defaults
print("\nCalling predict_batch with industrial validation defaults...")
result = predict_batch(default_params)
print(f"Result Yield: {result['Yield']:.2f}%")
