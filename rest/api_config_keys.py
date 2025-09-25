"""
This example shows how to create, revoke, and list api config keys for an account.
Please refer to https://docs.pacifica.fi/api-documentation/api/rate-limits/api-config-keys#using-a-pacifica-api-config-key
for the use of API Config Keys.
"""

import time
import json

import requests
from solders.keypair import Keypair

from common.constants import REST_URL
from common.utils import sign_message


CREATE_ENDPOINT = f"{REST_URL}/account/api_keys/create"
REVOKE_ENDPOINT = f"{REST_URL}/account/api_keys/revoke"
LIST_ENDPOINT = f"{REST_URL}/account/api_keys"

PRIVATE_KEY = ""  # e.g. "2Z2Wn4kN5ZNhZzuFTQSyTiN4ixX8U6ew5wPDJbHngZaC3zF3uWNj4dQ63cnGfXpw1cESZPCqvoZE7VURyuj9kf8b"


def create_api_config_key(keypair: Keypair):
    public_key = str(keypair.pubkey())

    # Scaffold the signature header
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "create_api_key",
    }

    # Construct the signature payload
    signature_payload = {}

    # Use the helper function to sign the message
    message, signature = sign_message(signature_header, signature_payload, keypair)

    print(f"Message: {message}")
    print(f"Signature: {signature}")

    # Construct the request reusing the payload and constructing common request fields
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
    response = requests.post(CREATE_ENDPOINT, json=request, headers=headers)

    return response


def revoke_api_config_key(keypair: Keypair, api_key: str):
    public_key = str(keypair.pubkey())

    # Scaffold the signature header
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "revoke_api_key",
    }

    # Construct the signature payload
    signature_payload = {
        "api_key": api_key,
    }

    # Use the helper function to sign the message
    message, signature = sign_message(signature_header, signature_payload, keypair)

    print(f"Message: {message}")
    print(f"Signature: {signature}")

    # Construct the request reusing the payload and constructing common request fields
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
    response = requests.post(REVOKE_ENDPOINT, json=request, headers=headers)

    return response


def list_api_config_keys(keypair: Keypair):
    public_key = str(keypair.pubkey())

    # Scaffold the signature header
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "list_api_keys",
    }

    # Construct the signature payload
    signature_payload = {}

    # Use the helper function to sign the message
    message, signature = sign_message(signature_header, signature_payload, keypair)

    print(f"Message: {message}")
    print(f"Signature: {signature}")

    # Construct the request reusing the payload and constructing common request fields
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
    response = requests.post(LIST_ENDPOINT, json=request, headers=headers)

    return response


def main():
    # Generate account based on private key
    keypair = Keypair.from_base58_string(PRIVATE_KEY)

    print("Creating API Config Key")
    response = create_api_config_key(keypair)
    print(json.dumps(response.json(), indent=4))

    api_key = response.json()["data"]["api_key"]

    print("Listing API Config Keys")
    response = list_api_config_keys(keypair)
    print(json.dumps(response.json(), indent=4))

    print(f"Revoking API Config Key {api_key}")
    response = revoke_api_config_key(keypair, api_key)
    print(json.dumps(response.json(), indent=4))

    print("Listing API Keys")
    response = list_api_config_keys(keypair)
    print(json.dumps(response.json(), indent=4))


if __name__ == "__main__":
    main()
