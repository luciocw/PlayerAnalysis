from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config import settings
from services import pdf_generator, session_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sessions/{session_id}/export/pdf")
async def export_pdf(session_id: str) -> FileResponse:
    """
    Generate (or return cached) a PDF analysis report for the session.

    The PDF is cached at {sessions_dir}/{session_id}/report.pdf.
    Returns the file as an attachment download.
    """
    session: dict[str, Any] | None = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada")

    if session.get("status") != "done":
        raise HTTPException(
            status_code=422,
            detail=(
                "O relatório só pode ser exportado após o processamento completo. "
                f"Status atual: '{session.get('status')}'."
            ),
        )

    metrics_path: Path = settings.sessions_dir / session_id / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Arquivo de métricas não encontrado. O pipeline pode ter falhado.",
        )

    try:
        metrics: dict[str, Any] = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Erro ao ler metrics.json para exportação da sessão %s: %s", session_id, exc)
        raise HTTPException(status_code=500, detail="Erro ao ler arquivo de métricas") from exc

    pdf_path: Path = settings.sessions_dir / session_id / "report.pdf"

    if not pdf_path.exists():
        heatmap_path: Path = settings.sessions_dir / session_id / "heatmap.png"
        try:
            pdf_generator.generate_pdf(
                session_id=session_id,
                session=session,
                metrics=metrics,
                output_path=str(pdf_path),
                heatmap_path=str(heatmap_path) if heatmap_path.exists() else None,
            )
            logger.info("PDF gerado para sessão %s em %s", session_id, pdf_path)
        except Exception as exc:
            logger.error("Erro ao gerar PDF para sessão %s: %s", session_id, exc)
            raise HTTPException(status_code=500, detail="Erro ao gerar relatório PDF") from exc

    today_str = date.today().strftime("%Y-%m-%d")
    download_name = f"analise-{today_str}.pdf"

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=download_name,
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )
