"""Finding — one explainable issue with severity, evidence, and confidence."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class FindingConfidence(str, Enum):
    CONFIRMED = "confirmed"
    POTENTIAL = "potential"


class Finding(BaseModel):
    id: str
    category: str
    severity: FindingSeverity
    confidence: FindingConfidence
    title: str
    message: str
    evidence: list[str] = Field(default_factory=list)
    confidence_reason: Optional[str] = None
    suggested_action: Optional[str] = None
    related_mod_ids: list[str] = Field(default_factory=list)
    related_files: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
