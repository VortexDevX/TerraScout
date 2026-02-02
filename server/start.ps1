# Terra Scout Minecraft Server Launcher

$minRam = "1G"
$maxRam = "2G"
$serverJar = "server.jar"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Terra Scout Minecraft Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if server.jar exists
if (-not (Test-Path $serverJar)) {
    Write-Host ""
    Write-Host "ERROR: server.jar not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download the Minecraft server:" -ForegroundColor Yellow
    Write-Host "  Option 1 (Vanilla): https://www.minecraft.net/en-us/download/server" -ForegroundColor White
    Write-Host "  Option 2 (Paper):   https://papermc.io/downloads/paper" -ForegroundColor White
    Write-Host ""
    Write-Host "Then place the jar file in this directory and rename to 'server.jar'" -ForegroundColor Yellow
    exit 1
}

# Check EULA
if (-not (Test-Path "eula.txt") -or -not (Select-String -Path "eula.txt" -Pattern "eula=true" -Quiet)) {
    Write-Host ""
    Write-Host "Accepting Minecraft EULA..." -ForegroundColor Yellow
    "eula=true" | Out-File -FilePath "eula.txt" -Encoding ASCII
}

# Check Java
Write-Host ""
Write-Host "Java Version:" -ForegroundColor Yellow
java -version

Write-Host ""
Write-Host "Starting server with $minRam - $maxRam RAM..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start server
java "-Xms$minRam" "-Xmx$maxRam" -jar $serverJar nogui