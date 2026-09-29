import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from ..core.config import UPLOAD_DIR, ALLOWED_FILE_EXTENSION, MAX_FILE_SIZE_MB
from ..processing.document_service import process_uploaded_pdf

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(ALLOWED_FILE_EXTENSION):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only PDF files ({ALLOWED_FILE_EXTENSION}) are supported."
        )

    file_path = UPLOAD_DIR / file.filename
    counter = 1
    stem = Path(file.filename).stem
    while file_path.exists():
        file_path = UPLOAD_DIR / f"{stem}_{counter}.pdf"
        counter += 1

    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_MB}MB."
        )

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        result = process_uploaded_pdf(pdf_path=str(file_path), filename=file.filename)
        return result
    except HTTPException:
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass
        raise
    except Exception as e:
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF document: {str(e)}"
        )
