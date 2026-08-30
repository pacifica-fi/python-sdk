"""Bounds and format checks for the values these examples sign.

Every script here signs a payload and submits it without any confirmation step, so a
mistyped literal becomes a real order, a real leverage change, or a real transfer. The
checks below are cheap local guards against the mistakes that are expensive and
irreversible rather than merely wrong: an extra zero on an amount, a leverage value
copied from a different venue's scale, an address with a typo that still base58-decodes.

Amounts are handled as ``Decimal`` from a *string*, never as ``float``. A USDC amount
has six decimals, and binary floating point cannot represent most decimal fractions
exactly: ``0.1 + 0.2`` is ``0.30000000000000004``, and ``int(round(4200.69 * 1_000_000))``
depends on how the literal happened to round. The API accepts amounts as strings for
this reason, and signatures are computed over the exact string, so keeping the value in
decimal form all the way through is both safer and required for the signature to match
what the user intended.
"""

from decimal import Decimal, InvalidOperation

import base58

# USDC on Solana has six decimal places. A value with more precision than the token
# supports would be silently truncated somewhere downstream.
USDC_DECIMALS = 6
USDC_SCALE = Decimal(10) ** USDC_DECIMALS

# Pacifica's documented leverage range. Checked so a value from another venue's scale
# (or a stray extra digit) is rejected locally instead of being signed and sent.
MIN_LEVERAGE = 1
MAX_LEVERAGE = 50

PUBLIC_KEY_BYTES = 32


def check_amount(value, *, name="amount", minimum="0", maximum=None):
    """Validate a decimal amount given as a string and return it as ``Decimal``.

    ``value`` must be a string (or ``Decimal``); passing a ``float`` is rejected rather
    than coerced, because by the time a float reaches this function the precision loss
    has already happened and there is nothing useful left to check.
    """
    if isinstance(value, float):
        raise TypeError(
            f"{name} was passed as a float ({value!r}); pass it as a string such as "
            f'"{value:.6f}" so the decimal value is exact.'
        )
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name}={value!r} is not a valid decimal number.") from exc

    if not amount.is_finite():
        raise ValueError(f"{name}={value!r} is not a finite number.")
    if amount <= Decimal(minimum):
        raise ValueError(f"{name} must be greater than {minimum}; got {amount}.")
    if maximum is not None and amount > Decimal(maximum):
        raise ValueError(
            f"{name}={amount} exceeds the configured ceiling of {maximum}. Raise the "
            "ceiling deliberately if this is intended."
        )
    if -amount.as_tuple().exponent > USDC_DECIMALS:
        raise ValueError(
            f"{name}={amount} has more than {USDC_DECIMALS} decimal places, which is "
            "more precision than the token supports."
        )
    return amount


def to_base_units(amount):
    """Convert a validated ``Decimal`` amount to integer base units (6 decimals).

    The multiplication is exact because both operands are ``Decimal``. ``check_amount``
    has already rejected anything with more than six decimal places, so the result has
    no fractional part to round away - and this asserts that rather than assuming it.
    """
    scaled = Decimal(amount) * USDC_SCALE
    if scaled != scaled.to_integral_value():
        raise ValueError(f"amount {amount} does not convert to whole base units.")
    return int(scaled)


def check_leverage(value):
    """Validate a leverage setting and return it as ``int``."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"leverage must be an integer; got {value!r}.")
    if not MIN_LEVERAGE <= value <= MAX_LEVERAGE:
        raise ValueError(
            f"leverage={value} is outside the supported range "
            f"{MIN_LEVERAGE}-{MAX_LEVERAGE}x."
        )
    return value


def check_address(value, *, name="address"):
    """Validate that a value is a base58 32-byte Solana address and return it.

    A transfer destination cannot be recovered if it is wrong, and a typo in base58
    often still decodes - just to different bytes - so the length check is the part that
    catches real mistakes.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty base58 string.")
    value = value.strip()
    try:
        decoded = base58.b58decode(value)
    except Exception as exc:
        raise ValueError(f"{name} is not valid base58.") from exc
    if len(decoded) != PUBLIC_KEY_BYTES:
        raise ValueError(
            f"{name} decodes to {len(decoded)} bytes; a Solana address is "
            f"{PUBLIC_KEY_BYTES} bytes."
        )
    return value
