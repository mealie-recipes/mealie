from fastapi import APIRouter

from . import defaults, events

about_router = APIRouter(prefix="/api/about")

about_router.include_router(events.router)
about_router.include_router(defaults.router)
