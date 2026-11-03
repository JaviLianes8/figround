"""Rounding modes and notations accepted by the public functions."""

from __future__ import annotations

import decimal
from typing import Literal, get_args

from ._errors import InvalidOptionError

Rounding = Literal["half_even", "half_up", "half_down", "up", "down", "ceiling", "floor", "05up"]
"""Rounding mode names, the same eight algorithms as the ``decimal`` module."""

Notation = Literal["fixed", "sci", "eng"]
"""Output notation: positional, scientific (one leading digit) or engineering (exponent % 3)."""

ROUNDING_MODES: tuple[str, ...] = get_args(Rounding)
NOTATIONS: tuple[str, ...] = get_args(Notation)

_DECIMAL_MODES = {
    "half_even": decimal.ROUND_HALF_EVEN,
    "half_up": decimal.ROUND_HALF_UP,
    "half_down": decimal.ROUND_HALF_DOWN,
    "up": decimal.ROUND_UP,
    "down": decimal.ROUND_DOWN,
    "ceiling": decimal.ROUND_CEILING,
    "floor": decimal.ROUND_FLOOR,
    "05up": decimal.ROUND_05UP,
}


def decimal_mode(rounding: str) -> str:
    """Map a public rounding name to the ``decimal`` constant, rejecting unknown names."""
    if not isinstance(rounding, str):
        raise TypeError("rounding must be a str")
    try:
        return _DECIMAL_MODES[rounding]
    except (KeyError, TypeError):
        choices = ", ".join(ROUNDING_MODES)
        raise InvalidOptionError(f"unknown rounding; use one of {choices}") from None


def check_notation(notation: str) -> None:
    """Reject a notation name that is not one of ``NOTATIONS``."""
    if not isinstance(notation, str):
        raise TypeError("notation must be a str")
    if notation not in NOTATIONS:
        choices = ", ".join(NOTATIONS)
        raise InvalidOptionError(f"unknown notation; use one of {choices}")
