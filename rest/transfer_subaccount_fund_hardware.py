import time
import json

import requests
from solders.keypair import Keypair

from common.constants import REQUEST_TIMEOUT, REST_URL
from common.utils import sign_with_hardware_wallet
from common.env import load_public_key, load_wallet_path


API_URL = f"{REST_URL}/account/subaccount/transfer"
HARDWARE_PATH = load_wallet_path("PACIFICA_HARDWARE_PATH")
FROM_HARDWARE_PUB_KEY = load_public_key("PACIFICA_FROM_HARDWARE_PUB_KEY")
TO_PUBLIC_KEY = load_public_key("PACIFICA_TO_PUBLIC_KEY")


def main():
    # Scaffold the signature header
    timestamp = int(time.time() * 1_000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 200_000,
        "type": "transfer_funds",
    }

    # Construct the signature payload
    signature_payload = {
        "to_account": TO_PUBLIC_KEY,
        "amount": "420.69",
    }

    print("Signing with hardware wallet...")
    message, signature = sign_with_hardware_wallet(
        signature_header, signature_payload, HARDWARE_PATH
    )

    # Construct the request reusing the payload and constructing common request fields
    request_header = {
        "account": FROM_HARDWARE_PUB_KEY,
        "signature": {
            "type": "hardware",
            "value": signature,
        },
        "timestamp": signature_header["timestamp"],
        "expiry_window": signature_header["expiry_window"],
    }

    # Send the request
    headers = {"Content-Type": "application/json"}

    request = {
        **request_header,
        **signature_payload,
    }

    response = requests.post(API_URL, json=request, headers=headers, timeout=REQUEST_TIMEOUT)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Request: {request}")

    # Print details for debugging
    print("\nDebug Info:")
    print(f"From Account: {FROM_HARDWARE_PUB_KEY}")
    print(f"To Account: {TO_PUBLIC_KEY}")
    print(f"Message: {message}")
    print(f"Signature: {signature}")


if __name__ == "__main__":
    main()
