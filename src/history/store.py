# src/history/store.py
from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

HISTORY_DB_PATH = Path("saved_docs") / "history.json"
_HISTORY_LOCK = threading.Lock()


@dataclass
class HistoryEntry:
    """
    One past run of the research agent.
    Stored in a simple JSON list: [ { ... }, ... ]
    """

    id: str
    query: str
    topic: Optional[str]
    language: str
    created_at: str  # ISO8601
    download_pdf_url: Optional[str]
    download_docx_url: Optional[str]
    download_txt_url: Optional[str]
    slides_download_url: Optional[str]

    # You can extend with more fields if you like:
    # companies_visual, resources_visual, model, temperature, etc.


def _load_all() -> List[Dict[str, Any]]:
    if not HISTORY_DB_PATH.exists():
        return []
    try:
        raw = HISTORY_DB_PATH.read_text(encoding="utf-8")
        if not raw.strip():
            return []
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        # Corrupted file? Don't crash the app—just reset.
        return []


def _save_all(entries: List[Dict[str, Any]]) -> None:
    HISTORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_DB_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def add_history_entry(entry: HistoryEntry) -> None:
    """
    Append a new entry to history.json (thread-safe).
    """
    with _HISTORY_LOCK:
        entries = _load_all()
        entries.append(asdict(entry))
        _save_all(entries)


def list_history(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Return most recent N history entries (newest first).
    """
    entries = _load_all()

    # Sort by created_at desc if present
    def key_fn(e: Dict[str, Any]) -> str:
        return e.get("created_at") or ""

    entries_sorted = sorted(entries, key=key_fn, reverse=True)
    return entries_sorted[:limit]

def clear_all_history_entries() -> None:
    """
    Remove all history entries (thread-safe).
    """
    with _HISTORY_LOCK:
        _save_all([])