"""AnalysisResult — the whole answer for one analysis run."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from .finding import Finding
from .mod import Mod, ModLoader


class ScorePenalty(BaseModel):
    reason: str
    amount: int
    category: str
    finding_id: Optional[str] = None


class HealthScore(BaseModel):
    score: int = 100
    category_scores: dict[str, int] = Field(default_factory=dict)
    score_explanation: list[ScorePenalty] = Field(default_factory=list)


class AnalysisSummary(BaseModel):
    pack_name: str
    path: str
    jar_count: int = 0
    mod_count: int = 0
    parse_failure_count: int = 0
    inferred_minecraft_version: Optional[str] = None
    inferred_loader: Optional[ModLoader] = None
    client_mod_count: int = 0
    server_mod_count: int = 0
    both_mod_count: int = 0
    finding_counts: dict[str, int] = Field(default_factory=dict)
    has_mods_folder: bool = False
    has_config_folder: bool = False
    has_logs_folder: bool = False


class GraphNode(BaseModel):
    id: str
    label: str
    mod_id: str
    version: str
    environment: str
    loader: str
    has_error: bool = False


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    kind: str
    label: Optional[str] = None


class DependencyGraphData(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    cycles: list[list[str]] = Field(default_factory=list)


class ModpackInventory(BaseModel):
    """Raw scan of the folder before JAR interpretation."""

    path: str
    pack_name: str
    jar_files: list[str] = Field(default_factory=list)
    config_files: list[str] = Field(default_factory=list)
    log_files: list[str] = Field(default_factory=list)
    has_mods_folder: bool = False
    has_config_folder: bool = False
    has_logs_folder: bool = False
    other_notable: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    analysis_id: str
    summary: AnalysisSummary
    mods: list[Mod] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    graph: DependencyGraphData = Field(default_factory=DependencyGraphData)
    health: HealthScore = Field(default_factory=HealthScore)
    inventory: Optional[ModpackInventory] = None
    duration_ms: int = 0
    created_at: str = ""
    extras: dict[str, Any] = Field(default_factory=dict)
