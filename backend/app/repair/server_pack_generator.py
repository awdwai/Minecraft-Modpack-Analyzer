"""Server pack generator stub — Phase 6. Never mutates source pack."""

from __future__ import annotations

from typing import Any


def preview_server_pack(_analysis_id: str) -> dict[str, Any]:
    return {
        "implemented": False,
        "message": "Server pack generator not implemented (Phase 6).",
        "note": "When implemented, this will copy-out excluding client-only mods.",
    }
