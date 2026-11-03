from decimal import Decimal

import pytest

from figround import round_sig


def test_rounds_to_significant_figures() -> None:
    assert round_sig(123456, 3) == 123000.0
    assert round_sig(0.00123456, 3) == 0.00123


def test_keeps_small_values_exact_without_binary_drift() -> None:
    # Decimal("2.675") rounds up where the binary float 2.675 would round down.
    assert round_sig(2.675, 3) == 2.68


def test_rounds_half_to_even() -> None:
    assert round_sig(1.25, 2) == 1.2
    assert round_sig(1.35, 2) == 1.4
    assert round_sig(2.5, 1) == 2.0


def test_zero_rounds_to_zero() -> None:
    assert round_sig(0, 3) == 0.0
    assert round_sig(0.0, 1) == 0.0


def test_negatives_round_by_magnitude() -> None:
    assert round_sig(-123456, 3) == -123000.0
    assert round_sig(-0.0987, 2) == -0.099


def test_very_large_and_very_small_magnitudes() -> None:
    assert round_sig(1.23456e30, 3) == 1.23e30
    assert round_sig(9.87654e-30, 2) == 9.9e-30


def test_rounding_carry_increases_magnitude() -> None:
    assert round_sig(9.99, 2) == 10.0
    assert round_sig(999.9, 3) == 1000.0


def test_accepts_strings_and_decimals() -> None:
    assert round_sig("123.456", 4) == 123.5
    assert round_sig(Decimal("0.0045678"), 2) == 0.0046


def test_rejects_non_positive_figures() -> None:
    with pytest.raises(ValueError):
        round_sig(1.0, 0)


def test_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError):
        round_sig(float("inf"), 3)
    with pytest.raises(ValueError):
        round_sig(float("nan"), 3)


def test_rejects_bad_types() -> None:
    with pytest.raises(TypeError):
        round_sig(True, 3)
    with pytest.raises(TypeError):
        round_sig(1.0, 2.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        round_sig("not a number", 3)
