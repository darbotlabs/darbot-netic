#!/usr/bin/env python3
"""
Simple WebSocket client test to verify connectivity to Magentic-UI
"""
import asyncio
import json
import websockets


async def test_websocket_connection():
    """Test WebSocket connection to the Magentic-UI server"""
    
    # Test with a valid run_id that should exist in the database
    ws_url = "ws://localhost:8085/api/ws/runs/9"
    
    print(f"Testing WebSocket connection to: {ws_url}")
    
    try:
        # Attempt to connect
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connection established successfully!")
            
            # Send a ping message
            ping_message = {
                "type": "ping",
                "timestamp": "2025-06-01T18:55:00Z"
            }
            
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(
                    websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
                
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
                
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"🔌 Connection closed: {e}")
        if e.code == 4004:
            print("   This is expected - run ID 123 probably doesn't exist")
            print("   ✅ WebSocket endpoint is reachable and responding "
                  "correctly")
        else:
            print(f"   ❌ Unexpected close code: {e.code}")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - server might not be running on "
              "port 8001")
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    print("=== WebSocket Client Test ===")
    asyncio.run(test_websocket_connection())
