from fastapi import APIRouter

from mealie.routes.recipe import (
    all_recipe_routes,
    comments,
    image_and_assets,
    ingredient_parser,
    recipe_crud_routes,
    recipe_export,
)

prefix = "/recipes"

router = APIRouter()

router.include_router(all_recipe_routes.router, prefix=prefix, tags=["Recipe: Query All"])
router.include_router(recipe_export.user_router, prefix=prefix, tags=["Recipe: Exports"])
router.include_router(recipe_crud_routes.user_router, prefix=prefix, tags=["Recipe: CRUD"])
router.include_router(image_and_assets.user_router, prefix=prefix, tags=["Recipe: Images and Assets"])
router.include_router(comments.router, prefix=prefix, tags=["Recipe: Comments"])
router.include_router(ingredient_parser.public_router, tags=["Recipe: Ingredient Parser"])
