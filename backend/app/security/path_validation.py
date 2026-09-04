"""Path validation for modpack analysis."""

from __future__ import annotations

from pathlib import Path


class PathValidationError(ValueError):
    """Raised when a user-supplied path is invalid for analysis."""


def validate_modpack_path(raw: str) -> Path:
    """Validate that *raw* is an absolute existing directory.

    Analysis is read-only. We never follow into symlink escapes for writes
    (repairs are separate and require confirm + backup).
    """
    if not raw or not str(raw).strip():
        raise PathValidationError("Path must not be empty.")

    path = Path(raw.strip())

    if not path.is_absolute():
        raise PathValidationError(
            f"Path must be absolute (got relative: {raw!r}). "
            "Example: C:\\\\Games\\\\MyModpack"
        )

    try:
        resolved = path.resolve(strict=False)
    except OSError as exc:
        raise PathValidationError(f"Cannot resolve path: {exc}") from exc

    if not resolved.exists():
        raise PathValidationError(f"Path does not exist: {resolved}")

    if not resolved.is_dir():
        raise PathValidationError(f"Path is not a directory: {resolved}")

    return resolved
