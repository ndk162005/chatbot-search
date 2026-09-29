"""
Database models for the PDF chatbot.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Document:
    """
    Represents an uploaded PDF document.
    """

    id: Optional[int] = None
    filename: str = ""
    total_pages: int = 0
    uploaded_at: Optional[datetime] = None


@dataclass
class Paragraph:
    """
    Represents a processed PDF paragraph/chunk.
    """

    id: Optional[int] = None
    document_id: int = 0
    page_number: int = 0
    paragraph_number: int = 0
    text: str = ""