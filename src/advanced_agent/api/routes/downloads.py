# src/api/routes/downloads.py
import os
import re
import unicodedata
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

SAVED_DOCS_DIR = Path("saved_docs")
SAVED_SLIDES_DIR = Path("saved_slides")


def _find_file(filename: str) -> Path:
    """
    Look for the file in known base folders.
    """
    for base in (SAVED_DOCS_DIR, SAVED_SLIDES_DIR):
        candidate = base / filename
        if candidate.exists():
            return candidate
    raise HTTPException(status_code=404, detail="File not found")


def _ascii_download_name(filename: str) -> str:
    """
    Convert any filename (possibly with Chinese chars) into a safe ASCII name
    that can be used inside HTTP headers.
    """
    # Normalize and strip accents
    normalized = unicodedata.normalize("NFKD", filename)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")
    # Keep only [A-Za-z0-9_.-], replace others with "_"
    ascii_str = re.sub(r'[^A-Za-z0-9_.-]+', "_", ascii_str)
    # Fallback if everything got stripped
    return ascii_str or "download"


@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = _find_file(filename)
    suffix = file_path.suffix.lower()

    safe_name = _ascii_download_name(filename)

    # PDFs: inline so iframe/embed can render
    if suffix == ".pdf":
        return FileResponse(
            file_path,
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{safe_name}"'},
        )

    # TXT: inline, works for preview + browser view
    if suffix == ".txt":
        return FileResponse(
            file_path,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'inline; filename="{safe_name}"'},
        )

    # PPTX: download (browser can't preview natively in iframe)
    if suffix == ".pptx":
        return FileResponse(
            file_path,
            media_type=(
                "application/"
                "vnd.openxmlformats-officedocument.presentationml.presentation"
            ),
            headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
        )

    # Fallback for other extensions
    return FileResponse(
        file_path,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )