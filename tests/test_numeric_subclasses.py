"""Hand-written contracts for bounded conversions and numeric subclass handling."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from typing import cast

import pytest

from figround import (
    InvalidFiguresError,
    InvalidNumberError,
    InvalidOptionError,
    Notation,
    format_sig,
    format_uncertainty,
    round_decimal,
    round_uncertainty,
)


class WrappedFloat(float):
    def __repr__(self) -> str:
        return "PRIVATE_CANARY"

    def __float__(self) -> float:
        raise AssertionError("custom conversion must not run")


class WrappedInt(int):
    def __le__(self, other: int) -> bool:
        return True

    def __ge__(self, other: int) -> bool:
        return True

    def __sub__(self, other: int) -> int:
        return 10001

    def __rsub__(self, other: int) -> int:
        return 10001

    def __int__(self) -> int:
        return 10001

    def bit_length(self) -> int:
        return 1


class WrappedNotation(str):
    def __repr__(self) -> str:
        return "PRIVATE_CANARY" * 100000


@pytest.mark.parametrize("trap", [False, True])
def test_float_subclass_uses_base_value_without_context_changes(trap: bool) -> None:
    with localcontext() as context:
        context.clear_flags()
        context.traps[InvalidOperation] = trap
        flags, traps = context.flags.copy(), context.traps.copy()
        try:
            assert round_decimal(WrappedFloat(1.25), 2) == Decimal("1.2")
        finally:
            assert context.flags == flags
            assert context.traps == traps


def test_notation_conflict_does_not_render_supplied_object() -> None:
    with pytest.raises(InvalidOptionError) as caught:
        format_sig(1, 2, sci=True, notation=cast(Notation, WrappedNotation("fixed")))
    message = str(caught.value)
    assert len(message) < 100
    assert "PRIVATE_CANARY" not in message


@pytest.mark.parametrize("figures", [-1, 0, 10001, 10**100])
def test_int_subclass_cannot_bypass_figure_limits(figures: int) -> None:
    with pytest.raises(InvalidFiguresError):
        round_decimal("1", WrappedInt(figures))
    with pytest.raises(InvalidFiguresError):
        round_uncertainty("1", "1", WrappedInt(figures))


def test_int_subclass_is_normalized_before_precision_arithmetic() -> None:
    assert round_decimal("1.25", WrappedInt(2)).as_tuple() == Decimal("1.2").as_tuple()
    assert round_decimal("0", WrappedInt(2)).as_tuple() == Decimal("0.0").as_tuple()
    assert format_uncertainty("1.25", "0.11", WrappedInt(2)) == "1.25(11)"


@pytest.mark.parametrize("sign", [-1, 1])
def test_integer_conversion_bit_limit_is_inclusive(sign: int) -> None:
    accepted = sign * (1 << 65535)
    expected = round_decimal(Decimal(accepted), 3)
    assert round_decimal(accepted, 3) == expected
    with pytest.raises(InvalidNumberError, match="65536 bits"):
        round_decimal(sign * (1 << 65536), 3)
    with pytest.raises(InvalidNumberError, match="65536 bits"):
        round_uncertainty("0", WrappedInt(sign * (1 << 65536)), 1)
