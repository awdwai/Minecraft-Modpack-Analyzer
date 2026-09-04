"""Dependency — needs / optionally wants / conflicts with a mod id + version rule."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class DependencyKind(str, Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    CONFLICTS = "conflicts"
    EMBEDDED = "embedded"


class Dependency(BaseModel):
    mod_id: str
    version_constraint: Optional[str] = None
    kind: DependencyKind = DependencyKind.REQUIRED
    side: Optional[str] = None  # client / server / both / None
