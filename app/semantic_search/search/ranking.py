"""
Result ranking module for semantic search.
"""

def distance_to_score(
    distance: float
) -> float:
    """
    Convert vector distance into a relevance score.
    Smaller distance means greater similarity.
    """
    if distance < 0:
        distance = 0.0

    score = 1.0 / (1.0 + distance)
    return round(score, 4)


def rank_results(
    results: list[dict],
    min_score: float = 0.0
) -> list[dict]:
    """
    Rank search results by score in descending order.
    """
    if not results:
        return []

    ranked_results = []

    for result in results:
        ranked_result = result.copy()

        if "score" in result:
            score = float(result["score"])
        elif "relevance_score" in result:
            score = float(result["relevance_score"])
        else:
            distance = float(result.get("distance", 0.0))
            score = distance_to_score(distance)

        if score < min_score:
            continue

        ranked_result["score"] = score
        ranked_result["relevance_score"] = score
        ranked_results.append(ranked_result)

    # Sort descending by score
    ranked_results.sort(
        key=lambda r: r["score"],
        reverse=True
    )

    return ranked_results


def get_top_results(
    results: list[dict],
    top_k: int = 5,
    min_score: float = 0.0
) -> list[dict]:
    ranked = rank_results(results, min_score=min_score)
    return ranked[:top_k]