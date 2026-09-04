"""Dependency analysis — missing required/optional deps and version mismatches."""

from __future__ import annotations

import uuid
from collections import defaultdict

from app.models.dependency import DependencyKind
from app.models.finding import Finding, FindingConfidence, FindingSeverity
from app.models.mod import Mod
from app.parser.version_parser import satisfies


def analyze_dependencies(mods: list[Mod]) -> list[Finding]:
    findings: list[Finding] = []
    by_id: dict[str, list[Mod]] = defaultdict(list)
    for mod in mods:
        if mod.parse_ok:
            by_id[mod.mod_id.lower()].append(mod)

    present_ids = set(by_id.keys())

    for mod in mods:
        if not mod.parse_ok:
            continue
        for dep in mod.dependencies:
            dep_key = dep.mod_id.lower()
            if dep.kind == DependencyKind.EMBEDDED:
                continue

            if dep.kind == DependencyKind.REQUIRED:
                if dep_key not in present_ids:
                    findings.append(
                        Finding(
                            id=_fid("missing"),
                            category="dependency",
                            severity=FindingSeverity.CRITICAL,
                            confidence=FindingConfidence.CONFIRMED,
                            title=f"Missing required dependency: {dep.mod_id}",
                            message=(
                                f"{mod.name} ({mod.mod_id}) requires {dep.mod_id}"
                                + (f" ({dep.version_constraint})" if dep.version_constraint else "")
                                + " but it was not found in the pack."
                            ),
                            evidence=[
                                f"Source JAR: {mod.file_name}",
                                f"Declared dependency: {dep.mod_id} kind=required"
                                + (f" version={dep.version_constraint}" if dep.version_constraint else ""),
                            ],
                            confidence_reason="Explicit required dependency in mod metadata.",
                            suggested_action=f"Install mod '{dep.mod_id}' matching the version constraint, or remove {mod.mod_id}.",
                            related_mod_ids=[mod.mod_id, dep.mod_id],
                            related_files=[mod.file_path],
                        )
                    )
                else:
                    # Version constraint check against installed
                    if dep.version_constraint:
                        installed = by_id[dep_key]
                        if not any(satisfies(m.version, dep.version_constraint) for m in installed):
                            versions = ", ".join(f"{m.version} ({m.file_name})" for m in installed)
                            findings.append(
                                Finding(
                                    id=_fid("ver"),
                                    category="version",
                                    severity=FindingSeverity.CRITICAL,
                                    confidence=FindingConfidence.CONFIRMED,
                                    title=f"Version conflict: {dep.mod_id}",
                                    message=(
                                        f"{mod.mod_id} needs {dep.mod_id} {dep.version_constraint}, "
                                        f"but installed version(s): {versions}"
                                    ),
                                    evidence=[
                                        f"Constraint from {mod.file_name}: {dep.version_constraint}",
                                        f"Installed: {versions}",
                                    ],
                                    confidence_reason="Version constraint from metadata fails numeric compare.",
                                    suggested_action=f"Update {dep.mod_id} to satisfy {dep.version_constraint}.",
                                    related_mod_ids=[mod.mod_id, dep.mod_id],
                                    related_files=[mod.file_path] + [m.file_path for m in installed],
                                )
                            )

            elif dep.kind == DependencyKind.OPTIONAL:
                if dep_key not in present_ids:
                    findings.append(
                        Finding(
                            id=_fid("opt"),
                            category="dependency",
                            severity=FindingSeverity.INFO,
                            confidence=FindingConfidence.CONFIRMED,
                            title=f"Optional dependency missing: {dep.mod_id}",
                            message=f"{mod.mod_id} optionally uses {dep.mod_id}, which is not installed.",
                            evidence=[f"Optional dep declared in {mod.file_name}"],
                            confidence_reason="Explicit optional dependency in metadata.",
                            suggested_action=f"Install {dep.mod_id} for extra features, or ignore.",
                            related_mod_ids=[mod.mod_id, dep.mod_id],
                            related_files=[mod.file_path],
                        )
                    )

            elif dep.kind == DependencyKind.CONFLICTS:
                if dep_key in present_ids:
                    # If constraint present, only conflict when installed version matches the conflict range
                    installed = by_id[dep_key]
                    hits = installed
                    if dep.version_constraint:
                        hits = [m for m in installed if satisfies(m.version, dep.version_constraint)]
                    if hits:
                        findings.append(
                            Finding(
                                id=_fid("conf"),
                                category="conflict",
                                severity=FindingSeverity.CRITICAL,
                                confidence=FindingConfidence.CONFIRMED,
                                title=f"Confirmed conflict: {mod.mod_id} ↔ {dep.mod_id}",
                                message=(
                                    f"{mod.name} declares a conflict with {dep.mod_id}"
                                    + (f" ({dep.version_constraint})" if dep.version_constraint else "")
                                    + " and that mod is present."
                                ),
                                evidence=[
                                    f"Conflict declared in {mod.file_name}",
                                    f"Present: {', '.join(m.file_name for m in hits)}",
                                ],
                                confidence_reason="Explicit conflicts/breaks entry in mod metadata.",
                                suggested_action=f"Remove either {mod.mod_id} or {dep.mod_id}.",
                                related_mod_ids=[mod.mod_id, dep.mod_id],
                                related_files=[mod.file_path] + [m.file_path for m in hits],
                            )
                        )

    return findings


def _fid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"
