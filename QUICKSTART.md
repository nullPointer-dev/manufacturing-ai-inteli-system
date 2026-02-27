# Quick Start Scripts

## Windows PowerShell

Run the complete system with one command:

```powershell
.\start.ps1
```

This script will:
1. Check Python and Node.js installation
2. Create virtual environment (if needed)
3. Install all dependencies
4. Train model (if not already trained)
5. Start Backend API (port 8000)
6. Start Frontend UI (port 3000)
7. Open services in separate windows

## Manual Start

### Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python backend_api.py
```

### Frontend
```powershell
cd frontend
npm run dev
```

## Access Points

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Stopping Services

Press `Ctrl+C` in each PowerShell window to stop the services.

## Troubleshooting

### Port already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Dependencies issues
```powershell
# Backend
cd backend
pip install --upgrade -r ../requirements.txt

# Frontend
cd frontend
Remove-Item node_modules -Recurse -Force
npm install
```

### Model not found
```powershell
cd backend
python src/train_model.py
```
