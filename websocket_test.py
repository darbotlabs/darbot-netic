#!/usr/bin/env python3
"""
Simple WebSocket test client to test the Magentic-UI WebSocket API functionality.
"""

import asyncio
import json
import websockets
import time
import requests

# Configuration
API_BASE = "http://localhost:8085/api"
WS_BASE = "ws://localhost:8085/api/ws"
USER_ID = "test@example.com"

async def create_session():
    """Create a new session"""
    url = f"{API_BASE}/sessions/"
    payload = {
        "name": "Test Session",
        "user_id": USER_ID,
        "id": None  # Let the server assign an ID
    }
    
    print(f"Creating session at {url} with payload: {json.dumps(payload)}")
    response = requests.post(url, json=payload)
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Failed to create session: {response.status_code} {response.text}")
        return None
    
    response_data = response.json()
    print(f"Session creation response: {json.dumps(response_data, indent=2)}")
    
    if not response_data.get("status"):
        print(f"API error: {response_data.get('message', 'Unknown error')}")
        return None
    
    session = response_data.get("data")
    print(f"Created session with ID: {session['id']}")
    return session

async def create_run(session_id):
    """Create a run for the session"""
    url = f"{API_BASE}/runs/"
    payload = {
        "session_id": session_id,
        "user_id": USER_ID
    }
    
    print(f"Creating run at {url} with payload: {json.dumps(payload)}")
    response = requests.post(url, json=payload)
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Failed to create run: {response.status_code} {response.text}")
        return None
    
    response_data = response.json()
    print(f"Run creation response: {json.dumps(response_data, indent=2)}")
    
    if not response_data.get("status"):
        print(f"API error: {response_data.get('message', 'Unknown error')}")
        return None
    
    run_id = response_data.get("data", {}).get("run_id")
    if not run_id:
        print(f"No run_id in response")
        return None
        
    print(f"Created run with ID: {run_id}")
    return run_id

async def test_websocket():
    """Test WebSocket functionality"""
    # Step 1: Create a session
    session = await create_session()
    if not session:
        print("Failed to create session")
        return
    
    # Step 2: Create a run
    run_id = await create_run(session["id"])
    if not run_id:
        print("Failed to create run")
        return
    
    # Step 3: Connect to WebSocket
    uri = f"{WS_BASE}/runs/{run_id}"
    
    print(f"=== WebSocket Test for Run ID {run_id} ===")
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connection established")
            
            # Send a message to start the run
            start_message = {
                "type": "start",
                "task": "Hello! This is a functionality test. Please respond with a simple greeting.",
                "files": [],
                "team_config": {
                    "model": "studio-cat",
                    "provider": "AzureOpenAIChatCompletionClient"
                },
                "settings_config": {
                    "max_turns": 3
                }
            }
            
            print("\nSending start message...")
            await websocket.send(json.dumps(start_message))
            print("✅ Start message sent")
            
            # Wait for responses
            print("\nWaiting for responses (30 seconds timeout):")
            start_time = time.time()
            max_wait = 30  # seconds
            message_count = 0
            
            while time.time() - start_time < max_wait:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    message_count += 1
                    
                    print(f"\n--- Message {message_count} ---")
                    print(f"Type: {data.get('type')}")
                    
                    if data.get('type') == 'message':
                        sender = data.get('data', {}).get('sender', 'Unknown')
                        content = data.get('data', {}).get('content', '')
                        print(f"From: {sender}")
                        print(f"Content: {content[:150]}...")
                    
                    elif data.get('type') == 'run_status':
                        status = data.get('data', {}).get('status', 'unknown')
                        print(f"Run status: {status}")
                        
                        if status in ["completed", "failed"]:
                            print(f"\n✅ Run completed with status: {status}")
                            break
                    
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
                    continue
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    break
            
            print(f"\n\nReceived {message_count} messages in {time.time() - start_time:.1f} seconds")
            if message_count == 0:
                print("❌ No messages received from server")
            else:
                print("✅ Test completed successfully")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
