"""
Context builder for the PDF chatbot.

This module converts retrieved document chunks into a clean context
format that can be supplied to the LLM.
"""

from typing import Any


class ContextBuilder:
    """
    Builds document context from semantic retrieval results.
    """

    def __init__(self, max_chunks: int = 6) -> None:
        """
        Parameters
        ----------
        max_chunks:
            Maximum number of retrieved chunks to include in the
            final LLM context.
        """

        self.max_chunks = max_chunks

    def build_context(
        self,
        retrieved_chunks: list[dict[str, Any]],
    ) -> str:
        """
        Convert retrieved chunks into a formatted context string.

        Parameters
        ----------
        retrieved_chunks:
            List of chunks returned by the Retriever.

        Returns
        -------
        str
            Formatted document context for the LLM.
        """

        if not retrieved_chunks:
            return ""

        # Limit the amount of information sent to the LLM.
        chunks = retrieved_chunks[:self.max_chunks]

        context_parts = []

        for index, chunk in enumerate(chunks, start=1):

            filename = chunk.get(
                "filename",
                "Unknown document"
            )

            page_number = chunk.get(
                "page_number",
                "Unknown"
            )

            paragraph_number = chunk.get(
                "paragraph_number",
                "Unknown"
            )

            text = chunk.get(
                "text",
                ""
            )

            # Ignore empty chunks.
            if not text or not text.strip():
                continue

            formatted_chunk = (
                f"[Document Context {index}]\n"
                f"Document: {filename}\n"
                f"Page: {page_number}\n"
                f"Paragraph: {paragraph_number}\n"
                f"Content:\n"
                f"{text.strip()}\n"
            )

            context_parts.append(formatted_chunk)

        return "\n".join(context_parts)

    def build_context_records(
        self,
        retrieved_chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Return cleaned structured context records.

        This is useful when the API needs to return source information
        separately from the formatted LLM context.
        """

        if not retrieved_chunks:
            return []

        chunks = retrieved_chunks[:self.max_chunks]

        records = []

        for chunk in chunks:

            text = chunk.get("text", "")

            if not text or not text.strip():
                continue

            records.append(
                {
                    "document_id": chunk.get("document_id"),
                    "filename": chunk.get("filename"),
                    "page_number": chunk.get("page_number"),
                    "paragraph_number": chunk.get(
                        "paragraph_number"
                    ),
                    "text": text.strip(),
                    "score": chunk.get("score"),
                }
            )

        return records

    def build(
        self,
        retrieved_chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Build both the LLM context and source records.

        Returns
        -------
        dict
            {
                "context": "...",
                "sources": [...]
            }
        """

        return {
            "context": self.build_context(retrieved_chunks),
            "sources": self.build_context_records(
                retrieved_chunks
            ),
        }