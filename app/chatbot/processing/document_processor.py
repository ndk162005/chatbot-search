"""
Document processor module for chatbot.
"""

from typing import Any, List, Union, Dict
from .doc_proess import DocumentProcessor as BaseDocumentProcessor, process_document as base_process_document


class DocumentProcessor(BaseDocumentProcessor):
    """
    Extended DocumentProcessor supporting string or list of pages for process().
    """

    def process(self, input_data: Union[str, List[Dict[str, Any]]]) -> List[Any]:
        """
        Process input text (str) or pages (list of dicts) into usable text chunks.
        """
        if isinstance(input_data, str):
            paragraphs = self.split_into_paragraphs(input_data)
            chunks: List[str] = []
            for p in paragraphs:
                sub_chunks = self.chunk_text(p)
                chunks.extend(sub_chunks)
            return [c for c in chunks if c and c.strip()]
        elif isinstance(input_data, list):
            return self.process_document(input_data)
        return []


def process_document(
    pages: Union[str, List[Dict[str, Any]]],
    document_id: int | None = None,
    filename: str | None = None,
) -> List[Any]:
    processor = DocumentProcessor()
    if isinstance(pages, str):
        return processor.process(pages)
    return processor.process_document(pages, document_id=document_id, filename=filename)


__all__ = [
    "DocumentProcessor",
    "process_document",
]
