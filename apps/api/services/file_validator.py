from __future__ import annotations

import os
import re
from uuid import uuid4

ALLOWED_MIME_TYPES: set[str] = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
}

MAX_FILE_SIZE_BYTES: int = 4 * 1024 * 1024 * 1024  # 4 GB

_ALLOWED_EXTENSIONS: set[str] = {".mp4", ".mov", ".avi"}
_SAFE_CHARS = re.compile(r"[^a-zA-Z0-9._\-]")


def sanitize_filename(filename: str) -> str:
    basename = os.path.basename(filename)
    _SAFE_CHARS.sub("_", basename)
    return f"{uuid4()}.mp4"


def validate_file_size(file_size: int) -> None:
    if file_size > MAX_FILE_SIZE_BYTES:
        limit_gb = MAX_FILE_SIZE_BYTES / (1024 ** 3)
        raise ValueError(
            f"File size {file_size} bytes exceeds maximum allowed {limit_gb:.0f} GB."
        )


def validate_mime_type(file_path: str) -> None:
    try:
        import magic  # type: ignore

        mime = magic.from_file(file_path, mime=True)
        if mime not in ALLOWED_MIME_TYPES:
            raise ValueError(
                f"Unsupported file type '{mime}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
            )
        return
    except ImportError:
        pass

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension '{ext}'. "
            f"Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}"
        )
