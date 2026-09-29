def test_context_builder_empty_result():
    """
    Empty retrieval results should produce
    empty context.
    """

    from app.chatbot.retrieval.context_builder import (
        ContextBuilder,
    )

    builder = ContextBuilder()

    result = builder.build(
        []
    )

    assert result["context"] == ""
    assert result["sources"] == []


def test_context_builder():
    """
    Verify retrieved chunks are converted
    into LLM context.
    """

    from app.chatbot.retrieval.context_builder import (
        ContextBuilder,
    )

    builder = ContextBuilder()

    chunks = [
        {
            "document_id": 1,
            "filename": "sample.pdf",
            "page_number": 5,
            "paragraph_number": 2,
            "text": "The vessel must submit documentation.",
            "score": 0.95,
        }
    ]

    result = builder.build(
        chunks
    )

    assert "sample.pdf" in result["context"]
    assert "Page: 5" in result["context"]
    assert (
        "The vessel must submit documentation."
        in result["context"]
    )

    assert len(result["sources"]) == 1