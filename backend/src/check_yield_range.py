"""
Quick script to check the actual min/max range of yield_score in training data
and calculate what the current prediction would be with min-max normalization.
"""

from data_pipeline import build_pipeline

# Load the training data
df = build_pipeline()

# Check yield_score statistics
yield_score = df['yield_score']

yield_min = yield_score.min()
yield_max = yield_score.max()
yield_mean = yield_score.mean()
yield_std = yield_score.std()

print("\n===== YIELD_SCORE STATISTICS FROM TRAINING DATA =====")
print(f"Min: {yield_min:.4f}")
print(f"Max: {yield_max:.4f}")
print(f"Mean: {yield_mean:.4f}")
print(f"Std: {yield_std:.4f}")
print(f"Range: {yield_max - yield_min:.4f}")

# Check performance_score statistics
performance_score = df['performance_score']

perf_min = performance_score.min()
perf_max = performance_score.max()
perf_mean = performance_score.mean()
perf_std = performance_score.std()

print("\n===== PERFORMANCE_SCORE STATISTICS FROM TRAINING DATA =====")
print(f"Min: {perf_min:.4f}")
print(f"Max: {perf_max:.4f}")
print(f"Mean: {perf_mean:.4f}")
print(f"Std: {perf_std:.4f}")
print(f"Range: {perf_max - perf_min:.4f}")

# Now calculate what the current prediction values would be with min-max normalization
# Current raw PCA scores from the model prediction
current_yield_pca = -0.32
current_performance_pca = 0.66

# Apply min-max normalization formula
yield_normalized = ((current_yield_pca - yield_min) / (yield_max - yield_min)) * 100
performance_normalized = ((current_performance_pca - perf_min) / (perf_max - perf_min)) * 100

print("\n===== CURRENT PREDICTIONS WITH MIN-MAX NORMALIZATION (0-100) =====")
print(f"Yield: {current_yield_pca:.4f} (raw PCA) → {yield_normalized:.2f}%")
print(f"Performance: {current_performance_pca:.4f} (raw PCA) → {performance_normalized:.2f}%")

print("\n===== COMPARISON WITH CURRENT NORMALIZATION (70-100) =====")
# Current normalization formula
def normalize_current(pca_score, min_pct=70.0, max_pct=100.0):
    pca_min = -3.0
    pca_max = 3.0
    clamped_score = max(pca_min, min(pca_max, pca_score))
    normalized = (clamped_score - pca_min) / (pca_max - pca_min)
    percentage = min_pct + normalized * (max_pct - min_pct)
    return percentage

current_yield_normalized_v1 = normalize_current(current_yield_pca)
current_perf_normalized_v1 = normalize_current(current_performance_pca)

print(f"CURRENT METHOD (fixed range -3 to +3 → 70-100%):")
print(f"  Yield: {current_yield_normalized_v1:.2f}%")
print(f"  Performance: {current_perf_normalized_v1:.2f}%")

print(f"\nUSER'S METHOD (actual data min/max → 0-100%):")
print(f"  Yield: {yield_normalized:.2f}%")
print(f"  Performance: {performance_normalized:.2f}%")
