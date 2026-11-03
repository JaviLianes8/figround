"""Write CLI results and handle closed output pipes across platforms."""

from __future__ import annotations

import errno
import io
import os
import sys
from collections.abc import Sequence


def write_lines(lines: Sequence[str]) -> int:
    try:
        for line in lines:
            print(line)
        sys.stdout.flush()
    except OSError as error:
        if not isinstance(error, BrokenPipeError) and not (
            os.name == "nt" and error.errno == errno.EINVAL
        ):
            raise
        # Shutdown must not retry flushing the failed output stream.
        sys.stdout = io.StringIO()
        return 1
    return 0
