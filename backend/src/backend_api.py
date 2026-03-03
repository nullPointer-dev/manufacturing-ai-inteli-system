"""
FastAPI Backend Server for Manufacturing AI Frontend Integration
"""
import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Literal
import sys
from pathlib import Path
import shutil
import os

logger = logging.getLogger(__name__)

# Add backend/src to path (backend_api.py is in src, so parent is src)
sys.path.insert(0, str(Path(__file__).parent))

from integration_api import (
    api_predict,
    api_optimize_auto,
    api_optimize_target,
    api_accept_golden,
    api_get_golden,
    api_get_golden_archive,
    api_clear_session,
    api_get_model_history,
    api_get_feature_importance,
    api_check_retrain,
    api_system_status,
    api_get_batches,
    api_analyze_batch,
    api_get_dashboard_stats,
    api_get_anomalies,
    api_get_production_trends,
    api_log_rejection,
    api_get_rejections,
    api_get_asset_reliability,
)
from golden_updater import _safe_load, HISTORY_FILE
from industrial_validation import calculate_industrial_validation
from data_pipeline import invalidate_pipeline_cache, classify_excel_file


# =========================================================
# HELPERS
# =========================================================
def _http_error(exc: Exception, status_code: int = 500) -> HTTPException:
    """Log the real error server-side; return a safe message to the client."""
    logger.exception("API error: %s", exc)
    return HTTPException(status_code=status_code, detail="An internal server error occurred.")

# =========================================================
# Lifespan (replaces deprecated @app.on_event)
# =========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 60)
    logger.info("Manufacturing AI Intelligence API - Server Starting")
    logger.info("=" * 60)
    logger.info("API Documentation: http://localhost:8001/docs")
    logger.info("Alternative docs:  http://localhost:8001/redoc")
    logger.info("Frontend URL:      http://localhost:5173")
    logger.info("API Base:          http://localhost:8001/api")
    logger.info("=" * 60)
    # Ensure the governance version log exists for any already-trained model
    from integration_api import _ensure_version_log
    _ensure_version_log()
    yield
    # Shutdown (nothing to clean up)

