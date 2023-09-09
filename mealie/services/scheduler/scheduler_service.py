import asyncio
from datetime import datetime, timedelta

from pathlib import Path

from mealie.core import root_logger
from mealie.services.scheduler.runner import repeat_every

from .scheduler_registry import SchedulerRegistry

logger = root_logger.get_logger()

CWD = Path(__file__).parent

MINUTES_DAY = 1440
MINUTES_5 = 5
MINUTES_HOUR = 60


class SchedulerService:
    @staticmethod
    async def start():
        await run_minutely()
        await run_hourly()

        # Wait to trigger our daily run until our given "daily time", so having asyncio handle it.
        asyncio.create_task(schedule_daily())


async def schedule_daily():
    target_time = time_at_hour(0)
    logger.debug("Daily tasks scheduled for " + str(target_time))
    wait_seconds = (target_time - datetime.now()).total_seconds()
    await asyncio.sleep(wait_seconds)
    await run_daily()


def time_at_hour(hour=0):
    """Return a time for the next occurence of the given hour for the local time zone."""
    now = datetime.now()
    hours_until = ((hour - now.hour) % 24) or 24
    dt = timedelta(hours=hours_until)
    return (now + dt).replace(microsecond=0, second=0, minute=0)


def _scheduled_task_wrapper(callable):
    try:
        callable()
    except Exception as e:
        logger.error(f"Error in scheduled task func='{callable.__name__}': exception='{e}'")


@repeat_every(minutes=MINUTES_DAY, wait_first=False, logger=logger)
def run_daily():
    logger.debug("Running daily callbacks")
    for func in SchedulerRegistry._daily:
        _scheduled_task_wrapper(func)


@repeat_every(minutes=MINUTES_HOUR, wait_first=True, logger=logger)
def run_hourly():
    logger.debug("Running hourly callbacks")
    for func in SchedulerRegistry._hourly:
        _scheduled_task_wrapper(func)


@repeat_every(minutes=MINUTES_5, wait_first=True, logger=logger)
def run_minutely():
    logger.debug("Running minutely callbacks")
    for func in SchedulerRegistry._minutely:
        _scheduled_task_wrapper(func)
