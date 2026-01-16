import time

import requests
from solders.keypair import Keypair

from common.constants import REST_URL
from common.utils import sign_message

API_URL = f"{REST_URL}/account/subaccount/list"
PRIVATE_KEY = ""


def main():
    # Generate account based on private key
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    public_key = str(keypair.pubkey())

    # Generate a timestamp and expiry window
    timestamp = int(time.time() * 1000)

    # Create the signed message for listing subaccounts
    signature_header = {
        "expiry_window": 5_000,
        "timestamp": timestamp,
        "type": "list_subaccounts",
    }

    signature_payload = {}  # No additional data needed for listing

    # Use the helper function to sign the message
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields
    request_header = {
        "account": public_key,
        "signature": signature,
        "timestamp": signature_header["timestamp"],
        "expiry_window": signature_header["expiry_window"],
    }

    headers = {"Content-Type": "application/json"}
    request = {
        **request_header,
        **signature_payload,
    }

    response = requests.post(API_URL, json=request, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and "data" in data:
            subaccounts = data["data"]["subaccounts"]
            print(f"\nFound {len(subaccounts)} subaccounts:")
            for i, subaccount in enumerate(subaccounts, 1):
                print(f"  {i}. Address: {subaccount['address']}")
                print(f"     Balance: {subaccount['balance']}")
                print(f"     Fee Level: {subaccount['fee_level']}")
                print(f"     Fee Mode: {subaccount['fee_mode']}")
                print(f"     Created: {subaccount['created_at']}")
                print()
        else:
            print("No subaccounts found or error in response")
    else:
        print("Error occurred while fetching subaccounts")

    # Print details for debugging
    print("\nDebug Info:")
    print(f"Address: {public_key}")
    print(f"Message: {message}")
    print(f"Signature: {signature}")


if __name__ == "__main__":
    main()
