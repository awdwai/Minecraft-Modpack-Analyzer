"""Compare service — stub for Phase 5."""

from __future__ import annotations

from typing import Any


def compare_modpacks(_path_a: str, _path_b: str) -> dict[str, Any]:
    return {
        "implemented": False,
        "message": "Modpack comparison is not implemented yet (Phase 5).",
        "diff": None,
    }
