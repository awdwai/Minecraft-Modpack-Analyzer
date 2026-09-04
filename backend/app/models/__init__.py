"""Shared domain models — the vocabulary used across all layers."""

from .analysis_result import AnalysisResult, AnalysisSummary, DependencyGraphData, HealthScore
from .dependency import Dependency, DependencyKind
from .finding import Finding, FindingSeverity, FindingConfidence
from .mod import Mod, ModEnvironment, ModLoader

__all__ = [
    "AnalysisResult",
    "AnalysisSummary",
    "Dependency",
    "DependencyGraphData",
    "DependencyKind",
    "Finding",
    "FindingConfidence",
    "FindingSeverity",
    "HealthScore",
    "Mod",
    "ModEnvironment",
    "ModLoader",
]
