from mealie.http.api import APIRouter

from . import foods, units

router = APIRouter()

router.include_router(foods.router)
router.include_router(units.router)
