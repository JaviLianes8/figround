"""Validation of boolean options."""

from __future__ import annotations


def check_bool(value: bool, name: str) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a bool")
