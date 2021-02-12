import uvicorn
from fastapi import FastAPI

# import utils.startup as startup
from app_config import APP_VERSION, PORT, WEB_PATH, docs_url, redoc_url
from routes import (
    backup_routes,
    debug_routes,
    meal_routes,
    migration_routes,
    setting_routes,
    theme_routes,
)
from routes.recipe import (
    all_recipe_routes,
    category_routes,
    recipe_crud_routes,
    tag_routes,
)
from services.settings_services import default_settings_init
from utils.logger import logger

app = FastAPI(
    title="Mealie",
    description="A place for all your recipes",
    version=APP_VERSION,
    docs_url=docs_url,
    redoc_url=redoc_url,
)


def start_scheduler():
    import services.scheduler.scheduled_jobs


def init_settings():
    default_settings_init()
    import services.theme_services


def api_routers():
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


api_routers()
start_scheduler()
init_settings()

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
