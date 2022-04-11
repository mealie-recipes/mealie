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
        await run_daily()
        await run_hourly()


def _scheduled_task_wrapper(callable):
    try:
        callable()
    except Exception as e:
        logger.error(f"Error in scheduled task func='{callable.__name__}': exception='{e}'")


@repeat_every(minutes=MINUTES_DAY, wait_first=True, logger=logger)
def run_daily():
    logger.info("Running daily callbacks")
    for func in SchedulerRegistry._daily:
        _scheduled_task_wrapper(func)


@repeat_every(minutes=MINUTES_HOUR, wait_first=True, logger=logger)
def run_hourly():
    logger.info("Running hourly callbacks")
    for func in SchedulerRegistry._hourly:
        _scheduled_task_wrapper(func)


@repeat_every(minutes=MINUTES_5, wait_first=True, logger=logger)
def run_minutely():
    logger.info("Running minutely callbacks")
    for func in SchedulerRegistry._minutely:
        _scheduled_task_wrapper(func)
