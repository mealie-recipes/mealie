from fastapi import APIRouter

from . import auth, crud, sign_up

user_router = APIRouter()

user_router.include_router(auth.router)
user_router.include_router(sign_up.router)
user_router.include_router(crud.router)
