from pathlib import Path

from fastapi import APIRouter, responses
from fastapi.responses import FileResponse

CWD = Path(__file__).parent
WEB_PATH = CWD.parent.joinpath("dist")
BASE_HTML = WEB_PATH.joinpath("index.html")
router = APIRouter(include_in_schema=False)


@router.get("/favicon.ico")
def facivon():
    return responses.RedirectResponse(url="/mealie/favicon.ico")


@router.get("/")
def root():
    return FileResponse(BASE_HTML)


@router.get("/{full_path:path}")
def root_plus(full_path):
    return FileResponse(BASE_HTML)
