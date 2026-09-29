from pydantic import BaseModel, Field
from datetime import datetime


class Document(BaseModel):
    """
    Represents an uploaded PDF document.
    """

    filename: str
    total_pages: int = 0
    uploaded_at: datetime = Field(
        default_factory=datetime.now
    )


class Paragraph(BaseModel):
    """
    Represents a processed paragraph extracted
    from a PDF document.
    """

    document_id: int
    page_number: int
    paragraph_number: int
    text: str


class ProcessedDocument(BaseModel):
    """
    Represents a complete processed PDF document
    and all of its paragraphs.
    """

    document: Document
    paragraphs: list[Paragraph] = []