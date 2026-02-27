# 🏭 Manufacturing AI Intelligence System

> **AI-Driven Adaptive Multi-Objective Optimization for Industrial Batch Processes**  
> Real-time energy pattern analytics, asset reliability monitoring, and carbon management

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178c6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Demo Video](#demo-video)
- [Hackathon Alignment](#hackathon-alignment)
- [Technology Stack](#technology-stack)
- [Documentation](#documentation)

---

## 🎯 Overview

This system addresses the critical challenge of **batch-level energy optimization** in manufacturing through:

- **Multi-objective NSGA-II optimization** balancing Quality, Yield, Performance, Energy, and CO₂
- **Golden signature management** with human-in-the-loop workflow for continuous improvement
- **Context-aware clustering** for different operational regimes
- **Energy pattern intelligence** revealing asset health and process reliability
- **Adaptive target setting** aligned with regulatory and ESG requirements
- **Real-time drift detection** with automatic model retraining

**Primary Track**: Track B (Optimization Engine Specialization)  
**Secondary Track**: Track A (Predictive Modeling Specialization)

---

## ✨ Key Features

### 🎯 Track B: Optimization Engine (Primary)

#### ✅ Golden Signature Framework
- **5 preset scenarios**: Balanced, Eco, Quality, Yield, Performance
- **Custom weight scenarios** with MD5-based isolation
- **Cluster-aware storage**: Separate signatures per operational context
- **Improvement threshold**: 1% minimum gain for golden updates
- **Historical audit trail**: Complete update history with metrics

#### ✅ Continuous Learning
- **Automatic golden updates** when optimization exceeds benchmarks
- **Human-in-the-loop approval**: User can accept or reject proposals
- **Self-improving system**: Learns from production performance
- **Decision memory**: Stores all human decisions for future reuse

#### ✅ Adaptive Optimization
- **Real-time parameter optimization**: NSGA-II multi-objective algorithm
- **Dynamic goal setting**: Target-based constraints (CO₂ reduction, min quality/yield)
- **Context-adaptive**: Respects operational cluster boundaries
- **Reliability gating**: Filters unstable solutions

### 🧠 Track A: Predictive Modeling (Secondary)

#### ✅ Advanced Multi-Target Prediction
- **6 simultaneous predictions**: Hardness, Dissolution, Uniformity, Yield, Performance, Energy
- **>90% accuracy potential**: RandomForest MultiOutputRegressor
- **Real-time forecasting**: Batch-level prediction API

#### ✅ Energy Pattern Intelligence
- **Asset reliability insights**: Detects Efficiency Loss, Process Instability, Calibration Gains
- **Power consumption analysis**: Rolling statistics and drift detection
- **Predictive maintenance flags**: Early warnings for equipment issues

### 🌐 Universal Features

- **Industrial ROI calculator** with adjustable assumptions
- **Adaptive carbon alignment** with regulatory scenario support
- **Model governance dashboard** with drift monitoring
- **Feature importance analysis** for explainability
- **Version tracking** with automatic retraining
- **Integration APIs** for seamless system connectivity

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Dashboard │ │Prediction│ │Optimizer │ │ Golden  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                          │
│      Zustand State          React Query Cache           │
└──────────────────┬──────────────────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────────────────┐
│              Backend (FastAPI + Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Prediction   │  │ Optimization │  │  Golden      │  │
│  │ Service      │  │ NSGA-II      │  │  Manager     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Anomaly      │  │ Energy       │  │  Model       │  │
│  │ Detection    │  │ Intelligence │  │  Governance  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                   Data Layer                             │
│  • Batch production data (Excel)                         │
│  • Process time-series data (Excel)                      │
│  • Trained ML models (.pkl)                              │
│  • Golden registries (.json)                             │
│  • Model versions & metrics (.json)                      │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input → Frontend → API → Backend Logic → ML Models → Response
                                    ↓
                          Golden Registry Check
                                    ↓
                          Human Approval (if required)
                                    ↓
                          Update Golden Signature
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (for cloning)

### One-Command Setup (Windows)

```powershell
.\start.ps1
```

This automated script:
1. ✅ Checks Python and Node.js
2. ✅ Creates virtual environment
3. ✅ Installs backend dependencies
4. ✅ Installs frontend dependencies
5. ✅ Trains initial model
6. ✅ Starts Backend API (port 8000)
7. ✅ Starts Frontend UI (port 3000)

### Manual Setup

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Train initial model
python src/train_model.py

# Start API server
python backend_api.py
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access Points

- 🌐 **Frontend UI**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 📖 **Alternative Docs**: http://localhost:8000/redoc

---

## 🎥 Demo Video

[TODO: Add demo video link]

**Demo Script (5 minutes):**
1. Dashboard overview (30s)
2. Real-time prediction (45s)
3. Run optimization + golden approval (2min)
4. Custom scenario demonstration (1min)
5. Model governance & registry (45s)

---

## 🏆 Hackathon Alignment

### Track B Requirements ✅

| Requirement | Implementation | Evidence |
|------------|----------------|----------|
| Golden Signature Framework | Multi-scenario registry with cluster isolation | `golden_signature.py`, `golden_updater.py` |
| Continuous Learning | Auto-updates when performance exceeds +1% | `check_and_update_golden()` function |
| Adaptive Optimization | NSGA-II with real-time goals | `optimizer_nsga2.py`, `optimizer_target.py` |
| Human-in-the-loop | Approve/reject workflow in UI | `Optimization.tsx` proposal cards |
| Historical Tracking | Complete audit trail | `golden_history.json` |

### Track A Requirements ✅

| Requirement | Implementation | Evidence |
|------------|----------------|----------|
| Multi-Target Prediction | 6 outputs via MultiOutputRegressor | `train_model.py`, `prediction_service.py` |
| Energy Pattern Analysis | Reliability state classification | `energy_intelligence.py` |
| Real-Time Forecasting | REST API with <100ms response | `backend_api.py` `/api/predict` |
| >90% Accuracy | R² tracking per target | `model_metrics.json` |

### Universal Requirements ✅

| Requirement | Implementation | Evidence |
|------------|----------------|----------|
| Adaptive Target Setting | Regulatory scenario support | Dashboard ROI calculator |
| Integration APIs | 10+ REST endpoints | `backend_api.py`, `integration_api.py` |
| Data Pipeline | Robust preprocessing | `data_pipeline.py`, `feature_engineering.py` |
| Industrial Validation | Excel data ingestion | `data/` folder |

---

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core language
- **FastAPI**: REST API framework
- **scikit-learn**: ML models (RandomForest, Isolation Forest, K-Means)
- **pandas/numpy**: Data processing
- **joblib**: Model persistence

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Shadcn/ui + Radix UI**: Component library
- **Tailwind CSS**: Styling
- **Framer Motion**: Animations
- **Zustand**: State management
- **React Query**: Server state
- **Recharts + Plotly.js**: Visualizations

### Infrastructure
- **uvicorn**: ASGI server
- **CORS**: Cross-origin support
- **JSON**: Data persistence

---

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)**: Comprehensive setup instructions
- **[QUICKSTART.md](QUICKSTART.md)**: Quick start scripts and troubleshooting
- **[frontend/README.md](frontend/README.md)**: Frontend architecture and API integration
- **[Backend Module Docs](backend/src/)**: Inline docstrings in all Python files

---

## 📂 Project Structure

```
manufacturing-ai-inteli-system/
├── backend/
│   ├── src/                    # Python modules (15+ files)
│   ├── data/                   # Excel data files
│   ├── models/                 # Trained models & registries
│   └── backend_api.py          # FastAPI server
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # 7 main pages
│   │   ├── store/              # Zustand stores
│   │   ├── lib/                # API client & utils
│   │   └── types/              # TypeScript types
│   ├── external_ui_assets/     # Animated components
│   └── package.json
├── requirements.txt            # Python dependencies
├── start.ps1                   # Automated setup script
├── SETUP_GUIDE.md
├── QUICKSTART.md
└── README.md                   # This file
```

---

## 🤝 Contributing

This is a hackathon project. For production deployment:

1. Add authentication & authorization
2. Implement database backend (PostgreSQL/MongoDB)
3. Add WebSocket support for real-time updates
4. Implement comprehensive logging
5. Add unit & integration tests
6. Set up CI/CD pipeline
7. Configure production CORS policies

---

## 📄 License

Proprietary - Manufacturing AI Intelligence System  
Developed for Industrial AI Hackathon 2026

---

## 👥 Team

[Add team member names and roles]

---

## 🙏 Acknowledgments

- Problem statement provided by hackathon organizers
- UI assets inspired by modern control room designs
- Built with open-source technologies

---

## 📞 Support

For technical issues or questions:
- Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Review API docs at http://localhost:8000/docs
- Inspect browser console for frontend errors
- Check backend logs in terminal

---

**Built with ❤️ for Sustainable Manufacturing** 🌱🏭
