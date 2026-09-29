from pathlib import Path

import pytest


def test_pdf_file_exists():
    """
    Verify that the test PDF exists.
    """

    pdf_path = Path("tests/data/sample.pdf")

    if not pdf_path.exists():
        pytest.skip(
            "tests/data/sample.pdf not available."
        )

    assert pdf_path.is_file()
    assert pdf_path.suffix.lower() == ".pdf"


def test_pdf_extraction_returns_text():
    """
    Verify that PDF extraction produces text.
    """

    from app.chatbot.processing.pdf_extractor import (
        PDFExtractor,
    )

    pdf_path = Path("tests/data/sample.pdf")

    if not pdf_path.exists():
        pytest.skip(
            "tests/data/sample.pdf not available."
        )

    extractor = PDFExtractor()

    result = extractor.extract(
        pdf_path
    )

    assert result is not None
    assert len(result) > 0


def test_document_processor_creates_chunks():
    """
    Verify that document processing creates
    usable text chunks.
    """

    from app.chatbot.processing.document_processor import (
        DocumentProcessor,
    )

    processor = DocumentProcessor()

    text = """
    This is the first paragraph.

    This is the second paragraph.

    This is the third paragraph.
    """

    result = processor.process(text)

    assert result is not None
    assert len(result) > 0

    for chunk in result:
        assert chunk