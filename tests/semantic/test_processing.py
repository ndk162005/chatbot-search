from pathlib import Path

import pytest


def test_pdf_exists():

    pdf_path = Path(
        "tests/data/sample.pdf"
    )

    if not pdf_path.exists():
        pytest.skip(
            "tests/data/sample.pdf not found."
        )

    assert pdf_path.is_file()
    assert pdf_path.suffix.lower() == ".pdf"


def test_pdf_extraction():

    from app.semantic_search.processing.pdf_extractor import (
        PDFExtractor,
    )

    pdf_path = Path(
        "tests/data/sample.pdf"
    )

    if not pdf_path.exists():
        pytest.skip(
            "tests/data/sample.pdf not found."
        )

    extractor = PDFExtractor()

    result = extractor.extract(
        pdf_path
    )

    assert result is not None
    assert len(result) > 0


def test_extracted_text_is_string():

    from app.semantic_search.processing.pdf_extractor import (
        PDFExtractor,
    )

    pdf_path = Path(
        "tests/data/sample.pdf"
    )

    if not pdf_path.exists():
        pytest.skip(
            "tests/data/sample.pdf not found."
        )

    extractor = PDFExtractor()

    result = extractor.extract(
        pdf_path
    )

    assert isinstance(
        result,
        str,
    )

    assert result.strip()