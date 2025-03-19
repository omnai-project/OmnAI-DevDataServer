import asyncio
import json
import math
import signal
from aiohttp import web

# Data stream definitions
DATASTREAMS = [
    {"UUID": "1002345", "color": {"r": 0, "g": 0, "b": 255}, "type": "sine"},
    {"UUID": "299345", "color": {"r": 255, "g": 0, "b": 0}, "type": "square"}
]

# Function to generate sine wave
def generate_sine_wave(time: int, frequency: float = 1.0, amplitude: float = 1.0, sample_rate: int = 60) -> float:
    return amplitude * math.sin(2 * math.pi * frequency * time / sample_rate)

# Function to generate square wave
def generate_square_wave(time: int, frequency: float = 1.0, amplitude: float = 1.0, sample_rate: int = 60) -> float:
    return amplitude if (time // (sample_rate / (2 * frequency))) % 2 == 0 else -amplitude

# HTTP API for fetching available data streams
async def get_datastreams(request: web.Request) -> web.Response:
    response = {
        "datastreams": [{"UUID": ds["UUID"], "color": ds["color"]} for ds in DATASTREAMS]
    }
    return web.json_response(response)

# WebSocket connection handling
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print("Client connected to WebSocket")
    time = 0
    try:
        async for message in ws:
            command = message.data.strip().split()
            if not command:
                continue  # Ignore empty commands

            uuids = command[:-2] if len(command) > 2 else command
            uuids = [uuid for uuid in uuids if uuid in {ds["UUID"] for ds in DATASTREAMS}]
            if not uuids:
                await ws.send_json({"error": "No valid UUIDs provided"})
                continue

            sample_rate = int(command[-2]) if len(command) > 2 and command[-2].isdigit() else 60
            output_format = command[-1] if len(command) > 2 else "json"

            selected_datastreams = [ds for ds in DATASTREAMS if ds["UUID"] in uuids]
            device_order = [ds["UUID"] for ds in selected_datastreams]

            async def send_data():
                nonlocal time
                while not ws.closed:
                    sample_data = {
                        "timestamp": time,
                        "datastreams": device_order,
                        "data": [[
                            round(generate_sine_wave(time), 3) if ds["type"] == "sine" else generate_square_wave(time)
                            for ds in selected_datastreams
                        ]]
                    }
                    
                    if output_format == "json":
                        await ws.send_json(sample_data)
                    elif output_format == "csv":
                        csv_data = f"{time}," + ",".join(map(str, sample_data["data"][0]))
                        await ws.send_str(csv_data)
                    await asyncio.sleep(1 / sample_rate)
                    time += 1
            
            task = asyncio.create_task(send_data())
            await task
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("Client disconnected")
    return ws

# Create aiohttp application
app = web.Application()
app.router.add_get("/UUID", get_datastreams)
app.router.add_get("/ws", websocket_handler)

# Start the server
async def main() -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Server running on port 8080 (HTTP & WebSocket)")
    
    stop_event = asyncio.Event()
    
    def shutdown_signal_handler() -> None:
        print("Shutting down...")
        stop_event.set()
    
    signal.signal(signal.SIGINT, lambda s, f: shutdown_signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: shutdown_signal_handler())
    
    await stop_event.wait()
    await runner.cleanup()
    print("Server stopped cleanly.")

if __name__ == "__main__":
    asyncio.run(main())