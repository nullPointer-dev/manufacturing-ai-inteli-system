import json
from pathlib import Path

from prediction_service import predict_batch
from optimizer_auto import optimize_auto
from optimizer_target import optimize_target
from golden_updater import check_and_update_golden, _safe_load, SESSION_FILE, HISTORY_FILE, REGISTRY_FILE, clear_session_and_archive, get_archive, log_rejection, get_rejections
from explainability_engine import get_global_feature_importance
from learning_controller import check_and_retrain

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
VERSION_LOG = MODEL_DIR / "model_versions.json"

# =========================================================
# PREDICTION
# =========================================================
def api_predict(payload: dict):
    preds = predict_batch(payload)
    return {"prediction": preds}


# =========================================================
# AUTO OPTIMIZATION
# =========================================================
def api_optimize_auto(mode="balanced", custom_weights=None):

    results, proposal, cluster_id, scenario_key = optimize_auto(
        mode=mode,
        custom_weights=custom_weights
    )

    if results is None:
        return {"status": "no_solution"}

    best = results.iloc[0].to_dict()

    return {
        "status": "success",
        "top_result": best,
        "proposal": proposal,
        "cluster_id": int(cluster_id),
        "scenario_key": scenario_key
    }


# =========================================================
# TARGET OPTIMIZATION
# =========================================================
def api_optimize_target(required_reduction=None,
                        min_quality=None,
                        min_yield=None,
                        min_performance=None,
                        mode="balanced",
                        custom_weights=None):

    results = optimize_target(
        required_reduction=required_reduction,
        min_quality=min_quality,
        min_yield=min_yield,
        min_performance=min_performance,
        mode=mode,
        custom_weights=custom_weights,
    )

    if results is None or len(results) == 0:
        return {"status": "no_solution"}

    return {
        "status": "success",
        "best_solution": results.iloc[0].to_dict()
    }


# =========================================================
# ACCEPT GOLDEN UPDATE
# =========================================================
def api_accept_golden(best_row: dict,
                      mode: str,
                      cluster_id: int,
                      scenario_key: str | None = None):

    success = check_and_update_golden(
        best_row,
        mode,
        int(cluster_id),
        scenario_key=scenario_key,
        force=True
    )

    return {"golden_updated": success}


# =========================================================
# GET GOLDEN REGISTRY (SESSION)
# =========================================================
def api_get_golden():
    return _safe_load(SESSION_FILE, {})


# =========================================================
# GET GOLDEN ARCHIVE (ALL HISTORY)
# =========================================================
def api_get_golden_archive():
    return get_archive()


# =========================================================
# CLEAR SESSION AND ARCHIVE
# =========================================================
def api_clear_session():
    return clear_session_and_archive()


# =========================================================
# MODEL HISTORY
# =========================================================
def api_get_model_history():
    if VERSION_LOG.exists():
        with open(VERSION_LOG, "r") as f:
            return json.load(f)
    return []


# =========================================================
# FEATURE IMPORTANCE
# =========================================================
_SHAP_EXCLUDED = {
    "Hardness_zscore", "total_energy_zscore", "Content_Uniformity_zscore",
    "Dissolution_Rate_zscore", "quality_score", "yield_score",
    "performance_score", "energy_efficiency_score", "process_intensity",
    "stability_index", "energy_per_tablet", "process_efficiency",
    "temperature_pressure_ratio", "duration_granulation", "duration_drying",
}

def api_get_feature_importance():
    df = get_global_feature_importance()
    if df is None:
        return {"status": "no_data"}
    # Remove redundant/derived features (z-scores, composite KPIs, duplicates)
    df = df[~df["feature"].isin(_SHAP_EXCLUDED)].reset_index(drop=True)
    return df.to_dict(orient="records")


# =========================================================
# RETRAIN CHECK
# =========================================================
def api_check_retrain():
    retrained, flags = check_and_retrain()
    return {
        "retrained": retrained,
        "flags": flags
    }


# =========================================================
# SYSTEM STATUS
# =========================================================
def api_system_status():
    return {
        "model_exists": (MODEL_DIR / "model.pkl").exists(),
        "golden_session_exists": SESSION_FILE.exists(),
        "version_log_exists": VERSION_LOG.exists()
    }


# =========================================================
# BATCH CORRECTION ANALYSIS
# =========================================================
def api_get_batches():
    """Get list of all available batches"""
    from data_pipeline import build_pipeline
    
    df = build_pipeline()
    
    # Select relevant columns with correct names
    batch_list = []
    for _, row in df.iterrows():
        batch_list.append({
            "Batch_ID": row["Batch_ID"],
            "Quality_Score": row["quality_score"],
            "Yield_Percentage": row["yield_score"] * 100,  # Convert to percentage
            "Performance_Index": row["performance_score"]
        })
    
    return {
        "status": "success",
        "batches": batch_list,
        "total": len(batch_list)
    }


