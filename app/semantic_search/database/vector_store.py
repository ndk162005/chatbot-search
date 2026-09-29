"""
ChromaDB vector store for semantic search.
"""

import chromadb
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..core.config import VECTOR_DB_PATH, CHROMA_COLLECTION_NAME


class VectorStore:
    """
    VectorStore class for managing ChromaDB collection.
    """

    def __init__(
        self,
        persist_directory: str | Path = VECTOR_DB_PATH,
        collection_name: str = CHROMA_COLLECTION_NAME,
    ) -> None:
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        try:
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        except Exception:
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def count(self) -> int:
        return self.collection.count()

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        document_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        if not query_embedding or self.count() == 0:
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}

        where_clause = {"document_id": document_id} if document_id is not None else None
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, max(self.count(), 1))
        }
        if where_clause:
            kwargs["where"] = where_clause

        try:
            res = self.collection.query(**kwargs)
            return {
                "ids": res.get("ids", [[]])[0],
                "documents": res.get("documents", [[]])[0],
                "metadatas": res.get("metadatas", [[]])[0],
                "distances": res.get("distances", [[]])[0],
            }
        except Exception:
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}


# Module instance for backward compatibility
_default_store = VectorStore()


def add_embeddings(records: List[Dict[str, Any]]):
    if not records:
        return
    ids = [str(item.get("id")) for item in records]
    documents = [item.get("text", "") for item in records]
    embeddings = [item.get("embedding", []) for item in records]
    metadatas = [{
        "document_id": int(item.get("document_id", 0)),
        "page_number": int(item.get("page_number", 1)),
        "paragraph_number": int(item.get("paragraph_number", 1))
    } for item in records]
    _default_store.add_documents(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def query_vectors(query_embedding: List[float], top_k: int = 5, document_id: Optional[int] = None) -> List[Dict[str, Any]]:
    res = _default_store.search(query_embedding=query_embedding, top_k=top_k, document_id=document_id)
    ids = res.get("ids", [])
    documents = res.get("documents", [])
    distances = res.get("distances", [])
    metadatas = res.get("metadatas", [])

    parsed_results = []
    for i in range(len(ids)):
        meta = metadatas[i] if i < len(metadatas) else {}
        parsed_results.append({
            "id": ids[i],
            "text": documents[i] if i < len(documents) else "",
            "distance": float(distances[i]) if i < len(distances) else 1.0,
            "document_id": meta.get("document_id", 0),
            "page_number": meta.get("page_number", 1),
            "paragraph_number": meta.get("paragraph_number", 1)
        })
    return parsed_results


def delete_vectors_by_document(document_id: int):
    try:
        _default_store.collection.delete(where={"document_id": document_id})
    except Exception:
        pass
