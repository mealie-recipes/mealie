import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger

# import utils.startup as startup
from core.config import APP_VERSION, PORT, docs_url, redoc_url
from db.db_setup import sql_exists
from db.init_db import init_db
from routes import (
    backup_routes,
    debug_routes,
    meal_routes,
    migration_routes,
    setting_routes,
    theme_routes,
)
from routes.groups import groups
from routes.recipe import (
    all_recipe_routes,
    category_routes,
    recipe_crud_routes,
    tag_routes,
)
from routes.users import users

app = FastAPI(
    title="Mealie",
    description="A place for all your recipes",
    version=APP_VERSION,
    docs_url=docs_url,
    redoc_url=redoc_url,
)


def data_base_first_run():
    init_db()


def start_scheduler():
    import services.scheduler.scheduled_jobs


def api_routers():
    # Authentication
    app.include_router(users.router)
    app.include_router(groups.router)
    # Recipes
    app.include_router(all_recipe_routes.router)
    app.include_router(category_routes.router)
    app.include_router(tag_routes.router)
    app.include_router(recipe_crud_routes.router)

    # Meal Routes
    app.include_router(meal_routes.router)
    # Settings Routes
    app.include_router(setting_routes.router)
    app.include_router(theme_routes.router)
    # Backups/Imports Routes
    app.include_router(backup_routes.router)
    # Migration Routes
    app.include_router(migration_routes.router)
    app.include_router(debug_routes.router)


if not sql_exists:
    data_base_first_run()

api_routers()
start_scheduler()

if __name__ == "__main__":
    logger.info("-----SYSTEM STARTUP-----")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        debug=True,
        log_level="info",
        workers=1,
        forwarded_allow_ips="*",
    )