def api_analyze_batch(batch_id: str):
    """Analyze a specific batch against golden ranges"""
    from data_pipeline import build_pipeline
    from correction_engine import analyze_batch_against_golden
    from golden_signature import identify_golden_signatures
    from context_engine import assign_context_clusters
    import joblib
    
    # Load all data
    df = build_pipeline()
    
    # Find the batch
    batch_data = df[df["Batch_ID"] == batch_id]
    
    if len(batch_data) == 0:
        return {
            "status": "error",
            "message": f"Batch {batch_id} not found"
        }
    
    batch_row = batch_data.iloc[0].to_dict()
    
    # Assign context clusters to historical data
    df, _ = assign_context_clusters(df)
    
    # Get the cluster for the current batch (use mode of historical data)
    current_cluster = df["context_cluster"].mode()[0] if "context_cluster" in df.columns else 1
    
    # Identify golden signatures and ranges from historical top performers
    # This recomputes ranges from the best historical batches
    _, golden_ranges, _ = identify_golden_signatures(
        df,
        mode="balanced",  # Use balanced mode for analysis
        cluster_id=current_cluster,
        custom_weights=None
    )
    
    if not golden_ranges or len(golden_ranges) == 0:
        return {
            "status": "error",
            "message": "Could not compute golden ranges from historical data. Need at least 10 batches."
        }
    
    # Strip parameters that are redundant / not directly actionable:
    # - z-score variants (already represented by the base metric)
    # - composite computed KPI scores (outcomes, not controllable process inputs)
    # - process-data duration columns that duplicate production-data input params
    EXCLUDED_PARAMS = {
        "Hardness_zscore",
        "total_energy_zscore",
        "Content_Uniformity_zscore",
        "Dissolution_Rate_zscore",
        "quality_score",
        "yield_score",
        "performance_score",
        "energy_efficiency_score",
        "process_intensity",
        "stability_index",
        "energy_per_tablet",
        "process_efficiency",
        "temperature_pressure_ratio",
        "duration_granulation",   # duplicate of Granulation_Time
        "duration_drying",        # duplicate of Drying_Time
    }
    golden_ranges = {k: v for k, v in golden_ranges.items() if k not in EXCLUDED_PARAMS}

    # Load model and features for impact prediction
    model = None
    feature_cols = None
    
    try:
        model = joblib.load(MODEL_DIR / "model.pkl")
        feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")
    except:
        pass
    
    # Analyze batch
    report_df = analyze_batch_against_golden(
        batch_row,
        golden_ranges,
        model=model,
        feature_cols=feature_cols
    )

    # Enforce consistent severity ordering: Critical > Moderate > OK
    severity_order = {"Critical": 0, "Moderate": 1, "OK": 2}
    if len(report_df) > 0:
        report_df["_severity_rank"] = report_df["Severity"].map(severity_order).fillna(3)
        report_df["_abs_drift"] = report_df["Drift (σ)"].abs()
        report_df = report_df.sort_values(
            by=["_severity_rank", "_abs_drift"],
            ascending=[True, False]
        ).drop(columns=["_severity_rank", "_abs_drift"])
    
    # Calculate CO2 from energy
    CO2_FACTOR = 0.82  # kg CO₂ per kWh
    energy = batch_row.get("total_energy", 0)
    co2 = energy * CO2_FACTOR
    
    return {
        "status": "success",
        "batch_id": batch_id,
        "batch_info": {
            "quality": batch_row.get("quality_score"),
            "yield": batch_row.get("yield_score", 0) * 100,  # Convert to percentage
            "performance": batch_row.get("performance_score"),
            "energy": energy,
            "co2": co2
        },
        "analysis": report_df.to_dict(orient="records"),
        "summary": {
            "total_parameters": len(report_df),
            "critical": len(report_df[report_df["Severity"] == "Critical"]),
            "moderate": len(report_df[report_df["Severity"] == "Moderate"]),
            "ok": len(report_df[report_df["Severity"] == "OK"])
        }
    }


