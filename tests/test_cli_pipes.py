"""Output failure contracts, including real process shutdown with a closed pipe."""

from __future__ import annotations

import errno
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

import figround
from figround._cli import main


def test_module_closed_output_pipe_exits_quietly() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(figround.__file__).resolve().parent.parent)
    with subprocess.Popen(
        [sys.executable, "-m", "figround", "round", "1", "2"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    ) as process:
        assert process.stdout is not None and process.stderr is not None
        process.stdout.close()
        status = process.wait(timeout=30)
        error = process.stderr.read()
    assert (status, error) == (1, "")


@pytest.mark.parametrize("operation", ["write", "flush"])
@pytest.mark.parametrize("code", [errno.EINVAL, errno.EPIPE, errno.EIO])
def test_output_error_handling_is_specific(
    monkeypatch: pytest.MonkeyPatch, operation: str, code: int
) -> None:
    class FailedOutput(io.StringIO):
        def write(self, text: str) -> int:
            if operation == "write":
                raise OSError(code, "output failed")
            return super().write(text)

        def flush(self) -> None:
            if operation == "flush":
                raise OSError(code, "output failed")

    output = FailedOutput()
    monkeypatch.setattr(sys, "stdout", output)
    if code == errno.EPIPE or (os.name == "nt" and code == errno.EINVAL):
        assert main(["round", "1", "2"]) == 1
        assert sys.stdout is not output
        sys.stdout.flush()
    else:
        with pytest.raises(OSError) as caught:
            main(["round", "1", "2"])
        assert caught.value.errno == code
