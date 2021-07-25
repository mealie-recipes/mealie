from fastapi import APIRouter

from . import groups

groups_router = APIRouter()

groups_router.include_router(groups.router)
