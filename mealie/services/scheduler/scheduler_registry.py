from collections.abc import Callable, Iterable

from mealie.core import root_logger

logger = root_logger.get_logger()


class SchedulerRegistry:
    """
    A container class for registering and removing callbacks for the scheduler.
    """

    _daily: list[Callable] = []
    _hourly: list[Callable] = []
    _minutely: list[Callable] = []

    @staticmethod
    def _register(name: str, callbacks: list[Callable], callback: Iterable[Callable]):
        for cb in callback:
            logger.debug(f"Registering {name} callback: {cb.__name__}")
            callbacks.append(cb)

    @staticmethod
    def register_daily(*callbacks: Callable):
        SchedulerRegistry._register("daily", SchedulerRegistry._daily, callbacks)

    @staticmethod
    def remove_daily(callback: Callable):
        logger.debug(f"Removing daily callback: {callback.__name__}")
        SchedulerRegistry._daily.remove(callback)

    @staticmethod
    def register_hourly(*callbacks: Callable):
        SchedulerRegistry._register("daily", SchedulerRegistry._hourly, callbacks)

    @staticmethod
    def remove_hourly(callback: Callable):
        logger.debug(f"Removing hourly callback: {callback.__name__}")
        SchedulerRegistry._hourly.remove(callback)

    @staticmethod
    def register_minutely(*callbacks: Callable):
        SchedulerRegistry._register("minutely", SchedulerRegistry._minutely, callbacks)

    @staticmethod
    def remove_minutely(callback: Callable):
        logger.debug(f"Removing minutely callback: {callback.__name__}")
        SchedulerRegistry._minutely.remove(callback)

    @staticmethod
    def print_jobs():
        for job in SchedulerRegistry._daily:
            logger.debug(f"Daily job: {job.__name__}")

        for job in SchedulerRegistry._hourly:
            logger.debug(f"Hourly job: {job.__name__}")

        for job in SchedulerRegistry._minutely:
            logger.debug(f"Minutely job: {job.__name__}")