app = FastAPI(
    title="Manufacturing AI Intelligence API",
    description="Backend API for AI-driven batch optimization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# Request/Response Models
# =========================================================

class PredictionRequest(BaseModel):
    data: Dict[str, Any]

class OptimizeAutoRequest(BaseModel):
    mode: Literal['balanced', 'eco', 'quality', 'yield', 'performance', 'custom'] = 'balanced'
    custom_weights: Optional[Dict[str, float]] = None

class OptimizeTargetRequest(BaseModel):
    required_reduction: Optional[float] = None
    min_quality: Optional[float] = None
    min_yield: Optional[float] = None
    min_performance: Optional[float] = None
    mode: Literal['balanced', 'eco', 'quality', 'yield', 'performance', 'custom'] = "balanced"
    custom_weights: Optional[Dict[str, float]] = None

class AcceptGoldenRequest(BaseModel):
    best_row: Dict[str, float]
    mode: str
    cluster_id: int
    scenario_key: Optional[str] = None

class RejectGoldenRequest(BaseModel):
    mode: str
    cluster_id: int
    proposed_metrics: Dict[str, float]
    reason: str = "User rejected"
    scenario_key: Optional[str] = None

class IndustrialValidationRequest(BaseModel):
    electricity_cost: float = 0.12  # cost per kWh (currency matches frontend display)
    batches_per_day: float = 10.0
    deployment_cost: float = 50000.0  # one-time
    annual_maintenance_cost: float = 5000.0  # per year
    operating_days_per_year: int = 250
    current_batch_params: Optional[Dict[str, Any]] = None

# =========================================================
# API Routes
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Manufacturing AI Intelligence API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/predict")
def predict(request: PredictionRequest):
    """Real-time batch prediction"""
    try:
        return api_predict(request.data)
    except Exception as e:
        raise _http_error(e)

@app.post("/api/optimize_auto")
def optimize_auto(request: OptimizeAutoRequest):
    """Automatic optimization"""
    try:
        return api_optimize_auto(request.mode, request.custom_weights)
    except Exception as e:
        raise _http_error(e)

@app.post("/api/optimize_target")
def optimize_target(request: OptimizeTargetRequest):
    """Target-based optimization with constraints"""
    try:
        return api_optimize_target(
            required_reduction=request.required_reduction,
            min_quality=request.min_quality,
            min_yield=request.min_yield,
            min_performance=request.min_performance,
            mode=request.mode,
            custom_weights=request.custom_weights,
        )
    except Exception as e:
        raise _http_error(e)

@app.post("/api/accept_golden")
def accept_golden(request: AcceptGoldenRequest):
    """Accept golden signature update"""
    try:
        return api_accept_golden(
            request.best_row,
            request.mode,
            request.cluster_id,
            request.scenario_key
        )
    except Exception as e:
        raise _http_error(e)

@app.post("/api/reject_golden")
def reject_golden(request: RejectGoldenRequest):
    """Log a human rejection of a proposed golden signature update"""
    try:
        return api_log_rejection(
            mode=request.mode,
            cluster_id=request.cluster_id,
            proposed_metrics=request.proposed_metrics,
            reason=request.reason,
            scenario_key=request.scenario_key
        )
    except Exception as e:
        raise _http_error(e)

@app.get("/api/rejection_history")
def get_rejection_history():
    """Get all logged human rejection events"""
    try:
        return api_get_rejections()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/asset_reliability")
def get_asset_reliability():
    """Get per-batch asset reliability and predictive maintenance diagnosis"""
    try:
        return api_get_asset_reliability()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/golden")
def get_golden():
    """Get golden registry"""
    try:
        return api_get_golden()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/golden_history")
def get_golden_history():
    """Get golden update history"""
    try:
        history = _safe_load(HISTORY_FILE, [])
        return history
    except Exception as e:
        raise _http_error(e)

@app.get("/api/golden_archive")
def get_golden_archive():
    """Get all archived golden signatures from previous sessions"""
    try:
        return api_get_golden_archive()
    except Exception as e:
        raise _http_error(e)

@app.post("/api/clear_session")
def clear_session():
    """Clear current session and archive golden signatures"""
    try:
        return api_clear_session()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/model_history")
def get_model_history():
    """Get model version history"""
    try:
        return api_get_model_history()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/feature_importance")
def get_feature_importance():
    """Get feature importance"""
    try:
        result = api_get_feature_importance()
        if isinstance(result, dict) and result.get("status") == "no_data":
            return []
        return result
    except Exception as e:
        raise _http_error(e)

@app.post("/api/check_retrain")
async def check_retrain():
    """Check for drift and retrain if needed (runs in thread pool to avoid blocking)."""
    try:
        result = await run_in_threadpool(api_check_retrain)
        return result
    except Exception as e:
        raise _http_error(e)

@app.get("/api/system_status")
def system_status():
    """Get system status"""
    try:
        return api_system_status()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/batches")
def get_batches():
    """Get list of all available batches"""
    try:
        return api_get_batches()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/batch/{batch_id}/analyze")
def analyze_batch(batch_id: str):
    """Analyze a specific batch against golden ranges"""
    try:
        return api_analyze_batch(batch_id)
    except Exception as e:
        raise _http_error(e)

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """Get dashboard statistics from historical batch data"""
    try:
        return api_get_dashboard_stats()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/anomalies")
def get_anomalies():
    """Get anomaly detection results using Isolation Forest"""
    try:
        return api_get_anomalies()
    except Exception as e:
        raise _http_error(e)

@app.get("/api/production/trends")
def get_production_trends():
    """Get production performance trends over time"""
    try:
        return api_get_production_trends()
    except Exception as e:
        raise _http_error(e)

@app.post("/api/industrial_validation")
def industrial_validation(request: IndustrialValidationRequest):
    """
    Calculate industrial validation metrics including ROI, payback period,
    CO2 savings, and energy efficiency based on real-time predictions
    and correction engine simulations.
    """
    try:
        result = calculate_industrial_validation(
            electricity_cost=request.electricity_cost,
            batches_per_day=request.batches_per_day,
            deployment_cost=request.deployment_cost,
            annual_maintenance_cost=request.annual_maintenance_cost,
            current_batch_params=request.current_batch_params,
            operating_days_per_year=request.operating_days_per_year,
        )
        return result
    except Exception as e:
        raise _http_error(e)

# =========================================================
# Data File Management Routes
# =========================================================

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@app.get("/api/data-files")
def get_data_files():
    """Get list of current data files being used"""
    try:
        files = []
        for file_path in DATA_DIR.glob("*.xlsx"):
            file_stat = file_path.stat()
            files.append({
                "name": file_path.name,
                "size": file_stat.st_size,
                "modified": file_stat.st_mtime
            })
        return {"files": files}
    except Exception as e:
        raise _http_error(e)

@app.get("/api/data-files/{filename}")
def download_data_file(filename: str):
    """Download a specific data file"""
    try:
        # Security: only allow downloading xlsx files and prevent path traversal
        if not filename.endswith('.xlsx') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Only .xlsx files can be downloaded")
        
        file_path = DATA_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise _http_error(e)

def _upload_sync_worker(
    content1: bytes, content2: bytes,
    filename1: str, filename2: str,
) -> dict:
    """
    All CPU/IO-bound work for a file upload: classification, file copy, pipeline
    rebuild, and model retrain.  Runs inside run_in_threadpool so the event
    loop is never blocked.
    """
    upload_id = uuid.uuid4().hex
    backup_dir = DATA_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    temp_dir = DATA_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)

    temp_file1 = temp_dir / f"temp1_{upload_id}.xlsx"
    temp_file2 = temp_dir / f"temp2_{upload_id}.xlsx"

    # Write raw bytes to temporary paths
    temp_file1.write_bytes(content1)
    temp_file2.write_bytes(content2)

    # Backup existing data files so we can roll back on error
    for old_file in DATA_DIR.glob("*.xlsx"):
        backup_path = backup_dir / f"{old_file.stem}_{upload_id}{old_file.suffix}"
        shutil.copy2(old_file, backup_path)

    def _cleanup_temp():
        for f in (temp_file1, temp_file2):
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

    # --- Classify -------------------------------------------------------
    try:
        type1 = classify_excel_file(temp_file1)
        type2 = classify_excel_file(temp_file2)
    except Exception as e:
        _cleanup_temp()
        logger.exception("File classification failed: %s", e)
        raise HTTPException(
            status_code=400,
            detail="File classification failed. Ensure one production and one process file are uploaded.",
        )

    if type1 == type2:
        _cleanup_temp()
        raise HTTPException(
            status_code=400,
            detail=f"Both files appear to be {type1} data. Please upload one production and one process file.",
        )

    if type1 == "production":
        production_temp, process_temp = temp_file1, temp_file2
        production_filename, process_filename = filename1, filename2
    else:
        production_temp, process_temp = temp_file2, temp_file1
        production_filename, process_filename = filename2, filename1

    # --- Copy to canonical paths ----------------------------------------
    try:
        shutil.copy2(str(production_temp), str(DATA_DIR / "batch_production_data.xlsx"))
        shutil.copy2(str(process_temp),    str(DATA_DIR / "batch_process_data.xlsx"))
    finally:
        _cleanup_temp()

    # --- Reload system --------------------------------------------------
    try:
        from data_pipeline import build_pipeline
        from train_model import train_and_save_model

        invalidate_pipeline_cache()
        model_dir = Path(__file__).resolve().parent.parent / "models"
        for stale_file in ["model_versions.json", "golden_session.json", "drift_baseline.json", "scaling_params.json"]:
            stale_path = model_dir / stale_file
            if stale_path.exists():
                stale_path.unlink()

        df = build_pipeline()
        train_and_save_model()

        return {
            "success": True,
            "message": "Files uploaded and system reloaded successfully",
            "production_file": production_filename,
            "process_file": process_filename,
            "batches_loaded": len(df),
            "classified_as": {filename1: type1, filename2: type2},
        }
    except Exception as e:
        # Restore backups
        for backup_file in backup_dir.glob(f"*_{upload_id}.xlsx"):
            original_name = backup_file.name.replace(f"_{upload_id}", "")
            shutil.copy2(backup_file, DATA_DIR / original_name)
        invalidate_pipeline_cache()
        logger.exception("Failed to reload system with new data: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Files uploaded but system reload failed. Previous data has been restored.",
        )


@app.post("/api/data-files/upload")
async def upload_data_files(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    """Upload new data files - automatically classifies production vs process data"""
    try:
        if not file1.filename.endswith(".xlsx"):
            raise HTTPException(status_code=400, detail="First file must be .xlsx")
        if not file2.filename.endswith(".xlsx"):
            raise HTTPException(status_code=400, detail="Second file must be .xlsx")

        # Read file contents in the async context; all subsequent heavy work
        # is handed off to a thread so the event loop is never blocked.
        content1 = await file1.read()
        content2 = await file2.read()

        return await run_in_threadpool(
            _upload_sync_worker,
            content1, content2,
            file1.filename, file2.filename,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise _http_error(e)

# =========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
