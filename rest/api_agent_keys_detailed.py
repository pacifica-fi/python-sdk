import time
import uuid
import requests
from solders.keypair import Keypair

from common.constants import REST_URL
from common.utils import sign_message

# Agent Wallet Management Endpoints
BIND_ENDPOINT = f"{REST_URL}/agent/bind"
LIST_ENDPOINT = f"{REST_URL}/agent/list"
REVOKE_ENDPOINT = f"{REST_URL}/agent/revoke"
REVOKE_ALL_ENDPOINT = f"{REST_URL}/agent/revoke_all"

# IP Whitelist Management Endpoints
IP_LIST_ENDPOINT = f"{REST_URL}/agent/ip_whitelist/list"
IP_ADD_ENDPOINT = f"{REST_URL}/agent/ip_whitelist/add"
IP_REMOVE_ENDPOINT = f"{REST_URL}/agent/ip_whitelist/remove"
IP_TOGGLE_ENDPOINT = f"{REST_URL}/agent/ip_whitelist/toggle"

def bind_agent_wallet(keypair: Keypair, agent_wallet_address: str):
    """Bind an agent wallet to your account."""
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "bind_agent_wallet",
    }

    # Construct the signature payload.
    signature_payload = {
        "agent_wallet": agent_wallet_address,
    }

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    print(f"Message: {message}")
    print(f"Signature: {signature}")

    # Construct the request reusing the payload and constructing common request fields.
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
    response = requests.post(BIND_ENDPOINT, json=request, headers=headers)

    return response

def list_agent_wallets(keypair: Keypair):
    """List all bound agent wallets."""
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "list_agent_wallets",
    }

    # Construct the signature payload.
    signature_payload = {}

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields.
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

def revoke_agent_wallet(keypair: Keypair, agent_wallet_address: str):
    """Revoke a specific agent wallet."""
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "revoke_agent_wallet",
    }

    # Construct the signature payload.
    signature_payload = {
        "agent_wallet": agent_wallet_address,
    }

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields.
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

def revoke_all_agent_wallets(keypair: Keypair):
    """Revoke all agent wallets."""
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "revoke_all_agent_wallets",
    }

    # Construct the signature payload.
    signature_payload = {}

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields.
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
    response = requests.post(REVOKE_ALL_ENDPOINT, json=request, headers=headers)

    return response

def list_ip_whitelist(keypair: Keypair, agent_wallet_address: str):
    """List IP addresses in the whitelist for an agent wallet."""
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "list_agent_ip_whitelist",
    }

    # Construct the signature payload.
    signature_payload = {
        "agent_wallet": agent_wallet_address,
    }

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields.
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
    response = requests.post(IP_LIST_ENDPOINT, json=request, headers=headers)

    return response

def add_ip_to_whitelist(keypair: Keypair, agent_wallet_address: str, ip_address: str):
    """Add an IP address to the whitelist."""
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "add_agent_whitelisted_ip",
    }

    # Construct the signature payload.
    signature_payload = {
        "agent_wallet": agent_wallet_address,
        "ip_address": ip_address,
    }

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields.
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
    response = requests.post(IP_ADD_ENDPOINT, json=request, headers=headers)

    return response

def remove_ip_from_whitelist(keypair: Keypair, agent_wallet_address: str, ip_address: str):
    """Remove an IP address from the whitelist."""
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "remove_agent_whitelisted_ip",
    }

    # Construct the signature payload.
    signature_payload = {
        "agent_wallet": agent_wallet_address,
        "ip_address": ip_address,
    }

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields.
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
    response = requests.post(IP_REMOVE_ENDPOINT, json=request, headers=headers)

    return response

def toggle_ip_whitelist(keypair: Keypair, agent_wallet_address: str, enabled: bool):
    """Enable or disable IP whitelist enforcement."""
    public_key = str(keypair.pubkey())

    # Scaffold the signature header.
    timestamp = int(time.time() * 1000)

    signature_header = {
        "timestamp": timestamp,
        "expiry_window": 5000,
        "type": "set_agent_ip_whitelist_enabled",
    }

    # Construct the signature payload.
    signature_payload = {
        "agent_wallet": agent_wallet_address,
        "enabled": enabled,
    }

    # Use the helper function to sign the message.
    message, signature = sign_message(signature_header, signature_payload, keypair)

    # Construct the request reusing the payload and constructing common request fields.
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
    response = requests.post(IP_TOGGLE_ENDPOINT, json=request, headers=headers)

    return response