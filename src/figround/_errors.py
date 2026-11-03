"""Exception types. Every error a caller can fix is a ``FigroundError``, itself a ``ValueError``."""

from __future__ import annotations


class FigroundError(ValueError):
    """Base class for every value error raised by figround.

    It subclasses ``ValueError`` so code written against 0.1.0, which raised plain
    ``ValueError``, keeps catching everything.

    >>> isinstance(FigroundError("invalid input"), ValueError)
    True
    """


class InvalidNumberError(FigroundError):
    """The input is invalid, nonfinite, outside the decimal range or too wide to render.

    >>> isinstance(InvalidNumberError("invalid input"), ValueError)
    True
    """


class InvalidFiguresError(FigroundError):
    """The requested count of significant figures is outside 1 to 10000.

    >>> isinstance(InvalidFiguresError("invalid input"), ValueError)
    True
    """


class InvalidOptionError(FigroundError):
    """An option such as ``rounding``, ``notation`` or ``style`` has an unknown value.

    >>> isinstance(InvalidOptionError("invalid input"), ValueError)
    True
    """


class AmbiguousFiguresError(FigroundError):
    """A strict count met trailing zeros that may or may not be significant (``"1200"``).

    >>> isinstance(AmbiguousFiguresError("invalid input"), ValueError)
    True
    """


class UncertaintyError(FigroundError):
    """The uncertainty is nonpositive or requires more than 100000 value digits.

    >>> isinstance(UncertaintyError("invalid input"), ValueError)
    True
    """
