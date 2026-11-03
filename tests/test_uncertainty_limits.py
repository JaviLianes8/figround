"""Hand-written contracts for uncertainty precision and zero representation."""

from __future__ import annotations

from decimal import Context, Decimal

import pytest

from figround import UncertaintyError, format_uncertainty, round_uncertainty


@pytest.mark.parametrize("digits", [99999, 100000])
def test_uncertainty_accepts_inclusive_digit_limit(digits: int) -> None:
    number = Decimal(f"1e{digits - 1}")
    expected = number.quantize(Decimal(1), context=Context(prec=digits))
    value, spread = round_uncertainty(number, "1", 1)
    assert value.as_tuple() == expected.as_tuple()
    assert len(value.as_tuple().digits) == digits
    assert spread.as_tuple() == Decimal("1").as_tuple()


@pytest.mark.parametrize("rounding", ["down", "up"])
def test_uncertainty_carry_at_digit_limit(rounding: str) -> None:
    from typing import cast

    from figround import Rounding

    number = Decimal("9" * 100000 + ".9")
    if rounding == "up":
        with pytest.raises(UncertaintyError):
            round_uncertainty(number, "1", 1, rounding=cast(Rounding, rounding))
    else:
        value, _ = round_uncertainty(number, "1", 1, rounding=cast(Rounding, rounding))
        assert value.as_tuple() == Decimal("9" * 100000).as_tuple()


def test_uncertainty_rejects_above_digit_limit() -> None:
    with pytest.raises(UncertaintyError):
        round_uncertainty("1e100000", "1", 1)


@pytest.mark.parametrize("zero", ["0", "-0", "0e100000", "-0e1000000", "0e-1000000"])
@pytest.mark.parametrize("spread", ["1", "1e-100000"])
def test_uncertainty_zero_ignores_written_exponent(zero: str, spread: str) -> None:
    expected_spread = Decimal(spread)
    place = expected_spread.as_tuple().exponent
    assert isinstance(place, int)
    expected = Decimal((0, (0,), place))
    value, uncertainty = round_uncertainty(zero, spread, 1)
    assert value.as_tuple() == expected.as_tuple()
    assert uncertainty.as_tuple() == expected_spread.as_tuple()


def test_zero_uncertainty_scientific_format_at_tiny_scale() -> None:
    assert format_uncertainty("0", "1e-100000", notation="sci") == "0.0(10)e-100000"
