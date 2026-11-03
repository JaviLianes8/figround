"""Command-line diagnostics without reflecting user input."""

from __future__ import annotations

import argparse
import sys
from typing import NoReturn


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: invalid arguments; use --help\n")
