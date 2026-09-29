import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Document:
    id: Optional[int] = None
    filename: str = ""
    filepath: str = ""
    file_size: int = 0
    total_pages: int = 0
    total_paragraphs: int = 0
    created_at: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "file_size": self.file_size,
            "total_pages": self.total_pages,
            "total_paragraphs": self.total_paragraphs,
            "created_at": self.created_at
        }


@dataclass
class Paragraph:
    id: Optional[int] = None
    document_id: int = 0
    page_number: int = 1
    paragraph_number: int = 1
    text: str = ""
    vector_id: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "paragraph_number": self.paragraph_number,
            "text": self.text,
            "vector_id": self.vector_id
        }
