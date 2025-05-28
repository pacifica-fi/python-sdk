import time

import base58
import requests
from solders.keypair import Keypair

from utils import sign_message


API_URL = "https://api.pacifica.fi/api/v1/orders/cancel_all"
PRIVATE_KEY = ""


def main():
    # Generate account based on private key.
    keypair = Keypair.from_bytes(base58.b58decode(PRIVATE_KEY))
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "cancel_all_orders",
    }

    # Construct the signature payload.
    signature_payload = {
        "all_symbols": True,
        "exclude_reduce_only": False,
    }

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields.
    request_header = {
        "account": public_key,
        "agent_wallet": None,
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
