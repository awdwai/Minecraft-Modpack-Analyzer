"""In-memory analysis store + optional JAR metadata cache hooks."""

from __future__ import annotations

from threading import Lock
from typing import Optional

from app.models.analysis_result import AnalysisResult

_lock = Lock()
_store: dict[str, AnalysisResult] = {}


def save_analysis(result: AnalysisResult) -> None:
    with _lock:
        _store[result.analysis_id] = result


def get_analysis(analysis_id: str) -> Optional[AnalysisResult]:
    with _lock:
        return _store.get(analysis_id)


def list_analysis_ids() -> list[str]:
    with _lock:
        return list(_store.keys())


def clear_store() -> None:
    with _lock:
        _store.clear()
