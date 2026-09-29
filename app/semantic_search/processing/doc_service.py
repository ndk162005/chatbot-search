from datetime import datetime

from app.processing.pdf_extractor import extract_pdf_text
from app.processing.document_processor import process_document

from app.database.database import (
    insert_document,
    insert_paragraphs
)

from app.core.embeddings import generate_embeddings

from app.database.vector_store import add_embeddings


def process_uploaded_pdf(
    pdf_path: str,
    filename: str
) -> dict:
    """
    Complete PDF processing pipeline.

    PDF
      ↓
    Text extraction
      ↓
    Paragraph processing
      ↓
    SQLite
      ↓
    Embeddings
      ↓
    ChromaDB
    """

    # ==================================================
    # 1. EXTRACT TEXT FROM PDF
    # ==================================================

    pages = extract_pdf_text(pdf_path)

    if not pages:
        raise ValueError(
            "No text could be extracted from the PDF."
        )

    # ==================================================
    # 2. CONVERT TEXT INTO PARAGRAPHS
    # ==================================================

    paragraphs = process_document(pages)

    if not paragraphs:
        raise ValueError(
            "No paragraphs were found in the PDF."
        )

    # ==================================================
    # 3. INSERT DOCUMENT INTO SQLITE
    # ==================================================

    document_id = insert_document(
        filename=filename,
        total_pages=len(pages),
        uploaded_at=datetime.now().isoformat()
    )

    # ==================================================
    # 4. ADD DOCUMENT ID TO EACH PARAGRAPH
    # ==================================================

    for paragraph in paragraphs:
        paragraph["document_id"] = document_id

    # ==================================================
    # 5. INSERT PARAGRAPHS INTO SQLITE
    # ==================================================

    paragraph_ids = insert_paragraphs(
        document_id=document_id,
        paragraphs=paragraphs
    )

    # ==================================================
    # 6. GENERATE EMBEDDINGS
    # ==================================================

    texts = [
        paragraph["text"]
        for paragraph in paragraphs
    ]

    embeddings = generate_embeddings(texts)

    # ==================================================
    # 7. PREPARE VECTOR RECORDS
    # ==================================================

    vector_records = []

    for paragraph_id, paragraph, embedding in zip(
        paragraph_ids,
        paragraphs,
        embeddings
    ):

        vector_records.append({
            "id": str(paragraph_id),

            "text": paragraph["text"],

            "embedding": embedding,

            "document_id": document_id,

            "page_number": paragraph["page_number"],

            "paragraph_number":
                paragraph["paragraph_number"]
        })

    # ==================================================
    # 8. STORE EMBEDDINGS IN CHROMADB
    # ==================================================

    add_embeddings(vector_records)

    # ==================================================
    # 9. RETURN RESULT
    # ==================================================

    return {
        "document_id": document_id,
        "filename": filename,
        "total_pages": len(pages),
        "total_paragraphs": len(paragraphs),
        "status": "success"
    }