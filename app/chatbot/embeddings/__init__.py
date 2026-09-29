"""
Embedding package for the PDF chatbot.

This package provides functionality for converting text into
vector embeddings using a Sentence Transformer model.
"""

from .embedding import (
    EmbeddingModel,
    generate_embedding,
    generate_embeddings,
)

__all__ = [
    "EmbeddingModel",
    "generate_embedding",
    "generate_embeddings",
]