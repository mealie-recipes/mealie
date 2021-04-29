import uvicorn
from fastapi import FastAPI

from mealie.core import root_logger
from mealie.core.config import APP_VERSION, settings
from mealie.routes import (backup_routes, debug_routes, migration_routes,
                           theme_routes, utility_routes)
from mealie.routes.groups import groups
from mealie.routes.mealplans import mealplans
from mealie.routes.recipe import (all_recipe_routes, category_routes,
                                  recipe_assets, recipe_crud_routes,
                                  tag_routes)
from mealie.routes.site_settings import all_settings
from mealie.routes.users import users

logger = root_logger.get_logger()

app = FastAPI(
    title="Mealie",
    description="A place for all your recipes",
    version=APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)


def start_scheduler():
    import mealie.services.scheduler.scheduled_jobs  # noqa: F401


def api_routers():
    # Authentication
    app.include_router(utility_routes.router)
    app.include_router(users.router)
    app.include_router(groups.router)
    # Recipes
    app.include_router(all_recipe_routes.router)
    app.include_router(category_routes.router)
    app.include_router(tag_routes.router)
    app.include_router(recipe_crud_routes.router)
    app.include_router(recipe_assets.router)
    # Meal Routes
    app.include_router(mealplans.router)
    # Settings Routes
    app.include_router(all_settings.router)
    app.include_router(theme_routes.router)
    # Backups/Imports Routes
    app.include_router(backup_routes.router)
    # Migration Routes
    app.include_router(migration_routes.router)
    app.include_router(debug_routes.router)


api_routers()


@app.on_event("startup")
def system_startup():
    start_scheduler()
    logger.info("-----SYSTEM STARTUP----- \n")
    logger.info("------APP SETTINGS------")
    logger.info(settings.json(indent=4, exclude={"SECRET", "DEFAULT_PASSWORD", "SFTP_PASSWORD", "SFTP_USERNAME"}))


def main():

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True,
        reload_dirs=["mealie"],
        debug=True,
        log_level="info",
        log_config=None,
        workers=1,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
