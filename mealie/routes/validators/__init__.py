from fastapi import APIRouter

from . import validators

prefix = "/validators"

router = APIRouter()

router.include_router(validators.router, prefix=prefix, tags=["Validators"])
