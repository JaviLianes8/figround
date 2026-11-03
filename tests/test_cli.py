"""The ``figround`` command, driven in-process. The installed script is checked by the e2e."""

import pytest

from figround._cli import main


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    status = main(list(argv))
    out, err = capsys.readouterr()
    return status, out, err


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["round", "2.675", "3"], "2.68\n"),
        (["round", "123456", "2", "--notation", "sci"], "1.2e+05\n"),
        (["round", "1.2", "3"], "1.20\n"),
        (["round", "2.5", "1", "--rounding", "half_up"], "3\n"),
        (["round", "123456", "4", "--notation", "eng"], "123.5e+03\n"),
        (["round", "1000", "4", "--trailing-point"], "1000.\n"),
        (["round", "--", "-0.0125", "2"], "-0.012\n"),
        (["count", "0.00120", "1200", "1200."], "3\n2\n4\n"),
        (["count", "1200", "--bounds"], "2 4\n"),
        (["format", "100.02147", "-u", "0.00035"], "100.02147(35)\n"),
        (["format", "100.02147", "-u", "0.00035", "--style", "pm"], "100.02147 +/- 0.00035\n"),
        (["format", "10.05762", "-u", "0.027"], "10.058(27)\n"),
        (["format", "1", "-u", "10.47", "--uncertainty-rounding", "up"], "1(11)\n"),
        (["format", "1234.5", "--figures", "3", "--notation", "sci"], "1.23e+03\n"),
        (["format", "1.23456", "-u", "0.0123", "--figures", "1"], "1.23(1)\n"),
    ],
)
def test_commands(capsys: pytest.CaptureFixture[str], argv: list[str], expected: str) -> None:
    assert run(capsys, *argv) == (0, expected, "")


@pytest.mark.parametrize(
    "argv",
    [
        ["count", "1200", "--strict"],
        ["round", "abc", "2"],
        ["round", "1", "0"],
        ["format", "1", "-u", "0"],
        ["round", "1e999999999999999999", "3"],
        ["round", "1", "99999999999999999999"],
        ["count", "1200", "abc"],
    ],
)
def test_bad_input_exits_1_with_message(
    capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    status, out, err = run(capsys, *argv)
    assert (status, out) == (1, "")
    assert err.startswith("figround: error: ")


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["format", "1"],
        ["round", "1", "x"],
        ["round", "1", "2", "--rounding", "nearest"],
        ["count", "1", "--strict", "--bounds"],
        ["format", "1", "--figures", "2", "--style", "pm"],
        ["format", "1", "--figures", "2", "--uncertainty-rounding", "up"],
    ],
)
def test_bad_usage_exits_2(capsys: pytest.CaptureFixture[str], argv: list[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        main(argv)
    assert stop.value.code == 2
    assert "usage: figround" in capsys.readouterr().err


@pytest.mark.parametrize("command", [[], ["round"], ["count"], ["format"]])
def test_help_has_examples(capsys: pytest.CaptureFixture[str], command: list[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        main([*command, "--help"])
    assert stop.value.code == 0
    out = capsys.readouterr().out
    assert "examples:" in out
    assert "figround " in out
