"""Type checks that read only the real type, never attributes of the supplied value."""

from __future__ import annotations

# ``isinstance`` falls back to the instance's ``__class__`` attribute, which a value can
# override or spoof; ``type()`` and ``issubclass`` on it read the real type only.


def check_bool(value: bool, name: str) -> bool:
    """Return ``value`` if it is an actual bool, else raise ``TypeError``."""
    if type(value) is not bool:
        raise TypeError(f"{name} must be a bool")
    return value


def is_kind(value: object, kind: type) -> bool:
    """Whether the real type of ``value`` is ``kind`` or a subclass of it."""
    return issubclass(type(value), kind)


def check_str(value: str, name: str) -> str:
    """Return the stored text of a str or str subclass, else raise ``TypeError``."""
    if not is_kind(value, str):
        raise TypeError(f"{name} must be a str")
    return str.__str__(value)
