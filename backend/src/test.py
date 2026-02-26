import json
import random
from pathlib import Path
import pandas as pd
import numpy as np

from data_pipeline import build_pipeline
from prediction_service import predict_batch
from optimizer_auto import optimize_auto
from optimizer_target import optimize_target
from golden_updater import check_and_update_golden
from learning_controller import check_and_retrain
from integration_api import (
    api_predict,
    api_optimize_auto,
    api_optimize_target,
    api_get_golden,
    api_get_model_history,
    api_system_status
)

print("\n==============================")
print("FULL BACKEND SYSTEM TEST")
print("==============================\n")


# =========================================================
# TEST 1 — DATA PIPELINE
# =========================================================
print("TEST 1: Data pipeline")

df = build_pipeline()
assert isinstance(df, pd.DataFrame)
assert len(df) > 0
print("✔ Pipeline OK — rows:", len(df))


# =========================================================
# TEST 2 — PREDICTION ENGINE
# =========================================================
print("\nTEST 2: Prediction engine")

sample_row = df.iloc[0].to_dict()
preds = predict_batch(sample_row)

required_keys = ["Quality","Yield","Performance","Energy","CO2"]

for k in required_keys:
    assert k in preds

print("✔ Prediction OK:", preds)


# =========================================================
# TEST 3 — API PREDICTION
# =========================================================
print("\nTEST 3: API predict")

api_out = api_predict(sample_row)
assert "prediction" in api_out
print("✔ API predict OK")


# =========================================================
# TEST 4 — PRESET OPTIMIZATION
# =========================================================
print("\nTEST 4: Preset optimization")

results, proposal, cluster, scenario = optimize_auto(mode="balanced")

assert results is not None
assert len(results) > 0
assert cluster is not None

print("✔ Preset optimization OK")
print("Top row:\n", results.iloc[0])


# =========================================================
# TEST 5 — CUSTOM OPTIMIZATION
# =========================================================
print("\nTEST 5: Custom optimization")

weights = {
    "quality": 0.4,
    "yield": 0.2,
    "performance": 0.2,
    "energy": 0.1,
    "co2": 0.1
}

results_c, proposal_c, cluster_c, scenario_key = optimize_auto(
    mode="custom",
    custom_weights=weights
)

assert scenario_key is not None
assert results_c is not None

print("✔ Custom optimization OK")
print("Scenario key:", scenario_key)


# =========================================================
# TEST 6 — TARGET OPTIMIZATION
# =========================================================
print("\nTEST 6: Target optimization")

target_res = optimize_target(
    required_reduction=2,
    min_quality=0,
    min_yield=0,
    min_performance=0,
    mode="balanced"
)

assert target_res is not None
assert len(target_res) > 0

print("✔ Target optimization OK")


# =========================================================
# TEST 7 — GOLDEN UPDATE
# =========================================================
print("\nTEST 7: Golden update")

best = results.iloc[0]
updated = check_and_update_golden(best, "balanced", cluster)

assert isinstance(updated, bool)
print("✔ Golden update logic OK")


# =========================================================
# TEST 8 — RETRAIN CONTROLLER
# =========================================================
print("\nTEST 8: Retrain controller")

retrained, flags = check_and_retrain()
assert isinstance(retrained, bool)
assert isinstance(flags, dict)

print("✔ Retrain controller OK")
print("Flags:", flags)


# =========================================================
# TEST 9 — API OPTIMIZATION
# =========================================================
print("\nTEST 9: API optimize")

api_opt = api_optimize_auto("balanced")
assert "top_result" in api_opt
print("✔ API optimize OK")


# =========================================================
# TEST 10 — API TARGET OPTIMIZE
# =========================================================
print("\nTEST 10: API target optimize")

api_target = api_optimize_target(
    required_reduction=1,
    min_quality=0,
    min_yield=0,
    min_performance=0
)

assert api_target["status"] in ["success","no_solution"]
print("✔ API target OK")


# =========================================================
# TEST 11 — GOLDEN REGISTRY
# =========================================================
print("\nTEST 11: Golden registry")

gold = api_get_golden()
assert isinstance(gold, dict)
print("✔ Golden registry OK")


# =========================================================
# TEST 12 — MODEL HISTORY
# =========================================================
print("\nTEST 12: Model history")

hist = api_get_model_history()
assert isinstance(hist, list)
print("✔ Model history OK")


# =========================================================
# TEST 13 — SYSTEM STATUS
# =========================================================
print("\nTEST 13: System status")

status = api_system_status()
assert isinstance(status, dict)
print("✔ System status OK:", status)


# =========================================================
# TEST 14 — STRESS TEST (MULTIPLE RUNS)
# =========================================================
print("\nTEST 14: Stress test optimizer")

for i in range(3):
    res, prop, cl, sc = optimize_auto(mode="balanced")
    assert res is not None
    print(f"Run {i+1} OK")

print("✔ Stress test passed")

# =========================================================
# TEST 15 — REAL-TIME BATCH ANALYSIS & CORRECTION
# =========================================================

print("\nTEST 15: Real-time batch analysis & correction")

from correction_engine import analyze_batch_against_golden
from golden_signature import identify_golden_signatures
from context_engine import assign_context_clusters

# simulate live batch
live_batch = df.iloc[0].copy()

# inject artificial drift
live_batch["avg_temperature"] *= 1.20
live_batch["Compression_Force"] *= 0.75

live_df = pd.DataFrame([live_batch])

# assign cluster
live_df, _ = assign_context_clusters(live_df)
cluster_id = live_df["context_cluster"].iloc[0]

# get golden ranges for that cluster
_, golden_ranges, _ = identify_golden_signatures(
    df,
    cluster_id=cluster_id
)

# analyze batch
analysis = analyze_batch_against_golden(
    live_df.iloc[0].to_dict(),
    golden_ranges
)

assert isinstance(analysis, pd.DataFrame)
assert len(analysis) > 0
assert "Severity" in analysis.columns
assert "Suggestion" in analysis.columns

print("Correction analysis preview:")
print(analysis.head())

print("✔ Real-time correction engine OK")

print("\n==============================")
print("ALL SYSTEM TESTS PASSED")
print("==============================\n")