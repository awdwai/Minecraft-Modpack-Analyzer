"""Crash / log analysis routes — Phase 5 stubs."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.parser.crash_parser import parse_crash_log

router = APIRouter(tags=["logs"])


class CrashAnalyzeRequest(BaseModel):
    path: str | None = Field(None, description="Absolute path to a crash log file")
    text: str | None = Field(None, description="Raw crash log text")


@router.post("/crash/analyze")
def crash_analyze(body: CrashAnalyzeRequest):
    if body.text:
        return parse_crash_log(body.text)
    return {
        "implemented": False,
        "message": "Crash log analysis is not implemented yet (Phase 5).",
        "hint": "Pass text= for a future parser; path-based reading will land in Phase 5.",
        "findings": [],
    }
