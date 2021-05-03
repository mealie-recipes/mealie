from fastapi import APIRouter

from .events import router as events_router

about_router = APIRouter(prefix="/api/about")

about_router.include_router(events_router)
