from fastapi import APIRouter
from routes.users import auth, crud

router = APIRouter()

router.include_router(auth.router)
router.include_router(crud.router)
