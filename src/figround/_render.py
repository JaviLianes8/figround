"""Turn rounded Decimals into text without losing significant trailing zeros."""

from __future__ import annotations

from decimal import Decimal

from ._errors import InvalidNumberError

FIXED_LIMIT = 10_000
"""Most zeros ``fixed`` will write around the digits; beyond it use scientific notation."""


def _parts(value: Decimal) -> tuple[int, str, int]:
    sign, digits, exponent = value.as_tuple()
    assert isinstance(exponent, int)
    return sign, "".join(str(d) for d in digits), exponent


def fixed(value: Decimal, *, trailing_point: bool = False) -> str:
    """Write a finite Decimal positionally, keeping every coefficient digit.

    ``Decimal("1.2E+3")`` becomes ``"1200"``, ``Decimal("0.0120")`` becomes ``"0.0120"``.
    A zero never carries a minus sign. With ``trailing_point`` a whole number whose
    last digit is a significant zero gets a final ``"."`` (``"1000."``).
    """
    sign, text, exponent = _parts(value)
    if exponent > FIXED_LIMIT or -exponent - len(text) > FIXED_LIMIT:
        raise InvalidNumberError("too many zeros for fixed notation; use 'sci'")
    if exponent >= 0:
        body = text + "0" * exponent
        if trailing_point and exponent == 0 and body.endswith("0") and not value.is_zero():
            body += "."
    else:
        point = len(text) + exponent
        body = "0." + "0" * -point + text if point <= 0 else text[:point] + "." + text[point:]
    return "-" + body if sign and not value.is_zero() else body


def shift(value: Decimal, power: int) -> Decimal:
    """Divide by ``10**power`` exactly, keeping the coefficient digits untouched."""
    sign, digits, exponent = value.as_tuple()
    assert isinstance(exponent, int)
    return Decimal((sign, digits, exponent - power))


def exponent_marker(power: int) -> str:
    """Write a power of ten as ``e+03`` or ``e-04``: sign always, at least two digits."""
    return f"e{'+' if power >= 0 else '-'}{abs(power):02d}"


def power_for(value: Decimal, notation: str) -> int:
    """The exponent a notation puts on ``value``: 0 for fixed or zero, else by magnitude."""
    if notation == "fixed" or value.is_zero():
        return 0
    adjusted = value.adjusted()
    return adjusted if notation == "sci" else adjusted // 3 * 3
