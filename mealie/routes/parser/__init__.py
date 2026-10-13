from mealie.http.api import APIRouter

from . import ingredient_parser

router = APIRouter()
router.include_router(ingredient_parser.router, tags=["Recipe: Ingredient Parser"])
