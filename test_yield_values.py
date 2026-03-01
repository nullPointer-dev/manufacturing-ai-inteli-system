"""
Test script to check yield values from the scaled yield_score
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

# Check yield statistics
print("=" * 80)
print("YIELD VALUES FROM SCALED YIELD_SCORE (-4.33 to +3.08 → 0-100%)")
print("=" * 80)
print(f"Min: {df['Yield'].min():.2f}%")
print(f"Max: {df['Yield'].max():.2f}%")
print(f"Mean: {df['Yield'].mean():.2f}%")
print(f"Median: {df['Yield'].median():.2f}%")
print(f"Std Dev: {df['Yield'].std():.2f}%")

# Count batches in ranges
print("\nDistribution:")
print(f"  0-50%: {len(df[df['Yield'] < 50])}")
print(f"  50-60%: {len(df[(df['Yield'] >= 50) & (df['Yield'] < 60)])}")
print(f"  60-70%: {len(df[(df['Yield'] >= 60) & (df['Yield'] < 70)])}")
print(f"  70-80%: {len(df[(df['Yield'] >= 70) & (df['Yield'] < 80)])}")
print(f"  80-90%: {len(df[(df['Yield'] >= 80) & (df['Yield'] < 90)])}")
print(f"  90-100%: {len(df[(df['Yield'] >= 90) & (df['Yield'] <= 100)])}")

# Show sample values
print("\nSample Yield Values (first 10 batches):")
print(df[['Yield', 'Quality', 'Performance', 'Energy']].head(10).to_string())

print("\n" + "=" * 80)
