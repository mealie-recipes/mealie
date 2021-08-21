from fastapi import APIRouter

from . import auth, groups, users

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(groups.router)
