from fastapi import APIRouter

from . import ingredient_parser

router = APIRouter()
router.include_router(ingredient_parser.public_router, tags=["Recipe: Ingredient Parser"])
