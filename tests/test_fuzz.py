"""Seeded generated cases; integer arithmetic is independent of Decimal rounding."""

from __future__ import annotations

import random
from decimal import Decimal
from typing import cast

from figround import (
    ROUNDING_MODES,
    InvalidNumberError,
    Rounding,
    count_sig,
    format_sig,
    round_decimal,
    sig_bounds,
)


def test_integer_oracle_for_all_rounding_directions() -> None:
    rng = random.Random(20261103)
    for _ in range(3000):
        coefficient = rng.randint(10, 10**15)
        sign = rng.choice([-1, 1])
        figures = rng.randint(1, len(str(coefficient)) - 1)
        exponent = rng.randint(-50, 50)
        power = len(str(coefficient)) - figures
        divisor = 10**power
        whole, remainder = divmod(coefficient, divisor)
        for mode in ROUNDING_MODES:
            increment = {
                "down": False,
                "up": remainder > 0,
                "floor": sign < 0 and remainder > 0,
                "ceiling": sign > 0 and remainder > 0,
                "half_up": 2 * remainder >= divisor,
                "half_down": 2 * remainder > divisor,
                "half_even": 2 * remainder > divisor
                or (2 * remainder == divisor and whole % 2 == 1),
                "05up": remainder > 0 and whole % 10 in (0, 5),
            }[mode]
            expected = Decimal(f"{sign * (whole + increment)}e{exponent + power}")
            value = Decimal(f"{sign * coefficient}e{exponent}")
            actual = round_decimal(value, figures, rounding=cast(Rounding, mode))
            assert actual == expected, (value, figures, mode)
            assert len(actual.as_tuple().digits) == figures


def test_seeded_ascii_and_unicode_parser_inputs() -> None:
    rng = random.Random(20261104)
    alphabet = "0123456789eE+-. _\n\t\x00secret" + "\u0661\uff12\ud800"
    for _ in range(5000):
        text = "".join(rng.choices(alphabet, k=rng.randrange(100)))
        try:
            low, high = sig_bounds(text)
        except InvalidNumberError:
            pass
        else:
            assert 1 <= low <= high
            assert count_sig(text) == low
        try:
            output = format_sig(text, 4, notation="sci")
        except InvalidNumberError:
            continue
        assert count_sig(output) == 4


def test_long_inputs_and_exponents_are_bounded_or_linear() -> None:
    for length in (1000, 10000, 100000):
        assert sig_bounds("1" * length) == (length, length)
        assert format_sig("1" * length, 3, notation="sci") == f"1.11e+{length - 1:02d}"
        for text in ("1" * length + "!", "1e" + "+" * length, "." * length):
            try:
                sig_bounds(text)
            except InvalidNumberError as error:
                assert len(str(error)) < 100
            else:
                raise AssertionError("malformed input accepted")
