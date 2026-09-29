import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from ..database.database import (
    get_all_documents,
    get_document_by_id,
    delete_document,
    get_db_connection
)
from ..database.vector_store import delete_vectors_by_document

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("")
async def list_documents():
    docs = get_all_documents()
    return {"count": len(docs), "documents": docs}


@router.get("/{doc_id}")
async def get_document(doc_id: int):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return doc


@router.get("/{doc_id}/paragraphs")
async def get_document_paragraphs(doc_id: int):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM paragraphs WHERE document_id = ? ORDER BY page_number, paragraph_number
    """, (doc_id,))
    rows = cursor.fetchall()
    conn.close()

    paragraphs = [dict(row) for row in rows]
    return {
        "document": doc,
        "count": len(paragraphs),
        "paragraphs": paragraphs
    }


@router.get("/{doc_id}/download")
async def download_document(doc_id: int):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    filepath = Path(doc["filepath"])
    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Physical PDF file was not found on server storage."
        )

    return FileResponse(
        path=filepath,
        filename=doc["filename"],
        media_type="application/pdf"
    )


@router.delete("/{doc_id}")
async def remove_document(doc_id: int):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    delete_vectors_by_document(doc_id)

    filepath = Path(doc["filepath"])
    if filepath.exists():
        try:
            filepath.unlink()
        except Exception:
            pass

    deleted = delete_document(doc_id)

    return {
        "success": deleted,
        "message": f"Successfully deleted document #{doc_id} ('{doc['filename']}')"
    }
