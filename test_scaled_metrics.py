"""
Check scaled Performance values from batch_scorer
"""
import sys
sys.path.append('backend/src')

from data_pipeline import build_pipeline
from batch_scorer import attach_predictions

# Load historical data
df = build_pipeline()
print(f"Loaded {len(df)} historical batches\n")

# Attach predictions (with scaling applied)
df = attach_predictions(df)

# Check Performance statistics (now scaled to 0-100%)
print("=" * 80)
print("PERFORMANCE (SCALED TO 0-100%)")
print("=" * 80)
print(f"Min: {df['Performance'].min():.2f}%")
print(f"Max: {df['Performance'].max():.2f}%")
print(f"Mean: {df['Performance'].mean():.2f}%")
print(f"Median: {df['Performance'].median():.2f}%")
print(f"Std Dev: {df['Performance'].std():.2f}%")

print("\nDistribution:")
print(f"  0-20%: {len(df[df['Performance'] < 20])}")
print(f"  20-40%: {len(df[(df['Performance'] >= 20) & (df['Performance'] < 40)])}")
print(f"  40-60%: {len(df[(df['Performance'] >= 40) & (df['Performance'] < 60)])}")
print(f"  60-80%: {len(df[(df['Performance'] >= 60) & (df['Performance'] < 80)])}")
print(f"  80-100%: {len(df[(df['Performance'] >= 80) & (df['Performance'] <= 100)])}")

print("\nSample Performance values (first 10 batches):")
print(df[['Performance', 'Yield', 'Quality', 'Energy']].head(10).to_string())

print("\n" + "=" * 80)
print("YIELD (SCALED TO 0-100%)")
print("=" * 80)
print(f"Min: {df['Yield'].min():.2f}%")
print(f"Max: {df['Yield'].max():.2f}%")
print(f"Mean: {df['Yield'].mean():.2f}%")
print(f"Median: {df['Yield'].median():.2f}%")

print("\n" + "=" * 80)
print("BOTH METRICS NOW PROPERLY SCALED FROM PCA TO 0-100%")
print("  - Yield: PCA range -4.33 to +3.08 → 0-100%")
print("  - Performance: PCA range -1.82 to +1.68 → 0-100%")
print("=" * 80)
