import json
import logging
import math
from pathlib import Path

from constants import CO2_FACTOR
from prediction_service import predict_batch
from optimizer_auto import optimize_auto
from optimizer_target import optimize_target
from optimizer_core import compute_pareto_front
from golden_updater import check_and_update_golden, _safe_load, SESSION_FILE, HISTORY_FILE, clear_session_and_archive, get_archive, log_rejection, get_rejections
from explainability_engine import get_global_feature_importance
from learning_controller import check_and_retrain

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
VERSION_LOG = MODEL_DIR / "model_versions.json"

# =========================================================
# SHARED EXCLUDED PARAMETERS
# Single source of truth — used by both SHAP and batch analysis.
# Contains z-scores, composite KPI scores, and columns that
# duplicate a controllable input (e.g. duration_* = *_Time).
# =========================================================
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

# =========================================================
# PREDICTION
# =========================================================
def api_predict(payload: dict):
    preds = predict_batch(payload)
    return {"prediction": preds}


# =========================================================
# AUTO OPTIMIZATION
# =========================================================
def _sanitize(d: dict) -> dict:
    """Replace NaN/Inf with None so JSON serialization never fails."""
    return {k: (None if isinstance(v, float) and not math.isfinite(v) else v)
            for k, v in d.items()}


def api_optimize_auto(mode="balanced", custom_weights=None):

    results, proposal, cluster_id, scenario_key = optimize_auto(
        mode=mode,
        custom_weights=custom_weights
    )

    if results is None:
        return {"status": "no_solution"}

    pareto_df = compute_pareto_front(results)
    pareto_ids = set(pareto_df.index.tolist()) if pareto_df is not None else set()

    all_results = [_sanitize(row.to_dict()) for _, row in results.iterrows()]
    pareto_front = [_sanitize(row.to_dict()) for _, row in pareto_df.iterrows()] if pareto_df is not None else []
    best = _sanitize(results.iloc[0].to_dict())

    return {
        "status": "success",
        "top_result": best,
        "all_results": all_results,
        "pareto_front": pareto_front,
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

    pareto_df = compute_pareto_front(results)
    all_results = [_sanitize(row.to_dict()) for _, row in results.iterrows()]
    pareto_front = [_sanitize(row.to_dict()) for _, row in pareto_df.iterrows()] if pareto_df is not None else []

    return {
        "status": "success",
        "best_solution": _sanitize(results.iloc[0].to_dict()),
        "all_results": all_results,
        "pareto_front": pareto_front,
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

    # Record decision for future audit / learning
    try:
        from decision_engine import log_decision
        metrics = {k: best_row.get(k, 0) for k in ("Quality", "Yield", "Performance", "Energy", "CO2", "Score")}
        log_decision(
            mode=mode,
            cluster_id=int(cluster_id),
            engine="user_accept",
            weights={},
            decision="ACCEPTED",
            reason="User accepted golden signature update",
            best_metrics=metrics,
        )
    except Exception:
        logger.warning("Could not log accept decision to decision_engine", exc_info=True)

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
AGGREGATE_METRICS_FILE = MODEL_DIR / "model_aggregate_metrics.json"


def _ensure_version_log():
    """
    Called once at startup. If model.pkl exists but model_versions.json
    does not, synthesise a v1 entry from model_aggregate_metrics.json
    (written by every train_and_save_model call) or fall back to the
    per-target model_metrics.json.
    """
    if VERSION_LOG.exists():
        return

    MODEL_FILE = MODEL_DIR / "model.pkl"
    if not MODEL_FILE.exists():
        return  # no model trained yet – nothing to backfill

    entry = {
        "time": None,
        "reason": {"initial_training": True},
        "metrics": {"mae": None, "rmse": None, "r2": None, "mape": None},
        "dataset_size": None,
        "model_version": 1,
    }

    # Prefer the aggregate file (all four metrics available)
    if AGGREGATE_METRICS_FILE.exists():
        try:
            with open(AGGREGATE_METRICS_FILE, "r") as f:
                agg = json.load(f)
            entry["metrics"] = {
                "mae":  round(float(agg["mae"]),  6),
                "rmse": round(float(agg["rmse"]), 6),
                "r2":   round(float(agg["r2"]),   6),
                "mape": round(float(agg["mape"]), 6),
            }
        except Exception:
            logger.warning("Could not read model_aggregate_metrics.json for backfill", exc_info=True)

    # Fall back to per-target file (only mae + r2)
    elif (MODEL_DIR / "model_metrics.json").exists():
        try:
            with open(MODEL_DIR / "model_metrics.json", "r") as f:
                per_target = json.load(f)
            maes = [v["mae"] for v in per_target.values() if "mae" in v]
            r2s  = [v["r2"]  for v in per_target.values() if "r2"  in v]
            if maes:
                entry["metrics"]["mae"] = round(float(sum(maes) / len(maes)), 6)
            if r2s:
                entry["metrics"]["r2"]  = round(float(sum(r2s)  / len(r2s)),  6)
        except Exception:
            logger.warning("Could not read model_metrics.json for backfill", exc_info=True)

    VERSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(VERSION_LOG, "w") as f:
        json.dump([entry], f, indent=2)
    logger.info("Governance: backfilled model_versions.json (v1 from existing model)")


def api_get_model_history():
    if VERSION_LOG.exists():
        with open(VERSION_LOG, "r") as f:
            return json.load(f)
    return []


# =========================================================
# FEATURE IMPORTANCE
# =========================================================
def api_get_feature_importance():
    df = get_global_feature_importance()
    if df is None:
        return {"status": "no_data"}
    # Remove redundant/derived features using shared EXCLUDED_PARAMS constant
    df = df[~df["feature"].isin(EXCLUDED_PARAMS)].reset_index(drop=True)
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
        "golden_registry_exists": SESSION_FILE.exists(),
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
    
    # Determine context cluster using the persisted cluster model —
    # avoids refitting KMeans on the full dataset on every request.
    CLUSTER_FILE = MODEL_DIR / "context_cluster.pkl"
    SCALER_FILE  = MODEL_DIR / "context_scaler.pkl"
    CONTEXT_FEATURES = ["Batch_Size", "Machine_Speed", "Compression_Force",
                        "avg_temperature", "avg_pressure"]

    current_cluster = 1  # default
    try:
        if CLUSTER_FILE.exists() and SCALER_FILE.exists():
            scaler  = joblib.load(SCALER_FILE)
            kmeans  = joblib.load(CLUSTER_FILE)
            avail   = [f for f in CONTEXT_FEATURES if f in batch_data.columns]
            if len(avail) >= 2:
                X_row = batch_data[avail].fillna(batch_data[avail].median())
                X_scaled = scaler.transform(X_row)
                current_cluster = int(kmeans.predict(X_scaled)[0])
        else:
            # Persisted model not available — fall back to dataset-wide mode
            from context_engine import assign_context_clusters
            df_clustered, _ = assign_context_clusters(df)
            current_cluster = int(df_clustered["context_cluster"].mode()[0])
    except Exception:
        logger.warning("Could not determine context cluster for batch %s; using default 1", batch_id)
        current_cluster = 1
    
    # Identify golden signatures and ranges from historical top performers
    _, golden_ranges, _ = identify_golden_signatures(
        df,
        mode="balanced",
        cluster_id=current_cluster,
        custom_weights=None
    )
    
    if not golden_ranges or len(golden_ranges) == 0:
        return {
            "status": "error",
            "message": "Could not compute golden ranges from historical data. Need at least 10 batches."
        }
    
    # Filter out non-actionable parameters using shared constant
    golden_ranges = {k: v for k, v in golden_ranges.items() if k not in EXCLUDED_PARAMS}

    # Load model and features for impact prediction
    model = None
    feature_cols = None
    
    try:
        model = joblib.load(MODEL_DIR / "model.pkl")
        feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")
    except Exception as e:
        logger.warning("Could not load model for batch analysis: %s", e)
    
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
    Returns dataset-wide averages across ALL batches as the headline numbers.
    Trend shows how the most recent 20% of batches compare to the overall mean.

    Note: yield_score and performance_score are PCA-derived z-scores, not percentages.
    quality_score is a weighted combination of quality metrics.
    """
    from data_pipeline import build_pipeline
    import numpy as np

    df = build_pipeline()
    n = len(df)

    # ------------------------------------------------------------------
    # Performance metric: normalise quality/time to 0-100 across ALL batches
    # ------------------------------------------------------------------
    df["performance_raw"] = df["quality_score"] / df["total_process_time"]
    perf_min = df["performance_raw"].min()
    perf_max = df["performance_raw"].max()
    if perf_max > perf_min:
        df["performance_metric"] = ((df["performance_raw"] - perf_min) / (perf_max - perf_min)) * 100
    else:
        df["performance_metric"] = 50.0

    # ------------------------------------------------------------------
    # HEADLINE METRICS — mean across every batch in the dataset
    # ------------------------------------------------------------------
    current_quality     = df["quality_score"].mean()
    current_yield       = df["Content_Uniformity"].mean()
    current_performance = df["performance_metric"].mean()
    current_energy      = df["total_energy"].mean()
    current_co2         = current_energy * CO2_FACTOR

    # ------------------------------------------------------------------
    # BASELINE — first 80% of batches (chronological anchor)
    # ------------------------------------------------------------------
    cutoff = max(1, int(n * 0.8))
    baseline_df = df.iloc[:cutoff]

    baseline_quality     = baseline_df["quality_score"].mean()
    baseline_yield       = baseline_df["Content_Uniformity"].mean()
    baseline_performance = baseline_df["performance_metric"].mean()
    baseline_energy      = baseline_df["total_energy"].mean()
    baseline_co2         = baseline_energy * CO2_FACTOR

    # ------------------------------------------------------------------
    # TREND — most recent 20% of batches vs the baseline above
    # This answers: "is the dataset improving or declining recently?"
    # ------------------------------------------------------------------
    recent_df = df.iloc[cutoff:]
    if len(recent_df) > 0:
        recent_quality     = recent_df["quality_score"].mean()
        recent_yield       = recent_df["Content_Uniformity"].mean()
        recent_performance = recent_df["performance_metric"].mean()
        recent_energy      = recent_df["total_energy"].mean()
        recent_co2         = recent_energy * CO2_FACTOR
    else:
        recent_quality = current_quality
        recent_yield = current_yield
        recent_performance = current_performance
        recent_energy = current_energy
        recent_co2 = current_co2

    def pct_change(recent, base):
        return round(((recent - base) / base) * 100, 1) if base != 0 else 0.0

    quality_trend     = pct_change(recent_quality,     baseline_quality)
    yield_trend       = pct_change(recent_yield,       baseline_yield)
    performance_trend = pct_change(recent_performance, baseline_performance)
    energy_trend      = pct_change(recent_energy,      baseline_energy)
    co2_trend         = pct_change(recent_co2,         baseline_co2)

    # ------------------------------------------------------------------
    # ENERGY EFFICIENCY: how close to the best-ever batch (0-100%)
    # ------------------------------------------------------------------
    max_energy = df["total_energy"].max()
    min_energy = df["total_energy"].min()
    if max_energy > min_energy:
        energy_efficiency = ((max_energy - current_energy) / (max_energy - min_energy)) * 100
    else:
        energy_efficiency = 50.0
    energy_efficiency = max(0.0, min(100.0, energy_efficiency))

    return {
        "current": {
            "quality":           round(current_quality, 2),
            "yield":             round(current_yield, 2),
            "performance":       round(current_performance, 2),
            "energy":            round(current_energy, 2),
            "co2":               round(current_co2, 2),
            "energy_efficiency": round(energy_efficiency, 1),
        },
        "trends": {
            "quality":     quality_trend,
            "yield":       yield_trend,
            "performance": performance_trend,
            "energy":      energy_trend,
            "co2":         co2_trend,
        },
        "baseline": {
            "quality":     round(baseline_quality, 2),
            "yield":       round(baseline_yield, 2),
            "performance": round(baseline_performance, 2),
            "energy":      round(baseline_energy, 2),
            "co2":         round(baseline_co2, 2),
        },
        "total_batches": n,
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
            "co2": float(row.get("total_energy", 0)) * CO2_FACTOR
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
            "co2": round(float(row["total_energy"]) * CO2_FACTOR, 2)
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