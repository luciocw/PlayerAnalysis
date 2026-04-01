from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from services import session_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sessions")
async def list_sessions() -> dict[str, list[dict[str, Any]]]:
    """Return all non-deleted sessions, newest first."""
    sessions = session_store.list_sessions()
    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict[str, Any]:
    """Return a single session by ID, or 404."""
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict[str, bool]:
    """Soft-delete a session (marks status='deleted', files are kept)."""
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")

    session_store.update_session(session_id, status="deleted")
    logger.info("Sessão marcada como deletada: %s", session_id)
    return {"ok": True}
