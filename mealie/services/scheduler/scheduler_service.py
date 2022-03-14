from pathlib import Path

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from mealie.core import root_logger

from .scheduled_func import ScheduledFunc
from .scheduler_registry import SchedulerRegistry

logger = root_logger.get_logger()

CWD = Path(__file__).parent

SCHEDULER_DB = CWD / ".scheduler.db"
SCHEDULER_DATABASE = f"sqlite:///{SCHEDULER_DB}"

MINUTES_DAY = 1440
MINUTES_15 = 15
MINUTES_HOUR = 60


class SchedulerService:
    """
    SchedulerService is a wrapper class around the APScheduler library. It is resonpseible for interacting with the scheduler
    and scheduling events. This includes the interval events that are registered in the SchedulerRegistry as well as cron events
    that are used for sending webhooks. In most cases, unless the the schedule is dynamic, events should be registered with the
    SchedulerRegistry. See app.py for examples.
    """

    _scheduler: BackgroundScheduler

    @staticmethod
    def start():
        # Preclean
        SCHEDULER_DB.unlink(missing_ok=True)

        # Register Interval Jobs and Start Scheduler
        SchedulerService._scheduler = BackgroundScheduler(jobstores={"default": SQLAlchemyJobStore(SCHEDULER_DATABASE)})
        SchedulerService._scheduler.add_job(run_daily, "interval", minutes=MINUTES_DAY, id="Daily Interval Jobs")
        SchedulerService._scheduler.add_job(run_hourly, "interval", minutes=MINUTES_HOUR, id="Hourly Interval Jobs")
        SchedulerService._scheduler.add_job(run_minutely, "interval", minutes=MINUTES_15, id="Regular Interval Jobs")
        SchedulerService._scheduler.start()

    @classmethod
    @property
    def scheduler(cls) -> BackgroundScheduler:
        return SchedulerService._scheduler

    @staticmethod
    def add_cron_job(job_func: ScheduledFunc):
        SchedulerService.scheduler.add_job(  # type: ignore
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

    @staticmethod
    def update_cron_job(job_func: ScheduledFunc):
        SchedulerService.scheduler.reschedule_job(  # type: ignore
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
        logger.error(f"Error in scheduled task func='{callable.__name__}': exception='{e}'")


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
