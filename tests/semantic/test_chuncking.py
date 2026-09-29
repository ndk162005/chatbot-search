def test_chunking_produces_chunks():

    from app.semantic_search.processing.document_processor import (
        DocumentProcessor,
    )

    processor = DocumentProcessor()

    text = """
    The vessel must submit the required
    documentation before entering the port.

    The master must also provide the vessel
    information to the port authority.

    Additional clearance requirements may
    apply depending on the vessel type.
    """

    chunks = processor.process(
        text
    )

    assert chunks is not None
    assert len(chunks) > 0


def test_chunks_are_not_empty():

    from app.semantic_search.processing.document_processor import (
        DocumentProcessor,
    )

    processor = DocumentProcessor()

    text = """
    First paragraph containing information.

    Second paragraph containing information.

    Third paragraph containing information.
    """

    chunks = processor.process(
        text
    )

    for chunk in chunks:

        assert chunk is not None
        assert str(chunk).strip()


def test_chunking_preserves_information():

    from app.semantic_search.processing.document_processor import (
        DocumentProcessor,
    )

    processor = DocumentProcessor()

    text = """
    PORT ENTRY REQUIREMENTS

    The vessel must submit documentation
    before entering the port.
    """

    chunks = processor.process(
        text
    )

    combined = " ".join(
        str(chunk)
        for chunk in chunks
    )

    assert "PORT ENTRY" in combined
    assert "documentation" in combined