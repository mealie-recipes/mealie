from fastapi import APIRouter
from mealie.routes.groups import crud

router = APIRouter()

router.include_router(crud.admin_router)
router.include_router(crud.user_router)
