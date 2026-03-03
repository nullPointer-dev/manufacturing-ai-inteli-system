"""
Check performance_score (PCA) range to understand the normalization
"""
import sys
sys.path.append('backend/src')

from data_pipeline import build_pipeline
from batch_scorer import attach_predictions

# Load historical data
df = build_pipeline()
print(f"Loaded {len(df)} historical batches\n")

# Attach predictions
df = attach_predictions(df)

# Check Performance statistics (this is the raw PCA score)
print("=" * 80)
print("PERFORMANCE (PCA SCORE) RANGE")
print("=" * 80)
print(f"Min: {df['Performance'].min():.4f}")
print(f"Max: {df['Performance'].max():.4f}")
print(f"Mean: {df['Performance'].mean():.4f}")
print(f"Median: {df['Performance'].median():.4f}")
print(f"Std Dev: {df['Performance'].std():.4f}")

print("\nSample Performance values (first 10 batches):")
print(df[['Performance', 'Yield', 'Quality']].head(10).to_string())

# Test the normalization formula used in industrial_validation.py
print("\n" + "=" * 80)
print("NORMALIZATION FORMULA TEST")
print("=" * 80)
print("Formula: (perf_raw + 3) / 6 * 50 + 50")
print("Clamped to: max(50.0, min(100.0, value))")
print()

sample_perfs = df['Performance'].head(10).values
for i, perf in enumerate(sample_perfs):
    normalized = (perf + 3) / 6 * 50 + 50
    clamped = max(50.0, min(100.0, normalized))
    print(f"Batch {i}: Raw={perf:.3f} -> Normalized={normalized:.2f}% -> Clamped={clamped:.2f}%")

print("\n" + "=" * 80)
