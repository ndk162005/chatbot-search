"""
Semantic search pipeline.
"""

from typing import List, Dict, Any, Optional
from ..core.embeddings import generate_embedding
from ..database.vector_store import query_vectors
from ..database.database import get_document_by_id
from .ranking import rank_results


class SemanticSearch:
    """
    Class wrapper for Semantic Search.
    """

    def __init__(self) -> None:
        pass

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return semantic_search(query=query, top_k=top_k, document_id=document_id)


def semantic_search(
    query: str,
    top_k: int = 5,
    document_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    if not query or not query.strip():
        return []

    query_embedding = generate_embedding(query.strip())
    raw_results = query_vectors(query_embedding=query_embedding, top_k=top_k, document_id=document_id)

    enriched_results = []
    doc_cache = {}

    for res in raw_results:
        doc_id = res.get("document_id")
        doc_info = None
        if doc_id:
            if doc_id not in doc_cache:
                doc_cache[doc_id] = get_document_by_id(doc_id)
            doc_info = doc_cache[doc_id]

        res_copy = dict(res)
        if doc_info:
            res_copy["filename"] = doc_info.get("filename", f"Document #{doc_id}")
            res_copy["filepath"] = doc_info.get("filepath", "")
        else:
            res_copy["filename"] = f"Document #{doc_id}" if doc_id else "Uploaded Document"

        enriched_results.append(res_copy)

    ranked = rank_results(enriched_results)
    return ranked[:top_k]
