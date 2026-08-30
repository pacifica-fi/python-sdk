import time
import uuid

import requests
from solders.keypair import Keypair

from common.constants import REQUEST_TIMEOUT, REST_URL
from common.utils import sign_message
from common.env import require_env


API_URL = f"{REST_URL}/orders/twap/history_by_id"
# Not a secret, but read from the environment for the same reason as the keys: nothing
# about running an example should require editing a tracked file.
ORDER_ID = require_env("PACIFICA_TWAP_ORDER_ID", hint='e.g. `export PACIFICA_TWAP_ORDER_ID="6"`.')


def main():
    # See the note in get_open_twap_order.py. `order_id` is passed through `params=`
    # rather than concatenated, so a value that is not a bare number cannot append
    # further query parameters of its own.
    params = {"order_id": ORDER_ID}
    response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Request: {response.url}")

    # Print details for debugging
    print("\nDebug Info:")
    print(f"Order id: {ORDER_ID}")

if __name__ == "__main__":
    main()
