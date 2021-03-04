from fastapi import APIRouter
from routes.users import auth, crud, sign_up

router = APIRouter()

router.include_router(sign_up.router)
router.include_router(auth.router)
router.include_router(crud.router)
