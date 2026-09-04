"""Parse Fabric / Forge / NeoForge metadata into normalized fields."""

from __future__ import annotations

import json
import sys
from typing import Any, Optional

from app.models.dependency import Dependency, DependencyKind
from app.models.mod import ModEnvironment, ModLoader

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def parse_fabric_mod_json(raw: bytes) -> dict[str, Any]:
    data = json.loads(raw.decode("utf-8", errors="replace"))
    mod_id = str(data.get("id") or "unknown")
    name = str(data.get("name") or mod_id)
    version = str(data.get("version") or "unknown")
    description = data.get("description")
    authors = _normalize_authors(data.get("authors"))

    env = _fabric_environment(data.get("environment"))
    mc_version = None
    deps: list[Dependency] = []

    depends = data.get("depends") or {}
    if isinstance(depends, dict):
        for dep_id, constraint in depends.items():
            if dep_id in {"minecraft", "java"}:
                if dep_id == "minecraft":
                    mc_version = str(constraint)
                continue
            if dep_id in {"fabricloader", "fabric-loader", "fabric"}:
                continue
            deps.append(
                Dependency(
                    mod_id=str(dep_id),
                    version_constraint=_constraint_str(constraint),
                    kind=DependencyKind.REQUIRED,
                )
            )

    recommends = data.get("recommends") or {}
    if isinstance(recommends, dict):
        for dep_id, constraint in recommends.items():
            deps.append(
                Dependency(
                    mod_id=str(dep_id),
                    version_constraint=_constraint_str(constraint),
                    kind=DependencyKind.OPTIONAL,
                )
            )

    breaks = data.get("breaks") or {}
    if isinstance(breaks, dict):
        for dep_id, constraint in breaks.items():
            deps.append(
                Dependency(
                    mod_id=str(dep_id),
                    version_constraint=_constraint_str(constraint),
                    kind=DependencyKind.CONFLICTS,
                )
            )

    conflicts = data.get("conflicts") or {}
    if isinstance(conflicts, dict):
        for dep_id, constraint in conflicts.items():
            deps.append(
                Dependency(
                    mod_id=str(dep_id),
                    version_constraint=_constraint_str(constraint),
                    kind=DependencyKind.CONFLICTS,
                )
            )

    return {
        "mod_id": mod_id,
        "name": name,
        "version": version,
        "loader": ModLoader.FABRIC,
        "minecraft_version": mc_version,
        "environment": env,
        "description": description if isinstance(description, str) else None,
        "authors": authors,
        "dependencies": deps,
    }


