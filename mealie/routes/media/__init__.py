from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from mealie.core.config import get_app_dirs

from . import media_recipe, media_user

media_router = APIRouter(prefix="/api/media", tags=["Recipe: Images and Assets"])

media_router.include_router(media_recipe.router)
media_router.include_router(media_user.router)


@media_router.get("/docker/validate.txt", response_class=FileResponse)
async def get_validation_text():
    folders = get_app_dirs()

    file = folders.DATA_DIR / "docker-validation" / "validate.txt"

    if file.exists():
        return file
    else:
        raise HTTPException(status_code=404, detail="File not found")
