$ErrorActionPreference = "Stop"

Write-Host "[bot] Starting bot setup..." -ForegroundColor Cyan

$botDir = Join-Path $PSScriptRoot "bot"
$venvDir = Join-Path $botDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python not found in PATH. Install Python 3.11+ and reopen PowerShell."
}

if (-not (Test-Path $pythonExe)) {
    Write-Host "[bot] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvDir
}

Write-Host "[bot] Installing dependencies..." -ForegroundColor Yellow
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $botDir "requirements.txt")

if (-not (Test-Path (Join-Path $PSScriptRoot ".env")) -and -not (Test-Path (Join-Path $botDir ".env"))) {
    throw "[bot] No env file found. Create either .env in repo root or bot\\.env and set BOT_TOKEN."
}

Write-Host "[bot] Launching bot..." -ForegroundColor Green
Push-Location $botDir
try {
    & $pythonExe -m app.main
}
finally {
    Pop-Location
}
