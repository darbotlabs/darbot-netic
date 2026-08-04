# WebSocket connection test script for Magentic-UI
# This script tests whether the WebSocket connections are working properly

# Add command line parameter to skip Docker checks
param(
    [switch]$SkipDocker,
    [string]$Hostname = "localhost",
    [int]$Port = 8085,
    [int]$RunId = 9
)

# Test function for WebSocket connection
function Test-WebSocketConnection {
    param (
        [string]$Hostname = "localhost",
        [int]$Port = 8085
    )

    try {        Write-Host "Testing TCP connectivity to ${Hostname}:${Port}..." -ForegroundColor Cyan
        $tcpTest = Test-NetConnection -ComputerName $Hostname -Port $Port -WarningAction SilentlyContinue
        
        if ($tcpTest.TcpTestSucceeded) {
            Write-Host "✅ TCP connection to ${Hostname}:${Port} is SUCCESSFUL" -ForegroundColor Green
        } else {
            Write-Host "❌ TCP connection to ${Hostname}:${Port} FAILED" -ForegroundColor Red
            Write-Host "  Error: $($tcpTest.CommonTCPPort)" -ForegroundColor Red
            return $false
        }
        
        return $true
    }
    catch {
        Write-Host "❌ Error testing connection: $_" -ForegroundColor Red
        return $false
    }
}

# Function to check Docker container status
function Get-DockerContainerStatus {
    param (
        [string]$ImageName
    )
    
    try {
        $containers = Invoke-DockerWithTimeout "docker ps -a --filter `"ancestor=$ImageName`" --format `"{{.ID}}|{{.Status}}|{{.Ports}}`""
        
        if (-not $containers) {
            Write-Host "No containers found for image: $ImageName" -ForegroundColor Yellow
            return $null
        }
        
        $containerList = @()
        foreach ($container in $containers -split "`n") {
            if ($container.Trim()) {
                $parts = $container -split "\|"
                $containerInfo = @{
                    ID = $parts[0]
                    Status = $parts[1]
                    Ports = $parts[2]
                }
                $containerList += $containerInfo
                
                $statusColor = if ($containerInfo.Status -match "Up") { "Green" } else { "Red" }
                Write-Host "Container ID: $($containerInfo.ID)" -ForegroundColor Cyan
                Write-Host "  Status: $($containerInfo.Status)" -ForegroundColor $statusColor
                Write-Host "  Ports: $($containerInfo.Ports)" -ForegroundColor Cyan
            }
        }
        
        return $containerList
    }
    catch {
        Write-Host "❌ Error checking Docker container status: $_" -ForegroundColor Red
        return $null
    }
}

# Function to get container logs
function Get-ContainerLogs {
    param (
        [string]$ContainerId,
        [int]$Lines = 20
    )
    
    try {
        Write-Host "Fetching logs for container $ContainerId (last $Lines lines)..." -ForegroundColor Cyan
        $logs = Invoke-DockerWithTimeout "docker logs --tail $Lines $ContainerId"
        return $logs
    }
    catch {
        Write-Host "❌ Error fetching container logs: $_" -ForegroundColor Red
        return $null
    }
}

# Function to test actual WebSocket endpoint with Python
function Test-WebSocketEndpoint {
    param (
        [string]$Hostname = "localhost",
        [int]$Port = 8085,
        [int]$RunId = 9
    )

    try {
        Write-Host "Testing actual WebSocket endpoint: ws://${Hostname}:${Port}/api/ws/runs/${RunId}" -ForegroundColor Cyan
          # Create a temporary Python script to test WebSocket
        $pythonScript = @"
import asyncio
import websockets
import json
import sys

async def test_websocket():
    uri = f"ws://${Hostname}:${Port}/api/ws/runs/${RunId}"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connection established successfully!")
            
            # Send a test message
            test_message = {"type": "test", "message": "Hello WebSocket!"}
            await websocket.send(json.dumps(test_message))
            print(f"Sent test message: {test_message}")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"Received response: {response}")
            
            return True
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    sys.exit(0 if result else 1)
"@

        # Write the Python script to a temporary file
        $tempScript = "$env:TEMP\test_websocket_temp.py"
        $pythonScript | Out-File -FilePath $tempScript -Encoding UTF8
        
        # Run the Python script
        $result = python $tempScript
        Write-Host $result
        
        # Clean up
        Remove-Item $tempScript -ErrorAction SilentlyContinue
        
        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-Host "❌ Error testing WebSocket endpoint: $_" -ForegroundColor Red
        return $false
    }
}

