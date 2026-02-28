# 🚀 Manufacturing AI Intelligence System - Complete Setup Guide

## Project Overview

This is a production-grade AI-driven manufacturing intelligence system featuring:
- **Track B (Primary)**: Multi-objective optimization with golden signature management
- **Track A (Secondary)**: Predictive modeling and energy pattern intelligence
- **Frontend**: React 18 + TypeScript with industrial control room UI
- **Backend**: Python with FastAPI + integration layer

---

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install Python dependencies
pip install -r ../requirements.txt

# Train initial model (required)
python src/train_model.py

# Start FastAPI server
python src/backend_api.py
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:3000
```

---

## Architecture

### Backend Structure
```
backend/
├── data/                    # Excel data files
├── models/                  # Trained models & registries
│   ├── model.pkl
│   ├── feature_columns.pkl
│   ├── golden_registry.json
│   ├── golden_history.json
│   ├── model_metrics.json
│   └── model_versions.json
└── src/
    ├── backend_api.py      # FastAPI server
    ├── train_model.py      # Model training
    ├── prediction_service.py
    ├── optimizer_nsga2.py   # NSGA-II engine
    ├── golden_signature.py  # Golden framework
    ├── energy_intelligence.py
    ├── anomaly_detection.py
    └── ... (15+ modules)
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── dashboard/      # KPI cards, gauges, timelines
│   │   ├── layout/         # Sidebar, header
│   │   └── ui/             # Shadcn/ui components
│   ├── pages/              # 7 main pages
│   ├── store/              # Zustand stores
│   ├── lib/                # API client & utilities
│   └── types/              # TypeScript definitions
└── external_ui_assets/     # Animated components
```

---

## Backend API Integration

### Required: FastAPI Server

Create `backend/backend_api.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from integration_api import *

app = FastAPI(title="Manufacturing AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict")
def predict(payload: dict):
    return api_predict(payload)

@app.post("/api/optimize_auto")
def optimize_auto(mode: str, custom_weights: dict = None):
    return api_optimize_auto(mode, custom_weights)

@app.post("/api/optimize_target")
def optimize_target(**kwargs):
    return api_optimize_target(**kwargs)

@app.post("/api/accept_golden")
def accept_golden(best_row: dict, mode: str, cluster_id: int, scenario_key: str = None):
    return api_accept_golden(best_row, mode, cluster_id, scenario_key)

@app.get("/api/golden")
def get_golden():
    return api_get_golden()

@app.get("/api/golden_history")
def get_golden_history():
    # Implement: load golden_history.json
    pass

@app.get("/api/model_history")
def get_model_history():
    return api_get_model_history()

@app.get("/api/feature_importance")
def get_feature_importance():
    return api_get_feature_importance()

@app.post("/api/check_retrain")
def check_retrain():
    return api_check_retrain()

@app.get("/api/system_status")
def system_status():
    return api_system_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run with:
```bash
pip install fastapi uvicorn
python backend_api.py
```

---

## Key Features Implementation

### 1. Golden Signature Workflow

**How it works:**
1. User runs optimization in any mode
2. Backend compares result with current golden benchmark
3. If score exceeds by >1%, `proposal: true` is returned
4. Frontend shows approve/reject UI
5. On approve: calls `/api/accept_golden` → updates registry
6. All actions logged in `golden_history.json`

**API Flow:**
```typescript
// 1. Run optimization
const response = await optimizationApi.optimizeAuto('balanced')

// 2. Check proposal
if (response.proposal) {
  // Show approve/reject buttons
  setProposal(true, response.cluster_id, response.scenario_key)
}

// 3. User approves
await goldenApi.acceptGolden(
  response.top_result,
  'balanced',
  response.cluster_id,
  response.scenario_key
)
```

### 2. Custom Scenario Support

**Frontend:**
- User selects "Custom" mode
- Adjusts 5 weight sliders (quality, yield, performance, energy, co2)
- Weights auto-normalize to sum = 1.0
- System generates unique `scenario_key` (MD5 hash)

**Backend:**
- Stores custom scenarios in `golden_registry.custom.{scenario_key}.cluster_{id}`
- Isolates custom scenarios from preset modes
- Retrieves correct golden based on mode + scenario_key + cluster_id

### 3. Context-Aware Clustering

**Backend Logic:**
```python
# 1. Cluster historical batches by operational context
hist_df, kmeans = assign_context_clusters(hist_df)

# 2. Current batch maps to cluster_id
current_cluster = hist_df["context_cluster"].mode()[0]

# 3. Optimization searches within cluster
golden_ranges = identify_golden_signatures(
    hist_df, 
    mode="balanced",
    cluster_id=current_cluster
)
```

### 4. Model Drift & Auto-Retraining

**Trigger Conditions:**
```python
def detect_model_drift(df):
    flags = {
        "high_anomaly_rate": anomaly_rate > 0.15,
        "high_energy_drift": energy_drift > 0.05
    }
    return any(flags.values()), flags
```

**Cooldown:**
- 6-hour minimum between retrains
- Prevents excessive retraining
- Logged in `model_versions.json`

---

## Deployment

### Frontend (Vercel/Netlify)

```bash
# Build
npm run build

# Deploy dist/ folder
# Update VITE_API_URL to production backend URL
```

### Backend (AWS/Azure/GCP)

```bash
# Install production dependencies
pip install -r requirements.txt fastapi uvicorn

# Run with gunicorn (production)
gunicorn backend_api:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Hackathon Demo Script

### 1. Show Dashboard (30 sec)
- System status indicators
- Real-time KPIs
- Golden update timeline

### 2. Run Prediction (45 sec)
- Input batch parameters
- Show AI predictions
- Highlight CO₂ estimate

### 3. Run Optimization (2 min)
- Select "Eco" mode
- Run optimization
- Show golden proposal
- **Accept golden update** (human-in-the-loop)
- View updated registry

### 4. Custom Scenario (1 min)
- Switch to "Custom" mode
- Adjust weight sliders
- Run optimization
- Show isolated custom scenario in registry

### 5. Model Governance (45 sec)
- View version history
- Show drift detection
- Display feature importance

### 6. Golden Signature Registry (30 sec)
- Show all active modes
- View update history
- Demonstrate multi-cluster support

**Total: 5 minutes**

---

## Troubleshooting

### Frontend won't connect to backend
- Check backend is running on port 8000
- Verify CORS settings in FastAPI
- Check browser console for errors

### Model not trained
```bash
python backend/src/train_model.py
```

### Golden registry empty
- Run at least one optimization
- Accept the first golden proposal
- Check `backend/models/golden_registry.json`

### Dependencies issues
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Performance Tips

1. **Backend**: Run FastAPI with uvicorn workers
2. **Frontend**: Use production build (`npm run build`)
3. **Optimization**: Reduce `population_size` and `generations` for faster demo
4. **Data**: Use subset of batches for quicker training

---

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Plotly.js chart integration (Pareto frontier)
- [ ] Recharts production trends
- [ ] Batch correction drift table
- [ ] Anomaly detection visualizations
- [ ] Export reports to PDF
- [ ] Multi-user authentication
- [ ] Production deployment configs

---

**Ready for Demo! 🏆**

For questions or issues, refer to:
- Frontend: `frontend/README.md`
- Backend modules: `backend/src/*.py` docstrings
- API integration: `backend/src/integration_api.py`
