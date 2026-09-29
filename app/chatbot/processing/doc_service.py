from pathlib import Path
from typing import Any

from app.chatbot.processing.pdf_extractor import extract_pdf_text
from app.chatbot.processing.document_processor import process_document
from app.chatbot.embeddings.embedding import generate_embeddings
from app.chatbot.database.database import (
    create_document,
    insert_paragraphs,
)
from app.chatbot.database.vector_store import add_documents


def process_and_store_document(pdf_path: str | Path) -> dict[str, Any]:
    """
    Process a PDF and store it in the chatbot knowledge base.

    Pipeline:

        PDF
         ↓
        PDF extraction
         ↓
        Document processing / chunking
         ↓
        SQLite
         ↓
        Embedding generation
         ↓
        ChromaDB

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.

    Returns
    -------
    dict
        Information about the processed document.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file does not exist: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, received: {pdf_path.suffix}"
        )

    # ---------------------------------------------------------
    # STEP 1: Extract text from PDF
    # ---------------------------------------------------------

    pages = extract_pdf_text(pdf_path)

    if not pages:
        raise ValueError(
            f"No text could be extracted from PDF: {pdf_path.name}"
        )

    # ---------------------------------------------------------
    # STEP 2: Process extracted text into chunks
    # ---------------------------------------------------------

    chunks = process_document(pages)

    if not chunks:
        raise ValueError(
            f"No usable text chunks were created from: "
            f"{pdf_path.name}"
        )

    # ---------------------------------------------------------
    # STEP 3: Create document record in SQLite
    # ---------------------------------------------------------

    document_id = create_document(
        filename=pdf_path.name,
        total_pages=len(pages),
    )

    # ---------------------------------------------------------
    # STEP 4: Attach document ID to every chunk
    # ---------------------------------------------------------

    for index, chunk in enumerate(chunks, start=1):

        chunk["document_id"] = document_id

        # Make sure every chunk has a paragraph number.
        if "paragraph_number" not in chunk:
            chunk["paragraph_number"] = index

    # ---------------------------------------------------------
    # STEP 5: Store chunks in SQLite
    # ---------------------------------------------------------

    insert_paragraphs(chunks)

    # ---------------------------------------------------------
    # STEP 6: Extract chunk text for embedding
    # ---------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
        if chunk.get("text")
    ]

    if not texts:
        raise ValueError(
            f"No valid text available for embedding: "
            f"{pdf_path.name}"
        )

    # ---------------------------------------------------------
    # STEP 7: Generate embeddings
    # ---------------------------------------------------------

    embeddings = generate_embeddings(texts)

    if len(embeddings) != len(texts):
        raise RuntimeError(
            "Number of embeddings does not match "
            "number of document chunks."
        )

    # ---------------------------------------------------------
    # STEP 8: Prepare ChromaDB metadata
    # ---------------------------------------------------------

    valid_chunks = [chunk for chunk in chunks if chunk.get("text")]
    vector_documents = []

    for idx, chunk in enumerate(valid_chunks):
        vector_documents.append(
            {
                "id": (
                    f"{document_id}_"
                    f"{chunk.get('paragraph_number', idx + 1)}_"
                    f"{idx}"
                ),
                "text": chunk["text"],
                "embedding": embeddings[idx],
                "metadata": {
                    "document_id": document_id,
                    "filename": pdf_path.name,
                    "page_number": chunk.get("page_number", 1),
                    "paragraph_number": chunk.get("paragraph_number", idx + 1),
                },
            }
        )

    # ---------------------------------------------------------
    # STEP 9: Store vectors in ChromaDB
    # ---------------------------------------------------------

    add_documents(vector_documents)

    # ---------------------------------------------------------
    # STEP 10: Return processing information
    # ---------------------------------------------------------

    return {
        "status": "success",
        "document_id": document_id,
        "filename": pdf_path.name,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
        "embedded_chunks": len(vector_documents),
    }