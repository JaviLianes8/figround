"""Rounding modes at precision 5, by hand and against the General Decimal Arithmetic tests.

The hand-written table runs always. The decTest vectors come from rounding.decTest 2.62
inside https://speleotrove.com/decimal/dectest.zip, which is not committed:
`python scripts/fetch_upstream.py` fetches it as pinned in tests/upstream/MANIFEST.json,
and those tests skip until then. Each line "id add a b -> r" at precision 5 gives
r = round(a + b, 5 digits, mode); the decTest mode names are the names figround uses.
"""

from __future__ import annotations

import zipfile
from decimal import Decimal, localcontext

import pytest
from conftest import upstream_path

from figround import format_sig, round_decimal

MODES = ("down", "half_down", "half_even", "half_up", "up", "floor", "ceiling", "05up")
INPUTS = ("12345.5", "12344.5", "-12345.5", "12345.1", "12340.1", "12345.01")

# Hand-written from the rounding definitions in the General Decimal Arithmetic
# specification (https://speleotrove.com/decimal/damodel.html), one row per mode.
HAND = {
    "down": ("12345", "12344", "-12345", "12345", "12340", "12345"),
    "half_down": ("12345", "12344", "-12345", "12345", "12340", "12345"),
    "half_even": ("12346", "12344", "-12346", "12345", "12340", "12345"),
    "half_up": ("12346", "12345", "-12346", "12345", "12340", "12345"),
    "up": ("12346", "12345", "-12346", "12346", "12341", "12346"),
    "floor": ("12345", "12344", "-12346", "12345", "12340", "12345"),
    "ceiling": ("12346", "12345", "-12345", "12346", "12341", "12346"),
    "05up": ("12346", "12344", "-12346", "12346", "12341", "12346"),
}


@pytest.mark.parametrize("mode", MODES)
def test_hand_written_rounding(mode: str) -> None:
    for value, expected in zip(INPUTS, HAND[mode], strict=True):
        assert round_decimal(Decimal(value), 5, rounding=mode) == Decimal(expected)  # type: ignore[arg-type]
        assert format_sig(value, 5, rounding=mode) == expected  # type: ignore[arg-type]


def _dectest_cases() -> list[tuple[str, str, str, str, str]]:
    with zipfile.ZipFile(upstream_path("dectest.zip")) as archive:
        text = archive.read("rounding.decTest").decode("ascii")
    cases = []
    mode = ""
    for raw in text.splitlines():
        line = raw.split("--", 1)[0].strip()
        if line.lower().startswith("rounding:"):
            mode = line.split(":", 1)[1].strip()
        # rzex and r0ze test the sign of a zero result, which figround does not promise.
        elif " add " in line and not line.startswith(("rzex", "r0ze")):
            ident, _, left, right, _, result, *_ = line.split()
            cases.append((ident, mode, left, right, result))
    return cases


@pytest.fixture(scope="module")
def dectest() -> list[tuple[str, str, str, str, str]]:
    return _dectest_cases()


def test_the_dectest_add_blocks_cover_every_mode(dectest: list[tuple[str, ...]]) -> None:
    assert len(dectest) == 482
    assert {mode for _, mode, *_ in dectest} == set(MODES)


def test_dectest_rounding(dectest: list[tuple[str, str, str, str, str]]) -> None:
    for ident, mode, left, right, result in dectest:
        with localcontext() as ctx:
            ctx.prec = 50
            exact = Decimal(left) + Decimal(right)
        rounded = round_decimal(exact, 5, rounding=mode)  # type: ignore[arg-type]
        assert rounded == Decimal(result), ident
        assert format_sig(exact, 5, rounding=mode) == result, ident  # type: ignore[arg-type]
