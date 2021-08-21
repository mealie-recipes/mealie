from fastapi import APIRouter

from . import auth, users

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(users.router)
