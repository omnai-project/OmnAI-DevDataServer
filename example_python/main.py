import asyncio
import json
import math
import signal
from aiohttp import web 
from aiohttp_middlewares import cors_middleware
import time

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
                while not ws.closed:
                    real_timestamp = round(time.time(), 3)  # UNIX-Zeit mit Millisekunden
                    # Alternative: ISO 8601 Zeitformat
                    # real_timestamp = datetime.datetime.now().isoformat()

                    sample_data = {
                        "timestamp": real_timestamp,
                        "datastreams": device_order,
                        "data": [[
                            round(generate_sine_wave(real_timestamp), 3) if ds["type"] == "sine" else generate_square_wave(real_timestamp)
                            for ds in selected_datastreams
                        ]]
                    }
                    
                    if output_format == "json":
                        await ws.send_json(sample_data)
                    elif output_format == "csv":
                        csv_data = f"{real_timestamp}," + ",".join(map(str, sample_data["data"][0]))
                        await ws.send_str(csv_data)

                    await asyncio.sleep(1 / sample_rate)
            
            task = asyncio.create_task(send_data())
            #await task
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("Client disconnected")
    return ws

# Create aiohttp application
app = web.Application(middlewares=[cors_middleware(origins=["http://localhost:4200"])])
app.router.add_get("/v1/get_devices", get_datastreams)
app.router.add_get("/v1/subscribe_ws", websocket_handler)

# Start the server
async def main() -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    port = 8080
    site = web.TCPSite(runner, "0.0.0.0", port )
    await site.start()
    print("Server running on port 8080 (HTTP & WebSocket)")
    
    
    await stop_event.wait()
    await runner.cleanup()
    print("Server stopped cleanly.")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

stop_event = asyncio.Event()

def _on_shutdown():
    stop_event.set()

loop.add_signal_handler(signal.SIGINT, _on_shutdown)
loop.add_signal_handler(signal.SIGTERM, _on_shutdown)

try:
    loop.run_until_complete(main())
finally:
    loop.close()