from fastapi import Depends
from fastapi.routing import APIRouter
from mealie.core.config import APP_VERSION, app_dirs, settings
from mealie.core.root_logger import LOGGER_FILE
from mealie.core.security import create_file_token
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter
from mealie.schema.about import AppInfo, AppStatistics, DebugInfo
from sqlalchemy.orm.session import Session


admin_router = AdminAPIRouter(prefix="/api/debug", tags=["Debug"])
public_router = APIRouter(prefix="/api/debug", tags=["Debug"])


@admin_router.get("")
async def get_debug_info():
    """ Returns general information about the application for debugging """

    return DebugInfo(
        production=settings.PRODUCTION,
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        api_port=settings.API_PORT,
        api_docs=settings.API_DOCS,
        db_type=settings.DB_ENGINE,
        db_url=settings.DB_URL,
        default_group=settings.DEFAULT_GROUP,
    )


@admin_router.get("/statistics")
async def get_app_statistics(session: Session = Depends(generate_session)):
    return AppStatistics(
        total_recipes=db.recipes.count_all(session),
        uncategorized_recipes=db.recipes.count_uncategorized(session),
        untagged_recipes=db.recipes.count_untagged(session),
        total_users=db.users.count_all(session),
        total_groups=db.groups.count_all(session),
    )


@public_router.get("/version")
async def get_mealie_version():
    """ Returns the current version of mealie"""
    return AppInfo(
        version=APP_VERSION,
        demo_status=settings.IS_DEMO,
        production=settings.PRODUCTION,
    )


@admin_router.get("/last-recipe-json")
async def get_last_recipe_json():
    """ Returns a token to download a file """
    return {"fileToken": create_file_token(app_dirs.DEBUG_DIR.joinpath("last_recipe.json"))}


@admin_router.get("/log/{num}")
async def get_log(num: int):
    """ Doc Str """
    with open(LOGGER_FILE, "rb") as f:
        log_text = tail(f, num)
    return log_text


@admin_router.get("/log")
async def get_log_file():
    """ Returns a token to download a file """
    return {"fileToken": create_file_token(LOGGER_FILE)}


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
