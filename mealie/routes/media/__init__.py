from fastapi import APIRouter

from . import media_recipe, media_user

media_router = APIRouter(prefix="/api/media", tags=["Recipe: Images and Assets"])

media_router.include_router(media_recipe.router)
media_router.include_router(media_user.router)
