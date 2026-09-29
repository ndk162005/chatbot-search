"""
PDF upload API.
"""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile


router = APIRouter(
    prefix="/api",
    tags=["Upload"],
)


UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    # Generate unique filename
    unique_name = (
        f"{uuid4().hex}_"
        f"{Path(file.filename).name}"
    )

    file_path = UPLOAD_DIR / unique_name

    try:

        contents = await file.read()

        with open(
            file_path,
            "wb",
        ) as output_file:

            output_file.write(contents)

        # ----------------------------------------------------
        # Connect chatbot and semantic-search document ingestion
        # ----------------------------------------------------
        try:
            from app.chatbot.processing.doc_service import process_and_store_document
            process_and_store_document(file_path)
        except Exception:
            pass

        return {
            "success": True,
            "filename": file.filename,
            "stored_as": unique_name,
            "message": (
                "PDF uploaded successfully."
            ),
        }

    except Exception as error:

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error