def parse_mods_toml(raw: bytes, *, neoforge: bool = False) -> dict[str, Any]:
    data = tomllib.loads(raw.decode("utf-8", errors="replace"))
    mods = data.get("mods") or []
    if not mods:
        raise ValueError("mods.toml has no [[mods]] entries")

    first = mods[0]
    mod_id = str(first.get("modId") or first.get("modid") or "unknown")
    name = str(first.get("displayName") or first.get("name") or mod_id)
    version = str(first.get("version") or "unknown")
    # ${file.jarVersion} style placeholders stay as-is; callers may refine
    description = first.get("description")
    authors_raw = first.get("authors")
    authors = _normalize_authors(authors_raw)

    loader = ModLoader.NEOFORGE if neoforge else ModLoader.FORGE
    # Detect NeoForge from loader / dependencies section even if path was mods.toml
    if not neoforge:
        loader_tokens = " ".join(
            str(x).lower()
            for x in (
                data.get("modLoader"),
                data.get("loaderVersion"),
            )
            if x
        )
        if "neoforge" in loader_tokens:
            loader = ModLoader.NEOFORGE

    deps: list[Dependency] = []
    mc_version = None
    environment = ModEnvironment.BOTH

    # dependencies.<modId> = [{...}]
    dep_section = data.get("dependencies") or {}
    if isinstance(dep_section, dict):
        entries = dep_section.get(mod_id) or dep_section.get(mod_id.lower()) or []
        # Sometimes keyed oddly — flatten all lists
        if not entries:
            for _key, val in dep_section.items():
                if isinstance(val, list):
                    entries = list(entries) + val
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            dep_id = str(entry.get("modId") or entry.get("modid") or "")
            if not dep_id:
                continue
            side = str(entry.get("side") or "BOTH").upper()
            mandatory = entry.get("mandatory")
            # NeoForge uses type= required/optional/incompatible/discouraged
            dep_type = str(entry.get("type") or "").lower()
            version_range = entry.get("versionRange") or entry.get("version")
            constraint = str(version_range) if version_range else None

            if dep_id.lower() in {"minecraft", "forge", "neoforge", "fml"}:
                if dep_id.lower() == "minecraft":
                    mc_version = constraint
                if dep_id.lower() == "neoforge":
                    loader = ModLoader.NEOFORGE
                continue

            kind = DependencyKind.REQUIRED
            if dep_type in {"incompatible", "discouraged"} or (
                isinstance(mandatory, bool) and not mandatory and dep_type == ""
            ):
                if dep_type == "incompatible":
                    kind = DependencyKind.CONFLICTS
                else:
                    kind = DependencyKind.OPTIONAL
            elif isinstance(mandatory, bool) and not mandatory:
                kind = DependencyKind.OPTIONAL
            elif dep_type == "optional":
                kind = DependencyKind.OPTIONAL
            elif dep_type in {"required", ""}:
                kind = DependencyKind.REQUIRED

            # side CLIENT → client-only dependency; also hint environment
            side_norm = None
            if side == "CLIENT":
                side_norm = "client"
            elif side == "SERVER":
                side_norm = "server"

            deps.append(
                Dependency(
                    mod_id=dep_id,
                    version_constraint=constraint,
                    kind=kind,
                    side=side_norm,
                )
            )

    return {
        "mod_id": mod_id,
        "name": name,
        "version": version,
        "loader": loader,
        "minecraft_version": mc_version,
        "environment": environment,
        "description": description if isinstance(description, str) else None,
        "authors": authors,
        "dependencies": deps,
    }


def parse_mcmod_info(raw: bytes) -> dict[str, Any]:
    data = json.loads(raw.decode("utf-8", errors="replace"))
    if isinstance(data, list):
        if not data:
            raise ValueError("mcmod.info is an empty list")
        entry = data[0]
    elif isinstance(data, dict) and "modList" in data:
        mod_list = data["modList"]
        if not mod_list:
            raise ValueError("mcmod.info modList is empty")
        entry = mod_list[0]
    else:
        entry = data

    mod_id = str(entry.get("modid") or entry.get("modId") or "unknown")
    name = str(entry.get("name") or mod_id)
    version = str(entry.get("version") or "unknown")
    mc_version = entry.get("mcversion") or entry.get("minecraftVersion")
    deps_raw = entry.get("requiredMods") or entry.get("dependencies") or []
    deps: list[Dependency] = []
    for item in deps_raw:
        dep_id = str(item).split("@")[0].strip()
        constraint = None
        if "@" in str(item):
            constraint = str(item).split("@", 1)[1]
        if dep_id.lower() in {"forge", "fml", "minecraft"}:
            continue
        deps.append(Dependency(mod_id=dep_id, version_constraint=constraint, kind=DependencyKind.REQUIRED))

    return {
        "mod_id": mod_id,
        "name": name,
        "version": version,
        "loader": ModLoader.FORGE,
        "minecraft_version": str(mc_version) if mc_version else None,
        "environment": ModEnvironment.BOTH,
        "description": entry.get("description") if isinstance(entry.get("description"), str) else None,
        "authors": _normalize_authors(entry.get("authorList") or entry.get("authors")),
        "dependencies": deps,
    }


def _fabric_environment(value: Any) -> ModEnvironment:
    if value == "client":
        return ModEnvironment.CLIENT
    if value == "server":
        return ModEnvironment.SERVER
    if value in ("*", None, ""):
        return ModEnvironment.BOTH
    return ModEnvironment.UNKNOWN


def _constraint_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, list):
        return ",".join(str(v) for v in value)
    return str(value)


def _normalize_authors(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [a.strip() for a in value.split(",") if a.strip()]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict) and "name" in item:
                out.append(str(item["name"]))
        return out
    return []
