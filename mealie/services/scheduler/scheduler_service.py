from pathlib import Path

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from mealie.core import root_logger

from .scheduled_func import ScheduledFunc
from .scheduler_registry import SchedulerRegistry

logger = root_logger.get_logger()

CWD = Path(__file__).parent
TEMP_DATA = CWD / ".temp"
SCHEDULER_DB = TEMP_DATA / "scheduler.db"
SCHEDULER_DATABASE = f"sqlite:///{SCHEDULER_DB}"

DAY_IN_MINUTES = 1440
MINUTELY_INTERVAL = 1
HOUR_IN_MINUTES = 60


class SchedulerService:
    _scheduler: BackgroundScheduler = None

    # Not Sure if this is still needed?
    # _job_store: dict[str, ScheduledFunc] = {}

    def start():
        # Preclean
        SCHEDULER_DB.unlink(missing_ok=True)

        # Scaffold
        TEMP_DATA.mkdir(parents=True, exist_ok=True)

        # Start
        SchedulerService._scheduler = BackgroundScheduler(jobstores={"default": SQLAlchemyJobStore(SCHEDULER_DATABASE)})
        SchedulerService._scheduler.add_job(run_daily, "interval", minutes=DAY_IN_MINUTES, id="Daily Interval Jobs")
        SchedulerService._scheduler.add_job(run_hourly, "interval", minutes=HOUR_IN_MINUTES, id="Hourly Interval Jobs")
        SchedulerService._scheduler.add_job(
            run_minutely, "interval", minutes=MINUTELY_INTERVAL, id="Regular Interval Jobs"
        )

        SchedulerService._scheduler.start()

    @classmethod
    @property
    def scheduler(cls) -> BackgroundScheduler:
        return SchedulerService._scheduler

    def add_cron_job(job_func: ScheduledFunc):
        SchedulerService.scheduler.add_job(
            job_func.callback,
            trigger="cron",
            name=job_func.id,
            hour=job_func.hour,
            minute=job_func.minutes,
            max_instances=job_func.max_instances,
            replace_existing=job_func.replace_existing,
            args=job_func.args,
        )

        # SchedulerService._job_store[job_func.id] = job_func

    def update_cron_job(job_func: ScheduledFunc):
        SchedulerService.scheduler.reschedule_job(
            job_func.id,
            trigger="cron",
            hour=job_func.hour,
            minute=job_func.minutes,
        )

        # SchedulerService._job_store[job_func.id] = job_func


def _scheduled_task_wrapper(callable):
    try:
        callable()
    except Exception as e:
        logger.error(f"Error in scheduled task: {e}")


def run_daily():
    logger.info("Running daily callbacks")
    for func in SchedulerRegistry._daily:
        _scheduled_task_wrapper(func)


def run_hourly():
    logger.info("Running hourly callbacks")
    for func in SchedulerRegistry._hourly:
        _scheduled_task_wrapper(func)


def run_minutely():
    logger.info("Running minutely callbacks")
    for func in SchedulerRegistry._minutely:
        _scheduled_task_wrapper(func)
