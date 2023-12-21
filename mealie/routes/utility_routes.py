from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import FileResponse

from mealie.core.config import get_app_dirs
from mealie.core.dependencies import validate_file_token

router = APIRouter(prefix="/api/utils", tags=["Utils"], include_in_schema=True)


@router.get("/download")
async def download_file(file_path: Path = Depends(validate_file_token)):
    """Uses a file token obtained by an active user to retrieve a file from the operating
    system."""

    file_path = Path(file_path).resolve()

    dirs = get_app_dirs()

    if not file_path.is_relative_to(dirs.DATA_DIR):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if not file_path.is_file():
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    return FileResponse(file_path, media_type="application/octet-stream", filename=file_path.name)
