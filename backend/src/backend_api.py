"""
FastAPI Backend Server for Manufacturing AI Frontend Integration
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path
import shutil
import os

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

app = FastAPI(
    title="Manufacturing AI Intelligence API",
    description="Backend API for AI-driven batch optimization",
    version="1.0.0"
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
    mode: str
    custom_weights: Optional[Dict[str, float]] = None

class OptimizeTargetRequest(BaseModel):
    required_reduction: Optional[float] = None
    min_quality: Optional[float] = None
    min_yield: Optional[float] = None
    min_performance: Optional[float] = None
    mode: str = "balanced"
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize_auto")
def optimize_auto(request: OptimizeAutoRequest):
    """Automatic optimization"""
    try:
        print(f"Received optimize_auto request: mode={request.mode}, custom_weights={request.custom_weights}")
        result = api_optimize_auto(request.mode, request.custom_weights)
        print(f"Optimization result: {result}")
        return result
    except Exception as e:
        print(f"Optimization error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rejection_history")
def get_rejection_history():
    """Get all logged human rejection events"""
    try:
        return api_get_rejections()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/asset_reliability")
def get_asset_reliability():
    """Get per-batch asset reliability and predictive maintenance diagnosis"""
    try:
        return api_get_asset_reliability()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/golden")
def get_golden():
    """Get golden registry"""
    try:
        return api_get_golden()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/golden_history")
def get_golden_history():
    """Get golden update history"""
    try:
        history = _safe_load(HISTORY_FILE, [])
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/golden_archive")
def get_golden_archive():
    """Get all archived golden signatures from previous sessions"""
    try:
        return api_get_golden_archive()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear_session")
def clear_session():
    """Clear current session and archive golden signatures"""
    try:
        return api_clear_session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model_history")
def get_model_history():
    """Get model version history"""
    try:
        return api_get_model_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feature_importance")
def get_feature_importance():
    """Get feature importance"""
    try:
        result = api_get_feature_importance()
        if isinstance(result, dict) and result.get("status") == "no_data":
            return []
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check_retrain")
def check_retrain():
    """Check for drift and retrain if needed"""
    try:
        return api_check_retrain()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system_status")
def system_status():
    """Get system status"""
    try:
        return api_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/batches")
def get_batches():
    """Get list of all available batches"""
    try:
        return api_get_batches()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/batch/{batch_id}/analyze")
def analyze_batch(batch_id: str):
    """Analyze a specific batch against golden ranges"""
    try:
        return api_analyze_batch(batch_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """Get dashboard statistics from historical batch data"""
    try:
        return api_get_dashboard_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/anomalies")
def get_anomalies():
    """Get anomaly detection results using Isolation Forest"""
    try:
        return api_get_anomalies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/production/trends")
def get_production_trends():
    """Get production performance trends over time"""
    try:
        return api_get_production_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data-files/{filename}")
def download_data_file(filename: str):
    """Download a specific data file"""
    try:
        # Security: only allow downloading xlsx files
        if not filename.endswith('.xlsx'):
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
        raise HTTPException(status_code=500, detail=str(e))

def classify_excel_file(file_path: Path) -> str:
    """
    Classify an Excel file as either 'production' or 'process' based on its structure.
    
    Process files have:
    - Multiple sheets (one per batch, named like "Batch_*")
    - Columns: Time_Minutes, Phase, Temperature_C, etc.
    
    Production files have:
    - Single sheet (or fewer sheets)
    - Columns: Granulation_Time, Binder_Amount, Drying_Temp, etc.
    """
    import pandas as pd
    
    try:
        # Read all sheet names - use context manager to ensure file is closed
        with pd.ExcelFile(file_path) as xl_file:
            sheet_names = xl_file.sheet_names
            
            # Process files typically have multiple sheets (one per batch)
            if len(sheet_names) > 3:
                # Check if sheets are named like "Batch_*"
                batch_sheets = [s for s in sheet_names if s.startswith('Batch_') or 'batch' in s.lower()]
                if len(batch_sheets) > 2:
                    return 'process'
            
            # Read first sheet to check columns
            first_sheet = pd.read_excel(xl_file, sheet_name=0)
            columns = set(first_sheet.columns)
        
        # Process data indicators
        process_indicators = {'Time_Minutes', 'Phase', 'Temperature_C', 'Pressure_Bar', 'Power_Consumption_kW'}
        
        # Production data indicators
        production_indicators = {'Granulation_Time', 'Binder_Amount', 'Drying_Temp', 'Compression_Force', 'Machine_Speed'}
        
        # Count how many indicators match
        process_matches = len(process_indicators.intersection(columns))
        production_matches = len(production_indicators.intersection(columns))
        
        if process_matches > production_matches:
            return 'process'
        elif production_matches > process_matches:
            return 'production'
        
        # Fallback: if multiple sheets, likely process data
        if len(sheet_names) > 1:
            return 'process'
        else:
            return 'production'
            
    except Exception as e:
        raise Exception(f"Failed to classify file {file_path}: {str(e)}")

@app.post("/api/data-files/upload")
async def upload_data_files(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """Upload new data files - automatically classifies production vs process data"""
    try:
        # Validate file types
        if not file1.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="First file must be .xlsx")
        if not file2.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Second file must be .xlsx")
        
        # Create backup of old files
        backup_dir = DATA_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        import time
        timestamp = int(time.time())
        
        for old_file in DATA_DIR.glob("*.xlsx"):
            backup_path = backup_dir / f"{old_file.stem}_{timestamp}{old_file.suffix}"
            shutil.copy2(old_file, backup_path)
        
        # Save files temporarily to classify them
        temp_dir = DATA_DIR / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file1 = temp_dir / f"temp1_{timestamp}.xlsx"
        temp_file2 = temp_dir / f"temp2_{timestamp}.xlsx"
        
        # Write temporary files
        with open(temp_file1, "wb") as f:
            content = await file1.read()
            f.write(content)
        
        with open(temp_file2, "wb") as f:
            content = await file2.read()
            f.write(content)
        
        # Classify the files
        try:
            type1 = classify_excel_file(temp_file1)
            type2 = classify_excel_file(temp_file2)
            
            # Force garbage collection to release file handles
            import gc
            gc.collect()
            
            # Ensure we have one of each type
            if type1 == type2:
                # Clean up temp files
                temp_file1.unlink()
                temp_file2.unlink()
                raise HTTPException(
                    status_code=400, 
                    detail=f"Both files appear to be {type1} data. Please upload one production and one process file."
                )
            
            # Determine which is which
            if type1 == 'production':
                production_temp = temp_file1
                process_temp = temp_file2
                production_filename = file1.filename
                process_filename = file2.filename
            else:
                production_temp = temp_file2
                process_temp = temp_file1
                production_filename = file2.filename
                process_filename = file1.filename
            
            # Save to final locations with standard names
            production_path = DATA_DIR / "batch_production_data.xlsx"
            process_path = DATA_DIR / "batch_process_data.xlsx"
            
            # Use copy instead of move to avoid file locking issues
            shutil.copy2(str(production_temp), str(production_path))
            shutil.copy2(str(process_temp), str(process_path))
            
            # Clean up temp files
            production_temp.unlink()
            process_temp.unlink()
            
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                
        except HTTPException:
            raise
        except Exception as e:
            # Force garbage collection before cleanup
            import gc
            gc.collect()
            
            # Clean up temp files on error
            try:
                if temp_file1.exists():
                    temp_file1.unlink()
                if temp_file2.exists():
                    temp_file2.unlink()
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception:
                pass  # Ignore cleanup errors
            
            raise HTTPException(
                status_code=500,
                detail=f"File classification failed: {str(e)}"
            )
        
        # Reload the system with new data
        try:
            from data_pipeline import build_pipeline
            from train_model import train_and_save_model

            # --- Reset stale governance state from the old dataset ---
            model_dir = Path(__file__).resolve().parent.parent / "models"
            for stale_file in ["model_versions.json", "golden_session.json", "drift_baseline.json"]:
                stale_path = model_dir / stale_file
                if stale_path.exists():
                    stale_path.unlink()

            # Rebuild data pipeline
            df = build_pipeline()
            
            # Retrain models
            train_and_save_model()
            
            return {
                "success": True,
                "message": "Files uploaded and system reloaded successfully",
                "production_file": production_filename,
                "process_file": process_filename,
                "batches_loaded": len(df),
                "classified_as": {
                    file1.filename: type1,
                    file2.filename: type2
                }
            }
        except Exception as e:
            # If loading fails, restore backups
            for backup_file in backup_dir.glob(f"*_{timestamp}.xlsx"):
                original_name = backup_file.name.replace(f"_{timestamp}", "")
                original_path = DATA_DIR / original_name
                shutil.copy2(backup_file, original_path)
            
            raise HTTPException(
                status_code=500,
                detail=f"Failed to reload system with new data: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# Startup Event
# =========================================================

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("Manufacturing AI Intelligence API - Server Starting")
    print("=" * 60)
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Alternative docs: http://localhost:8000/redoc")
    print(f"Frontend URL: http://localhost:5173")
    print(f"API Base: http://localhost:8000/api")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
