# ============================================================
#  Manufacturing AI Intelligence System - Launcher
#  Run this from the project root:  .\start.ps1
# ============================================================

$ROOT   = $PSScriptRoot
$BACK   = Join-Path $ROOT "backend"
$FRONT  = Join-Path $ROOT "frontend"
$PYTHON = Join-Path $BACK  "venv\Scripts\python.exe"
$ENTRY  = Join-Path $BACK  "src\backend_api.py"

# ---- colours -----------------------------------------------
function Write-Header { param($msg)
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}
function Write-Ok    { param($msg) Write-Host "[OK]  $msg" -ForegroundColor Green  }
function Write-Info  { param($msg) Write-Host "[..] $msg"  -ForegroundColor Yellow }
function Write-Err   { param($msg) Write-Host "[ERR] $msg" -ForegroundColor Red    }

# ---- pre-flight checks -------------------------------------
Write-Header "Manufacturing AI Intelligence System"

if (-not (Test-Path $PYTHON)) {
    Write-Err "Python venv not found at: $PYTHON"
    Write-Err "Run:  cd backend; python -m venv venv; .\venv\Scripts\pip install -r ..\requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "$FRONT\node_modules")) {
    Write-Info "node_modules not found. Installing npm packages..."
    & npm install --prefix $FRONT
    if ($LASTEXITCODE -ne 0) {
        Write-Err "npm install failed. Install Node.js and try again."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# ---- free ports if already in use -------------------------
foreach ($port in @(8001, 5173)) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Info "Freeing port $port (PID $($conn.OwningProcess))..."
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 800
    }
}

# ---- start backend -----------------------------------------
Write-Info "Starting backend (FastAPI) on http://localhost:8001 ..."

$backJob = Start-Process -FilePath $PYTHON `
    -ArgumentList $ENTRY `
    -WorkingDirectory (Join-Path $BACK "src") `
    -PassThru `
    -WindowStyle Normal

Start-Sleep -Seconds 3

$healthOk = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $r = Invoke-RestMethod -Uri "http://localhost:8001/api/health" -TimeoutSec 2 -ErrorAction Stop
        if ($r.status -eq "healthy") { $healthOk = $true; break }
    } catch {}
    Start-Sleep -Seconds 1
}

if ($healthOk) {
    Write-Ok "Backend healthy  ->  http://localhost:8001"
} else {
    Write-Err "Backend did not respond after 10 s. Check the backend window for errors."
}

# ---- start frontend ----------------------------------------
Write-Info "Starting frontend (Vite) on http://localhost:5173 ..."

$frontJob = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c npm run dev" `
    -WorkingDirectory $FRONT `
    -PassThru `
    -WindowStyle Normal

Start-Sleep -Seconds 4

$frontOk = $false
for ($i = 1; $i -le 10; $i++) {
    $conn = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
    if ($conn) { $frontOk = $true; break }
    Start-Sleep -Seconds 1
}

if ($frontOk) {
    Write-Ok "Frontend ready   ->  http://localhost:5173"
} else {
    Write-Err "Frontend did not start on port 5173. Check the frontend window for errors."
}

# ---- open browser ------------------------------------------
Write-Header "System ready"
Write-Host "  Frontend  :  http://localhost:5173" -ForegroundColor White
Write-Host "  API docs  :  http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Close this window (or press Ctrl+C) to shut everything down." -ForegroundColor DarkGray
Write-Host ""

Start-Process "http://localhost:5173"

# ---- wait and clean up on Ctrl+C ---------------------------
try {
    while ($true) { Start-Sleep -Seconds 5 }
} finally {
    Write-Host "`nShutting down..." -ForegroundColor Yellow
    if ($backJob  -and -not $backJob.HasExited)  { Stop-Process -Id $backJob.Id  -Force -ErrorAction SilentlyContinue }
    if ($frontJob -and -not $frontJob.HasExited) { Stop-Process -Id $frontJob.Id -Force -ErrorAction SilentlyContinue }
    # also kill any child node processes on port 5173
    $conn = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
    if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
    Write-Ok "All processes stopped."
}
