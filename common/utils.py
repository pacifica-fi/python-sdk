import json
import base58
import subprocess


def sign_message(header, payload, keypair):
    message = prepare_message(header, payload)
    message_bytes = message.encode("utf-8")
    signature = keypair.sign_message(message_bytes)
    return (message, base58.b58encode(bytes(signature)).decode("ascii"))


def sign_with_hardware_wallet(header, payload, hardware_wallet_path):
    message = prepare_message(header, payload)

    # Construct the solana CLI command
    cmd = [
        "solana",
        "sign-offchain-message",
        "-k",
        hardware_wallet_path,
        message,
    ]

    try:
        # Execute the command and get the signature
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        if result.returncode != 0:
            raise Exception(f"Ledger signing failed: {result.stderr}")

        # The output contains both the approval message and the signature
        # We need to extract just the signature (the last line)
        output_lines = result.stdout.strip().split("\n")
        signature = output_lines[-1]  # already in base58 ASCII format

        return (message, signature)

    except Exception as e:
        print(f"Error signing with Ledger: {e}")
        raise


def prepare_message(header, payload):
    if (
        "type" not in header
        or "timestamp" not in header
        or "expiry_window" not in header
    ):
        raise ValueError("Header must have type, timestamp, and expiry_window")

    data = {
        **header,
        "data": payload,
    }

    message = sort_json_keys(data)

    # Specifying the separaters is important because the JSON message is expected to be compact.
    message = json.dumps(message, separators=(",", ":"))

    return message


def sort_json_keys(value):
    if isinstance(value, dict):
        sorted_dict = {}
        for key in sorted(value.keys()):
            sorted_dict[key] = sort_json_keys(value[key])
        return sorted_dict
    elif isinstance(value, list):
        return [sort_json_keys(item) for item in value]
    else:
        return value
