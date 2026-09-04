"""Comparison + report routes — Phase 5 stubs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.cache import get_analysis
from app.services.compare_service import compare_modpacks

router = APIRouter(tags=["comparison"])


class CompareRequest(BaseModel):
    path_a: str = Field(..., description="Absolute path to first modpack")
    path_b: str = Field(..., description="Absolute path to second modpack")


@router.post("/compare")
def compare(body: CompareRequest):
    return compare_modpacks(body.path_a, body.path_b)


@router.get("/report")
def report(
    analysis_id: str = Query(...),
    format: str = Query("json", pattern="^(json|html)$"),
):
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Unknown analysis_id: {analysis_id}")
    return {
        "implemented": False,
        "message": "Report export is not implemented yet (Phase 5).",
        "analysis_id": analysis_id,
        "requested_format": format,
        "hint": "Use GET /api/analysis/{id} for the raw AnalysisResult JSON today.",
    }
