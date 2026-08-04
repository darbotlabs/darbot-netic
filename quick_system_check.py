#!/usr/bin/env python3
"""
Quick system check for Magentic-UI
This script performs a simplified verification of key system components:
1. API server health
2. Session creation
3. WebSocket connectivity
"""

import asyncio
import json
import requests
import websockets
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8085"
API_BASE = f"{BASE_URL}/api"
WS_BASE = "ws://localhost:8085/api/ws"
USER_ID = "test@example.com"


def print_status(message, status="INFO"):
    """Print status messages with timestamp and formatting"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Add emoji indicators for better readability
    emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARN": "⚠️"
    }.get(status, "")
    
    print(f"[{timestamp}] {emoji} {status}: {message}")


async def check_system():
    """Perform a quick system check"""
    test_results = {
        "api_health": False,
        "session_creation": False,
        "websocket": False
    }
    
    # Step 1: Check API health
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200 and response.json().get("status"):
            print_status("API server is healthy", "SUCCESS")
            test_results["api_health"] = True
        else:
            print_status(
                f"API health check failed: {response.status_code}",
                "ERROR"
            )
    except Exception as e:
        print_status(f"Health check error: {e}", "ERROR")
    
    if not test_results["api_health"]:
        print_status("API is not responding, aborting further tests", "ERROR")
        return test_results
    
    # Step 2: Create a session
    try:
        session_name = f"Quick Check - {datetime.now().strftime('%H:%M:%S')}"
        payload = {
            "name": session_name,
            "user_id": USER_ID,
            "agent_config": {
                "model": "studio-cat",
                "provider": "AzureOpenAIChatCompletionClient"
            }
        }
        response = requests.post(f"{API_BASE}/sessions/", json=payload)
        
        if response.status_code == 200 and response.json().get("status"):
            session = response.json().get("data")
            print_status(f"Session created with ID: {session['id']}", "SUCCESS")
            test_results["session_creation"] = True
            session_id = session["id"]
        else:
            print_status("Session creation failed", "ERROR")
            return test_results
            
        # Create a run for WebSocket testing
        run_payload = {"session_id": session_id, "user_id": USER_ID}
        run_response = requests.post(f"{API_BASE}/runs/", json=run_payload)
        
        if run_response.status_code != 200:
            print_status("Run creation failed", "ERROR")
            return test_results
            
        run = run_response.json().get("data", {})
        if isinstance(run, dict):
            run_id = run.get("run_id") or run.get("id")
        else:
            run_id = run
            
        if not run_id:
            print_status("Failed to extract run ID", "ERROR")
            return test_results
            
        print_status(f"Created run with ID: {run_id}", "SUCCESS")
        
        # Step 3: Test WebSocket connectivity
        try:
            uri = f"{WS_BASE}/runs/{run_id}"
            print_status(f"Testing WebSocket connection to {uri}")
            
            async with websockets.connect(uri, open_timeout=5) as websocket:
                print_status("WebSocket connection established", "SUCCESS")
                
                # Send a ping message
                ping = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(ping))
                
                # Wait for response
                response = await asyncio.wait_for(
                    websocket.recv(), timeout=5.0
                )
                data = json.loads(response)
                # Any response means WebSocket is working
                print_status(f"Received: {data.get('type')}", "SUCCESS")
                test_results["websocket"] = True
                
        except Exception as e:
            print_status(f"WebSocket connection error: {e}", "ERROR")
            
    except Exception as e:
        print_status(f"Session/run creation error: {e}", "ERROR")
        
    return test_results


def print_summary(results):
    """Print test results summary"""
    print("\n==================================")
    print("📊 QUICK SYSTEM CHECK SUMMARY 📊")
    print("==================================")
    
    for test, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status:<10} | {test}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All systems operational! 🎉")
    else:
        print("\n🔧 Some systems require attention 🔧")


async def main():
    print("\n==================================")
    print("🔍 MAGENTIC-UI QUICK SYSTEM CHECK 🔍")
    print("==================================\n")
    
    results = await check_system()
    print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
