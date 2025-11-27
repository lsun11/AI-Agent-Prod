# src/api/routes/downloads.py
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

SAVED_DOCS_DIR = "saved_docs"
SAVED_SLIDES_DIR = "saved_slides"

@router.get("/download/{filename}")
async def download_file(filename: str):
    # pick media_type based on extension
    if filename.lower().endswith(".pptx"):
        file_path = os.path.join(SAVED_SLIDES_DIR, filename)
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        if not os.path.exists(file_path):
            # You'd see a clean 404, not a 500
            raise HTTPException(status_code=404, detail="File not found")
    else:
        file_path = os.path.join(SAVED_DOCS_DIR, filename)
        media_type = "text/plain; charset=utf-8"
        if not os.path.exists(file_path):
            # You'd see a clean 404, not a 500
            raise HTTPException(status_code=404, detail="File not found")

    # Let FileResponse set Content-Disposition correctly
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,  # Starlette will generate the header safely
    )
