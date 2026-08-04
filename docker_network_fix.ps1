# PowerShell script to help diagnose and fix Docker networking issues with Magentic-UI

Write-Host "=== Docker Networking Diagnostic Tool for Magentic-UI ===" -ForegroundColor Green
Write-Host "Checking Docker status..." -ForegroundColor Cyan
docker info

Write-Host "`nStopping any running Magentic-UI Docker containers..." -ForegroundColor Cyan
docker stop $(docker ps -q --filter "ancestor=magentic-ui-python-env") 2>$null
docker stop $(docker ps -q --filter "ancestor=magentic-ui-vnc-browser") 2>$null

Write-Host "`nRemoving any existing Magentic-UI network configuration..." -ForegroundColor Cyan
docker network prune -f

Write-Host "`nCreating a dedicated bridge network for Magentic-UI..." -ForegroundColor Cyan
docker network create magentic-ui-network

Write-Host "`nVerifying network configuration..." -ForegroundColor Cyan
docker network ls

Write-Host "`nStarting Magentic-UI with custom network..." -ForegroundColor Cyan
Write-Host "Now run: magentic ui --port 8083 --config d:\0GH_PROD\darbot-netic\config.yaml" -ForegroundColor Yellow

Write-Host "`nTo view the Docker logs after starting Magentic-UI, run:" -ForegroundColor Cyan
Write-Host "docker logs -f $(docker ps -q --filter 'ancestor=magentic-ui-vnc-browser' | select -First 1)" -ForegroundColor Yellow
