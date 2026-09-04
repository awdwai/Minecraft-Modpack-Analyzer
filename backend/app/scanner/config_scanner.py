"""Config folder scanner (read-only inventory helper)."""

from __future__ import annotations

from pathlib import Path


def list_config_files(root: Path, limit: int = 500) -> list[str]:
    config_dir = root / "config"
    if not config_dir.is_dir():
        return []
    files: list[str] = []
    for path in sorted(config_dir.rglob("*")):
        if path.is_file():
            files.append(str(path.relative_to(root)))
            if len(files) >= limit:
                break
    return files
