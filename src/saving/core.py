# src/saving/core.py
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict  # <- moved Optional, TypedDict here

from .pdf_builder import build_pdf_document
from .docx_builder import build_docx_document
from .slides import _save_result_slides


class SavedResultPaths(TypedDict):
    pdf: str
    txt: str
    docx: Optional[str]


def save_result_document_raw(
    query: str,
    result_text: str,
    flowchart_png_path: Optional[str] = None,  # 🔹 NEW
) -> Dict[str, str]:
    """
    Save the result in three formats:

    - Always: UTF-8 .txt
    - If python-docx is available: .docx
    - Always: .pdf

    Returns: dict with paths {"pdf": ..., "docx": ..., "txt": ...}
    """
    # ✅ use the original query for filename base
    raw_summary = query.strip() or "research"

    # Normalize unicode so Chinese characters are preserved
    normalized = unicodedata.normalize("NFKC", raw_summary)

    # Replace any invalid filename characters with "_"
    safe = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", normalized)

    # Trim and collapse spaces
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
        docx_path: Optional[str] = None
    else:
        docx_path = os.path.join(folder, base + ".docx")
        build_docx_document(docx_path, query, result_text)

    # 3) pdf
    pdf_path = os.path.join(folder, base + ".pdf")
    # 🔹 pass the optional flowchart path into the PDF builder
    build_pdf_document(query, result_text, pdf_path, flowchart_png_path=flowchart_png_path)

    return {
        "pdf": pdf_path,
        "docx": docx_path,
        "txt": txt_path,
    }


def save_result_slides(
    output_path: str | Path,
    layout: Any,
    flowchart_png_path: Optional[str] = None,
) -> None:
    """
    Thin wrapper that delegates to the layout-based PPTX builder in slides.py.

    This keeps the `src.saving.core.save_result_slides` name working for callers
    (like generate_files.write_slides), but the real logic lives in slides.py.
    """
    return _save_result_slides(
        output_path=output_path,
        layout=layout,
        flowchart_png_path=flowchart_png_path,
    )

