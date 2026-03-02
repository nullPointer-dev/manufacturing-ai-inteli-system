# Manufacturing AI Intelligence System

> **AI-Driven Adaptive Multi-Objective Optimization for Industrial Batch Processes**
> Real-time energy analytics, asset reliability monitoring, predictive quality control, and continuous model governance — all in one integrated platform.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178c6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)

---

## Table of Contents

- [Overview](#overview)
- [System Pages & Features](#system-pages--features)
- [Backend Engine](#backend-engine)
- [Architecture](#architecture)
- [Data Pipeline](#data-pipeline)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)

> **Pages**: Dashboard · Prediction · Optimization · Golden Signature · Anomaly · Correction · Governance · Industrial Validation

---

## Overview

This system ingests batch-level manufacturing data from two Excel sources — **production quality records** and **process time-series sensor logs** — and provides a complete AI intelligence layer on top:

- A **multi-target ML model** predicts quality, yield, performance, energy, and CO₂ simultaneously
- A **NSGA-II genetic optimizer** finds Pareto-optimal process parameters across all five objectives
- A **Golden Signature registry** encodes the best known batch configurations per scenario and context cluster
- A **human-in-the-loop approval workflow** lets engineers accept or reject AI-proposed parameter changes
- An **energy intelligence engine** classifies every batch by reliability state and attributes causes to specific assets
- An **anomaly detection engine** flags statistically unusual batches using Isolation Forest
- A **correction engine** compares live batches to the golden signature and recommends actionable parameter corrections
- A **model governance layer** tracks model versions, detects drift, and retrains automatically when data distribution shifts

All components are exposed through a FastAPI REST backend and consumed by a React + TypeScript dashboard with 8 purpose-built pages.

---

## System Pages & Features

### 1. Dashboard

The real-time operational overview page.

- **Key metric cards**: Quality Score, Content Uniformity (Yield), Performance Score, Energy (kWh), CO₂ Emissions (kg) — each showing **dataset-wide averages** across all batches, with trend direction comparing the most recent 20% of batches against the first 80% baseline
- **Energy Efficiency card**: 0–100% score showing how close the dataset-wide average energy consumption is to the best-ever (lowest energy) batch recorded
- **Anomaly summary card**: Live count of flagged batches with contamination rate and one-click navigation to the Anomaly page
- **Production Performance Trends chart**: Line chart showing Quality, Energy, Performance, and Content Uniformity over the most recent batches
- All cards refreshed on a 30–120 second polling cycle via React Query

### 2. Real-Time Batch Prediction

Input any combination of process parameters and get immediate AI predictions.

- **Input form**: All process parameters (Granulation Time, Binder Amount, Compression Force, Machine Speed, Moisture Content, etc.)
- **Quality Metrics card**: Overall Quality score, Hardness, Dissolution Rate, Content Uniformity, Yield %, Performance %
- **Energy & Emissions card**: Predicted energy consumption (kWh) and CO₂ emissions (kg)
- **AI Insight**: Contextual plain-English summary of the predicted batch quality and energy profile
- Powered by the trained **MultiOutputRegressor** (6 simultaneous targets)

### 3. Multi-Objective Optimization

AI-driven parameter optimization with human approval workflow.

**Optimization Mode Selection**
- 5 preset optimization scenarios: **Balanced**, **Eco** (energy-focused), **Quality**, **Yield**, **Performance**
- **Custom** mode with per-objective weight sliders (Quality, Yield, Performance, Energy, CO₂ each 0–100%)

**Strategy Selection**
- **Automatic**: Let the optimizer learn the best process parameters freely
- **Target-Based**: Constrain the optimizer to meet specific production goals

**Target Constraints (optional)**
- Minimum required CO₂ reduction %
- Minimum quality, yield, and performance floor values
- When set, the optimizer only returns solutions that satisfy all hard constraints

**Results Panel — Optimal Solution**
- Primary KPIs: Quality, Yield, Performance, Energy Used (kWh), CO₂ Emissions (kg)
- Performance metrics: Hardness, Dissolution Rate, Content Uniformity, Friability
- Process parameters table: all 10 key production parameters at their optimized values
- Energy & Efficiency section: energy per tablet, efficiency score, process efficiency, equipment load
- Process Timing breakdown: granulation, drying, compression, coating durations
- Process Conditions: average power, temperature, pressure, vibration
- Advanced Scores: yield score, performance score, stability index, process intensity

**Pareto Front Chart**
- Interactive scatter plot across all non-dominated solutions
- Color-coded by quality score; hover to inspect any point

**Golden Signature Proposals**
- After optimization, the system proposes updating the golden signature for the active scenario
- Shows current vs. proposed parameter ranges with % change indicators
- One-click **Accept** or **Reject** — recorded in the audit trail
- Rejection modal with selectable reason: Score too low, Energy too high, Quality concern, Yield insufficient, Process risk, or Other

### 4. Golden Signature Management

The central knowledge registry for what "a good batch" looks like.

- **Active session card**: Current scenario, cluster context, golden score, and improvement since baseline
- **Parameter range table**: For each process parameter — current value, golden min/max range, whether it is in-range (green tick) or out-of-range (warning)
- **Scenario switcher**: Toggle between Balanced, Eco, Quality, Yield, Performance scenarios — each maintains its own independent golden registry
- **Golden Update History timeline**: Chronological list of all accepted golden updates with timestamps, reason, and metric deltas (quality, energy, CO₂ before/after)
- **Clear session**: Reset the active golden session to force a fresh baseline on next optimization run

**Behind the scenes:** The golden registry uses KMeans context clustering (k=2) to maintain separate signatures for different operational regimes. A proposed update is only accepted if it represents at least a 1% improvement in the weighted fitness score over the current golden.

### 5. Anomaly Detection & Asset Reliability

Statistical anomaly detection with root-cause attribution.

**Summary Cards**
- Total anomalies detected, contamination rate %, low/medium/high risk breakdown

**Anomaly Scatter Plot**
- 2D scatter: Content Uniformity (X-axis) vs Anomaly Score (Y-axis), bubble size = Quality score
- Color: green (normal) vs red (anomalous)
- Risk level legend (Low / Medium / High)

**Actionable Batches Table**
- Filtered to show only non-stable batches (batches in normal operation are excluded)
- Columns: Batch ID, Asset Reliability State, Root Cause, Recommended Maintenance Action
- Reliability states: **Efficiency Loss**, **Process Instability**, **Calibration Gain**
- Root causes are diagnosed per batch by comparing sensor readings against dataset percentile thresholds:
  - Efficiency Loss → high equipment load, elevated temperature, excess pressure, abnormal power draw
  - Process Instability → high moisture, speed variance, elevated vibration, excess compression force
  - Calibration Gain → below-baseline power or speed (under-processing risk)
- Empty state banner shown when all batches are in stable normal operation

### 6. Batch Correction Engine

Parameter-level correction recommendations for any specific batch.

- **Batch selector**: Choose any batch ID from the dataset (with loading animation while batches populate)
- **Batch summary cards**: After selecting a batch — Quality Score, Drift Analysis summary (Critical / Moderate / OK parameter counts), Energy (kWh), CO₂ (kg)
- **Correction report table**: For every process parameter — current value vs golden mean, drift (in standard deviations), severity (OK / Moderate / Critical), whether the correction is beneficial, and the recommended adjustment
- **Expected impact**: Model-simulated quality delta when correcting each parameter toward the golden mean
- Parameters are ranked by severity so the most impactful corrections appear first
- Only corrections with a positive quality impact are marked as beneficial

### 7. Model Governance & Drift Monitor

Full model lifecycle visibility.

**Metric header cards**
- Current model version (v1, v2, …)
- MAE, RMSE, average R², MAPE across all 6 prediction targets

**Model Version History table**
- Every model version with timestamp, trigger reason (high anomaly rate / high energy drift), metrics, and dataset size
- When a new dataset is uploaded, previous version history is cleared automatically — no stale metrics from old data

**Check Drift & Retrain button**
- Compares current dataset statistics against the training baseline (energy mean shift > 10%, anomaly rate > 15%)
- If drift is detected and cooldown period (6 hours) has passed, automatically retrains and logs a new version
- Shows inline status badge: “Retrained successfully”, “No drift detected”, or “Cooldown active”

**Feature Importance chart**
- SHAP-based global feature importance averaged across all 6 target estimators
- Animated horizontal bar chart showing top 15 contributing process parameters
- Includes loading skeleton with pulse animation while SHAP values compute

**Dataset Upload**
- Drag-and-drop (or file picker) upload for a new pair of Excel files
- System auto-classifies which file is production data vs process sensor data based on column patterns and sheet structure
- Backs up current files, wipes stale model state, and retrains automatically on upload

---

### 8. Industrial Validation

Business-case ROI calculator powered by the live prediction and correction engines.

**Input Parameters (all adjustable via sliders)**
- Electricity cost (₹/kWh)
- Batches per day
- One-time deployment cost (₹)
- Annual maintenance cost (₹)
- Operating days per year

**Financial Impact**
- 3-year ROI %
- Payback period (months)
- Annual net benefit and total annual savings

**Environmental Impact**
- CO₂ reduction % and annual CO₂ saved (kg)
- Annual energy saved (kWh)
- Energy efficiency improvement %
- Trees-equivalent carbon offset

**Operational Improvements**
- Quality, Yield, Performance improvement % (AI-optimized vs current baseline)

**Detailed Breakdown**
- Side-by-side Baseline vs Optimized performance table (Quality, Yield, Performance, Energy/batch, CO₂/batch)
- Annual Savings Breakdown: energy cost savings, raw material savings, quality savings, performance savings, minus maintenance cost, equals net annual benefit

**How it works**: The backend runs the current batch parameters through the prediction model to get baseline metrics, then applies the correction engine against the golden signature to simulate the optimized scenario. The delta is extrapolated to annual scale using the configured production parameters.

---

## Backend Engine

### Data Pipeline (`data_pipeline.py`)
- Loads `batch_production_data.xlsx` (quality outcomes) and `batch_process_data.xlsx` (per-phase sensor time-series, one sheet per batch)
- Strips the Summary sheet automatically
- Aggregates time-series to batch-level features: mean/max power, total energy (kWh = Power × Time/60), phase durations, temperature, pressure, vibration statistics
- Merges production outcomes with process features on Batch_ID
- Derives engineered features: energy intensity, energy efficiency score, equipment load, process efficiency, instability score, quality score, yield score, performance score

### ML Model (`train_model.py`)
- **Algorithm**: `RandomForestRegressor` (100 trees) wrapped in `MultiOutputRegressor`
- **Targets**: Hardness, Dissolution Rate, Content Uniformity, Yield Score, Performance Score, Total Energy
- **Features**: All numeric process columns excluding targets
- **Metrics**: MAE, RMSE, avg R², MAPE — saved to `model_metrics.json` and logged in `model_versions.json`
- Saves `model.pkl` + `feature_columns.pkl` for consistent inference

### NSGA-II Optimizer (`optimizer_nsga2.py`)
- Initializes population from golden signature parameter ranges (realistic starting points)
- Tournament selection, blend crossover (α=0.3), Gaussian mutation (σ=0.05)
- Pareto non-domination sorting across (Quality, Yield, Performance, Energy, CO₂)
- Energy values clamped to ±30% of historical mean to prevent unrealistic solutions
- Filtered through **reliability gate** (rejects solutions scoring below the 20th percentile fitness)
- Returns the top-ranked Pareto front solution plus all non-dominated alternatives

### Energy Intelligence (`energy_intelligence.py`)
- Classifies each batch into one of four reliability states using percentile thresholds:
  - **Efficiency Loss**: energy drift > 80th percentile
  - **Calibration Gain**: energy drift < 20th percentile
  - **Process Instability**: instability score > 85th percentile
  - **Stable**: none of the above
- Diagnoses specific root causes per batch by checking which sensor readings exceed their respective percentile bounds
- Computes rolling energy statistics, energy drift from moving average, and per-batch instability score

### Anomaly Detection (`anomaly_detection.py`)
- **Algorithm**: Isolation Forest (contamination = 10%)
- Assigns anomaly score and binary flag to every batch
- Classifies risk level into Low / Medium / High bins based on score distribution

### Golden Signature (`golden_signature.py`, `golden_updater.py`)
- Selects top 25% of batches by weighted fitness score for the active scenario
- Applies KMeans (k=2) clustering to isolate the more homogeneous high-performing cluster
- Computes parameter ranges (mean ± 1.5σ with minimum width floor) as the golden envelope
- On proposed update: checks for ≥1% improvement; if passed, archives the old signature and writes the new one
- Stores separate signatures per scenario × cluster key with full history in `golden_history.json`

### Correction Engine (`correction_engine.py`)
- For each parameter, computes z-score drift from the golden mean
- Simulates a correction by setting the parameter to the golden mean and re-running the model
- Reports impact estimate (predicted quality delta), severity, and whether the correction is net-beneficial

### Model Governance (`model_governance.py`, `learning_controller.py`)
- Saves drift baseline (energy mean, energy std, anomaly rate, sample count) at training time
- On retrain check: computes energy mean shift and current anomaly rate; flags drift if either threshold exceeded
- Enforces 6-hour cooldown between retrains
- Appends structured version record to `model_versions.json` on each retrain

### Explainability (`explainability_engine.py`)
- Uses SHAP `TreeExplainer` on each target estimator inside `MultiOutputRegressor`
- Computes mean absolute SHAP values per feature, averaged across all 6 targets
- Returns ranked feature importance list for the governance dashboard

### Industrial Validation (`industrial_validation.py`)
- Accepts user-defined production economics: electricity cost, batches/day, deployment cost, maintenance cost, operating days
- Runs the **prediction model** on default batch parameters to establish a current baseline (quality, yield, energy, CO₂)
- Queries the **golden signature registry** and runs the **correction engine** to simulate the optimized scenario
- Computes the improvement delta (quality %, yield %, performance %, energy saved/batch, CO₂ saved/batch)
- Extrapolates to annual scale: energy cost savings, raw material savings, quality savings, performance savings
- Calculates **3-year ROI %**, **payback period (months)**, and **net annual benefit** after maintenance costs
- Computes environmental metrics: CO₂ reduction %, annual CO₂ saved, energy efficiency improvement %, and trees-equivalent offset
- Falls back to simulated improvements when no golden signature exists yet

---

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                     Browser (React + TS)                   │
│   Dashboard │ Prediction │ Optimization │ GoldenSignature  │
│   Anomaly   │ Correction │ Governance                      │
│                                                            │
│   React Query (server state)   Zustand (client state)     │
└──────────────────────┬────────────────────────────────────┘
                       │  HTTP REST
┌──────────────────────▼────────────────────────────────────┐
│                  FastAPI (port 8001)                       │
│   /api/predict         /api/optimize_auto                  │
│   /api/optimize_target /api/accept_golden                  │
│   /api/anomalies       /api/asset_reliability              │
│   /api/check_retrain   /api/feature_importance             │
│   /api/data-files/upload  /api/rejection_history           │
└──────────────────────┬────────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────────┐
│                   Backend Modules                          │
│  data_pipeline → feature_engineering → train_model        │
│  golden_signature → golden_updater → correction_engine     │
│  optimizer_nsga2 → optimizer_target → reliability_gate     │
│  anomaly_detection → energy_intelligence                   │
│  model_governance → learning_controller → explainability   │
└──────────────────────┬────────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────────┐
│                    Persistent Storage                      │
│  backend/data/   batch_production_data.xlsx                │
│                  batch_process_data.xlsx                   │
│  backend/models/ model.pkl  feature_columns.pkl            │
│                  model_metrics.json                        │
│                  golden_session.json golden_registry.json  │
│                  golden_archive.json golden_history.json   │
│                  golden_rejections.json drift_baseline.json│
└───────────────────────────────────────────────────────────┘
```

---

## Data Pipeline

The system expects two Excel files placed in `backend/data/`:

| File | Content |
|------|---------|
| `batch_production_data.xlsx` | One row per batch — quality outcomes (Hardness, Dissolution Rate, Content Uniformity, etc.) |
| `batch_process_data.xlsx` | Multiple sheets (one per batch) — time-series sensor readings (Power, Temperature, Pressure, Vibration, Phase) |

When you upload a new pair via the **Governance** page upload endpoint, the system automatically:
1. Classifies which file is production vs process data
2. Backs up the previous files to `backend/data/backups/`
3. Wipes stale state (`golden_session.json`, `drift_baseline.json`)
4. Retrains the model on the new data from scratch

---

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+

### One-Command Setup (Windows)

```powershell
.\start.ps1
```

This script installs all dependencies, trains the initial model, and starts both servers.

### Manual Setup

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r ../requirements.txt
cd src
python train_model.py          # trains initial model
python backend_api.py          # starts on port 8001

# Frontend (new terminal)
cd frontend
npm install
npm run dev                    # starts on port 5173
```

### Access

| Service | URL |
|---------|-----|
| Frontend UI | http://localhost:5173 |
| Backend API | http://localhost:8001 |
| Swagger Docs | http://localhost:8001/docs |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Predict quality/energy for given parameters |
| POST | `/api/optimize_auto` | Run NSGA-II for a given scenario mode |
| POST | `/api/optimize_target` | Run NSGA-II with hard constraints |
| GET | `/api/golden` | Get active golden signature |
| POST | `/api/accept_golden` | Accept a proposed golden update |
| POST | `/api/reject_golden` | Log a golden proposal rejection |
| GET | `/api/rejection_history` | Rejection audit trail |
| GET | `/api/golden_archive` | Full golden update history |
| GET | `/api/golden_history` | Golden update timeline |
| POST | `/api/clear_session` | Reset active golden session |
| GET | `/api/anomalies` | Anomaly detection results |
| GET | `/api/asset_reliability` | Reliability states + root causes |
| GET | `/api/dashboard/stats` | Dataset-wide KPI averages + trends |
| GET | `/api/production/trends` | Batch trend time-series |
| GET | `/api/model_history` | Model version history |
| GET | `/api/feature_importance` | SHAP feature importance |
| POST | `/api/check_retrain` | Trigger drift check + optional retrain |
| GET | `/api/batches` | All batch records |
| GET | `/api/batch/{batch_id}/analyze` | Correction report for a specific batch |
| GET | `/api/system_status` | Model + registry existence flags |
| GET | `/api/data-files` | List current data files |
| POST | `/api/data-files/upload` | Upload new dataset pair (auto-classified) |
| GET | `/api/health` | Health check |

---

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Backend language | Python 3.8+ |
| API framework | FastAPI + uvicorn |
| ML | scikit-learn (RandomForest, IsolationForest, KMeans), SHAP |
| Data processing | pandas, numpy, scipy |
| Model persistence | joblib |
| Frontend framework | React 18 + TypeScript |
| Build tool | Vite |
| UI components | shadcn/ui + Radix UI + Tailwind CSS |
| Animations | Framer Motion, GSAP |
| State management | Zustand + TanStack Query v5 |
| Charts | Recharts, Plotly.js |
| HTTP client | Axios |
| Date utilities | date-fns |

---

## Project Structure

```
manufacturing-ai-inteli-system/
├── backend/
│   ├── src/
│   │   ├── backend_api.py          # FastAPI server + all route handlers
│   │   ├── integration_api.py      # Business logic bridge layer
│   │   ├── data_pipeline.py        # Excel ingestion + feature engineering
│   │   ├── feature_engineering.py  # Derived metrics + scoring
│   │   ├── train_model.py          # Model training + metrics
│   │   ├── prediction_service.py   # Inference wrapper
│   │   ├── batch_scorer.py         # Attach predictions to batch rows
│   │   ├── optimizer_nsga2.py      # NSGA-II genetic optimizer
│   │   ├── optimizer_auto.py       # Auto mode dispatcher
│   │   ├── optimizer_target.py     # Constraint-based optimization
│   │   ├── optimizer_core.py       # Core optimization utilities
│   │   ├── core_fitness.py         # Multi-objective fitness function
│   │   ├── golden_signature.py     # Golden cluster identification
│   │   ├── golden_updater.py       # Registry write + history management
│   │   ├── correction_engine.py    # Per-batch correction analysis
│   │   ├── context_engine.py       # Operational cluster assignment
│   │   ├── anomaly_detection.py    # Isolation Forest detection
│   │   ├── energy_intelligence.py  # Reliability states + root causes
│   │   ├── explainability_engine.py# SHAP feature importance
│   │   ├── model_governance.py     # Drift detection logic
│   │   ├── learning_controller.py  # Retrain orchestration + versioning
│   │   ├── reliability_gate.py     # Solution quality filter
│   │   └── scenario_utils.py       # Scenario helpers
│   ├── data/                       # Excel input files
│   └── models/                     # Trained models + JSON registries
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── Prediction.tsx
│       │   ├── Optimization.tsx
│       │   ├── GoldenSignature.tsx
│       │   ├── Anomaly.tsx
│       │   ├── Correction.tsx
│       │   ├── Governance.tsx
│       │   └── IndustrialValidation.tsx
│       ├── components/
│       │   ├── dashboard/          # MetricCard, Gauge, GoldenTimeline
│       │   ├── layout/             # Header, Sidebar, Layout
│       │   └── ui/                 # Button, Card, Dialog, Slider, Table…
│       ├── store/                  # Zustand: optimizationStore, systemStore
│       ├── lib/                    # api.ts (all fetch calls), utils.ts
│       └── types/                  # Shared TypeScript interfaces
├── requirements.txt
├── start.ps1
├── SETUP_GUIDE.md
├── QUICKSTART.md
└── README.md
```
