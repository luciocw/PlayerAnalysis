from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "storage/sessions.db"

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    original_name TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    status TEXT DEFAULT 'uploaded',
    created_at TEXT NOT NULL,
    field_width_m REAL DEFAULT 40.0,
    field_height_m REAL DEFAULT 20.0,
    homography_matrix TEXT,
    selected_track_id INTEGER,
    error_message TEXT,
    duration_seconds REAL
)
"""

_UPDATABLE_FIELDS = {
    "original_name",
    "stored_filename",
    "status",
    "field_width_m",
    "field_height_m",
    "homography_matrix",
    "selected_track_id",
    "error_message",
    "duration_seconds",
}


def _get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    with _get_connection(db_path) as conn:
        conn.execute(_CREATE_TABLE_SQL)
        conn.commit()


def create_session(
    session_id: str,
    original_name: str,
    stored_filename: str,
    db_path: str = DB_PATH,
) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    with _get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sessions (id, original_name, stored_filename, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, original_name, stored_filename, created_at),
        )
        conn.commit()


def get_session(
    session_id: str, db_path: str = DB_PATH
) -> Optional[dict]:
    with _get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()

    if row is None:
        return None

    result = dict(row)
    if result.get("homography_matrix"):
        try:
            result["homography_matrix"] = json.loads(result["homography_matrix"])
        except (json.JSONDecodeError, TypeError):
            pass
    return result


def update_session(
    session_id: str, db_path: str = DB_PATH, **kwargs: object
) -> None:
    fields = {k: v for k, v in kwargs.items() if k in _UPDATABLE_FIELDS}
    if not fields:
        return

    if "homography_matrix" in fields and not isinstance(
        fields["homography_matrix"], str
    ):
        fields["homography_matrix"] = json.dumps(fields["homography_matrix"])

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [session_id]

    with _get_connection(db_path) as conn:
        conn.execute(
            f"UPDATE sessions SET {set_clause} WHERE id = ?",
            values,
        )
        conn.commit()


def list_sessions(db_path: str = DB_PATH) -> list[dict]:
    with _get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY created_at DESC"
        ).fetchall()

    sessions = []
    for row in rows:
        record = dict(row)
        if record.get("homography_matrix"):
            try:
                record["homography_matrix"] = json.loads(record["homography_matrix"])
            except (json.JSONDecodeError, TypeError):
                pass
        sessions.append(record)

    return sessions


def session_exists(session_id: str, db_path: str = DB_PATH) -> bool:
    with _get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    return row is not None
