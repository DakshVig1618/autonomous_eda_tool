import os
import shutil
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.agents.scanner import DatasetScanner

router = APIRouter()

# Resolve path to the backend uploads directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Saves an uploaded dataset to disk and runs the initial EDA scanner.
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        scanner = DatasetScanner(file_path)
        profile = scanner.generate_profile()

        return {
            "message": "File uploaded successfully.",
            "file_name": file.filename,
            "file_path": file_path,
            "data_profile": profile,
        }
    except Exception as e:
        print(f"ERROR in upload_dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{file_name}")
async def download_file(file_name: str):
    """
    Serves the cleaned output file for browser download.
    """
    file_path = os.path.join(UPLOAD_DIR, file_name)

    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            filename=file_name,
        )

    raise HTTPException(status_code=404, detail="Cleaned file not found.")