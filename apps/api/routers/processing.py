from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from config import settings
from services import pipeline, session_store

logger = logging.getLogger(__name__)

router = APIRouter()

# SSE poll interval in seconds
_SSE_POLL_INTERVAL = 1.0


# ── Background task ────────────────────────────────────────────────────────────

def _run_pipeline_task(
    session_id: str,
    video_path: str,
    homography_matrix: list[list[float]],
    selected_track_id: int,
    sessions_dir: str,
) -> None:
    """
    Synchronous wrapper executed inside FastAPI BackgroundTasks.
    Updates session status on success or failure.
    """
    try:
        pipeline.run_pipeline(
            session_id=session_id,
            video_path=video_path,
            homography_matrix=homography_matrix,
            selected_track_id=selected_track_id,
            sessions_dir=sessions_dir,
        )
        session_store.update_session(session_id, status="done")
        logger.info("Pipeline concluído com sucesso para sessão %s", session_id)
    except Exception as exc:
        error_msg = str(exc)
        session_store.update_session(session_id, status="error", error_message=error_msg)
        logger.error("Pipeline falhou para sessão %s: %s", session_id, error_msg)


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/sessions/{session_id}/process", status_code=202)
async def start_processing(
    session_id: str,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """
    Trigger full video analysis for a session.

    Preconditions:
      - Session must exist
      - Homography matrix must be set (status >= 'calibrated')
      - A player track must be selected (status >= 'player_selected')
    """
    session: dict[str, Any] | None = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")

    # Guard: must have homography
    if not session.get("homography_matrix"):
        raise HTTPException(
            status_code=422,
            detail="A sessão ainda não foi calibrada. Execute a calibração antes de processar.",
        )

    # Guard: must have selected player
    if session.get("selected_track_id") is None:
        raise HTTPException(
            status_code=422,
            detail="Nenhum jogador selecionado. Selecione um jogador antes de processar.",
        )

    # Guard: already running
    if session.get("status") == "processing":
        raise HTTPException(status_code=409, detail="Já está processando")

    # Parse persisted homography matrix
    try:
        raw_h = session["homography_matrix"]
        homography_matrix: list[list[float]] = (
            json.loads(raw_h) if isinstance(raw_h, str) else raw_h
        )
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        raise HTTPException(
            status_code=500, detail="Matriz de homografia inválida na sessão"
        ) from exc

    video_path = str(settings.upload_dir / session["stored_filename"])
    if not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado no disco")

    # Mark as processing
    session_store.update_session(session_id, status="processing")

    # Schedule pipeline in background
    background_tasks.add_task(
        _run_pipeline_task,
        session_id=session_id,
        video_path=video_path,
        homography_matrix=homography_matrix,
        selected_track_id=int(session["selected_track_id"]),
        sessions_dir=str(settings.sessions_dir),
    )

    logger.info("Pipeline iniciado em background para sessão %s", session_id)
    return {"status": "processing", "session_id": session_id}


# ── SSE progress stream ────────────────────────────────────────────────────────

async def _progress_generator(session_id: str) -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE events by polling progress.json.
    Stops when percent == 100 (done) or percent == -1 (error).
    """
    progress_path: Path = settings.sessions_dir / session_id / "progress.json"

    while True:
        payload: dict[str, Any]

        if progress_path.exists():
            try:
                text = progress_path.read_text(encoding="utf-8")
                payload = json.loads(text)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug("Erro ao ler progress.json para %s: %s", session_id, exc)
                payload = {"percent": 0, "message": "Aguardando..."}
        else:
            # File not yet created — pipeline may be initialising
            payload = {"percent": 0, "message": "Iniciando pipeline..."}

        yield f"data: {json.dumps(payload)}\n\n"

        percent = payload.get("percent", 0)
        if percent == 100 or percent == -1:
            break

        await asyncio.sleep(_SSE_POLL_INTERVAL)


@router.get("/progress/{session_id}")
async def stream_progress(session_id: str) -> StreamingResponse:
    """
    Server-Sent Events endpoint for real-time pipeline progress.
    Polls {sessions_dir}/{session_id}/progress.json every second.
    """
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")

    return StreamingResponse(
        _progress_generator(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering if behind proxy
        },
    )
