from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

_BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Server ─────────────────────────────────────────────────────────────
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_reload: bool = True
    app_version: str = "1.0.0"

    # ── Storage roots ──────────────────────────────────────────────────────
    storage_root: Path = _BASE_DIR / "storage"

    @property
    def upload_dir(self) -> Path:
        return self.storage_root / "uploads"

    @property
    def chunks_dir(self) -> Path:
        return self.storage_root / "chunks"

    @property
    def sessions_dir(self) -> Path:
        return self.storage_root / "sessions"

    # ── Database ────────────────────────────────────────────────────────────
    db_path: Path = _BASE_DIR / "storage" / "sessions.db"

    # ── Processing ─────────────────────────────────────────────────────────
    prescan_frames: int = 300
    pipeline_fps: float = 5.0
    max_upload_size_mb: int = 2048

    # ── CORS ────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["*"]

    @field_validator("storage_root", "db_path", mode="before")
    @classmethod
    def _to_path(cls, v: object) -> Path:
        return Path(str(v))


settings = Settings()
