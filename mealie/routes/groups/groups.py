from fastapi import APIRouter
from routes.groups import crud

router = APIRouter()

router.include_router(crud.router)

