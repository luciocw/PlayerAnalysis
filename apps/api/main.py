from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from routers import calibration, export, metrics, players, processing, sessions, upload
from services import session_store

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Foothub API v%s", settings.app_version)

    # Ensure all storage directories exist
    dirs: list[Path] = [
        settings.upload_dir,
        settings.chunks_dir,
        settings.sessions_dir,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        logger.info("Storage directory ready: %s", d)

    # Initialise SQLite database
    session_store.init_db()
    logger.info("Session database initialised at %s", settings.db_path)

    yield

    logger.info("Shutting down Foothub API")


# ── Application factory ────────────────────────────────────────────────────────
app = FastAPI(
    title="Foothub Futsal Analysis API",
    version=settings.app_version,
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ───────────────────────────────────────────────────────────────
# Served under /storage so the frontend can display heatmaps and thumbnails
# without a round-trip through Python.  The directory is created on startup.
app.mount(
    "/storage",
    StaticFiles(directory=str(settings.storage_root), html=False),
    name="storage",
)

# ── Routers ────────────────────────────────────────────────────────────────────
_PREFIX = "/api"

app.include_router(upload.router, prefix=_PREFIX, tags=["upload"])
app.include_router(sessions.router, prefix=_PREFIX, tags=["sessions"])
app.include_router(calibration.router, prefix=_PREFIX, tags=["calibration"])
app.include_router(players.router, prefix=_PREFIX, tags=["players"])
app.include_router(processing.router, prefix=_PREFIX, tags=["processing"])
app.include_router(metrics.router, prefix=_PREFIX, tags=["metrics"])
app.include_router(export.router, prefix=_PREFIX, tags=["export"])


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}
