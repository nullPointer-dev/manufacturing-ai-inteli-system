import sys
sys.path.insert(0, 'src')
from data_pipeline import build_pipeline
import pandas as pd

# Load the data
df = build_pipeline()

# Calculate performance the new way
df["performance_raw"] = (df["quality_score"] / df["total_process_time"])
perf_min = df["performance_raw"].min()
perf_max = df["performance_raw"].max()

print('='*60)
print('NORMALIZED PERFORMANCE CALCULATION')
print('='*60)
print(f'Raw performance min: {perf_min:.6f}')
print(f'Raw performance max: {perf_max:.6f}')

if perf_max > perf_min:
    df["performance_metric"] = ((df["performance_raw"] - perf_min) / (perf_max - perf_min)) * 100
else:
    df["performance_metric"] = 50.0

print(f'\nNormalized Performance (0-100 scale):')
print(f'Min: {df["performance_metric"].min():.2f}')
print(f'Max: {df["performance_metric"].max():.2f}')
print(f'Mean: {df["performance_metric"].mean():.2f}')
print(f'Median: {df["performance_metric"].median():.2f}')

# Last 5 batches (what shows on dashboard)
recent_df = df.tail(5)
current_performance = recent_df["performance_metric"].mean()

print(f'\nDashboard will show (last 5 batches avg): {current_performance:.2f} Score')
print(f'This replaces the previous: 292.40%')

print('\n' + '='*60)
print('LAST 5 BATCHES PERFORMANCE SCORES')
print('='*60)
for idx, perf in recent_df["performance_metric"].items():
    quality = recent_df.loc[idx, "quality_score"]
    time = recent_df.loc[idx, "total_process_time"]
    print(f'Batch {idx}: {perf:.2f} Score (Quality: {quality:.2f}, Time: {time:.0f})')
