"""
Document management API connected to SQLite and ChromaDB vector store.
"""

from typing import Any
from fastapi import APIRouter, HTTPException

from app.chatbot.database.database import database
from app.chatbot.database.vector_store import vector_store


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


@router.get("")
def get_documents() -> dict[str, Any]:
    """
    Return all uploaded documents from SQLite database.
    """
    try:
        docs = database.list_documents()
        return {
            "documents": docs,
            "count": len(docs),
        }
    except Exception as error:
        return {
            "documents": [],
            "count": 0,
            "error": str(error),
        }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
) -> dict[str, Any]:
    """
    Delete document from SQLite, ChromaDB, and return confirmation.
    """
    try:
        # Delete vectors from ChromaDB
        try:
            vector_store.delete_document(document_id)
        except Exception:
            pass

        # Delete record from SQLite
        deleted = database.delete_document(document_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {document_id} not found.",
            )

        return {
            "success": True,
            "document_id": document_id,
            "message": "Document deleted successfully.",
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error