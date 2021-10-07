from __future__ import annotations

from typing import Callable

from mealie.core import root_logger

logger = root_logger.get_logger()


class SchedulerRegistry:
    """
    A container class for registring and removing callbacks for the scheduler.
    """

    _daily: list[Callable] = []
    _hourly: list[Callable] = []
    _minutely: list[Callable] = []

    def _register(name: str, callbacks: list[Callable], callback: Callable):
        for cb in callback:
            logger.info(f"Registering {name} callback: {cb.__name__}")
            callbacks.append(cb)

    def register_daily(*callbacks: Callable):
        SchedulerRegistry._register("daily", SchedulerRegistry._daily, callbacks)

    def remove_daily(callback: Callable):
        logger.info(f"Removing daily callback: {callback.__name__}")
        SchedulerRegistry._daily.remove(callback)

    def register_hourly(*callbacks: Callable):
        SchedulerRegistry._register("daily", SchedulerRegistry._hourly, callbacks)

    def remove_hourly(callback: Callable):
        logger.info(f"Removing hourly callback: {callback.__name__}")
        SchedulerRegistry._hourly.remove(callback)

    def register_minutely(*callbacks: Callable):
        SchedulerRegistry._register("minutely", SchedulerRegistry._minutely, callbacks)

    def remove_minutely(callback: Callable):
        logger.info(f"Removing minutely callback: {callback.__name__}")
        SchedulerRegistry._minutely.remove(callback)
