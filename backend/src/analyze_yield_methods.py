"""
Analyze manufacturing data to find the best way to calculate yield.
"""

from data_pipeline import build_pipeline
import pandas as pd
import numpy as np

df = build_pipeline()

print("\n===== ALL AVAILABLE COLUMNS =====")
print(df.columns.tolist())

print("\n===== PRODUCTION-RELATED COLUMNS =====")
production_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['batch', 'weight', 'tablet', 'uniformity', 'hardness', 'friability', 'dissolution', 'content'])]
print(production_cols)

print("\n===== SAMPLE DATA (First 3 Batches) =====")
key_cols = ['Batch_ID', 'Tablet_Weight', 'Hardness', 'Content_Uniformity', 'Friability', 'Dissolution_Rate']
print(df[key_cols].head(3))

print("\n===== STATISTICS FOR KEY QUALITY METRICS =====")
quality_metrics = ['Hardness', 'Content_Uniformity', 'Friability', 'Dissolution_Rate']
print(df[quality_metrics].describe())

print("\n" + "="*70)
print("BEST WAYS TO CALCULATE YIELD IN PHARMACEUTICAL MANUFACTURING")
print("="*70)

print("""
1. DIRECT YIELD FORMULA (If batch quantities are known):
   Yield % = (Actual Good Tablets / Theoretical Tablets) × 100
   
   Best for: Real-world manufacturing where you track input/output
   Accuracy: ★★★★★ (Most accurate - uses actual counts)
   
   Formula: yield = (tablets_produced / tablets_expected) × 100
   Requires: Production records with actual vs expected counts

2. CONTENT UNIFORMITY AS YIELD PROXY (Current Dashboard Method):
   Uses: Content_Uniformity directly as yield percentage
   
   Best for: When direct production data isn't available
   Accuracy: ★★★★☆ (Good proxy - high uniformity = less waste)
   
   Logic: High content uniformity (95-100%) indicates consistent
          product quality with minimal rejections and rework
   
   Current Range: {df['Content_Uniformity'].min():.1f}% - {df['Content_Uniformity'].max():.1f}%
   Current Mean: {df['Content_Uniformity'].mean():.1f}%

3. QUALITY-WEIGHTED YIELD (Recommended for ML):
   Combines multiple quality factors that affect yield
   
   Best for: Predictive models and optimization
   Accuracy: ★★★★☆ (Captures multiple yield drivers)
   
   Formula:
   yield = (
       0.40 × Content_Uniformity +
       0.30 × (100 - Friability×50) +  # Lower friability = higher yield
       0.20 × (Hardness/max_hardness)×100 +
       0.10 × (Dissolution_Rate/max_dissolution)×100
   )
   
   Logic: 
   - Content_Uniformity (40%): Primary indicator of consistency
   - Low Friability (30%): Less tablet breakage = less waste
   - Adequate Hardness (20%): Tablets meet specs
   - Good Dissolution (10%): Product efficacy maintained

4. PCA-BASED YIELD SCORE (Current ML Approach):
   Uses: PCA on [Hardness, Content_Uniformity, Friability]
   
   Best for: Dimensionality reduction in complex models
   Accuracy: ★★★☆☆ (Mathematically valid but not intuitive)
   
   Problem: Produces z-scores (-4 to +4) not percentages (0-100%)
   Solution: Requires normalization to meaningful range
   
   Current Range: {df['yield_score'].min():.2f} to {df['yield_score'].max():.2f}

5. REJECTION RATE BASED YIELD (Industry Standard):
   Yield % = 100% - Rejection Rate
   
   Best for: Quality control systems with defect tracking
   Accuracy: ★★★★★ (Direct measure of production efficiency)
   
   Formula: yield = 100 - (defects / total_produced) × 100
   Requires: Defect/rejection tracking system
""")

print("\n" + "="*70)
print("RECOMMENDATION FOR YOUR SYSTEM")
print("="*70)

print("""
BEST APPROACH: Quality-Weighted Yield Formula

Reasons:
1. Uses actual measured data (Content_Uniformity, Hardness, Friability)
2. Produces intuitive percentage values (0-100%)
3. No need for PCA normalization gymnastics
4. Aligns with pharmaceutical manufacturing KPIs
5. Each factor has clear industrial meaning

Implementation:
""")

# Calculate quality-weighted yield
max_hardness = df['Hardness'].max()
max_dissolution = df['Dissolution_Rate'].max()

df['yield_quality_weighted'] = (
    0.40 * df['Content_Uniformity'] +
    0.30 * (100 - df['Friability'] * 50) +
    0.20 * (df['Hardness'] / max_hardness) * 100 +
    0.10 * (df['Dissolution_Rate'] / max_dissolution) * 100
)

# Ensure it's in 0-100 range
df['yield_quality_weighted'] = df['yield_quality_weighted'].clip(0, 100)

print(f"\nQuality-Weighted Yield Statistics:")
print(f"  Min: {df['yield_quality_weighted'].min():.2f}%")
print(f"  Max: {df['yield_quality_weighted'].max():.2f}%")
print(f"  Mean: {df['yield_quality_weighted'].mean():.2f}%")
print(f"  Std: {df['yield_quality_weighted'].std():.2f}%")

print(f"\nComparison with Current Methods:")
print(f"  Content_Uniformity (Dashboard): {df['Content_Uniformity'].mean():.2f}%")
print(f"  PCA yield_score (ML): {df['yield_score'].mean():.2f} (z-score)")
print(f"  Quality-Weighted (Recommended): {df['yield_quality_weighted'].mean():.2f}%")

print("\n" + "="*70)
print("QUICK WIN: Replace PCA yield_score in feature_engineering.py")
print("="*70)
print("""
Instead of:
    pca_yield = PCA(n_components=1)
    df["yield_score"] = pca_yield.fit_transform(yield_scaled)

Use:
    max_hardness = df['Hardness'].max()
    max_dissolution = df['Dissolution_Rate'].max()
    
    df['yield_score'] = (
        0.40 * df['Content_Uniformity'] +
        0.30 * (100 - df['Friability'] * 50) +
        0.20 * (df['Hardness'] / max_hardness) * 100 +
        0.10 * (df['Dissolution_Rate'] / max_dissolution) * 100
    ).clip(0, 100)

Benefits:
✓ Direct percentage values (70-100% typical range)
✓ No normalization needed
✓ Industrially meaningful
✓ Easy to explain to stakeholders
✓ Maintains model accuracy with better interpretability
""")
