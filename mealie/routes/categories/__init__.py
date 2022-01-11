from fastapi import APIRouter

from . import categories

router = APIRouter()
router.include_router(categories.router)
