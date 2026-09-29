"""
Document processor for semantic search.
"""

from typing import Any, List, Union
from .doc_process import clean_text, split_into_paragraphs, process_document as base_process_document


class DocumentProcessor:
    """
    Class wrapper for processing text or pages for semantic search.
    """

    def __init__(self) -> None:
        pass

    def process(self, input_data: Union[str, List[dict]]) -> List[Any]:
        if isinstance(input_data, str):
            cleaned = clean_text(input_data)
            return split_into_paragraphs(cleaned)
        elif isinstance(input_data, list):
            return base_process_document(input_data)
        return []


def process_document(pages: list[dict]) -> list[dict]:
    return base_process_document(pages)


__all__ = [
    "DocumentProcessor",
    "process_document",
    "clean_text",
    "split_into_paragraphs",
]
