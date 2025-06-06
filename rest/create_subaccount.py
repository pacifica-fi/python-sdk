"""
## Authentication Flow

The authentication flow uses a cross-signature scheme to ensure that both the main account and the subaccount consent to the relationship. This is necessary because:

1. The main account must authorize the creation of a subaccount under its control
2. The subaccount must consent to being controlled by the main account
3. The API server must verify both signatures to prevent unauthorized subaccount creation

```
┌─────────────┐                ┌────────────┐               ┌────────────┐
│ Main Account│                │ Subaccount │               │ API Server │
└──────┬──────┘                └─────┬──────┘               └─────┬──────┘
       │                             │                            │
       │                             │                            │
       │ Step 1: Sign main_pubkey    │                            │
       │◄────────────────────────────┤                            │
       │                             │                            │
       │                             │                            │
       │ Step 2: Sign sub_signature  │                            │
       ├────────────────────────────►│                            │
       │                             │                            │
       │                             │                            │
       │ Step 3: Send both signature │                            │
       └─────────────────────────────┼───────────────────────────►│
                                     │                            │
                                     │                            │
                                     │                     Step 4: Verify
                                     │                      signatures
                                     │                            │
                                     │                            │
                                     │                     Step 5: Create
                                     │                      relationship
                                     │                            │
```

## Authentication Steps

1. **Subaccount Signs Main Account's Public Key**:

   - The subaccount signs the main account's public key using its private key
   - This creates the `sub_signature` which proves the subaccount consents to the relationship

2. **Main Account Signs the Subaccount's Signature**:

   - The main account signs the `sub_signature` using its private key
   - This creates the `main_signature` which proves the main account consents to the relationship

3. **API Server Verification**:
   - The API server verifies that `sub_signature` was created by the subaccount's private key by signing the main account's public key
   - The API server verifies that `main_signature` was created by the main account's private key by signing the `sub_signature`
   - If both verifications succeed, the subaccount relationship is established
"""

import time

import requests
from solders.keypair import Keypair

from common.constants import REST_URL
from common.utils import sign_message

API_URL = f"{REST_URL}/account/subaccount/create"
MAIN_PRIVATE_KEY = ""
SUB_PRIVATE_KEY = ""


def main():

    # Generate main and sub accounts from private keys
    main_keypair = Keypair.from_base58_string(MAIN_PRIVATE_KEY)
    sub_keypair = Keypair.from_base58_string(SUB_PRIVATE_KEY)

    # Generate a timestamp and expiry window
    # Both signatures must have the same timestamp and expiry window.
    timestamp = int(time.time() * 1_000)
    expiry_window = 5_000

    # Get public keys
    main_public_key = str(main_keypair.pubkey())
    sub_public_key = str(sub_keypair.pubkey())

    # Step 1: Subaccount signs the main account's public key
    subaccount_signature_header = {
        "timestamp": timestamp,
        "expiry_window": expiry_window,
        "type": "subaccount_initiate",
    }

    payload = {"account": main_public_key}

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

    main_account_message, main_signature = sign_message(
        main_account_signature_header, payload, main_keypair
    )

    # Step 3: Create and send the request
    request = {
        "main_account": main_public_key,
        "subaccount": sub_public_key,
        "main_signature": main_signature,
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
    print(f"Main Account: {main_public_key}")
    print(f"Main Message: {main_account_message}")
    print(f"Main Signature: {main_signature}")
    print(f"Sub Account: {sub_public_key}")
    print(f"Sub Message: {subaccount_message}")
    print(f"Sub Signature: {subaccount_signature}")


if __name__ == "__main__":
    main()
