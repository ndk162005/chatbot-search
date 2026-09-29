"""
PDF extractor for semantic search.
"""

from pathlib import Path
from typing import List, Dict, Any
from .pdf_ext import extract_pdf_text


class PDFExtractor:
    """
    Class wrapper for PDF text extraction.
    """

    def __init__(self) -> None:
        pass

    def extract(self, pdf_path: str | Path) -> str:
        pages = extract_pdf_text(str(pdf_path))
        return "\n\n".join(p["text"] for p in pages if p.get("text"))


__all__ = [
    "PDFExtractor",
    "extract_pdf_text",
]
