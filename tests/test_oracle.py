"""Seeded cross-checks against the standard library.

Oracles: ``Decimal.quantize`` in each rounding mode, ``format(Decimal, ".{n-1}e")`` and
``format(x, ".{n}g")``. Known, documented differences (GUIDE.md):

* ``'g'`` drops insignificant trailing zeros and switches to scientific notation by
  magnitude; figround keeps the zeros and lets the caller pick the notation, so the
  comparison is by numeric value.
* For a float, ``'g'`` rounds the exact binary value while figround rounds ``repr(x)``.
  They differ only when the two decimals fall on different sides of a rounding
  boundary; the test checks that every disagreement is such a case.
"""

import decimal
import random
from decimal import Decimal, localcontext

from figround import ROUNDING_MODES, format_sig, round_decimal

SEED = 20261012
COUNT = 3000


def _random_decimal(rng: random.Random) -> Decimal:
    digits = "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 12)))
    sign = rng.choice(["", "-"])
    return Decimal(f"{sign}{digits}E{rng.randint(-30, 30)}")


def _quantize_oracle(value: Decimal, figures: int, mode: str) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 100
        quantum = Decimal(1).scaleb(value.adjusted() - figures + 1)
        return value.quantize(quantum, rounding=getattr(decimal, "ROUND_" + mode.upper()))


def test_matches_decimal_quantize_in_every_mode() -> None:
    rng = random.Random(SEED)
    for _ in range(COUNT):
        value = _random_decimal(rng)
        if value.is_zero():
            continue
        figures = rng.randint(1, 10)
        mode = rng.choice(ROUNDING_MODES)
        ours = round_decimal(value, figures, rounding=mode)  # type: ignore[arg-type]
        assert ours == _quantize_oracle(value, figures, mode), (value, figures, mode)
        assert len(ours.as_tuple().digits) == figures


def _normal_exponent(text: str) -> str:
    mantissa, exponent = text.split("e")
    power = int(exponent)
    return f"{mantissa}e{'+' if power >= 0 else '-'}{abs(power):02d}"


def test_scientific_matches_decimal_e_format() -> None:
    rng = random.Random(SEED + 1)
    for _ in range(COUNT):
        value = _random_decimal(rng)
        if value.is_zero():
            continue
        figures = rng.randint(1, 10)
        expected = _normal_exponent(format(value, f".{figures - 1}e"))
        assert format_sig(value, figures, notation="sci") == expected, (value, figures)


def test_value_matches_g_format_for_decimals() -> None:
    rng = random.Random(SEED + 2)
    for _ in range(COUNT):
        value = _random_decimal(rng)
        figures = rng.randint(1, 10)
        oracle = Decimal(format(value, f".{figures}g"))
        assert Decimal(format_sig(value, figures)) == oracle, (value, figures)


def test_float_g_format_differs_only_on_binary_boundaries() -> None:
    rng = random.Random(SEED + 3)
    differences = 0
    for _ in range(COUNT):
        x = round(rng.uniform(-1000, 1000), rng.randint(0, 6))
        figures = rng.randint(1, 8)
        if x == 0:
            continue
        ours = Decimal(format_sig(x, figures))
        theirs = Decimal(format(x, f".{figures}g"))
        if ours != theirs:
            differences += 1
            # The exact binary value rounds to what 'g' printed.
            assert round_decimal(Decimal(x), figures) == theirs, (x, figures)
    assert differences > 0  # the sample does exercise the documented difference
    assert format(2.675, ".3g") == "2.67"
    assert format_sig(2.675, 3) == "2.68"
