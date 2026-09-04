"""Analyze service — scanner → parser → analyzers → AnalysisResult."""

from __future__ import annotations

import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from app.analysis.compatibility_analyzer import analyze_compatibility
from app.analysis.conflict_analyzer import analyze_conflicts
from app.analysis.dependency_analyzer import analyze_dependencies
from app.analysis.health_analyzer import compute_health_score
from app.analysis.performance_analyzer import analyze_performance
from app.cache import save_analysis
from app.graph.dependency_graph import build_dependency_graph
from app.models.analysis_result import AnalysisResult, AnalysisSummary
from app.models.finding import Finding, FindingConfidence, FindingSeverity
from app.models.mod import Mod, ModEnvironment, ModLoader
from app.parser.jar_parser import parse_jar
from app.scanner.mod_scanner import scan_modpack
from app.security.path_validation import validate_modpack_path


def run_analysis(path: str) -> AnalysisResult:
    started = time.perf_counter()
    root = validate_modpack_path(path)
    inventory = scan_modpack(root)

    mods: list[Mod] = []
    for jar in inventory.jar_files:
        mods.append(parse_jar(Path(jar)))

    findings: list[Finding] = []
    findings.extend(analyze_dependencies(mods))
    findings.extend(analyze_conflicts(mods))
    findings.extend(analyze_compatibility(mods, assume_server_context=False))
    findings.extend(analyze_performance(mods))

    # Cycle findings from graph
    graph = build_dependency_graph(mods)
    for cycle in graph.cycles:
        findings.append(
            Finding(
                id=f"cycle-{uuid.uuid4().hex[:10]}",
                category="dependency",
                severity=FindingSeverity.WARNING,
                confidence=FindingConfidence.CONFIRMED,
                title="Dependency cycle detected",
                message=" → ".join(cycle) + f" → {cycle[0]}",
                evidence=[f"Cycle: {' → '.join(cycle)}"],
                confidence_reason="Detected via NetworkX simple_cycles on declared dependencies.",
                suggested_action="Inspect the cycle; cycles often indicate optional/embedded deps or metadata mistakes.",
                related_mod_ids=list(cycle),
            )
        )

    health = compute_health_score(findings)
    summary = _build_summary(root, inventory, mods, findings)
    duration_ms = int((time.perf_counter() - started) * 1000)

    result = AnalysisResult(
        analysis_id=uuid.uuid4().hex,
        summary=summary,
        mods=mods,
        findings=findings,
        graph=graph,
        health=health,
        inventory=inventory,
        duration_ms=duration_ms,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    save_analysis(result)
    return result


def _build_summary(root: Path, inventory, mods: list[Mod], findings: list[Finding]) -> AnalysisSummary:
    ok = [m for m in mods if m.parse_ok]
    env_counts = Counter(m.environment for m in ok)
    loaders = Counter(m.loader for m in ok if m.loader != ModLoader.UNKNOWN)
    inferred_loader = loaders.most_common(1)[0][0] if loaders else None

    mc_versions = [m.minecraft_version for m in ok if m.minecraft_version]
    inferred_mc = Counter(mc_versions).most_common(1)[0][0] if mc_versions else None

    finding_counts = Counter(f.severity.value for f in findings)

    return AnalysisSummary(
        pack_name=root.name,
        path=str(root),
        jar_count=len(inventory.jar_files),
        mod_count=len(ok),
        parse_failure_count=sum(1 for m in mods if not m.parse_ok),
        inferred_minecraft_version=inferred_mc,
        inferred_loader=inferred_loader,
        client_mod_count=env_counts.get(ModEnvironment.CLIENT, 0),
        server_mod_count=env_counts.get(ModEnvironment.SERVER, 0),
        both_mod_count=env_counts.get(ModEnvironment.BOTH, 0),
        finding_counts=dict(finding_counts),
        has_mods_folder=inventory.has_mods_folder,
        has_config_folder=inventory.has_config_folder,
        has_logs_folder=inventory.has_logs_folder,
    )
