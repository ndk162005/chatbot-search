from pathlib import Path
from .pdf_extractor import extract_pdf_text
from .document_processor import process_document
from ..core.embeddings import generate_embeddings
from ..database.database import add_document, add_paragraphs
from ..database.vector_store import add_embeddings as add_vector_embeddings


def process_uploaded_pdf(pdf_path: str, filename: str) -> dict:
    path_obj = Path(pdf_path)
    file_size = path_obj.stat().st_size if path_obj.exists() else 0

    pages = extract_pdf_text(pdf_path)
    total_pages = len(pages)

    paragraphs = process_document(pages)
    total_paragraphs = len(paragraphs)

    if total_paragraphs == 0:
        return {
            "filename": filename,
            "total_pages": total_pages,
            "total_paragraphs": 0,
            "document_id": None,
            "message": "No readable text extracted from PDF."
        }

    doc_id = add_document(
        filename=filename,
        filepath=str(pdf_path),
        file_size=file_size,
        total_pages=total_pages,
        total_paragraphs=total_paragraphs
    )

    saved_records = add_paragraphs(doc_id, paragraphs)

    texts = [r["text"] for r in saved_records]
    embeddings = generate_embeddings(texts)

    vector_records = []
    for rec, emb in zip(saved_records, embeddings):
        rec_copy = dict(rec)
        rec_copy["embedding"] = emb
        vector_records.append(rec_copy)

    add_vector_embeddings(vector_records)

    return {
        "success": True,
        "message": f"Successfully processed '{filename}'",
        "document": {
            "id": doc_id,
            "filename": filename,
            "filepath": str(pdf_path),
            "file_size": file_size,
            "total_pages": total_pages,
            "total_paragraphs": total_paragraphs
        }
    }
