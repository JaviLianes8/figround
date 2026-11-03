import importlib.resources

import figround

# The public API. Add every exported name here as the library grows; this list is the
# contract and the test below fails if the module and this list disagree.
PUBLIC_API: list[str] = [
    "NOTATIONS",
    "ROUNDING_MODES",
    "STYLES",
    "AmbiguousFiguresError",
    "InvalidFiguresError",
    "InvalidNumberError",
    "InvalidOptionError",
    "Notation",
    "Number",
    "Rounding",
    "FigroundError",
    "Style",
    "UncertaintyError",
    "count_sig",
    "format_sig",
    "format_uncertainty",
    "round_decimal",
    "round_sig",
    "round_uncertainty",
    "sig_bounds",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(figround.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in figround.__all__:
        assert hasattr(figround, name)


def test_version_is_a_three_part_string() -> None:
    parts = figround.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("figround").joinpath("py.typed").is_file()
