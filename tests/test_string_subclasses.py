"""Hand-written contracts for stored string values and bounded subclass handling."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from typing import cast

import pytest

from figround import (
    InvalidNumberError,
    InvalidOptionError,
    Notation,
    format_sig,
    format_uncertainty,
    round_decimal,
)


class RaisingStrip(str):
    def strip(self, chars: str | None = None) -> str:
        raise RuntimeError("PRIVATE_CANARY strip")

    def __str__(self) -> str:
        raise RuntimeError("PRIVATE_CANARY conversion")


class RaisingInequality(str):
    def __ne__(self, other: object) -> bool:
        raise RuntimeError("PRIVATE_CANARY inequality")


class RaisingComparisons(RaisingInequality):
    def __eq__(self, other: object) -> bool:
        raise RuntimeError("PRIVATE_CANARY equality")

    def __str__(self) -> str:
        raise RuntimeError("PRIVATE_CANARY conversion")


@pytest.mark.parametrize("digits", [32000, 128000])
def test_string_strip_cannot_substitute_an_oversized_integer(digits: int) -> None:
    huge: int = 10**digits - 1

    class IntegerStrip(str):
        def strip(self, chars: str | None = None) -> int:  # type: ignore[override]
            return huge

    assert round_decimal(IntegerStrip(" 1.25 "), 3).as_tuple() == Decimal("1.25").as_tuple()


@pytest.mark.parametrize("trap", [False, True])
@pytest.mark.parametrize("text", [" 1.25 ", "PRIVATE_CANARY", "NaN"])
def test_numeric_string_subclass_uses_stored_text_without_context_changes(
    trap: bool, text: str
) -> None:
    with localcontext() as context:
        context.clear_flags()
        context.traps[InvalidOperation] = trap
        flags, traps = context.flags.copy(), context.traps.copy()
        try:
            if text == " 1.25 ":
                assert round_decimal(RaisingStrip(text), 2) == Decimal("1.2")
            else:
                with pytest.raises(InvalidNumberError) as caught:
                    round_decimal(RaisingStrip(text), 2)
                assert len(str(caught.value)) < 100
                assert "PRIVATE_CANARY" not in str(caught.value)
        finally:
            assert context.flags == flags
            assert context.traps == traps


@pytest.mark.parametrize("wrapper", [RaisingInequality, RaisingComparisons])
def test_notation_subclass_conflict_raises_bounded_typed_error(wrapper: type[str]) -> None:
    with pytest.raises(InvalidOptionError) as caught:
        format_sig(1, 2, sci=True, notation=cast(Notation, wrapper("fixed")))
    assert str(caught.value) == "sci=True requires scientific notation"


@pytest.mark.parametrize(
    "text, expected", [("fixed", "1.0"), ("sci", "1.0e+00"), ("eng", "1.0e+00")]
)
def test_notation_subclass_uses_stored_text_through_rendering(text: str, expected: str) -> None:
    notation = cast(Notation, RaisingComparisons(text))
    assert format_sig(1, 2, notation=notation) == expected
    if text == "sci":
        assert format_sig(1, 2, sci=True, notation=notation) == expected
    expected_uncertainty = "1.00(10)" + ("" if text == "fixed" else "e+00")
    assert format_uncertainty(1, "0.1", notation=notation) == expected_uncertainty


def test_unknown_notation_subclass_raises_bounded_typed_error() -> None:
    notation = cast(Notation, RaisingComparisons("PRIVATE_CANARY"))
    with pytest.raises(InvalidOptionError) as caught:
        format_sig(1, 2, notation=notation)
    assert str(caught.value) == "unknown notation; use one of fixed, sci, eng"
