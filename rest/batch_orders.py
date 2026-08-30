import time
import uuid

import requests
from solders.keypair import Keypair

from common.constants import REQUEST_TIMEOUT, REST_URL
from common.utils import sign_message
from common.env import load_private_key


API_URL = f"{REST_URL}/orders/batch"
PRIVATE_KEY = load_private_key("PACIFICA_PRIVATE_KEY")


def main():
    # Generate account based on private key
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    public_key = str(keypair.pubkey())

    timestamp = int(time.time() * 1_000)
    request_list = []

    # BATCH ORDER 1: CREATE ORDER

    # Scaffold the signature header
    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5_000,
        "type": "create_order",
    }

    # Construct the signature payload
    signature_payload = {
        "symbol": "BTC",
        "price": str(100_000),
        "reduce_only": False,
        "amount": "0.1",
        "side": "bid",
        "tif": "GTC",
        "client_order_id": str(uuid.uuid4()),
    }

    # Use the helper function to sign the message
    _, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields
    request_header = {
        "account": public_key,
        "signature": signature,
        "timestamp": signature_header["timestamp"],
        "expiry_window": signature_header["expiry_window"],
    }
    request = {
        **request_header,
        **signature_payload,
    }
    request_list.append(
        {
            "type": "Create",
            "data": request,
        }
    )

    # BATCH ORDER 2: CANCEL ORDER

    # Scaffold the signature header
    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5_000,
        "type": "cancel_order",
    }

    # Construct the signature payload
    signature_payload = {
        "symbol": "BTC",
        "order_id": 42069,  # or "client_order_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }

    # Use the helper function to sign the message
    _, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields
    request_header = {
        "account": public_key,
        "signature": signature,
        "timestamp": signature_header["timestamp"],
        "expiry_window": signature_header["expiry_window"],
    }
    request = {
        **request_header,
        **signature_payload,
    }
    request_list.append(
        {
            "type": "Cancel",
            "data": request,
        }
    )

    # Send the request
    headers = {"Content-Type": "application/json"}
    request_payload = {"actions": request_list}
    response = requests.post(API_URL, json=request_payload, headers=headers, timeout=REQUEST_TIMEOUT)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    # `requests` here is the HTTP library module, not the payload - the original line
    # printed `<module 'requests' from '...'>` and its filesystem path instead of the
    # batch that was sent, which is the one thing this debug line existed to show.
    print(f"Requests: {request_payload}")


if __name__ == "__main__":
    main()
