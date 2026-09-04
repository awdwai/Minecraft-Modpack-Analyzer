"""Backup manager stub — real backups land under .mpa-backups/ in Phase 6."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class BackupManager:
    def __init__(self, root: Path):
        self.root = root
        self.backup_root = root / ".mpa-backups"

    def preview(self) -> dict[str, Any]:
        return {
            "implemented": False,
            "backup_root": str(self.backup_root),
            "message": "Backups are not implemented yet (Phase 6).",
        }
