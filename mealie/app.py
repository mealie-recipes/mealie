import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from mealie.core.config import get_app_settings
from mealie.core.root_logger import get_logger
from mealie.core.settings.static import APP_VERSION
from mealie.routes import router, utility_routes
from mealie.routes.handlers import register_debug_handler
from mealie.routes.media import media_router
from mealie.services.scheduler import SchedulerRegistry, SchedulerService, tasks

logger = get_logger()
settings = get_app_settings()

description = f"""
Mealie is a web application for managing your recipes, meal plans, and shopping lists. This is the Restful
API interactive documentation that can be used to explore the API. If you're justing getting started with
the API and want to get started quickly, you can use the [API Usage | Mealie Docs](https://hay-kot.github.io/mealie/documentation/getting-started/api-usage/)
as a reference for how to get started.


As of this release <b>{APP_VERSION}</b>, Mealie is still in rapid development and therefore some of these APIs may change from version to version.


If you have any questions or comments about mealie, please use the discord server to talk to the developers or other community members.
If you'd like to file an issue, please use the [GitHub Issue Tracker | Mealie](https://github.com/hay-kot/mealie/issues/new/choose)


## Helpful Links
- [Home Page](https://mealie.io)
- [Documentation](https://hay-kot.github.io/mealie/)
- [Discord](https://discord.gg/QuStdQGSGK)
- [Demo](https://demo.mealie.io)
- [Beta](https://beta.mealie.io)


"""

app = FastAPI(
    title="Mealie",
    description=description,
    version=APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

register_debug_handler(app)


async def start_scheduler():
    SchedulerRegistry.register_daily(
        tasks.purge_group_registration,
        tasks.purge_password_reset_tokens,
        tasks.purge_group_data_exports,
    )

    SchedulerRegistry.register_minutely(lambda: logger.info("Scheduler tick"))

    SchedulerRegistry.print_jobs()

    await SchedulerService.start()


def api_routers():
    app.include_router(router)
    app.include_router(media_router)
    app.include_router(utility_routes.router)


api_routers()


@app.on_event("startup")
async def system_startup():
    await start_scheduler()

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
