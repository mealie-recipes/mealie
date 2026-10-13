from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from mealie.core.config import get_app_settings
from mealie.core.root_logger import get_logger
from mealie.services.scheduler import SchedulerRegistry, SchedulerService, tasks

logger = get_logger()


async def start_scheduler() -> None:
    SchedulerRegistry.register_daily(
        tasks.purge_expired_tokens,
        tasks.purge_group_registration,
        tasks.purge_password_reset_tokens,
        tasks.purge_group_data_exports,
        tasks.create_mealplan_timeline_events,
        tasks.delete_old_checked_list_items,
    )
    SchedulerRegistry.register_minutely(tasks.post_group_webhooks)
    SchedulerRegistry.register_hourly(tasks.locked_user_reset)
    SchedulerRegistry.print_jobs()
    await SchedulerService.start()


@asynccontextmanager
async def lifespan_fn(_: Any = None) -> AsyncGenerator[None]:
    from mealie.db.init_db import main

    logger.info("start: database initialization")
    main()
    logger.info("end: database initialization")
    await start_scheduler()
    logger.info("-----SYSTEM STARTUP-----")
    logger.info(
        get_app_settings().model_dump_json(indent=4, exclude={"SECRET", "SESSION_SECRET", "DB_URL", "DB_PROVIDER"})
    )
    try:
        yield
    finally:
        # Only terminate tasks this application owns; never cancel server tasks.
        await SchedulerService.stop()
        logger.info("-----SYSTEM SHUTDOWN-----")


class DjangoApplication:
    def __init__(self, application: Any, registry: Any) -> None:
        self.application = application
        self.routes = registry.routes
        from mealie.http.dependencies import dependency_overrides

        self.dependency_overrides = dependency_overrides
        self.openapi_schema: dict[str, Any] | None = None

    def openapi(self) -> dict[str, Any]:
        from mealie.http.openapi import generate_schema

        if self.openapi_schema is None:
            self.openapi_schema = generate_schema(self.routes)
        return self.openapi_schema

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "lifespan":
            await self.application(scope, receive, send)
            return
        started = False
        try:
            await receive()
            async with lifespan_fn(self):
                started = True
                await send({"type": "lifespan.startup.complete"})
                await receive()
            await send({"type": "lifespan.shutdown.complete"})
        except Exception as exc:
            logger.exception("Application lifecycle failed")
            await send(
                {"type": "lifespan.shutdown.failed" if started else "lifespan.startup.failed", "message": str(exc)}
            )
