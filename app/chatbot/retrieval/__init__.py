"""
Retrieval package for the PDF chatbot.

This package is responsible for:

1. Searching the chatbot's vector database.
2. Retrieving relevant document chunks.
3. Building the context that will be provided to Ollama.
"""

from .retriever import Retriever
from .context_builder import ContextBuilder

__all__ = [
    "Retriever",
    "ContextBuilder",
]