from fastapi import APIRouter

from . import tags

prefix = "/tags"

router = APIRouter()

router.include_router(tags.public_router, prefix=prefix, tags=["Tags: CRUD"])
router.include_router(tags.user_router, prefix=prefix, tags=["Tags: CRUD"])
router.include_router(tags.admin_router, prefix=prefix, tags=["Tags: CRUD"])
