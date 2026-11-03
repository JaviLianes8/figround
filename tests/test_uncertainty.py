"""Value-with-uncertainty rounding and formatting. Hand-written cases; GUM vectors live in
test_sources.py."""

from decimal import Decimal

import pytest

from figround import (
    InvalidFiguresError,
    InvalidNumberError,
    InvalidOptionError,
    UncertaintyError,
    count_sig,
    format_uncertainty,
    round_uncertainty,
)


def test_uncertainty_keeps_the_requested_figures() -> None:
    assert round_uncertainty("1.23456", "0.0123") == (Decimal("1.235"), Decimal("0.012"))
    assert round_uncertainty("1.23456", "0.0123", 1) == (Decimal("1.23"), Decimal("0.01"))
    assert round_uncertainty("1.23456", "0.0123", 3) == (Decimal("1.2346"), Decimal("0.0123"))


def test_uncertainty_carry_moves_the_rounding_place() -> None:
    value, spread = round_uncertainty("5.04321", "0.0997")
    assert (str(value), str(spread)) == ("5.04", "0.10")


def test_value_smaller_than_its_uncertainty() -> None:
    assert format_uncertainty("0.0004", "0.25") == "0.00(25)"
    assert format_uncertainty("-0.004", "0.25") == "0.00(25)"
    assert format_uncertainty("-0.7", "0.25") == "-0.70(25)"


def test_uncertainty_wider_than_one_unit() -> None:
    assert format_uncertainty("1234.5", "12") == "1234(12)"
    assert format_uncertainty("123456", "1234") == "123500(1200)"
    assert format_uncertainty("123456", "1234", style="pm") == "123500 +/- 1200"


def test_shared_exponent_in_sci_and_eng() -> None:
    assert format_uncertainty("123456", "1234", notation="sci") == "1.235(12)e+05"
    assert format_uncertainty("123456", "1234", notation="eng") == "123.5(12)e+03"
    pm = format_uncertainty("0.000123456", "0.0000012", style="pm", notation="sci")
    assert pm == "(1.235 +/- 0.012)e-04"


def test_exponent_follows_the_uncertainty_when_it_is_larger() -> None:
    assert format_uncertainty("0.2", "35", notation="sci") == "0.0(35)e+01"
    assert format_uncertainty("0.2", "350", notation="sci", style="pm") == "(0.0 +/- 3.5)e+02"


def test_rounding_modes_apply_separately() -> None:
    assert round_uncertainty("2.45", "0.11", 1) == (Decimal("2.4"), Decimal("0.1"))
    up = round_uncertainty("2.45", "0.11", 1, rounding="half_up", uncertainty_rounding="up")
    assert up == (Decimal("2.5"), Decimal("0.2"))


def test_custom_plus_minus_symbol() -> None:
    text = format_uncertainty("1.234", "0.005", 1, style="pm", pm="±")
    assert text == "1.234 ± 0.005"


def test_value_figures_follow_the_uncertainty() -> None:
    value, _ = round_uncertainty("9.87654321", "0.00042")
    assert count_sig(str(value)) == 6


@pytest.mark.parametrize("bad", ["0", "-0.1", 0, -1.5])
def test_rejects_non_positive_uncertainty(bad: object) -> None:
    with pytest.raises(UncertaintyError):
        round_uncertainty(1, bad)  # type: ignore[arg-type]


def test_rejects_bad_options() -> None:
    with pytest.raises(InvalidOptionError):
        format_uncertainty(1, 0.1, style="brackets")  # type: ignore[arg-type]
    with pytest.raises(InvalidOptionError):
        format_uncertainty(1, 0.1, notation="fixedpoint")  # type: ignore[arg-type]
    with pytest.raises(InvalidOptionError):
        round_uncertainty(1, 0.1, uncertainty_rounding="nearest")  # type: ignore[arg-type]
    with pytest.raises(InvalidFiguresError):
        round_uncertainty(1, 0.1, 0)
    with pytest.raises(InvalidNumberError):
        round_uncertainty("x", 0.1)
    with pytest.raises(InvalidNumberError):
        round_uncertainty(1, "inf")
