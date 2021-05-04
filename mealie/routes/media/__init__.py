from fastapi import APIRouter

from . import recipe

media_router = APIRouter(prefix="/api/media", tags=["Site Media"])

media_router.include_router(recipe.router)
