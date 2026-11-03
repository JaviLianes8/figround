"""Typed errors: each is a FigroundError and still a ValueError, as in 0.1.0."""

import pytest

import figround
from figround import (
    AmbiguousFiguresError,
    FigroundError,
    InvalidFiguresError,
    InvalidNumberError,
    InvalidOptionError,
    UncertaintyError,
    format_sig,
    round_decimal,
    round_sig,
)

ERRORS = [
    AmbiguousFiguresError,
    InvalidFiguresError,
    InvalidNumberError,
    InvalidOptionError,
    UncertaintyError,
]


@pytest.mark.parametrize("error", ERRORS)
def test_hierarchy(error: type[Exception]) -> None:
    assert issubclass(error, FigroundError)
    assert issubclass(error, ValueError)


@pytest.mark.parametrize("text", ["abc", "", "1.2.3", "nan", "-inf", "Infinity", "sNaN"])
def test_invalid_numbers(text: str) -> None:
    with pytest.raises(InvalidNumberError):
        round_decimal(text, 2)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_floats(value: float) -> None:
    with pytest.raises(InvalidNumberError):
        format_sig(value, 2)


@pytest.mark.parametrize("figures", [0, -1])
def test_invalid_figures(figures: int) -> None:
    with pytest.raises(InvalidFiguresError):
        round_sig(1, figures)


def test_unknown_rounding() -> None:
    with pytest.raises(InvalidOptionError, match="half_even"):
        round_decimal(1, 2, rounding="nearest")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("value", "figures"), [(True, 2), (None, 2), ([1], 2), (1, 2.0), (1, True)]
)
def test_wrong_types_raise_type_error(value: object, figures: object) -> None:
    with pytest.raises(TypeError):
        round_decimal(value, figures)  # type: ignore[arg-type]


def test_0_1_0_callers_catching_value_error_still_work() -> None:
    for call in (lambda: round_sig("x", 2), lambda: format_sig(1, 0)):
        with pytest.raises(ValueError):
            call()


def test_errors_are_exported() -> None:
    for error in ERRORS:
        assert getattr(figround, error.__name__) is error


@pytest.mark.parametrize(
    "call",
    [
        lambda: format_sig("1e999999999999999999", 3),
        lambda: format_sig("9.999e999999999999999999", 3, notation="sci"),
        lambda: round_decimal("1e-1000000000000000010", 2),
        lambda: format_sig("1e10002", 2),
        lambda: format_sig("1e-10003", 2),
    ],
)
def test_out_of_range_magnitudes_raise_typed_errors(call: object) -> None:
    with pytest.raises(InvalidNumberError):
        call()  # type: ignore[operator]


def test_fixed_limit_is_inclusive_and_sci_still_works() -> None:
    assert len(format_sig("1e10000", 1)) == 10001
    assert format_sig("1e10001", 2, notation="sci") == "1.0e+10001"


def test_figures_have_an_upper_bound() -> None:
    assert len(round_decimal(1, 10_000).as_tuple().digits) == 10_000
    for figures in (10_001, 10**19):
        with pytest.raises(InvalidFiguresError):
            round_decimal(1, figures)


def test_uncertainty_far_below_the_value_is_rejected() -> None:
    from figround import round_uncertainty

    with pytest.raises(UncertaintyError):
        round_uncertainty("1e999999999999999999", "1e-999999999999999999")
