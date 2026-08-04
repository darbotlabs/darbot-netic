import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8085/api/ws/runs/9"
    print(f"Testing WebSocket connection to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established successfully!")
            
            # Send a test message
            test_message = {
                "type": "test",
                "message": "Hello WebSocket!"
            }
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent test message: {test_message}")
            
            # Wait for a response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds (this might be expected)")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection was closed: {e}")
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ General error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
