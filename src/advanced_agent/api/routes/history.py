# src/api/routes/history.py
from typing import List
from fastapi import APIRouter, Query
from ...history.store import list_history, clear_all_history_entries

router = APIRouter()


@router.post("/history/clear")
def clear_history():
    clear_all_history_entries()  # <- your storage helper
    return {"ok": True}

@router.get("/history")
def get_history(limit: int = Query(20, ge=1, le=100)) -> List[dict]:
    """
    Return most recent history entries.
    Each entry looks like:
    {
      "id": "...",
      "query": "...",
      "topic": "...",
      "language": "Eng" | "Chn",
      "created_at": "...",
      "download_pdf_url": "...",
      "download_docx_url": "...",
      "download_txt_url": "...",
      "slides_download_url": "..."
    }
    """
    return list_history(limit=limit)
