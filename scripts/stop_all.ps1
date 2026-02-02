# Terra Scout - Stop All Components

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "    Terra Scout - Stopping All" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Stop Node.js processes
Write-Host "Stopping Node.js processes..." -ForegroundColor Gray
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Stop Java processes (Minecraft server)
Write-Host "Stopping Java processes..." -ForegroundColor Gray
Get-Process -Name "java" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "All components stopped." -ForegroundColor Green
Write-Host ""