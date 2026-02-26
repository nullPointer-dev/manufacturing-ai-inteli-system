import json
from pathlib import Path

from prediction_service import predict_batch
from optimizer_auto import optimize_auto
from optimizer_target import optimize_target
from golden_updater import check_and_update_golden
from explainability_engine import get_global_feature_importance
from learning_controller import check_and_retrain

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
VERSION_LOG = MODEL_DIR / "model_versions.json"
REG_FILE = MODEL_DIR / "golden_registry.json"

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
                        mode="balanced"):

    results = optimize_target(
        required_reduction=required_reduction,
        min_quality=min_quality,
        min_yield=min_yield,
        min_performance=min_performance,
        mode=mode
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
# GET GOLDEN REGISTRY
# =========================================================
def api_get_golden():
    if not REG_FILE.exists():
        return {}

    try:
        with open(REG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


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
def api_get_feature_importance():
    df = get_global_feature_importance()
    if df is None:
        return {"status": "no_data"}
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
        "golden_registry_exists": REG_FILE.exists(),
        "version_log_exists": VERSION_LOG.exists()
    }