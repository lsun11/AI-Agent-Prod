# src/saving/core.py
import os
import re
import unicodedata
from datetime import datetime
from typing import Any

from .pdf_builder import build_pdf_document
from .docx_builder import build_docx_document
from .slides import save_result_slides as _save_result_slides
from typing import Optional, TypedDict


class SavedResultPaths(TypedDict):
    pdf: str
    txt: str
    docx: Optional[str]

def save_result_document_raw(query: str, result_text: str) -> SavedResultPaths:
    """
    Save the result in three formats:

    - Always: UTF-8 .txt
    - If python-docx is available: .docx
    - Always: .pdf

    Returns: path to the preferred file (pdf > docx > txt).
    """
    raw_summary = query.strip() or "research"

    normalized = unicodedata.normalize("NFKC", raw_summary)
    safe = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", normalized)
    safe = "_".join(safe.split())[:80]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    folder = "saved_docs"
    os.makedirs(folder, exist_ok=True)

    base = f"{safe}_{timestamp}"

    # 1) txt
    txt_path = os.path.join(folder, base + ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result_text)

    # 2) docx
    try:
        import docx  # noqa: F401
    except ImportError:
        docx_path = None
    else:
        docx_path = os.path.join(folder, base + ".docx")
        build_docx_document(docx_path, query, result_text)

    # 3) pdf
    pdf_path = os.path.join(folder, base + ".pdf")
    build_pdf_document(query, result_text, pdf_path)

    # Prefer pdf, then docx, then txt
    return {
        "pdf": pdf_path,
        "docx": docx_path,
        "txt": txt_path,
    }


def save_result_slides(query: str, result: Any) -> str:
    """Public wrapper around the PPTX saver."""
    return _save_result_slides(query, result)
