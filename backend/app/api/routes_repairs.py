"""Repair + server-pack routes — Phase 6 stubs."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services import repair_service

router = APIRouter(tags=["repairs"])


class RepairDuplicateRequest(BaseModel):
    analysis_id: str
    confirm: bool = False


class ServerPackRequest(BaseModel):
    analysis_id: str
    output_path: str | None = Field(None, description="Destination folder (Phase 6)")


@router.post("/repair/duplicate")
def repair_duplicate(body: RepairDuplicateRequest):
    if body.confirm:
        return repair_service.apply_duplicate_repair(body.analysis_id, confirm=True)
    return repair_service.preview_duplicate_repair(body.analysis_id)


@router.post("/server-pack")
def server_pack(body: ServerPackRequest):
    return repair_service.preview_server_pack(body.analysis_id)
