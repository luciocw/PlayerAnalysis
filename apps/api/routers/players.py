from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import settings
from services import pipeline, session_store

logger = logging.getLogger(__name__)

router = APIRouter()

# Number of video frames to scan when building the thumbnail gallery
_PRESCAN_FRAMES = settings.prescan_frames


# ── Models ─────────────────────────────────────────────────────────────────────

class PlayerThumbnail(BaseModel):
    track_id: int
    thumbnail_url: str


class PlayersResponse(BaseModel):
    players: list[PlayerThumbnail]


class SelectPlayerRequest(BaseModel):
    track_id: int


# ── Helpers ────────────────────────────────────────────────────────────────────

def _thumbnail_url(session_id: str, track_id: int) -> str:
    return f"/storage/sessions/{session_id}/thumbnails/{track_id}.jpg"


def _thumbnails_dir(session_id: str) -> Path:
    return settings.sessions_dir / session_id / "thumbnails"


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/players", response_model=PlayersResponse)
async def list_players(session_id: str) -> PlayersResponse:
    """
    Return thumbnails for every tracked player found in the video.

    If the thumbnails directory does not yet exist, runs a quick prescan
    (first N frames at low fps) synchronously before responding.
    """
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")

    thumbs_dir = _thumbnails_dir(session_id)

    if not thumbs_dir.exists() or not any(thumbs_dir.glob("*.jpg")):
        # Run a fast pre-scan to populate thumbnails (first ~10 s of video)
        video_path = settings.upload_dir / session["stored_filename"]
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado")

        thumbs_dir.mkdir(parents=True, exist_ok=True)

        try:
            pipeline.prescan_players(
                video_path=str(video_path),
                output_dir=str(thumbs_dir),
                max_frames=_PRESCAN_FRAMES,
            )
        except Exception as exc:
            logger.error("Erro no prescan para sessão %s: %s", session_id, exc)
            raise HTTPException(
                status_code=500,
                detail="Erro ao escanear jogadores no vídeo",
            ) from exc

    # Collect all thumbnail jpegs; filename stem is the track_id
    jpg_files = sorted(thumbs_dir.glob("*.jpg"))
    players: list[PlayerThumbnail] = []
    for jpg in jpg_files:
        try:
            track_id = int(jpg.stem)
        except ValueError:
            logger.warning("Thumbnail com nome inesperado ignorado: %s", jpg.name)
            continue
        players.append(
            PlayerThumbnail(
                track_id=track_id,
                thumbnail_url=_thumbnail_url(session_id, track_id),
            )
        )

    logger.info("Sessão %s — %d thumbnails encontrados", session_id, len(players))
    return PlayersResponse(players=players)


@router.post("/sessions/{session_id}/select-player")
async def select_player(session_id: str, body: SelectPlayerRequest) -> dict[str, bool]:
    """Record which player track should be analysed in full."""
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")

    # Verify the thumbnail actually exists so the client can't select a ghost track
    thumb_path = _thumbnails_dir(session_id) / f"{body.track_id}.jpg"
    if not thumb_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Track ID {body.track_id} não encontrado nos thumbnails desta sessão",
        )

    session_store.update_session(
        session_id,
        selected_track_id=body.track_id,
        status="player_selected",
    )
    logger.info("Sessão %s — jogador selecionado: track_id=%d", session_id, body.track_id)
    return {"ok": True}
