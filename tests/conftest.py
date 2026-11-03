from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

MANIFEST = Path(__file__).resolve().parent / "upstream" / "MANIFEST.json"
UPSTREAM = Path(os.environ.get("FIGROUND_UPSTREAM_DIR", str(MANIFEST.parent)))


def upstream_path(name: str) -> Path:
    """Return the path of a third-party test file, checked against tests/upstream/MANIFEST.json.

    The files are not committed: `python scripts/fetch_upstream.py` fetches them. Their
    tests skip while a file is absent and fail if it differs from the manifest.
    """
    path = UPSTREAM / name
    if not path.is_file():
        pytest.skip(f"{name} is not fetched; run python scripts/fetch_upstream.py")
    entry = json.loads(MANIFEST.read_text(encoding="utf-8"))[name]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == entry["sha256"], f"{name} differs from MANIFEST"
    return path
