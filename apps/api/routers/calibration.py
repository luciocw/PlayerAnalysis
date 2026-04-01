from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

from config import settings
from services import homography, session_store

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Models ─────────────────────────────────────────────────────────────────────

class CornerPoint(BaseModel):
    x: float
    y: float


class CalibrateRequest(BaseModel):
    corners: list[CornerPoint]
    frame_width: int
    frame_height: int

    @field_validator("corners")
    @classmethod
    def _must_have_four_corners(cls, v: list[CornerPoint]) -> list[CornerPoint]:
        if len(v) != 4:
            raise ValueError(f"São necessários exatamente 4 cantos, recebido {len(v)}")
        return v

    @field_validator("frame_width", "frame_height")
    @classmethod
    def _positive_dimensions(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("As dimensões do frame devem ser positivas")
        return v


class CalibrateResponse(BaseModel):
    homography_matrix: list[list[float]]
    reprojection_error: float
    valid: bool


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/frame/first")
async def get_first_frame(session_id: str) -> FileResponse:
    """Return the first frame JPEG for the calibration UI."""
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")

    frame_path: Path = settings.sessions_dir / session_id / "frame_first.jpg"
    if not frame_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Primeiro frame ainda não disponível. Tente novamente em instantes.",
        )

    return FileResponse(
        path=str(frame_path),
        media_type="image/jpeg",
        filename=f"frame_first_{session_id}.jpg",
    )


@router.post("/sessions/{session_id}/calibrate", response_model=CalibrateResponse)
async def calibrate_session(session_id: str, body: CalibrateRequest) -> CalibrateResponse:
    """Compute homography matrix from four field-corner points."""
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")

    # Build pixel-coordinate list expected by homography service
    pixel_corners: list[tuple[float, float]] = [(c.x, c.y) for c in body.corners]

    try:
        result: dict[str, Any] = homography.compute_homography(
            pixel_corners=pixel_corners,
            frame_width=body.frame_width,
            frame_height=body.frame_height,
            field_width_m=session["field_width_m"],
            field_height_m=session["field_height_m"],
        )
    except Exception as exc:
        logger.error("Erro ao computar homografia para sessão %s: %s", session_id, exc)
        raise HTTPException(status_code=500, detail="Erro interno ao computar homografia") from exc

    h_matrix: list[list[float]] = result["homography_matrix"]
    reprojection_error: float = result["reprojection_error"]
    valid: bool = reprojection_error < 5.0

    if not valid:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Calibração imprecisa, tente novamente "
                f"(erro de reprojeção={reprojection_error:.2f}px, máximo=5px)"
            ),
        )

    # Persist the matrix as JSON in the session record
    session_store.update_session(
        session_id,
        homography_matrix=json.dumps(h_matrix),
        status="calibrated",
    )

    logger.info(
        "Sessão %s calibrada com sucesso (reprojection_error=%.3f)",
        session_id,
        reprojection_error,
    )

    return CalibrateResponse(
        homography_matrix=h_matrix,
        reprojection_error=reprojection_error,
        valid=valid,
    )
