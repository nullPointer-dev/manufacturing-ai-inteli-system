# Manufacturing AI Intelligence System - Quick Start

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Manufacturing AI Intelligence System" -ForegroundColor Green
Write-Host " Complete System Startup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "`n[1/5] Checking Python..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}
Write-Host "Python found: " -NoNewline
python --version

# Check if Node.js is installed
Write-Host "`n[2/5] Checking Node.js..." -ForegroundColor Yellow
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js not found. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}
Write-Host "Node.js found: " -NoNewline
node --version

# Backend Setup
Write-Host "`n[3/5] Setting up Backend..." -ForegroundColor Yellow
cd backend

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -q -r ..\requirements.txt
pip install -q fastapi uvicorn

# Check if model exists
$modelPath = "models\model.pkl"
if (!(Test-Path $modelPath)) {
    Write-Host "Training initial model (this may take a minute)..." -ForegroundColor Cyan
    python src\train_model.py
}

Write-Host "Backend setup complete!" -ForegroundColor Green

# Frontend Setup
Write-Host "`n[4/5] Setting up Frontend..." -ForegroundColor Yellow
cd ..\frontend

# Check if node_modules exists
if (!(Test-Path "node_modules")) {
    Write-Host "Installing Node dependencies (this may take a few minutes)..." -ForegroundColor Cyan
    npm install
} else {
    Write-Host "Node dependencies already installed." -ForegroundColor Green
}

Write-Host "Frontend setup complete!" -ForegroundColor Green

# Start Services
Write-Host "`n[5/5] Starting Services..." -ForegroundColor Yellow

# Start Backend API in new window
Write-Host "Starting Backend API on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\..\backend'; .\venv\Scripts\Activate.ps1; python backend_api.py"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend in new window
Write-Host "Starting Frontend on port 3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " System Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nServices running:"
Write-Host "  Backend API:  " -NoNewline -ForegroundColor Yellow
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:     " -NoNewline -ForegroundColor Yellow
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Frontend UI:  " -NoNewline -ForegroundColor Yellow
Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C in each window to stop services" -ForegroundColor Gray
Write-Host "========================================`n" -ForegroundColor Cyan
