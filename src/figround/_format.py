"""Render significant-figure values as strings while keeping trailing zeros."""

from __future__ import annotations

from ._errors import InvalidOptionError
from ._modes import Notation, Rounding, check_notation
from ._render import exponent_marker, fixed, power_for, shift
from ._round import Number, round_decimal
from ._validation import check_bool


def _resolve_notation(sci: bool, notation: str | None) -> str:
    if notation is None:
        return "sci" if sci else "fixed"
    check_notation(notation)
    if sci and notation != "sci":
        raise InvalidOptionError(f"sci=True conflicts with notation={notation!r}")
    return notation


def format_sig(
    x: Number,
    figures: int,
    *,
    sci: bool = False,
    notation: Notation | None = None,
    rounding: Rounding = "half_even",
    trailing_point: bool = False,
) -> str:
    """Round ``x`` to ``figures`` significant figures and write it, keeping trailing zeros.

    >>> format_sig(1.2, 3)
    '1.20'
    >>> format_sig(0.00012345, 2, sci=True)
    '1.2e-04'
    >>> format_sig(123456, 4, notation="eng")
    '123.5e+03'
    >>> format_sig(1000, 4, trailing_point=True)
    '1000.'

    ``notation`` is ``"fixed"`` (default), ``"sci"`` (one digit before the point) or
    ``"eng"`` (exponent a multiple of three). ``sci=True`` is the 0.1.0 spelling of
    ``notation="sci"``. Exponents are written ``e+03`` / ``e-04``. When fewer figures are
    requested than there are digits before the point (``format_sig(1234, 2)`` gives
    ``"1200"``) the placeholder zeros are ambiguous on paper; use ``"sci"`` to avoid it.
    ``"eng"`` has the same issue inside the mantissa (``format_sig(12, 1, notation="eng")``
    is ``"10e+00"``). Fixed notation refuses to write more than 10000 placeholder zeros
    (``InvalidNumberError``); use ``"sci"`` for such magnitudes.
    ``trailing_point`` marks a whole number whose zeros are all significant.

    Raises the errors of ``round_decimal``, plus ``InvalidOptionError`` for an unknown
    ``notation`` or one that conflicts with ``sci=True``. Wrong option types raise
    ``TypeError``; ``sci`` and ``trailing_point`` must be actual booleans.
    """
    check_bool(sci, "sci")
    check_bool(trailing_point, "trailing_point")
    chosen = _resolve_notation(sci, notation)
    rounded = round_decimal(x, figures, rounding=rounding)
    if chosen == "fixed":
        return fixed(rounded, trailing_point=trailing_point)
    power = power_for(rounded, chosen)
    mantissa = fixed(shift(rounded, power), trailing_point=trailing_point)
    return mantissa + exponent_marker(power)
