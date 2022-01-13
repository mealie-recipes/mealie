from fastapi import APIRouter

from . import api_tokens, crud, favorites, forgot_password, images, registration

# Must be used because of the way FastAPI works with nested routes
user_prefix = "/users"

router = APIRouter()

router.include_router(registration.router, prefix=user_prefix, tags=["Users: Registration"])
router.include_router(crud.user_router)
router.include_router(crud.admin_router)
router.include_router(forgot_password.router, prefix=user_prefix, tags=["Users: Passwords"])
router.include_router(images.router, prefix=user_prefix, tags=["Users: Images"])
router.include_router(api_tokens.router)
router.include_router(favorites.router, prefix=user_prefix, tags=["Users: Favorites"])
