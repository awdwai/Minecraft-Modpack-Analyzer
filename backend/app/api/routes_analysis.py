"""Analysis routes: health + analyze + stored result lookups."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.cache import get_analysis
from app.models.analysis_result import AnalysisResult
from app.security.path_validation import PathValidationError
from app.services.analyze_service import run_analysis

router = APIRouter(tags=["analysis"])


class AnalyzeRequest(BaseModel):
    path: str = Field(..., description="Absolute path to a local modpack folder")


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "minecraft-modpack-analyzer"


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.post("/analyze", response_model=AnalysisResult)
def analyze(body: AnalyzeRequest) -> AnalysisResult:
    try:
        return run_analysis(body.path)
    except PathValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@router.get("/analysis/{analysis_id}", response_model=AnalysisResult)
def get_stored_analysis(analysis_id: str) -> AnalysisResult:
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Unknown analysis_id: {analysis_id}")
    return result


@router.get("/dependencies")
def get_dependencies(analysis_id: str = Query(...)):
    result = _require(analysis_id)
    dep_findings = [f for f in result.findings if f.category in {"dependency", "version"}]
    return {
        "analysis_id": analysis_id,
        "graph": result.graph,
        "findings": dep_findings,
    }


@router.get("/conflicts")
def get_conflicts(analysis_id: str = Query(...)):
    result = _require(analysis_id)
    conflict_findings = [
        f for f in result.findings if f.category in {"conflict", "duplicate", "compatibility"}
    ]
    return {"analysis_id": analysis_id, "findings": conflict_findings}


def _require(analysis_id: str) -> AnalysisResult:
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Unknown analysis_id: {analysis_id}")
    return result
