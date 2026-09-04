"""Conflict / duplicate analysis."""

from __future__ import annotations

import uuid
from collections import defaultdict

from app.models.finding import Finding, FindingConfidence, FindingSeverity
from app.models.mod import Mod
from app.parser.version_parser import Version


def analyze_conflicts(mods: list[Mod]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_duplicate_mod_ids(mods))
    findings.extend(_hash_duplicates(mods))
    findings.extend(_parse_failures(mods))
    return findings


def _duplicate_mod_ids(mods: list[Mod]) -> list[Finding]:
    by_id: dict[str, list[Mod]] = defaultdict(list)
    for mod in mods:
        if mod.parse_ok:
            by_id[mod.mod_id.lower()].append(mod)

    findings: list[Finding] = []
    for mod_id, group in by_id.items():
        if len(group) < 2:
            continue
        versions = {m.version for m in group}
        files = [m.file_name for m in group]
        multi_version = len(versions) > 1
        # Prefer keeping the highest version
        try:
            newest = max(group, key=lambda m: Version.parse(m.version))
            keep_hint = newest.file_name
        except Exception:  # noqa: BLE001
            keep_hint = group[0].file_name

        findings.append(
            Finding(
                id=f"dup-{uuid.uuid4().hex[:10]}",
                category="duplicate",
                severity=FindingSeverity.WARNING,
                confidence=FindingConfidence.CONFIRMED,
                title=f"Duplicate mod ID: {mod_id}",
                message=(
                    f"Mod ID '{mod_id}' appears {len(group)} times"
                    + (" with different versions" if multi_version else " (same version)")
                    + f": {', '.join(files)}"
                ),
                evidence=[f"{m.file_name} version={m.version}" for m in group],
                confidence_reason="Same mod_id parsed from multiple JAR metadata files.",
                suggested_action=f"Keep one JAR (likely {keep_hint}) and remove the others.",
                related_mod_ids=[mod_id],
                related_files=[m.file_path for m in group],
                metadata={"versions": sorted(versions), "multi_version": multi_version},
            )
        )
    return findings


def _hash_duplicates(mods: list[Mod]) -> list[Finding]:
    by_hash: dict[str, list[Mod]] = defaultdict(list)
    for mod in mods:
        if mod.file_hash:
            by_hash[mod.file_hash].append(mod)

    findings: list[Finding] = []
    for digest, group in by_hash.items():
        if len(group) < 2:
            continue
        # Skip if already same mod_id duplicate (still useful as identical bytes)
        findings.append(
            Finding(
                id=f"hash-{uuid.uuid4().hex[:10]}",
                category="duplicate",
                severity=FindingSeverity.INFO,
                confidence=FindingConfidence.CONFIRMED,
                title="Identical JAR copies",
                message=f"These files are byte-identical: {', '.join(m.file_name for m in group)}",
                evidence=[f"sha256={digest[:16]}…", *[m.file_path for m in group]],
                confidence_reason="Matching full-file SHA-256 hashes.",
                suggested_action="Remove redundant copies.",
                related_mod_ids=[m.mod_id for m in group],
                related_files=[m.file_path for m in group],
            )
        )
    return findings


def _parse_failures(mods: list[Mod]) -> list[Finding]:
    findings: list[Finding] = []
    for mod in mods:
        if mod.parse_ok:
            continue
        findings.append(
            Finding(
                id=f"parse-{uuid.uuid4().hex[:10]}",
                category="parse",
                severity=FindingSeverity.WARNING,
                confidence=FindingConfidence.CONFIRMED,
                title=f"Failed to parse JAR: {mod.file_name}",
                message=mod.parse_error or "Unknown parse error",
                evidence=[mod.file_path, mod.parse_error or ""],
                confidence_reason="ZIP/metadata read failed during analysis.",
                suggested_action="Re-download the mod or remove the corrupt file.",
                related_mod_ids=[mod.mod_id] if mod.mod_id else [],
                related_files=[mod.file_path],
            )
        )
    return findings
