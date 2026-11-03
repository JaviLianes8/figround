"""Hand-written contracts: no public entry point runs instance hooks of a supplied value."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

import pytest

from figround import (
    InvalidNumberError,
    count_sig,
    format_sig,
    format_uncertainty,
    round_decimal,
    round_sig,
    round_uncertainty,
    sig_bounds,
)
from figround._cli import main

CANARY = "PRIVATE_CANARY"
_HOOKS = (  # noqa: SIM905
    "__getattribute__ __eq__ __ne__ __lt__ __le__ __gt__ __ge__ __hash__ __str__ "
    "__repr__ __format__ __bool__ __len__ __getitem__ __iter__ __contains__ __int__ "
    "__index__ __float__ __add__ __radd__ __sub__ __rsub__ __mul__ __neg__ __pos__ "
    "__abs__ __round__"
).split()


def hooked(base: type[Any], calls: list[str]) -> type[Any]:
    """A subclass of ``base`` whose attribute access and overridable dunders record and raise."""

    def make(name: str) -> Any:
        def hook(*args: object, **kwargs: object) -> Any:
            calls.append(name)
            raise RuntimeError(CANARY)

        return hook

    return type("Hooked", (base,), {name: make(name) for name in _HOOKS})


def spoof(kind: type[Any]) -> Any:
    """An object that claims ``kind`` as its ``__class__`` and raises on any other use."""

    class Spoof:
        def __getattribute__(self, name: str) -> Any:
            if name == "__class__":
                return kind
            raise RuntimeError(CANARY)

        def __bool__(self) -> bool:
            raise RuntimeError(CANARY)

    return Spoof()


@pytest.fixture
def calls() -> list[str]:
    return []


def test_numeric_text_subclass_reads_stored_text_without_hooks(calls: list[str]) -> None:
    text = hooked(str, calls)(" \t6.92\n")
    assert round_decimal(text, 3).as_tuple() == Decimal("6.92").as_tuple()
    assert calls == []


@pytest.mark.parametrize("base, raw", [(int, 692), (float, 6.92), (Decimal, Decimal("6.92"))])
def test_numeric_subclass_reads_base_value_without_hooks(
    base: type[Any], raw: object, calls: list[str]
) -> None:
    expected = round_decimal(cast(Any, raw), 3)
    assert round_decimal(hooked(base, calls)(raw), 3).as_tuple() == expected.as_tuple()
    assert calls == []


@pytest.mark.parametrize("base, raw", [(str, " 6.92 "), (int, 7), (float, 6.92), (Decimal, "6.92")])
def test_public_wrappers_reach_numeric_conversion_without_hooks(
    base: type[Any], raw: object, calls: list[str]
) -> None:
    cls = hooked(base, calls)
    value, spread = cls(raw), cls(raw)
    assert format_sig(value, 2, notation="sci") == format_sig(cast(Any, raw), 2, notation="sci")
    assert round_sig(value, 2) == round_sig(cast(Any, raw), 2)
    assert round_uncertainty(value, spread, 1) == round_uncertainty(
        cast(Any, raw), cast(Any, raw), 1
    )
    assert format_uncertainty(value, spread, 1) == format_uncertainty(
        cast(Any, raw), cast(Any, raw), 1
    )
    assert calls == []


def test_decimal_subclass_methods_never_run_after_conversion(calls: list[str]) -> None:
    value = hooked(Decimal, calls)("0")
    assert round_decimal(value, 2) == Decimal("0.0")
    assert round_uncertainty(hooked(Decimal, calls)("1.25"), hooked(Decimal, calls)("0.11")) == (
        Decimal("1.25"),
        Decimal("0.11"),
    )
    assert calls == []


def test_figure_count_subclass_reads_base_integer_without_hooks(calls: list[str]) -> None:
    figures = hooked(int, calls)(2)
    assert round_decimal("1.25", figures) == Decimal("1.2")
    assert round_uncertainty("1.25", "0.11", figures) == (Decimal("1.25"), Decimal("0.11"))
    assert calls == []


def test_rounding_subclasses_use_stored_text_without_hooks(calls: list[str]) -> None:
    mode = hooked(str, calls)("half_up")
    assert round_decimal("2.5", 1, rounding=mode) == Decimal("3")
    assert round_uncertainty("1", "10.47", uncertainty_rounding=hooked(str, calls)("up")) == (
        Decimal("1"),
        Decimal("11"),
    )
    assert calls == []


def test_notation_subclass_uses_stored_text_without_hooks(calls: list[str]) -> None:
    notation = hooked(str, calls)("sci")
    assert format_sig(1, 2, sci=True, notation=notation) == "1.0e+00"
    assert format_uncertainty(1, "0.1", notation=notation) == "1.00(10)e+00"
    assert calls == []


def test_style_and_symbol_subclasses_use_stored_text_without_hooks(calls: list[str]) -> None:
    style, symbol = hooked(str, calls)("pm"), hooked(str, calls)("Â±")
    assert format_uncertainty(1, "0.1", style=style, pm=symbol) == "1.00 Â± 0.10"
    assert calls == []


def test_count_text_subclass_reads_stored_text_without_hooks(calls: list[str]) -> None:
    text = hooked(str, calls)(" 1200 ")
    assert sig_bounds(text) == (2, 4)
    assert count_sig(text) == 2
    assert calls == []


def test_count_decimal_subclass_reads_base_value_without_hooks(calls: list[str]) -> None:
    assert sig_bounds(hooked(Decimal, calls)("1200")) == (4, 4)
    assert count_sig(hooked(Decimal, calls)("0.00")) == 3
    assert calls == []


@pytest.mark.parametrize("option", ["sci", "trailing_point"])
def test_spoofed_boolean_format_options_raise_type_error(option: str) -> None:
    with pytest.raises(TypeError, match=rf"^{option} must be a bool$"):
        format_sig(1000, 4, **{option: spoof(bool)})


def test_spoofed_boolean_strict_raises_type_error() -> None:
    with pytest.raises(TypeError, match=r"^strict must be a bool$"):
        count_sig("1200", strict=spoof(bool))


@pytest.mark.parametrize("kind", [Decimal, int, float, str])
def test_spoofed_numeric_class_raises_type_error(kind: type[Any]) -> None:
    with pytest.raises(TypeError, match=r"^expected int, float, str or Decimal$"):
        round_decimal(spoof(kind), 3)
    with pytest.raises(TypeError, match=r"^figures must be an int$"):
        round_decimal("1", spoof(int))


@pytest.mark.parametrize("kind", [Decimal, str])
def test_spoofed_count_input_raises_type_error(kind: type[Any]) -> None:
    with pytest.raises(TypeError, match=r"^expected str or Decimal$"):
        sig_bounds(spoof(kind))


@pytest.mark.parametrize("option", ["rounding", "notation", "style", "pm"])
def test_spoofed_string_options_raise_type_error(option: str) -> None:
    call = round_decimal if option == "rounding" else format_uncertainty
    args = ("1", 2) if option == "rounding" else ("1", "0.1")
    with pytest.raises(TypeError, match=rf"^{option} must be a str$"):
        call(*args, **{option: spoof(str)})


def test_invalid_hooked_text_raises_bounded_typed_error(calls: list[str]) -> None:
    with pytest.raises(InvalidNumberError) as caught:
        round_decimal(hooked(str, calls)(CANARY), 3)
    assert str(caught.value) == "not a number"
    assert calls == []


def test_cli_arguments_subclasses_use_stored_text_without_hooks(
    calls: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    cls = hooked(str, calls)
    argv = [cls("format"), cls("1.25"), cls("-u"), cls("0.11"), cls("--style"), cls("pm")]
    assert main(argv) == 0
    assert capsys.readouterr().out == "1.25 +/- 0.11\n"
    assert calls == []
