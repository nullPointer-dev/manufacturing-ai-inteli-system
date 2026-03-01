"""
Compare yield_score WITH and WITHOUT StandardScaler in feature_engineering
"""

from data_pipeline import build_pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Load the data
df = build_pipeline()

# Extract yield features
yield_features = df[["Hardness", "Content_Uniformity", "Friability"]].copy()
yield_features = yield_features.fillna(yield_features.mean())

print("\n===== RAW FEATURE STATISTICS =====")
print(yield_features.describe())

# METHOD 1: WITH StandardScaler (Current Implementation)
print("\n===== METHOD 1: WITH StandardScaler (CURRENT) =====")
scaler = StandardScaler()
yield_scaled = scaler.fit_transform(yield_features)
pca_yield_with_scaler = PCA(n_components=1)
yield_score_with_scaler = pca_yield_with_scaler.fit_transform(yield_scaled).flatten()

print(f"Scaled Features Mean: {yield_scaled.mean(axis=0)}")
print(f"Scaled Features Std: {yield_scaled.std(axis=0)}")
print(f"\nPCA Explained Variance: {pca_yield_with_scaler.explained_variance_ratio_[0]:.4f}")
print(f"PCA Components (weights): {pca_yield_with_scaler.components_[0]}")
print(f"\nYield Score Statistics:")
print(f"  Min: {yield_score_with_scaler.min():.4f}")
print(f"  Max: {yield_score_with_scaler.max():.4f}")
print(f"  Mean: {yield_score_with_scaler.mean():.4f}")
print(f"  Std: {yield_score_with_scaler.std():.4f}")

# METHOD 2: WITHOUT StandardScaler (Your Question)
print("\n===== METHOD 2: WITHOUT StandardScaler =====")
pca_yield_no_scaler = PCA(n_components=1)
yield_score_no_scaler = pca_yield_no_scaler.fit_transform(yield_features.values).flatten()

print(f"PCA Explained Variance: {pca_yield_no_scaler.explained_variance_ratio_[0]:.4f}")
print(f"PCA Components (weights): {pca_yield_no_scaler.components_[0]}")
print(f"\nYield Score Statistics:")
print(f"  Min: {yield_score_no_scaler.min():.4f}")
print(f"  Max: {yield_score_no_scaler.max():.4f}")
print(f"  Mean: {yield_score_no_scaler.mean():.4f}")
print(f"  Std: {yield_score_no_scaler.std():.4f}")

# Compare specific prediction case
# Default batch parameters from industrial_validation.py
print("\n===== COMPARISON FOR TYPICAL BATCH =====")
typical_batch = {
    'Hardness': 85.0,
    'Content_Uniformity': 95.0,
    'Friability': 0.5
}

print(f"Input: Hardness={typical_batch['Hardness']}, Content_Uniformity={typical_batch['Content_Uniformity']}, Friability={typical_batch['Friability']}")

# WITH StandardScaler
batch_scaled = scaler.transform([[typical_batch['Hardness'], typical_batch['Content_Uniformity'], typical_batch['Friability']]])
yield_with_scaler = pca_yield_with_scaler.transform(batch_scaled)[0][0]

# WITHOUT StandardScaler
yield_no_scaler = pca_yield_no_scaler.transform([[typical_batch['Hardness'], typical_batch['Content_Uniformity'], typical_batch['Friability']]])[0][0]

print(f"\nWITH StandardScaler: {yield_with_scaler:.4f}")
print(f"WITHOUT StandardScaler: {yield_no_scaler:.4f}")

print(f"\nDifference: {abs(yield_no_scaler - yield_with_scaler):.4f}")
print(f"Ratio: {yield_no_scaler / yield_with_scaler if yield_with_scaler != 0 else 'N/A':.2f}x")

# Show what percentage normalization would give
print("\n===== NORMALIZED TO 0-100% =====")

# Method 1 (WITH StandardScaler) - uses actual training data range
yield_min_scaled = yield_score_with_scaler.min()
yield_max_scaled = yield_score_with_scaler.max()
yield_normalized_method1 = ((yield_with_scaler - yield_min_scaled) / (yield_max_scaled - yield_min_scaled)) * 100

# Method 2 (WITHOUT StandardScaler) - uses actual training data range
yield_min_no_scaler = yield_score_no_scaler.min()
yield_max_no_scaler = yield_score_no_scaler.max()
yield_normalized_method2 = ((yield_no_scaler - yield_min_no_scaler) / (yield_max_no_scaler - yield_min_no_scaler)) * 100

print(f"WITH StandardScaler → 0-100%: {yield_normalized_method1:.2f}%")
print(f"WITHOUT StandardScaler → 0-100%: {yield_normalized_method2:.2f}%")
