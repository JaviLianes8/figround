"""Failure contracts and independence from ambient decimal settings."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal, DefaultContext, Inexact, InvalidOperation, localcontext

import pytest

from figround import (
    FigroundError,
    InvalidFiguresError,
    InvalidNumberError,
    count_sig,
    format_sig,
    format_uncertainty,
    round_decimal,
    round_uncertainty,
    sig_bounds,
)


@pytest.mark.parametrize(
    "call",
    [
        lambda: round_decimal("SECRET" * 10000, 2),
        lambda: sig_bounds("SECRET" * 10000),
        lambda: round_decimal("1", 10**5000),
        lambda: round_decimal(1, 2, rounding="SECRET" * 10000),  # type: ignore[arg-type]
        lambda: format_sig(1, 2, notation="SECRET" * 10000),  # type: ignore[arg-type]
        lambda: format_uncertainty(1, 1, style="SECRET" * 10000),  # type: ignore[arg-type]
        lambda: round_uncertainty(1, "-" + "9" * 10000),
        lambda: sig_bounds(Decimal("NaN" + "9" * 10000)),
        lambda: count_sig("1" + "0" * 10000, strict=True),
    ],
)
def test_errors_are_bounded_and_do_not_echo_input(call: Callable[[], object]) -> None:
    with pytest.raises(FigroundError) as error:
        call()
    assert len(str(error.value)) < 200
    assert "SECRET" not in str(error.value)


@pytest.mark.parametrize("traps", [False, True])
def test_caller_context_and_flags_survive_success_and_failure(traps: bool) -> None:
    with localcontext() as ctx:
        ctx.prec, ctx.Emax, ctx.Emin, ctx.clamp = 1, 2, -2, 1
        for signal in ctx.traps:
            ctx.traps[signal] = traps
        ctx.clear_flags()
        before = ctx.copy()
        assert format_sig("2.675", 3) == "2.68"
        assert format_uncertainty("100.02147", "0.00035") == "100.02147(35)"
        for value in ("secret", "1e9999999999999999999", "NaN", "sNaN"):
            with pytest.raises(InvalidNumberError):
                round_decimal(value, 3)
        assert ctx.flags == before.flags
        assert ctx.traps == before.traps
        assert (ctx.prec, ctx.Emax, ctx.Emin, ctx.clamp) == (1, 2, -2, 1)


def test_default_context_cannot_change_rounding() -> None:
    saved = DefaultContext.copy()
    try:
        DefaultContext.clamp = 1
        DefaultContext.traps[Inexact] = True
        DefaultContext.traps[InvalidOperation] = False
        assert format_sig("2.675", 3) == "2.68"
        with pytest.raises(InvalidNumberError):
            round_decimal("not numeric", 3)
    finally:
        DefaultContext.clamp = saved.clamp
        DefaultContext.traps = saved.traps


@pytest.mark.parametrize(
    "call",
    [
        lambda: count_sig("1", strict=1),  # type: ignore[arg-type]
        lambda: format_sig(1, 2, sci=1),  # type: ignore[arg-type]
        lambda: format_sig(1, 2, trailing_point="yes"),  # type: ignore[arg-type]
        lambda: format_sig(1, 2, notation=[]),  # type: ignore[arg-type]
        lambda: round_decimal(1, 2, rounding=[]),  # type: ignore[arg-type]
        lambda: format_uncertainty(1, 1, style=[]),  # type: ignore[arg-type]
        lambda: format_uncertainty(1, 1, pm=None),  # type: ignore[arg-type]
    ],
)
def test_wrong_option_types_raise_type_error(call: Callable[[], object]) -> None:
    with pytest.raises(TypeError):
        call()


def test_precision_and_output_limits() -> None:
    assert len(format_sig(0, 10000)) == 10001
    with pytest.raises(InvalidFiguresError):
        round_decimal(1, 10001)
    assert len(format_sig("1e-10001", 1)) == 10003
    with pytest.raises(InvalidNumberError):
        format_sig("1e-10002", 1)
    assert format_sig("1e-10002", 1, notation="sci") == "1e-10002"
