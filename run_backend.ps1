$ErrorActionPreference = "Stop"

Write-Host "[backend] Starting backend setup..." -ForegroundColor Cyan

$backendDir = Join-Path $PSScriptRoot "backend"
$venvDir = Join-Path $backendDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python not found in PATH. Install Python 3.11+ and reopen PowerShell."
}

if (-not (Test-Path $pythonExe)) {
    Write-Host "[backend] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvDir
}

Write-Host "[backend] Installing dependencies..." -ForegroundColor Yellow
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $backendDir "requirements.txt")

if (-not (Test-Path (Join-Path $PSScriptRoot ".env"))) {
    Write-Host "[backend] .env not found in root. Copy .env.example to .env before production use." -ForegroundColor Yellow
}

Write-Host "[backend] Launching API at http://127.0.0.1:8000" -ForegroundColor Green
Push-Location $backendDir
try {
    & $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}
finally {
    Pop-Location
}
