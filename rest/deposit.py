from borsh_construct import CStruct, U64
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
import hashlib
from common.env import load_private_key

from common.env import load_private_key
from common.validate import check_amount, to_base_units

PRIVATE_KEY = load_private_key("PACIFICA_PRIVATE_KEY")
# The amount is a *string*, validated into a `Decimal` below. It used to be the float
# literal `4200.69`, which the instruction encoder then scaled with
# `int(round(amount * 1_000_000))` - and `4200.69` is not representable in binary
# floating point, so the base-unit count depended on how that product happened to round.
# For an irreversible on-chain transfer, the number of base units must follow from the
# number the user wrote, not from the rounding of an intermediate double.
DEPOSIT_AMOUNT = "4200.69"  # minimum amount is 10

PROGRAM_ID = Pubkey.from_string("PCFA5iYgmqK6MqPhWNKg7Yv7auX7VZ4Cx7T1eJyrAMH")
CENTRAL_STATE = Pubkey.from_string("9Gdmhq4Gv1LnNMp7aiS1HSVd7pNnXNMsbuXALCQRmGjY")
PACIFICA_VAULT = Pubkey.from_string("72R843XwZxqWhsJceARQQTTbYtWy6Zw9et2YV4FpRHTa")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")

RPC_URL = "https://api.mainnet-beta.solana.com"

deposit_layout = CStruct("amount" / U64)


def get_discriminator(name: str) -> bytes:
    return hashlib.sha256(f"global:{name}".encode()).digest()[:8]


def build_deposit_instruction_data(amount: str) -> bytes:
    # `check_amount` enforces the documented 10 USDC floor and rejects anything with
    # more than six decimal places; `to_base_units` then does the scaling in exact
    # decimal arithmetic and refuses any value that would not land on a whole base unit.
    validated = check_amount(amount, name="DEPOSIT_AMOUNT", minimum="10")
    borsh_args = deposit_layout.build({"amount": to_base_units(validated)})  # 6 decimals
    return get_discriminator("deposit") + borsh_args


def get_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [
            bytes(owner),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint),
        ],
        ASSOCIATED_TOKEN_PROGRAM_ID,
    )[0]


def main():
    # Load user keypair
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    client = Client(RPC_URL)

    # Get associated token address
    user_usdc_ata = get_associated_token_address(keypair.pubkey(), USDC_MINT)
    event_authority, _ = Pubkey.find_program_address([b"__event_authority"], PROGRAM_ID)

    # Prepare accounts
    keys = [
        AccountMeta(
            pubkey=keypair.pubkey(), is_signer=True, is_writable=True
        ),  # depositor
        AccountMeta(
            pubkey=user_usdc_ata, is_signer=False, is_writable=True
        ),  # depositorUsdcAccount
        AccountMeta(pubkey=CENTRAL_STATE, is_signer=False, is_writable=True),
        AccountMeta(pubkey=PACIFICA_VAULT, is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=USDC_MINT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=event_authority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=PROGRAM_ID, is_signer=False, is_writable=False),
    ]

    # Build instruction
    data = build_deposit_instruction_data(DEPOSIT_AMOUNT)
    ix = Instruction(program_id=PROGRAM_ID, accounts=keys, data=data)

    # Build and send transaction
    tx = Transaction().add(ix)
    resp = client.send_transaction(tx, keypair)
    print("Deposit transaction signature:", resp)


if __name__ == "__main__":
    main()
