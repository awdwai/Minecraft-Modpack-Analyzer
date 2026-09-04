"""Scan a modpack folder for JARs and notable structure."""

from __future__ import annotations

from pathlib import Path

from app.models.analysis_result import ModpackInventory


def scan_modpack(root: Path) -> ModpackInventory:
    """List what is in the pack without interpreting mods yet."""
    mods_dir = _find_mods_dir(root)
    config_dir = root / "config"
    logs_dir = _find_logs_dir(root)

    jar_files: list[str] = []
    if mods_dir and mods_dir.is_dir():
        for path in sorted(mods_dir.rglob("*.jar")):
            if path.is_file():
                jar_files.append(str(path))

    # Also catch JARs directly under root/mods-like layouts already handled;
    # if no mods folder, look one level deep for *.jar as a last resort.
    if not jar_files:
        for path in sorted(root.glob("*.jar")):
            if path.is_file():
                jar_files.append(str(path))

    config_files: list[str] = []
    has_config = config_dir.is_dir()
    if has_config:
        for path in sorted(config_dir.rglob("*")):
            if path.is_file():
                config_files.append(str(path.relative_to(root)))
                if len(config_files) >= 500:
                    break

    log_files: list[str] = []
    has_logs = bool(logs_dir and logs_dir.is_dir())
    if has_logs and logs_dir:
        for path in sorted(logs_dir.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".log", ".txt", ".gz"}:
                log_files.append(str(path.relative_to(root)))
                if len(log_files) >= 100:
                    break

    other_notable: list[str] = []
    for name in ("manifest.json", "modlist.html", "minecraftinstance.json", "instance.cfg"):
        candidate = root / name
        if candidate.is_file():
            other_notable.append(name)

    return ModpackInventory(
        path=str(root),
        pack_name=root.name,
        jar_files=jar_files,
        config_files=config_files,
        log_files=log_files,
        has_mods_folder=mods_dir is not None and mods_dir.is_dir(),
        has_config_folder=has_config,
        has_logs_folder=has_logs,
        other_notable=other_notable,
    )


def _find_mods_dir(root: Path) -> Path | None:
    direct = root / "mods"
    if direct.is_dir():
        return direct
    # Some launchers nest: .minecraft/mods
    nested = root / ".minecraft" / "mods"
    if nested.is_dir():
        return nested
    return None


def _find_logs_dir(root: Path) -> Path | None:
    for candidate in (root / "logs", root / "crash-reports", root / ".minecraft" / "logs"):
        if candidate.is_dir():
            return candidate
    return None
