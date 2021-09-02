from fastapi import APIRouter

from . import admin, app, auth, categories, groups, recipe, shopping_lists, tags, unit_and_foods, users

router = APIRouter(prefix="/api")

router.include_router(app.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(groups.router)
router.include_router(recipe.router)
router.include_router(unit_and_foods.router)
router.include_router(categories.router)
router.include_router(tags.router)
router.include_router(shopping_lists.router)
router.include_router(admin.router)
