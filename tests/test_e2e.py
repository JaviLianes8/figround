"""Optional built-artifact checks: set FIGROUND_WHEEL and FIGROUND_SDIST."""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

import pytest

CONSUMER = """
from decimal import Decimal
from importlib.metadata import version
from pathlib import Path
import figround
from figround import (
    count_sig, format_sig, format_uncertainty, round_decimal, round_sig,
    round_uncertainty, sig_bounds,
)
assert version("figround") == figround.__version__ == "1.0.0"
assert "site-packages" in str(Path(figround.__file__).resolve())
assert count_sig("0.00120") == 3
assert sig_bounds("1200") == (2, 4)
assert round_sig(2.675, 3) == 2.68
assert str(round_decimal("1.2", 3)) == "1.20"
assert format_sig("123456", 4, notation="eng") == "123.5e+03"
assert round_uncertainty("10.05762", "0.027") == (Decimal("10.058"), Decimal("0.027"))
assert format_uncertainty("100.02147", "0.00035") == "100.02147(35)"
try:
    count_sig("1200", strict=True)
except figround.AmbiguousFiguresError:
    pass
else:
    raise AssertionError("strict count did not reject ambiguity")
print("consumer passed")
"""


def _artifact(variable: str) -> Path:
    path = os.environ.get(variable)
    if not path:
        pytest.skip(f"set {variable} to a built artifact")
    result = Path(path).resolve()
    assert result.is_file()
    return result


def _run(command: list[str], folder: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["TMP"] = env["TEMP"] = str(folder)
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return subprocess.run(command, cwd=folder, env=env, capture_output=True, text=True, timeout=180)


def test_wheel_metadata_and_contents() -> None:
    with zipfile.ZipFile(_artifact("FIGROUND_WHEEL")) as archive:
        names = archive.namelist()
        assert "figround/py.typed" in names
        assert "figround-1.0.0.dist-info/licenses/LICENSE" in names
        assert all(name.startswith(("figround/", "figround-1.0.0.dist-info/")) for name in names)
        assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)
        metadata = BytesParser().parsebytes(archive.read("figround-1.0.0.dist-info/METADATA"))
        assert metadata["Name"] == "figround"
        assert metadata["Version"] == "1.0.0"
        assert metadata["Requires-Python"] == ">=3.10"
        assert metadata["License-Expression"] == "MIT"
        assert {
            "Source, https://github.com/JaviLianes8/sigfigs",
            "Issues, https://github.com/JaviLianes8/sigfigs/issues",
            "Changelog, https://github.com/JaviLianes8/sigfigs/blob/main/CHANGELOG.md",
        } <= set(metadata.get_all("Project-URL", []))
        assert "Development Status :: 5 - Production/Stable" in metadata.get_all("Classifier", [])
        assert all("extra == 'dev'" in value for value in metadata.get_all("Requires-Dist", []))
        entries = archive.read("figround-1.0.0.dist-info/entry_points.txt").decode()
        assert "figround = figround._cli:main" in entries


def test_sdist_contents() -> None:
    with tarfile.open(_artifact("FIGROUND_SDIST")) as archive:
        names = [member.name.split("/", 1)[1] for member in archive.getmembers() if member.isfile()]
        assert {"LICENSE", "README.md", "GUIDE.md", "CHANGELOG.md", "pyproject.toml"} <= set(names)
        assert "src/figround/py.typed" in names
        assert "tests/upstream/MANIFEST.json" in names
        assert "scripts/check.ps1" in names
        assert not any(name.endswith((".zip", ".pdf", ".pyc")) for name in names)
        assert not any("__pycache__" in name or "CERT-" in name for name in names)
        assert all(
            name.startswith(("src/figround/", "tests/"))
            or name
            in {
                "LICENSE",
                "README.md",
                "GUIDE.md",
                "CHANGELOG.md",
                "pyproject.toml",
                "PKG-INFO",
                ".gitignore",
                "scripts/fetch_upstream.py",
                "scripts/check.ps1",
            }
            for name in names
        )


def test_installed_wheel_consumer_and_cli(tmp_path: Path) -> None:
    wheel = _artifact("FIGROUND_WHEEL")
    envdir = tmp_path / "env"
    result = _run([sys.executable, "-m", "venv", str(envdir)], tmp_path)
    assert result.returncode == 0, result.stderr
    scripts = envdir / ("Scripts" if os.name == "nt" else "bin")
    python = str(scripts / ("python.exe" if os.name == "nt" else "python"))
    command = str(scripts / ("figround.exe" if os.name == "nt" else "figround"))
    result = _run([python, "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)], tmp_path)
    assert result.returncode == 0, result.stderr
    result = _run([python, "-I", "-c", CONSUMER], tmp_path)
    assert (result.returncode, result.stdout.strip(), result.stderr) == (0, "consumer passed", "")
    for prefix in ([command], [python, "-I", "-m", "figround"]):
        for arguments, expected in [
            (["round", "2.675", "3"], "2.68\n"),
            (["count", "0.00120", "1200", "1200."], "3\n2\n4\n"),
            (["count", "1200", "--bounds"], "2 4\n"),
            (["format", "100.02147", "-u", "0.00035"], "100.02147(35)\n"),
            (["round", "--", "-0.0125", "2"], "-0.012\n"),
        ]:
            result = _run([*prefix, *arguments], tmp_path)
            assert (result.returncode, result.stdout, result.stderr) == (0, expected, "")
        for arguments, status in [
            (["count", "1", "SECRET" * 100], 1),
            (["round", "1", "2", "--rounding", "SECRET" * 100], 2),
            (["round", "1", "SECRET" * 100], 2),
        ]:
            result = _run([*prefix, *arguments], tmp_path)
            assert (result.returncode, result.stdout) == (status, "")
            assert "SECRET" not in result.stderr
            assert len(result.stderr) < 1000
        result = _run([*prefix, "--help"], tmp_path)
        assert result.returncode == 0
        assert "examples:" in result.stdout
        with subprocess.Popen(
            [*prefix, "round", "1", "2"],
            cwd=tmp_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as process:
            assert process.stdout is not None and process.stderr is not None
            process.stdout.close()
            status = process.wait(timeout=30)
            error = process.stderr.read()
        assert (status, error) == (1, "")
