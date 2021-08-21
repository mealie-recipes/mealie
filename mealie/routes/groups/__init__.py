from fastapi import APIRouter

from . import crud

router = APIRouter()

router.include_router(crud.user_router)
router.include_router(crud.admin_router)
