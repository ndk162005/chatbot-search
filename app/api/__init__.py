"""
API package for the PDF AI application.
"""

from .query import router as query_router
from .upload import router as upload_router
from .document import router as documents_router

__all__ = [
    "query_router",
    "upload_router",
    "documents_router",
]