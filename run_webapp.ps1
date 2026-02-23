$ErrorActionPreference = "Stop"

Write-Host "[webapp] Starting webapp setup..." -ForegroundColor Cyan

$webappDir = Join-Path $PSScriptRoot "webapp"

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm not found in PATH. Install Node.js 18+ and reopen PowerShell."
}

Push-Location $webappDir
try {
    Write-Host "[webapp] Installing npm packages..." -ForegroundColor Yellow
    npm install

    Write-Host "[webapp] Launching Next.js dev server at http://localhost:3000" -ForegroundColor Green
    npm run dev
}
finally {
    Pop-Location
}
