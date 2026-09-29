"""
Embedding module for semantic search.
"""

from typing import List, Sequence
from ..core.embeddings import generate_embedding as core_generate_embedding, generate_embeddings as core_generate_embeddings


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for single text string.
    Raises ValueError if text is empty.
    """
    if not text or not isinstance(text, str) or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")
    return core_generate_embedding(text.strip())


def generate_embeddings(texts: Sequence[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple text strings.
    """
    if not texts:
        return []
    return core_generate_embeddings(texts)


__all__ = [
    "generate_embedding",
    "generate_embeddings",
]
