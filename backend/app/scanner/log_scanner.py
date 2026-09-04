"""Log / crash-report file discovery (read-only)."""

from __future__ import annotations

from pathlib import Path


def list_log_files(root: Path, limit: int = 100) -> list[str]:
    results: list[str] = []
    for folder_name in ("logs", "crash-reports"):
        folder = root / folder_name
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                results.append(str(path.relative_to(root)))
                if len(results) >= limit:
                    return results
    return results
