#!/usr/bin/env python3
"""
Comprehensive test script for Magentic-UI system verification.
This script tests:
1. API server health
2. API version
3. Session creation
4. Run creation
5. WebSocket communication
6. Task execution and agent response
7. Message storage verification
8. Plans API functionality
"""

import asyncio
import json
import websockets
import time
import requests
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
        "WARN": "⚠️",
        "RECV": "📩"
    }.get(status, "")
    
    print(f"[{timestamp}] {emoji} {status}: {message}")


async def check_health():
    """Check API server health"""
    print("\n=== Step 1: Checking API Server Health ===")
    url = f"{API_BASE}/health"
    
    try:
        response = requests.get(url)
        if response.status_code == 200 and response.json().get("status"):
            print_status("API server is healthy", "SUCCESS")
            return True
        else:
            print_status(
                f"API health check failed: {response.status_code}",
                "ERROR"
            )
            return False
    except Exception as e:
        print_status(f"Health check error: {e}", "ERROR")
        return False


async def get_api_version():
    """Get API version"""
    print("\n=== Step 2: Checking API Version ===")
    url = f"{API_BASE}/version"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            version_info = response.json()
            print_status(
                f"API Version: {version_info.get('version')}",
                "SUCCESS"
            )
            return True
        else:
            print_status(
                f"Version check failed: {response.status_code}",
                "ERROR"
            )
            return False
    except Exception as e:
        print_status(f"Version check error: {e}", "ERROR")
        return False


async def create_session():
    """Create a new session"""
    print("\n=== Step 3: Creating User Session ===")
    url = f"{API_BASE}/sessions/"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session_name = f"Functionality Test - {timestamp}"
    
    payload = {
        "name": session_name,
        "user_id": USER_ID,
        "agent_config": {
            "model": "studio-cat",
            "provider": "AzureOpenAIChatCompletionClient"
        }
    }
    
    try:
        print_status(f"Creating session '{session_name}'...")
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            print_status(
                f"Session creation failed: {response.status_code}",
                "ERROR"
            )
            return None
        
        response_data = response.json()
        if not response_data.get("status"):
            print_status(f"API error: {response_data.get('message')}", "ERROR")
            return None
        
        session = response_data.get("data")
        print_status(f"Created session with ID: {session['id']}", "SUCCESS")
        return session
    except Exception as e:
        print_status(f"Session creation error: {e}", "ERROR")
        return None


async def create_run(session_id):
    """Create a run for the session"""
    print("\n=== Step 4: Creating Run for Session ===")
    url = f"{API_BASE}/runs/"
    payload = {
        "session_id": session_id,
        "user_id": USER_ID
    }
    
    try:
        print_status("Creating run for session...")
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print_status(
                f"Run creation failed: {response.status_code}",
                "ERROR"
            )
            return None
        
        response_data = response.json()
        if not response_data.get("status"):
            print_status(f"API error: {response_data.get('message')}", "ERROR")
            return None
        
        run = response_data.get("data", {})
        # Extract run_id from different possible API response formats
        if isinstance(run, dict):
            run_id = run.get("run_id") or run.get("id")
        else:
            # If run is returned directly as an integer
            run_id = run
            
        if not run_id:
            print_status("No run_id in response", "ERROR")
            print_status(f"Response data: {response_data}", "INFO")
            return None
        
        print_status(f"Created run with ID: {run_id}", "SUCCESS")
        return run_id
    except Exception as e:
        print_status(f"Run creation error: {e}", "ERROR")
        return None


