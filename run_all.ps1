$ErrorActionPreference = "Stop"

Write-Host "Starting backend, bot, and webapp in separate PowerShell windows..." -ForegroundColor Cyan

$backendScript = Join-Path $PSScriptRoot "run_backend.ps1"
$botScript = Join-Path $PSScriptRoot "run_bot.ps1"
$webappScript = Join-Path $PSScriptRoot "run_webapp.ps1"

Start-Process powershell -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$backendScript`"")
Write-Host "Waiting for backend health endpoint..." -ForegroundColor Yellow

$healthUrl = "http://127.0.0.1:8000/health"
$maxAttempts = 120
$backendReady = $false

for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    try {
        $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 2
        if ($response.status -eq "ok") {
            $backendReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $backendReady) {
    throw "Backend did not become healthy in time. Check the backend PowerShell window logs."
}

Write-Host "Backend is healthy. Launching bot and webapp..." -ForegroundColor Green
Start-Process powershell -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$botScript`"")
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$webappScript`"")

Write-Host "All services launched." -ForegroundColor Green
