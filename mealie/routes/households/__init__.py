from fastapi import APIRouter

from . import controller_household_self_service

router = APIRouter()

router.include_router(controller_household_self_service.router)