async def test_websocket_communication(run_id):
    """Test WebSocket functionality"""
    print("\n=== Step 5: Testing WebSocket Communication ===")
    uri = f"{WS_BASE}/runs/{run_id}"
    
    print_status(f"Connecting to WebSocket: {uri}")
    
    try:
        # Set reasonable timeouts to prevent hanging
        async with websockets.connect(uri, open_timeout=10) as websocket:
            print_status("WebSocket connection established", "SUCCESS")
            
            # Send a start message
            start_message = {
                "type": "start",
                "task": (
                    "Hello! This is a functionality test. "
                    "Please respond with a simple greeting and "
                    "list the tools you have available. "
                    "Keep your response brief."
                ),
                "files": [],
                "team_config": {
                    "cooperative_planning": True,
                    "autonomous_execution": False
                },
                "settings_config": {
                    "max_turns": 3
                }
            }
            
            print_status("Sending start message...")
            await websocket.send(json.dumps(start_message))
            print_status("Start message sent", "SUCCESS")
            
            # Wait for responses
            print_status("Waiting for server responses (max 30 seconds)...")
            start_time = time.time()
            max_wait = 30  # seconds
            message_count = 0
            messages = []
            
            while time.time() - start_time < max_wait:
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=1.0
                    )
                    data = json.loads(response)
                    message_count += 1
                    messages.append(data)
                    
                    message_type = data.get('type', 'unknown')
                    
                    if message_type == 'message':
                        sender = data.get('data', {}).get('sender', 'Unknown')
                        content_raw = data.get('data', {}).get('content', '')
                        content = content_raw[:50]
                        if len(content_raw) > 50:
                            content += "..."
                        print_status(
                            f"Message from '{sender}': {content}",
                            "RECV"
                        )
                    
                    elif message_type == 'run_status':
                        status = data.get('data', {}).get('status', 'unknown')
                        print_status(f"Run status update: {status}", "INFO")
                        
                        if status in ["completed", "failed"]:
                            print_status(
                                f"Run completed with status: {status}",
                                "SUCCESS"
                            )
                            break
                    
                    elif message_type == 'system':
                        sys_data = data.get('data', {})
                        print_status(
                            f"System message: {sys_data}",
                            "INFO"
                        )
                    
                    elif message_type == 'error':
                        error = data.get('error', 'Unknown error')
                        print_status(f"Error received: {error}", "ERROR")
                    
                    elif message_type == 'completion':
                        print_status("Task completion received", "SUCCESS")
                        break
                    
                    else:
                        print_status(
                            f"Unknown message type: {message_type}",
                            "WARN"
                        )
                    
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
                    continue
                except Exception as e:
                    print_status(f"Error receiving message: {e}", "ERROR")
                    break
            
            print(f"\nReceived {message_count} messages in total")
            return message_count > 0, messages
    
    except websockets.exceptions.WebSocketException as e:
        print_status(
            f"WebSocket connection error: {e}",
            "ERROR"
        )
        return False, []
    except ConnectionRefusedError:
        print_status("Connection refused - server not running?", "ERROR")
        return False, []
    except Exception as e:
        print_status(f"WebSocket connection error: {e}", "ERROR")
        return False, []


async def verify_messages_stored(run_id):
    """Verify that messages were stored in the database"""
    print("\n=== Step 6: Verifying Messages Storage ===")
    url = f"{API_BASE}/runs/{run_id}/messages"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print_status(
                f"Failed to retrieve messages: {response.status_code}",
                "ERROR"
            )
            return False
        
        response_data = response.json()
        if not response_data.get("status"):
            print_status("API error retrieving messages", "ERROR")
            return False
        
        messages = response_data.get("data", [])
        if not messages:
            print_status("No messages found in database", "WARN")
            print_status("Verifying message db table structure...", "INFO")
            
            # Inspect the run data directly to confirm the structure
            run_url = f"{API_BASE}/runs/{run_id}"
            run_response = requests.get(run_url)
            if run_response.status_code == 200:
                run_data = run_response.json().get("data", {})
                print_status(f"Run data: {run_data}", "INFO")
                
                # The run itself should have a task field that contains the initial message
                if "task" in run_data and run_data["task"]:
                    print_status("Found task in run data, which should be saved as a message", "INFO")
            
            return False
        
        print_status(f"Found {len(messages)} messages in database", "SUCCESS")
        for i, msg in enumerate(messages[:5]):  # Show first 5 messages
            config = msg.get("config", {})
            src = config.get("source", "unknown")
            content = config.get("content", "")[:50]
            print_status(f"Message {i+1}: {src} -> {content}...", "INFO")
            
        return True
    except Exception as e:
        print_status(f"Message verification failed: {e}", "ERROR")
        return False


