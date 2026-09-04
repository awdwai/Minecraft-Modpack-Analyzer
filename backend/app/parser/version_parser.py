"""Semantic-ish Minecraft version parsing and constraint checking.

Numeric segment compare — never string lexicographic (avoids 2.9 > 2.10 bugs).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


_SEGMENT = re.compile(r"(\d+)|([A-Za-z]+)|([.+_-])")


@dataclass(frozen=True, order=False)
class Version:
    raw: str
    segments: tuple

    @classmethod
    def parse(cls, text: str) -> "Version":
        raw = (text or "").strip()
        if not raw:
            return cls(raw="", segments=())
        # Strip common wrappers like [1.20.1]
        cleaned = raw.strip("[]() ")
        parts: list = []
        for match in _SEGMENT.finditer(cleaned):
            num, alpha, _sep = match.groups()
            if num is not None:
                parts.append(int(num))
            elif alpha is not None:
                parts.append(alpha.lower())
        return cls(raw=raw, segments=tuple(parts))

    def __lt__(self, other: "Version") -> bool:
        return _cmp(self.segments, other.segments) < 0

    def __le__(self, other: "Version") -> bool:
        return _cmp(self.segments, other.segments) <= 0

    def __gt__(self, other: "Version") -> bool:
        return _cmp(self.segments, other.segments) > 0

    def __ge__(self, other: "Version") -> bool:
        return _cmp(self.segments, other.segments) >= 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return _cmp(self.segments, other.segments) == 0


def _cmp(a: tuple, b: tuple) -> int:
    n = max(len(a), len(b))
    for i in range(n):
        left = a[i] if i < len(a) else 0
        right = b[i] if i < len(b) else 0
        # Numbers before strings for mixed (rare)
        if type(left) is not type(right):
            if isinstance(left, int) and isinstance(right, str):
                return -1
            if isinstance(left, str) and isinstance(right, int):
                return 1
        if left < right:
            return -1
        if left > right:
            return 1
    return 0


@dataclass(frozen=True)
class Constraint:
    """A single version constraint like >=1.20.1 or [1.20,1.21)."""

    op: str
    version: Version
    upper: Optional[Version] = None
    upper_inclusive: bool = False
    lower_inclusive: bool = True


_OPS = (">=", "<=", "!=", "==", ">", "<", "=")


def parse_constraint(expr: Optional[str]) -> list[Constraint]:
    """Parse Maven/Forge/Fabric-ish version ranges into constraints.

    Supported forms:
    - empty / * / any → no constraints (always satisfied)
    - >=1.20.1, >1.0, <=2.0, =1.20.1
    - [1.20,1.21), (1.19,1.20], [1.20.1]
    - comma-separated AND of the above
    """
    if expr is None:
        return []
    text = str(expr).strip()
    if not text or text in {"*", "any", "Any"}:
        return []

    # Bracket range: [1.20,1.21), [1.20.1], [5.0,), (,1.21]
    bracket = re.fullmatch(
        r"([\[\(])\s*([^,\]]*?)\s*(?:,\s*([^\)\]]*?)?\s*)?([\]\)])",
        text,
    )
    if bracket:
        lo_br, lo_v, hi_v, hi_br = bracket.groups()
        lo_v = (lo_v or "").strip()
        hi_v = (hi_v or "").strip() if hi_v is not None else None

        # Exact single version [1.20.1] — no comma in original
        if "," not in text:
            return [Constraint(op="=", version=Version.parse(lo_v))]

        constraints: list[Constraint] = []
        if lo_v:
            op = ">=" if lo_br == "[" else ">"
            constraints.append(Constraint(op=op, version=Version.parse(lo_v)))
        if hi_v:
            op = "<=" if hi_br == "]" else "<"
            constraints.append(Constraint(op=op, version=Version.parse(hi_v)))
        return constraints

    constraints: list[Constraint] = []
    # Split on && or comma (but not inside brackets — already handled)
    pieces = re.split(r"\s*(?:,|&&)\s*", text)
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        matched = False
        for op in _OPS:
            if piece.startswith(op):
                ver = Version.parse(piece[len(op) :].strip())
                normalized = "=" if op == "==" else op
                constraints.append(Constraint(op=normalized, version=ver))
                matched = True
                break
        if not matched:
            # Bare version → equality
            constraints.append(Constraint(op="=", version=Version.parse(piece)))
    return constraints


def satisfies(version_text: str, constraint_expr: Optional[str]) -> bool:
    """Return True if version_text satisfies the constraint expression."""
    constraints = parse_constraint(constraint_expr)
    if not constraints:
        return True
    ver = Version.parse(version_text)
    return all(_satisfies_one(ver, c) for c in constraints)


def _satisfies_one(ver: Version, c: Constraint) -> bool:
    if c.op == "range":
        assert c.upper is not None
        lower_ok = ver >= c.version if c.lower_inclusive else ver > c.version
        upper_ok = ver <= c.upper if c.upper_inclusive else ver < c.upper
        return lower_ok and upper_ok
    if c.op in ("=", "=="):
        return ver == c.version
    if c.op == "!=":
        return ver != c.version
    if c.op == ">":
        return ver > c.version
    if c.op == ">=":
        return ver >= c.version
    if c.op == "<":
        return ver < c.version
    if c.op == "<=":
        return ver <= c.version
    return True
