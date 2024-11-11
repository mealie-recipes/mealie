from fastapi import APIRouter

from . import bulk_actions, comments, exports, recipe_crud_routes, shared_routes, timeline_events

prefix = "/recipes"

router = APIRouter()

router.include_router(exports.router, tags=["Recipe: Exports"])
router.include_router(recipe_crud_routes.router, tags=["Recipe: CRUD"])
router.include_router(comments.router, prefix=prefix, tags=["Recipe: Comments"])
router.include_router(bulk_actions.router, prefix=prefix, tags=["Recipe: Bulk Actions"])
router.include_router(shared_routes.router, prefix=prefix, tags=["Recipe: Shared"])
router.include_router(timeline_events.router, prefix=prefix, tags=["Recipe: Timeline"])
