# app/chatbot/processing/pdf_extractor.py

from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF


class PDFExtractionError(Exception):
    """Raised when PDF text extraction fails."""
    pass


def extract_pdf_text(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text from every page of a PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A list of dictionaries containing:
            - page_number
            - text

        Example:
        [
            {
                "page_number": 1,
                "text": "Text from page 1..."
            },
            {
                "page_number": 2,
                "text": "Text from page 2..."
            }
        ]

    Raises:
        FileNotFoundError:
            If the PDF does not exist.

        ValueError:
            If the supplied file is not a PDF.

        PDFExtractionError:
            If the PDF cannot be opened or processed.
    """

    pdf_path = Path(pdf_path)

    # ---------------------------------------------------------
    # Validate file
    # ---------------------------------------------------------

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"Provided path is not a file: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, got: {pdf_path.suffix}"
        )

    extracted_pages: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # Open PDF
    # ---------------------------------------------------------

    try:
        document = fitz.open(pdf_path)

    except Exception as exc:
        raise PDFExtractionError(
            f"Unable to open PDF: {pdf_path}"
        ) from exc

    # ---------------------------------------------------------
    # Extract page text
    # ---------------------------------------------------------

    try:

        for page_index, page in enumerate(document):

            # PyMuPDF page numbers are zero-indexed internally.
            # We expose human-readable page numbers starting at 1.
            page_number = page_index + 1

            text = page.get_text("text")

            if text is None:
                text = ""

            # Normalize basic whitespace.
            text = text.replace("\x00", "").strip()

            extracted_pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    except Exception as exc:
        raise PDFExtractionError(
            f"Failed while extracting text from: {pdf_path}"
        ) from exc

    finally:
        document.close()

    return extracted_pages


def extract_non_empty_pages(
    pdf_path: str | Path,
) -> List[Dict[str, Any]]:
    """
    Extract only pages that contain text.

    Args:
        pdf_path: Path to the PDF.

    Returns:
        List of non-empty pages.
    """

    pages = extract_pdf_text(pdf_path)

    return [
        page
        for page in pages
        if page["text"].strip()
    ]


def get_pdf_page_count(pdf_path: str | Path) -> int:
    """
    Return the total number of pages in a PDF.

    Args:
        pdf_path: Path to the PDF.

    Returns:
        Number of pages.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    try:
        document = fitz.open(pdf_path)
        page_count = len(document)
        document.close()

        return page_count

    except Exception as exc:
        raise PDFExtractionError(
            f"Unable to determine page count: {pdf_path}"
        ) from exc