import asyncio
import json
import websockets

async def test():
    uri = "ws://127.0.0.1:8001/"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as ws:
            sub_msg = json.dumps({"cmd": "metrics_subscribe"})
            print(f"Sending: {sub_msg}")
            await ws.send(sub_msg)
            resp = await ws.recv()
            print(f"Server response: {resp}")
            for i in range(3):
                metric = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(metric)
                print(f"Metric packet {i+1} keys: {list(data.keys())}")
                if "metrics" in data:
                    print("Metrics summary:", json.dumps(data["metrics"], indent=2)[:300])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
