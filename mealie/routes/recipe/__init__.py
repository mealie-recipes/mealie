from fastapi import APIRouter
from mealie.routes.recipe import all_recipe_routes, category_routes, comments, recipe_crud_routes, tag_routes

recipe_router = APIRouter()

recipe_router.include_router(all_recipe_routes.router)
recipe_router.include_router(recipe_crud_routes.public_router)
recipe_router.include_router(recipe_crud_routes.user_router)
recipe_router.include_router(category_routes.public_router)
recipe_router.include_router(category_routes.user_router)
recipe_router.include_router(category_routes.admin_router)
recipe_router.include_router(tag_routes.admin_router)
recipe_router.include_router(tag_routes.user_router)
recipe_router.include_router(tag_routes.public_router)
recipe_router.include_router(comments.router)
