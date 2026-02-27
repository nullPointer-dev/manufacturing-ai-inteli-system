"""
FastAPI Backend Server for Manufacturing AI Frontend Integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

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
        "http://localhost:3000",
        "http://127.0.0.1:5173",
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

class AcceptGoldenRequest(BaseModel):
    best_row: Dict[str, float]
    mode: str
    cluster_id: int
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
            mode=request.mode
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
        if result.get("status") == "no_data":
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
        port=8000,
        log_level="info"
    )
