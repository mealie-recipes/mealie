from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends
from mealie.routes.deps import validate_file_token
from mealie.schema.snackbar import SnackResponse
from starlette.responses import FileResponse

router = APIRouter(prefix="/api/utils", tags=["Utils"], include_in_schema=True)


@router.get("/download")
async def download_file(file_path: Optional[Path] = Depends(validate_file_token)):
    """ Uses a file token obtained by an active user to retrieve a file from the operating
    system. """
    print("File Name:", file_path)
    if file_path.is_file():
        return FileResponse(file_path, media_type="application/octet-stream", filename=file_path.name)
    else:
        return SnackResponse.error("No File Found")
