import time
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel
from ..search.semantic_search import semantic_search
from ..search.ranking import rank_results, get_top_results
from ..core.config import DEFAULT_TOP_K, MAX_TOP_K

router = APIRouter(prefix="/api", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = DEFAULT_TOP_K
    min_score: Optional[float] = 0.0
    document_id: Optional[int] = None


@router.post("/search")
async def execute_search(request: SearchRequest):
    return await _process_search(
        query=request.query,
        top_k=request.top_k or DEFAULT_TOP_K,
        min_score=request.min_score or 0.0,
        document_id=request.document_id
    )


@router.get("/search")
async def execute_search_get(
    q: str = Query(..., description="Semantic search query"),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=MAX_TOP_K),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    document_id: Optional[int] = Query(None)
):
    return await _process_search(
        query=q,
        top_k=top_k,
        min_score=min_score,
        document_id=document_id
    )


async def _process_search(query: str, top_k: int, min_score: float, document_id: Optional[int]):
    clean_query = query.strip()
    if not clean_query:
        return {
            "query": "",
            "total_results": 0,
            "results": [],
            "execution_time_ms": 0.0
        }

    start_time = time.time()

    raw_results = semantic_search(
        query=clean_query,
        top_k=max(top_k * 2, 10),
        document_id=document_id
    )

    ranked = rank_results(raw_results)
    filtered = [r for r in ranked if r.get("relevance_score", 0.0) >= min_score]
    final_results = get_top_results(filtered, top_k=top_k)

    exec_time = round((time.time() - start_time) * 1000, 2)

    return {
        "query": clean_query,
        "count": len(final_results),
        "total_results": len(final_results),
        "results": final_results,
        "execution_time_ms": exec_time
    }
