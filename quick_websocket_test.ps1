# Quick WebSocket Test Script - bypasses Docker checks
# This script only tests the WebSocket connection without Docker overhead

param(
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

    try {
        Write-Host "Testing TCP connectivity to ${Hostname}:${Port}..." -ForegroundColor Cyan
        $tcpTest = Test-NetConnection -ComputerName $Hostname -Port $Port -WarningAction SilentlyContinue
        
        if ($tcpTest.TcpTestSucceeded) {
            Write-Host "✅ TCP connection to ${Hostname}:${Port} is SUCCESSFUL" -ForegroundColor Green
        } else {
            Write-Host "❌ TCP connection to ${Hostname}:${Port} FAILED" -ForegroundColor Red
            Write-Host "  Error: Port may not be listening or service is down" -ForegroundColor Red
            return $false
        }
        
        return $true
    }
    catch {
        Write-Host "❌ Error testing connection: $_" -ForegroundColor Red
        return $false
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
        Write-Host "Testing actual WebSocket endpoint: ws://${Hostname}:${Port}/api/ws/runs/${RunId}" -ForegroundColor Cyan        # Create a temporary Python script to test WebSocket
        $pythonScript = @"
import asyncio
import websockets
import json
import sys

async def test_websocket():
    uri = f"ws://${Hostname}:${Port}/api/ws/runs/${RunId}"
    try:
        async with websockets.connect(uri) as websocket:
            print("SUCCESS: WebSocket connection established successfully!")
            
            # Send a test message
            test_message = {"type": "test", "message": "Hello WebSocket!"}
            await websocket.send(json.dumps(test_message))
            print(f"SENT: Test message: {test_message}")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"RECEIVED: Response: {response}")
            
            return True
    except Exception as e:
        print(f"FAILED: WebSocket connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    sys.exit(0 if result else 1)
"@

        # Write the Python script to a temporary file
        $tempScript = "$env:TEMP\test_websocket_quick.py"
        $pythonScript | Out-File -FilePath $tempScript -Encoding UTF8
        
        # Run the Python script
        $result = python $tempScript 2>&1
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

# Main quick test routine
Write-Host "===== Quick WebSocket Test (No Docker Checks) =====" -ForegroundColor Green
Write-Host "Testing WebSocket at: ${Hostname}:${Port} with Run ID: ${RunId}" -ForegroundColor Cyan

# Test WebSocket connection
Write-Host "`nStep 1: Testing WebSocket port connectivity..." -ForegroundColor Cyan
$wsTest = Test-WebSocketConnection -Hostname $Hostname -Port $Port

if ($wsTest) {
    Write-Host "✅ WebSocket port is accessible" -ForegroundColor Green
    
    # Test the actual WebSocket endpoint
    Write-Host "`nStep 2: Testing WebSocket endpoint..." -ForegroundColor Cyan
    $wsEndpointTest = Test-WebSocketEndpoint -Hostname $Hostname -Port $Port -RunId $RunId
    
    if ($wsEndpointTest) {
        Write-Host "✅ WebSocket endpoint test completed successfully" -ForegroundColor Green
        Write-Host "`n🎉 SUCCESS! WebSocket connection is working properly!" -ForegroundColor Green
    } else {
        Write-Host "❌ WebSocket endpoint test failed" -ForegroundColor Red
        Write-Host "  Possible causes:" -ForegroundColor Yellow
        Write-Host "  - Server is not running" -ForegroundColor Yellow
        Write-Host "  - Run ID ${RunId} does not exist in the database" -ForegroundColor Yellow
        Write-Host "  - WebSocket endpoint is not properly configured" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ WebSocket port is not accessible" -ForegroundColor Red
    Write-Host "  Possible causes:" -ForegroundColor Yellow
    Write-Host "  - Service is not running on port ${Port}" -ForegroundColor Yellow
    Write-Host "  - Port is blocked by firewall" -ForegroundColor Yellow
    Write-Host "  - Wrong hostname or port specified" -ForegroundColor Yellow
}

Write-Host "`n===== Quick Test Complete =====" -ForegroundColor Green
