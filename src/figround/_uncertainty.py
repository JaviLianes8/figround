"""Round and write a value with its uncertainty as JCGM 100:2008 (the GUM) clause 7.2 asks."""

from __future__ import annotations

from decimal import Decimal, DecimalException
from typing import Literal, get_args

from ._errors import InvalidOptionError, UncertaintyError
from ._modes import Notation, Rounding, check_notation, decimal_mode
from ._render import exponent_marker, fixed, power_for, shift
from ._round import Number, check_figures, exact_context, out_of_range, round_value, to_decimal

Style = Literal["paren", "pm"]
"""Parenthesis or plus-minus uncertainty notation.

>>> get_args(Style) == STYLES
True
"""

STYLES: tuple[str, ...] = get_args(Style)
"""All accepted uncertainty styles.

>>> STYLES
('paren', 'pm')
"""
_MAX_DIGITS = 100_000


def round_uncertainty(
    value: Number,
    uncertainty: Number,
    figures: int = 2,
    *,
    rounding: Rounding = "half_even",
    uncertainty_rounding: Rounding | None = None,
) -> tuple[Decimal, Decimal]:
    """Round an uncertainty to ``figures`` significant figures and the value to match.

    GUM 7.2.6: quote the uncertainty to at most two significant digits and round the
    estimate to be consistent with it, that is, to the same decimal place:

    >>> round_uncertainty("10.05762", "0.027")
    (Decimal('10.058'), Decimal('0.027'))
    >>> round_uncertainty(100.02147, 0.00035)
    (Decimal('100.02147'), Decimal('0.00035'))
    >>> round_uncertainty("1", "10.47", uncertainty_rounding="up")
    (Decimal('1'), Decimal('11'))

    ``uncertainty_rounding`` defaults to ``rounding``; GUM 7.2.6 notes it may be
    appropriate to round an uncertainty up (``"up"``) rather than to the nearest digit.
    The sign of ``uncertainty`` must be positive.

    Raises:
        UncertaintyError: ``uncertainty`` is zero or negative, or so much smaller than
            ``value`` that the value would need more than 100000 digits.
        TypeError, InvalidNumberError, InvalidFiguresError, InvalidOptionError: as in
            ``round_decimal``.
    """
    figures = check_figures(figures)
    value_mode = decimal_mode(rounding)
    unc_mode = decimal_mode(rounding if uncertainty_rounding is None else uncertainty_rounding)
    number, spread = to_decimal(value), to_decimal(uncertainty)
    if spread <= 0:
        raise UncertaintyError("uncertainty must be positive")
    spread = round_value(spread, figures, unc_mode)
    place = spread.as_tuple().exponent
    assert isinstance(place, int)
    digits = 1 if number.is_zero() else max(number.adjusted() - place + 1, 1)
    if digits > _MAX_DIGITS:
        raise UncertaintyError("the value needs more than 100000 digits at this uncertainty")
    # Allow a carry during rounding, then enforce the limit on the actual result.
    ctx = exact_context(digits + 1, value_mode)
    try:
        rounded = number.quantize(Decimal(1).scaleb(place, ctx), context=ctx)
    except DecimalException:
        raise out_of_range() from None
    if len(rounded.as_tuple().digits) > _MAX_DIGITS:
        raise UncertaintyError("the value needs more than 100000 digits at this uncertainty")
    return (rounded.copy_abs() if rounded.is_zero() else rounded), spread


def _check_style(style: str) -> None:
    if not isinstance(style, str):
        raise TypeError("style must be a str")
    if style not in STYLES:
        raise InvalidOptionError(f"unknown style; use one of {', '.join(STYLES)}")


def _in_last_digits(value: Decimal, spread: Decimal) -> str:
    """The uncertainty counted in units of the last digit written for ``value``."""
    exponent = value.as_tuple().exponent
    assert isinstance(exponent, int)
    return fixed(shift(spread, min(exponent, 0)))


def format_uncertainty(
    value: Number,
    uncertainty: Number,
    figures: int = 2,
    *,
    style: Style = "paren",
    notation: Notation = "fixed",
    rounding: Rounding = "half_even",
    uncertainty_rounding: Rounding | None = None,
    pm: str = "+/-",
) -> str:
    """Write a value with its standard uncertainty, both rounded per ``round_uncertainty``.

    >>> format_uncertainty(100.02147, 0.00035)
    '100.02147(35)'
    >>> format_uncertainty(100.02147, 0.00035, style="pm")
    '100.02147 +/- 0.00035'
    >>> format_uncertainty(6.02214129e23, 2.7e16, notation="sci")
    '6.02214129(27)e+23'
    >>> format_uncertainty(1234.56, 21, style="pm", notation="eng")
    '(1.235 +/- 0.021)e+03'

    In ``"paren"`` style the number in parentheses is the uncertainty referred to the
    last digits of the quoted value (GUM 7.2.2 form 2); when the value is written
    without decimals the uncertainty is in units of one (``"123500(1200)"``).
    ``"pm"`` is GUM form 4; ``pm`` sets the symbol, for example ``"\\u00b1"``.
    In ``"sci"`` and ``"eng"`` notation both numbers share one exponent, taken from
    whichever of the two has the larger magnitude.

    Raises the errors of ``round_uncertainty``, plus ``InvalidOptionError`` for an
    unknown ``style`` or ``notation``. Wrong option types raise ``TypeError``;
    ``pm`` must be a string.
    """
    if not isinstance(pm, str):
        raise TypeError("pm must be a str")
    _check_style(style)
    notation = check_notation(notation)
    number, spread = round_uncertainty(
        value,
        uncertainty,
        figures,
        rounding=rounding,
        uncertainty_rounding=uncertainty_rounding,
    )
    larger = number if not number.is_zero() and number.adjusted() > spread.adjusted() else spread
    power = power_for(larger, notation)
    number, spread = shift(number, power), shift(spread, power)
    marker = "" if notation == "fixed" else exponent_marker(power)
    if style == "paren":
        return f"{fixed(number)}({_in_last_digits(number, spread)}){marker}"
    body = f"{fixed(number)} {pm} {fixed(spread)}"
    return f"({body}){marker}" if marker else body
