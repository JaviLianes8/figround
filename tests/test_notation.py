"""Notations, rounding modes and exact Decimal results. Hand-written cases."""

from decimal import Decimal

import pytest

from figround import ROUNDING_MODES, InvalidOptionError, format_sig, round_decimal, round_sig


@pytest.mark.parametrize(
    ("value", "figures", "expected"),
    [
        (123456, 4, "123.5e+03"),
        (1234, 2, "1.2e+03"),
        (12, 3, "12.0e+00"),
        (0.00012, 2, "120e-06"),
        ("0.0012345", 3, "1.23e-03"),
        ("-45678", 3, "-45.7e+03"),
        (0, 2, "0.0e+00"),
        (999.96, 4, "1.000e+03"),  # the carry moves the value into the next group
    ],
)
def test_engineering_notation(value: object, figures: int, expected: str) -> None:
    assert format_sig(value, figures, notation="eng") == expected  # type: ignore[arg-type]


def test_scientific_spellings_agree() -> None:
    assert format_sig(1234, 3, notation="sci") == format_sig(1234, 3, sci=True) == "1.23e+03"


def test_fixed_keeps_zeros_on_both_sides_of_the_point() -> None:
    assert format_sig("0.000120", 3, notation="fixed") == "0.000120"
    assert format_sig("1.2e-7", 3) == "0.000000120"
    assert format_sig("1.2e7", 3) == "12000000"


def test_trailing_point_marks_significant_zeros() -> None:
    assert format_sig(1000, 4, trailing_point=True) == "1000."
    assert format_sig(1000, 3, trailing_point=True) == "1000"  # last zero is a placeholder
    assert format_sig(1234, 4, trailing_point=True) == "1234"
    assert format_sig(10, 2, notation="eng", trailing_point=True) == "10.e+00"


def test_conflicting_notation_is_rejected() -> None:
    with pytest.raises(InvalidOptionError):
        format_sig(1, 2, sci=True, notation="eng")
    with pytest.raises(InvalidOptionError):
        format_sig(1, 2, notation="hex")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("mode", "positive", "negative"),
    [
        ("half_even", "2.4", "-2.4"),
        ("half_up", "2.5", "-2.5"),
        ("half_down", "2.4", "-2.4"),
        ("up", "2.5", "-2.5"),
        ("down", "2.4", "-2.4"),
        ("ceiling", "2.5", "-2.4"),
        ("floor", "2.4", "-2.5"),
        ("05up", "2.4", "-2.4"),
    ],
)
def test_every_mode_on_a_tie(mode: str, positive: str, negative: str) -> None:
    assert format_sig("2.45", 2, rounding=mode) == positive  # type: ignore[arg-type]
    assert format_sig("-2.45", 2, rounding=mode) == negative  # type: ignore[arg-type]


def test_mode_list_is_complete() -> None:
    assert len(ROUNDING_MODES) == 8
    for mode in ROUNDING_MODES:
        assert round_decimal("1.05", 2, rounding=mode) in {Decimal("1.0"), Decimal("1.1")}  # type: ignore[arg-type]


def test_round_decimal_records_figures_in_the_exponent() -> None:
    assert str(round_decimal(1.2, 3)) == "1.20"
    assert str(round_decimal(123456, 2)) == "1.2E+5"
    assert str(round_decimal(0, 3)) == "0.00"
    assert str(round_decimal("-0.0", 2)) == "0.0"
    assert str(round_decimal("9.96", 2)) == "10"


def test_huge_and_tiny_exponents_are_exact() -> None:
    assert str(round_decimal("1.23456e-400", 3)) == "1.23E-400"
    assert format_sig("9.995e999", 3, notation="sci") == "1.00e+1000"
    assert round_sig("1.5e-320", 1) == 2e-320


def test_floats_are_read_through_repr() -> None:
    # 2.675 as a binary float is 2.67499999...; figround reads the shortest repr "2.675".
    assert format_sig(2.675, 3) == "2.68"
    assert format_sig(0.1 + 0.2, 2) == "0.30"
    assert round_decimal(1e22, 2) == Decimal("1.0E+22")


def test_round_sig_keeps_its_0_1_0_behaviour() -> None:
    assert round_sig(1.25, 2) == 1.2
    assert round_sig(1.25, 2, rounding="half_up") == 1.3
