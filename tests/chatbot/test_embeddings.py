import pytest


def test_embedding_generation():
    """
    Verify that text can be converted into an embedding.
    """

    from app.chatbot.embeddings.embedding import (
        generate_embedding,
    )

    embedding = generate_embedding(
        "This is a test sentence."
    )

    assert embedding is not None
    assert len(embedding) > 0


def test_embedding_values_are_numeric():
    """
    Verify that embedding values are numeric.
    """

    from app.chatbot.embeddings.embedding import (
        generate_embedding,
    )

    embedding = generate_embedding(
        "Semantic search test."
    )

    assert all(
        isinstance(value, (int, float))
        for value in embedding
    )


def test_empty_text_is_rejected():
    """
    Empty text should not generate an embedding.
    """

    from app.chatbot.embeddings.embedding import (
        generate_embedding,
    )

    with pytest.raises(
        ValueError
    ):
        generate_embedding("")