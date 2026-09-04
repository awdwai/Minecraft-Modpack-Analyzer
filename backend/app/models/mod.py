"""Normalized Mod — one JAR after parsing. Loader quirks stay in the parser."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .dependency import Dependency


class ModLoader(str, Enum):
    FABRIC = "fabric"
    FORGE = "forge"
    NEOFORGE = "neoforge"
    UNKNOWN = "unknown"


class ModEnvironment(str, Enum):
    CLIENT = "client"
    SERVER = "server"
    BOTH = "both"
    UNKNOWN = "unknown"


class Mod(BaseModel):
    """One JAR after metadata parsing, normalized across loaders."""

    mod_id: str
    name: str
    version: str = "unknown"
    loader: ModLoader = ModLoader.UNKNOWN
    minecraft_version: Optional[str] = None
    environment: ModEnvironment = ModEnvironment.UNKNOWN
    description: Optional[str] = None
    authors: list[str] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)
    file_path: str
    file_name: str
    file_size: int = 0
    file_hash: Optional[str] = None
    parse_ok: bool = True
    parse_error: Optional[str] = None
