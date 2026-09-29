def test_ranking_orders_results():

    from app.semantic_search.search.ranking import (
        rank_results,
    )

    results = [
        {
            "text": "Low relevance result",
            "score": 0.40,
        },
        {
            "text": "Highly relevant result",
            "score": 0.95,
        },
        {
            "text": "Medium relevance result",
            "score": 0.70,
        },
    ]

    ranked = rank_results(
        results
    )

    assert ranked is not None

    assert (
        ranked[0]["score"]
        >= ranked[1]["score"]
    )

    assert (
        ranked[1]["score"]
        >= ranked[2]["score"]
    )


def test_ranking_empty_results():

    from app.semantic_search.search.ranking import (
        rank_results,
    )

    result = rank_results([])

    assert result == []