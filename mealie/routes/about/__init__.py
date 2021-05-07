from fastapi import APIRouter

from . import events

about_router = APIRouter(prefix="/api/about")

about_router.include_router(events.router)
