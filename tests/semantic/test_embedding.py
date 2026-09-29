def test_embedding_generation():

    from app.semantic_search.embeddings.embedding import (
        generate_embedding,
    )

    embedding = generate_embedding(
        "Port entry requirements"
    )

    assert embedding is not None
    assert len(embedding) > 0


def test_embedding_contains_numbers():

    from app.semantic_search.embeddings.embedding import (
        generate_embedding,
    )

    embedding = generate_embedding(
        "The vessel must submit documentation."
    )

    assert all(
        isinstance(
            value,
            (int, float),
        )
        for value in embedding
    )


def test_same_text_has_same_dimension():

    from app.semantic_search.embeddings.embedding import (
        generate_embedding,
    )

    embedding_1 = generate_embedding(
        "Port entry requirements"
    )

    embedding_2 = generate_embedding(
        "Vessel documentation"
    )

    assert len(embedding_1) == len(
        embedding_2
    )


def test_empty_text_is_rejected():

    import pytest

    from app.semantic_search.embeddings.embedding import (
        generate_embedding,
    )

    with pytest.raises(
        ValueError
    ):
        generate_embedding("")