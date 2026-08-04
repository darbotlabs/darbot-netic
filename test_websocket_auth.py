import websocket
import requests
import json
import time
import sys

# Configuration
API_BASE = "http://localhost:8085/api"
WS_BASE = "ws://localhost:8085/api/ws"
USER_ID = "test@example.com"

def create_session():
    """Create a new session"""
    url = f"{API_BASE}/sessions/?user_id={USER_ID}"
    payload = {
        "name": "Test Session",
        "user_id": USER_ID
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Failed to create session: {response.status_code} {response.text}")
        return None
    
    response_data = response.json()
    if not response_data.get("status"):
        print(f"API error: {response_data.get('message', 'Unknown error')}")
        return None
    
    session = response_data.get("data")
    print(f"Created session with ID: {session['id']}")
    return session

def create_run(session_id):
    """Create a run for the session"""
    url = f"{API_BASE}/runs/"
    payload = {
        "session_id": session_id,
        "user_id": USER_ID
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Failed to create run: {response.status_code} {response.text}")
        return None
    
    response_data = response.json()
    print(f"Run creation response: {json.dumps(response_data, indent=2)}")
    
    if not response_data.get("status"):
        print(f"API error: {response_data.get('message', 'Unknown error')}")
        return None
    
    run = response_data.get("data")
    if not run:
        print(f"No run data in response")
        return None
        
    print(f"Created run with ID: {run.get('id')}")
    return run

def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed: {close_status_code} {close_msg}")

def on_open(ws):
    print("WebSocket connection opened")
    
    # Send a start message
    start_message = {
        "type": "start",
        "task": json.dumps({"content": "Hello, this is a test message"}),
        "files": [],
        "team_config": {
            "cooperative_planning": True,
            "autonomous_execution": False
        },
        "settings_config": {}
    }
    ws.send(json.dumps(start_message))
    print("Sent start message")

def main():
    # Step 1: Create a session
    session = create_session()
    if not session:
        print("Failed to create session")
        return
    
    # Step 2: Create a run
    run = create_run(session["id"])
    if not run:
        print("Failed to create run")
        return
    
    # Step 3: Connect to WebSocket
    ws_url = f"{WS_BASE}/runs/{run['id']}"
    print(f"Connecting to WebSocket at {ws_url}")
    
    # Enable trace for debugging
    websocket.enableTrace(True)
    
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Run the WebSocket connection in a blocking call
    print("Waiting for messages (30 seconds)...")
    ws.run_forever(dispatcher=None, ping_interval=5, ping_timeout=2, ping_payload="PING")
    
    print("Test completed")

if __name__ == "__main__":
    main()
