from fastapi import APIRouter

from . import auth

router = APIRouter(prefix="/auth")

router.include_router(auth.public_router)
router.include_router(auth.user_router)