# =========================================================
# DASHBOARD STATISTICS
# =========================================================
def api_get_dashboard_stats():
    """
    Get overall statistics from Excel data for the dashboard.
    Returns averages and baselines from historical batch data.
    
    Note: yield_score and performance_score are PCA-derived z-scores, not percentages.
    quality_score is a weighted combination of quality metrics.
    """
    from data_pipeline import build_pipeline
    import numpy as np
    
    df = build_pipeline()
    
    # Calculate baseline (median of all batches)
    baseline_quality = df["quality_score"].median()
    baseline_energy = df["total_energy"].median()
    
    # For yield: use Content_Uniformity as a proxy
    # It represents consistency of product (higher = better yield)
    baseline_yield = df["Content_Uniformity"].median()
    
    # For performance: calculate throughput efficiency
    # Performance = quality output per unit time (higher is better)
    # Normalize to 0-100 scale for realistic display
    df["performance_raw"] = (df["quality_score"] / df["total_process_time"])
    perf_min = df["performance_raw"].min()
    perf_max = df["performance_raw"].max()
    if perf_max > perf_min:
        df["performance_metric"] = ((df["performance_raw"] - perf_min) / (perf_max - perf_min)) * 100
    else:
        df["performance_metric"] = 50.0  # Default if no variation
    baseline_performance = df["performance_metric"].median()
    
    # Calculate CO2 from energy
    CO2_FACTOR = 0.82  # kg CO₂ per kWh
    baseline_co2 = baseline_energy * CO2_FACTOR
    
    # Calculate latest batch metrics (last 5 batches average)
    recent_df = df.tail(5)
    current_quality = recent_df["quality_score"].mean()
    current_yield = recent_df["Content_Uniformity"].mean()
    current_performance = recent_df["performance_metric"].mean()
    current_energy = recent_df["total_energy"].mean()
    current_co2 = current_energy * CO2_FACTOR
    
    # Calculate trends (percent change vs baseline)
    quality_trend = ((current_quality - baseline_quality) / baseline_quality) * 100 if baseline_quality != 0 else 0
    yield_trend = ((current_yield - baseline_yield) / baseline_yield) * 100 if baseline_yield != 0 else 0
    performance_trend = ((current_performance - baseline_performance) / baseline_performance) * 100 if baseline_performance != 0 else 0
    energy_trend = ((current_energy - baseline_energy) / baseline_energy) * 100 if baseline_energy != 0 else 0
    co2_trend = ((current_co2 - baseline_co2) / baseline_co2) * 100 if baseline_co2 != 0 else 0
    
    # Energy efficiency as a percentage (0-100)
    # Lower energy consumption = higher efficiency
    # Scale: efficiency = (1 - (current / max)) * 100, but use a normalized approach
    max_energy = df["total_energy"].max()
    min_energy = df["total_energy"].min()
    if max_energy > min_energy:
        # Invert so lower energy = higher score
        energy_efficiency = ((max_energy - current_energy) / (max_energy - min_energy)) * 100
    else:
        energy_efficiency = 50.0  # Default if no variation
    energy_efficiency = max(0, min(100, energy_efficiency))
    
    return {
        "current": {
            "quality": round(current_quality, 2),
            "yield": round(current_yield, 2),
            "performance": round(current_performance, 2),
            "energy": round(current_energy, 2),
            "co2": round(current_co2, 2),
            "energy_efficiency": round(energy_efficiency, 1)
        },
        "trends": {
            "quality": round(quality_trend, 1),
            "yield": round(yield_trend, 1),
            "performance": round(performance_trend, 1),
            "energy": round(energy_trend, 1),
            "co2": round(co2_trend, 1)
        },
        "baseline": {
            "quality": round(baseline_quality, 2),
            "yield": round(baseline_yield, 2),
            "performance": round(baseline_performance, 2),
            "energy": round(baseline_energy, 2),
            "co2": round(baseline_co2, 2)
        },
        "total_batches": len(df)
    }


