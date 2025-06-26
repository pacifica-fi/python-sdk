import asyncio
import json

import websockets

from common.constants import WS_URL


async def exec_main():
    # Connect to WebSocket
    async with websockets.connect(WS_URL, ping_interval=30) as websocket:
        # Prepare the WebSocket message according to the backend format
        ws_message = {"method": "subscribe", "params": {"source": "prices"}}

        # Send the message
        await websocket.send(json.dumps(ws_message))

        # Wait for response
        async for message in websocket:
            data = json.loads(message)
            print(data)


async def main():
    await exec_main()


if __name__ == "__main__":
    asyncio.run(main())
