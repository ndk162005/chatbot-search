"""
PDF text extraction for chatbot.
"""

from pathlib import Path
from typing import List, Dict, Any

from .pdf_ext import extract_pdf_text, PDFExtractionError, extract_non_empty_pages, get_pdf_page_count


class PDFExtractor:
    """
    Class wrapper for PDF extraction expected by unit tests and processing components.
    """

    def __init__(self) -> None:
        pass

    def extract(self, pdf_path: str | Path) -> str:
        """
        Extract full text from a PDF file as a single string.
        """
        pages = extract_pdf_text(pdf_path)
        return "\n\n".join(page["text"] for page in pages if page.get("text"))


__all__ = [
    "PDFExtractor",
    "extract_pdf_text",
    "PDFExtractionError",
    "extract_non_empty_pages",
    "get_pdf_page_count",
]
