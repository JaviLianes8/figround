"""Stable public types, signatures, defaults and runnable documentation."""

from __future__ import annotations

import ast
import inspect
import pickle
import re
from decimal import Decimal
from pathlib import Path
from typing import get_args, get_type_hints

import pytest

import figround


def test_no_unlisted_public_names() -> None:
    assert {name for name in vars(figround) if not name.startswith("_")} == set(figround.__all__)
    assert figround.__version__ == "1.0.0"


def test_option_tuples_and_type_aliases() -> None:
    assert figround.ROUNDING_MODES == (
        "half_even",
        "half_up",
        "half_down",
        "up",
        "down",
        "ceiling",
        "floor",
        "05up",
    )
    assert figround.NOTATIONS == ("fixed", "sci", "eng")
    assert figround.STYLES == ("paren", "pm")
    assert get_args(figround.Rounding) == figround.ROUNDING_MODES
    assert get_args(figround.Notation) == figround.NOTATIONS
    assert get_args(figround.Style) == figround.STYLES
    assert set(get_args(figround.Number)) == {int, float, str, Decimal}


@pytest.mark.parametrize(
    ("name", "parameters", "defaults"),
    [
        ("count_sig", "text strict", {"strict": False}),
        ("sig_bounds", "text", {}),
        ("round_decimal", "x figures rounding", {"rounding": "half_even"}),
        ("round_sig", "x figures rounding", {"rounding": "half_even"}),
        (
            "format_sig",
            "x figures sci notation rounding trailing_point",
            {"sci": False, "notation": None, "rounding": "half_even", "trailing_point": False},
        ),
        (
            "round_uncertainty",
            "value uncertainty figures rounding uncertainty_rounding",
            {"figures": 2, "rounding": "half_even", "uncertainty_rounding": None},
        ),
        (
            "format_uncertainty",
            "value uncertainty figures style notation rounding uncertainty_rounding pm",
            {
                "figures": 2,
                "style": "paren",
                "notation": "fixed",
                "rounding": "half_even",
                "uncertainty_rounding": None,
                "pm": "+/-",
            },
        ),
    ],
)
def test_signatures_and_defaults(name: str, parameters: str, defaults: dict[str, object]) -> None:
    function = getattr(figround, name)
    signature = inspect.signature(function)
    assert list(signature.parameters) == parameters.split()
    assert {
        p.name: p.default for p in signature.parameters.values() if p.default is not p.empty
    } == defaults
    for p in signature.parameters.values():
        expected_kind = (
            p.KEYWORD_ONLY
            if p.name in defaults and p.name != "figures"
            else p.POSITIONAL_OR_KEYWORD
        )
        assert p.kind == expected_kind
    assert set(get_type_hints(function)) == set(parameters.split()) | {"return"}
    assert ">>>" in function.__doc__


def test_exception_examples_and_serialization() -> None:
    for name in figround.__all__:
        if not name.endswith("Error"):
            continue
        cls = getattr(figround, name)
        assert ">>>" in cls.__doc__
        error = cls("invalid input")
        restored = pickle.loads(pickle.dumps(error))
        assert type(restored) is cls
        assert restored.args == ("invalid input",)
        assert isinstance(restored, figround.FigroundError)


@pytest.mark.parametrize("filename", ["README.md", "GUIDE.md"])
def test_documentation_python_blocks(filename: str) -> None:
    text = (Path(__file__).resolve().parents[1] / filename).read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    assert blocks
    for block in blocks:
        namespace: dict[str, object] = {"Decimal": Decimal}
        exec(compile(block, filename, "exec"), namespace)
        for node in ast.parse(block).body:
            if not isinstance(node, ast.Expr) or node.end_lineno != node.lineno:
                continue
            line = block.splitlines()[node.lineno - 1]
            if "#" not in line:
                continue
            expected = line.split("#", 1)[1].strip()
            try:
                parsed = ast.parse(expected, mode="eval")
            except SyntaxError:
                continue
            actual = eval(compile(ast.Expression(node.value), filename, "eval"), namespace)
            assert actual == eval(compile(parsed, filename, "eval"), namespace)
