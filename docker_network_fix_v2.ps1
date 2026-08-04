# PowerShell script to fix Docker networking issues with Magentic-UI WebSockets
# This script ensures proper network communication between containers

Write-Host "=== Docker WebSocket Networking Fix for Magentic-UI ===" -ForegroundColor Green
Write-Host "Step 1: Checking Docker status..." -ForegroundColor Cyan
docker info

Write-Host "`nStep 2: Stopping all running Magentic-UI Docker containers..." -ForegroundColor Cyan
$runningContainers = docker ps -q --filter "ancestor=magentic-ui-python-env" --filter "ancestor=magentic-ui-vnc-browser"
if ($runningContainers) {
    docker stop $runningContainers
} else {
    Write-Host "No running Magentic-UI containers found." -ForegroundColor Yellow
}

Write-Host "`nStep 3: Removing all stopped Magentic-UI containers..." -ForegroundColor Cyan
docker container prune -f

Write-Host "`nStep 4: Resetting Docker network configuration..." -ForegroundColor Cyan
$existingNetwork = docker network ls --filter name=magentic-ui-network -q
if ($existingNetwork) {
    Write-Host "Removing existing magentic-ui-network..." -ForegroundColor Yellow
    docker network rm magentic-ui-network
}
docker network prune -f

Write-Host "`nStep 5: Creating a new bridge network with proper WebSocket support..." -ForegroundColor Cyan
docker network create --driver bridge magentic-ui-network

Write-Host "`nStep 6: Verifying network configuration..." -ForegroundColor Cyan
docker network inspect magentic-ui-network

Write-Host "`nStep 7: Setting up environment variables for Docker containers..." -ForegroundColor Cyan
$env:DOCKER_PLAYWRIGHT_CONTAINER_PORT = "37367"
$env:DOCKER_NOVNC_PORT = "6080"
$env:DOCKER_NETWORK = "magentic-ui-network"

Write-Host "`nStep 8: Exposing the host's port range for WebSocket connections..." -ForegroundColor Cyan
# Open firewall ports for WebSocket connections if needed (Windows only)
if ((Get-Command "netsh" -ErrorAction SilentlyContinue)) {
    Write-Host "Opening WebSocket ports in Windows Firewall..." -ForegroundColor Yellow
    netsh advfirewall firewall add rule name="Magentic-UI WebSocket" dir=in action=allow protocol=TCP localport=37000-38000 profile=any
    netsh advfirewall firewall add rule name="Magentic-UI noVNC" dir=in action=allow protocol=TCP localport=6080-6090 profile=any
}

Write-Host "`nStep 9: Setting up port forwarding for Docker Desktop on Windows..." -ForegroundColor Cyan
Write-Host "If using Docker Desktop for Windows, ensure 'Expose daemon on tcp://localhost:2375 without TLS' is enabled in Docker Desktop settings." -ForegroundColor Yellow

Write-Host "`nStep 10: Network setup complete!" -ForegroundColor Green
Write-Host "Now run Magentic-UI with the following command:" -ForegroundColor Cyan
Write-Host "magentic ui --port 8083 --config d:\0GH_PROD\darbot-netic\config.yaml --docker-network magentic-ui-network" -ForegroundColor Yellow

Write-Host "`nMonitoring instructions:" -ForegroundColor Cyan
Write-Host "1. To view logs from the VNC browser container:" -ForegroundColor Yellow
Write-Host "   docker logs -f \$(docker ps -q --filter 'ancestor=magentic-ui-vnc-browser' | Select-Object -First 1)" -ForegroundColor Yellow
Write-Host "2. To check WebSocket connectivity:" -ForegroundColor Yellow
Write-Host "   Test-NetConnection -ComputerName localhost -Port 37367" -ForegroundColor Yellow
Write-Host "3. To check the Docker network:" -ForegroundColor Yellow
Write-Host "   docker network inspect magentic-ui-network" -ForegroundColor Yellow

Write-Host "`nTroubleshooting tips:" -ForegroundColor Cyan
Write-Host "1. If WebSocket connections still fail, try running the browser in non-Docker mode." -ForegroundColor Yellow
Write-Host "2. Check that port 37367 is not blocked by any other application." -ForegroundColor Yellow  
Write-Host "3. Verify that Docker Desktop's networking is properly configured." -ForegroundColor Yellow
Write-Host "4. If using Windows, ensure Hyper-V networking is functioning correctly." -ForegroundColor Yellow
