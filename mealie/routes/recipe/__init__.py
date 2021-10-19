from fastapi import APIRouter

from . import all_recipe_routes, bulk_actions, comments, image_and_assets, recipe_crud_routes, recipe_export

prefix = "/recipes"

router = APIRouter()

router.include_router(all_recipe_routes.router, prefix=prefix, tags=["Recipe: Query All"])
router.include_router(recipe_export.user_router, prefix=prefix, tags=["Recipe: Exports"])
router.include_router(recipe_crud_routes.user_router, prefix=prefix, tags=["Recipe: CRUD"])
router.include_router(image_and_assets.user_router, prefix=prefix, tags=["Recipe: Images and Assets"])
router.include_router(comments.router, prefix=prefix, tags=["Recipe: Comments"])
router.include_router(bulk_actions.router, prefix=prefix, tags=["Recipe: Bulk Actions"])