# Function to run Docker commands with timeout
function Invoke-DockerWithTimeout {
    param (
        [string]$Command,
        [int]$TimeoutSeconds = 10
    )
    
    try {
        $job = Start-Job -ScriptBlock { 
            param($cmd)
            Invoke-Expression $cmd
        } -ArgumentList $Command
        
        if (Wait-Job $job -Timeout $TimeoutSeconds) {
            $result = Receive-Job $job
            Remove-Job $job
            return $result
        } else {
            Remove-Job $job -Force
            Write-Host "❌ Docker command timed out after $TimeoutSeconds seconds" -ForegroundColor Red
            return $null
        }
    }
    catch {
        Write-Host "❌ Error running Docker command: $_" -ForegroundColor Red
        return $null
    }
}

# Main diagnostic routine
Write-Host "===== Magentic-UI WebSocket Connection Diagnostic Tool =====" -ForegroundColor Green
Write-Host "Usage: .\websocket_diagnostics.ps1 [-SkipDocker] [-Hostname localhost] [-Port 8085] [-RunId 9]" -ForegroundColor Yellow

if ($SkipDocker) {
    Write-Host "⚠️  Skipping Docker checks (-SkipDocker flag specified)" -ForegroundColor Yellow
    $dockerAvailable = $false
} else {
    $dockerAvailable = $true
}