async def test_plans_api():
    """Test plans API functionality"""
    print("\n=== Step 7: Testing Plans API ===")
    url = f"{API_BASE}/plans/?user_id={USER_ID}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print_status(f"Plans API failed: {response.status_code}", "ERROR")
            return False
            
        response_data = response.json()
        if not response_data.get("status"):
            print_status("API error retrieving plans", "ERROR")
            return False
            
        plans = response_data.get("data", [])
        print_status(f"Plans API working, found {len(plans)} plans", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Plans API test failed: {e}", "ERROR")
        return False


async def debug_database_messages():
    """Debug helper to check the messages table in the database"""
    print("\n=== Debug: Checking Messages Table ===")
    url = f"{API_BASE}/debug/messages"
    
    try:
        print_status("Checking if debug endpoint exists...")
        response = requests.get(url)
        if response.status_code == 404:
            print_status("Debug endpoint not available", "WARN")
            return False
            
        if response.status_code != 200:
            print_status(f"Debug endpoint failed: {response.status_code}", "ERROR")
            return False
            
        messages = response.json().get("data", [])
        print_status(f"Found {len(messages)} total messages in database", "INFO")
        return True
    except Exception as e:
        print_status(f"Debug query failed: {e}", "WARN")
        return False


async def main():
    """Main test function"""
    print("\n============================================")
    print("🧪 MAGENTIC-UI SYSTEM FUNCTIONALITY TEST 🧪")
    print("============================================")
    
    test_results = {
        "health": False,
        "version": False,
        "session": False,
        "run": False,
        "websocket": False,
        "messages": False,
        "plans": False
    }
    
    # Step 1: Check API health
    test_results["health"] = await check_health()
    if not test_results["health"]:
        print_status("Test aborted: API server is not healthy", "ERROR")
        print_summary(test_results)
        return
    
    # Step 2: Get API version
    test_results["version"] = await get_api_version()
    
    # Step 3: Create a session
    session = await create_session()
    test_results["session"] = bool(session)
    if not session:
        print_status("Test aborted: Failed to create session", "ERROR")
        print_summary(test_results)
        return
    
    # Step 4: Create a run
    run_id = await create_run(session["id"])
    test_results["run"] = bool(run_id)
    if not run_id:
        print_status("Test aborted: Failed to create run", "ERROR")
        print_summary(test_results)
        return
    
    # Step 5: Test WebSocket communication
    success, messages = await test_websocket_communication(run_id)
    test_results["websocket"] = success
    if not success:
        print_status("Warning: WebSocket communication had issues", "WARN")
        # Continue with other tests
    
    # Step 6: Verify messages were stored
    test_results["messages"] = await verify_messages_stored(run_id)
    
    # Try debug database messages (optional)
    await debug_database_messages()
    
    # Step 7: Test plans API
    test_results["plans"] = await test_plans_api()
    
    # Print summary
    print_summary(test_results)


def print_summary(results):
    """Print test results summary"""
    print("\n============================================")
    print("🧪 FUNCTIONALITY AUDIT SUMMARY 🧪")
    print("============================================")
    
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        emoji = "✅" if passed else "❌"
        print(f"{emoji} {test.capitalize()}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 Overall Status: ALL TESTS PASSED 🎉")
    else:
        print("\n⚠️ Overall Status: SOME TESTS FAILED ⚠️")
        
        # Provide recommendations for failures
        if not results.get("health"):
            print("\nRecommendation for API health issue:")
            print("- Check if the Magentic-UI server is running")
            print("- Verify the PORT setting in run_magentic_ui.ps1")
        
        if not results.get("session"):
            print("\nRecommendation for session creation issue:")
            print("- Check database connectivity")
            print("- Verify user authentication flow")
            
        if not results.get("run"):
            print("\nRecommendation for run creation issue:")
            print("- Check session_id is correct format")
            print("- Verify run creation API endpoint implementation")
        
        if not results.get("websocket"):
            print("\nRecommendation for WebSocket connection issue:")
            print("- Verify run_id exists in database")
            print("- Check WebSocket endpoint implementation")
            print("- Ensure Docker containers for agents are running")
        
        if not results.get("messages"):
            print("\nRecommendation for message storage issue:")
            print("- The WebSocket message flow is working, but messages")
            print("  aren't being properly saved to the database")
            print("- Check the _save_message implementation in connection.py")
            print("- Ensure the Message model is properly defined")
            print("- Verify database transactions are being committed")
        
        if not results.get("plans"):
            print("\nRecommendation for plans API issue:")
            print("- Check plans database schema and implementation")
            print("- Verify user_id parameter is being correctly handled")


if __name__ == "__main__":
    asyncio.run(main())
