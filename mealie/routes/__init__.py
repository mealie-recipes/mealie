from fastapi import APIRouter

from . import admin, app, auth, categories, comments, groups, parser, recipe, shared, tags, tools, unit_and_foods, users

router = APIRouter(prefix="/api")

router.include_router(app.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(groups.router)
router.include_router(recipe.router)
router.include_router(shared.router)
router.include_router(comments.router)
router.include_router(parser.router)
router.include_router(unit_and_foods.router)
router.include_router(tools.router)
router.include_router(categories.router)
router.include_router(tags.router)
router.include_router(admin.router)