# =========================================================
# ANOMALY DETECTION
# =========================================================
def api_get_anomalies():
    """
    Run anomaly detection on all batches using Isolation Forest.
    Returns anomaly scores, flags, and detailed batch information.
    """
    from data_pipeline import build_pipeline
    from anomaly_detection import detect_anomalies
    
    df = build_pipeline()
    anomalies_df = detect_anomalies(df, contamination=0.1)
    
    # Get anomalous batches
    anomalous = anomalies_df[anomalies_df["anomaly_flag"] == 1].copy()
    
    # Prepare detailed anomaly data
    anomaly_details = []
    for _, row in anomalous.iterrows():
        anomaly_details.append({
            "batch_id": row["Batch_ID"],
            "anomaly_score": float(row["anomaly_score"]),
            "risk_level": str(row["risk_level"]),
            "quality": float(row.get("quality_score", 0)),
            "yield": float(row.get("yield_score", 0)) * 100,
            "performance": float(row.get("performance_score", 0)) * 100,
            "energy": float(row.get("total_energy", 0)),
            "co2": float(row.get("total_energy", 0)) * 0.82
        })
    
    # Sort by anomaly score descending
    anomaly_details = sorted(anomaly_details, key=lambda x: x["anomaly_score"], reverse=True)
    
    # Get all batches with scores for visualization
    all_batches = []
    for _, row in anomalies_df.iterrows():
        all_batches.append({
            "batch_id": row["Batch_ID"],
            "anomaly_score": float(row["anomaly_score"]),
            "is_anomaly": int(row["anomaly_flag"]),
            "risk_level": str(row["risk_level"]),
            "quality": float(row.get("quality_score", 0)),
            "energy": float(row.get("total_energy", 0)),
            "content_uniformity": float(row.get("Content_Uniformity", 0)),
            "hardness": float(row.get("Hardness", 0))
        })
    
    return {
        "total_batches": len(df),
        "anomalous_count": len(anomalous),
        "contamination_rate": round((len(anomalous) / len(df)) * 100, 1),
        "anomalous_batches": anomaly_details,
        "all_batches": all_batches,
        "risk_distribution": {
            "high": int((anomalies_df["risk_level"] == "High").sum()),
            "medium": int((anomalies_df["risk_level"] == "Medium").sum()),
            "low": int((anomalies_df["risk_level"] == "Low").sum())
        }
    }


# =========================================================
# PRODUCTION TRENDS
# =========================================================
def api_get_production_trends():
    """
    Get time-series production trends for visualization.
    Returns quality, energy, and performance metrics over batches.
    """
    from data_pipeline import build_pipeline
    
    df = build_pipeline()
    
    # Sort by batch ID to ensure chronological order
    df = df.sort_values('Batch_ID').reset_index(drop=True)
    
    # Calculate performance metric (quality throughput)
    df['performance_metric_calc'] = (df['quality_score'] / df['total_process_time']) * 100000
    
    # Prepare trends data
    trends = []
    for idx, row in df.iterrows():
        trends.append({
            "batch_id": row["Batch_ID"],
            "batch_number": idx + 1,
            "quality": round(float(row["quality_score"]), 2),
            "energy": round(float(row["total_energy"]), 2),
            "performance": round(float(row["performance_metric_calc"]), 2),
            "content_uniformity": round(float(row["Content_Uniformity"]), 2),
            "co2": round(float(row["total_energy"]) * 0.82, 2)
        })
    
    return {
        "trends": trends,
        "total_batches": len(trends)
    }


# =========================================================
# REJECTION LOGGING
# =========================================================
def api_log_rejection(mode: str, cluster_id: int, proposed_metrics: dict,
                      reason: str = "User rejected", scenario_key=None):
    """
    Records a human rejection of a proposed golden update.
    Supports future decision re-use per PS requirement.
    """
    result = log_rejection(
        mode=mode,
        cluster_id=cluster_id,
        proposed_metrics=proposed_metrics,
        reason=reason,
        scenario_key=scenario_key
    )
    return result


def api_get_rejections():
    """Returns all logged rejection events, newest first."""
    return {"rejections": get_rejections()}


# =========================================================
# ASSET RELIABILITY
# =========================================================
def api_get_asset_reliability():
    """
    Returns per-batch asset reliability diagnosis including energy states,
    asset causes, and predictive maintenance actions.
    """
    from data_pipeline import build_pipeline
    from energy_intelligence import compute_energy_intelligence

    df = build_pipeline()
    df = compute_energy_intelligence(df)

    needed = ["Batch_ID", "reliability_state", "asset_cause", "maintenance_action",
              "energy_drift", "instability_score", "total_energy"]
    available = [c for c in needed if c in df.columns]

    rows = []
    for _, row in df[available].iterrows():
        rows.append({
            "batch_id": str(row.get("Batch_ID", "")),
            "reliability_state": str(row.get("reliability_state", "Unknown")),
            "asset_cause": str(row.get("asset_cause", "Normal operation")),
            "maintenance_action": str(row.get("maintenance_action", "No action required")),
            "energy_drift": round(float(row.get("energy_drift", 0)), 4),
            "instability_score": round(float(row.get("instability_score", 0)), 4),
            "total_energy": round(float(row.get("total_energy", 0)), 2),
        })

    state_counts = df["reliability_state"].value_counts().to_dict()
    return {
        "batches": rows,
        "summary": {
            "stable": int(state_counts.get("Stable", 0)),
            "efficiency_loss": int(state_counts.get("Efficiency Loss", 0)),
            "process_instability": int(state_counts.get("Process Instability", 0)),
            "calibration_gain": int(state_counts.get("Calibration Gain", 0)),
        }
    }