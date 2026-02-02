# Terra Scout Minecraft Server Launcher

param(
    [string]$MinRam = "1G",
    [string]$MaxRam = "2G"
)

$serverJar = "server.jar"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Terra Scout Minecraft Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if server.jar exists
if (-not (Test-Path $serverJar)) {
    Write-Host "ERROR: server.jar not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download the Minecraft server:" -ForegroundColor Yellow
    Write-Host "  https://papermc.io/downloads/paper" -ForegroundColor White
    Write-Host ""
    Write-Host "Then rename to 'server.jar' and place in this folder." -ForegroundColor Yellow
    pause
    exit 1
}

# Check EULA
if (-not (Test-Path "eula.txt")) {
    Write-Host "Creating eula.txt..." -ForegroundColor Yellow
    "eula=true" | Out-File -FilePath "eula.txt" -Encoding ASCII
}

# Java info
Write-Host "Java Version:" -ForegroundColor Yellow
java -version 2>&1 | Select-Object -First 1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host ""
Write-Host "Server Configuration:" -ForegroundColor Yellow
Write-Host "  RAM: $MinRam - $MaxRam" -ForegroundColor Gray
Write-Host "  Port: 25565" -ForegroundColor Gray
Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start server with optimized flags for Paper
java `
"-Xms$MinRam" `
"-Xmx$MaxRam" `
"-XX:+UseG1GC" `
"-XX:+ParallelRefProcEnabled" `
"-XX:MaxGCPauseMillis=200" `
"-XX:+UnlockExperimentalVMOptions" `
"-XX:+DisableExplicitGC" `
"-XX:G1NewSizePercent=30" `
"-XX:G1MaxNewSizePercent=40" `
"-XX:G1HeapRegionSize=8M" `
"-XX:G1ReservePercent=20" `
"-XX:G1HeapWastePercent=5" `
"-XX:G1MixedGCCountTarget=4" `
"-XX:InitiatingHeapOccupancyPercent=15" `
"-XX:G1MixedGCLiveThresholdPercent=90" `
"-XX:G1RSetUpdatingPauseTimePercent=5" `
"-XX:SurvivorRatio=32" `
"-XX:+PerfDisableSharedMem" `
"-XX:MaxTenuringThreshold=1" `
"-Dusing.aikars.flags=https://mcflags.emc.gs" `
"-Daikars.new.flags=true" `
"-jar" "$serverJar" `
"nogui"
