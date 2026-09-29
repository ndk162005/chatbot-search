def test_complete_semantic_search_pipeline():

    """
    Test:

    User query
        ↓
    Embedding
        ↓
    Vector search
        ↓
    Ranking
        ↓
    Results
    """

    from app.semantic_search.search.semantic_search import (
        SemanticSearch,
    )

    search = SemanticSearch()

    results = search.search(
        "What are the requirements for port entry?"
    )

    assert results is not None
    assert isinstance(
        results,
        list,
    )

    if results:

        first_result = results[0]

        assert first_result is not None


def test_semantic_search_top_k():

    from app.semantic_search.search.semantic_search import (
        SemanticSearch,
    )

    search = SemanticSearch()

    results = search.search(
        "port entry requirements",
        top_k=3,
    )

    assert len(results) <= 3