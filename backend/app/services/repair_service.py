"""Repair service — stub for Phase 6. Never mutates without confirm + backup."""

from __future__ import annotations

from typing import Any


def preview_duplicate_repair(_analysis_id: str) -> dict[str, Any]:
    return {
        "implemented": False,
        "message": "Duplicate repair is not implemented yet (Phase 6).",
        "preview": None,
        "requires_confirm": True,
    }


def apply_duplicate_repair(_analysis_id: str, *, confirm: bool = False) -> dict[str, Any]:
    return {
        "implemented": False,
        "message": "Duplicate repair is not implemented yet (Phase 6).",
        "applied": False,
        "confirm_received": confirm,
    }


def preview_server_pack(_analysis_id: str) -> dict[str, Any]:
    return {
        "implemented": False,
        "message": "Server pack generation is not implemented yet (Phase 6). Preview-only stub.",
        "would_exclude_client_only": True,
        "preview": None,
    }
