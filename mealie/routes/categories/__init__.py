from fastapi import APIRouter

from . import categories

prefix = "/categories"

router = APIRouter()

router.include_router(categories.public_router, prefix=prefix, tags=["Categories: CRUD"])
router.include_router(categories.user_router, prefix=prefix, tags=["Categories: CRUD"])
router.include_router(categories.admin_router, prefix=prefix, tags=["Categories: CRUD"])
