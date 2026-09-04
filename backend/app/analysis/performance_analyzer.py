"""Performance heuristics — stub / light informational findings for Phase 4+."""

from __future__ import annotations

import uuid

from app.models.finding import Finding, FindingConfidence, FindingSeverity
from app.models.mod import Mod


def analyze_performance(mods: list[Mod]) -> list[Finding]:
    """Light heuristic only — never claim hard performance numbers without evidence."""
    findings: list[Finding] = []
    jar_count = len(mods)
    if jar_count >= 300:
        findings.append(
            Finding(
                id=f"perf-{uuid.uuid4().hex[:10]}",
                category="performance",
                severity=FindingSeverity.INFO,
                confidence=FindingConfidence.POTENTIAL,
                title="Very large mod count",
                message=f"This pack has {jar_count} JAR files, which may increase startup time and RAM use.",
                evidence=[f"jar_count={jar_count}"],
                confidence_reason="Heuristic based on count alone; not a measured profile.",
                suggested_action="Consider profiling with Spark after launch; large packs can still run well.",
                related_mod_ids=[],
            )
        )
    return findings
