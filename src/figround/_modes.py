"""Rounding modes and notations accepted by the public functions."""

from __future__ import annotations

import decimal
from typing import Literal, cast, get_args

from ._errors import InvalidOptionError
from ._validation import check_str

Rounding = Literal["half_even", "half_up", "half_down", "up", "down", "ceiling", "floor", "05up"]
"""Rounding mode names, the same eight algorithms as the ``decimal`` module.

>>> get_args(Rounding) == ROUNDING_MODES
True
"""

Notation = Literal["fixed", "sci", "eng"]
"""Output notation: positional, scientific or engineering.

>>> get_args(Notation) == NOTATIONS
True
"""

ROUNDING_MODES: tuple[str, ...] = get_args(Rounding)
"""All accepted rounding option strings, in stable order.

>>> "half_even" in ROUNDING_MODES
True
"""
NOTATIONS: tuple[str, ...] = get_args(Notation)
"""All accepted output notations.

>>> NOTATIONS
('fixed', 'sci', 'eng')
"""

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
    """Map stored rounding text to the ``decimal`` constant, rejecting unknown names."""
    rounding = check_str(rounding, "rounding")
    try:
        return _DECIMAL_MODES[rounding]
    except KeyError:
        choices = ", ".join(ROUNDING_MODES)
        raise InvalidOptionError(f"unknown rounding; use one of {choices}") from None


def check_notation(notation: str) -> Notation:
    """Normalize stored notation text and reject names outside ``NOTATIONS``."""
    notation = check_str(notation, "notation")
    if notation not in NOTATIONS:
        choices = ", ".join(NOTATIONS)
        raise InvalidOptionError(f"unknown notation; use one of {choices}")
    return cast(Notation, notation)
