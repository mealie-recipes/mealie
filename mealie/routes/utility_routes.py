from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import FileResponse

from mealie.routes.deps import validate_file_token

router = APIRouter(prefix="/api/utils", tags=["Utils"], include_in_schema=True)


@router.get("/download")
async def download_file(file_path: Optional[Path] = Depends(validate_file_token)):
    """Uses a file token obtained by an active user to retrieve a file from the operating
    system."""
    if not file_path.is_file():
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    return FileResponse(file_path, media_type="application/octet-stream", filename=file_path.name)
