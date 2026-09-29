"""
ChromaDB vector store for the PDF chatbot.

This database is completely separate from the semantic-search
application.
"""

from pathlib import Path
from typing import Any

import chromadb

from ..config import VECTOR_DB_PATH


class VectorStore:
    """
    Persistent ChromaDB storage for chatbot document embeddings.
    """

    def __init__(
        self,
        persist_directory: str | Path = VECTOR_DB_PATH,
        collection_name: str = "chatbot_documents",
    ) -> None:

        self.persist_directory = Path(
            persist_directory
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "description":
                    "PDF chatbot document memory"
                },
            )
        )

    # ---------------------------------------------------------
    # Add documents
    # ---------------------------------------------------------

    def add_documents(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """
        Store document embeddings in ChromaDB.
        """

        if not ids:
            return

        if not (
            len(ids)
            == len(embeddings)
            == len(documents)
            == len(metadatas)
        ):
            raise ValueError(
                "ids, embeddings, documents and "
                "metadatas must have the same length."
            )

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> dict[str, Any]:
        """
        Search for documents similar to the query embedding.
        """

        if not query_embedding:
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "distances": [],
            }

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
        )

        return {
            "ids": (
                results.get("ids", [[]])[0]
            ),
            "documents": (
                results.get("documents", [[]])[0]
            ),
            "metadatas": (
                results.get("metadatas", [[]])[0]
            ),
            "distances": (
                results.get("distances", [[]])[0]
            ),
        }

    # ---------------------------------------------------------
    # Delete document
    # ---------------------------------------------------------

    def delete_document(
        self,
        document_id: int,
    ) -> None:
        """
        Delete all vectors belonging to a document.
        """

        self.collection.delete(
            where={
                "document_id": document_id
            }
        )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(self) -> int:
        """
        Return the number of vectors stored.
        """

        return self.collection.count()


# -------------------------------------------------------------
# Shared vector store instance and helper functions
# -------------------------------------------------------------

vector_store = VectorStore()


def add_documents(
    docs_or_ids: list[dict[str, Any]] | list[str],
    embeddings: list[list[float]] | None = None,
    documents: list[str] | None = None,
    metadatas: list[dict[str, Any]] | None = None,
) -> None:
    if isinstance(docs_or_ids, list) and docs_or_ids and isinstance(docs_or_ids[0], dict):
        ids = [str(d["id"]) for d in docs_or_ids]
        embs = [d["embedding"] for d in docs_or_ids]
        texts = [d["text"] for d in docs_or_ids]
        metas = [d.get("metadata", {}) for d in docs_or_ids]
        vector_store.add_documents(ids=ids, embeddings=embs, documents=texts, metadatas=metas)
    elif embeddings is not None and documents is not None and metadatas is not None:
        vector_store.add_documents(ids=docs_or_ids, embeddings=embeddings, documents=documents, metadatas=metadatas)