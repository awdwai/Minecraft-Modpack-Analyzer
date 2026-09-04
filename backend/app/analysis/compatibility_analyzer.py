"""Client/server compatibility findings."""

from __future__ import annotations

import uuid
from collections import Counter

from app.models.finding import Finding, FindingConfidence, FindingSeverity
from app.models.mod import Mod, ModEnvironment, ModLoader


def analyze_compatibility(mods: list[Mod], *, assume_server_context: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    ok_mods = [m for m in mods if m.parse_ok]

    # Loader mix heuristic
    loaders = Counter(m.loader for m in ok_mods if m.loader != ModLoader.UNKNOWN)
    if len(loaders) > 1:
        findings.append(
            Finding(
                id=f"loader-{uuid.uuid4().hex[:10]}",
                category="compatibility",
                severity=FindingSeverity.WARNING,
                confidence=FindingConfidence.POTENTIAL,
                title="Multiple mod loaders detected",
                message=(
                    "This pack appears to contain mods for more than one loader: "
                    + ", ".join(f"{k.value}={v}" for k, v in loaders.items())
                ),
                evidence=[f"{m.file_name}: {m.loader.value}" for m in ok_mods if m.loader != ModLoader.UNKNOWN][:20],
                confidence_reason="Inferred from per-JAR metadata loader field; some dual-published mods may be fine.",
                suggested_action="Confirm the pack targets a single loader (Fabric / Forge / NeoForge).",
                related_mod_ids=[],
            )
        )

    # Client-only mods — always report as informational; escalate if server context
    client_only = [m for m in ok_mods if m.environment == ModEnvironment.CLIENT]
    for mod in client_only:
        severity = FindingSeverity.WARNING if assume_server_context else FindingSeverity.INFO
        findings.append(
            Finding(
                id=f"env-{uuid.uuid4().hex[:10]}",
                category="environment",
                severity=severity,
                confidence=FindingConfidence.CONFIRMED
                if mod.environment == ModEnvironment.CLIENT
                else FindingConfidence.POTENTIAL,
                title=f"Client-only mod: {mod.mod_id}",
                message=(
                    f"{mod.name} is marked client-only. "
                    + (
                        "It should not be on a dedicated server."
                        if assume_server_context
                        else "Exclude it when building a server pack."
                    )
                ),
                evidence=[f"environment={mod.environment.value} from {mod.file_name}"],
                confidence_reason="Explicit environment field in Fabric metadata (or equivalent).",
                suggested_action="Omit from server pack / dedicated server mods folder.",
                related_mod_ids=[mod.mod_id],
                related_files=[mod.file_path],
            )
        )

    return findings
