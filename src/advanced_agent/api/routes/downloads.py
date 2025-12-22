# src/api/routes/downloads.py
import os
import re
import unicodedata
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

SAVED_DOCS_DIR = Path("saved_docs")
SAVED_SLIDES_DIR = Path("saved_slides")

# Ensure they exist so listing doesn't crash
SAVED_DOCS_DIR.mkdir(parents=True, exist_ok=True)
SAVED_SLIDES_DIR.mkdir(parents=True, exist_ok=True)


def _find_file(filename: str) -> Path:
    """Look for the file in known base folders."""
    for base in (SAVED_DOCS_DIR, SAVED_SLIDES_DIR):
        candidate = base / filename
        if candidate.exists():
            return candidate
    raise HTTPException(status_code=404, detail="File not found")


def _ascii_download_name(filename: str) -> str:
    """Safe ASCII name for headers."""
    normalized = unicodedata.normalize("NFKD", filename)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_str = re.sub(r'[^A-Za-z0-9_.-]+', "_", ascii_str)
    return ascii_str or "download"


def _get_file_info(path: Path) -> Dict:
    """Helper to get file metadata for the frontend."""
    stat = path.stat()
    dt = datetime.fromtimestamp(stat.st_mtime)

    # Simple logic to determine "Today", "Yesterday", or Date
    now = datetime.now()
    if dt.date() == now.date():
        date_str = f"Today, {dt.strftime('%H:%M')}"
    elif (now.date() - dt.date()).days == 1:
        date_str = "Yesterday"
    else:
        date_str = dt.strftime("%b %d")

    return {
        "name": path.name,
        "type": "file",
        "ext": path.suffix.lstrip(".").lower(),
        "date": date_str,
        "size": stat.st_size
    }


def _scan_folder(folder: Path) -> List[Dict]:
    """Scans a directory and returns a list of file objects."""
    items = []
    if not folder.exists():
        return items

    # Sort by modification time (newest first)
    paths = sorted(folder.glob("*"), key=os.path.getmtime, reverse=True)

    for p in paths:
        if p.is_file() and not p.name.startswith("."):
            items.append(_get_file_info(p))
    return items


@router.get("/files/structure")
def get_file_structure():
    """
    Returns the virtual file system structure mapping real folders
    to the UI structure (AI Agent -> saved_docs / saved_slides).
    """
    docs = _scan_folder(SAVED_DOCS_DIR)
    slides = _scan_folder(SAVED_SLIDES_DIR)

    # Construct the specific tree for your UI
    structure = [
        {
            "name": "AI Agent",
            "type": "folder",
            "children": [
                {
                    "name": "saved_docs",
                    "type": "folder",
                    "children": docs
                },
                {
                    "name": "saved_slides",
                    "type": "folder",
                    "children": slides
                }
            ]
        },
        {
            "name": "Weather App",
            "type": "folder",
            "children": []  # Kept empty as requested
        }
    ]
    return structure


@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = _find_file(filename)
    suffix = file_path.suffix.lower()
    safe_name = _ascii_download_name(filename)

    # PDFs: inline for preview
    if suffix == ".pdf":
        return FileResponse(
            file_path,
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{safe_name}"'},
        )

    # TXT: inline for preview
    if suffix == ".txt":
        return FileResponse(
            file_path,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'inline; filename="{safe_name}"'},
        )

    # PPTX: download (attachment)
    if suffix == ".pptx":
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
        )

    # Fallback
    return FileResponse(
        file_path,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )

@router.delete("/files/delete/{filename}")
def delete_file(filename: str):
    """
    Deletes a file from saved_docs or saved_slides.
    """
    # 1. Security Check: Prevent path traversal (e.g. "../../../etc/passwd")
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # 2. Find the file
    try:
        file_path = _find_file(filename)
    except HTTPException:
        raise HTTPException(status_code=404, detail="File not found")

    # 3. Delete it
    try:
        os.remove(file_path)
        return {"status": "deleted", "file": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))