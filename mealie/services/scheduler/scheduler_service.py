import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from mealie.core import root_logger
from mealie.core.config import get_app_settings
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
    now = datetime.now()
    daily_schedule_time = get_app_settings().DAILY_SCHEDULE_TIME
    logger.debug(
        "Current time is %s and DAILY_SCHEDULE_TIME is %s",
        str(now),
        daily_schedule_time,
    )
    try:
        hour_target, minute_target = _parse_daily_schedule_time(daily_schedule_time)
    except Exception:
        logger.exception(f"Unable to parse {daily_schedule_time=}")
        hour_target = 23
        minute_target = 45

    hours_until = ((hour_target - now.hour) % 24) or 24
    minutes_until = (minute_target - now.minute) % 60
    logger.debug("Hours until %s and minutes until %s", str(hours_until), str(minutes_until))

    delta = timedelta(hours=hours_until, minutes=minutes_until)
    target_time = (now + delta).replace(microsecond=0, second=0)
    logger.info("Daily tasks scheduled for %s", str(target_time))
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)
    await run_daily()


def _parse_daily_schedule_time(time):
    hour_target = int(time.split(":")[0])
    minute_target = int(time.split(":")[1])
    return hour_target, minute_target


def _scheduled_task_wrapper(callable):
    try:
        callable()
    except Exception as e:
        logger.error("Error in scheduled task func='%s': exception='%s'", callable.__name__, e)


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
