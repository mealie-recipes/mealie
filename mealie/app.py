import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from mealie.core.config import APP_VERSION, settings
from mealie.core.root_logger import get_logger
from mealie.routes import backup_routes, debug_routes, migration_routes, router, theme_routes, utility_routes
from mealie.routes.about import about_router
from mealie.routes.mealplans import meal_plan_router
from mealie.routes.media import media_router
from mealie.routes.site_settings import settings_router
from mealie.services.events import create_general_event
from mealie.services.recipe.all_recipes import subscripte_to_recipe_events

logger = get_logger()

app = FastAPI(
    title="Mealie",
    description="A place for all your recipes",
    version=APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


def start_scheduler():
    import mealie.services.scheduler.scheduled_jobs  # noqa: F401


def api_routers():
    # Authentication
    app.include_router(router)
    # Recipes
    app.include_router(media_router)
    app.include_router(about_router)
    # Meal Routes
    app.include_router(meal_plan_router)
    # Settings Routes
    app.include_router(settings_router)
    app.include_router(theme_routes.public_router)
    app.include_router(theme_routes.user_router)
    # Backups/Imports Routes
    app.include_router(backup_routes.router)
    # Migration Routes
    app.include_router(migration_routes.router)
    # Debug routes
    app.include_router(debug_routes.public_router)
    app.include_router(debug_routes.admin_router)
    # Utility routes
    app.include_router(utility_routes.router)


api_routers()


@app.on_event("startup")
def system_startup():
    start_scheduler()
    logger.info("-----SYSTEM STARTUP----- \n")
    logger.info("------APP SETTINGS------")
    logger.info(
        settings.json(
            indent=4,
            exclude={
                "SECRET",
                "DEFAULT_PASSWORD",
                "SFTP_PASSWORD",
                "SFTP_USERNAME",
                "DB_URL",  # replace by DB_URL_PUBLIC for logs
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
            },
        )
    )
    create_general_event("Application Startup", f"Mealie API started on port {settings.API_PORT}")
    subscripte_to_recipe_events()


def main():
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True,
        reload_dirs=["mealie"],
        debug=True,
        log_level="debug",
        use_colors=True,
        log_config=None,
        workers=1,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
