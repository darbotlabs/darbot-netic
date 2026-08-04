# PowerShell script to launch Magentic-UI with proper Docker network configuration
# This script sets up Docker networking and then runs Magentic-UI

# Set configuration variables
$CONFIG_PATH = "d:\0GH_PROD\darbot-netic\config.yaml"
$PORT = 8085  # Using a different port to avoid conflicts
$NETWORK_NAME = "magentic-ui-network"
$USE_EXISTING = $true  # Set to true to use existing containers

# Display banner
Write-Host "=== Magentic-UI Launcher with Docker Network Configuration ===" -ForegroundColor Green

# Step 1: Ensure Docker is running
Write-Host "Step 1: Checking Docker status..." -ForegroundColor Cyan
$dockerRunning = $false
try {
    docker info > $null 2>&1
    $dockerRunning = $true
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Step 2: Set up Docker network
Write-Host "`nStep 2: Setting up Docker network..." -ForegroundColor Cyan
$networkExists = docker network ls --filter name=$NETWORK_NAME -q

if (-not $networkExists) {
    Write-Host "Creating Docker network: $NETWORK_NAME" -ForegroundColor Yellow
    docker network create --driver bridge $NETWORK_NAME
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create Docker network" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Docker network $NETWORK_NAME exists" -ForegroundColor Green
}

# Step 3: Only stop processes, don't stop containers if using existing ones
Write-Host "`nStep 3: Stopping existing Magentic-UI processes..." -ForegroundColor Cyan

# Kill any existing magentic processes
Write-Host "Stopping any running magentic processes..." -ForegroundColor Yellow
$magenticProcesses = Get-Process -Name "*magentic*", "*uvicorn*", "*python*" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*magentic ui*" -or $_.CommandLine -like "*uvicorn*" }
if ($magenticProcesses) {
    $magenticProcesses | ForEach-Object { 
        try {
            $_ | Stop-Process -Force
            Write-Host "Stopped process: $($_.Name) (PID: $($_.Id))" -ForegroundColor Yellow
        } catch {
            Write-Host "Could not stop process: $($_.Name) (PID: $($_.Id))" -ForegroundColor Red
        }
    }
    # Give processes time to shut down
    Start-Sleep -Seconds 2
}

# Only stop Docker containers if not using existing ones
if (-not $USE_EXISTING) {
    # Stop Docker containers
    $vncContainers = docker ps -q --filter "ancestor=magentic-ui-vnc-browser"
    $pythonContainers = docker ps -q --filter "ancestor=magentic-ui-python-env"

    if ($vncContainers -or $pythonContainers) {
        if ($vncContainers) {
            docker stop $vncContainers
            Write-Host "Stopped VNC browser containers" -ForegroundColor Yellow
        }
        if ($pythonContainers) {
            docker stop $pythonContainers
            Write-Host "Stopped Python environment containers" -ForegroundColor Yellow
        }
    } else {
        Write-Host "No running Magentic-UI containers found" -ForegroundColor Green
    }
} else {
    Write-Host "Keeping existing Docker containers running" -ForegroundColor Green
    # List the running containers
    Write-Host "Current running containers:" -ForegroundColor Cyan
    docker ps --filter "ancestor=magentic-ui" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
}


# Step 4: Start or restart the magentic-ui-vnc-browser container with correct ports and network
Write-Host "`nStep 4: Ensuring magentic-ui-vnc-browser container is running with correct ports..." -ForegroundColor Cyan
$browserContainerName = "magentic-ui-vnc-browser"
$browserImage = "magentic-ui-vnc-browser:latest"

# Stop any existing container with the same name
if (docker ps -a --format '{{.Names}}' | Select-String -Pattern "^$browserContainerName$") {
    Write-Host "Stopping existing $browserContainerName container..." -ForegroundColor Yellow
    docker stop $browserContainerName | Out-Null
    docker rm $browserContainerName | Out-Null
}

# Start the container with required ports and network
Write-Host "Starting $browserContainerName on ports 4334 (noVNC) and 37367 (Playwright)..." -ForegroundColor Yellow
docker run --rm -d --name $browserContainerName --network $NETWORK_NAME -p 4334:4334 -p 37367:37367 $browserImage | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ $browserContainerName container is running." -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start $browserContainerName container." -ForegroundColor Red
    exit 1
}

# Set environment variables
Write-Host "`nStep 5: Setting environment variables..." -ForegroundColor Cyan
$env:MAGENTIC_UI_DOCKER_NETWORK = $NETWORK_NAME
$env:MAGENTIC_UI_PORT = $PORT
$env:MAGENTIC_UI_CONFIG = $CONFIG_PATH
$env:MAGENTIC_UI_USE_EXISTING_CONTAINERS = if ($USE_EXISTING) { "true" } else { "false" }


# Step 6: Launch Magentic-UI
Write-Host "`nStep 6: Launching Magentic-UI..." -ForegroundColor Cyan
Write-Host "Starting Magentic-UI on port $PORT with config: $CONFIG_PATH" -ForegroundColor Yellow
Write-Host "Using Docker network: $NETWORK_NAME" -ForegroundColor Yellow
Write-Host "Using existing containers: $USE_EXISTING" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C to stop Magentic-UI" -ForegroundColor Cyan
Write-Host "===============================================`n" -ForegroundColor Green

# Run Magentic-UI
magentic ui --port $PORT --config $CONFIG_PATH

# Clean up if the script exits
Write-Host "`nCleaning up..." -ForegroundColor Cyan
