import time
import json

import requests
from solders.keypair import Keypair

from common.constants import REST_URL
from common.utils import sign_message, sign_with_hardware_wallet

API_URL = f"{REST_URL}/account/subaccount/create"
MAIN_HARDWARE_PUB_KEY = ""
MAIN_HARDWARE_PATH = ""  # e.g. "usb://ledger?key=1"
SUB_PRIVATE_KEY = ""


def main():

    # Generate subaccount from private key
    sub_keypair = Keypair.from_base58_string(SUB_PRIVATE_KEY)

    # Generate a timestamp and expiry window
    # Both signatures must have the same timestamp and expiry window.
    timestamp = int(time.time() * 1_000)
    expiry_window = 200_000

    # Get public keys
    sub_public_key = str(sub_keypair.pubkey())

    # Step 1: Subaccount signs the main account's public key
    subaccount_signature_header = {
        "timestamp": timestamp,
        "expiry_window": expiry_window,
        "type": "subaccount_initiate",
    }

    payload = {"account": MAIN_HARDWARE_PUB_KEY}

    subaccount_message, subaccount_signature = sign_message(
        subaccount_signature_header, payload, sub_keypair
    )

    # Step 2: Main account signs the sub_signature
    main_account_signature_header = {
        "timestamp": timestamp,
        "expiry_window": expiry_window,
        "type": "subaccount_confirm",
    }

    payload = {"signature": subaccount_signature}

    print("Signing with hardware wallet...")
    main_account_message, main_signature = sign_with_hardware_wallet(
        main_account_signature_header, payload, MAIN_HARDWARE_PATH
    )

    # Step 3: Create and send the request
    request = {
        "main_account": MAIN_HARDWARE_PUB_KEY,
        "subaccount": sub_public_key,
        "main_signature": {
            "type": "hardware",
            "value": main_signature,
        },
        "sub_signature": subaccount_signature,
        "timestamp": timestamp,
        "expiry_window": expiry_window,
    }

    # Send the request
    headers = {"Content-Type": "application/json"}

    response = requests.post(API_URL, json=request, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Request: {request}")

    # Print details for debugging
    print("\nDebug Info:")
    print(f"Main Account: {MAIN_HARDWARE_PUB_KEY}")
    print(f"Main Message: {main_account_message}")
    print(f"Main Signature: {main_signature}")
    print(f"Sub Account: {sub_public_key}")
    print(f"Sub Message: {subaccount_message}")
    print(f"Sub Signature: {subaccount_signature}")


if __name__ == "__main__":
    main()
