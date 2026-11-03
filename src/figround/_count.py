"""Count the significant figures a written number claims."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import cast

from ._errors import AmbiguousFiguresError, InvalidNumberError
from ._validation import check_bool, is_kind

_NUMBER = re.compile(r"[+-]?(?P<int>[0-9]*)(?:(?P<point>\.)(?P<frac>[0-9]*))?(?:[eE][+-]?[0-9]+)?")


def _decimal_bounds(value: Decimal) -> tuple[int, int]:
    if not value.is_finite():
        raise InvalidNumberError("not a finite number")
    _sign, digits, exponent = value.as_tuple()
    assert isinstance(exponent, int)
    count = 1 + max(0, -exponent) if value.is_zero() else len(digits)
    return count, count


def sig_bounds(text: str | Decimal) -> tuple[int, int]:
    """Return the fewest and most significant figures ``text`` can be read as.

    >>> sig_bounds("0.00120")
    (3, 3)
    >>> sig_bounds("1200")
    (2, 4)
    >>> sig_bounds("1200.")
    (4, 4)
    >>> sig_bounds("1.20e3")
    (3, 3)

    Rules: leading zeros never count. With a decimal point every digit from the first
    nonzero one counts, trailing zeros included. Without a point, trailing zeros of a
    whole number are ambiguous, so the bounds differ. An exponent never changes the count.
    A zero counts ``1`` plus its decimal places (``"0"`` is 1, ``"0.00"`` is 3), the
    convention ``format_sig`` writes. A ``Decimal`` is exact: every coefficient digit
    counts, so ``Decimal("1200")`` is 4 and ``Decimal("1.2E+3")`` is 2. Subclasses are
    read as their stored base value.

    Raises:
        TypeError: ``text`` is not a ``str`` or ``Decimal`` (an int or float cannot
            record trailing zeros).
        InvalidNumberError: ``text`` is not a plain finite decimal number.
    """
    if is_kind(text, Decimal):
        return _decimal_bounds(Decimal(text))
    if not is_kind(text, str):
        raise TypeError("expected str or Decimal")
    match = _NUMBER.fullmatch(str.strip(cast(str, text)))
    if match is None or not (match["int"] or match["frac"]):
        raise InvalidNumberError("not a number")
    whole, frac = match["int"], match["frac"] or ""
    significant = (whole + frac).lstrip("0")
    if not significant:
        count = 1 + len(frac)
        return count, count
    if match["point"]:
        return len(significant), len(significant)
    return len(significant.rstrip("0")), len(significant)


def count_sig(text: str | Decimal, *, strict: bool = False) -> int:
    """Count the significant figures in a written number.

    >>> count_sig("0.0450")
    3
    >>> count_sig("6.022e23")
    4
    >>> count_sig("1200")
    2

    Ambiguous trailing zeros (``"1200"``) count as not significant, the conservative
    reading; pass ``strict=True`` to raise ``AmbiguousFiguresError`` instead, or call
    ``sig_bounds`` for both readings. The rules are those of ``sig_bounds``.
    """
    check_bool(strict, "strict")
    low, high = sig_bounds(text)
    if strict and low != high:
        raise AmbiguousFiguresError(
            f"ambiguous count: {low} to {high} significant figures; "
            "add a decimal point or use scientific notation"
        )
    return low
