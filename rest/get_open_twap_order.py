import time
import uuid

import requests
from solders.keypair import Keypair

from common.constants import REQUEST_TIMEOUT, REST_URL
from common.utils import sign_message
from common.env import load_public_key


API_URL = f"{REST_URL}/orders/twap"
PUBLIC_KEY = load_public_key("PACIFICA_PUBLIC_KEY")


def main():
    # `params=` rather than string concatenation: `requests` then percent-encodes the
    # value, so an address containing a `&`, `#` or space cannot graft extra query
    # parameters onto the request. It also keeps the URL and its query separable in
    # logs. The timeout is explicit because `requests` has no default one.
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
