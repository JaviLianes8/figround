"""Hand-written contracts for signed zero, counting and independent rounding modes."""

from __future__ import annotations

import math
from decimal import Decimal

import pytest

from figround import count_sig, round_sig, round_uncertainty, sig_bounds


@pytest.mark.parametrize("value, sign", [("-1e-400", -1), ("1e-400", 1), ("-0", 1)])
def test_float_underflow_preserves_sign(value: str, sign: int) -> None:
    result = round_sig(value, 2)
    assert result == 0.0
    assert math.copysign(1.0, result) == sign


@pytest.mark.parametrize("value, digits", [("0E+3", 1), ("0E+0", 1), ("0E-3", 4)])
def test_decimal_zero_count_uses_only_decimal_places(value: str, digits: int) -> None:
    zero = Decimal(value)
    assert sig_bounds(zero) == (digits, digits)
    assert count_sig(zero) == count_sig(zero, strict=True) == digits


def test_uncertainty_rounding_does_not_override_value_rounding() -> None:
    value, spread = round_uncertainty(
        "2.41", "0.11", 1, rounding="half_down", uncertainty_rounding="up"
    )
    assert value.as_tuple() == Decimal("2.4").as_tuple()
    assert spread.as_tuple() == Decimal("0.2").as_tuple()


@pytest.mark.parametrize("value", ["-0.004", "-0"])
def test_uncertainty_result_zero_is_positive(value: str) -> None:
    rounded, _ = round_uncertainty(value, "0.25")
    assert rounded.is_zero()
    assert not rounded.is_signed()
