$ErrorActionPreference = "Stop"

Write-Host "Starting backend, bot, and webapp in separate PowerShell windows..." -ForegroundColor Cyan

$backendScript = Join-Path $PSScriptRoot "run_backend.ps1"
$botScript = Join-Path $PSScriptRoot "run_bot.ps1"
$webappScript = Join-Path $PSScriptRoot "run_webapp.ps1"

Start-Process powershell -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$backendScript`"")
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$botScript`"")
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$webappScript`"")

Write-Host "All services launched." -ForegroundColor Green
