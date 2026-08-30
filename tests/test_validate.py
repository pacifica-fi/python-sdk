"""Tests for common/validate.py.

Run from the repository root with:

    python -m unittest discover -s tests -v

`base58` is not installed in every environment these examples are read in, and the
audit that produced these tests was not authorised to install packages, so a minimal
base58 decoder is injected into `sys.modules` before importing the module under test.
It is deliberately only a *decoder* - that is the whole surface `check_address` uses -
and it is implemented straightforwardly from the alphabet so the length assertions
below are testing real base58 semantics rather than a stub that agrees with them.
"""

import sys
import types
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _b58decode(value):
    if isinstance(value, bytes):
        value = value.decode("ascii")
    number = 0
    for char in value:
        index = _ALPHABET.find(char)
        if index < 0:
            raise ValueError(f"invalid base58 character: {char!r}")
        number = number * 58 + index
    body = number.to_bytes((number.bit_length() + 7) // 8, "big") if number else b""
    # Each leading '1' encodes one leading zero byte.
    leading_zeros = len(value) - len(value.lstrip("1"))
    return b"\x00" * leading_zeros + body


if "base58" not in sys.modules:
    stub = types.ModuleType("base58")
    stub.b58decode = _b58decode
    sys.modules["base58"] = stub

from common.validate import (  # noqa: E402  (import must follow the stub above)
    MAX_LEVERAGE,
    check_address,
    check_amount,
    check_leverage,
    to_base_units,
)

# A real 32-byte Solana address (the SPL token program), used because it is public,
# well-known, and not anyone's account.
VALID_ADDRESS = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"


class TestCheckAmount(unittest.TestCase):
    def test_accepts_a_decimal_string(self):
        self.assertEqual(check_amount("420.69"), Decimal("420.69"))

    def test_rejects_a_float(self):
        # The regression this guards: `4200.69` as a float has already lost precision
        # by the time it arrives, so it is refused rather than quietly accepted.
        with self.assertRaises(TypeError):
            check_amount(4200.69)

    def test_rejects_zero_and_negative(self):
        for value in ["0", "-1", "-0.000001"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check_amount(value)

    def test_rejects_non_numeric(self):
        for value in ["", "abc", "1.2.3", "1e"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check_amount(value)

    def test_rejects_nan_and_infinity(self):
        for value in ["NaN", "Infinity", "-Infinity"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check_amount(value)

    def test_rejects_more_precision_than_the_token_has(self):
        check_amount("1.123456")
        with self.assertRaises(ValueError):
            check_amount("1.1234567")

    def test_enforces_a_minimum(self):
        with self.assertRaises(ValueError):
            check_amount("9.99", minimum="10")
        self.assertEqual(check_amount("10.01", minimum="10"), Decimal("10.01"))

    def test_enforces_a_maximum_when_given(self):
        with self.assertRaises(ValueError):
            check_amount("1000", maximum="500")
        self.assertEqual(check_amount("500", maximum="500"), Decimal("500"))


class TestToBaseUnits(unittest.TestCase):
    def test_scales_exactly(self):
        self.assertEqual(to_base_units(Decimal("4200.69")), 4_200_690_000)
        self.assertEqual(to_base_units(Decimal("0.000001")), 1)

    def test_matches_the_written_decimal_not_the_float(self):
        # `int(round(4200.69 * 1_000_000))` - the previous implementation - is compared
        # against the exact decimal result. They agree for this literal, which is why
        # the old code appeared to work; the point is that the new path does not depend
        # on that coincidence. `0.1 + 0.2` is asserted separately as the case where
        # binary floating point visibly diverges.
        self.assertEqual(to_base_units(Decimal("4200.69")), int(round(4200.69 * 1_000_000)))
        self.assertEqual(to_base_units(Decimal("0.1") + Decimal("0.2")), 300_000)
        self.assertNotEqual(0.1 + 0.2, 0.3)


class TestCheckLeverage(unittest.TestCase):
    def test_accepts_the_supported_range(self):
        self.assertEqual(check_leverage(1), 1)
        self.assertEqual(check_leverage(MAX_LEVERAGE), MAX_LEVERAGE)

    def test_rejects_out_of_range(self):
        for value in [0, -1, MAX_LEVERAGE + 1, 420]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check_leverage(value)

    def test_rejects_non_integers(self):
        for value in ["10", 10.5, True, None]:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    check_leverage(value)


class TestCheckAddress(unittest.TestCase):
    def test_accepts_a_32_byte_address(self):
        self.assertEqual(check_address(VALID_ADDRESS), VALID_ADDRESS)

    def test_trims_surrounding_whitespace(self):
        self.assertEqual(check_address(f"  {VALID_ADDRESS}\n"), VALID_ADDRESS)

    def test_rejects_the_wrong_length(self):
        # A truncated address is still valid base58, which is exactly why the length
        # check is the part that catches a real paste error.
        with self.assertRaises(ValueError):
            check_address(VALID_ADDRESS[:-4])

    def test_rejects_non_base58_and_empty(self):
        for value in ["not base58 !", "", "   ", None, 42]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check_address(value)


if __name__ == "__main__":
    unittest.main()
