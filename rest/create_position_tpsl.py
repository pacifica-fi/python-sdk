import time
import uuid

import requests
from solders.keypair import Keypair

from common.constants import REST_URL
from common.utils import sign_message


# Assume a BTC long position has already been opened
API_URL = f"{REST_URL}/positions/tpsl"
PRIVATE_KEY = ""  # e.g. "2Z2Wn4kN5ZNhZzuFTQSyTiN4ixX8U6ew5wPDJbHngZaC3zF3uWNj4dQ63cnGfXpw1cESZPCqvoZE7VURyuj9kf8b"


def main():
    # Generate account based on private key
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    public_key = str(keypair.pubkey())

    # Scaffold the signature header
    timestamp = int(time.time() * 1_000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5_000,
        "type": "set_position_tpsl",
    }

    # Construct the signature payload
    signature_payload = {
        "symbol": "BTC",
        "side": "ask",
        "take_profit": {
            "stop_price": "120000",
            "limit_price": "120300",
            "amount": "0.1",
            "client_order_id": str(uuid.uuid4()),
        },
        "stop_loss": {
            "stop_price": "99800",
            # omitting limit_price to place a market order at trigger
            # omitting amount to use the full position size
            # client_order_id is optional
        },
    }

    # Use the helper function to sign the message
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields
    request_header = {
        "account": public_key,
        "signature": signature,
        "timestamp": signature_header["timestamp"],
        "expiry_window": signature_header["expiry_window"],
    }

    # Send the request
    headers = {"Content-Type": "application/json"}

    request = {
        **request_header,
        **signature_payload,
    }

    response = requests.post(API_URL, json=request, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Request: {request}")

    # Print details for debugging
    print("\nDebug Info:")
    print(f"Address: {public_key}")
    print(f"Message: {message}")
    print(f"Signature: {signature}")


if __name__ == "__main__":
    main()
