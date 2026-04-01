from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from uuid import UUID, uuid4

import aiofiles
from fastapi import APIRouter, Form, HTTPException, UploadFile
from pydantic import BaseModel

from config import settings
from services import file_validator, frame_extractor, session_store

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Request / Response models ──────────────────────────────────────────────────

class FinalizeRequest(BaseModel):
    upload_id: str
    total_chunks: int
    original_filename: str
    field_width_m: float
    field_height_m: float


class FinalizeResponse(BaseModel):
    session_id: str
    status: str


class ChunkResponse(BaseModel):
    received: bool
    chunk_index: int


# ── Helpers ────────────────────────────────────────────────────────────────────

def _chunk_path(upload_id: str, index: int) -> Path:
    return settings.chunks_dir / upload_id / f"chunk_{index:05d}"


def _upload_id_is_valid(upload_id: str) -> bool:
    try:
        UUID(upload_id, version=4)
        return True
    except ValueError:
        return False


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/upload/chunk", response_model=ChunkResponse, status_code=200)
async def upload_chunk(
    chunk: UploadFile,
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    upload_id: str = Form(...),
    original_filename: str = Form(...),
) -> ChunkResponse:
    """Receive a single chunk of a multipart upload."""

    # Validate upload_id is a proper UUID
    if not _upload_id_is_valid(upload_id):
        raise HTTPException(status_code=400, detail="upload_id deve ser um UUID v4 válido")

    # Validate chunk index is within expected range
    if chunk_index < 0 or chunk_index >= total_chunks:
        raise HTTPException(
            status_code=400,
            detail=f"chunk_index {chunk_index} fora do intervalo [0, {total_chunks - 1}]",
        )

    # Build destination path (never trusting original_filename for the path)
    dest: Path = _chunk_path(upload_id, chunk_index)
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        async with aiofiles.open(dest, "wb") as f:
            while True:
                data = await chunk.read(1024 * 1024)  # 1 MB read buffer
                if not data:
                    break
                await f.write(data)
    except OSError as exc:
        logger.error("Falha ao salvar chunk %d para upload %s: %s", chunk_index, upload_id, exc)
        raise HTTPException(status_code=500, detail="Erro ao salvar chunk no disco") from exc

    logger.debug("Chunk %d/%d salvo para upload_id=%s", chunk_index + 1, total_chunks, upload_id)
    return ChunkResponse(received=True, chunk_index=chunk_index)


@router.post("/upload/finalize", response_model=FinalizeResponse, status_code=200)
async def finalize_upload(body: FinalizeRequest) -> FinalizeResponse:
    """Assemble chunks, validate MIME type, create session, return session_id."""

    upload_id = body.upload_id
    total_chunks = body.total_chunks

    if not _upload_id_is_valid(upload_id):
        raise HTTPException(status_code=400, detail="upload_id inválido")

    # 1. Verify every chunk is present
    missing: list[int] = []
    for i in range(total_chunks):
        if not _chunk_path(upload_id, i).exists():
            missing.append(i)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Chunks ausentes: {missing[:10]}{'...' if len(missing) > 10 else ''}",
        )

    # 2. Assemble chunks into a temporary file
    assembled_tmp = settings.chunks_dir / upload_id / "_assembled.mp4"
    try:
        async with aiofiles.open(assembled_tmp, "wb") as out_file:
            for i in range(total_chunks):
                chunk_file = _chunk_path(upload_id, i)
                async with aiofiles.open(chunk_file, "rb") as in_file:
                    while True:
                        data = await in_file.read(1024 * 1024)
                        if not data:
                            break
                        await out_file.write(data)
    except OSError as exc:
        logger.error("Erro ao montar arquivo para upload %s: %s", upload_id, exc)
        raise HTTPException(status_code=500, detail="Erro ao montar arquivo de vídeo") from exc

    # 3. Validate MIME type
    try:
        file_validator.validate_mime_type(str(assembled_tmp))
    except ValueError as exc:
        assembled_tmp.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # 4. Create session ID and move assembled file to uploads directory
    session_id = str(uuid4())
    stored_filename = f"{session_id}.mp4"
    final_video_path = settings.upload_dir / stored_filename

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(assembled_tmp), str(final_video_path))
    except OSError as exc:
        logger.error("Erro ao mover arquivo montado: %s", exc)
        raise HTTPException(status_code=500, detail="Erro ao armazenar vídeo") from exc

    # 5. Extract first frame for calibration UI
    session_dir = settings.sessions_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    first_frame_path = session_dir / "frame_first.jpg"

    try:
        frame_extractor.extract_first_frame(str(final_video_path), str(first_frame_path))
    except Exception as exc:
        logger.error("Erro ao extrair primeiro frame para sessão %s: %s", session_id, exc)
        # Non-fatal: calibration endpoint will surface a proper 404 if file is missing

    # 6. Persist session record
    session_store.create_session(
        session_id=session_id,
        original_filename=body.original_filename,
        stored_filename=stored_filename,
        field_width_m=body.field_width_m,
        field_height_m=body.field_height_m,
    )

    # 7. Clean up chunks directory for this upload
    chunk_dir = settings.chunks_dir / upload_id
    try:
        shutil.rmtree(str(chunk_dir), ignore_errors=True)
    except OSError as exc:
        logger.warning("Não foi possível limpar chunks para upload %s: %s", upload_id, exc)

    logger.info(
        "Upload finalizado: session_id=%s  arquivo=%s  campo=%.1fx%.1fm",
        session_id,
        stored_filename,
        body.field_width_m,
        body.field_height_m,
    )

    return FinalizeResponse(session_id=session_id, status="uploaded")
