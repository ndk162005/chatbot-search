"""
Document retrieval module for the chatbot.

This module searches the chatbot's vector store and returns
the most relevant document chunks for a user's question.
"""

from typing import Any

from app.chatbot.database.vector_store import VectorStore
from app.chatbot.embeddings.embedding import EmbeddingGenerator


class Retriever:
    """
    Retrieves relevant document chunks using semantic similarity.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
        top_k: int = 5,
    ) -> None:
        """
        Initialize the retriever.

        Parameters
        ----------
        vector_store:
            Chatbot vector database interface.

        embedding_generator:
            Generates embeddings for user queries.

        top_k:
            Number of relevant chunks to retrieve.
        """

        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve document chunks relevant to the query.

        Parameters
        ----------
        query:
            User's natural-language question.

        top_k:
            Optional number of results to retrieve.

        Returns
        -------
        list[dict]
            Relevant document chunks with metadata and similarity
            information.
        """

        if not query or not query.strip():
            return []

        query = query.strip()

        number_of_results = top_k or self.top_k

        # ---------------------------------------------------------
        # 1. Convert the user's question into an embedding
        # ---------------------------------------------------------

        query_embedding = self.embedding_generator.generate_embedding(
            query
        )

        # ---------------------------------------------------------
        # 2. Search the chatbot vector database
        # ---------------------------------------------------------

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=number_of_results,
        )

        # ---------------------------------------------------------
        # 3. Normalize the returned results
        # ---------------------------------------------------------

        return self._normalize_results(results)

    @staticmethod
    def _normalize_results(
        results: Any,
    ) -> list[dict[str, Any]]:
        """
        Convert vector-store results into a consistent structure.
        """

        if not results:
            return []

        normalized_results: list[dict[str, Any]] = []

        # ChromaDB commonly returns a structure such as:
        #
        # {
        #     "ids": [[...]],
        #     "documents": [[...]],
        #     "metadatas": [[...]],
        #     "distances": [[...]]
        # }

        ids = results.get("ids", [[]])
        documents = results.get("documents", [[]])
        metadatas = results.get("metadatas", [[]])
        distances = results.get("distances", [[]])

        ids = ids[0] if ids else []
        documents = documents[0] if documents else []
        metadatas = metadatas[0] if metadatas else []
        distances = distances[0] if distances else []

        for index, document_id in enumerate(ids):

            document_text = (
                documents[index]
                if index < len(documents)
                else ""
            )

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            normalized_results.append(
                {
                    "id": document_id,
                    "text": document_text,
                    "document_id": metadata.get("document_id"),
                    "filename": metadata.get("filename"),
                    "page_number": metadata.get("page_number"),
                    "paragraph_number": metadata.get(
                        "paragraph_number"
                    ),
                    "distance": distance,
                }
            )

        return normalized_results

    def retrieve_for_chat(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve document context specifically for chatbot use.

        This is a convenience wrapper around retrieve().
        """

        results = self.retrieve(
            query=query,
            top_k=top_k,
        )

        return results