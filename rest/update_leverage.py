import time

import requests
from solders.keypair import Keypair

from common.constants import REQUEST_TIMEOUT, REST_URL
from common.utils import sign_message
from common.env import load_private_key
from common.validate import check_leverage


API_URL = f"{REST_URL}/account/leverage"
PRIVATE_KEY = load_private_key("PACIFICA_PRIVATE_KEY")


def main():
    # Generate account based on private key
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    public_key = str(keypair.pubkey())

    # Scaffold the signature header
    timestamp = int(time.time() * 1_000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5_000,
        "type": "update_leverage",
    }

    # Construct the signature payload
    #
    # `check_leverage` rejects a value outside Pacifica's 1-50x range before it is
    # signed. This script has no confirmation step, so an accidental `420` here would
    # otherwise be submitted as-is and rejected only by the API - after the account's
    # leverage had already been changed on any earlier successful attempt.
    signature_payload = {
        "symbol": "BTC",
        "leverage": check_leverage(42),
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

    response = requests.post(API_URL, json=request, headers=headers, timeout=REQUEST_TIMEOUT)
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
