import time

import requests
from solders.keypair import Keypair

from common.constants import REQUEST_TIMEOUT, REST_URL
from common.utils import sign_message
from common.env import load_private_key, load_public_key
from common.validate import check_address, check_amount


API_URL = f"{REST_URL}/account/subaccount/transfer"
FROM_PRIVATE_KEY = load_private_key("PACIFICA_FROM_PRIVATE_KEY")
TO_PUBLIC_KEY = load_public_key("PACIFICA_TO_PUBLIC_KEY")


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
    #
    # The amount is kept as a string and validated as a `Decimal`: the signature is
    # computed over these exact characters, and a transfer is not reversible, so the
    # value that is signed must be the value that was written. `check_address` catches a
    # destination typo that still base58-decodes but to the wrong length.
    signature_payload = {
        "to_account": check_address(TO_PUBLIC_KEY, name="to_account"),
        "amount": str(check_amount("420.69", name="amount")),
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

    response = requests.post(API_URL, json=request, headers=headers, timeout=REQUEST_TIMEOUT)
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
