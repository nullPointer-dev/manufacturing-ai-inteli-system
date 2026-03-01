"""
Verify Content_Uniformity scaling to 80-100% for yield
"""
import sys
sys.path.append('backend/src')

from data_pipeline import build_pipeline
from batch_scorer import attach_predictions

# Load historical data
df = build_pipeline()
print(f"Loaded {len(df)} historical batches\n")

# Attach predictions (with new scaling)
df = attach_predictions(df)

print("=" * 80)
print("YIELD (CONTENT_UNIFORMITY SCALED TO 80-100%)")
print("=" * 80)
print(f"Min: {df['Yield'].min():.2f}%")
print(f"Max: {df['Yield'].max():.2f}%")
print(f"Mean: {df['Yield'].mean():.2f}%")
print(f"Median: {df['Yield'].median():.2f}%")
print(f"Std Dev: {df['Yield'].std():.2f}%")

print("\nDistribution:")
print(f"  80-85%: {len(df[(df['Yield'] >= 80) & (df['Yield'] < 85)])}")
print(f"  85-90%: {len(df[(df['Yield'] >= 85) & (df['Yield'] < 90)])}")
print(f"  90-95%: {len(df[(df['Yield'] >= 90) & (df['Yield'] < 95)])}")
print(f"  95-100%: {len(df[(df['Yield'] >= 95) & (df['Yield'] <= 100)])}")

print("\nSample Yield values (first 10 batches):")
print(df[['Yield', 'Content_Uniformity', 'Quality', 'Performance']].head(10).to_string())

print("\n" + "=" * 80)
print("ORIGINAL CONTENT_UNIFORMITY VALUES")
print("=" * 80)
print(f"Min: {df['Content_Uniformity'].min():.2f}%")
print(f"Max: {df['Content_Uniformity'].max():.2f}%")
print(f"Mean: {df['Content_Uniformity'].mean():.2f}%")

print("\n" + "=" * 80)
print("SCALING FORMULA VERIFICATION")
print("=" * 80)
print("Formula: 80 + (Content_Uniformity - 89.8) * (20 / 16.5)")
print("Range: 89.8-106.3% → 80-100%")
print()

# Test formula with edge cases
test_values = [89.8, 95.0, 98.34, 100.0, 106.3]
for val in test_values:
    scaled = 80.0 + (val - 89.8) * (20.0 / 16.5)
    clamped = max(80.0, min(100.0, scaled))
    print(f"  Content_Uniformity {val:.2f}% → Yield {clamped:.2f}%")

print("\n" + "=" * 80)
