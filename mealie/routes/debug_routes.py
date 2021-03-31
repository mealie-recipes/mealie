import json

from fastapi import APIRouter, Depends
from mealie.core.config import APP_VERSION, LOGGER_FILE, app_dirs, settings
from mealie.routes.deps import get_current_user

router = APIRouter(prefix="/api/debug", tags=["Debug"])


@router.get("/version")
async def get_mealie_version(current_user=Depends(get_current_user)):
    """ Returns the current version of mealie"""
    return {"version": APP_VERSION}


@router.get("/is-demo")
async def get_demo_status():
    print(settings.IS_DEMO)
    return {"demoStatus": settings.IS_DEMO}


@router.get("/last-recipe-json")
async def get_last_recipe_json(current_user=Depends(get_current_user)):
    """ Doc Str """

    with open(app_dirs.DEBUG_DIR.joinpath("last_recipe.json"), "r") as f:
        return json.loads(f.read())


@router.get("/log/{num}")
async def get_log(num: int, current_user=Depends(get_current_user)):
    """ Doc Str """
    with open(LOGGER_FILE, "rb") as f:
        log_text = tail(f, num)
    return log_text


def tail(f, lines=20):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if block_end_byte - BLOCK_SIZE > 0:
            f.seek(block_number * BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0, 0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b"\n")
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b"".join(reversed(blocks))
    return b"/n".join(all_read_text.splitlines()[-total_lines_wanted:])
