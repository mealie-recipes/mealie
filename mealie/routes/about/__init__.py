from fastapi import APIRouter

from . import events, notifications

about_router = APIRouter(prefix="/api/about")

about_router.include_router(events.router, tags=["Events: CRUD"])
about_router.include_router(notifications.router, tags=["Events: Notifications"])
