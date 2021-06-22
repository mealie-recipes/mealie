from fastapi import APIRouter

from . import api_tokens, auth, crud, sign_up

user_router = APIRouter()

user_router.include_router(auth.public_router)
user_router.include_router(auth.user_router)
user_router.include_router(sign_up.public_router)
user_router.include_router(sign_up.admin_router)
user_router.include_router(crud.public_router)
user_router.include_router(crud.user_router)
user_router.include_router(crud.admin_router)
user_router.include_router(api_tokens.router)
