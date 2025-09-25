"""
This example shows how to bind an api agent key (also called agent wallet)
to an account and use the api agent key to sign on behalf of the account
to create a market order.
"""

import time
import uuid

import requests
from solders.keypair import Keypair

from common.constants import REST_URL
from common.utils import sign_message


BIND_AGENT_WALLET_API_URL = f"{REST_URL}/agent/bind"
MARKET_ORDER_API_URL = f"{REST_URL}/orders/create_market"
PRIVATE_KEY = ""  # e.g. "2Z2Wn4kN5ZNhZzuFTQSyTiN4ixX8U6ew5wPDJbHngZaC3zF3uWNj4dQ63cnGfXpw1cESZPCqvoZE7VURyuj9kf8b"


def main():
    # Generate account based on private key
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    public_key = str(keypair.pubkey())

    # Generate a new agent wallet
    agent_wallet_private_key = Keypair()
    agent_wallet_public_key = str(agent_wallet_private_key.pubkey())

    # ---------------------------------------------------------------
    # Bind agent wallet
    # ---------------------------------------------------------------

    # Scaffold the signature header
    timestamp = int(time.time() * 1_000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5_000,
        "type": "bind_agent_wallet",
    }

    # Construct the signature payload
    signature_payload = {
        "agent_wallet": agent_wallet_public_key,
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

    response = requests.post(BIND_AGENT_WALLET_API_URL, json=request, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Request: {request}")

    # Print details for debugging
    print("\nDebug Info:")
    print(f"Address: {public_key}")
    print(f"Agent Wallet: {agent_wallet_public_key}")
    print(f"Message: {message}")
    print(f"Signature: {signature}")
    print("\n")

    # ---------------------------------------------------------------
    # Create market order
    # ---------------------------------------------------------------

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

    # Use the helper function to sign the message, with the agent wallet's private key
    message, signature = sign_message(
        signature_header, signature_payload, agent_wallet_private_key
    )

    # Construct the request reusing the payload and constructing common request fields
    request_header = {
        "account": public_key,
        "agent_wallet": agent_wallet_public_key,  # use the agent wallet's public key
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

    response = requests.post(MARKET_ORDER_API_URL, json=request, headers=headers)
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
