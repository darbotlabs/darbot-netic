import requests
import websocket
import json
import time
import uuid
import sys
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "http://localhost:8085/api"
USER_ID = "test@example.com"
SESSION_NAME = f"Test Session {uuid.uuid4()}"
PROMPT = "Tell me a brief joke about programming"

def print_colored(text, color="green"):
    """Print colored text to console."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['green'])}{text}{colors['end']}")

def check_health() -> bool:
    """Check API health."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        return data.get("status", False)
    except Exception as e:
        print_colored(f"Health check failed: {e}", "red")
        return False

def create_session() -> Optional[str]:
    """Create a new session and return its ID."""
    try:
        payload = {
            "name": SESSION_NAME,
            "user_id": USER_ID
        }
        
        response = requests.post(f"{BASE_URL}/sessions/", json=payload)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") and "data" in response_data:
                session = response_data.get("data", {})
                return str(session.get("id"))
            else:
                print_colored(f"Unexpected response format: {response_data}", "red")
                return None
        else:
            print_colored(f"Failed to create session: {response.text}", "red")
            return None
    except Exception as e:
        print_colored(f"Error creating session: {e}", "red")
        return None

def create_run(session_id: str) -> Optional[str]:
    """Create a new run within the session and return its ID."""
    try:
        payload = {
            "session_id": session_id,
            "prompt": PROMPT,
            "user_id": USER_ID,
            "attachments": []
        }
        
        response = requests.post(f"{BASE_URL}/runs/", json=payload)
        print_colored(f"Run creation response status: {response.status_code}", "yellow")
        
        if response.status_code == 200:
            response_data = response.json()
            print_colored(f"Full response data: {response_data}", "yellow")
            if response_data.get("status") and "data" in response_data:
                run_data = response_data.get("data", {})
                run_id = run_data.get("run_id")  # Changed from "id" to "run_id"
                print_colored(f"Extracted run ID: {run_id}", "yellow")
                return str(run_id) if run_id is not None else None
            else:
                print_colored("Unexpected response format", "red")
                print_colored(f"{response_data}", "red")
                return None
        else:
            print_colored(f"Failed to create run: {response.text}", "red")
            return None
    except Exception as e:
        print_colored(f"Error creating run: {e}", "red")
        return None

def on_message(ws, message):
    """Handle incoming WebSocket messages."""
    try:
        data = json.loads(message)
        if "type" in data:
            if data["type"] == "message":
                print_colored(f"Received message: {data.get('content', '').strip()}", "blue")
            elif data["type"] == "tool_start":
                print_colored(f"Tool started: {data.get('name', '')}", "yellow")
            elif data["type"] == "tool_end":
                print_colored(f"Tool ended: {data.get('name', '')}", "green")
            elif data["type"] == "run_update":
                print_colored(f"Run status updated: {data.get('status', '')}", "purple")
            else:
                print_colored(f"Other event: {data['type']}", "cyan")
    except json.JSONDecodeError:
        print_colored(f"Received non-JSON message: {message}", "red")

def on_error(ws, error):
    print_colored(f"WebSocket error: {error}", "red")

def on_close(ws, close_status_code, close_msg):
    print_colored("WebSocket connection closed", "yellow")

def on_open(ws):
    print_colored("WebSocket connection opened", "green")

def connect_to_websocket(run_id: str):
    """Connect to WebSocket for real-time updates."""
    ws_url = f"ws://localhost:8085/api/ws/runs/{run_id}"
    
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    
    # Start WebSocket connection in a separate thread
    import threading
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    return ws, wst

def run_test():
    """Run a complete end-to-end test."""
    print_colored("Starting Magentic-UI full functionality test", "cyan")
    
    # Step 1: Check health
    print_colored("\n[Step 1] Checking API health...", "cyan")
    if not check_health():
        print_colored("API health check failed. Aborting test.", "red")
        return False
    print_colored("API health check passed!", "green")
    
    # Step 2: Create a session
    print_colored("\n[Step 2] Creating a new session...", "cyan")
    session_id = create_session()
    if not session_id:
        print_colored("Failed to create session. Aborting test.", "red")
        return False
    print_colored(f"Session created successfully with ID: {session_id}", "green")
      # Step 3: Create a run
    print_colored("\n[Step 3] Creating a new run...", "cyan")
    run_id = create_run(session_id)
    if not run_id or run_id == "None":
        print_colored("Failed to create run. Aborting test.", "red")
        return False
    print_colored(f"Run created successfully with ID: {run_id}", "green")
    
    # Step 4: Connect to WebSocket
    print_colored("\n[Step 4] Connecting to WebSocket...", "cyan")
    ws, wst = connect_to_websocket(run_id)
    print_colored("WebSocket connection initialized", "green")
    
    # Step 5: Wait for messages
    print_colored("\n[Step 5] Waiting for messages (30 seconds)...", "cyan")
    try:
        time.sleep(30)  # Wait for 30 seconds to receive messages
    except KeyboardInterrupt:
        print_colored("\nTest interrupted by user.", "yellow")
    
    # Step 6: Check run status
    print_colored("\n[Step 6] Checking final run status...", "cyan")
    try:
        response = requests.get(f"{BASE_URL}/runs/{run_id}")
        if response.status_code == 200:
            run_data = response.json()
            print_colored(f"Final run status: {run_data.get('status', 'unknown')}", "green")
            
            # Check for errors
            if run_data.get("error"):
                print_colored(f"Run encountered an error: {run_data.get('error')}", "red")
        else:
            print_colored(f"Failed to get run status: {response.text}", "red")
    except Exception as e:
        print_colored(f"Error checking run status: {e}", "red")
    
    # Clean up WebSocket
    ws.close()
    
    print_colored("\nTest completed!", "cyan")
    return True

if __name__ == "__main__":
    # Run the test
    success = run_test()
    sys.exit(0 if success else 1)
