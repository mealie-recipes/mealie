from fastapi import APIRouter

from . import admin, app, auth, comments, groups, organizers, parser, recipe, shared, unit_and_foods, users, validators

router = APIRouter(prefix="/api")

router.include_router(app.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(groups.router)
router.include_router(recipe.router)
router.include_router(organizers.router)
router.include_router(shared.router)
router.include_router(comments.router)
router.include_router(parser.router)
router.include_router(unit_and_foods.router)
router.include_router(admin.router)
router.include_router(validators.router)
