"""Counting significant figures of written numbers. Hand-written cases from the stated rules."""

from decimal import Decimal

import pytest

from figround import AmbiguousFiguresError, InvalidNumberError, count_sig, sig_bounds


@pytest.mark.parametrize(
    ("text", "bounds"),
    [
        ("123", (3, 3)),
        ("0.00120", (3, 3)),  # leading zeros never count, trailing ones after a point do
        ("0.0450", (3, 3)),
        ("1200", (2, 4)),  # whole-number trailing zeros are ambiguous
        ("1200.", (4, 4)),  # an explicit point makes them significant
        ("1200.0", (5, 5)),
        ("100", (1, 3)),
        ("1001", (4, 4)),  # zeros between nonzero digits count
        ("1.20e3", (3, 3)),  # the exponent never changes the count
        ("6.022E23", (4, 4)),
        ("1200e-2", (2, 4)),  # no point in the mantissa: still ambiguous
        ("-0.050", (2, 2)),
        ("+7", (1, 1)),
        (".5", (1, 1)),
        ("5.", (1, 1)),
        ("0", (1, 1)),  # a zero counts one plus its decimal places
        ("0.00", (3, 3)),
        ("0e5", (1, 1)),
        ("  42  ", (2, 2)),
    ],
)
def test_sig_bounds(text: str, bounds: tuple[int, int]) -> None:
    assert sig_bounds(text) == bounds


def test_count_sig_takes_the_conservative_reading() -> None:
    assert count_sig("1200") == 2
    assert count_sig("1200.") == 4


def test_strict_count_rejects_ambiguous_zeros() -> None:
    with pytest.raises(AmbiguousFiguresError, match="2 to 4"):
        count_sig("1200", strict=True)
    assert count_sig("1.200e3", strict=True) == 4


def test_decimal_input_is_exact() -> None:
    assert sig_bounds(Decimal("1200")) == (4, 4)
    assert sig_bounds(Decimal("1.2E+3")) == (2, 2)
    assert sig_bounds(Decimal("0.00")) == (3, 3)


@pytest.mark.parametrize("text", ["", ".", "abc", "1.2.3", "1e", "e5", "nan", "inf", "1,000"])
def test_rejects_text_that_is_not_a_number(text: str) -> None:
    with pytest.raises(InvalidNumberError):
        count_sig(text)


def test_rejects_non_finite_decimal() -> None:
    with pytest.raises(InvalidNumberError):
        sig_bounds(Decimal("NaN"))


@pytest.mark.parametrize("value", [1200, 1.5, None])
def test_rejects_numbers_that_cannot_record_zeros(value: object) -> None:
    with pytest.raises(TypeError):
        count_sig(value)  # type: ignore[arg-type]


def test_round_trip_with_format() -> None:
    from figround import format_sig

    for figures in range(1, 8):
        assert count_sig(format_sig("0.000123456789", figures)) == figures
        assert count_sig(format_sig("123456789", figures, notation="sci")) == figures
