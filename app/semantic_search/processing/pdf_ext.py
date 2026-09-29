import fitz
from pathlib import Path


def extract_pdf_text(pdf_path: str):
    """
    Extract text from every page of a PDF.

    Returns:
        list[dict]: page-wise extracted text
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("The uploaded file must be a PDF.")

    document = fitz.open(pdf_path)

    pages = []

    try:
        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text")

            pages.append({
                "page_number": page_number,
                "text": text.strip()
            })

    finally:
        document.close()

    return pages