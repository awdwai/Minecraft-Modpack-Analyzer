"""Dependency / duplicate / health analysis tests."""

from pathlib import Path

import pytest

from app.analysis.conflict_analyzer import analyze_conflicts
from app.analysis.dependency_analyzer import analyze_dependencies
from app.analysis.health_analyzer import compute_health_score
from app.graph.dependency_graph import build_dependency_graph
from app.services.analyze_service import run_analysis
from fixtures.build_fixtures import build

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "modpacks"


@pytest.fixture(scope="session", autouse=True)
def _fixtures():
    build()


def test_missing_dependency_finding():
    result = run_analysis(str(FIXTURES / "mini_missing_dep"))
    titles = [f.title for f in result.findings]
    assert any("Missing required dependency" in t and "curios" in t.lower() for t in titles)
    assert result.health.score < 100


def test_duplicates():
    result = run_analysis(str(FIXTURES / "mini_duplicates"))
    dup_findings = [f for f in result.findings if f.category == "duplicate"]
    assert any("jei" in f.title.lower() for f in dup_findings)


def test_version_conflict():
    result = run_analysis(str(FIXTURES / "mini_version_conflict"))
    assert any(f.category == "version" for f in result.findings)


def test_circular_deps():
    result = run_analysis(str(FIXTURES / "mini_circular"))
    assert result.graph.cycles
    assert any("cycle" in f.title.lower() for f in result.findings)


def test_fabric_pack_healthy_enough():
    result = run_analysis(str(FIXTURES / "mini_fabric"))
    # missing fabric-api (skipped as loader) but librarymod present; optional missing is info
    assert result.summary.mod_count >= 2
    assert result.summary.jar_count == 3
    assert result.analysis_id


def test_corrupt_pack_continues():
    result = run_analysis(str(FIXTURES / "mini_corrupt"))
    assert result.summary.parse_failure_count >= 1
    assert any(f.category == "parse" for f in result.findings)


def test_health_score_formula_caps():
    from app.models.finding import Finding, FindingConfidence, FindingSeverity

    findings = [
        Finding(
            id=f"m{i}",
            category="dependency",
            severity=FindingSeverity.CRITICAL,
            confidence=FindingConfidence.CONFIRMED,
            title=f"Missing {i}",
            message="x",
        )
        for i in range(10)
    ]
    health = compute_health_score(findings)
    # 15 * 5 cap = 75 → score 25
    assert health.score == 25
