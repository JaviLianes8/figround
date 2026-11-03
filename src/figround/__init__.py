"""Significant-figures rounding and formatting: exact Decimal math, trailing zeros kept.

The type aliases describe accepted inputs and options; constants enumerate each option.

>>> from typing import get_args
>>> set(get_args(Number)) == {int, float, str, __import__("decimal").Decimal}
True
>>> get_args(Rounding) == ROUNDING_MODES
True
>>> get_args(Notation) == NOTATIONS == ("fixed", "sci", "eng")
True
>>> get_args(Style) == STYLES == ("paren", "pm")
True
"""

from __future__ import annotations

from ._count import count_sig, sig_bounds
from ._errors import (
    AmbiguousFiguresError,
    FigroundError,
    InvalidFiguresError,
    InvalidNumberError,
    InvalidOptionError,
    UncertaintyError,
)
from ._format import format_sig
from ._modes import NOTATIONS, ROUNDING_MODES, Notation, Rounding
from ._round import Number, round_decimal, round_sig
from ._uncertainty import STYLES, Style, format_uncertainty, round_uncertainty

__version__ = "1.0.0"

__all__ = [
    "NOTATIONS",
    "ROUNDING_MODES",
    "STYLES",
    "AmbiguousFiguresError",
    "FigroundError",
    "InvalidFiguresError",
    "InvalidNumberError",
    "InvalidOptionError",
    "Notation",
    "Number",
    "Rounding",
    "Style",
    "UncertaintyError",
    "count_sig",
    "format_sig",
    "format_uncertainty",
    "round_decimal",
    "round_sig",
    "round_uncertainty",
    "sig_bounds",
]

del annotations
