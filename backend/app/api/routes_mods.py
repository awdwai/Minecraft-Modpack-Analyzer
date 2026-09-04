"""Mods listing route."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.cache import get_analysis

router = APIRouter(tags=["mods"])


@router.get("/mods")
def list_mods(
    analysis_id: str = Query(...),
    q: str | None = Query(None, description="Search name/id/filename"),
):
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Unknown analysis_id: {analysis_id}")

    mods = result.mods
    if q:
        needle = q.lower()
        mods = [
            m
            for m in mods
            if needle in m.mod_id.lower()
            or needle in m.name.lower()
            or needle in m.file_name.lower()
        ]
    return {"analysis_id": analysis_id, "count": len(mods), "mods": mods}