# Only run Docker steps if Docker is available
if ($dockerAvailable) {
    # Step 1: Check if required Docker images exist
    Write-Host "`nStep 1: Checking if required Docker images exist..." -ForegroundColor Cyan

    # Check if Docker is running first
    try {
        $dockerInfo = Invoke-DockerWithTimeout "docker info --format '{{.ServerVersion}}'" -TimeoutSeconds 5
        if ($dockerInfo) {
            Write-Host "✅ Docker is running (version: $dockerInfo)" -ForegroundColor Green
        } else {
            Write-Host "❌ Docker is not responding or not installed" -ForegroundColor Red
            Write-Host "  Skipping Docker-related checks..." -ForegroundColor Yellow
            $dockerAvailable = $false
        }
    } catch {
        Write-Host "❌ Cannot communicate with Docker daemon" -ForegroundColor Red
        Write-Host "  Skipping Docker-related checks..." -ForegroundColor Yellow
        $dockerAvailable = $false
    }

    if ($dockerAvailable -ne $false) {
        $vncBrowserImage = Invoke-DockerWithTimeout 'docker images "magentic-ui-vnc-browser" --format "{{.Repository}}:{{.Tag}}"'
        $pythonEnvImage = Invoke-DockerWithTimeout 'docker images "magentic-ui-python-env" --format "{{.Repository}}:{{.Tag}}"'

        if ($vncBrowserImage) {
            Write-Host "✅ Found VNC browser image: $vncBrowserImage" -ForegroundColor Green
        } else {
            Write-Host "❌ VNC browser image not found" -ForegroundColor Red
        }

        if ($pythonEnvImage) {
            Write-Host "✅ Found Python environment image: $pythonEnvImage" -ForegroundColor Green
        } else {
            Write-Host "❌ Python environment image not found" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  Skipping Docker image checks (Docker not available)" -ForegroundColor Yellow
    }

    # Step 2: Check Docker network configuration
    Write-Host "`nStep 2: Checking Docker network configuration..." -ForegroundColor Cyan

    if ($dockerAvailable -ne $false) {
        $networks = Invoke-DockerWithTimeout 'docker network ls --filter "name=magentic-ui-network" --format "{{.Name}}|{{.Driver}}"'

        if ($networks) {
            foreach ($network in $networks -split "`n") {
                $parts = $network -split "\|"
                if ($parts[0]) {
                    Write-Host "✅ Found network: $($parts[0]), Driver: $($parts[1])" -ForegroundColor Green
                }
            }
            
            # Get network details with timeout
            $networkDetailsJson = Invoke-DockerWithTimeout "docker network inspect magentic-ui-network"
            if ($networkDetailsJson) {
                try {
                    $networkDetails = $networkDetailsJson | ConvertFrom-Json
                    Write-Host "  Network ID: $($networkDetails.Id)" -ForegroundColor Cyan
                    Write-Host "  Subnet: $($networkDetails.IPAM.Config.Subnet)" -ForegroundColor Cyan
                    Write-Host "  Gateway: $($networkDetails.IPAM.Config.Gateway)" -ForegroundColor Cyan
                } catch {
                    Write-Host "  Network details available but couldn't parse" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "❌ magentic-ui-network not found" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  Skipping Docker network checks (Docker not available)" -ForegroundColor Yellow
    }

    # Step 3: Check container status
    Write-Host "`nStep 3: Checking container status..." -ForegroundColor Cyan

    if ($dockerAvailable -ne $false) {
        Write-Host "VNC Browser Containers:" -ForegroundColor Cyan
        $vncContainers = Get-DockerContainerStatus "magentic-ui-vnc-browser"

        Write-Host "`nPython Environment Containers:" -ForegroundColor Cyan
        $pythonContainers = Get-DockerContainerStatus "magentic-ui-python-env"    } else {
        Write-Host "⚠️  Skipping Docker container checks (Docker not available)" -ForegroundColor Yellow
        $vncContainers = $null
    }

    # End Docker steps
} else {
    Write-Host "⚠️  All Docker checks skipped (SkipDocker flag specified)" -ForegroundColor Yellow
    $vncContainers = $null
}

# Step 4: Test WebSocket connection
Write-Host "`nStep 4: Testing WebSocket connection..." -ForegroundColor Cyan
$wsTest = Test-WebSocketConnection -Hostname $Hostname -Port $Port
if ($wsTest) {
    Write-Host "✅ WebSocket port is accessible" -ForegroundColor Green
    
    # Test the actual WebSocket endpoint
    Write-Host "`nStep 4b: Testing WebSocket endpoint with run ID..." -ForegroundColor Cyan
    $wsEndpointTest = Test-WebSocketEndpoint -Hostname $Hostname -Port $Port -RunId $RunId
    
    if ($wsEndpointTest) {
        Write-Host "✅ WebSocket endpoint test completed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ WebSocket endpoint test failed - check if server is running with valid run ID" -ForegroundColor Red
    }
} else {
    Write-Host "❓ WebSocket port test failed, checking container logs for more information..." -ForegroundColor Yellow
    
    if ($vncContainers -and $dockerAvailable) {
        $containerId = $vncContainers[0].ID
        Write-Host "`nVNC Browser Container Logs:" -ForegroundColor Cyan
        $logs = Get-ContainerLogs -ContainerId $containerId
        $logs | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Host "  No container logs available (Docker not accessible or no containers found)" -ForegroundColor Yellow
    }
}

# Step 5: Network diagnostic summary
Write-Host "`nStep 5: Network Diagnostic Summary" -ForegroundColor Cyan

# Check host IP configuration
Write-Host "`nHost Network Configuration:" -ForegroundColor Cyan
$ipConfig = Get-NetIPAddress | Where-Object { $_.InterfaceAlias -match 'Ethernet|Wi-Fi' -and $_.AddressFamily -eq 'IPv4' }
$ipConfig | ForEach-Object {
    Write-Host "  Interface: $($_.InterfaceAlias), IP: $($_.IPAddress)" -ForegroundColor Yellow
}

# Print recommendations
Write-Host "`n===== Diagnostic Results and Next Steps =====" -ForegroundColor Green

if (-not $wsTest) {
    Write-Host "❌ WebSocket connection issue detected. Recommended fixes:" -ForegroundColor Red
    Write-Host "  1. Run the docker_network_fix_v2.ps1 script to reset Docker networking" -ForegroundColor Yellow
    Write-Host "  2. Ensure no other application is using port 8085" -ForegroundColor Yellow
    Write-Host "  3. Try using the --docker-network magentic-ui-network flag when starting Magentic-UI" -ForegroundColor Yellow
    Write-Host "  4. Try using --inside-docker false flag if running inside WSL or another Docker container" -ForegroundColor Yellow
} else {
    Write-Host "✅ Network diagnostic completed successfully" -ForegroundColor Green
    Write-Host "  You can now run Magentic-UI with the following command:" -ForegroundColor Yellow
    Write-Host "  magentic ui --port 8083 --config d:\0GH_PROD\darbot-netic\config.yaml --docker-network magentic-ui-network" -ForegroundColor Yellow
}

Write-Host "`nFor VNC browser access, open: http://localhost:6080/?autoconnect=1" -ForegroundColor Cyan
