# Test Terra Scout Connection

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Terra Scout Connection Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Java/Minecraft server
Write-Host "[1] Checking for Java processes (Minecraft server)..." -ForegroundColor Yellow
$javaProcs = Get-Process -Name "java" -ErrorAction SilentlyContinue
if ($javaProcs) {
    Write-Host "    [OK] Java process found (Minecraft server likely running)" -ForegroundColor Green
} else {
    Write-Host "    [WARN] No Java process found!" -ForegroundColor Red
    Write-Host "    Start the Minecraft server first:" -ForegroundColor Yellow
    Write-Host "      cd server && .\start.ps1" -ForegroundColor White
}

# Check Node.js bot
Write-Host ""
Write-Host "[2] Checking for Node.js processes (Bot)..." -ForegroundColor Yellow
$nodeProcs = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcs) {
    Write-Host "    [OK] Node.js process found (Bot likely running)" -ForegroundColor Green
} else {
    Write-Host "    [WARN] No Node.js process found!" -ForegroundColor Red
    Write-Host "    Start the bot:" -ForegroundColor Yellow
    Write-Host "      cd bot && npm start" -ForegroundColor White
}

# Check Bot API
Write-Host ""
Write-Host "[3] Checking Bot API..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:3000/health" -TimeoutSec 5
    Write-Host "    [OK] API responding" -ForegroundColor Green
    Write-Host "    Connected to Minecraft: $($health.connected)" -ForegroundColor $(if($health.connected){"Green"}else{"Yellow"})
} catch {
    Write-Host "    [FAIL] API not responding" -ForegroundColor Red
    Write-Host "    Start the bot: cd bot && npm start" -ForegroundColor Yellow
}

# Check Minecraft port
Write-Host ""
Write-Host "[4] Checking Minecraft port 25565..." -ForegroundColor Yellow
$tcpConnection = Test-NetConnection -ComputerName localhost -Port 25565 -WarningAction SilentlyContinue
if ($tcpConnection.TcpTestSucceeded) {
    Write-Host "    [OK] Port 25565 is open (Minecraft server accepting connections)" -ForegroundColor Green
} else {
    Write-Host "    [FAIL] Port 25565 not responding" -ForegroundColor Red
    Write-Host "    Make sure Minecraft server is fully started" -ForegroundColor Yellow
}

# Try to connect if API is up but not connected
Write-Host ""
Write-Host "[5] Attempting connection..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "http://localhost:3000/status" -TimeoutSec 5
    if (-not $status.connected) {
        Write-Host "    Trying to connect bot to Minecraft..." -ForegroundColor Gray
        $result = Invoke-RestMethod -Uri "http://localhost:3000/connect" -Method POST -TimeoutSec 30
        if ($result.success) {
            Write-Host "    [OK] Connected successfully!" -ForegroundColor Green
        } else {
            Write-Host "    [FAIL] $($result.error)" -ForegroundColor Red
        }
    } else {
        Write-Host "    [OK] Already connected!" -ForegroundColor Green
    }
} catch {
    Write-Host "    [SKIP] Could not test connection" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""