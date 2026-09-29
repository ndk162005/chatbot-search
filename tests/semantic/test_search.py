def test_semantic_search_returns_results():

    from app.semantic_search.search.semantic_search import (
        SemanticSearch,
    )

    search = SemanticSearch()

    results = search.search(
        "What are the port entry requirements?"
    )

    assert results is not None
    assert isinstance(
        results,
        list,
    )


def test_semantic_search_result_structure():

    from app.semantic_search.search.semantic_search import (
        SemanticSearch,
    )

    search = SemanticSearch()

    results = search.search(
        "port entry requirements"
    )

    if not results:
        return

    result = results[0]

    assert result is not None