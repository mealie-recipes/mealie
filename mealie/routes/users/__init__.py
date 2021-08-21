from fastapi import APIRouter

from . import api_tokens, crud, favorites, images, passwords, sign_up

# Must be used because of the way FastAPI works with nested routes
user_prefix = "/users"

router = APIRouter()

router.include_router(sign_up.admin_router, prefix=user_prefix, tags=["Users: Sign-Up"])
router.include_router(sign_up.public_router, prefix=user_prefix, tags=["Users: Sign-Up"])

router.include_router(crud.user_router, prefix=user_prefix, tags=["Users: CRUD"])
router.include_router(crud.admin_router, prefix=user_prefix, tags=["Users: CRUD"])

router.include_router(passwords.user_router, prefix=user_prefix, tags=["Users: Passwords"])

router.include_router(images.public_router, prefix=user_prefix, tags=["Users: Images"])
router.include_router(images.user_router, prefix=user_prefix, tags=["Users: Images"])

router.include_router(api_tokens.router, prefix=user_prefix, tags=["Users: Tokens"])

router.include_router(favorites.user_router, prefix=user_prefix, tags=["Users: Favorites"])
