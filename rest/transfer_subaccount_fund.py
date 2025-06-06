import time

import requests
from solders.keypair import Keypair

from common.constants import REST_URL
from common.utils import sign_message


API_URL = f"{REST_URL}/account/subaccount/transfer"
FROM_PRIVATE_KEY = ""  # must be a main account or a subaccount
TO_PUBLIC_KEY = ""  # must be the above's child subaccount or parent main account


def main():
    # Generate account based on private key
    from_keypair = Keypair.from_base58_string(FROM_PRIVATE_KEY)
    from_public_key = str(from_keypair.pubkey())

    # Scaffold the signature header
    timestamp = int(time.time() * 1_000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5_000,
        "type": "transfer_funds",
    }

    # Construct the signature payload
    signature_payload = {
        "to_account": TO_PUBLIC_KEY,
        "amount": "420.69",
    }

    # Use the helper function to sign the message
    message, signature = sign_message(signature_header, signature_payload, from_keypair)

    # Construct the request reusing the payload and constructing common request fields
    request_header = {
        "account": from_public_key,
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
    print(f"From Account: {from_public_key}")
    print(f"To Account: {TO_PUBLIC_KEY}")
    print(f"Message: {message}")
    print(f"Signature: {signature}")


if __name__ == "__main__":
    main()
