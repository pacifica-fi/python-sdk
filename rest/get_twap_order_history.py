import time
import uuid

import requests
from solders.keypair import Keypair

from common.constants import REQUEST_TIMEOUT, REST_URL
from common.utils import sign_message
from common.env import load_public_key


API_URL = f"{REST_URL}/orders/twap/history"
PUBLIC_KEY = load_public_key("PACIFICA_PUBLIC_KEY")

def main():
    # See the note in get_open_twap_order.py: `params=` percent-encodes the account so
    # it cannot inject additional query parameters, and the timeout is explicit because
    # `requests` does not apply one by default.
    params = {"account": PUBLIC_KEY}
    response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Request: {response.url}")

    # Print details for debugging
    print("\nDebug Info:")
    print(f"Account: {PUBLIC_KEY}")


if __name__ == "__main__":
    main()
