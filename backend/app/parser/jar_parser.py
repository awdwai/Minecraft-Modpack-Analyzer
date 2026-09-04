"""Open a JAR as a ZIP and extract normalized Mod metadata. Never execute code."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from app.models.mod import Mod, ModEnvironment, ModLoader
from app.parser import metadata_parser


def parse_jar(path: Path | str) -> Mod:
    """Parse one JAR file into a Mod. Corrupt/unreadable → parse_ok=False."""
    jar_path = Path(path)
    file_name = jar_path.name
    file_size = jar_path.stat().st_size if jar_path.exists() else 0
    file_hash = _sha256_prefix(jar_path) if jar_path.exists() else None

    base = dict(
        mod_id=_guess_id_from_filename(file_name),
        name=file_name,
        version="unknown",
        loader=ModLoader.UNKNOWN,
        environment=ModEnvironment.UNKNOWN,
        file_path=str(jar_path),
        file_name=file_name,
        file_size=file_size,
        file_hash=file_hash,
    )

    if not jar_path.is_file():
        return Mod(**base, parse_ok=False, parse_error="File not found")

    try:
        with zipfile.ZipFile(jar_path, "r") as zf:
            names = set(zf.namelist())
            # Prefer NeoForge → Fabric → Forge mods.toml → legacy mcmod.info
            if "META-INF/neoforge.mods.toml" in names:
                raw = zf.read("META-INF/neoforge.mods.toml")
                meta = metadata_parser.parse_mods_toml(raw, neoforge=True)
            elif "fabric.mod.json" in names:
                raw = zf.read("fabric.mod.json")
                meta = metadata_parser.parse_fabric_mod_json(raw)
            elif "META-INF/mods.toml" in names:
                raw = zf.read("META-INF/mods.toml")
                meta = metadata_parser.parse_mods_toml(raw, neoforge=False)
            elif "mcmod.info" in names:
                raw = zf.read("mcmod.info")
                meta = metadata_parser.parse_mcmod_info(raw)
            else:
                return Mod(
                    **base,
                    parse_ok=False,
                    parse_error="No recognized mod metadata (fabric.mod.json / mods.toml / mcmod.info)",
                )

            env = meta.get("environment", ModEnvironment.UNKNOWN)
            # Refine env from Fabric-style or side hints on deps
            if env == ModEnvironment.BOTH:
                env = _infer_env_from_deps(meta.get("dependencies") or [])

            return Mod(
                mod_id=meta["mod_id"],
                name=meta["name"],
                version=_clean_version(meta.get("version"), jar_path),
                loader=meta["loader"],
                minecraft_version=meta.get("minecraft_version"),
                environment=env,
                description=meta.get("description"),
                authors=meta.get("authors") or [],
                dependencies=meta.get("dependencies") or [],
                file_path=str(jar_path),
                file_name=file_name,
                file_size=file_size,
                file_hash=file_hash,
                parse_ok=True,
            )
    except zipfile.BadZipFile as exc:
        return Mod(**base, parse_ok=False, parse_error=f"Corrupt JAR (bad zip): {exc}")
    except Exception as exc:  # noqa: BLE001 — one bad file must never kill analysis
        return Mod(**base, parse_ok=False, parse_error=f"Parse error: {exc}")


def _clean_version(version: str | None, jar_path: Path) -> str:
    if not version or version.startswith("${"):
        # Fall back to filename heuristic: name-1.2.3.jar
        stem = jar_path.stem
        parts = stem.rsplit("-", 1)
        if len(parts) == 2 and parts[1] and parts[1][0].isdigit():
            return parts[1]
        return version or "unknown"
    return version


def _guess_id_from_filename(file_name: str) -> str:
    stem = Path(file_name).stem.lower()
    # strip version-like suffix
    parts = stem.rsplit("-", 1)
    if len(parts) == 2 and parts[1] and parts[1][0].isdigit():
        return parts[0]
    return stem


def _sha256_prefix(path: Path, nbytes: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(nbytes)
            if not chunk:
                break
            h.update(chunk)
            # Full file hash for correctness on duplicates
    return h.hexdigest()


def _infer_env_from_deps(deps) -> ModEnvironment:
    return ModEnvironment.BOTH
