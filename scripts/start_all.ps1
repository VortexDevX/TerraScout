# Terra Scout - Start All Components
# Run this from the project root

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Terra Scout - Starting All" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot

# Check if server.jar exists
if (-not (Test-Path "$projectRoot\server\server.jar")) {
    Write-Host "ERROR: server.jar not found in server/" -ForegroundColor Red
    Write-Host "Please download from https://papermc.io/downloads/paper" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Minecraft Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\server'; .\start.ps1"

Write-Host "Waiting for server to start (30 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 30

Write-Host "Starting Bot..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\bot'; npm start"

Write-Host "Waiting for bot to connect (10 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    All components started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Windows opened:" -ForegroundColor Yellow
Write-Host "  1. Minecraft Server (port 25565)" -ForegroundColor Gray
Write-Host "  2. Bot API (port 3000)" -ForegroundColor Gray
Write-Host ""
Write-Host "To run Python agent:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python scripts/test_training.py" -ForegroundColor White
Write-Host ""