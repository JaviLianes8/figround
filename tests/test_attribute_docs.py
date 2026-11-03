"""Run the attribute docstrings attached to public aliases and constants."""

from __future__ import annotations

import ast
import doctest
import importlib
import inspect

import pytest


@pytest.mark.parametrize(
    ("module_name", "names"),
    [
        ("figround", {"__version__"}),
        ("figround._modes", {"Rounding", "Notation", "ROUNDING_MODES", "NOTATIONS"}),
        ("figround._round", {"Number"}),
        ("figround._uncertainty", {"Style", "STYLES"}),
    ],
)
def test_attribute_docstrings(module_name: str, names: set[str]) -> None:
    module = importlib.import_module(module_name)
    tree = ast.parse(inspect.getsource(module))
    found = set()
    for assignment, following in zip(tree.body, tree.body[1:], strict=False):
        if isinstance(assignment, ast.Assign):
            target = assignment.targets[0]
        elif isinstance(assignment, ast.AnnAssign):
            target = assignment.target
        else:
            continue
        if not isinstance(target, ast.Name) or target.id not in names:
            continue
        assert isinstance(following, ast.Expr)
        assert isinstance(following.value, ast.Constant)
        text = following.value.value
        assert isinstance(text, str) and ">>>" in text
        example = doctest.DocTestParser().get_doctest(text, vars(module), target.id, "", 0)
        result = doctest.DocTestRunner().run(example)
        assert result.failed == 0 and result.attempted > 0
        found.add(target.id)
    assert found == names
