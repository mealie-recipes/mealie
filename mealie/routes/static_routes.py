from pathlib import Path

from fastapi import APIRouter, responses
from fastapi.responses import FileResponse

CWD = Path(__file__).parent
WEB_PATH = CWD.parent.joinpath("dist")
BASE_HTML = WEB_PATH.joinpath("index.html")
router = APIRouter()


@router.get("/favicon.ico", include_in_schema=False)
def facivon():
    return responses.RedirectResponse(url="/mealie/favicon.ico")


@router.get("/", include_in_schema=False)
def root():
    return FileResponse(BASE_HTML)


@router.get("/{full_path:path}", include_in_schema=False)
def root_plus(full_path):
    return FileResponse(BASE_HTML)
