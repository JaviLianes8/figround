from decimal import Decimal

import pytest

from figround import format_sig, round_sig


def test_keeps_trailing_zeros() -> None:
    assert format_sig(1.2, 3) == "1.20"
    assert format_sig(1, 3) == "1.00"
    assert format_sig(0.5, 4) == "0.5000"


def test_rounds_before_formatting() -> None:
    assert format_sig(123456, 3) == "123000"
    assert format_sig(0.00123456, 3) == "0.00123"
    assert format_sig(2.675, 3) == "2.68"


def test_format_differs_from_round_on_trailing_zeros() -> None:
    assert round_sig(1.2, 3) == 1.2
    assert format_sig(1.2, 3) == "1.20"


def test_negatives_keep_sign() -> None:
    assert format_sig(-0.0987, 2) == "-0.099"
    assert format_sig(-1234, 2) == "-1200"


def test_zero_shows_requested_precision() -> None:
    assert format_sig(0, 3) == "0.00"
    assert format_sig(0, 1) == "0"
    assert format_sig(0.0, 4) == "0.000"


def test_large_integer_keeps_placeholder_zeros() -> None:
    assert format_sig(1234, 2) == "1200"
    assert format_sig(9.99, 2) == "10"


def test_scientific_notation() -> None:
    assert format_sig(1.2, 3, sci=True) == "1.20e+00"
    assert format_sig(1234, 3, sci=True) == "1.23e+03"
    assert format_sig(0.00012345, 2, sci=True) == "1.2e-04"
    assert format_sig(9.99, 2, sci=True) == "1.0e+01"
    assert format_sig(-5, 1, sci=True) == "-5e+00"
    assert format_sig(0, 3, sci=True) == "0.00e+00"


def test_accepts_strings_and_decimals() -> None:
    assert format_sig("0.30", 2) == "0.30"
    assert format_sig(Decimal("7"), 3) == "7.00"


def test_rejects_non_positive_figures() -> None:
    with pytest.raises(ValueError):
        format_sig(1.0, 0)
