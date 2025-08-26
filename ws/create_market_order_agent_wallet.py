import asyncio
import json
import time
import uuid

import websockets
from solders.keypair import Keypair

from common.constants import WS_URL
from common.utils import sign_message

PRIVATE_KEY = ""
API_PRIVATE_KEY = ""  # must be the above public key's registered agent wallet


async def exec_main():
    # Generate account based on private key
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    public_key = str(keypair.pubkey())
    api_keypair = Keypair.from_base58_string(API_PRIVATE_KEY)
    agent_key = str(api_keypair.pubkey())

    # Scaffold the signature header
    timestamp = int(time.time() * 1_000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5_000,
        "type": "create_market_order",
    }

    # Construct the signature payload
    signature_payload = {
        "symbol": "BTC",
        "reduce_only": False,
        "amount": "0.1",
        "side": "bid",
        "slippage_percent": "0.5",
        "client_order_id": str(uuid.uuid4()),
    }

    # Use the helper function to sign the message
    message, signature = sign_message(signature_header, signature_payload, api_keypair)

    # Construct the request reusing the payload and constructing common request fields
    request_header = {
        "account": public_key,
        "agent_wallet": agent_key,
        "signature": signature,
        "timestamp": signature_header["timestamp"],
        "expiry_window": signature_header["expiry_window"],
    }

    # Combine headers and payload for the final message
    message_to_send = {
        **request_header,
        **signature_payload,
    }

    # Connect to WebSocket
    async with websockets.connect(WS_URL, ping_interval=30) as websocket:
        # Prepare the WebSocket message according to the backend format
        ws_message = {
            "id": str(uuid.uuid4()),
            "params": {"create_market_order": message_to_send},
        }

        # Send the message
        await websocket.send(json.dumps(ws_message))

        # Wait for response
        response = await websocket.recv()
        print(f"Response: {response}")

        # Print details for debugging
        print("\nDebug Info:")
        print(f"Address: {public_key}")
        print(f"Message: {message}")
        print(f"Signature: {signature}")
        print(f"WebSocket Message: {ws_message}")


async def main():
    await exec_main()


if __name__ == "__main__":
    asyncio.run(main())
