from fastapi import APIRouter

from . import all_recipe_routes, bulk_actions, comments, recipe_crud_routes, shared_routes

prefix = "/recipes"

router = APIRouter()

router.include_router(all_recipe_routes.router, prefix=prefix, tags=["Recipe: Query All"])
router.include_router(recipe_crud_routes.router_exports)
router.include_router(recipe_crud_routes.router)
router.include_router(comments.router, prefix=prefix, tags=["Recipe: Comments"])
router.include_router(bulk_actions.router, prefix=prefix)
router.include_router(bulk_actions.router, prefix=prefix, tags=["Recipe: Bulk Exports"])
router.include_router(shared_routes.router, prefix=prefix, tags=["Recipe: Shared"])
