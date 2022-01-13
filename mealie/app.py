import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from mealie.core.config import get_app_settings
from mealie.core.root_logger import get_logger
from mealie.core.settings.static import APP_VERSION
from mealie.routes import backup_routes, router, utility_routes
from mealie.routes.about import about_router
from mealie.routes.handlers import register_debug_handler
from mealie.routes.media import media_router
from mealie.services.events import create_general_event
from mealie.services.scheduler import SchedulerRegistry, SchedulerService, tasks

logger = get_logger()
settings = get_app_settings()

app = FastAPI(
    title="Mealie",
    description="A place for all your recipes",
    version=APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

register_debug_handler(app)


def start_scheduler():
    SchedulerService.start()

    SchedulerRegistry.register_daily(
        tasks.purge_events_database,
        tasks.purge_group_registration,
        tasks.auto_backup,
        tasks.purge_password_reset_tokens,
        tasks.purge_group_data_exports,
    )

    SchedulerRegistry.register_hourly()
    SchedulerRegistry.register_minutely(tasks.update_group_webhooks)

    logger.info(SchedulerService.scheduler.print_jobs())


def api_routers():
    app.include_router(router)
    app.include_router(media_router)
    app.include_router(about_router)
    app.include_router(backup_routes.router)
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
                "SMTP_USER",
                "SMTP_PASSWORD",
            },
        )
    )

    create_general_event("Application Startup", f"Mealie API started on port {settings.API_PORT}")


def main():
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True,
        reload_dirs=["mealie"],
        reload_delay=2,
        debug=True,
        log_level="info",
        use_colors=True,
        log_config=None,
        workers=1,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
