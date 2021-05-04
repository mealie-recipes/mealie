from fastapi import APIRouter
from mealie.routes.recipe import all_recipe_routes, category_routes, recipe_crud_routes, recipe_media, tag_routes

router = APIRouter()

router.include_router(all_recipe_routes.router)
router.include_router(recipe_crud_routes.router)
router.include_router(recipe_media.router)
router.include_router(category_routes.router)
router.include_router(tag_routes.router)
