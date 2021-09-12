from fastapi import APIRouter

from . import app_about

router = APIRouter(prefix="/app")

router.include_router(app_about.router, tags=["App: About"])
