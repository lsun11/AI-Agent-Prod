# src/save_utils.py
"""
Compatibility wrapper for the old save_utils module.

Existing imports like:
    from save_utils import save_result_document_raw, save_result_slides, format_result_text

will continue to work.
"""

from .saving import (
    format_result_text,
    save_result_document_raw,
    save_result_slides,
)

__all__ = [
    "format_result_text",
    "save_result_document_raw",
    "save_result_slides",
]


