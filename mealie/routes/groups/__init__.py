from fastapi import APIRouter

from . import crud, groups

groups_router = APIRouter()

groups_router.include_router(crud.router)
groups_router.include_router(groups.router)
