"""Pytest configuration — ensure backend/ is on sys.path."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

FIXTURES = BACKEND / "fixtures" / "modpacks"
